"""
플래시카드 생성 서비스 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Dict
from src.Entity.flashcard import Flashcard


class IFlashcardGeneratorService(ABC):
    """플래시카드 생성 서비스 인터페이스"""
    
    @abstractmethod
    def generate_cards_from_section(self, text: str, context: Dict) -> List[Flashcard]:
        """텍스트 섹션에서 플래시카드 생성"""
        pass
    
    @abstractmethod
    def generate_cards_from_pdf(self, pdf_path: str, process_all: bool = False) -> List[Flashcard]:
        """PDF 파일에서 플래시카드 생성"""
        pass 