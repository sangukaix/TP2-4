import json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from ai_server.app.proposal_growth_comparison import comparison
r=json.loads(Path('output/final_validation_20260915/jeju_report.json').read_text(encoding='utf-8-sig'))
x=comparison(r)
Path('output/ppt_growth_20260915/comparison.json').write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(x,ensure_ascii=True))
