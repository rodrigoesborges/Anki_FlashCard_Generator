"""
메인 애플리케이션
"""
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from src.Config.llm_config import LLMConfig
from src.Entity.flashcard import Flashcard
from src.Service.llm_service import LLMService
from src.Service.pdf_reader_service import PDFReaderService
from src.Service.flashcard_generator_service import FlashcardGeneratorService
from src.Service.export_service import ExportService


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/flashcard_generator.log'),
        logging.StreamHandler()
    ]
)


class AnkiFlashcardMaker:
    """메인 플래시카드 생성기 클래스"""
    
    def __init__(self):
        self.config = LLMConfig()
        self.llm_service = LLMService(self.config)
        self.pdf_service = PDFReaderService()
        self.generator_service = FlashcardGeneratorService(
            self.llm_service, 
            self.pdf_service, 
            self.config
        )
        self.export_service = ExportService()
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def process_pdf(self, pdf_path: str, process_all: bool = False) -> List[Flashcard]:
        """PDF 파일 처리"""
        return self.generator_service.generate_cards_from_pdf(pdf_path, process_all)
    
    def save_flashcards(self, cards: List[Flashcard], base_name: str):
        """플래시카드를 여러 형식으로 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Anki 텍스트 형식
        anki_path = self.output_dir / f"{base_name}_{timestamp}_anki.txt"
        self.export_service.export_to_anki_txt(cards, str(anki_path))
        
        # CSV 형식
        csv_path = self.output_dir / f"{base_name}_{timestamp}.csv"
        self.export_service.export_to_csv(cards, str(csv_path))
        
        # JSON 형식
        json_path = self.output_dir / f"{base_name}_{timestamp}.json"
        self.export_service.export_to_json(cards, str(json_path))
        
        return anki_path, csv_path, json_path
    
    def generate_statistics(self, cards: List[Flashcard]) -> Dict[str, Any]:
        """생성된 카드 통계"""
        stats: Dict[str, Any] = {
            'total_cards': len(cards),
            'tags_distribution': {},
            'avg_question_length': 0.0,
            'avg_answer_length': 0.0
        }
        
        if cards:
            q_lengths = [len(card.question) for card in cards]
            a_lengths = [len(card.answer) for card in cards]
            
            stats['avg_question_length'] = sum(q_lengths) / len(q_lengths)
            stats['avg_answer_length'] = sum(a_lengths) / len(a_lengths)
            
            # 태그 분포
            for card in cards:
                for tag in card.tags:
                    if tag not in stats['tags_distribution']:
                        stats['tags_distribution'][tag] = 0
                    stats['tags_distribution'][tag] += 1
        
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