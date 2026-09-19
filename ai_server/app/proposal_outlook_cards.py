"""Restyle comparison contents while preserving approved outer geometry."""
import json
from pptx.util import Pt
from pptx.dml.color import RGBColor
from .proposal_layout_v7 import EMU,text,rect,fit_text
from .proposal_theme_spicus import get,pos,rounded
from .proposal_infographics import icon


def restyle_outlook_cards(prs):
    for slide in prs.slides:
        if get(slide,'growth-card-0') is None:continue
        try:result=json.loads(slide.notes_slide.notes_text_frame.text)['comparison']
        except (ValueError,KeyError,TypeError):continue
        for i,(key,symbol,color) in enumerate([('visitors','users','27649B'),('spending','coins','187C70')]):
            panel=get(slide,f'growth-card-{i}');y=panel.top/EMU
            row=result['metrics'][key]
            for name in (f'growth-gap-{i}',):
                sh=get(slide,name)
                if sh is not None:sh._element.getparent().remove(sh._element)
            icon(slide,f'growth-metric-icon-{i}',symbol,578,y+18,37,'ocean' if i==0 else 'jade')
            label=get(slide,f'growth-label-{i}');pos(label,631,y+17,365,42);fit_text(label,label.text,25,'26333F',True)
            total=sum(row['forecast']);value=f'{total/10000:,.1f}만 명' if i==0 else f'{total/1e8:,.1f}억 원'
            text(slide,f'growth-total-caption-{i}','3개월 예측 합계',1124,y+12,338,26,16,'75808B')
            total_shape=get(slide,f'growth-total-{i}');pos(total_shape,1124,y+38,338,37);fit_text(total_shape,value,25,color,True)
            rect(slide,f'growth-inner-divider-{i}',580,y+81,893,1,'EBEFF3')
            chart=get(slide,f'growth-chart-{i}');pos(chart,571,y+100,650,113)
            chart.chart.plots[0].data_labels.font.size=Pt(14)
            chart.chart.plots[0].data_labels.font.color.rgb=RGBColor.from_string('26333F')
            chart.chart.category_axis.tick_labels.font.size=Pt(13)
            delta=row['gap_pp'];negative=delta<0
            fill='FFF1F4' if negative else 'E9F5F1';ink='BA3153' if negative else '187C70'
            badge=rect(slide,f'growth-gap-badge-{i}',1240,y+103,232,105,fill);rounded(badge,fill,13000)
            text(slide,f'growth-gap-caption-{i}','전국 평균보다',1256,y+118,200,26,17,'687583')
            direction='낮음' if negative else '높음' if delta>0 else '동일'
            text(slide,f'growth-gap-inline-{i}',f'{abs(delta):.2f}% {direction}',1256,y+151,208,42,26,ink,True)
        note=get(slide,'purpose-note')
        if note is not None:
            copy=note.text+'\n카드의 높음·낮음은 두 증가율의 차이(퍼센트포인트)입니다.'
            fit_text(note,copy,15,'667480')
        period=get(slide,'purpose-period')
        if period is not None:
            start,end=result['months'][0],result['months'][-1]
            fit_text(period,f'향후 3개월 전망 · {start[:4]}.{start[4:]} ~ {end[:4]}.{end[4:]}',26,'62666C')
            from .proposal_theme_spicus import center
            center(period)
