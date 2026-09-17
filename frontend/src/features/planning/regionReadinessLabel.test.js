import test from 'node:test'
import assert from 'node:assert/strict'
import { regionReadinessLabel, regionDataReady } from './regionReadinessLabel.js'

test('입력자료 준비를 기획서 품질 승인으로 표시하지 않는다', () => {
  const audit = { regions: [{ region_code: '30170', data_ready: true, verified: false }] }
  assert.equal(regionReadinessLabel(audit, '30170'), '입력자료 준비됨')
  assert.equal(regionDataReady(audit, '30170'), true)
  assert.equal(regionDataReady(audit, '99999'), false)
  assert.equal(regionReadinessLabel(audit, '99999'), '준비 상태 미확인')
})

test('조회 실패 후 남은 옛 기록은 초록색 확인 상태가 아니다', () => {
  const audit = { refreshFailed: true, regions: [{ region_code: '30170', data_ready: true }] }
  assert.equal(regionReadinessLabel(audit, '30170'), '상태 재확인 필요')
  assert.equal(regionDataReady(audit, '30170'), false)
})

test('누락 자료와 재점검 사유를 유지한다', () => {
  const audit = { regions: [{ region_code: '30170', data_ready: false, readiness_reason: 'SQL 연결 확인 필요' }] }
  assert.equal(regionReadinessLabel(audit, '30170'), 'SQL 연결 확인 필요')
  assert.equal(regionDataReady(audit, '30170'), false)
  assert.equal(regionDataReady({}, '30170'), false)
})
