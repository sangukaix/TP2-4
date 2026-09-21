# OLIGO React + Vite frontend

`src/main.jsx`가 React 19 앱을 시작하고 `src/App.jsx`가 페이지를 지연 로딩합니다. 공개 경로와 과거 주소 별칭은 `src/routes.js`에서 관리합니다. 현재 화면 수가 적어 별도 Router 패키지를 설치하지 않으며, 알 수 없는 주소는 404 안내를 표시합니다.

개발 서버는 `/api`를 Backend `8200`, `/ai`를 AI Server `8212`로 프록시합니다. Nginx 배포에서는 같은 경로를 각 서버로 전달합니다.

Netlify Drop에는 `npm run build` 후 생성되는 `dist` 폴더 자체를 올립니다. `public/_redirects`의 `/* /index.html 200` 규칙이 빌드 때 `dist/_redirects`로 복사되어 `/dashboard` 같은 화면 주소를 직접 열거나 새로고침해도 React의 `index.html`이 응답합니다. Netlify Drop은 정적 프런트만 배포하므로 `/api/*`, `/ai/*`, 프로젝트 구조 탐색기 `:8501` 기능을 사용하려면 별도로 공개 배포한 서버 프록시가 필요합니다.

검증 명령:

```powershell
npm test
npm run lint
npm run build
```
