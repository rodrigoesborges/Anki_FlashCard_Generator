"""
플래시카드 생성 서비스 구현
"""
import re
import hashlib
import logging
from typing import List, Dict, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.Entity.flashcard import Flashcard
from src.IService.flashcard_generator_interface import IFlashcardGeneratorService
from src.IService.llm_service_interface import ILLMService
from src.IService.pdf_reader_interface import IPDFReaderService
from src.Config.llm_config import LLMConfig
from src.Utils.text_processor import TextProcessor


class FlashcardGeneratorService(IFlashcardGeneratorService):
    """플래시카드 생성 서비스"""
    
    def __init__(self, llm_service: ILLMService, pdf_service: IPDFReaderService, config: LLMConfig):
        self.llm_service = llm_service
        self.pdf_service = pdf_service
        self.config = config
        self.generated_cards: Set[str] = set()  # 중복 방지용
    
    def generate_cards_from_section(self, text: str, context: Dict) -> List[Flashcard]:
        """텍스트 섹션에서 플래시카드 생성"""
        prompt = self._create_generation_prompt(text, context)
        
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm_service.call_api_with_retry(messages)
        cards = self._parse_flashcards(response, context)
        
        # 품질 검증 및 중복 제거
        valid_cards = []
        for card in cards:
            if card.is_valid() and self._is_unique(card):
                # LLM 기반 품질 평가
                quality_score = card.calculate_quality_score(self.llm_service)
                if quality_score >= self.config.min_card_quality:
                    valid_cards.append(card)
                    self._add_to_generated(card)
                else:
                    logging.warning(f"낮은 품질로 카드 제외 (점수: {quality_score:.2f}): {card.question[:50]}...")
        
        return valid_cards
    
    def generate_cards_from_pdf(self, pdf_path: str, process_all: bool = False) -> List[Flashcard]:
        """PDF 파일에서 플래시카드 생성"""
        logging.info(f"PDF 처리 시작: {pdf_path}")
        
        # PDF 읽기
        text, metadata = self.pdf_service.read_pdf(pdf_path)
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
                    self.generate_cards_from_section,
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