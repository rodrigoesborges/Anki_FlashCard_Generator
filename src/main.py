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
from src.Service.pdf_reader_service import FileReaderService
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
    
    # 지원하는 파일 확장자들
    SUPPORTED_EXTENSIONS = ['.pdf', '.md', '.markdown', '.txt', '.text']
    
    def __init__(self):
        self.config = LLMConfig()
        self.llm_service = LLMService(self.config)
        self.file_service = FileReaderService()  # 이름 변경
        self.generator_service = FlashcardGeneratorService(
            self.llm_service, 
            self.file_service,  # 이름 변경
            self.config
        )
        self.export_service = ExportService()
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def process_file(self, file_path: str, process_all: bool = False) -> List[Flashcard]:
        """파일 처리 (PDF, Markdown, Text 지원)"""
        return self.generator_service.generate_cards_from_pdf(file_path, process_all)
    
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
    
    def get_supported_files(self, source_dir: Path) -> List[Path]:
        """지원하는 형식의 파일들을 찾아서 반환"""
        files: List[Path] = []
        for ext in self.SUPPORTED_EXTENSIONS:
            files.extend(source_dir.glob(f"*{ext}"))
        return sorted(files)  # 파일명 순으로 정렬
    
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
    
    # 소스 디렉토리 확인
    source_dir = Path("SOURCE_DOCUMENTS")
    if not source_dir.exists():
        source_dir.mkdir()
        print(f"{source_dir} 폴더가 생성되었습니다.")
        print("지원 파일 형식: PDF, Markdown (.md), Text (.txt) 파일을 넣어주세요.")
        return
    
    # 지원하는 파일들 찾기
    supported_files = maker.get_supported_files(source_dir)
    if not supported_files:
        print("SOURCE_DOCUMENTS 폴더에 지원하는 파일이 없습니다.")
        print("지원 파일 형식: PDF, Markdown (.md), Text (.txt)")
        return
    
    # 파일 선택 메뉴
    print(f"\n사용 가능한 파일 ({len(supported_files)}개):")
    for i, file_path in enumerate(supported_files):
        file_size = file_path.stat().st_size
        size_str = f"{file_size/1024:.1f}KB" if file_size < 1024*1024 else f"{file_size/(1024*1024):.1f}MB"
        print(f"{i+1}. {file_path.name} ({file_path.suffix}) - {size_str}")
    
    # 모든 파일 처리 옵션 추가
    print(f"{len(supported_files)+1}. 모든 파일 처리")
    
    try:
        choice = int(input("\n처리할 파일 번호를 선택하세요: ")) - 1
        if choice < 0 or choice > len(supported_files):
            raise ValueError
    except:
        print("잘못된 선택입니다.")
        return
    
    # 처리 옵션
    process_all = input("모든 섹션을 처리하시겠습니까? (y/N): ").lower().startswith('y')
    
    try:
        if choice == len(supported_files):
            # 모든 파일 처리
            print(f"\n모든 파일 ({len(supported_files)}개)을 처리하고 있습니다...")
            all_cards = []
            processed_files = []
            
            for file_path in supported_files:
                try:
                    print(f"처리 중: {file_path.name}...")
                    cards = maker.process_file(str(file_path), process_all)
                    if cards:
                        all_cards.extend(cards)
                        processed_files.append(file_path.name)
                        print(f"✓ {file_path.name}: {len(cards)}개 카드 생성")
                    else:
                        print(f"⚠ {file_path.name}: 카드 생성 실패")
                except Exception as e:
                    print(f"✗ {file_path.name}: 처리 중 오류 - {e}")
                    continue
            
            if all_cards:
                # 통합 파일로 저장
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = f"ALL_FILES_{timestamp}"
                anki_path, csv_path, json_path = maker.save_flashcards(all_cards, base_name)
                
                # 통계 출력
                stats = maker.generate_statistics(all_cards)
                print(f"\n=== 전체 처리 통계 ===")
                print(f"처리된 파일 수: {len(processed_files)}")
                print(f"총 카드 수: {stats['total_cards']}")
                print(f"평균 질문 길이: {stats['avg_question_length']:.1f}자")
                print(f"평균 답변 길이: {stats['avg_answer_length']:.1f}자")
                
                if stats['tags_distribution']:
                    print(f"태그 분포: {dict(list(stats['tags_distribution'].items())[:5])}")
                
                print(f"\n처리된 파일들: {', '.join(processed_files)}")
                print(f"\n통합 파일 저장 위치:")
                print(f"- Anki: {anki_path}")
                print(f"- CSV: {csv_path}")
                print(f"- JSON: {json_path}")
            else:
                print("어떤 파일에서도 플래시카드가 생성되지 않았습니다.")
        else:
            # 개별 파일 처리 (기존 로직)
            selected_file = supported_files[choice]
            print(f"\n{selected_file.name} 파일을 처리하고 있습니다...")
            cards = maker.process_file(str(selected_file), process_all)
            
            if cards:
                # 파일 저장
                base_name = selected_file.stem
                anki_path, csv_path, json_path = maker.save_flashcards(cards, base_name)
                
                # 통계 출력
                stats = maker.generate_statistics(cards)
                print(f"\n=== 생성 통계 ===")
                print(f"총 카드 수: {stats['total_cards']}")
                print(f"평균 질문 길이: {stats['avg_question_length']:.1f}자")
                print(f"평균 답변 길이: {stats['avg_answer_length']:.1f}자")
                
                if stats['tags_distribution']:
                    print(f"태그 분포: {dict(list(stats['tags_distribution'].items())[:5])}")
                
                print(f"\n파일 저장 위치:")
                print(f"- Anki: {anki_path}")
                print(f"- CSV: {csv_path}")
                print(f"- JSON: {json_path}")
            else:
                print("플래시카드가 생성되지 않았습니다.")
            
    except Exception as e:
        logging.error(f"처리 중 오류 발생: {e}")
        print(f"오류가 발생했습니다: {e}")
        print("로그 파일을 확인하세요.")


if __name__ == "__main__":
    main() 