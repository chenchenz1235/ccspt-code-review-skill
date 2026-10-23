import importlib.util,unittest,re,json,subprocess,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'plugins/ccspt-code-review-skill/skills/ccspt-motor-parameter-review'
def load(p):
    spec=importlib.util.spec_from_file_location(p.stem,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class ReleaseTests(unittest.TestCase):
    def test_versions(self):
        for p in [SKILL/'scripts/check_version.py',ROOT/'plugins/ccspt-code-review-skill/scripts/check_version.py']:
            m=load(p);self.assertEqual(m.validate('0.2.0','local'),'0.2.0')
            with self.assertRaises(ValueError):m.validate('bad','local')
    def test_package_structure(self):
        plugin=ROOT/'plugins/ccspt-code-review-skill'
        skills=plugin/'skills'
        expected={'ccspt-code-review','ccspt-motor-parameter-review','ccspt-thermostat-logic'}
        self.assertEqual({p.name for p in skills.iterdir() if (p/'SKILL.md').is_file()},expected)
        for name in expected:
            folder=skills/name
            self.assertRegex((folder/'SKILL.md').read_text(encoding='utf-8'),rf'(?m)^name: {name}$')
            self.assertTrue((folder/'agents/openai.yaml').is_file())
            self.assertRegex((folder/'VERSION').read_text().strip(),r'^\d+\.\d+\.\d+$')
        version=(plugin/'VERSION').read_text().strip()
        self.assertEqual(json.loads((plugin/'plugin.json').read_text(encoding='utf-8'))['version'],version)
        claude=json.loads((ROOT/'.claude-plugin/marketplace.json').read_text(encoding='utf-8'))
        self.assertEqual(claude['plugins'][0]['version'],version)
        self.assertTrue((ROOT/claude['plugins'][0]['source']).is_dir())
        codex=json.loads((ROOT/'.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
        self.assertTrue((ROOT/codex['plugins'][0]['source']['path']).is_dir())
    def test_update_targets(self):
        for folder in [ROOT/'plugins/ccspt-code-review-skill',SKILL]:
            module=load(folder/'scripts/check_version.py')
            for url in [module.API_URL,module.RAW_URL]:
                target=url.split('/contents/')[-1] if '/contents/' in url else url.split('/main/')[-1]
                self.assertEqual((ROOT/target.split('?')[0]).resolve(),(folder/'VERSION').resolve())
    def test_all_document_links(self):
        paths=[ROOT/'README.md',*(ROOT/'plugins').rglob('*.md')]
        for p in paths:
            text=p.read_text(encoding='utf-8')
            links=re.findall(r'\]\(([^)]+)\)',text)+re.findall(r'`(references/[^`]+\.md)`',text)
            for link in links:
                if '://' not in link:
                    self.assertTrue((p.parent/link).is_file(),f'{p}: {link}')
    def test_git_text_artifacts(self):
        if not (ROOT/'.git').exists() or not shutil.which('git'):
            self.skipTest('Git checkout required for release blob verification')
        names=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
        for name in filter(None,names):
            if Path(name).suffix in {'.yaml','.csv','.md','.py','.json','.txt'} or Path(name).name=='VERSION':
                with self.subTest(path=name):
                    raw=subprocess.check_output(['git','show',':'+name],cwd=ROOT)
                    raw.decode('utf-8-sig')
    def test_html(self):
        m=load(SKILL/'scripts/render_report.py');r=m.render({'title':'<script>bad</script>','findings':[{'id':'R1','priority':'low','title':'范围','details_table':{'columns':['参数','值'],'rows':[['a','<unsafe>'],['b','2']]}}]})
        self.assertIn('&lt;script&gt;bad',r);self.assertIn('&lt;unsafe&gt;',r);self.assertEqual(r.count('class="issue"'),1)
    def test_duplicate_ids(self):
        with self.assertRaises(ValueError):load(SKILL/'scripts/render_report.py').render({'findings':[{'id':'a'},{'id':'a'}]})
    def test_links(self):
        for p in [SKILL/'SKILL.md',SKILL/'references/review-workflow.md']:
            for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                if '://' not in link:self.assertTrue((p.parent/link).is_file(),link)
if __name__=='__main__':unittest.main()
