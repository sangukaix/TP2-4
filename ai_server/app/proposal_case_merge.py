"""Combine saved local adaptation reasoning with the reference case page."""
import json
import re
from .proposal_layout_v7 import text, rect, EMU
from .proposal_theme_spicus import get, pos, rounded, fit_text


def merge_case_application(prs,report):
    slide=next((s for s in prs.slides if get(s,'result-title') is not None),None)
    if slide is None:return
    # Keep the reference photograph and operating/performance infographic.
    remove={'result-operation','result-action','result-interpretation','result-evidence-card'}
    for sh in list(slide.shapes):
        if sh.name in remove:sh._element.getparent().remove(sh._element)
    # Compress the visual block as a group, leaving a clear comparison row below.
    block=[sh for sh in slide.shapes if sh.name.startswith('result-') and sh.name not in ('result-title','result-scope') and sh.top/EMU>=295]
    bottom=max(((sh.top+sh.height)/EMU for sh in block),default=630)
    scale=min(.85,330/max(bottom-300,1))
    for sh in slide.shapes:
        if sh.name.startswith('result-') and sh.name not in ('result-title','result-scope'):
            top=sh.top/EMU
            if top>=295:
                sh.top=round((300+(top-300)*scale)*EMU)
                sh.height=round(sh.height*scale)
                if sh.shape_type==13:
                    # Preserve image/icon aspect ratio when fitting the shorter block.
                    w,h=sh.image.size
                    box_w,box_h=sh.width,sh.height
                    fitted=min(box_w/w,box_h/h)
                    sh.width=round(w*fitted);sh.height=round(h*fitted)
                    sh.left+=round((box_w-sh.width)/2)
                    sh.top+=round((box_h-sh.height)/2)
    decision=report.get('planning_decision') or {}
    selected=next((c for c in decision.get('design_candidates') or [] if c.get('candidate_id')==decision.get('selected_candidate_id')), {})
    strategy=(report.get('strategies') or [{}])[0]
    facts=[f"{f['metric']} · {f['value']}" for f in report.get('observed_findings') or [] if f.get('metric') and f.get('value')]
    reason=decision.get('selection_reason') or selected.get('local_fit') or strategy.get('comparison_analysis') or ''
    rows=[('우리 지역의 관광 신호','\n'.join(facts[:3]) or selected.get('local_fit') or '지역 지표와 사업 조건을 연결합니다.'),
          ('이 사례를 선택한 이유',selected.get('local_fit') or reason),
          ('우리 지역에 적용할 내용',strategy.get('solution') or selected.get('mechanism') or '')]
    for i,(label,body) in enumerate(rows):
        body=re.sub(r'\([^)]*(?:source_id|case:|ml:)[^)]*\)', '', str(body)).strip()
        x=106+i*472
        panel=rect(slide,f'case-adaptation-card-{i}',x,657,444,194,'FFFFFF');rounded(panel,'FFFFFF',9000)
        text(slide,f'case-adaptation-label-{i}',label,x+19,674,406,34,23,'137E7A',True)
        sh=text(slide,f'case-adaptation-body-{i}',body,x+19,722,406,109,20,'46515C')
        fit_text(sh,body,20,'46515C')
    slide.notes_slide.notes_text_frame.text+='\n지역 적용 근거 원문: '+json.dumps({'summary':rows,'selection_reason':reason},ensure_ascii=False)
    old=next((s for s in prs.slides if get(s,'selection-matrix') is not None),None)
    if old:
        sid=next(x for x in prs.slides._sldIdLst if x.id==old.slide_id)
        prs.part.drop_rel(sid.rId);prs.slides._sldIdLst.remove(sid)
    for s in prs.slides:
        sh=get(s,'title')
        if sh is not None:
            for old,new in [('3.2 4단계','3.1 4단계'),('3.3 머신러닝','3.2 머신러닝')]:
                if sh.text.startswith(old):
                    value=sh.text.replace(old,new,1);fit_text(sh,value,40,'22262A',True)
