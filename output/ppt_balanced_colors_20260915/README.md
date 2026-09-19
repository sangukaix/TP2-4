# 목차와 본문 색상 조정

- 최종 파일: deliverables/제주시_기획서_최종.pptx
- 2장: 회색 그라데이션, 검정 제목, 빨강 목차 번호.
- 7/8/9/10/12장: 검정 본문과 소제목, 방문 파랑/소비 청록, 단계·역할별 아이콘 색.
- icons.mjs: 기존 Lucide SVG의 색상 변형을 기존 sharp로 생성. 라이선스는 공통 아이콘 디렉터리에 보존.
- build.py: 저장 보고서 불변 확인 및 네트워크 차단 상태에서 생성.
- render/: 실제 PowerPoint 15장 렌더. 지정한 6장만 변경, 나머지 9장 동일.
- audit.json: 모든 텍스트/메모/차트/표 데이터 보존 확인.
- validation.json: 패키지/기하/차트·내장 Excel/Artifact Tool import 검수.
- 생성 시스템 공통 PPT v32 반영. LLM/유료 호출 없음.
