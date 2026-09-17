"""Audit transport/approval regressions. No live API, database or LLM calls."""
import json
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from ai_server.app.scripts import audit_all_regions as audit


class AuditCliTest(unittest.TestCase):
    def run_audit(self, args, *, changed_sql=False):
        with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
            path = Path(directory) / 'audit.json'
            stack.enter_context(patch.object(audit, 'AUDIT_PATH', path))
            stack.enter_context(patch('sys.argv', ['audit_all_regions', *args]))
            entry = SimpleNamespace(region_code='30170')
            stack.enter_context(patch.object(audit, 'list_region_data_catalog', return_value=[entry]))
            stack.enter_context(patch.object(audit, 'sql_signatures', side_effect=[
                {'30170': 'before'}, {'30170': 'after' if changed_sql else 'before'}]))
            inspect = stack.enter_context(patch.object(audit, 'inspect', return_value={
                'region_code': '30170', 'data_ready': True, 'verified': True, 'issues': []}))
            get = stack.enter_context(patch.object(audit.httpx, 'get', return_value=Mock(json=Mock(return_value=[]))))
            audit.main()
            return json.loads(path.read_text(encoding='utf-8')), inspect.call_args, get.call_args

    def test_default_targets_tp24_ai_server(self):
        _, inspected, fetched = self.run_audit([])
        self.assertEqual(fetched.args[0], 'http://127.0.0.1:8212/ai/v1/strategy-reports')
        self.assertEqual(inspected.args[2], 'http://127.0.0.1:8212')

    def test_override_is_passed_to_report_inspection(self):
        _, inspected, fetched = self.run_audit(['--api-base-url', 'http://127.0.0.1:9001/'])
        self.assertEqual(fetched.args[0], 'http://127.0.0.1:9001/ai/v1/strategy-reports')
        self.assertEqual(inspected.args[2], 'http://127.0.0.1:9001/')

    def test_data_only_does_not_fetch_saved_reports(self):
        payload, inspected, fetched = self.run_audit(['--data-only'])
        self.assertIsNone(fetched)
        self.assertEqual(inspected.args[1], [])
        self.assertEqual(payload['scope'], 'generation_inputs')

    def test_sql_change_invalidates_both_readiness_and_verification(self):
        payload, _, _ = self.run_audit([], changed_sql=True)
        row = payload['regions'][0]
        self.assertFalse(row['data_ready'])
        self.assertFalse(row['verified'])
        self.assertIn('SQL 자료 점검 도중 변경 또는 누락', row['issues'])

    def test_missing_saved_report_never_grants_verification(self):
        details = dict(latest_observed_month='202607', ml_status='available',
                       targets=['visitors', 'spending_krw', 'lodging_rate_pct', 'lodging_nights',
                                'stay_minutes', 'navigation_searches', 'lodging_searches'],
                       nationwide_available=True, peer_count=5, official_cases_allowed=4)
        with patch.object(audit, 'file_signature', return_value='unchanged'), \
             patch.object(audit, 'inspect_region', return_value=details), \
             patch('ai_server.app.main.assess_data_freshness', return_value=SimpleNamespace(can_generate=True)), \
             patch.object(audit.httpx, 'get') as get:
            row = audit.inspect(SimpleNamespace(region_code='30170', region_name='대전 서구'), [])
        get.assert_not_called()
        self.assertTrue(row['data_ready'])
        self.assertFalse(row['verified'])
        self.assertIn('기획안 실생성·목표·출력 미검증', row['issues'])


if __name__ == '__main__':
    unittest.main()
