"""
파일 리더 서비스 구현 (PDF, Markdown, Text 지원)
"""
import os
import re
import logging
from pathlib import Path
from typing import Tuple, Dict
import PyPDF2

from src.IService.pdf_reader_interface import IFileReaderService


class FileReaderService(IFileReaderService):
    """다양한 파일 형식을 지원하는 파일 리더 서비스"""
    
    def read_file(self, file_path: str) -> Tuple[str, Dict]:
        """파일을 읽고 메타데이터 추출"""
        file_path_obj = Path(file_path)
        file_extension = file_path_obj.suffix.lower()
        
        metadata = {
            'title': file_path_obj.stem,
            'author': '',
            'pages': 0,
            'file_name': file_path_obj.name,
            'file_type': file_extension
        }
        
        try:
            if file_extension == '.pdf':
                return self._read_pdf(file_path, metadata)
            elif file_extension in ['.md', '.markdown']:
                return self._read_markdown(file_path, metadata)
            elif file_extension in ['.txt', '.text']:
                return self._read_text(file_path, metadata)
            else:
                raise ValueError(f"지원하지 않는 파일 형식입니다: {file_extension}")
                
        except Exception as e:
            logging.error(f"파일 읽기 오류 ({file_path}): {e}")
            raise
    
    def _read_pdf(self, file_path: str, metadata: Dict) -> Tuple[str, Dict]:
        """PDF 파일 읽기"""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # 메타데이터 추출
            if reader.metadata:
                metadata['title'] = reader.metadata.get('/Title', metadata['title'])
                metadata['author'] = reader.metadata.get('/Author', '')
            
            metadata['pages'] = len(reader.pages)
            
            # 텍스트 추출
            text_parts = []
            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    logging.warning(f"PDF 페이지 {i+1} 읽기 실패: {e}")
            
            text = " ".join(text_parts)
            text = self._clean_text(text)
            
            return text, metadata
    
    def _read_markdown(self, file_path: str, metadata: Dict) -> Tuple[str, Dict]:
        """Markdown 파일 읽기"""
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # 첫 번째 헤더를 제목으로 추출 시도
        lines = text.split('\n')
        for line in lines[:5]:  # 처음 5줄만 확인
            if line.strip().startswith('#'):
                metadata['title'] = line.strip().lstrip('#').strip()
                break
        
        # 대략적인 페이지 수 계산 (2000자당 1페이지로 가정)
        metadata['pages'] = max(1, len(text) // 2000)
        
        return text, metadata
    
    def _read_text(self, file_path: str, metadata: Dict) -> Tuple[str, Dict]:
        """텍스트 파일 읽기"""
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # 대략적인 페이지 수 계산 (2000자당 1페이지로 가정)
        metadata['pages'] = max(1, len(text) // 2000)
        
        return text, metadata
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        # 연속된 공백을 하나로 통합
        text = re.sub(r'\s+', ' ', text)
        # 하이픈으로 분리된 단어 재결합
        text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)
        return text.strip()


# 기존 클래스명과의 호환성을 위한 별칭
PDFReaderService = FileReaderService 