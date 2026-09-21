import assert from 'node:assert/strict'
import test from 'node:test'
import { validateAdminCredentials } from './adminSession.js'

test('교육용 관리자 계정만 허용한다', () => {
  assert.equal(validateAdminCredentials('admin', '1234'), true)
  assert.equal(validateAdminCredentials('admin', '12345'), false)
  assert.equal(validateAdminCredentials('student', '1234'), false)
})
