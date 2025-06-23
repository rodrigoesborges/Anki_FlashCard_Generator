"""
파일 리더 서비스 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Tuple, Dict


class IFileReaderService(ABC):
    """파일 리더 서비스 인터페이스"""
    
    @abstractmethod
    def read_file(self, file_path: str) -> Tuple[str, Dict]:
        """파일을 읽고 텍스트와 메타데이터 반환"""
        pass 