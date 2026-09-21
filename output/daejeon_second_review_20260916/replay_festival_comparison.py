"""One local comparison using saved case cards; no paid calls or report writes."""
import asyncio
import hashlib
import json
from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ai_server.app.runtime_env import load_project_env
from ai_server.app.llm.router import LLMRouter
from ai_server.app.agents.transferability_agent import TransferabilityAgent
from ai_server.app.agents.planning_requirements import candidate_delivery_issues


async def main():
    folder = Path(__file__).parent
    source = folder / 'report_0.json'
    original = source.read_bytes()
    report = json.loads(original)
    from ai_server.app.main import build_region_snapshot
    snapshot = build_region_snapshot(report['region_name'])
    snapshot['ml_analysis'] = deepcopy(report['ml_analysis'])
    cases = [s for s in report['evidence_sources'] if s.get('document_type') == 'case_study']
    pack = dict(region_code='30170', region_name=report['region_name'], period=report['period'],
                planning_brief=report['planning_brief'], snapshot=snapshot,
                sources=report['evidence_sources'], benchmark_cases=cases, research_gaps=[])
    result = dict(status='prepared', input_evidence_pack=pack, paid_calls=0, report_approved=False,
                  source_sha256=hashlib.sha256(original).hexdigest())
    def save():
        (folder / 'festival_comparison.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    router = LLMRouter(project_root=ROOT, env_values=load_project_env(ROOT))
    router.config['mode'] = 'local_first'
    async def block_paid(request):
        raise RuntimeError('Paid calls forbidden in this diagnostic')
    router.providers['openai'].generate = block_paid
    assert router.effective_routes()['transferability']['provider'] == 'qwen'
    generate = router.generate
    async def capture(request):
        answer = await generate(request)
        result['model_decision'] = deepcopy(answer)
        save()
        return answer
    router.generate = capture
    save()
    try:
        await router.preflight_local_models()
        print('Local comparison started; 8 saved cases including 4 festival cards', flush=True)
        result['planning_decision'] = await TransferabilityAgent(api_key='', model='', llm_router=router).assess(evidence_pack=pack)
        result['remaining_findings'] = candidate_delivery_issues(pack, result['planning_decision'])
        result['status'] = 'completed_unapproved_diagnostic'
    except Exception as exc:
        result['status'] = 'failed'
        result['error_code'] = getattr(exc, 'code', type(exc).__name__)
    finally:
        result['provider_trace'] = router.consume_trace()
        result['source_unchanged'] = source.read_bytes() == original
        save()
        print(json.dumps({k:result.get(k) for k in ('status','error_code','source_unchanged','paid_calls')}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    asyncio.run(main())
