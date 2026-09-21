/** Serialize writes per report so a slower older request cannot overwrite a newer edit. */
export function createReportSaveQueue(save) {
  const tails = new Map()
  return (id, regionCode, report) => {
    const previous = tails.get(id) || Promise.resolve()
    const request = previous.catch(() => {}).then(() => save(id, regionCode, report))
    tails.set(id, request)
    const cleanup = () => { if (tails.get(id) === request) tails.delete(id) }
    request.then(cleanup, cleanup)
    return request
  }
}
