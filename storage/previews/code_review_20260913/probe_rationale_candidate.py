"""Diagnostic: source-bound candidate reasoning, paid calls and report writes blocked."""
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
    provider_name = sys.argv[1] if len(sys.argv) > 1 else 'qwen'
    assert provider_name in ('qwen', 'gemma')
    source=ROOT/'storage/previews/case_research_diagnostics/20260914_164711_160814_28237_revision/diagnostic.json'
    if len(sys.argv) > 2:
        source = Path(sys.argv[2]).resolve()
        if not source.is_relative_to(ROOT/'storage/previews/case_research_diagnostics'):
            raise ValueError('Use a saved project diagnosis')
    raw=source.read_bytes();previous=json.loads(raw);pack=deepcopy(previous['input_evidence_pack'])
    pack.pop('transfer_assessment',None);pack.pop('candidate_validation_findings',None)
    feedback = None
    if len(sys.argv) > 3:
        feedback_path = Path(sys.argv[3]).resolve()
        if not feedback_path.is_relative_to(ROOT/'storage/previews'):
            raise ValueError('Use a project diagnostic feedback file')
        feedback = json.loads(feedback_path.read_text(encoding='utf8'))
        pack['transfer_assessment'] = previous['planning_decision']
    folder=ROOT/'storage/previews/case_research_diagnostics'/(datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'_28237_rationale_'+provider_name)
    folder.mkdir(parents=True)
    result={'status':'prepared','input_evidence_pack':pack,'source_sha256':hashlib.sha256(raw).hexdigest(),
            'source_file':str(source.relative_to(ROOT)),'paid_calls':0,'report_approved':False,
            'scope':'fresh full candidate JSON from saved facts/cases using source-bound reasoning contract and diagnostic local route; no production routing changes'}
    if feedback:
        result['scope'] = 'One targeted correction using recorded human feedback; not a fresh or blind evaluation'
        result['revision_feedback'] = feedback
    def save():
        (folder/'diagnostic.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    router=LLMRouter(project_root=ROOT,env_values=load_project_env(ROOT))
    router.config['mode']='local_only'
    router.config['routes']['transferability']['provider']=provider_name
    router.config['routes']['transferability'].pop('model',None)
    router.config['routes']['transferability']['fallback']='none'
    async def block_paid(request):
        raise RuntimeError('Paid calls forbidden in full candidate diagnostic')
    router.providers['openai'].generate=block_paid
    provider = router.providers[provider_name]
    raw_chat = provider._chat
    async def capture_chat(**kwargs):
        message, usage = await raw_chat(**kwargs)
        # Diagnostic content only; do not persist hidden reasoning or credentials.
        result.setdefault('model_messages', []).append({
            'content': message.get('content'), 'tool_calls': message.get('tool_calls'),
            'usage': usage})
        save()
        return message, usage
    provider._chat = capture_chat
    assert router.effective_routes()['transferability']['provider']==provider_name
    generate=router.generate
    async def capture(request):
        result['request_schema']=request.schema
        result['reasoning_guide']=request.input_payload.get('reasoning_guide')
        save()
        answer=await generate(request)
        result['model_decision']=deepcopy(answer)
        save()
        return answer
    router.generate=capture
    save()
    try:
        print('Source-bound fresh candidate contract; saved input, paid/report writes blocked',flush=True)
        result['planning_decision']=await TransferabilityAgent(api_key='',model='',llm_router=router).assess(evidence_pack=pack, structured_reasoning=True, revision_feedback=feedback)
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
