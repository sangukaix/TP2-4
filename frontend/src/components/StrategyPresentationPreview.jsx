import { Expand, FileText, LoaderCircle, Presentation, RotateCcw, Undo2, X } from 'lucide-react'
import { createPortal } from 'react-dom'
import { useEffect, useRef, useState } from 'react'
import { createAiStrategyPresentationPreview } from '../api/dashboardApi'
import WorkspaceAssistantPanel from './WorkspaceAssistantPanel'

function PageRail({ count, selectedPage, onSelect }) {
  return <aside className="proposal-preview-pages" aria-label="기획서 페이지 목록">
    {Array.from({ length: count }, (_, index) => index + 1).map((page) => <button type="button" key={page} className={selectedPage === page ? 'is-active' : ''} onClick={() => onSelect(page)} aria-label={`${page}페이지 보기`} aria-current={selectedPage === page ? 'page' : undefined}>{page}</button>)}
  </aside>
}

function PdfViewer({ previewUrl, selectedPage, title }) {
  return <iframe key={`${previewUrl}-${selectedPage}`} src={`${previewUrl}#page=${selectedPage}&zoom=page-width&toolbar=0&navpanes=0&scrollbar=1`} title={title} />
}

export default function StrategyPresentationPreview({ region, report, planningBrief, onApplyPatch, onDownload, downloadingFormat, onReset, onUndo, canReset = false, canUndo = false, editing = false }) {
  const [previewUrl, setPreviewUrl] = useState('')
  const [slideCount, setSlideCount] = useState(1)
  const [selectedPage, setSelectedPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const closeButton = useRef(null)
  const modalRef = useRef(null)
  const [retry, setRetry] = useState(0)
  const [fullscreen, setFullscreen] = useState(false)

  useEffect(() => {
    const controller = new AbortController()
    let objectUrl = ''
    let active = true
    queueMicrotask(() => {
      if (!active) return
      setLoading(true); setError(''); setSelectedPage(1)
    })
    const start = window.setTimeout(() => {
      if (!active) return
      createAiStrategyPresentationPreview(region.code, report, controller.signal)
      .then(({ blob, slideCount: count }) => {
        if (!active) return
        objectUrl = URL.createObjectURL(blob)
        setPreviewUrl(objectUrl); setSlideCount(count); setLoading(false)
      })
      .catch((requestError) => {
        if (active && requestError.name !== 'AbortError') { setError(requestError.message); setLoading(false) }
      })
    }, 150)
    return () => { active = false; window.clearTimeout(start); controller.abort(); if (objectUrl) URL.revokeObjectURL(objectUrl) }
  }, [region.code, report, retry])

  useEffect(() => {
    if (!fullscreen) return undefined
    const previousFocus = document.activeElement
    closeButton.current?.focus()
    const previous = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const close = (event) => {
      if (event.key === 'Escape') setFullscreen(false)
      if (event.key !== 'Tab') return
      const controls = modalRef.current?.querySelectorAll('button:not(:disabled), textarea, input, a[href], iframe')
      if (!controls?.length) return
      const first = controls[0], last = controls[controls.length - 1]
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() }
    }
    window.addEventListener('keydown', close)
    return () => { document.body.style.overflow = previous; window.removeEventListener('keydown', close); previousFocus?.focus() }
  }, [fullscreen])

  const headerActions = <div className="proposal-preview-header-actions">
    <button type="button" className="proposal-history-button" onClick={onReset} disabled={!canReset || editing}><RotateCcw size={15} />처음으로 리셋</button>
    <button type="button" className="proposal-history-button" onClick={onUndo} disabled={!canUndo || editing}><Undo2 size={15} />한 단계 되돌리기</button>
    <button type="button" className="proposal-download-button" onClick={() => onDownload('docx')} disabled={Boolean(downloadingFormat)}>{downloadingFormat === 'docx' ? <LoaderCircle size={15} /> : <FileText size={15} />}{downloadingFormat === 'docx' ? 'Word 생성 중…' : 'Word 다운로드'}</button>
    <button type="button" className="proposal-download-button is-pptx" onClick={() => onDownload('pptx')} disabled={Boolean(downloadingFormat)}>{downloadingFormat === 'pptx' ? <LoaderCircle size={15} /> : <Presentation size={15} />}{downloadingFormat === 'pptx' ? 'PPT 생성 중…' : 'PowerPoint 다운로드'}</button>
    <button type="button" className="proposal-fullscreen-button" onClick={() => setFullscreen(true)} disabled={loading || Boolean(error) || !previewUrl}><Expand size={16} />전체보기</button>
  </div>

  const viewer = loading ? <div className="proposal-preview-state"><LoaderCircle size={22} />기획서 미리보기를 준비하고 있습니다.</div> : error ? <div className="proposal-preview-state is-error">{error}<small>미리보기가 없어도 Word와 PowerPoint는 내려받을 수 있습니다.</small><button type="button" onClick={() => setRetry((value) => value + 1)}>미리보기 다시 불러오기</button></div> : <div className="proposal-preview-viewer"><PageRail count={slideCount} selectedPage={selectedPage} onSelect={setSelectedPage} /><PdfViewer previewUrl={previewUrl} selectedPage={selectedPage} title="관광 전략기획서 미리보기" /></div>

  return <>
    <section className="proposal-preview-block">
      <header><div><h3>기획서 미리보기</h3><p>{loading ? '변환 중' : error ? '미리보기 확인 필요' : `생성본 ${slideCount}쪽`}</p></div>{headerActions}</header>
      {viewer}
    </section>
    {fullscreen && previewUrl && createPortal(<div className="proposal-preview-modal" ref={modalRef} role="dialog" aria-modal="true" aria-label="기획서 전체보기">
      <section>
        <header><div><h2>기획서 전체보기</h2><p>{selectedPage} / {slideCount}쪽</p></div><button ref={closeButton} type="button" onClick={() => setFullscreen(false)} aria-label="전체보기 닫기"><X size={21} /></button></header>
        <div className="proposal-preview-modal-grid">
          <PageRail count={slideCount} selectedPage={selectedPage} onSelect={setSelectedPage} />
          <main>{loading ? <div className="proposal-preview-state"><LoaderCircle size={22} />수정된 미리보기를 준비하고 있습니다.</div> : error ? <div className="proposal-preview-state is-error">{error}</div> : <PdfViewer previewUrl={previewUrl} selectedPage={selectedPage} title={`관광 전략기획서 ${selectedPage}페이지`} />}</main>
          <WorkspaceAssistantPanel key={`fullscreen-${report.__savedEntryId || 'draft'}`} planningBrief={planningBrief} region={region} report={report} onApplyPatch={onApplyPatch} applying={editing} />
        </div>
      </section>
    </div>, document.body)}
  </>
}
