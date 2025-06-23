"""
LLM 서비스 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Dict


class ILLMService(ABC):
    """LLM 서비스 인터페이스"""
    
    @abstractmethod
    def call_api_with_retry(self, messages: List[Dict]) -> str:
        """재시도 로직이 포함된 API 호출"""
        pass
    
    @abstractmethod
    def generate_prompt(self, system_prompt: str, user_prompt: str) -> List[Dict]:
        """프롬프트 생성"""
        pass 