from pathlib import Path
import json,re
from pptx import Presentation
ROOT=Path(__file__).parent
old=Presentation(ROOT.parent/'ppt_photo_growth_20260915/deliverables/제주시_기획서_최종.pptx')
new=Presentation(ROOT/'제주시_기획서_디자인최종.pptx')
def charts(p):
    return [[{'name':s.name,'series':[{'name':x.name,'values':list(x.values)} for x in s.chart.series]} for s in sl.shapes if s.has_chart] for sl in p.slides]
def tables(p):
    return [[[[c.text for c in row.cells] for row in s.table.rows] for s in sl.shapes if s.has_table] for sl in p.slides]
def links(p):
    return sorted(set(str(r.target_ref) for sl in p.slides for r in sl.part.rels.values() if r.is_external))
assert len(old.slides)==len(new.slides)==15
assert charts(old)==charts(new),'Chart values changed'
assert tables(old)==tables(new),'Table contents changed'
assert links(old)==links(new),'Source links changed'
# Only the user-requested heading and 0-section, line-color wording, and
# decorative cover/contents typography may change. All body text stays.
normalize=lambda t:re.sub(r'\s+','',t)
changes=[]
for i,(a,b) in enumerate(zip(old.slides,new.slides)):
    if i in (0,1,14):continue
    original={s.name:normalize(s.text) for s in a.shapes if s.has_text_frame and s.text}
    current={s.name:normalize(s.text) for s in b.shapes if s.has_text_frame and s.text}
    for name,value in original.items():
        if value!=current.get(name):
            changes.append({'slide':i+1,'name':name,'before':value,'after':current.get(name)})
            assert (i==2 and name in ('title','editorial-kicker')) or name=='comparison-note',(i,name)
result={'slides':15,'charts_unchanged':charts(new),'tables_identical':True,'source_links_identical':True,'source_links':len(links(new)),'approved_text_changes':changes}
(ROOT/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('15 slides: chart values, tables and all source links preserved. Approved wording changes only.')
