# 운영 규모 기반 목표와 PPT 인포그래픽

[PPT 최종본](deliverables/제주시_기획서_최종.pptx)

기존 제주시 보고서를 읽기 전용으로 사용했다. 새로운 사업 선택이나 ML 재학습 없이 자동 목표·견적의 산정 방식을 바꾼 예시다. 8장 운영 규모 산출, 9장 보수·기준·확대 그래프가 추가됐다. 디자인은 확정 v35를 유지한다.

운영량과 전환 가정은 코드로 재현 가능하지만 검증된 사업 효과가 아니다. 제주시 이용률 65%와 추가 방문 비중 30%는 계획 가정이다. 사례 원문은 사업 운영 방식을 참고하며 검토된 전환율이 확보되면 해당 비율을 쓸 수 있다. 주민 인구 보정은 적용하지 않았다. 거점 수는 실제 협약된 시설 수가 아니다.

- 계산: `ai_server/app/operating_target.py`
- 공통 연결: `idea_proposal.py`, `report_projection.py`, `proposal_presentation_v3.py`
- PPT 두 장: `proposal_operating_slides.py`
- 계산·시나리오·보존 확인: `audit.json`, `prepared_report.json`
- PPT 패키지/네이티브 차트/Artifact Tool 확인: `validation.json`
- Word 공통 연결 검수: `word/`
- 재현: `backend/.venv/Scripts/python.exe -m unittest ai_server.test_operating_target ai_server.test_idea_proposal ai_server.test_report_projection -q` (22개 통과)
- 프론트 수정 반영 검사 4개, 관련 lint, production build 통과.

새 LLM·유료 API·ML 학습은 실행하지 않았다. 지역별 전망과 선택한 운영 유형에 따라 자동 계산하되 실제 현장 수용력 확인은 별도다. 구형 고정 목표는 미리보기 사본에 갱신하며 저장 원본·관측·ML·출처·검수 상태는 보존한다. 명시적으로 수정한 목표·견적은 유지한다.

AI 서버 재시작 후 health와 실제 `/ai/v1/strategy-idea-preview` 응답 200 확인. 목표 2,246명·견적 168,080,000원 및 ML 원문 보존을 API 응답으로 대조했다(`live_preview.json`). Word 최종 렌더는 15쪽이며 4쪽에 같은 운영량·시나리오 표를 표시한다.
