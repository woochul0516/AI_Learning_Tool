## 나를 소개하는 웹페이지 처음부터 만들기
- JS / Web Development 과제 요구사항을 완벽히 준수하여 순수 바닐라 자바스크립트(ES6+)와 최신 웹 표준 기술만으로 제작한 반응형 개인 포트폴리오 웹사이트입니다.
- 외부 프레임워크(React 등) 없이 "사용자 이벤트 → 상태 변경(State) → DOM 렌더링" 흐름을 단일 상태 객체 기반으로 명확하게 추상화하여 구현했습니다.

### 배포 링크 및 개요
- 배포 URL: [배포 중단]
- GitHub 저장소: [https://github.com/woochul0516/AI_Learning_Tool/tree/main/B1-1]

### 사용 기술 및 개발 환경 (Tech Stack)
- Language: `HTML5` (시맨틱 마크업), `CSS3`, `JavaScript (ES6+)`
- API / Service: `GitHub REST API`, `EmailJS Browser SDK`
- Icons & Fonts: `Font Awesome Icons`, `Google Fonts`
- Environment: `VS Code`, `Live Server`, `GitHub Pages`

### 주요 기능 및 미션 요구사항 충족 내역
1. 상태 관리 패턴 (State Management)
단일 상태 객체 (state) 구현: `theme`, `repos`, `filter`, `loading`, `error`, `formErrors` 상태를 하나의 중앙 객체로 관리하여 UI와 완벽하게 동기화했습니다.

상태 객체 예시:
```javascript
const state = {
  theme: localStorage.getItem('theme') || 'light',
  repos: [],
  filter: 'all',
  loading: false,
  error: null,
  formErrors: {}
};
```

상태-렌더링 연결 사례:
- 다크 모드: 버튼 클릭 → `state.theme` 변경 → `DOM attributes` 및 `localStorage` 반영
- GitHub API: `Fetch` 시작/성공/실패 → `state.loading` / `error` / `repos 변경` → Projects UI 상태별 차등 렌더링
- 프로젝트 필터링: 언어 클릭 → `state.filter` 변경 → 배열 `.filter()` 후 카드 재렌더링
- 폼 유효성 검사: 제출 → `state.formErrors` 업데이트 → 에러 메시지 DOM 반영

2. 시맨틱 HTML & CSS 레이아웃
index.html을 보면 전체를 `<div>`로 도배하지 않고, 상단은 `<header>`와 `<nav>`, 본문은 `<main>`, 각 구역은 `<section id="about">`, `<section id="projects">`, 하단은 `<footer>`로 작성

- Flexbox & Grid 조합:
    - Flexbox (`css/style.css` 140줄): `.nav-container`에 `display: flex; justify-content: space-between;`을 써서 로고는 왼쪽, 메뉴는 오른쪽에 1차원(한 줄) 정렬.
    - Grid (`css/style.css` 330줄): `.projects-grid`에 `display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));`를 써서 프로젝트 카드가 화면 크기에 맞춰 2차원(바둑판) 배치.
- CSS 변수(`:root`):
    - `css/style.css` 11줄: `:root`에 `--accent-color: #4f46e5;`와 테마 색상들을 미리 변수로 선언. 다크모드(`[data-theme="dark"]`)가 될 때 이 변수 값만 바꿔주면 사이트 전체 색상이 일괄 변경.
- `onclick` 대신 `addEventListner`를 쓴 이유
    - `index.html` 태그 안에 `onclick="..."`을 넣지 않고, `js/main.js` 하단(224줄)처럼 `themeToggleBtn.addEventListener('click', toggleTheme)` 방식으로 바인딩. HTML과 JS 코드가 서로 깔끔하게 분리
- API 성공/실패 분기(`async/await` & `try/catch`)
    - `js/main.js` 74줄 (`fetchGitHubRepos` 함수):
        - `try` 문 안에서 `await fetch(...)`로 GitHub 데이터를 기다립니다. 만약 응답(`response.ok`)에 문제가 있거나 403 에러(요청 제한)가 나면 `throw new Error()`를 던집니다.
        - 에러가 발생하면 곧바로 `catch (err)` 문으로 이동하여 `state.error`에 에러 문구를 담고 `renderProjects()`를 불러 에러 화면을 띄웁니다.
- 배열 메서드(`filter`, `map`)의 활용
    - `js/main.js` 124~128줄:
        - `filter()`: `state.repos.filter(repo => repo.language === state.filter)`로 내가 선택한 버튼 언어(Python, JS 등)만 걸러냄.
        - `map()`: 걸러낸 데이터에서 `{ name, description, html_url, stargazers_count, language }`를 추출하여 HTML 카드 문맥(`project-card`)으로 바꾼 뒤 화면에 뿌려줌.
- 모바일 퍼스트로 작성한 이유:
    - `css/style.css`: 기본 스타일을 모바일 화면 크기 기준으로 먼저 작성, 아래쪽에 `@media (min-width: 768px)`로 큰 화면용 스타일을 덧붙임
    - 작은 화면(모바일)의 필수 요소부터 안전하게 완성한 뒤 넓은 화면으로 확장하는 것이 디자인 구조를 단순하고 튼튼하게 유지해 주기 때문

3. GitHub REST API 연동 및 상태별 UI
- async/await 및 fetch를 활용하여 https://api.github.com/users/woochul0516/repos?sort=updated&per_page=10 데이터를 수신하고 API 403 Rate Limit 예외 처리 및 try...catch 에러 핸들링을 적용했습니다.

- 4가지 UI 상태 완벽 대응:
    - 로딩 상태: `@keyframes spin` 기반의 `.spinner` 애니메이션 및 안내 메시지 표시 `(state.loading = true)`
    - 성공 상태: `Array.prototype.map`, 구조 분해 할당`({ name, description, html_url, stargazers_count, language })`, 템플릿 리터럴을 활용해 동적 카드 `.project-card` 렌더링
    - 에러 상태: `.error-msg` 출력 및 `#retry-btn` 클릭 시 `fetchGitHubRepos()` 재요청 기능 제공
    - 빈 데이터 상태: 조건 만족 프로젝트 부재 시 안내 메시지 출력 `(filteredRepos.length === 0)`

4. Contact Form 유효성 검사 및 실제 메일 발송 (EmailJS 연동)
    - `e.preventDefault()`를 통한 기본 폼 제출 방지
    - 이름(username), 메시지(message) 필수 입력값 검증 및 정규표현식`(/^[^\s@]+@[^\s@]+.[^\s@]+$/)`을 활용한 이메일(email) 포맷 유효성 검사
    - 보너스 미션 달성 (EmailJS): `External CDN (@emailjs/browser@3)` 연결 및 `emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, {...})` 호출로 백엔드 없이 지정된 이메일함으로 실시간 전송
    - 메일 전송 중 버튼 비활성화 `(submitBtn.disabled = true, textContent = '전송 중...')` 및 `#form-success` 영역을 통한 성공/실패 메시지 UX 처리

5. UI 인터랙션 및 애니메이션
    - 타이핑 효과 (보너스 미션): `initTypingEffect()` 함수로 `Hero` 섹션의 `#typing-text` 요소에 자바스크립트 기반 타자기 효과 구현 `(Jung Woochul)`
    - 프로젝트 카테고리 필터링 (보너스 미션): `e.target.dataset.filter` 값을 읽어 `Array.prototype.filter` 기반 기술 언어별 카드 스크리닝
    - Intersection Observer API: `initScrollAnimation()`을 통해 `.fade-in-section` 클래스를 관찰하여 스크롤 시 `is-visible` 클래스 추가 `(opacity: 1, transform: translateY(0))`
    - 스크롤 UX: 스크롤 60px 이상 시 헤더 그림자 및 배경 처리 `(#header.scrolled)`, 스크롤 300px 이상 시 상단 이동 버튼 노출 `(#scroll-top.show)` 및 클릭 시 `window.scrollTo({ top: 0, behavior: 'smooth' })` 동작


### 프로젝트 구조 (Directory Structure)
```text
├── index.html          # 시맨틱 구조 마크업 및 외부 스크립트(EmailJS, FontAwesome) 연결
├── css/
│   └── style.css       # CSS 변수, 다크모드, Flex/Grid 및 반응형 스타일
└── js/
    └── main.js         # 상태 관리, DOM 이벤트, API 연동, EmailJS 핵심 로직
```


### 프로젝트 실행 화면 (Screenshots)
| 화면 구분 | 설명 | 이미지 |
| :--- | :--- | :--- |
| **데스크톱 (Desktop)** | 메인 화면 및 카드 레이아웃 | ![Desktop](images/desktop.png) |
| **모바일 & 햄버거 메뉴** | 반응형 모바일 메뉴 동작 화면 | ![Mobile](images/mobile.png) |
| **다크 모드 (Dark Mode)** | 다크 테마 적용 화면 | ![DarkMode](images/darkmode.png) |
| **이메일 수신 (Contact Mail)** | EmailJS를 통해 실제 수신된 문의 메일 | ![ContactEmail](images/email.png) |

### 학습 및 성찰 (Mission Takeaways)
- 시맨틱 마크업의 이유: `header`, `main`, `article`, `section` 등의 시맨틱 태그를 명확히 구분하여 작성함으로써 웹 접근성(A11y) 향상과 검색엔진 최적화(SEO)의 중요성을 체득했습니다.
- Flexbox vs Grid: `Navigation`과 `Header Actions` 구조에서는 1차원 레이아웃 정렬을 위해 Flexbox를 사용하고, Skills 및 Projects 카드 영역에는 2차원 반응형 배치를 위해 CSS Grid를 선택하여 효용성을 확인했습니다.
- 상태 관리의 체득: 사용자 이벤트 발생 시 DOM을 직접 난잡하게 변경하는 대신, 단일 상태 객체(`state`)를 업데이트하고 상태에 맞게 DOM을 렌더링하는 순수 바닐라 JS 기반의 상태 중심 설계 원리를 익혔습니다.