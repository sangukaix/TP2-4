"""Read-only audit of the user-supplied festival downloads; no production imports."""
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
SOURCE = Path(r"\\192.168.0.17\Users\mbca\공유폴더\(2차 프로젝트) 생성형 AI 웹앱 기획 및 개발 프로젝트\제출폴더\4조_현상욱\테마별분석\문화관광축제 현황")
SNAPSHOT = ROOT / 'source_snapshot'
records = []
for path in sorted(SOURCE.rglob('*')):
    if not path.is_file():
        continue
    raw = path.read_bytes()
    relative = path.relative_to(SOURCE)
    local = SNAPSHOT / relative
    local.parent.mkdir(parents=True, exist_ok=True)
    if local.exists() and local.read_bytes() != raw:
        raise RuntimeError(f'Snapshot changed: {relative}')
    local.write_bytes(raw)
    item = {'file': str(relative), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
    if path.suffix.lower() == '.csv':
        for encoding in ('utf-8-sig', 'cp949'):
            try:
                content = raw.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise RuntimeError(f'Cannot decode: {relative}')
        reader = csv.DictReader(io.StringIO(content))
        item.update(encoding=encoding, columns=reader.fieldnames, rows=list(reader))
    records.append(item)

schemas = Counter(tuple(r['columns']) for r in records if 'columns' in r)
groups = defaultdict(list)
annual = []
indicators = []
for r in records:
    groups[Path(r['file']).parent.name].append(r)
    if r['file'].endswith('_연도별 방문자 추이.csv'):
        annual.extend(dict(row, source=r['file']) for row in r['rows'])
    if r['file'].endswith('_문화관광축제 주요 지표.csv'):
        indicators.extend(dict(row, source=r['file']) for row in r['rows'])

archive = ROOT.parents[1] / 'data/raw/downloads/rawdata.zip'
zip_matches = []
source_hashes = {r['sha256'] for r in records}
with zipfile.ZipFile(archive) as z:
    for entry in z.infolist():
        if not entry.filename.lower().endswith('.csv'):
            continue
        digest = hashlib.sha256(z.read(entry)).hexdigest()
        if digest in source_hashes:
            zip_matches.append({'entry': entry.filename, 'sha256': digest})

summary = {
    'source': str(SOURCE),
    'folder_count': len([p for p in SOURCE.iterdir() if p.is_dir()]),
    'file_count': len(records),
    'extensions': dict(Counter(Path(r['file']).suffix for r in records)),
    'schemas': [{'columns': list(k), 'files': v} for k, v in schemas.items()],
    'incomplete_folders': {k: [Path(v['file']).name for v in vals] for k, vals in groups.items() if k != '.' and len(vals) != 4},
    'annual_row_count': len(annual),
    'years': dict(Counter(r['개최년도'] for r in annual)),
    'festival_year_counts': dict(Counter(Counter(r['축제명'] for r in annual).values())),
    'indicator_names': sorted({r['구분명'] for r in indicators}),
    'indicator_groups': sorted({r['그룹명'] for r in indicators}),
    'rawdata_zip_exact_matches': len(zip_matches),
}
(ROOT / 'audit.json').write_text(json.dumps({'summary': summary, 'files': records, 'archive_matches': zip_matches}, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False, indent=2))
for name in ['한탄강얼음트레킹축제', '화성뱃놀이축제', '금산인삼축제', '제주들불축제', '보령머드축제']:
    print(json.dumps({'festival': name, 'annual': [r for r in annual if r['축제명']==name]}, ensure_ascii=False))
