import json
from pathlib import Path
from collections import Counter, defaultdict

root = Path(__file__).resolve().parent
audit = json.loads((root / 'audit.json').read_text(encoding='utf-8'))
files = audit['files']
matched = {m['sha256'] for m in audit['archive_matches']}
annual = defaultdict(list)
for f in files:
    if f['file'].endswith('_연도별 방문자 추이.csv'):
        for row in f['rows']:
            annual[row['축제명']].append(row)
results=[]
for name, rows in annual.items():
    rows.sort(key=lambda r:int(r['개최년도']))
    for old,new in zip(rows,rows[1:]):
        if int(new['개최년도']) != int(old['개최년도']) + 1:
            continue
        item={'name':name,'from':old['개최년도'],'to':new['개최년도']}
        for key,col in [('total','(전체)방문자수'),('outside','(외지인)방문자수'),('daily','일평균 방문자수')]:
            before,after=float(old[col]),float(new[col])
            item[key]={'before':before,'after':after,'difference':after-before,'change_pct':(after/before-1)*100 if before else None}
        item['days']=[int(old['축체기간(일)']),int(new['축체기간(일)'])]
        results.append(item)
summary = {
    'csv_exactly_already_in_local_zip':sum(f['sha256'] in matched for f in files if f['file'].endswith('.csv')),
    'csv_count':sum(f['file'].endswith('.csv') for f in files),
    'consecutive_year_pairs':len(results),
    'latest_2025_total_daily_outside_all_positive':sum(r['to']=='2025' and all(r[k]['change_pct']>0 for k in ['total','outside','daily']) for r in results),
    'examples':[r for r in results if r['name'] in ['한탄강얼음트레킹축제','화성뱃놀이축제','보령머드축제','금산인삼축제']],
    'festival_names': sorted(annual),
    'missing_values_by_type':{},
}
for suffix in ['문화관광축제 주요 지표','연도별 방문자 추이','성_연령별 내국인 방문자','목적지 검색순위']:
    selected=[f for f in files if f['file'].endswith(suffix+'.csv')]
    summary['missing_values_by_type'][suffix]={'empty_files':[f['file'] for f in selected if not f['rows']], 'rows':sum(len(f['rows']) for f in selected)}
selected = [f for f in files if f['file'].endswith('문화관광축제 주요 지표.csv')]
values = [float(r['지표값']) for f in selected for r in f['rows'] if r['지표값'] not in ('','N/A','null')]
summary['indicator_value_range']=[min(values),max(values)]
summary['top_2025_daily_growth_candidates'] = sorted([r for r in results if r['to']=='2025' and r['outside']['change_pct']>0],key=lambda r:r['daily']['change_pct'],reverse=True)[:6]
(root / 'findings.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
