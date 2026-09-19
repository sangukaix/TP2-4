"""One local prompt-ingestion probe, max 1 output token; no paid calls or report writes."""
import asyncio
from copy import deepcopy
import json
from pathlib import Path
import sys
import time
import requests

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from ai_server.app.llm.models import LLMRequest
from ai_server.app.llm.local_agent import run_local_agent
from ai_server.app.llm.ollama_provider import OllamaProvider
from ai_server.app.runtime_env import load_project_env

OUT=Path(__file__).parent

class Capture(OllamaProvider):
    async def _chat(self, **kwargs):
        self.captured=deepcopy(kwargs)
        raise InterruptedError('no generation in capture')

async def main():
    saved=json.loads((OUT/'local_reconstructed_request.json').read_text(encoding='utf-8'))
    env=load_project_env(ROOT)
    provider=Capture(base_url=env['LOCAL_LLM_BASE_URL'],default_model=env['OLLAMA_QWEN_MODEL'],
                     context_length=int(env['OLLAMA_QWEN_CONTEXT_LENGTH']),native_context_validation=True)
    req=LLMRequest(task='transferability',instructions='',input_payload=saved['input_payload'],schema_name='context_probe',
                   schema=saved['schema'],max_output_tokens=8000,local_evidence_tools=True)
    try:await run_local_agent(provider,req,env['OLLAMA_QWEN_MODEL'])
    except InterruptedError:pass
    call=provider.captured
    print('One local input probe, max output 1, no paid requests',flush=True)
    started=time.perf_counter()
    response=requests.post(env['LOCAL_LLM_BASE_URL'].rstrip('/')+'/api/chat',json={
        'model':env['OLLAMA_QWEN_MODEL'],'messages':call['messages'],'tools':call.get('tools'),
        'stream':False,'think':False,'truncate':False,'shift':False,'keep_alive':'15m',
        'options':{'num_ctx':int(env['OLLAMA_QWEN_CONTEXT_LENGTH']),'num_predict':1,'temperature':0.15}},timeout=600)
    body=response.json()
    result={'http_status':response.status_code,'elapsed_seconds':round(time.perf_counter()-started,2),
            'prompt_eval_count':body.get('prompt_eval_count'),'eval_count':body.get('eval_count'),
            'done_reason':body.get('done_reason'),'error':body.get('error'),
            'scope':'local reconstructed input only; not the original paid web evidence',
            'requested_context':int(env['OLLAMA_QWEN_CONTEXT_LENGTH'])}
    (OUT/'local_probe_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False),flush=True)

if __name__=='__main__':asyncio.run(main())
