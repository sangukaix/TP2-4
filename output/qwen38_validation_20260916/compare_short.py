"""Same short question on previous 14B; local only."""
import asyncio
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from ai_server.app.runtime_env import load_project_env
from ai_server.app.llm.ollama_provider import OllamaProvider

async def main():
    env=load_project_env(ROOT)
    p=OllamaProvider(base_url=env['LOCAL_LLM_BASE_URL'],default_model='qwen3:14b',
        context_length=40960,timeout_seconds=300,native_context_validation=True)
    schema={'type':'object','properties':{
        'capacity':{'type':'integer'},'participants':{'type':'integer'},
        'additional_visitors':{'type':'integer'},'is_observed_effect':{'type':'boolean'}},
        'required':['capacity','participants','additional_visitors','is_observed_effect'],
        'additionalProperties':False}
    started=time.perf_counter()
    msg,usage=await p._chat(model='qwen3:14b',messages=[{'role':'user','content':
        '제주시 운영 계획: 6개 거점 × 월 8일 × 3개월 × 하루 2회 × 회당 40명. '
        '참여 목표는 정원의 75%, 추가 방문은 참여의 30%다. 정원, 참여, 추가 방문을 계산하라. '
        '이 값은 계획이며 관측된 사업효과인지 여부는 false다. JSON만 반환하라.'}],
        schema=schema,max_output_tokens=256,think=False)
    answer=json.loads(msg['content'])
    result=dict(model='qwen3:14b',elapsed_seconds=round(time.perf_counter()-started,2),
        usage=usage,answer=answer,passed=answer==dict(capacity=11520,participants=8640,
        additional_visitors=2592,is_observed_effect=False),scope='one short question, not full report quality benchmark')
    Path(__file__).with_name('baseline_short.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False),flush=True)

if __name__=='__main__': asyncio.run(main())
