"""Diagnostic only: Gemma on the existing complete candidate contract, fresh input."""
import asyncio
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from ai_server.app.runtime_env import load_project_env
from ai_server.app.llm.router import LLMRouter
from ai_server.app.agents.transferability_agent import TransferabilityAgent
from ai_server.app.agents.planning_requirements import candidate_delivery_issues


async def main():
    source=ROOT/'storage/previews/case_research_diagnostics/20260914_164711_160814_28237_revision/diagnostic.json'
    raw=source.read_bytes();pack=deepcopy(json.loads(raw)['input_evidence_pack'])
    pack.pop('transfer_assessment',None);pack.pop('candidate_validation_findings',None)
    folder=ROOT/'storage/previews/case_research_diagnostics'/(datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'_28237_gemma_candidate')
    folder.mkdir(parents=True)
    result={'status':'prepared','input_evidence_pack':pack,'source_sha256':hashlib.sha256(raw).hexdigest(),
            'source_file':str(source.relative_to(ROOT)),'paid_calls':0,'report_approved':False,
            'scope':'fresh full candidate JSON from saved facts/cases using diagnostic Gemma route; no production routing changes'}
    def save():
        (folder/'diagnostic.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    router=LLMRouter(project_root=ROOT,env_values=load_project_env(ROOT))
    router.config['mode']='local_only'
    router.config['routes']['transferability']['provider']='gemma'
    router.config['routes']['transferability'].pop('model',None)
    router.config['routes']['transferability']['fallback']='none'
    async def block_paid(request):
        raise RuntimeError('Paid calls forbidden in full candidate diagnostic')
    router.providers['openai'].generate=block_paid
    assert router.effective_routes()['transferability']['provider']=='gemma'
    generate=router.generate
    async def capture(request):
        answer=await generate(request)
        result['model_decision']=deepcopy(answer)
        save()
        return answer
    router.generate=capture
    save()
    try:
        print('Gemma fresh full candidate contract; saved input, paid/report writes blocked',flush=True)
        result['planning_decision']=await TransferabilityAgent(api_key='',model='',llm_router=router).assess(evidence_pack=pack)
        result['remaining_findings']=candidate_delivery_issues(pack,result['planning_decision'])
        result['status']='completed_unapproved_diagnostic'
    except Exception as exc:
        result['status']='failed';result['error_code']=getattr(exc,'code',type(exc).__name__)
    finally:
        result['provider_trace']=router.consume_trace()
        result['source_unchanged']=source.read_bytes()==raw
        save()
        print(json.dumps({'status':result['status'],'output':str(folder)}),flush=True)


if __name__=='__main__':
    asyncio.run(main())
