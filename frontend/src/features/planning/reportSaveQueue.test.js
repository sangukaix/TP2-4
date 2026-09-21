import test from 'node:test'
import assert from 'node:assert/strict'
import { createReportSaveQueue } from './reportSaveQueue.js'
const tick = () => new Promise((resolve) => setImmediate(resolve))
test('same report writes finish in edit order; different reports do not block', async () => {
  const calls = [], completions = []
  const save = createReportSaveQueue((id, region, value) => new Promise((resolve) => { calls.push([id, value]); completions.push(resolve) }))
  const first = save('A', '1', 1), second = save('A', '1', 2), other = save('B', '2', 3)
  await tick()
  assert.deepEqual(calls, [['A', 1], ['B', 3]])
  completions[0](); completions[1](); await tick()
  assert.deepEqual(calls[2], ['A', 2]); completions[2]()
  await Promise.all([first, second, other])
})
test('failed save rejects to caller but does not discard the next edit', async () => {
  let count = 0
  const save = createReportSaveQueue(async () => { if (++count === 1) throw new Error('offline'); return 'saved' })
  const first = save('A', '1', 1), second = save('A', '1', 2)
  await assert.rejects(first, /offline/)
  assert.equal(await second, 'saved')
})
