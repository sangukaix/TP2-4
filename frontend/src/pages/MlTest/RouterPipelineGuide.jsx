import { ArrowDown, ArrowRight, BookOpen, BrainCircuit, CheckCheck, Database, FileOutput, FilePenLine, GitCompareArrows, Search, Settings2, Terminal } from 'lucide-react'

const stages = [
  { task: 'evidence', title: '지역 근거 조사', agent: 'EvidenceAgent', icon: Database, color: 'blue', input: '선택 지역의 관측값 · ML 전망 · 사용자 조건', action: '수치의 기간·단위를 유지하고 지역 시설·정책의 공식 근거를 보강합니다.', output: '지역 사실표 · 출처 ID · 미확인 항목', file: 'agents/evidence_agent.py' },
  { task: 'case_study', title: '타지역 사례 조사', agent: 'CaseStudyAgent', icon: Search, color: 'teal', input: 'ML에서 찾은 문제 · 사업 방향 · 비교 지역', action: '저장한 공식 사례를 우선 검토하고, 부족할 때 허용된 공식 자료를 조사합니다. 지역이 완전히 같아야 하는 것은 아닙니다.', output: '운영 방식 · 기간 · 공식 실적 · 적용 조건', file: 'agents/case_study_agent.py' },
  { task: 'transferability', title: '후보 비교 · 선정', agent: 'TransferabilityAgent', icon: GitCompareArrows, color: 'violet', input: '지역 사실표 + 사례 원문 + 운영 제약', action: '서로 다른 운영 방식의 후보를 비교합니다. 선택 이유·제외 이유와 우리 지역에서 바꿀 부분을 구분합니다.', output: '선정 후보 · 대안 · 지역 적용 근거', file: 'agents/transferability_agent.py' },
  { task: 'planner', title: '기획안 작성', agent: 'PlannerAgent', icon: FilePenLine, color: 'blue', input: '선정 후보 · 원문 근거 · 사업 여건', action: '사업명·소개·해결 방법·5단계 일정·측정 방법을 구조화 JSON으로 작성합니다. 방문·소비 전망은 ML 값을 사용합니다.', output: '기획 JSON → 화면 · Word · PPT 공통 입력', file: 'agents/planner_agent.py' },
  { task: 'reviewer', title: '코드 검사 · AI 검수', agent: 'ReviewerAgent', icon: CheckCheck, color: 'amber', input: '초안 + 같은 근거 + 코드 검사 결과', action: '출처·수치·일정·실행 조건을 검사합니다. 보완 가능하면 본문 수정 1회와 재검수를 거치며 미달 결과는 검토용 초안으로 남깁니다.', output: '승인 여부 · 점수 · 구체적인 보완 사항', file: 'agents/reviewer_agent.py' },
]
const providerNames = { openai: 'OpenAI', qwen: 'Qwen', gemma: 'Gemma', local_sources: '저장 근거 · 무료 검색 도구', unavailable: '이 모드에서 실행 불가' }
function RouteLabel({ route }) {
  if (!route) return <span className="router-model">서버 설정 확인 전</span>
  return <span className={`router-model provider-${route.provider}`}><b>{providerNames[route.provider] || route.provider}</b>{route.model && <code>{route.model}</code>}</span>
}
function Stage({ stage, route }) {
  const Icon = stage.icon
  return <article className={`router-stage tone-${stage.color}`}>
    <header><Icon size={21} /><div><h3>{stage.title}</h3><small>{stage.agent}</small></div></header>
    <RouteLabel route={route} />
    <p>{stage.action}</p>
    <details><summary>입력 · 출력 · 구현 위치</summary><dl><dt>입력</dt><dd>{stage.input}</dd><dt>출력</dt><dd>{stage.output}</dd></dl><code>ai_server/app/{stage.file}</code></details>
  </article>
}

/** 서버의 effective_routes를 표시하므로 Gemma 전환 뒤에도 Qwen으로 잘못 안내하지 않습니다. */
export default function RouterPipelineGuide({ status }) {
  const routes = status?.effective_routes || {}
  const policy = status?.cost_policy
  const localFirst = Boolean(policy?.local_first)
  return <section className="router-guide" aria-label="AI 실행 파이프라인과 설계 설명">
    <header className="router-guide-heading"><div><span>HOW IT WORKS</span><h2>데이터에서 기획서까지</h2><p>5개 업무 Agent를 서버가 정해진 순서로 실행합니다. Agent 수와 모델 수는 다릅니다.</p></div><span className="router-mode-badge"><Settings2 size={15} />{status?.mode || '설정 조회 중'}</span></header>
    <div className="router-inputs"><span><Database size={16} />MySQL · 공식 원자료</span><span><BrainCircuit size={16} />저장 ML의 7개 전망</span><span><BookOpen size={16} />검수된 사례 · RAG</span><span><Settings2 size={16} />사업 여건</span></div>
    <div className="router-connector"><ArrowDown size={18} /><span>생성 클릭 → 서버 작업 ID 발급 → 데이터 준비{localFirst ? ' · 로컬 연결 선확인' : ''}</span></div>
    <div className="router-parallel-label">01 / 병렬 조사 · 캐시 조건이 맞으면 조사 결과 재사용</div>
    <div className="router-research">{stages.slice(0, 2).map((stage) => <Stage key={stage.task} stage={stage} route={routes[stage.task]} />)}</div>
    <div className="router-connector"><ArrowDown size={18} /><span>같은 근거 묶음으로 순차 실행</span></div>
    <div className="router-sequence">{stages.slice(2).map((stage) => <Stage key={stage.task} stage={stage} route={routes[stage.task]} />)}</div>
    <div className="router-review-branch"><CheckCheck size={19} /><div><b>{localFirst ? '로컬 검수 통과 → 독립 최종 검수' : '설정 모드에 따른 검수 · 보완'}</b><p>{localFirst ? '로컬 검수 미통과 시 최종 유료 검수는 생략합니다. 최종 검수 실패를 승인으로 표시하지 않습니다.' : '재작성 여부와 실제 검수 횟수는 실행 기록에서 확인합니다. 모든 모드가 별도 최종 검수를 항상 호출하는 것은 아닙니다.'}</p></div><RouteLabel route={routes.final_reviewer} /></div>
    <div className="router-output"><FileOutput size={22} /><div><b>MySQL 자동 저장 → 기획서 미리보기 · Word · PowerPoint</b><p>브라우저는 작업 상태를 조회합니다. 같은 저장 JSON의 수치와 승인된 공통 양식으로 출력하며 PDF 변환에는 LLM이 필요하지 않습니다.</p></div></div>
    <section className="router-limits" aria-label="현재 실행 한도">
      <article><span>로컬 문맥 설정</span><strong>{policy ? Object.entries(policy.local_context_lengths || {}).map(([name, size]) => `${providerNames[name]} ${Number(size).toLocaleString()}`).join(' / ') || '로컬 설정 없음' : '조회 중'}</strong><small>입력 + 출력이 함께 사용 · 모델이 실제로 지원하는 용량과 별도</small></article>
      <article><span>로컬 요청 제한 시간</span><strong>{policy ? `${Math.round(policy.local_llm_timeout_seconds / 60)}분` : '조회 중'}</strong><small>주 비교 모델 기준 · 전체 기획서 완료 시간의 상한 아님</small></article>
      <article><span>OpenAI 요청 제한 / 생성 1건</span><strong>{policy ? policy.max_cloud_calls_per_generation == null ? '모드별 고정 제한 없음' : `최대 ${policy.max_cloud_calls_per_generation}회` : '조회 중'}</strong><small>금액·토큰 한도와 별도 · 실패·재시도도 실행 기록 확인</small></article>
    </section>
    <div className="router-guide-details">
      <details open><summary><BookOpen size={16} />프롬프트는 어떻게 구성되나요?</summary><ol><li><b>역할 지시:</b> 공식 사실·ML 전망·계획 목표를 구분하고 출처 ID를 유지합니다.</li><li><b>요청별 입력:</b> 해당 지역의 관측값, 저장 ML 전망, 조건, 수집 사례를 전달합니다. 첨부문서 속 명령은 실행 지시가 아닙니다.</li><li><b>읽기 전용 근거 도구:</b> 관측값·비교표·사례 원문을 조회합니다. 로컬 모델이 DB나 인터넷에 임의로 접근하지 않습니다.</li><li><b>출력 계약:</b> JSON Schema와 Pydantic으로 검증한 뒤 코드 품질 검사와 AI 검수에 전달합니다.</li></ol><p><code>agents/prompts.py</code> 공통·Agent 지시 · <code>llm/local_prompts.py</code> 로컬 역할 · <code>agents/planning_requirements.py</code> 작성 계약 · <code>agents/plan_quality_gate.py</code> 코드 검사</p></details>
      <details><summary><Settings2 size={16} />설정 우선순위 · 문맥 초과 · 재시도</summary><p>서버 환경변수의 기본값 → <code>storage/llm_runtime_config.json</code>의 관리자 설정 → 모드·능력 제한 → 실제 적용 경로 순서입니다. 위 모델명은 마지막 단계의 결과입니다.</p><p>문맥 크기는 <code>OLLAMA_GEMMA_CONTEXT_LENGTH</code> / <code>OLLAMA_QWEN_CONTEXT_LENGTH</code>, 시간은 <code>OLLAMA_GEMMA_TIMEOUT_SECONDS</code> / <code>LOCAL_LLM_TIMEOUT_SECONDS</code>로 설정합니다. 환경변수 변경에는 AI 서버 재시작이 필요합니다.</p><p>출력량은 각 Agent의 <code>local_max_output_tokens</code>와 <code>max_output_tokens</code>가 정합니다. 문맥 부족 시 근거를 임의로 잘라내지 않습니다. 제한된 JSON 복구·후보 보완과 본문 개정은 서로 다른 단계이며, 무제한 재시도가 아닙니다.</p><p>현재 자동 유료 대체: <b>{policy ? policy.automatic_paid_fallback ? '일부 경로 허용' : '없음' : '확인 전'}</b>. 로컬우선(Gemma)은 Qwen을 요구하지 않습니다. OpenAI 조사와 최종 검수까지 없애는 모드는 아닙니다.</p></details>
      <details><summary><Terminal size={16} />실행 명령 · API · 수정 흐름</summary><p>프로젝트 루트에서 개발 서버를 시작합니다. 서버 기본 포트: React 5177 / Backend 8200 / AI 8212.</p><pre>{String.raw`cd C:\Users\Admin\mbca\TP2-4
.\start-dev.ps1

# 프론트 검증 (LLM 호출 없음)
cd frontend
npm run lint
npm test
npm run build`}</pre><p><code>POST /ai/v1/demo/&#123;region_code&#125;/strategy-report/jobs</code> 생성 시작 → <code>GET …/jobs/&#123;job_id&#125;</code> 진행 조회. 이 페이지를 여는 것만으로 생성하지 않습니다.</p><p>챗봇은 기존 기획안에 수정안을 제안 → 사용자가 반영 → 같은 보고서를 자동 저장 → 미리보기 갱신. 학습 챗봇은 설명용으로 별도 동작합니다.</p><p><code>GET /ai/v1/llm/overview</code> 설정만 조회 · <code>GET /ai/v1/llm/trace</code> 실제 호출 기록 · <code>GET /ai/v1/llm/status</code> 명시적 연결 확인.</p></details>
      <details><summary><ArrowRight size={16} />사례 저장 · 수치 · 검수의 의미</summary><p>공식 사례와 원문 근거는 저장해 재사용합니다. 재사용 여부는 요청 조건·기간·캐시 정책에 따라 결정되므로 같은 사례를 영구히 무검사하는 구조는 아닙니다.</p><p>ML 전망은 자연스러운 방문·소비 추세입니다. 운영 규모 × 이용률 × 추가 방문 비중으로 계산한 사업 목표는 별도 계획 시나리오입니다. 다른 지역 성과를 인구 비율만으로 복사하지 않습니다.</p><p>저장 완료, 모델 연결, 품질검수 통과는 서로 다른 상태입니다. 전체 생성 품질과 실제 GPU 처리 시간은 기획서 생성으로 따로 확인해야 합니다.</p></details>
    </div>
  </section>
}
