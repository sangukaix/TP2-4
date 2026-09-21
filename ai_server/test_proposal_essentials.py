"""Small offline regression checks; no generation, provider or database calls."""
import copy
import unittest

from ai_server.app.agents.planning_requirements import EXECUTION_EVIDENCE_RULES
from ai_server.app.operating_schedule import operating_schedule
from ai_server.app.operating_target import build_operating_target
from ai_server.test_operating_target import report


class ProposalEssentialsTest(unittest.TestCase):
    def test_selected_refund_operation_drives_capacity_not_lodging_word(self):
        data = report(title='숙박·식음 결제 인증 지원')
        data['planning_decision'] = {'selected_candidate_id': 'C1', 'design_candidates': [
            {'candidate_id': 'C1', 'mechanism': '숙박·식음 결제 증빙을 확인한 뒤 여행비 환급'}]}
        before = copy.deepcopy(data)
        plan = build_operating_target(data)
        self.assertEqual(plan['family'], 'spend_conversion')
        # D-194: default refund is 30% of the fixture's 30,000 won eligible payment.
        self.assertEqual(plan['estimate']['unit_krw'], 9000)
        self.assertEqual(data, before)

    def test_preparation_month_excluded_for_both_launch_wordings(self):
        for label in ('시범 운영 개시', '운영 시작'):
            data = report()
            data['strategies'][0]['implementation_steps'] = [
                {'task': '운영 계획 수립과 참여처 모집', 'schedule': '2026-10'},
                {'task': label, 'schedule': '2026-11 ~ 2026-12'}]
            plan = build_operating_target(data)
            self.assertEqual(plan['active_months'], ['202611', '202612'])
            self.assertEqual(plan['months'], 2)
            self.assertEqual(plan['monthly_weights'][0], 0)
            self.assertEqual(sum(i['amount'] for i in plan['estimate']['items']), plan['estimate']['total_krw'])

    def test_monitoring_alone_does_not_invent_a_launch_date(self):
        rows = [{'month': '202610'}, {'month': '202611'}]
        plan = operating_schedule(rows, {'implementation_steps': [
            {'task': '신청 건수 모니터링', 'schedule': '2026-11'}]})
        self.assertEqual(plan['schedule_basis'], 'declared_business_window')

    def test_shared_instructions_keep_idea_scope_and_unverified_conditions(self):
        for text in ('핵심 KPI 2~3개', '분모가 0', '시범 운영 개시', '지급 보류',
                     '집행 승인서나 사업 효과 입증이 아니다', '승인 플래그를 임의로 올리지 않는다'):
            self.assertIn(text, EXECUTION_EVIDENCE_RULES)


if __name__ == '__main__':
    unittest.main()
