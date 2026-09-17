"""One local Gemma draft from a saved source-bound candidate diagnosis."""
import asyncio
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from ai_server.app.main import REPORT_SCHEMA
from ai_server.app.runtime_env import load_project_env
from ai_server.app.llm.router import LLMRouter
from ai_server.app.agents.planner_agent import PlannerAgent
from ai_server.app.agents.planning_requirements import candidate_delivery_issues, stabilize_candidate_decision
from ai_server.app.agents.plan_quality_gate import build_plan_quality_precheck


async def main():
    source = Path(sys.argv[1]).resolve()
    if not source.is_relative_to(ROOT / 'storage/previews/case_research_diagnostics'):
        raise ValueError('Diagnostic input must remain inside the project preview directory')
    raw = source.read_bytes()
    previous = json.loads(raw)
    pack = deepcopy(previous['input_evidence_pack'])
    decision, corrections = stabilize_candidate_decision(pack, previous['planning_decision'])
    pack['transfer_assessment'] = decision
    pack['candidate_validation_findings'] = candidate_delivery_issues(pack, decision)
    folder = ROOT / 'storage/previews/case_research_diagnostics' / (datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'_28237_rationale_handoff')
    folder.mkdir(parents=True)
    result = {'status': 'prepared', 'input_evidence_pack': pack, 'planning_decision': decision,
              'source_sha256': hashlib.sha256(raw).hexdigest(), 'source_file': str(source.relative_to(ROOT)),
              'corrections': corrections, 'paid_calls': 0, 'report_approved': False}
    feedback = None
    previous_draft = None
    if len(sys.argv) > 2:
        feedback_path = Path(sys.argv[2]).resolve()
        if not feedback_path.is_relative_to(ROOT/'storage/previews'):
            raise ValueError('Use a project diagnostic feedback file')
        feedback = {'issues': json.loads(feedback_path.read_text(encoding='utf8'))}
        previous_draft = previous['draft']
        result['revision_feedback'] = feedback
    def save():
        (folder/'diagnostic.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    router = LLMRouter(project_root=ROOT, env_values=load_project_env(ROOT))
    router.config['mode'] = 'local_only'
    router.config['routes']['planner']['provider'] = 'gemma'
    router.config['routes']['planner'].pop('model', None)
    router.config['routes']['planner']['fallback'] = 'none'
    async def block_paid(request):
        raise RuntimeError('Paid calls forbidden in handoff diagnostic')
    router.providers['openai'].generate = block_paid
    save()
    try:
        print('One Gemma draft; saved candidate facts/hypothesis, no paid calls/report saves', flush=True)
        result['draft'] = await PlannerAgent(api_key='', model='', report_schema=REPORT_SCHEMA, llm_router=router).write(
            pack, revision_feedback=feedback, previous_draft=previous_draft)
        result['precheck'] = build_plan_quality_precheck(pack, result['draft'], limit=None)
        result['status'] = 'completed_unapproved_diagnostic'
    except Exception as exc:
        result['status'] = 'failed'
        result['error_code'] = getattr(exc, 'code', type(exc).__name__)
    finally:
        result['provider_trace'] = router.consume_trace()
        result['source_unchanged'] = source.read_bytes() == raw
        save()
        print(json.dumps({'status': result['status'], 'output': str(folder)}), flush=True)


if __name__ == '__main__':
    asyncio.run(main())
