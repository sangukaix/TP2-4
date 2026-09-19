import { ExternalLink } from 'lucide-react'
import { resolveProjectTreeUrl } from '../routes'
import WorkspaceShell from '../components/WorkspaceShell'
import '../App.css'
import './projectTree.css'

const explorerUrl = resolveProjectTreeUrl(import.meta.env.VITE_PROJECT_TREE_URL, window.location.href)

/** 구조 지도 내부 기능은 유지하고, 외곽은 다른 업무 화면과 같은 Workspace로 통일합니다. */
export default function ProjectTreePage() {
  return <WorkspaceShell>
    <main className="project-tree-page">
      <header className="project-tree-toolbar">
        <span>TP2-3 프로젝트 구조 지도</span>
        <a href={explorerUrl} target="_blank" rel="noreferrer"><ExternalLink size={15} />새 창으로 보기</a>
      </header>
      <iframe title="TP2-3 프로젝트 구조 지도" src={explorerUrl} className="project-tree-frame" />
    </main>
  </WorkspaceShell>
}
