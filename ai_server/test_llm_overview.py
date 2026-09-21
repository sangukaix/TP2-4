"""Inspect routing without calling provider health or inference."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock
from ai_server.app.llm.router import LLMRouter


class OverviewTests(unittest.TestCase):
    def test_gemma_summary_uses_effective_routes_without_network(self):
        with TemporaryDirectory() as directory:
            router = LLMRouter(project_root=Path(directory), env_values={'LLM_MODE': 'local_first_gemma', 'OLLAMA_GEMMA_MODEL': 'gemma-test', 'OLLAMA_GEMMA_CONTEXT_LENGTH': '70000'})
            for provider in router.providers.values(): provider.health = AsyncMock(side_effect=AssertionError('health called'))
            result = router.runtime_summary()
            for task in ('transferability', 'planner', 'reviewer'):
                self.assertEqual(result['effective_routes'][task]['provider'], 'gemma')
                self.assertEqual(result['effective_routes'][task]['model'], 'gemma-test')
            self.assertEqual(result['cost_policy']['local_context_lengths'], {'gemma': 70000})
            self.assertFalse(result['cost_policy']['automatic_paid_fallback'])
            for provider in router.providers.values(): provider.health.assert_not_called()

    def test_openai_only_does_not_advertise_local_fallback(self):
        with TemporaryDirectory() as directory:
            router = LLMRouter(project_root=Path(directory), env_values={'LLM_MODE': 'openai_only'})
            self.assertFalse(router.runtime_summary()['cost_policy']['automatic_paid_fallback'])
