# Anki 플래시카드 생성기 문서

## 아키텍처 개요

이 프로젝트는 클린 아키텍처 원칙을 따르며, 다음과 같은 계층으로 구성됩니다:

### 1. Entity 계층
- `Flashcard`: 플래시카드 데이터 모델

### 2. Service 계층
- `LLMService`: LLM API 통합 서비스
- `PDFReaderService`: PDF 파일 읽기 서비스
- `FlashcardGeneratorService`: 플래시카드 생성 로직
- `ExportService`: 다양한 형식으로 내보내기

### 3. Interface 계층
- 각 서비스에 대한 인터페이스 정의
- 의존성 역전 원칙(DIP) 적용

## 주요 기능

### PDF 텍스트 추출
- PyPDF2를 사용한 텍스트 추출
- 메타데이터 수집 (제목, 저자, 페이지 수)
- 오류 처리 및 복구

### 텍스트 처리
- 토큰 기반 텍스트 분할
- 의미 단위 보존
- 핵심 개념 추출

### 플래시카드 생성
- LLM을 활용한 질문-답변 쌍 생성
- 품질 점수 기반 필터링
- 중복 제거

### 다중 LLM 지원
- OpenAI GPT 모델
- Ollama 로컬 모델
- OpenRouter 통합 API

## 확장 가능성

### 새로운 LLM 제공자 추가
1. `ILLMService` 인터페이스 구현
2. 설정 클래스에 제공자 추가
3. `LLMService`에 분기 로직 추가

### 새로운 문서 형식 지원
1. `IPDFReaderService` 인터페이스 구현
2. 해당 형식의 리더 서비스 생성

### 새로운 내보내기 형식
1. `IExportService`에 메서드 추가
2. `ExportService`에 구현 추가 