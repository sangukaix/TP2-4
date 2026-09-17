import {
  Bot,
  BrainCircuit,
  CodeXml,
  FileBarChart,
  LayoutDashboard,
  Network,
  Route as RouteIcon,
  Sparkles,
  ClipboardList,
} from 'lucide-react'
import nightLogo from '../assets/logo-night.png'
import dayLogo from '../assets/logo-day.png'
import { resolveAppRoute } from '../routes'
import HeaderActions from './HeaderActions'

const workspaceNavItems = [
  { href: '/dashboard', label: '지역선택', icon: LayoutDashboard },
  { href: '/planning', label: '기획안 생성', icon: ClipboardList },
  { href: '/strategy', label: '기획안 수정 · 출력', icon: Sparkles },
]
const savedPlansMenuItem = { href: '/saved-plans', label: '저장된 기획서', icon: FileBarChart }
const adminNavItems = [
  { href: '/ml-test', label: '머신러닝 결과', icon: BrainCircuit },
  { href: '/openai-test', label: 'OpenAI', icon: Bot },
  { href: '/react-test', label: 'React', icon: CodeXml },
  { href: '/llm-control', label: 'AI Router', icon: RouteIcon },
  { href: '/project-tree', label: '전체 구조', icon: Network },
]
const workspacePaths = new Set([
  ...workspaceNavItems.map(({ href }) => href),
  savedPlansMenuItem.href,
  ...adminNavItems.map(({ href }) => href),
])
const topbarLabels = Object.freeze({
  '/dashboard': '1. 희망 지역을 선택해주세요',
  '/planning': '2. 필수 조건을 선택 후 기획안 생성',
  '/strategy': '3. 기획안 수정 및 출력',
  '/saved-plans': '저장공간',
  '/ml-test': '머신러닝 결과',
  '/openai-test': 'OpenAI · Agent AI 구조',
  '/react-test': 'React · Vite 구조',
  '/llm-control': 'AI Router · LLM Control Center',
  '/project-tree': '발표용 프로젝트 구조 지도',
})

/**
 * bid3의 224px 사이드바·64px 상단바 비율을 React + Vite에 맞춰 옮긴 공통 화면 틀입니다.
 * 입찰·결제 메뉴는 제거하고 관광 분석 업무 흐름만 남겼습니다.
 */
export default function WorkspaceShell({ children }) {
  const currentPath = resolveAppRoute(window.location.pathname).canonicalPath
  const pageClassName = workspacePaths.has(currentPath)
    ? 'workspace-shell oligo-seoul-page tp23-workspace'
    : 'workspace-shell'
  const topbarLabel = topbarLabels[currentPath] || '지역관광 전략 업무공간'
  const mobileNavItems = [...workspaceNavItems, savedPlansMenuItem]

  return (
    <div className={pageClassName}>
      <header className="home-header workspace-global-header">
        <div>
          <div className="home-brand-wrap">
            <a className="home-brand" href="/" aria-label="OLIGO 홈">
              <img className="home-brand-logo theme-logo theme-logo--night" src={nightLogo} alt="OLIGO-K" />
              <img className="home-brand-logo theme-logo theme-logo--day" src={dayLogo} alt="OLIGO-K" />
            </a>
            <a className="ml-learning-dot" href="/ml-test" aria-label="머신러닝 학습 결과 보기" title="머신러닝 학습 결과" />
            <HeaderActions />
          </div>
        </div>
      </header>

      <aside className="workspace-sidebar">
        <nav className="workspace-nav" aria-label="관광 분석 메뉴">
          <p>분석 업무</p>
          {workspaceNavItems.map(({ href, label }, index) => (
            <a className={currentPath === href ? 'is-active' : ''} href={href} key={href}>
              <span className="workspace-nav-number">{index + 1}</span>
              <span>{label}</span>
            </a>
          ))}
          <p>기획서 관리</p>
          <a className={currentPath === '/saved-plans' ? 'is-active' : ''} href="/saved-plans"><FileBarChart size={17} /><span>저장된 기획서</span></a>
        </nav>

      </aside>

      <section className="workspace-main">
        <header className="workspace-topbar">
          <div>
            <p>{topbarLabel}</p>
          </div>
        </header>
        <div className="workspace-content">{children}</div>
      </section>

      <nav className="workspace-mobile-nav" aria-label="모바일 관광 분석 메뉴">
        {mobileNavItems.map(({ href, label, icon: Icon }) => (
          <a className={currentPath === href ? 'is-active' : ''} href={href} key={href}><Icon size={17} /><span>{label}</span></a>
        ))}
      </nav>
    </div>
  )
}
