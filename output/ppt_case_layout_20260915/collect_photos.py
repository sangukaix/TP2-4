"""Fetch two named Jeju facilities from the official API, without web search."""
import asyncio
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
load_dotenv(ROOT/'ai_server/.env')
load_dotenv(ROOT/'.env')
from ai_server.app.tourism_open_api import TourismOpenApiClient
from ai_server.app.proposal_cover_photo import choose_cover_photo

async def main():
    key=os.getenv('TOUR_CONTENT_LAB_API_KEY') or os.getenv('TOUR_API_SERVICE_KEY') or os.getenv('DATA_GO_KR_SERVICE_KEY') or ''
    client=TourismOpenApiClient(api_key=key,base_url='https://apis.data.go.kr/B551011/KorService2')
    results=[]
    for title in ('국립제주박물관','제주목 관아'):
        try:items=await client._get('searchKeyword2',keyword=title,numOfRows=5)
        except Exception as exc:
            print(title,type(exc).__name__)
            continue
        for item in items:
            address=str(item.get('addr1') or '')
            if not address.startswith('제주특별자치도 제주시 '):continue
            source={'source_id':'tour-api:'+str(item.get('contentid')),'source_type':'open_api',
                    'title':item.get('title'),'content_id':str(item.get('contentid')),
                    'content_type_id':str(item.get('contenttypeid')),'address':address,
                    'source_url':client.base_url,'image_url':item.get('firstimage') or ''}
            asset=choose_cover_photo({'region_name':'제주특별자치도 제주시','evidence_sources':[source]})
            if asset:
                results.append(source)
                (Path(__file__).parent/(source['content_id']+'.jpg')).write_bytes(asset[1])
                print(source['title'],source['content_id'])
                break
    path=ROOT/'ai_server/storage/application_photo_sources/50110.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print('saved',len(results))

asyncio.run(main())
