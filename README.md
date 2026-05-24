# 공문서 제작 LLM (RAG 기반)

<img src="main.png">

## 프로젝트 개요
이 프로젝트는 공문서 작성 업무를 지원하기 위한 Streamlit 기반 LLM 애플리케이션입니다.

- 내부 가이드 문서(`guide.pdf`)를 기반으로 RAG 검색 후 답변 생성
- 사용자의 요청을 받아 기획문서, 보고서, 공고문 등 문서 초안 작성 지원
- 공문 형식 준수를 위한 프롬프트 템플릿 적용

## 현재 구현 범위

### 1. 문서 작성 보조
- 사용자 입력을 받아 LLM이 초안을 생성합니다.
- 시스템 프롬프트에서 공문서 작성 방향(1장 분량, 표 포함 가능)을 지정합니다.
- LangChain + FAISS 기반 검색 컨텍스트를 함께 사용합니다.

### 2. 참고 데이터 연동(실험 기능)
- `의료기관통합.csv`를 읽어 위치 기반 필터링 로직을 수행합니다.
- `streamlit_geolocation`으로 사용자 위치를 받아 주변 기관 데이터를 추릴 수 있습니다.
- 현재 지도 출력 함수(`create_doc`)는 비어 있어 후속 구현이 필요합니다.

## 기술 스택
- Python 3.11
- Streamlit
- LangChain (`langchain`, `langchain-openai`, `langchain-community`)
- FAISS (`faiss-cpu`)
- Pandas
- python-dotenv

## 실행 방법 (간단 버전)
1. 가상환경 생성
   ```bash
   python3 -m venv .venv
   ```
2. 가상환경 활성화
   ```bash
   source .venv/bin/activate
   ```
3. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```
4. API 키 설정
   ```env
   OPENAI_API_KEY=발급받은_키
   ```
5. 앱 실행
   ```bash
   streamlit run app.py
   ```

## 파일 구성
- `app.py`: Streamlit 앱 엔트리포인트
- `guide.pdf`: RAG 검색에 사용하는 참고 가이드
- `refer.txt`: 보조 참고 텍스트 파일
- `의료기관통합.csv`: 위치 기반 필터링용 데이터
- `requirements.txt`: pip 의존성 목록

## 참고
- 첫 실행 시 문서 임베딩 및 벡터스토어 생성으로 시간이 소요될 수 있습니다.
- 위치 기반 기능을 사용하려면 브라우저 위치 권한 허용이 필요합니다.
