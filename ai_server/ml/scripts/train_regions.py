"""등록된 여러 시군구를 순서대로 재학습하는 관리용 CLI입니다.

실행: python -m ai_server.ml.scripts.train_regions --all
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json

from ..region_registry import list_region_pipelines
from ..region_service import train_region_demand


def _train_one(code: str) -> dict:
    """한 지역의 실패가 다른 지역 학습을 중단하지 않게 결과를 직렬화합니다."""
    try:
        return {'region_code': code, 'status': 'completed', 'metadata': train_region_demand(code)}
    except Exception as exc:
        return {'region_code': code, 'status': 'failed', 'error': str(exc)}


def main() -> None:
    # --all은 등록표의 모든 지역을 순서대로 학습합니다.
    # --region-code를 여러 번 쓰면 필요한 시군구만 골라 다시 학습할 수 있습니다.
    """지역별 실패를 분리해 한 지역 원본 오류가 전체 재학습을 멈추지 않게 합니다."""
    parser = argparse.ArgumentParser(description='등록된 지역 관광수요 모델을 재학습합니다.')
    parser.add_argument('--region-code', action='append', default=[], help='재학습할 시군구 코드. 여러 번 입력 가능')
    parser.add_argument('--all', action='store_true', help='등록된 모든 시군구를 재학습')
    parser.add_argument('--workers', type=int, default=1, help='병렬 학습 프로세스 수(기본 1)')
    parser.add_argument('--summary-only', action='store_true', help='전체 메타데이터 대신 성공·실패 요약만 출력')
    args = parser.parse_args()
    codes = args.region_code or ([item.region_code for item in list_region_pipelines()] if args.all else [])
    if not codes:
        parser.error('--region-code 또는 --all 중 하나가 필요합니다.')
    # 배치 결과를 JSON으로 출력하면 팀원이 실행 로그에서 성공·실패 지역을 한눈에 확인할 수 있습니다.
    workers = max(1, min(args.workers, len(codes)))
    if workers == 1:
        results = [_train_one(code) for code in codes]
    else:
        indexed = {code: index for index, code in enumerate(codes)}
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(_train_one, code): code for code in codes}
            results = [future.result() for future in as_completed(futures)]
        results.sort(key=lambda result: indexed[result['region_code']])
    if args.summary_only:
        failures = [result for result in results if result['status'] != 'completed']
        output = {
            'requested': len(codes),
            'completed': len(codes) - len(failures),
            'failed': len(failures),
            'failures': failures,
        }
    else:
        output = results
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
