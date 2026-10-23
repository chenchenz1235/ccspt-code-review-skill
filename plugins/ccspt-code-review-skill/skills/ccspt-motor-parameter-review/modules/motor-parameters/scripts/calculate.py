"""Deterministic static calculator; never executes C or Python from input files."""
import argparse, ast, csv, hashlib, json, math, operator, re
from pathlib import Path

OPS={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv}
TIME_EXCEPT={'single_phase_lose_phase_cnt','step_out_cnt','lose_phase_cnt','over_speed_cnt','linear_step_out_cnt'}
CAST=re.compile(r'\((u32|int|int32_t|uint32_t)\)')

def evaluate(expr, values):
    # Cast placement affects rounding. Support only a cast of the entire result.
    cast=None
    m=CAST.match(expr.strip())
    if m:
        cast=m[1];expr=expr.strip()[m.end():].strip()
        if expr.startswith('('):
            depth=0;end=None
            for i,c in enumerate(expr):
                depth+=(c=='(')-(c==')')
                if depth==0:end=i;break
            if end!=len(expr)-1:raise ValueError('cast placement requires C evaluation')
    if CAST.search(expr):raise ValueError('nested cast requires C evaluation')
    expr=re.sub(r'g_sys_ctrl_param\.(\w+)',r'\1',expr)
    expr=re.sub(r'(?<=\d)[fF]\b','',expr)
    def walk(n):
        if isinstance(n,ast.Constant) and type(n.value) in (int,float):return n.value
        if isinstance(n,ast.Name):return values[n.id]
        if isinstance(n,ast.BinOp) and type(n.op) in OPS:return OPS[type(n.op)](walk(n.left),walk(n.right))
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.UAdd,ast.USub)):
            return walk(n.operand)*(1 if isinstance(n.op,ast.UAdd) else -1)
        raise ValueError('unsupported expression')
    value=walk(ast.parse(expr,mode='eval').body)
    if not math.isfinite(value):raise ValueError('non-finite result')
    if cast:
        value=math.trunc(value)
        lo,hi=(0,2**32-1) if cast in ('u32','uint32_t') else (-2**31,2**31-1)
        if not lo<=value<=hi:raise ValueError('integer cast out of range')
    return value

def read_source(path):
    raw=path.read_bytes()
    for enc in ('utf-8-sig','gb18030'):
        try:return raw.decode(enc)
        except UnicodeDecodeError:pass
    raise ValueError('source encoding is unsupported')

def assignments(text):
    # Preserve lines while removing comments. Only top-level straight-line assignments.
    clean=re.sub(r'/\*.*?\*/',lambda m:'\n'*m[0].count('\n'),text,flags=re.S)
    clean=re.sub(r'//[^\n]*','',clean)
    if re.search(r'\b(?:if|else if|for|while)\s*\([^\n]*\)\s*\n\s*(?!\{)[A-Za-z_]',clean):
        raise ValueError('unbraced control statement unsupported; review manually')
    function=None;depth=0;result=[];unsupported=[]
    for line_no,line in enumerate(clean.splitlines(),1):
        fm=re.match(r'\s*void\s+(matlab_param_init|matlab_calc_param_init)\s*\(void\)',line)
        if fm:function=fm[1];depth=0
        if not function:continue
        match=re.match(r'\s*g_sys_ctrl_param\.(\w+)\s*=\s*(.*?);\s*$',line)
        if match:
            item={'name':match[1],'expression':match[2].strip(),'line':line_no,'function':function}
            (result if depth==1 else unsupported).append(item)
        depth+=line.count('{')-line.count('}')
        if depth==0 and '}' in line:function=None
    # Never borrow a value from a conditional assignment or an earlier duplicate.
    blocked={x['name'] for x in unsupported}
    counts={}
    for x in result:counts[x['name']]=counts.get(x['name'],0)+1
    blocked|={k for k,v in counts.items() if v>1}
    return result,unsupported,blocked

def calculate(source, references):
    text=read_source(source);items,conditional,blocked=assignments(text)
    values={'CONST_1E6':1e6};actual=[]
    for x in items:
        row=dict(x)
        try:
            if x['name'] in blocked:raise ValueError('conditional or duplicate assignment')
            row['value']=evaluate(x['expression'],values);values[x['name']]=row['value'];row['status']='calculated'
        except (KeyError,ValueError,SyntaxError,ZeroDivisionError,OverflowError) as e:
            row['status']='unresolved';row['reason']=str(e)
        actual.append(row)
    base={x['name']:x['value'] for x in actual if x['function']=='matlab_param_init' and 'value' in x}
    expected=dict(base,CONST_1E6=1e6);checks=[]
    with (references/'rx13t-common.csv').open(encoding='utf-8-sig') as f:formulas=list(csv.DictReader(f))
    # Expected values use baseline dependencies, never a changed project's derived value.
    pending=list(formulas)
    for _ in range(len(pending)+1):
        remaining=[]
        for row in pending:
            try:expected[row['参数']]=evaluate(row['文件1公式'],expected)
            except (KeyError,ValueError,SyntaxError,ZeroDivisionError,OverflowError):remaining.append(row)
        if len(remaining)==len(pending):break
        pending=remaining
        if not pending:break
    for row in formulas:
        name=row['参数'];check={'parameter':name,'baseline_formula':row['文件1公式']}
        a=values.get(name);e=expected.get(name)
        if a is None or e is None:check['status']='unresolved'
        else:check.update(actual=a,expected=e,status='match' if math.isclose(a,e,rel_tol=1e-6,abs_tol=1e-9) else 'difference')
        checks.append(check)
    # Document mappings are independent of project calculation expressions.
    mapping={4:(1,245,.4),6:(3,205,.2),8:(13,245,.5),9:(10,205,.5),10:(2,245,.4),11:(6,245,.2),12:(8,255,.5),15:(15,245,.4),16:(5,225,.5),17:(11,235,.4)}
    decoded=[]
    for test,(param,offset,scale) in mapping.items():
        name='test'+str(test);raw=base.get('param'+str(param));row={'parameter':name,'input':'param'+str(param),'formula':f'(param{param}-{offset})*{scale}'}
        if raw is None:row['status']='unresolved'
        else:
            value=(raw-offset)*scale;row.update(expected=value,actual=values.get(name),status='unresolved' if name not in values else ('match' if math.isclose(value,values[name],rel_tol=1e-6,abs_tol=1e-9) else 'difference'))
        decoded.append(row)
    risks=[]
    def check(names,ok,message,severity='error'):
        if all(n in values for n in names):
            if not ok(*(values[n] for n in names)):risks.append({'parameters':names,'severity':severity,'message':message,'values':{n:values[n] for n in names}})
        else:risks.append({'parameters':names,'severity':'unresolved','message':'missing calculable input'})
    check(['is_start','is_run'],lambda a,b:a<=b,'is_start must not exceed is_run')
    check(['run_mode_platform_wr','speed_min'],lambda a,b:a>=b,'platform speed must be >= speed_min')
    check(['forbid_rise_speed_ipm_temper','fall_speed_ipm_temper'],lambda a,b:math.isclose(b-a,.1,abs_tol=1e-6),'recommended temperature gap is 0.1 C','advisory')
    check(['ipm_temper_max','ipm_temper_max_recover'],lambda a,b:math.isclose(a-b,10,abs_tol=1e-6),'temperature recovery gap should be 10 C','advisory')
    if values.get('torque_mode_on',0)>0.5:
        check(['iq_cmd_switch','is_max'],lambda a,b:a<b,'torque current must be < is_max')
        check(['iq_cmd_switch','is_max'],lambda a,b:b>0 and a/b>=.3,'torque current below 30% is_max','advisory')
    timing=[{'parameter':n,'count':values.get(n),'status':'count_only','note':'actual duration requires verified counter call path; no duration inferred'} for n in sorted(TIME_EXCEPT)]
    metadata=metadata_checks(text,base)
    return {'mode':'calculation_only','source':str(source.resolve()),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'metadata_checks':metadata,
        'limits':['Static arithmetic estimates using Python numeric semantics, not bit-exact C float32/integer emulation.','Conditional and duplicate assignments are unresolved; runtime updates are not modeled.','Only selected rules implemented; this is not a complete audit.','RX13T baseline only. No project rating inferred from filenames.'],
        'actual_calculations':actual,'conditional_assignments':conditional,'baseline_checks':checks,'indirect_decoding':decoded,'selected_rule_findings':risks,'protection_counts':timing}

def metadata_checks(text,base):
    groups=[];entries=[];current=None;active=False
    for n,line in enumerate(text.splitlines(),1):
        if re.match(r'\s*void\s+matlab_param_init\(',line):active=True
        if re.match(r'\s*void\s+matlab_calc_param_init\(',line):active=False
        if not active:continue
        if '参数总个数和校验和' in line:current=None
        gm=re.search(r'/\*\{\s*-*\[([^\]]+):(\d+)\]',line)
        if gm:
            current={'name':gm[1],'declared':int(gm[2]),'actual':0,'line':n};groups.append(current)
        m=re.match(r'\s*g_sys_ctrl_param\.(\w+)\s*=.*?;\s*/\*\{(.*?)\}\*/',line)
        if m:
            if current:current['actual']+=1
            meta=dict(re.findall(r'(单位|最小值|最大值|用户是否可见|备注)\s*[:：]\s*([^;}]+)',m[2]))
            meta={k:v.strip() for k,v in meta.items()};entry={'parameter':m[1],'line':n,'metadata':meta}
            try:
                lo=evaluate(meta['最小值'],{});hi=evaluate(meta['最大值'],{});v=base[m[1]]
                entry['range_status']='match' if lo<=v<=hi else 'outside_declared_range'
                entry.update(value=v,minimum=lo,maximum=hi)
            except (KeyError,ValueError,SyntaxError,ZeroDivisionError):entry['range_status']='unresolved'
            entry['remark_status']='unclear' if meta.get('用户是否可见')=='1' and meta.get('备注','') in ('','-','测试参数') else 'requires_semantic_review'
            if re.fullmatch(r'(?:param|test)\d+',m[1]):
                entry['remark_status']='exempt_indirect_alias_units'
            entries.append(entry)
    for g in groups:g['status']='match' if g['declared']==g['actual'] else 'count_mismatch'
    a=re.search(r'param_sheet_info\s*=\s*"([^"]+)"',text);b=re.search(r'表单信息\s*[:：]\s*([^}]+)',text)
    return {'groups':groups,'entries':entries,'form_status':'match' if a and b and a[1]==b[1].strip() else 'mismatch_or_missing',
            'duplicate_group_names':[g['name'] for i,g in enumerate(groups) if g['name'] in [x['name'] for x in groups[:i]]],
            'note':'Exact complete group-name comparison; Chinese/English component normalization still needs manual review. Range violations do not automatically mean engineering values are wrong.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--mode',choices=['calculate','audit'],default='calculate')
    args=p.parse_args()
    if args.mode=='audit':p.error('Formal audit requires project initiation document and evidence-based context; this script only supports calculation. Supply the document to the reviewing agent first.')
    report=calculate(args.source,Path(__file__).resolve().parents[1]/'references')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(args.output),'calculated':sum('value' in x for x in report['actual_calculations']),'unresolved':sum('value' not in x for x in report['actual_calculations']),'baseline_differences':sum(x['status']=='difference' for x in report['baseline_checks'])},ensure_ascii=False))
if __name__=='__main__':main()
