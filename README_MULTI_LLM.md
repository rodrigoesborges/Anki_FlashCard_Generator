# 다중 LLM 모델 지원 Anki 플래시카드 생성기

이 도구는 OpenAI, Ollama, OpenRouter를 통해 다양한 LLM 모델을 사용하여 PDF에서 Anki 플래시카드를 생성합니다.

## 지원되는 LLM 제공자

### 1. Ollama (로컬)
- **장점**: 완전 무료, 프라이버시 보호, 오프라인 사용 가능
- **설치**: [Ollama 공식 사이트](https://ollama.ai)에서 설치
- **모델 다운로드**: `ollama pull llama3.2` (또는 원하는 모델)

### 2. OpenAI
- **장점**: 높은 품질, 안정적인 성능
- **비용**: API 사용량에 따른 과금
- **API 키**: [OpenAI 플랫폼](https://platform.openai.com)에서 발급

### 3. OpenRouter
- **장점**: 다양한 모델 선택, 경쟁력 있는 가격
- **비용**: 모델별 차등 과금
- **API 키**: [OpenRouter](https://openrouter.ai)에서 발급

## 설정 방법

### 환경 변수 설정
`.env.example` 파일을 `.env`로 복사하고 필요한 값들을 설정하세요:

```bash
cp .env.example .env
```

### 각 제공자별 설정

#### Ollama 사용
```bash
# Ollama 설치 및 모델 다운로드
ollama pull llama3.2

# 환경 변수 설정
export LLM_PROVIDER=ollama
export OLLAMA_MODEL=llama3.2
```

#### OpenAI 사용
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your-api-key
export OPENAI_MODEL=gpt-3.5-turbo
```

#### OpenRouter 사용
```bash
export LLM_PROVIDER=openrouter
export OPENROUTER_API_KEY=your-api-key
export OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
```

## 사용법

```bash
# 의존성 설치
pip install -r requirements.txt

# PDF 파일을 SOURCE_DOCUMENTS/ 폴더에 넣기
# 실행
python Anki_flashcards_creator.py
```

## 추천 모델

### Ollama (무료)
- `llama3.2`: 일반적인 용도, 빠른 속도
- `llama3.1:8b`: 더 나은 품질
- `mistral`: 효율적인 성능

### OpenRouter (유료)
- `meta-llama/llama-3.2-3b-instruct:free`: 무료 옵션
- `anthropic/claude-3-haiku`: 빠르고 저렴
- `openai/gpt-3.5-turbo`: 안정적인 성능

## 문제 해결

### Ollama 연결 오류
```bash
# Ollama 서비스 실행 확인
ollama serve

# 모델 목록 확인
ollama list
```

### API 키 오류
- `.env` 파일의 API 키가 올바른지 확인
- API 키에 충분한 크레딧이 있는지 확인

### 메모리 부족 (Ollama)
더 작은 모델 사용:
```bash
export OLLAMA_MODEL=llama3.2:1b
```