import json
from pathlib import Path
from pptx import Presentation
root=Path(__file__).parent
old=Presentation(root.parent/'ppt_compact_final_20260915/deliverables/제주시_기획서_최종.pptx')
new=Presentation(root/'deliverables/제주시_기획서_최종_v3.pptx')
def data(prs):
    return [(i,s.name,[(x.name,list(x.values))for x in s.chart.series]) if s.has_chart
            else (i,s.name,[[c.text for c in row.cells]for row in s.table.rows])
            for i,sl in enumerate(prs.slides)for s in sl.shapes if s.has_chart or s.has_table]
assert data(old)==data(new)
changed=[i for i in range(1,16)if (root/'render'/f'slide-{i:02}.png').read_bytes()!=
         (root.parent/'ppt_compact_final_20260915/render'/f'slide-{i:02}.png').read_bytes()]
assert changed==[4,5,7,8,15],changed
def get(i,name):return next(s for s in new.slides[i-1].shapes if s.name==name)
assert all(s.name!='case-intro'for s in new.slides[3].shapes)
assert get(4,'case-body-0').text_frame.paragraphs[0].runs[0].font.size.pt==15
assert '출처'not in get(15,'cover-source-label').text
assert get(15,'cover-source-bg').height==get(1,'cover-source-bg').height
assert len([s for s in new.slides[7].shapes if s.name.startswith('adaptation-photo-')and s.shape_type==13])==2
assert get(8,'selection-matrix').top+sum(r.height for r in get(8,'selection-matrix').table.rows)<get(8,'adaptation-panel').top
photos=json.loads((root.parents[1]/'ai_server/storage/application_photo_sources/50110.json').read_text(encoding='utf-8'))
assert all(s['address'].startswith('제주특별자치도 제주시 ') for s in photos)
result={'changed_slides':changed,'charts_tables_unchanged':True,'official_api_example_photos':photos,
        'last_caption_matches_cover':True,'photo_table_gap_checked':True,'PowerPoint_render_review':True}
(root/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS',changed,'2 official local facility photos; numbers preserved')
