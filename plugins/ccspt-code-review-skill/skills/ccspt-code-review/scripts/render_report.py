import argparse,html,json
from pathlib import Path

def render(data):
    e=lambda x:html.escape(str(x),quote=True)
    fs=data.get('findings',[]);ids=[f['id'] for f in fs]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate finding id')
    ranks={'high':0,'medium':1,'low':2};labels={'high':'高','medium':'中','low':'低'};rows=[]
    for i,f in enumerate(sorted(fs,key=lambda x:ranks[x['priority']])):
        detail=''.join('<p>'+e(x)+'</p>' for x in f.get('evidence',[]))
        t=f.get('details_table')
        if t:
            if any(len(r)!=len(t['columns']) for r in t['rows']):raise ValueError('table width mismatch')
            detail+='<table><thead><tr>'+''.join('<th>'+e(x)+'</th>' for x in t['columns'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(x)+'</td>' for x in r)+'</tr>' for r in t['rows'])+'</tbody></table>'
        search=' '.join(str(f.get(k,'')) for k in ['id','title','parameter','current','recommendation']).lower()
        rows.append(f'<tbody class="issue" data-priority="{e(f["priority"])}" data-search="{e(search)}"><tr><td><b class="{e(f["priority"])}">{labels[f["priority"]]}</b><small>{e(f["id"])}</small></td><td><button aria-expanded="false" aria-controls="d{i}">{e(f["title"])}</button><small>{e(f.get("parameter",""))}</small></td><td>{e(f.get("current",""))}</td><td>{e(f.get("status",""))}</td><td>{e(f.get("recommendation",""))}</td></tr><tr id="d{i}" class="detail" hidden><td colspan="5">{detail}</td></tr></tbody>')
    template='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CCSpt审核报告</title><style>body{font:15px/1.7 "Segoe UI","Microsoft YaHei",sans-serif;background:#f4f7f9;color:#203d51;margin:0}main{max-width:1280px;margin:auto;padding:30px}table{width:100%;border-collapse:collapse;background:white}td,th{text-align:left;padding:12px;border-bottom:1px solid #dce5eb;vertical-align:top}th{background:#edf3f6}small{display:block;color:#657d8d}.high{color:#a22b29}.medium{color:#876017}.low{color:#557386}button,input,select{font:inherit;color:inherit}button{cursor:pointer;border:0;background:none;text-align:left}button:focus-visible{outline:2px solid #568aac}.toolbar{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}input,select{padding:8px;border:1px solid #bcd0dc}.detail td{background:#eef5fa}p{overflow-wrap:anywhere}[hidden]{display:none!important}.wrap{overflow-x:auto}details{margin-top:20px}summary{cursor:pointer}@media(max-width:700px){.wrap>table{min-width:750px}}</style></head><body><main><h1>@@title@@</h1><p>@@project@@</p><p>版本 @@skill_version@@ · 更新检测 @@update_check@@</p><p>@@scope@@</p><p>优先级与证据状态独立；功能和保护风险优先，范围冲突合并明细。</p><div class="toolbar"><label>搜索 <input id="q" type="search"></label><label>优先级 <select id="p"><option value="all">全部</option><option value="high">高</option><option value="medium">中</option><option value="low">低</option></select></label><button id="expand">展开当前结果</button><button id="collapse">收起细节</button></div><p id="count" aria-live="polite"></p><div class="wrap"><table><thead><tr><th>优先级</th><th>问题 / 参数</th><th>当前值</th><th>确认状态</th><th>建议</th></tr></thead>@@rows@@</table></div><details><summary>已检查与验证</summary>@@checks@@</details><details><summary>未检查与缺少依据</summary>@@limitations@@</details></main><script>const nodes=[...document.querySelectorAll('.issue')],q=document.getElementById('q'),p=document.getElementById('p');function expand(n,v){n.querySelector('.detail').hidden=!v;n.querySelector('button').setAttribute('aria-expanded',String(v))}function filter(){let c=0;for(const n of nodes){n.hidden=!((p.value==='all'||n.dataset.priority===p.value)&&n.dataset.search.includes(q.value.toLowerCase()));if(!n.hidden)c++}document.getElementById('count').textContent=`显示 ${c} / ${nodes.length} 条`;}nodes.forEach(n=>n.querySelector('button').addEventListener('click',()=>expand(n,n.querySelector('.detail').hidden)));q.addEventListener('input',filter);p.addEventListener('change',filter);document.getElementById('expand').addEventListener('click',()=>nodes.filter(n=>!n.hidden).forEach(n=>expand(n,true)));document.getElementById('collapse').addEventListener('click',()=>nodes.forEach(n=>expand(n,false)));filter();</script></body></html>'''
    values={k:e(data.get(k,'')) for k in ['title','project','skill_version','update_check','scope']};values['rows']=''.join(rows)
    for k in ['checks','limitations']:values[k]=''.join('<p>'+e(x)+'</p>' for x in data.get(k,[]))
    import re
    return re.sub(r'@@(\w+)@@',lambda m:values[m[1]],template)

def main():
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    output=render(json.loads(a.input.read_text(encoding='utf-8-sig')));a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(output,encoding='utf-8')
if __name__=='__main__':main()
