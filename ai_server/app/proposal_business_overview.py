"""Shared proposal overview; uses saved scenario totals and editable visuals."""
import re
from pptx.opc.packuri import PackURI
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from .proposal_layout_v7 import text, rect, EMU
from .proposal_calculation_basis import calculation_basis
from .proposal_infographics import icon



def overview_description(report, width=558, size=23):
    """Expand the overview from saved proposal actions, without inventing details."""
    from .proposal_layout_v7 import wrap_words
    strategy=(report.get('strategies') or [{}])[0]
    def clean(value):
        value=re.sub(r'\([^)]*(?:source_id|case:|ml:)[^)]*\)', '', str(value or ''))
        return re.sub(r'\s+', ' ', value).strip()
    main=clean(strategy.get('solution') or report.get('summary') or strategy.get('title'))
    parts=[main] if main else []
    candidates=[clean(step.get('task')) for step in strategy.get('implementation_steps') or []]
    for candidate in candidates:
        if not candidate or candidate in main:continue
        proposal='\n'.join([*parts,candidate])
        if len(wrap_words(proposal,width,size))<=6:
            parts.append(candidate)
        if len(wrap_words('\n'.join(parts),width,size))>=5:break
    return '\n'.join(parts)


def insert_business_overview(prs, report):
    # Run last: older layout passes use fixed indexes and must finish first.
    for i, s in enumerate(prs.slides, 1):
        s.part._partname = PackURI(f'/ppt/slides/slide{i}.xml')
    for i, s in enumerate(prs.slides):
        for sh in s.shapes:
            if not sh.has_text_frame: continue
            value = sh.text
            if sh.name in ('editorial-kicker', 'title'):
                updated = re.sub(r'^(\d+)(?=\.)', lambda m: str(int(m[1])+1), value)
                if i == 2 and sh.name == 'title': updated = '1.2 지역 관광 전망'
            elif sh.name.startswith('toc-') and sh.name.endswith('-number') and value.isdigit():
                updated = str(int(value)+1)
            else: continue
            # Keep font, color and alignment from the accepted theme.
            if updated != value and sh.text_frame.paragraphs:
                first=sh.text_frame.paragraphs[0]
                if first.runs:
                    first.runs[0].text=updated
                    for r in list(first.runs)[1:]: r.text=''
                    for p in list(sh.text_frame.paragraphs)[1:]:
                        for r in p.runs:r.text=''
                else: first.text=updated
    slide=prs.slides.add_slide(prs.slides[-1].slide_layout)
    for sh in list(slide.shapes): sh._element.getparent().remove(sh._element)
    rect(slide,'overview-bg',0,0,1600,900,'F3F3F3')
    text(slide,'editorial-kicker','1. 개요',106,38,1200,37,23,'EC164B',True)
    text(slide,'title','1.1 제안 사업 소개',106,92,1388,65,42,'22262A',True)
    strategy=(report.get('strategies') or [{}])[0]
    name=strategy.get('title') or f"{report.get('region_name','선택 지역')} 관광 활성화 프로그램"
    name_shape=text(slide,'overview-name',name,106,172,1388,65,32,'22262A',True)
    for paragraph in name_shape.text_frame.paragraphs:paragraph.alignment=PP_ALIGN.CENTER
    rect(slide,'overview-photo-panel',106,280,674,337,'E4ECEB')
    from .proposal_business_images import select_business_image
    from PIL import Image
    info=select_business_image(report,prs)
    with Image.open(info['path']) as im: iw,ih=im.size
    # Show the complete original: contain, without crop or distortion.
    scale=min(674/iw,337/ih);w,h=iw*scale,ih*scale
    pic=slide.shapes.add_picture(str(info['path']),int((106+(674-w)/2)*EMU),int((280+(337-h)/2)*EMU),int(w*EMU),int(h*EMU))
    pic.name='overview-business-photo'
    from .proposal_layout_v7 import _width, wrap_words
    caption=info['caption'].replace(' · AI 생성 예시 이미지','')
    if not caption.endswith('예시안'):caption+=' 예시안'
    lines=wrap_words(caption,w-64,16)
    width=min(w-24,max(_width(line,16) for line in lines)+40)
    height=len(lines)*24+12
    x=106+(674-width)/2
    y=(pic.top+pic.height)/EMU-height-12
    rect(slide,'overview-caption-bg',x,y,width,height,'133954')
    caption_shape=text(slide,'overview-caption','\n'.join(lines),x+16,y+6,width-32,height-12,16,'FFFFFF')
    caption_shape.text_frame.vertical_anchor=MSO_ANCHOR.MIDDLE
    for paragraph in caption_shape.text_frame.paragraphs:paragraph.alignment=PP_ALIGN.CENTER
    from .proposal_theme_spicus import rounded
    card=rect(slide,'overview-description-panel',820,280,674,337,'FFFFFF')
    rounded(card,'FFFFFF',18000)
    rect(slide,'overview-description-accent',852,309,5,34,'D52C56')
    text(slide,'overview-description-label','사업개요',873,309,565,40,26,'22262A',True)
    rect(slide,'overview-description-divider',852,365,610,1,'E2E5E8')
    text(slide,'overview-description',overview_description(report),852,389,610,204,23,'44505C')
    b=calculation_basis(report); totals={r['key']:r for r in b['totals']}; months=len(b['months'])
    values=[('3개월 추가 방문 목표','visitors','blue','276AA5'),('3개월간 월평균 추가 소비 목표','spending','jade','12867F')]
    for i,(label,key,kind,color) in enumerate(values):
        x=106+i*714
        rect(slide,f'overview-goal-{i}',x,672,674,143,'EAF2FB' if i==0 else 'E7F4F0')
        icon(slide,f'overview-goal-icon-{i}','map-pinned' if i==0 else 'coins',x+24,696,60,kind)
        text(slide,f'overview-goal-label-{i}',label,x+108,692,533,35,21,'59636E')
        amount=totals.get(key,{}).get('additional')
        value=(f"+{amount:,.0f}명" if i==0 else f"약 +{amount/months/10000:,.0f}만 원") if amount is not None and months else '목표 미설정'
        text(slide,f'overview-goal-value-{i}',value,x+108,737,533,58,34,color,True)
    text(slide,'overview-note','운영 규모를 바탕으로 제안한 계획 목표입니다. 월평균 소비 증가는 준비 기간을 포함한 사업기간 합계 ÷ 개월 수입니다.',106,848,1388,31,17,'66717A')
    slide.notes_slide.notes_text_frame.text='사업명·사업개요는 저장된 제안에서 읽고, 추가 방문은 목표 합계−ML 합계, 월평균 추가 소비는 같은 차이를 전체 사업 개월 수로 나눈다. 사진은 사업 테마별 AI 생성 예시이며 실제 지역의 시행 현장 증거가 아니다.'
    sid=next(x for x in prs.slides._sldIdLst if x.id==slide.slide_id)
    prs.slides._sldIdLst.remove(sid);prs.slides._sldIdLst.insert(2,sid)
    for i,s in enumerate(prs.slides):
        page=next((sh for sh in s.shapes if sh.name=='editorial-page'),None)
        if page is not None:page.text=f'{i+1:02d} / {len(prs.slides):02d}'
        elif i==2:
            page=text(s,'editorial-page',f'03 / {len(prs.slides):02d}',1393,45,101,28,15,'66717A')
        if page is not None:
            for p in page.text_frame.paragraphs:p.alignment=PP_ALIGN.RIGHT
