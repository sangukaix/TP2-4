"""Gemma-only local routing must never require or call Qwen or paid fallback."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock
from ai_server.test_llm_router import LLMRouterTests, FakeProvider, sample_request
from ai_server.app.llm.router import LLMRouter
from ai_server.app.llm.errors import LLMProviderError


class GemmaFirstTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.router = LLMRouterTests().router(self.root)
        self.router.update_config({'mode': 'local_first_gemma', 'routes': {}})

    async def test_all_local_tasks_use_gemma_even_when_qwen_is_offline(self):
        self.router.providers['qwen'].health = AsyncMock(side_effect=AssertionError('Qwen queried'))
        await self.router.preflight_local_models()
        for task in ['local_web_query_planner', 'transferability', 'planner', 'planner_revision',
                     'reviewer', 'chat_explain', 'chat_revise']:
            self.assertEqual((await self.router.generate(sample_request(task)))['provider'], 'gemma')
        status = await self.router.status()
        self.assertTrue(status['cost_policy']['gemma_only_local'])
        self.assertEqual([p['role'] for p in status['providers']], ['openai', 'gemma'])
        self.assertEqual(self.router.providers['qwen'].requests, [])
        self.assertEqual(self.router.providers['openai'].requests, [])

    async def test_paid_stages_still_limited_and_failure_never_falls_back(self):
        for task in ['evidence', 'case_study', 'final_reviewer']:
            self.assertEqual((await self.router.generate(sample_request(task)))['provider'], 'openai')
        with self.assertRaises(LLMProviderError):
            await self.router.generate(sample_request('case_study'))
        self.assertEqual(len(self.router.providers['openai'].requests), 3)
        self.router.providers['gemma'] = FakeProvider('gemma', fails=True)
        with self.assertRaises(LLMProviderError):
            await self.router.generate(sample_request('transferability'))
        self.assertEqual(len(self.router.providers['openai'].requests), 3)

    async def test_missing_gemma_blocks_before_paid_calls(self):
        self.router.providers['gemma'].health = AsyncMock(side_effect=self.router.providers['qwen'].health)
        with self.assertRaises(LLMProviderError):
            await self.router.preflight_local_models()
        self.assertEqual(self.router.providers['openai'].requests, [])

    async def test_persistence_and_previous_mode_restore(self):
        restored = LLMRouter(project_root=self.root, env_values={})
        self.assertTrue(restored.gemma_only_local)
        self.router.update_config({'mode': 'local_first', 'routes': {}})
        self.assertEqual(self.router.effective_routes()['transferability']['provider'], 'qwen')

    async def test_provider_timeout_and_context_are_separate(self):
        router = LLMRouter(project_root=self.root, env_values={
            'LOCAL_LLM_TIMEOUT_SECONDS': '1800', 'OLLAMA_GEMMA_TIMEOUT_SECONDS': '3600',
            'OLLAMA_GEMMA_CONTEXT_LENGTH': '131072', 'OLLAMA_QWEN_CONTEXT_LENGTH': '70000'})
        self.assertEqual(router.providers['gemma'].timeout_seconds, 3600)
        self.assertEqual(router.providers['qwen'].timeout_seconds, 1800)
        self.assertEqual(router.providers['gemma'].context_length, 131072)


if __name__ == '__main__':
    unittest.main()
