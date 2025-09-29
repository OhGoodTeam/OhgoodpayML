---
title: OHGOODPAY
layout: home ## 이건 기본 레이아웃이라 변경하면 안된다.
nav_order: 1
---

# 🥖 **OhGoodPay - 지금 사고 돈은 나중에~!**
<br>
<a href="https://ohgoodpay.com">
    <img src="assets/images/썸네일.png" style="display: block; margin: 0 auto;" />
</a>

<p style="text-align: center;">이미지를 클릭하면 ohgoodpay로 이동합니다.</p>

## 🔗 목차

1. [프로젝트 소개](#프로젝트-소개)
2. [주요 기능](#주요-기능)
3. [팀 소개](#팀-소개)
4. [기술 스택](#기술-스택)
5. [파일 구조](#파일-구조)
6. [시스템 구조](#시스템-구조)
7. [보안](#보안)
8. [빌드 방법](#빌드-방법)
9. [협업 규칙](#협업-규칙)

----------------------------

<h2 id="프로젝트-소개">🖐🏻 프로젝트 소개</h2>
### OhgoodPay는 BNPL을 지원하는 페이 서비스 입니다.   
<br>
<img src="assets/images/프로젝트 소개.png" style="display: block; margin: 0 auto;" />
<br>  

### BNPL이란?  
**Buy Now, Pay Later**의 약자로 상품을 구매한 뒤, 일정 기간 후에 결제 대금을 지불하는 후불결제  
  
오굿페이의 BNPL 서비스는 카드 없이도 간편하게 사용할 수 있는 후불결제 솔루션입니다.  
신용카드 발급이 어려운 사용자, 당장 현금이 부족한 사용자도 **합리적인 소비**를 할 수 있도록 지원합니다.  
안전하고, **이자 없는** 단기간 후불 결제를 원하는 **누구나 사용 가능**합니다.  

 **“지금 사고, 나중에 갚는”** BNPL 서비스를 오굿페이에서 만나보세요.   

----------------------------

<h2 id="주요-기능">🎯 주요 기능</h2>

### 👤 사용자
- 카드 없이 간편하게 "지금 구매, 나중에 납부" 가능  
- 연체 없이 납부 및 결제, 숏폼 등을 통한 포인트 리워드 제공  
- 사용자 맞춤형 소비 리포트 제공으로 소비 습관 확인 가능  
- AI를 활용한 챗봇 서비스로 개인화된 상품 추천 가능  
- OhgoodScore를 통한 신용도 확인 가능  
- 한도 선정 이유 공개 및 등급 제도 확인 가능  

### 🧑‍🍳 가맹점  
- 오굿페이 BNPL 위젯 제공  
- API 연동으로 자체 서비스에 연동 가능  

### 👀 운영자  
- 사용자의 연체율, 이용 패턴 등을 분석해 OhgoodScore 산정  
- 결제 흐름, 연체 현황, API 호출 이력 등 모니터링 가능  
- 추천 시스템 및 PG창 연동으로 광고 효과 및 가맹점 관리 가능  

----------------------------

<h2 id="팀-소개">👥 팀 소개</h2>

<img src="assets/images/ohgoodteam.jpg" style="display: block; margin: 0 auto;" />

----------------------------

<h2 id="기술-스택">🔧 기술 스택</h2>

| 구분             | 기술 스택                                                                                                                                                                                                                                                                                                                                              |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Frontend         | ![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black&style=flat-square) ![Zustand](https://img.shields.io/badge/Zustand-000000?logo=react&logoColor=white&style=flat-square) ![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white&style=flat-square) |
| Backend          | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white&style=flat-square) ![Spring Boot](https://img.shields.io/badge/Spring%20Boot-6DB33F?logo=springboot&logoColor=white&style=flat-square) ![JPA](https://img.shields.io/badge/JPA-007396?logo=hibernate&logoColor=white&style=flat-square) ![QueryDSL](https://img.shields.io/badge/QueryDSL-00599C?logo=gradle&logoColor=white&style=flat-square) ![Spring Security](https://img.shields.io/badge/Security-6DB33F?logo=springsecurity&logoColor=white&style=flat-square) 
| Database         | ![MariaDB](https://img.shields.io/badge/MariaDB-003545?logo=mariadb&logoColor=white&style=flat-square) ![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white&style=flat-square)                                                                                                                                                 |
| Infra & Cloud    | ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white&style=flat-square) ![AWS EC2](https://img.shields.io/badge/AWS%20EC2-FF9900?logo=amazonaws&logoColor=white&style=flat-square) ![AWS S3](https://img.shields.io/badge/AWS%20S3-FF9900?logo=amazonaws&logoColor=white&style=flat-square)                            |
| 외부 API         | ![OpenAI](https://img.shields.io/badge/OpenAI-412991?logo=openai&logoColor=white&style=flat-square) ![Naver Shopping](https://img.shields.io/badge/Naver%20Shopping-03C75A?logo=naver&logoColor=white&style=flat-square)                                                                                                                                  |


----------------------------

<h2 id="파일-구조">📂 파일 구조</h2>  

### BE - Spring Boot
[Spring Boot Repo 바로가기](https://github.com/OhGoodTeam/OhgoodpayBE.git)  

```markdown
ohgoodpay/
├── OhgoodpayApplication.java        // Spring Boot 메인 실행 파일
├── common/                          // 공통 도메인(회원가입, 마이페이지 등) 서비스
├── pay/                             // 결제 및 포인트(BNPL 핵심) 서비스
├── recommend/                       // 대시보드 및 AI 추천 서비스
├── shorts/                          // 숏폼 커뮤니티(구독/댓글 등) 서비스
├── security/                        // JWT 및 사용자 인증 보안
│   ├── config/                      // Spring Security 설정
│   ├── filter/                      // 로그인/토큰 필터
│   ├── service/, util/              // 인증 서비스, JWT 유틸
│
├── config/                          // 글로벌 설정 파일들, CORS, Redis 등
├── scheduled/                       // 정기 작업 (스케줄링 서비스)
├── exception/                       // 커스텀 예외 및 전역 에러 핸들링
└── resources/                       // 공통 환경 설정 및 Redis, FastAPI 등 설정 파일

```  

### BE - FastAPI  
[FastAPI Repo 바로가기](https://github.com/OhGoodTeam/OhgoodpayML.git)  
```markdown  
OhGoodPayML/ 
├── main.py                          # FastAPI 진입점 (서버 실행 파일)
├── config/                          # OpenAI, Naver API 키 등 환경 설정
│   └── openai_config.py, naver_config.py
│
├── domain/                          # 챗봇 흐름 처리, Ohgood Score 계산 로직, 카테고리 분류  
├── routers/                         # FastAPI 라우터 (엔드포인트 정의)
├── schemas/                         # Pydantic 기반 요청/응답 DTO
├── services/                        # 서비스 계층 (FastAPI 내부 로직)
│   ├── spring_client.py             # Spring ↔ FastAPI 간 연동용 클라이언트
│   └── narratives/                  # Dash용 AI 응답 흐름 처리 (prompt)
|
├── requirements.txt                 # Python 패키지 목록
├── .venv/                           # 가상환경 디렉터리 (로컬용)

```

### FE - React
[React Repo 바로가기](https://github.com/OhGoodTeam/OhgoodpayFE.git)    
```markdown
src/
├── App.jsx, App.css, index.jsx, index.css   # 앱 진입점 및 글로벌 스타일
│
├── features/                                # 도메인별 기능 모듈화
│   ├── auth/                                # 로그인/회원가입 관련
│   ├── common/                              # 마이페이지, 회원정보 관리
│   ├── home/                                # 홈 화면 (BNPL, 체크인, 퀵액세스 등)
│   ├── pay/                                 # 결제 위젯, 포인트, 납부 내역
│   ├── planet/                              # 확장 예정 기능
│   ├── qrpin/                               # QR/핀 기반 결제
│   ├── recommend/                           # 대시보드 + AI 추천
│   └── shorts/                              # 숏폼(피드, 프로필, 검색, 업로드)
│
├── pages/                                   # 페이지 단위 컴포넌트 (라우팅 대상)
│   ├── auth/                                # 로그인, 회원가입
│   ├── common/                              # 마이페이지 화면
│   ├── home/                                # 홈 화면
│   ├── pay/                                 # 결제/포인트 조회 페이지
│   ├── planet/                              # (추가 예정)
│   ├── qrpin/                               # QR/핀 결제 페이지
│   ├── recommend/                           # 대시보드 & 챗봇 페이지
│   └── shorts/                              # 숏폼 관련 (피드, 프로필, 업로드 등)
│
└── shared/                                  # 공용 리소스 & 유틸
    ├── api/                                 # Axios 클라이언트 & API 모듈
    ├── assets/                              # 공용 CSS, 폰트, 이미지
    ├── components/                          # 공용 UI 컴포넌트 (버튼, 모달 등)
    ├── hook/                                # 커스텀 훅
    ├── layout/                              # 화면 레이아웃 (Main, Chat, Dash 등)
    ├── router/                              # React Router 설정
    ├── store/

```

----------------------------

<h2 id="시스템-구조">🧱 서비스 구조</h2>

<img src="assets/images/구조도.jpg" style="display: block; margin: 0 auto;" />  

1. 프론트엔드 (React + Vite)
- 사용자(웹/모바일)가 보는 화면.  
- 로그인/회원가입, 결제 위젯, 마이페이지, 숏폼(Shorts), 대시보드, AI 추천 등을 제공.
- Zustand를 이용한 상태관리, 백엔드 서버와 API 통신.

2. 메인 서버 (Spring Boot 기반)
- 서비스의 핵심 비즈니스 로직 담당.  
- 주요 도메인 모듈:Common, Shorts, Recodash, Pay  
- DB와 연결되어 트랜잭션 관리 + Redis 캐시 활용.  

3. 데이터 서버 (FastAPI + LLM 연동)  
- AI/추천/분석 기능을 맡는 서브 서버.  
- 주요 역할: 챗봇 응답 (LLM), 대시보드 오굿스코어 계산, 소비 카테고리 분류 및 분석
- OpenAI를 통한 AI 조언 생성, 네이버 쇼핑 API를 이용한 RAG 구현  

4. 스토리지 & 외부 연동
- MariaDB: 메인 데이터 저장 (사용자, 결제, 숏폼, 포인트 등)  
- Redis: 챗봇 캐시 DB (빠른 대화 응답 처리)  
- AWS S3: 숏폼 영상 저장소 (업로드/조회)  
- 네이버 쇼핑 API: 외부 쇼핑 데이터 연동  
- OpenAI API: AI 챗봇, 추천, 조언 생성에 활용  

----------------------------

<h2 id="보안">🕶️ 보안</h2>

> 사장님과 일반 사용자가 함께 이용하는 애플리케이션인 만큼, 보안 취약점에 대한 철저한 대비가 필요했습니다.
> 최근 잇따른 보안 사고를 고려하여, 자주 발생할 수 있는 주요 보안 이슈들에 대한 대책을 수립하고 모두 적용하였습니다.

### 1️⃣ SQL Injection

**개념**

- **SQL Injection** 은 공격자가 입력값에 악의적인 SQL 코드를 삽입해 데이터베이스를 조작하는 기법입니다.
- 예를 들어, 로그인 폼에 `’ OR ’1’=’1` 과 같은 문자열을 넣으면 비밀번호 검사 로직을 우회하여 사이트에 접속이 가능합니다.

**대응 방법: MyBatis `#{}` 바인딩**

- `#{}` 로 전달된 값은 **JDBC `PreparedStatement`** 의 파라미터로 처리됩니다.
- 모든 mapper에 `#{}` 바인딩을 적용하여  SQL Injection을 방지하였습니다.
- SQL 문과 데이터가 분리되므로, 입력값은 자동으로 이스케이프되어 쿼리 구조 변경이 불가능합니다.

### 2️⃣ XSS 방지

**개념**

- XSS는 `<script>` 삽입을 통해 악성 스크립트를 실행해 정보를 탈취하거나 조작하는 공격입니다.

**대응 방법 : 요청 파라미터를 HTML 이스케이프 처리**

- `XSSFilter` + `XSSRequestWrapper` 로 모든 요청 파라미터를 HTML 이스케이프 처리하고, Spring 전역 `StringEscapeEditor` 를 통해 `@RequestParam`/`@ModelAttribute` 로 바인딩되는 문자열까지 필터링해 방어합니다.
- [관련 깃 이슈](https://github.com/OhGoodTeam/OhGoodFood/issues/139)

### 3️⃣ 파일 업로드 검증 (비인가 파일 업로드 차단)

**개념**

- CSRF는 사용자의 인증된 세션을 악용해 원치 않는 요청을 실행하는 공격입니다.

**대응 방법 : 이미지 확장자에 해당하는 파일들만 허용**

- S3 업로드 시 **.jpg, .jpeg, .png** 확장자만 허용하도록 필터링해 비인가 파일 삽입을 차단합니다.

----------------------------

<h2 id="빌드-방법">🚀 빌드 방법</h2>

### OhgoodpayML
Ohgoodpay Reco&amp;Analytics

### 개발 환경(venv) 빠른 시작

### 1) Python 버전 확인
```bash
python --version
```  
  
### 2) 가상환경 설정  
- 가상환경 이름은 꼭 .venv가 아니어도 됨   

```
python -m venv .venv 
.\.venv\Scripts\Activate

python -m venv .venv # windows / git bash
source .venv/Scripts/activate

python -m venv .venv # macOS / Linux / WSL
source .venv/bin/activate
```    

### 3) 패키지 설치  
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4) 서버 실행  
```
uvicorn app.main:app --reload --port 8000
deactivate   ## 비활성화  

```  
- Swagger: http://localhost:8000/docs

----------------------------

<h2 id="협업-규칙">🤝 협업 규칙</h2>

### 🥖 Branch 규칙
- 메인 브랜치와 개인 이름별 브랜치를 구분하여 사용한다.
  - main : 배포 가능한 상태의 코드만을 관리하는 브랜치
  - dev  : main 배포 전 전체 기능 통합 test 브랜치

### 🥖 Commit 규칙
- 커밋 메세지는 다음과 같은 형식으로 작성한다.

```java
[이름] 명령:구현설명 ex) [gildong] feat:로그인서비스구현
```

- **깃 컨벤션**
    - feat : 로직 구현
    - docs : 정적 파일 추가
    - fix : 버그 수정

### 🥖 PR 규칙
- 공용 템플릿을 사용하여 PR을 작성 : [PR 템플릿 바로가기](https://github.com/OhGoodTeam/OhGoodFood/blob/main/.github/PULL_REQUEST_TEMPLATE.md)

### 🥖 Issue 규칙
- 공용 템플릿을 사용하여 issue 작성 : [issue 템플릿 바로가기](https://github.com/OhGoodTeam/OhGoodFood/tree/main/.github/ISSUE_TEMPLATE)


