import json
from hashlib import sha256
from pathlib import Path
from pptx import Presentation

root=Path(__file__).parent
previous=root.parent/'ppt_cover_20260915'
changed=[p.name for p in (root/'render').glob('*.png')
         if p.read_bytes()!=(previous/'render'/p.name).read_bytes()]
assert changed==['slide-01.png', 'slide-15.png'],changed
old=Presentation(previous/'deliverables/제주시_기획서_최종.pptx')
new=Presentation(root/'deliverables/제주시_기획서_최종.pptx')
def data(prs):
    return [(i, 'chart', [(s.name,list(s.values)) for s in shape.chart.series])
            if shape.has_chart else (i,'table',[[c.text for c in r.cells] for r in shape.table.rows])
            for i,slide in enumerate(prs.slides) for shape in slide.shapes
            if shape.has_chart or shape.has_table]
assert data(old)==data(new)
photos=[]
for i in (0,2,14):
    pics=[s for s in new.slides[i].shapes if s.shape_type==13]
    pic=max(pics,key=lambda s:s.width*s.height)
    photos.append(sha256(pic.image.blob).hexdigest())
assert len(set(photos))==3
caption=next(s for s in new.slides[14].shapes if s.has_text_frame and '고내포구' in s.text)
assert any(s.fill.type==1 and str(s.fill.fore_color.rgb)=='0F315B'
           for s in new.slides[14].shapes if hasattr(s,'fill'))
result={'changed_slides':changed,'three_distinct_photos':True,'blue_caption':True,
        'charts_tables_identical':True,'selected_photo':json.loads((root/'photo-source.json').read_text(encoding='utf-8'))}
(root/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS: slides 1 and 15 only; three distinct photos; charts/tables unchanged; blue caption')

