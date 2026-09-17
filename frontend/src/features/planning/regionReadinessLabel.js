export function regionReadinessLabel(audit, code) {
  if (audit.refreshFailed) return '상태 재확인 필요'
  const row = audit.regions?.find((item) => item.region_code === code)
  if (row?.data_ready) return '입력자료 준비됨'
  if (row) return row.readiness_reason || '자료 확인 필요'
  return '준비 상태 미확인'
}

export function regionDataReady(audit, code) {
  return !audit.refreshFailed && audit.regions?.some((item) => item.region_code === code && item.data_ready === true) === true
}
