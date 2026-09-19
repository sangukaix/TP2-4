"""Rebuild local-only Cheorwon evidence for size diagnosis. No LLM/cloud/report writes."""
import asyncio
from copy import deepcopy
import json
from pathlib import Path
import sys
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ai_server.app.main import build_region_snapshot
from ai_server.app.runtime_env import load_project_env
from ai_server.ml.planning_evidence import build_planning_ml_evidence
from ai_server.app.agents.decision_facts import build_decision_facts
from ai_server.app.agents.evidence_agent import EvidenceAgent
from ai_server.app.agents.case_study_agent import CaseStudyAgent
from ai_server.app.evidence_sources import merge_evidence_sources
from ai_server.app.agents.transferability_agent import TransferabilityAgent
from ai_server.app.llm.evidence_tools import EvidenceTools
from ai_server.app.llm.local_agent import _prefetch_required_evidence
from ai_server.app.llm.context_tables import evidence_json
from ai_server.app.llm.ollama_provider import OllamaProvider

OUT = Path(__file__).parent

class Capture:
    local_first = True
    async def generate(self, request):
        self.request = request
        raise InterruptedError('captured without inference')

async def main():
    job=json.loads((OUT/'job.json').read_text(encoding='utf-8'))
    brief=json.loads(job['request_json'])['planning_brief']
    snapshot=build_region_snapshot(job['region_name'])
    snapshot['ml_analysis']=build_planning_ml_evidence(job['region_code'],job['region_name'],brief).model_dump(mode='json')
    snapshot['decision_facts']=build_decision_facts(snapshot)
    env=load_project_env(ROOT)
    env.update(OPENAI_API_KEY='', TOUR_INFO_API_KEY='', ENABLE_OFFICIAL_WEB_RESEARCH='false',
               ENABLE_CASE_STUDY_WEB_RESEARCH='false',ENABLE_LOCAL_WEB_SEARCH='false')
    with patch('ai_server.app.rag_store.OfficialTourismRagStore.search',new=AsyncMock(return_value=[])), \
         patch('ai_server.app.tourism_open_api.TourismOpenApiClient.collect_region_resources',new=AsyncMock(return_value=[])):
        evidence=await EvidenceAgent(project_root=ROOT,env_values=env).collect(region_code=job['region_code'],snapshot=snapshot,planning_brief=brief)
        cases=await CaseStudyAgent(project_root=ROOT,env_values=env).collect(region_code=job['region_code'],snapshot=snapshot,planning_brief=brief)
    for key in ('benchmark_cases','case_research_plan','case_search_coverage','case_search_policy'):
        evidence[key]=cases[key]
    evidence['sources']=merge_evidence_sources(evidence['sources'],cases['sources'])
    evidence['planning_brief']=brief
    router=Capture()
    try:await TransferabilityAgent(api_key='',model='',llm_router=router).assess(evidence_pack=evidence)
    except InterruptedError:pass
    request=router.request
    (OUT/'local_reconstructed_request.json').write_text(json.dumps({'input_payload':request.input_payload,'schema':request.schema},ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    tools=EvidenceTools(request.input_payload,task='transferability')
    pages=_prefetch_required_evidence(tools,'transferability')
    estimate=OllamaProvider._estimated_context_tokens
    print('LOCAL reconstruction, excludes fresh paid web cases. Cases:',len(cases['benchmark_cases']))
    for tool in dict.fromkeys(p['tool'] for p in pages):
        group=[p for p in pages if p['tool']==tool]
        print(tool,len(group),'chars',len(evidence_json(group)),'estimate',estimate(evidence_json(group)))
    print('prefetch chars',len(evidence_json(pages)),'estimate',estimate(evidence_json(pages)))
    (OUT/'prefetch_before.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2,default=str),encoding='utf-8')

if __name__=='__main__':asyncio.run(main())
