const ADMIN_SESSION_KEY = 'oligo_admin_session'

export const ADMIN_USERNAME = 'admin'
export const ADMIN_PASSWORD = '1234'

export function validateAdminCredentials(username, password) {
  return username === ADMIN_USERNAME && password === ADMIN_PASSWORD
}

export function isAdminSessionAuthenticated(storage = globalThis.sessionStorage) {
  try { return storage?.getItem(ADMIN_SESSION_KEY) === 'authenticated' }
  catch { return false }
}

export function startAdminSession(storage = globalThis.sessionStorage) {
  storage?.setItem(ADMIN_SESSION_KEY, 'authenticated')
}

export function endAdminSession(storage = globalThis.sessionStorage) {
  storage?.removeItem(ADMIN_SESSION_KEY)
}
