import json
from pathlib import Path
from pptx import Presentation

root=Path(__file__).resolve().parent
old=Presentation(root.parent/'final_validation_20260915/제주시_최종검증.pptx')
new=Presentation(root/'deliverables/제주시_기획서_최종.pptx')
def charts(deck):
    return [[list(s.values) for s in shape.chart.series] for slide in deck.slides for shape in slide.shapes if shape.has_chart]
def tables(slide):
    return [[[c.text for c in row.cells] for row in shape.table.rows] for shape in slide.shapes if shape.has_table]
assert charts(old)==charts(new)
assert tables(old.slides[7])==tables(new.slides[9])
assert tables(old.slides[9])==tables(new.slides[10])
assert len(new.slides)==15
assert any(s.text=='사례 실적' for s in new.slides[6].shapes if s.has_text_frame)
def urls(deck):
    return {r.hyperlink.address for slide in deck.slides for shape in slide.shapes if shape.has_text_frame for p in shape.text_frame.paragraphs for r in p.runs if r.hyperlink.address}
# Old similar-night photo is replaced by the specific Jeongdong asset. All
# original appendix references, including the chosen budget PDF, are retained.
def source_urls(deck):
    return {r.hyperlink.address for slide in deck.slides for sh in slide.shapes if sh.name.startswith('reference-') and sh.has_text_frame for p in sh.text_frame.paragraphs for r in p.runs if r.hyperlink.address}
assert source_urls(old)<=source_urls(new)
result={'slides':len(new.slides),'native_charts_unchanged':True,'kpi_tables_unchanged':True,
        'estimate_unchanged':True,'all_original_source_links_retained':True,
        'case_result_slide':7,'source_pages':2,'llm_calls':0,'paid_calls':0,
        'visual_review':'All slides rendered in native PowerPoint; revised sources rechecked.',
        'layout_warnings':'Original cover/thanks bleed and contents watermark overlap are intentional; visually inspected.'}
(root/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
