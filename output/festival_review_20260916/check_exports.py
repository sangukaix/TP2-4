"""Offline product-renderer regression sample. Not a generated/approved proposal."""
from copy import deepcopy
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from ai_server.app.festival_cases import load_catalog,shortlist,as_case
from ai_server.app.proposal_presentation_v4 import create_strategy_proposal_presentation
from ai_server.app.proposal_document import create_strategy_proposal_document
from ai_server.app.proposal_case_outcomes import report_outcome

catalog,status=load_catalog(ROOT,{})
s={'region_code':'50110','region_name':'제주특별자치도 제주시','period':'202606',
   'ml_analysis':{'signals':[{'kind':'forecast_signal','metric':'visitors','change_percent':-3}]}}
cards=[as_case(c,status['dataset_hash']) for c in shortlist(catalog,s)]
primary=next(c for c in cards if c['retrieval_basis']['kind']=='external_benchmark')
report=json.loads((ROOT/'output/final_validation_20260915/jeju_report.json').read_text(encoding='utf-8-sig'))
report['evidence_sources']=[c for c in report['evidence_sources'] if c.get('source_type')!='benchmark_case']+[
    {**c,'source_type':'benchmark_case','title':c['source_title'],'summary':c['observed_result']} for c in cards]
report['planning_decision']={'selected_candidate_id':'render-fixture','recommended_case_ids':[primary['source_id']],
    'design_candidates':[{'candidate_id':'render-fixture','title':'출력 점검용 문화 체험 축제',
                         'mechanism':'지역 문화 체험 축제','case_source_ids':[primary['source_id']]}]}
report['strategies'][0]['title']='출력 점검용 문화 체험 축제'
report['strategies'][0]['solution']='문화 체험 축제를 지역 자원과 연계하는 출력 점검용 예시'
before=deepcopy(report)
folder=Path(__file__).resolve().parent/'exports';folder.mkdir(exist_ok=True)
with patch('httpx.Client.get',side_effect=AssertionError('Offline rendering only')),patch('httpx.get',side_effect=AssertionError('Offline rendering only')),patch('ai_server.app.proposal_presentation_v4.download_images',return_value=[]):
    (folder/'festival_render_check.pptx').write_bytes(create_strategy_proposal_presentation(report).getvalue())
    (folder/'festival_render_check.docx').write_bytes(create_strategy_proposal_document(report).getvalue())
assert report==before
(folder/'expected_case.json').write_text(json.dumps(report_outcome(report),ensure_ascii=False,indent=2,default=str),encoding='utf-8')
print('Product PPTX and DOCX created offline; source report unchanged.')
