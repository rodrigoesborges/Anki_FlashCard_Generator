"""
플래시카드 내보내기 서비스 구현
"""
import csv
import json
import logging
from typing import List

from src.Entity.flashcard import Flashcard
from src.IService.export_service_interface import IExportService


class ExportService(IExportService):
    """플래시카드 내보내기 서비스"""
    
    def export_to_anki_txt(self, cards: List[Flashcard], output_path: str) -> None:
        """Anki 텍스트 형식으로 내보내기"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for card in cards:
                f.write(card.to_anki_format() + '\n')
        logging.info(f"Anki 텍스트 파일 저장됨: {output_path}")
    
    def export_to_csv(self, cards: List[Flashcard], output_path: str) -> None:
        """CSV 형식으로 내보내기"""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Question', 'Answer', 'Tags'])
            
            for card in cards:
                tags_str = ' '.join(card.tags) if card.tags else ''
                writer.writerow([card.question, card.answer, tags_str])
        
        logging.info(f"CSV 파일 저장됨: {output_path}")
    
    def export_to_json(self, cards: List[Flashcard], output_path: str) -> None:
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