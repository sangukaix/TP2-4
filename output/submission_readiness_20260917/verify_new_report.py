"""Inspect the ONE authorized job; never starts or retries generation."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import httpx
from ai_server.app.idea_proposal import prepare_idea_report
from ai_server.app.main import ReportResponse

BASE = 'http://127.0.0.1:8212'
JOB = '7f59e8862c7f4a4591b1b3e9dc5106ea'
OLD = '91c4e7ff6d6d427e83d5875f956e272a'
OUT = Path(__file__).resolve().parent


def fetch(path):
    response = httpx.get(BASE + path, timeout=60)
    response.raise_for_status()
    return response


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def main():
    job = fetch(f'/ai/v1/demo/30170/strategy-report/jobs/{JOB}').json()
    print(json.dumps({k: job.get(k) for k in ('job_id', 'status', 'progress_step', 'message', 'error')}, ensure_ascii=False))
    if job['status'] not in ('completed', 'failed'):
        return
    (OUT / 'daejeon-new-job.json').write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding='utf-8')
    trace_path = OUT / 'daejeon-new-runtime-trace.json'
    if not trace_path.exists():
        trace_path.write_text(json.dumps(fetch('/ai/v1/llm/trace').json(), ensure_ascii=False, indent=2), encoding='utf-8')
    previous = json.loads((OUT / 'daejeon-previous-preserved.json').read_text(encoding='utf-8-sig'))
    current_previous = fetch(f'/ai/v1/strategy-reports/{OLD}').json()
    preservation = {'previous_report_unchanged': previous == current_previous,
                    'previous_canonical_sha256': digest(previous)}
    if job['status'] == 'failed':
        (OUT / 'daejeon-new-verification.json').write_text(json.dumps(preservation, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(preservation))
        return
    report = fetch(f'/ai/v1/strategy-reports/{JOB}').json()
    before = deepcopy(report)
    view = prepare_idea_report(report)
    ReportResponse.model_validate(view)
    estimate = view.get('reference_estimate') or {}
    checks = {**preservation, 'source_report_unchanged': before == report,
              'ml_unchanged': report.get('ml_analysis') == view.get('ml_analysis'),
              'quality_review_unchanged': report.get('quality_review') == view.get('quality_review'),
              'view_idempotent': prepare_idea_report(view) == view,
              'schema_valid': True,
              'estimate_total': estimate.get('total_krw'),
              'estimate_item_sum': sum(row['amount'] for row in estimate.get('items', [])),
              'quality_review': report.get('quality_review'),
              'planning_selection_status': (report.get('planning_decision') or {}).get('selection_status'),
              'source_count': len(report.get('evidence_sources') or []),
              'agent_trace': report.get('agent_trace')}
    checks['estimate_sum_matches'] = checks['estimate_total'] == checks['estimate_item_sum']
    for name, value in [('daejeon-new-report.json', report), ('daejeon-new-view.json', view),
                        ('daejeon-new-verification.json', checks)]:
        (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    for extension in ('docx', 'pptx'):
        document = fetch(f'/ai/v1/strategy-reports/{JOB}/documents/{extension}')
        (OUT / f'daejeon-new.{extension}').write_bytes(document.content)
    print(json.dumps({k: v for k, v in checks.items() if k not in ('quality_review', 'agent_trace')}, ensure_ascii=False, indent=2))
    for flag in ('previous_report_unchanged', 'source_report_unchanged', 'ml_unchanged',
                 'quality_review_unchanged', 'view_idempotent', 'estimate_sum_matches'):
        assert checks[flag], flag


if __name__ == '__main__':
    main()
