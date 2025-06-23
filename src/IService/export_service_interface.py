"""
플래시카드 내보내기 서비스 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List
from src.Entity.flashcard import Flashcard


class IExportService(ABC):
    """플래시카드 내보내기 서비스 인터페이스"""
    
    @abstractmethod
    def export_to_anki_txt(self, cards: List[Flashcard], output_path: str) -> None:
        """Anki 텍스트 형식으로 내보내기"""
        pass
    
    @abstractmethod
    def export_to_csv(self, cards: List[Flashcard], output_path: str) -> None:
        """CSV 형식으로 내보내기"""
        pass
    
    @abstractmethod
    def export_to_json(self, cards: List[Flashcard], output_path: str) -> None:
        """JSON 형식으로 내보내기"""
        pass 