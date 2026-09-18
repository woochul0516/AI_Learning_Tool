## Portfolio Web Application
JS / Web Development 과제 요구사항을 완벽히 준수하여 순수 바닐라 자바스크립트(ES6+)와 최신 웹 표준 기술만으로 제작한 반응형 개인 포트폴리오 웹사이트입니다.
외부 프레임워크(React 등) 없이 "사용자 이벤트 → 상태 변경(State) → DOM 렌더링" 흐름을 단일 상태 객체 기반으로 명확하게 추상화하여 구현했습니다.

### 배포 링크 및 개요
배포 URL: [https://woochul0516.github.io/AI_Learning_Tool/tree/main/B1-1]
GitHub 저장소: [https://github.com/woochul0516/AI_Learning_Tool/tree/main/B1-1]

### 사용 기술 및 개발 환경 (Tech Stack)
Language: `HTML5` (시맨틱 마크업), `CSS3`, `JavaScript (ES6+)`
API / Service: `GitHub REST API`, `EmailJS Browser SDK`
Icons & Fonts: `Font Awesome Icons`, `Google Fonts`
Environment: `VS Code`, `Live Server`, `GitHub Pages`

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
다크 모드: 버튼 클릭 → state.theme 변경 → DOM attributes 및 localStorage 반영
GitHub API: Fetch 시작/성공/실패 → state.loading / error / repos 변경 → Projects UI 상태별 차등 렌더링
프로젝트 필터링: 언어 클릭 → state.filter 변경 → 배열 .filter() 후 카드 재렌더링
폼 유효성 검사: 제출 → state.formErrors 업데이트 → 에러 메시지 DOM 반영

2. 시맨틱 HTML & CSS 레이아웃
<header>, <nav>, <main>, <section>, <article>, <footer> 시맨틱 태그만을 사용하여 구조를 설계했습니다.

Flexbox & Grid 조합:
Navigation: Flexbox 적용 (로고 좌측, 메뉴 우측 배치)
Projects Section: CSS Grid (auto-fit, minmax) 기반의 반응형 카드 레이아웃
CSS Custom Properties (:root):
색상, 간격, 테마 변수를 정의하고 [data-theme="dark"] 속성을 통한 다크 모드 스위칭
모바일 퍼스트 반응형 디자인: 브레이크포인트(768px, 1024px) 설정 및 모바일 햄버거 메뉴 구현

3. GitHub REST API 연동 및 상태별 UI
async/await 및 fetch를 활용하여 [https://api.github.com/users/woochul0516/repos](https://api.github.com/users/woochul0516/repos) 데이터 수신
API 403 Rate Limit 예외 처리 및 try/catch 에러 핸들링

4가지 UI 상태 완벽 대응:
로딩 상태: 스피너 애니메이션 표시
성공 상태: Array.map 및 템플릿 리터럴을 활용한 동적 카드 렌더링
에러 상태: 에러 메시지 출력 및 [다시 시도] 버튼을 통한 재요청 기능
빈 데이터 상태: 조건 만족 프로젝트 부재 시 메시지 출력

4. Contact Form 유효성 검사 및 실제 메일 발송 (EmailJS 연동)
event.preventDefault()를 통한 기본 폼 제출 방지
이름/메시지 필수 입력값 검증 및 정규표현식을 활용한 이메일 포맷 유효성 검사
보너스 미션 달성 (EmailJS):
백엔드 서버 없이 브라우저 단에서 EmailJS SDK를 연동하여 입력된 문의 내용을 지정된 이메일함으로 실시간 전송
메일 전송 중 버튼 비활성화(disabled) 및 성공/실패 메시지 알림 UX 처리

5. UI 인터랙션 및 애니메이션
타이핑 효과 (보너스 미션): Hero 섹션에 자바스크립트 기반 타자기 효과 구현
프로젝트 카테고리 필터링 (보너스 미션): Array.prototype.filter 기반 기술 언어별 카드 스크리닝
Intersection Observer API: 스크롤 시 섹션별 fade-in 애니메이션 구현 (threshold: 0.2)
스크롤 UX:
스크롤 60px 이상 시 헤더 스타일 변경 (scrolled)
스크롤 300px 이상 시 상단 이동 버튼 노출 (scroll-top)


### 📁 프로젝트 구조 (Directory Structure)
├── index.html          # 시맨틱 구조 마크업 및 외부 스크립트(EmailJS) 연결
├── css/
│   └── style.css       # CSS 변수, 다크모드, Flex/Grid 및 반응형 스타일
└── js/
    └── main.js         # 상태 관리, DOM 이벤트, API 연동, EmailJS 핵심 로직


### 📸 프로젝트 실행 화면 (Screenshots)
(GitHub 저장소의 images/ 폴더에 스크린샷을 업로드하신 후 경로를 연결해주세요)
데스크톱 화면모바일 & 햄버거 메뉴다크 모드![Desktop](images/desktop.png)![Mobile](images/mobile.png)![DarkMode](images/darkmode.png)

### 학습 및 성찰 (Mission Takeaways)시맨틱 마크업의 이유:
검색엔진 최적화(SEO)와 가독성, 웹 접근성 향상을 위해 의미에 맞는 태그를 정립했습니다.
Flexbox vs Grid: 1차원 레이아웃(헤더, 버튼 모음)에는 Flexbox를, 2차원 반응형 카드 정렬에는 CSS Grid를 선택하여 효율을 극대화했습니다.
상태 관리의 체득: 사용자 이벤트 발생 시 DOM을 직접 난잡하게 변경하는 대신, 상태 객체(state)를 먼저 변경하고 이를 바탕으로 UI를 그려내는 React의 core 원리를 직접 체험했습니다.