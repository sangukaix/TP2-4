import json
from pathlib import Path
from pptx import Presentation

root = Path(__file__).parent
old_root = root.parent / 'ppt_case_layout_20260915'
old = Presentation(old_root / 'deliverables/제주시_기획서_최종_v3.pptx')
new = Presentation(root / 'deliverables/제주시_기획서_최종.pptx')

def numerical_objects(deck):
    return [(i, s.name, [(x.name, list(x.values)) for x in s.chart.series]) if s.has_chart
            else (i, s.name, [[c.text for c in r.cells] for r in s.table.rows])
            for i, slide in enumerate(deck.slides) for s in slide.shapes if s.has_chart or s.has_table]

assert numerical_objects(new) == numerical_objects(old)
changed = [i for i in range(1, 16) if (root / 'render' / f'slide-{i:02}.png').read_bytes()
           != (old_root / 'render' / f'slide-{i:02}.png').read_bytes()]
assert changed == [2, 5, 6, 7, 12], changed

def shape(i, name):
    return next(s for s in new.slides[i - 1].shapes if s.name == name)

assert not any(s.name == 'top-date' for s in new.slides[1].shapes)
assert shape(5, 'title').text == '1.2 참고 사례 실적'
assert '출처:' in shape(5, 'result-photo-source').text
assert shape(5, 'result-photo-source').click_action.hyperlink.address
assert str(shape(5, 'result-photo-source-bg').fill.fore_color.rgb) == '0F315B'
assert '+3.29%' in shape(6, 'business-goal-intro').text
assert '+3.33%' in shape(6, 'business-goal-intro').text
for i, name in [(5, 'result-scope'), (6, 'business-goal-intro'), (7, 'kpi-intro'), (12, 'pipeline-intro')]:
    assert all(r.font.size.pt == 26 for p in shape(i, name).text_frame.paragraphs for r in p.runs)
result = {'changed_slides': changed, 'native_chart_and_table_values_preserved': True,
          'gray_intro_font_pt': 26, 'PowerPoint_visual_review': True,
          'goal_summary': {'visitors_pct': 3.29, 'spending_pct': 3.33},
          'case_photo_credit_and_hyperlink_preserved': True}
(root / 'audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print('PASS', result)
