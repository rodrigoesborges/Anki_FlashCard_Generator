# Anki Flash Card Generator

PDF 문서에서 자동으로 Anki 플래시카드를 생성하는 도구입니다. OpenAI, Ollama, OpenRouter 등 다양한 LLM 제공자를 지원합니다.

## 🚀 빠른 시작

### 1. 설치 및 실행

**Windows:**
```bash
run.bat
```

**Mac/Linux:**
```bash
./run.sh
```

### 2. PDF 파일 추가
`SOURCE_DOCUMENTS` 폴더에 PDF 파일을 넣어주세요.

### 3. LLM 설정
`.env` 파일에서 사용하고자 하는 LLM 제공자를 설정하세요.

## 📁 프로젝트 구조

```
Anki_FlashCard_Generator/
├── src/
│   ├── Config/         # 설정 파일
│   ├── Entity/         # 데이터 모델
│   ├── IService/       # 서비스 인터페이스
│   ├── Service/        # 서비스 구현
│   ├── Utils/          # 유틸리티 함수
│   └── main.py         # 메인 애플리케이션
├── SOURCE_DOCUMENTS/   # PDF 입력 폴더
├── output/            # 생성된 플래시카드 출력
├── logs/              # 로그 파일
├── backup/            # 백업 파일
├── .env.example       # 환경 변수 템플릿
├── run.sh             # Unix 실행 스크립트
└── run.bat            # Windows 실행 스크립트
```

## ⚙️ 설정

`.env` 파일에서 다음 항목들을 설정할 수 있습니다:

- `LLM_PROVIDER`: 사용할 LLM 제공자 (openai, ollama, openrouter)
- `CARDS_PER_SECTION`: 섹션당 생성할 카드 수
- `MIN_CARD_QUALITY`: 최소 카드 품질 점수 (0.0 ~ 1.0)

각 제공자별 설정은 `.env.example` 파일을 참조하세요.

## 📊 출력 형식

생성된 플래시카드는 다음 형식으로 저장됩니다:
- **Anki TSV**: Anki에 직접 임포트 가능
- **CSV**: 스프레드시트에서 편집 가능
- **JSON**: 프로그래밍 방식으로 처리 가능

## 🧪 테스트

LLM 연결 테스트:
```bash
python test_llm_providers.py
```

여러 제공자 데모:
```bash
python demo_multi_provider.py
```

## �� 라이선스

MIT License