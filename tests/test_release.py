import importlib.util,unittest,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'plugins/ccspt-code-review-skill/skills/ccspt-code-review'
def load(p):
    spec=importlib.util.spec_from_file_location(p.stem,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class ReleaseTests(unittest.TestCase):
    def test_versions(self):
        for p in [SKILL/'scripts/check_version.py',ROOT/'plugins/ccspt-code-review-skill/scripts/check_version.py']:
            m=load(p);self.assertEqual(m.validate('0.2.0','local'),'0.2.0')
            with self.assertRaises(ValueError):m.validate('bad','local')
    def test_html(self):
        m=load(SKILL/'scripts/render_report.py');r=m.render({'title':'<script>bad</script>','findings':[{'id':'R1','priority':'low','title':'范围','details_table':{'columns':['参数','值'],'rows':[['a','<unsafe>'],['b','2']]}}]})
        self.assertIn('&lt;script&gt;bad',r);self.assertIn('&lt;unsafe&gt;',r);self.assertEqual(r.count('class="issue"'),1)
    def test_duplicate_ids(self):
        with self.assertRaises(ValueError):load(SKILL/'scripts/render_report.py').render({'findings':[{'id':'a'},{'id':'a'}]})
    def test_links(self):
        for p in [SKILL/'SKILL.md',SKILL/'modules/motor-parameters/MODULE.md']:
            for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                if '://' not in link:self.assertTrue((p.parent/link).is_file(),link)
if __name__=='__main__':unittest.main()
