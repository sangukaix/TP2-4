"""Two bounded local probes; no cloud requests or report writes."""
import asyncio
from copy import deepcopy
import json
from pathlib import Path
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ai_server.app.runtime_env import load_project_env
from ai_server.app.llm.ollama_provider import OllamaProvider
from ai_server.app.llm.models import LLMRequest
from ai_server.app.llm.local_agent import run_local_agent
from jsonschema import validate

OUT = Path(__file__).parent
results = {}

def save():
    (OUT / 'result.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')

class Capture(OllamaProvider):
    async def _chat(self, **kwargs):
        self.captured = deepcopy(kwargs)
        raise InterruptedError('capture only')

async def main():
    env = load_project_env(ROOT)
    model = env['OLLAMA_QWEN_MODEL']
    base = env['LOCAL_LLM_BASE_URL'].rstrip('/')
    ctx = int(env['OLLAMA_QWEN_CONTEXT_LENGTH'])
    results.update(model=model, requested_context=ctx, paid_calls=0)
    provider = OllamaProvider(base_url=base, default_model=model, context_length=ctx,
                              timeout_seconds=600, native_context_validation=True)
    schema = {'type': 'object', 'properties': {
        'capacity': {'type': 'integer'}, 'participants': {'type': 'integer'},
        'additional_visitors': {'type': 'integer'}, 'is_observed_effect': {'type': 'boolean'}},
        'required': ['capacity','participants','additional_visitors','is_observed_effect'],
        'additionalProperties': False}
    started = time.perf_counter()
    msg, usage = await provider._chat(model=model, messages=[{'role':'user','content':
        '제주시 운영 계획: 6개 거점 × 월 8일 × 3개월 × 하루 2회 × 회당 40명. '
        '참여 목표는 정원의 75%, 추가 방문은 참여의 30%다. 정원, 참여, 추가 방문을 계산하라. '
        '이 값은 계획이며 관측된 사업효과인지 여부는 false다. JSON만 반환하라.'}],
        schema=schema, max_output_tokens=256, think=False)
    answer = json.loads(msg['content']); validate(answer, schema)
    expected = dict(capacity=11520,participants=8640,additional_visitors=2592,is_observed_effect=False)
    results['short_json'] = dict(elapsed_seconds=round(time.perf_counter()-started,2),usage=usage,
                                answer=answer,passed=answer==expected)
    print(json.dumps(results['short_json'],ensure_ascii=False),flush=True); save()
    with urllib.request.urlopen(base+'/api/ps',timeout=20) as r: results['loaded_after_short']=json.load(r)
    save(); print('Starting reconstructed Cheorwon input probe (one output token).',flush=True)
    saved = json.loads((ROOT/'output/context_error_20260916/local_reconstructed_request.json').read_text(encoding='utf-8'))
    capture=Capture(base_url=base,default_model=model,context_length=ctx,native_context_validation=True)
    req=LLMRequest(task='transferability',instructions='',input_payload=saved['input_payload'],
                   schema_name='context_probe',schema=saved['schema'],max_output_tokens=8000,local_evidence_tools=True)
    try: await run_local_agent(capture,req,model)
    except InterruptedError: pass
    call=capture.captured
    body={'model':model,'messages':call['messages'],'tools':call.get('tools'),
          'stream':False,'think':False,'truncate':False,'shift':False,'keep_alive':'15m',
          'options':{'num_ctx':ctx,'num_predict':1,'temperature':0.15}}
    started=time.perf_counter()
    request=urllib.request.Request(base+'/api/chat',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=600) as r: response=json.load(r)
    results['input_probe']={k:response.get(k) for k in ('prompt_eval_count','eval_count','done_reason','load_duration','prompt_eval_duration','eval_duration')}
    results['input_probe'].update(elapsed_seconds=round(time.perf_counter()-started,2),
        scope='reconstructed local input; excludes original paid web evidence; one token, not full report quality')
    with urllib.request.urlopen(base+'/api/ps',timeout=20) as r: results['loaded_after_input']=json.load(r)
    save(); print(json.dumps(results,ensure_ascii=False),flush=True)

if __name__=='__main__':
    try: asyncio.run(main())
    except Exception as exc:
        results['error']=dict(type=type(exc).__name__,message=str(exc)); save(); raise
