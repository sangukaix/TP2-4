import json,sys
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
sys.path.insert(0,str(Path.cwd()))
from ai_server.app.proposal_document import create_strategy_proposal_document
root=Path('output/participation_floor_20260915/word')
r=json.loads(Path('output/final_validation_20260915/jeju_report.json').read_text(encoding='utf-8-sig'))
before=deepcopy(r)
with patch('httpx.get',side_effect=AssertionError('network blocked')):
 data=create_strategy_proposal_document(r).getvalue()
assert r==before
(root/'제주시_기획서_디자인최종.docx').write_bytes(data)
print('Created',len(data),'bytes')


