import { LockKeyhole, ShieldCheck } from 'lucide-react'
import { useState } from 'react'
import { startAdminSession, validateAdminCredentials } from '../features/admin/adminSession'
import '../App.css'

export default function AdminLoginPage({ returnTo = '/ml-test' }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const submit = (event) => {
    event.preventDefault()
    if (!validateAdminCredentials(username.trim(), password)) {
      setError('아이디 또는 비밀번호가 올바르지 않습니다.')
      return
    }
    startAdminSession()
    window.location.assign(returnTo.startsWith('/') ? returnTo : '/ml-test')
  }

  return <main className="admin-login-page">
    <form className="admin-login-card" onSubmit={submit}>
      <span className="admin-login-icon"><ShieldCheck size={28} /></span>
      <p>OLIGO-K ADMIN</p>
      <h1>관리자 페이지 로그인</h1>
      <small>AI Router와 프로젝트 구조를 확인하려면 로그인하세요.</small>
      <label>아이디<input autoFocus autoComplete="username" value={username} onChange={(event) => setUsername(event.target.value)} /></label>
      <label>비밀번호<input type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} /></label>
      {error && <strong role="alert">{error}</strong>}
      <button type="submit"><LockKeyhole size={16} />로그인</button>
      <a href="/dashboard">서비스 화면으로 돌아가기</a>
    </form>
  </main>
}
