"""
텍스트 처리 유틸리티
"""
import re
from typing import List
import tiktoken


class TextProcessor:
    """텍스트 처리 및 분할 클래스"""
    
    @staticmethod
    def estimate_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
        """텍스트의 토큰 수 추정"""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except:
            encoding = tiktoken.get_encoding("cl100k_base")
        
        return len(encoding.encode(text))
    
    @staticmethod
    def smart_divide_text(text: str, max_tokens: int = 1500) -> List[str]:
        """의미 있는 단위로 텍스트 분할"""
        # 문장 단위로 분할
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        sections = []
        current_section: List[str] = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = TextProcessor.estimate_tokens(sentence)
            
            if current_tokens + sentence_tokens > max_tokens and current_section:
                sections.append(' '.join(current_section))
                current_section = [sentence]
                current_tokens = sentence_tokens
            else:
                current_section.append(sentence)
                current_tokens += sentence_tokens
        
        if current_section:
            sections.append(' '.join(current_section))
        
        return sections
    
    @staticmethod
    def extract_key_concepts(text: str) -> List[str]:
        """텍스트에서 핵심 개념 추출"""
        # 간단한 키워드 추출 (향후 NLP 라이브러리로 개선 가능)
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        concepts = list(set(words))[:10]  # 상위 10개 개념
        return concepts
    
    @staticmethod
    def clean_text(text: str) -> str:
        """텍스트 정리"""
        # 여러 공백을 하나로
        text = re.sub(r'\s+', ' ', text)
        # 줄바꿈 정리
        text = re.sub(r'\n+', ' ', text)
        # 특수문자 정리
        text = re.sub(r'[^\w\s.!?가-힣]', '', text)
        
        return text.strip() 