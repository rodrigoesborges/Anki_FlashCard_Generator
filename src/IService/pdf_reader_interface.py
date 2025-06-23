"""
PDF 리더 서비스 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Tuple, Dict


class IPDFReaderService(ABC):
    """PDF 리더 서비스 인터페이스"""
    
    @abstractmethod
    def read_pdf(self, file_path: str) -> Tuple[str, Dict]:
        """PDF 파일을 읽고 텍스트와 메타데이터 반환"""
        pass 