"""
PDF 리더 서비스 구현
"""
import os
import re
import logging
from typing import Tuple, Dict
import PyPDF2

from src.IService.pdf_reader_interface import IPDFReaderService


class PDFReaderService(IPDFReaderService):
    """향상된 PDF 읽기 서비스"""
    
    def read_pdf(self, file_path: str) -> Tuple[str, Dict]:
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