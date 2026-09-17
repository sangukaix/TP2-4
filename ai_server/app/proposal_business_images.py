"""Dedicated, generated business illustrations; no case/region-photo reuse."""
from pathlib import Path
import hashlib
from .case_recommendation import operation_family
ROOT=Path(__file__).resolve().parents[1]/'assets'/'proposal_business'
THEMES={
 'spend_conversion':('refund','관광객 쿠폰·환급 이용'),
 'night_time_experience':('night','야간 관광 프로그램'),
 'stay_conversion':('stay','숙박·체류 관광'),
 'access_and_mobility':('mobility','관광 교통 연계'),
 'experience_product':('experience','지역 문화·체험'),
 'reservation_conversion':('reservation','관광 프로그램 예약·입장'),
 'return_visit':('reservation','관광객 이용 혜택'),
 'other_operation':('experience','지역 관광 프로그램'),
}

def select_business_image(report, prs):
    strategy=(report.get('strategies') or [{}])[0]
    decision=report.get('planning_decision') or {}
    selected=next((c for c in decision.get('design_candidates') or [] if c.get('candidate_id')==decision.get('selected_candidate_id')), {})
    family=operation_family({'mechanism':selected.get('mechanism') or strategy.get('solution'),'title':strategy.get('title')})
    key,label=THEMES.get(family,THEMES['other_operation'])
    path=ROOT/(key+'.png')
    if not path.is_file():raise ValueError(f'사업 이미지 자산이 없습니다: {key}')
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape,'image') and hashlib.sha256(shape.image.blob).hexdigest()==digest:
                raise ValueError('사업개요 전용 이미지가 다른 슬라이드에서 이미 사용되었습니다.')
    return {'path':path,'family':family,'caption':label+' · AI 생성 예시 이미지',
            'sha256':digest,'kind':'generated_illustration','source':'OpenAI image generation',
            'note':'실제 지역·사업 현장의 기록 사진이 아닙니다.'}
