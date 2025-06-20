import PyPDF2
import openai
import requests
import os
import json
import re
import csv
import time
import hashlib
from typing import Dict, List, Optional, Tuple, Set
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import tiktoken

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flashcard_generator.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class Flashcard:
    """플래시카드 데이터 클래스"""
    question: str
    answer: str
    tags: List[str] = None
    notes: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def to_anki_format(self) -> str:
        """Anki 임포트 형식으로 변환"""
        tags_str = ' '.join(self.tags) if self.tags else ''
        return f"{self.question}\t{self.answer}\t{tags_str}"
    
    def is_valid(self) -> bool:
        """플래시카드 유효성 검사"""
        return bool(self.question.strip() and self.answer.strip())
    
    def calculate_quality_score(self, llm_client=None) -> float:
        """LLM을 사용하여 카드 품질 점수 계산 (0-1)"""
        if not llm_client:
            return 0.5  # 기본 점수
            
        validation_prompt = f"""
다음 플래시카드의 품질을 0-10 점수로 평가해주세요.

질문: {self.question}
답변: {self.answer}

평가 기준:
- 질문이 명확하고 구체적인가?
- 답변이 질문에 정확히 대답하는가?
- 답변이 의미있고 학습에 도움이 되는가?
- 답변이 "모르겠다", "언급되지 않음" 같은 무의미한 내용인가?

점수만 숫자로 답변하세요 (예: 8).
"""
        
        try:
            messages = [
                {"role": "system", "content": "당신은 교육 콘텐츠 품질 평가 전문가입니다."},
                {"role": "user", "content": validation_prompt}
            ]
            
            response = llm_client.call_api_with_retry(messages)
            score = float(re.search(r'\d+', response).group()) / 10.0
            return min(max(score, 0.0), 1.0)  # 0-1 범위로 제한
        except:
            return 0.5  # 오류 시 중간 점수

class LLMConfig:
    def __init__(self):
        # 기본 설정
        self.provider = os.getenv('LLM_PROVIDER', 'ollama')
        
        # OpenAI 설정
        self.openai_api_key = os.getenv('OPENAI_API_KEY', 'YOUR-OPENAI-API-KEY')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        # Ollama 설정
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        
        # OpenRouter 설정
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY', 'YOUR-OPENROUTER-API-KEY')
        self.openrouter_model = os.getenv('OPENROUTER_MODEL', 'meta-llama/llama-3.2-3b-instruct:free')
        self.openrouter_base_url = 'https://openrouter.ai/api/v1'
        
        # 공통 설정
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.retry_delay = int(os.getenv('RETRY_DELAY', '2'))
        self.temperature = float(os.getenv('TEMPERATURE', '0.3'))
        self.max_tokens = int(os.getenv('MAX_TOKENS', '2048'))
        
        # 플래시카드 생성 설정
        self.cards_per_section = int(os.getenv('CARDS_PER_SECTION', '5'))
        self.min_card_quality = float(os.getenv('MIN_CARD_QUALITY', '0.7'))

class EnhancedPDFReader:
    """향상된 PDF 읽기 클래스"""
    
    @staticmethod
    def read_pdf(file_path: str) -> Tuple[str, Dict]:
        """PDF 파일을 읽고 메타데이터 추출"""
        metadata = {
            'title': '',
            'author': '',
            'pages': 0,
            'file_name': os.path.basename(file_path)
        }
        
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # 메타데이터 추출
                if reader.metadata:
                    metadata['title'] = reader.metadata.get('/Title', '')
                    metadata['author'] = reader.metadata.get('/Author', '')
                
                metadata['pages'] = len(reader.pages)
                
                # 텍스트 추출 with 에러 처리
                text_parts = []
                for i, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    except Exception as e:
                        logging.warning(f"페이지 {i+1} 읽기 실패: {e}")
                
                text = " ".join(text_parts)
                
                # 텍스트 정리
                text = re.sub(r'\s+', ' ', text)
                text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)  # 하이픈 제거
                
                return text, metadata
                
        except Exception as e:
            logging.error(f"PDF 읽기 오류: {e}")
            raise

class TextProcessor:
    """텍스트 처리 및 분할 클래스"""
    
    @staticmethod
    def estimate_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
        """텍스트의 토큰 수 추정"""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except:
            encoding = tiktoken.get_encoding("cl100k_base")
        
        return len(encoding.encode(text))
    
    @staticmethod
    def smart_divide_text(text: str, max_tokens: int = 1500) -> List[str]:
        """의미 있는 단위로 텍스트 분할"""
        # 문장 단위로 분할
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        sections = []
        current_section = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = TextProcessor.estimate_tokens(sentence)
            
            if current_tokens + sentence_tokens > max_tokens and current_section:
                sections.append(' '.join(current_section))
                current_section = [sentence]
                current_tokens = sentence_tokens
            else:
                current_section.append(sentence)
                current_tokens += sentence_tokens
        
        if current_section:
            sections.append(' '.join(current_section))
        
        return sections
    
    @staticmethod
    def extract_key_concepts(text: str) -> List[str]:
        """텍스트에서 핵심 개념 추출"""
        # 간단한 키워드 추출 (향후 NLP 라이브러리로 개선 가능)
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        concepts = list(set(words))[:10]  # 상위 10개 개념
        return concepts

class LLMClient:
    """통합 LLM 클라이언트"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        if config.provider == 'openai':
            openai.api_key = config.openai_api_key
    
    def call_api_with_retry(self, messages: List[Dict]) -> str:
        """재시도 로직이 포함된 API 호출"""
        for attempt in range(self.config.max_retries):
            try:
                if self.config.provider == 'openai':
                    return self._call_openai(messages)
                elif self.config.provider == 'ollama':
                    return self._call_ollama(messages)
                elif self.config.provider == 'openrouter':
                    return self._call_openrouter(messages)
                else:
                    raise ValueError(f"지원되지 않는 LLM 제공자: {self.config.provider}")
                    
            except Exception as e:
                logging.warning(f"API 호출 실패 (시도 {attempt+1}/{self.config.max_retries}): {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                else:
                    raise
    
    def _call_openai(self, messages: List[Dict]) -> str:
        """OpenAI API 호출"""
        response = openai.ChatCompletion.create(
            model=self.config.openai_model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        return response['choices'][0]['message']['content']
    
    def _call_ollama(self, messages: List[Dict]) -> str:
        """Ollama API 호출"""
        prompt = self._format_messages_to_prompt(messages)
        
        url = f"{self.config.ollama_base_url}/api/generate"
        payload = {
            "model": self.config.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }
        
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        return response.json().get('response', '')
    
    def _call_openrouter(self, messages: List[Dict]) -> str:
        """OpenRouter API 호출"""
        url = f"{self.config.openrouter_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.openrouter_model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        
        return response.json()['choices'][0]['message']['content']
    
    def _format_messages_to_prompt(self, messages: List[Dict]) -> str:
        """메시지를 프롬프트로 변환"""
        prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                prompt += f"System: {msg['content']}\n\n"
            elif msg["role"] == "user":
                prompt += f"User: {msg['content']}\n\n"
            elif msg["role"] == "assistant":
                prompt += f"Assistant: {msg['content']}\n\n"
        return prompt

class FlashcardGenerator:
    """플래시카드 생성 클래스"""
    
    def __init__(self, llm_client: LLMClient, config: LLMConfig):
        self.llm_client = llm_client
        self.config = config
        self.generated_cards: Set[str] = set()  # 중복 방지용
    
    def generate_cards_from_section(self, text: str, context: Dict) -> List[Flashcard]:
        """텍스트 섹션에서 플래시카드 생성"""
        prompt = self._create_generation_prompt(text, context)
        
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm_client.call_api_with_retry(messages)
        cards = self._parse_flashcards(response, context)
        
        # 품질 검증 및 중복 제거
        valid_cards = []
        for card in cards:
            if card.is_valid() and self._is_unique(card):
                # LLM 기반 품질 평가
                quality_score = card.calculate_quality_score(self.llm_client)
                if quality_score >= self.config.min_card_quality:
                    valid_cards.append(card)
                    self._add_to_generated(card)
                else:
                    logging.warning(f"낮은 품질로 카드 제외 (점수: {quality_score:.2f}): {card.question[:50]}...")
        
        return valid_cards
    
    def _get_system_prompt(self) -> str:
        """시스템 프롬프트 생성"""
        return """당신은 효과적인 학습을 위한 Anki 플래시카드 전문가입니다.
        
        고품질 플래시카드 생성 원칙:
        1. 하나의 개념에 하나의 카드 (최소 정보 원칙)
        2. 명확하고 구체적인 질문
        3. 간결하고 정확한 답변 - 반드시 텍스트에서 답을 찾을 수 있어야 함
        4. 문맥 독립적 (카드만 봐도 이해 가능)
        5. 능동적 회상을 유도하는 질문
        
        중요: 텍스트에서 명확한 답변을 찾을 수 없는 질문은 생성하지 마세요.
        "모르겠다", "언급되지 않음", "정의가 나와있지 않음" 같은 답변은 금지입니다.
        
        형식: 각 카드는 다음 형식으로 작성
        Q: [질문]
        A: [답변]
        Tags: [태그1, 태그2, ...]
        ---"""
    
    def _create_generation_prompt(self, text: str, context: Dict) -> str:
        """생성 프롬프트 작성"""
        key_concepts = TextProcessor.extract_key_concepts(text)
        
        prompt = f"""다음 텍스트에서 {self.config.cards_per_section}개의 Anki 플래시카드를 생성하세요.

주요 개념: {', '.join(key_concepts) if key_concepts else '자동 감지'}

텍스트:
{text}

중요한 지침:
1. 질문을 만들기 전에 텍스트에서 명확한 답변을 먼저 찾으세요
2. 답변이 텍스트에 명시되어 있지 않으면 해당 질문을 만들지 마세요
3. 모든 답변은 주어진 텍스트를 기반으로 해야 합니다
4. "모르겠다", "언급되지 않음" 같은 답변은 절대 사용하지 마세요

각 카드는 위에서 설명한 형식을 정확히 따라주세요."""
        
        return prompt
    
    def _parse_flashcards(self, response: str, context: Dict) -> List[Flashcard]:
        """응답에서 플래시카드 파싱"""
        cards = []
        
        # 카드 분리
        card_texts = re.split(r'---+', response)
        
        for card_text in card_texts:
            if not card_text.strip():
                continue
                
            # Q&A 추출
            q_match = re.search(r'Q:\s*(.+?)(?=A:|$)', card_text, re.DOTALL)
            a_match = re.search(r'A:\s*(.+?)(?=Tags:|$)', card_text, re.DOTALL)
            tags_match = re.search(r'Tags:\s*(.+?)$', card_text, re.DOTALL)
            
            if q_match and a_match:
                question = q_match.group(1).strip()
                answer = a_match.group(1).strip()
                
                tags = []
                if tags_match:
                    tags_text = tags_match.group(1).strip()
                    tags = [tag.strip() for tag in re.split(r'[,，]', tags_text)]
                
                # 컨텍스트 태그 추가
                if context.get('file_name'):
                    tags.append(f"source:{context['file_name']}")
                
                card = Flashcard(
                    question=question,
                    answer=answer,
                    tags=tags
                )
                cards.append(card)
        
        return cards
    
    def _is_unique(self, card: Flashcard) -> bool:
        """카드 중복 확인"""
        card_hash = hashlib.md5(f"{card.question}:{card.answer}".encode()).hexdigest()
        return card_hash not in self.generated_cards
    
    def _add_to_generated(self, card: Flashcard):
        """생성된 카드 기록"""
        card_hash = hashlib.md5(f"{card.question}:{card.answer}".encode()).hexdigest()
        self.generated_cards.add(card_hash)

class FlashcardExporter:
    """플래시카드 내보내기 클래스"""
    
    @staticmethod
    def export_to_anki_txt(cards: List[Flashcard], output_path: str):
        """Anki 텍스트 형식으로 내보내기"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for card in cards:
                f.write(card.to_anki_format() + '\n')
        logging.info(f"Anki 텍스트 파일 저장됨: {output_path}")
    
    @staticmethod
    def export_to_csv(cards: List[Flashcard], output_path: str):
        """CSV 형식으로 내보내기"""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Question', 'Answer', 'Tags'])
            
            for card in cards:
                tags_str = ' '.join(card.tags) if card.tags else ''
                writer.writerow([card.question, card.answer, tags_str])
        
        logging.info(f"CSV 파일 저장됨: {output_path}")
    
    @staticmethod
    def export_to_json(cards: List[Flashcard], output_path: str):
        """JSON 형식으로 내보내기"""
        cards_data = []
        for card in cards:
            cards_data.append({
                'question': card.question,
                'answer': card.answer,
                'tags': card.tags,
                'notes': card.notes
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cards_data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"JSON 파일 저장됨: {output_path}")

class AnkiFlashcardMaker:
    """메인 플래시카드 생성기 클래스"""
    
    def __init__(self):
        self.config = LLMConfig()
        self.llm_client = LLMClient(self.config)
        self.generator = FlashcardGenerator(self.llm_client, self.config)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def process_pdf(self, pdf_path: str, process_all: bool = False) -> List[Flashcard]:
        """PDF 파일 처리"""
        logging.info(f"PDF 처리 시작: {pdf_path}")
        
        # PDF 읽기
        text, metadata = EnhancedPDFReader.read_pdf(pdf_path)
        logging.info(f"PDF 메타데이터: {metadata}")
        
        # 텍스트 분할
        sections = TextProcessor.smart_divide_text(text)
        logging.info(f"총 {len(sections)}개 섹션으로 분할됨")
        
        # 처리할 섹션 결정
        if not process_all:
            sections = sections[:3]  # 처음 3개 섹션만
            logging.info("처음 3개 섹션만 처리합니다")
        
        # 병렬 처리로 플래시카드 생성
        all_cards = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_section = {
                executor.submit(
                    self.generator.generate_cards_from_section,
                    section,
                    metadata
                ): i
                for i, section in enumerate(sections)
            }
            
            for future in as_completed(future_to_section):
                section_idx = future_to_section[future]
                try:
                    cards = future.result()
                    all_cards.extend(cards)
                    logging.info(f"섹션 {section_idx + 1}: {len(cards)}개 카드 생성됨")
                except Exception as e:
                    logging.error(f"섹션 {section_idx + 1} 처리 오류: {e}")
        
        logging.info(f"총 {len(all_cards)}개 플래시카드 생성 완료")
        return all_cards
    
    def save_flashcards(self, cards: List[Flashcard], base_name: str):
        """플래시카드를 여러 형식으로 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Anki 텍스트 형식
        anki_path = self.output_dir / f"{base_name}_{timestamp}_anki.txt"
        FlashcardExporter.export_to_anki_txt(cards, str(anki_path))
        
        # CSV 형식
        csv_path = self.output_dir / f"{base_name}_{timestamp}.csv"
        FlashcardExporter.export_to_csv(cards, str(csv_path))
        
        # JSON 형식
        json_path = self.output_dir / f"{base_name}_{timestamp}.json"
        FlashcardExporter.export_to_json(cards, str(json_path))
        
        return anki_path, csv_path, json_path
    
    def generate_statistics(self, cards: List[Flashcard]) -> Dict:
        """생성된 카드 통계"""
        stats = {
            'total_cards': len(cards),
            'tags_distribution': {},
            'avg_question_length': 0,
            'avg_answer_length': 0
        }
        
        if cards:
            q_lengths = [len(card.question) for card in cards]
            a_lengths = [len(card.answer) for card in cards]
            
            stats['avg_question_length'] = sum(q_lengths) / len(q_lengths)
            stats['avg_answer_length'] = sum(a_lengths) / len(a_lengths)
            
            # 태그 분포
            for card in cards:
                for tag in card.tags:
                    stats['tags_distribution'][tag] = stats['tags_distribution'].get(tag, 0) + 1
        
        return stats

def main():
    """메인 실행 함수"""
    print("=== 향상된 Anki 플래시카드 생성기 ===")
    
    maker = AnkiFlashcardMaker()
    print(f"현재 LLM 제공자: {maker.config.provider}")
    
    # PDF 파일 선택
    source_dir = Path("SOURCE_DOCUMENTS")
    if not source_dir.exists():
        source_dir.mkdir()
        print(f"{source_dir} 폴더가 생성되었습니다. PDF 파일을 넣어주세요.")
        return
    
    pdf_files = list(source_dir.glob("*.pdf"))
    if not pdf_files:
        print("SOURCE_DOCUMENTS 폴더에 PDF 파일이 없습니다.")
        return
    
    # 파일 선택
    print("\n사용 가능한 PDF 파일:")
    for i, pdf_file in enumerate(pdf_files):
        print(f"{i+1}. {pdf_file.name}")
    
    try:
        choice = int(input("\n처리할 파일 번호를 선택하세요: ")) - 1
        if choice < 0 or choice >= len(pdf_files):
            raise ValueError
    except:
        print("잘못된 선택입니다.")
        return
    
    pdf_path = str(pdf_files[choice])
    
    # 처리 옵션
    process_all = input("모든 섹션을 처리하시겠습니까? (y/N): ").lower().startswith('y')
    
    try:
        # 플래시카드 생성
        cards = maker.process_pdf(pdf_path, process_all)
        
        if cards:
            # 파일 저장
            base_name = pdf_files[choice].stem
            anki_path, csv_path, json_path = maker.save_flashcards(cards, base_name)
            
            # 통계 출력
            stats = maker.generate_statistics(cards)
            print(f"\n=== 생성 통계 ===")
            print(f"총 카드 수: {stats['total_cards']}")
            print(f"평균 질문 길이: {stats['avg_question_length']:.1f}자")
            print(f"평균 답변 길이: {stats['avg_answer_length']:.1f}자")
            
            print(f"\n파일 저장 위치:")
            print(f"- Anki: {anki_path}")
            print(f"- CSV: {csv_path}")
            print(f"- JSON: {json_path}")
        else:
            print("플래시카드가 생성되지 않았습니다.")
            
    except Exception as e:
        logging.error(f"처리 중 오류 발생: {e}")
        print(f"오류가 발생했습니다. 로그를 확인하세요.")

if __name__ == "__main__":
    main()