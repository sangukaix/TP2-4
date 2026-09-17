"""Saved Bupyeong comparison repair; local only, original/report storage untouched."""
import asyncio
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from ai_server.app.runtime_env import load_project_env
from ai_server.app.llm.router import LLMRouter
from ai_server.app.agents.transferability_agent import TransferabilityAgent
from ai_server.app.agents.planning_requirements import candidate_delivery_issues


async def main():
    source = ROOT / 'storage/previews/case_research_diagnostics/20260914_164711_160814_28237_revision/diagnostic.json'
    original = source.read_bytes()
    pack = deepcopy(json.loads(original)['input_evidence_pack'])
    feedback = candidate_delivery_issues(pack, pack['transfer_assessment'])
    feedback.extend([
        {'severity': 'major', 'field': 'planning_decision.selection_reason',
         'problem': '선정 이유가 인용 보완 후 다시 비교할 수 있다는 서버 안내다. 실제 후보 우열 설명이 없다.',
         'revision_instruction': '스탬프 투어와 숙박 할인 또는 더 적절한 보유 대안을 지역 관측·ML·공식 운영 근거로 비교하라. 선택안의 유리한 점과 불리한 점, 달라져야 할 조건을 써라. 낮은 숙박 비율만으로 답을 정하지 마라.'},
        {'severity': 'major', 'field': 'planning_decision.candidate_assessments',
         'problem': '서울 보라매공원 사례 case:e4d3e4b6fd4903의 위험 설명에 다른 인천 사례의 송도·개항장 특성이 섞였다.',
         'revision_instruction': '각 case_source_id의 원문 risks와 운영 방식·측정기간을 읽고 해당 사례의 적용 위험만 작성하라. 다른 행의 위험을 복사하지 마라. 같은 문서의 전후 관측을 단독 사업 효과로 바꾸지 마라.'},
        {'severity': 'major', 'field': 'planning_decision.design_candidates.stop_or_scale_rule',
         'problem': '중단·확대 기준이 상권 협력, 쿠폰 사용처, GPS 인프라 등 준비조건을 반복한다.',
         'revision_instruction': '준비조건은 prerequisites에 두고, 운영 중 어떤 기록으로 유지·축소·중단·확대를 판단할지 각 후보 방식에 맞게 써라. 근거 없는 확정 수치 문턱은 만들지 마라. 선택 요약도 동기화하라.'},
    ])
    folder = ROOT / 'storage/previews/case_research_diagnostics' / (datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '_28237_comparison_repair')
    folder.mkdir(parents=True)
    result = {'status': 'prepared', 'source_file': str(source.relative_to(ROOT)),
              'source_sha256': hashlib.sha256(original).hexdigest(), 'input_evidence_pack': pack,
              'revision_feedback': feedback, 'paid_calls': 0, 'report_approved': False,
              'scope': 'one saved local candidate comparison repair; no new research, planner, report writes or ML training'}
    def save():
        (folder / 'diagnostic.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    router = LLMRouter(project_root=ROOT, env_values=load_project_env(ROOT))
    router.config['mode'] = 'local_first'
    async def block_paid(request):
        raise RuntimeError('Paid calls forbidden in saved comparison diagnostic')
    router.providers['openai'].generate = block_paid
    assert router.effective_routes()['transferability']['provider'] == 'qwen'
    generate = router.generate
    async def capture(request):
        answer = await generate(request)
        # Preserve the model JSON before document-linking postprocessing.
        result['model_decision'] = deepcopy(answer)
        save()
        return answer
    router.generate = capture
    save()
    try:
        await router.preflight_local_models()
        print('Qwen saved comparison repair; paid calls/report writes blocked', flush=True)
        result['planning_decision'] = await TransferabilityAgent(api_key='', model='', llm_router=router).assess(
            evidence_pack=pack, revision_feedback=feedback)
        result['remaining_findings'] = candidate_delivery_issues(pack, result['planning_decision'])
        result['status'] = 'completed_unapproved_diagnostic'
    except Exception as exc:
        result['status'] = 'failed'
        result['error_code'] = getattr(exc, 'code', type(exc).__name__)
    finally:
        result['provider_trace'] = router.consume_trace()
        result['source_unchanged'] = source.read_bytes() == original
        save()
        print(json.dumps({'status': result['status'], 'output': str(folder), 'paid_calls': 0}), flush=True)


if __name__ == '__main__':
    asyncio.run(main())
