"""
플래시카드 엔티티 정의
"""
from dataclasses import dataclass, field
from typing import List, Optional
import re


@dataclass
class Flashcard:
    """플래시카드 데이터 클래스"""
    question: str
    answer: str
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    
    def to_anki_format(self) -> str:
        """Anki 임포트 형식으로 변환"""
        tags_str = ' '.join(self.tags) if self.tags else ''
        return f"{self.question}\t{self.answer}\t{tags_str}"
    
    def is_valid(self) -> bool:
        """플래시카드 유효성 검사"""
        return bool(self.question.strip() and self.answer.strip())
    
    def calculate_quality_score(self, llm_client=None) -> float:
        """LLM을 사용하여 카드 품질 점수 계산 (0-1)"""
        if not llm_client:
            return 0.5  # 기본 점수
            
        validation_prompt = f"""
다음 플래시카드의 품질을 0-10 점수로 평가해주세요.

질문: {self.question}
답변: {self.answer}

평가 기준:
- 질문이 명확하고 구체적인가?
- 답변이 질문에 정확히 대답하는가?
- 답변이 의미있고 학습에 도움이 되는가?
- 답변이 "모르겠다", "언급되지 않음" 같은 무의미한 내용인가?

점수만 숫자로 답변하세요 (예: 8).
"""
        
        try:
            messages = [
                {"role": "system", "content": "당신은 교육 콘텐츠 품질 평가 전문가입니다."},
                {"role": "user", "content": validation_prompt}
            ]
            
            response = llm_client.call_api_with_retry(messages)
            match = re.search(r'\d+', response)
            if match:
                score = float(match.group()) / 10.0
                return min(max(score, 0.0), 1.0)  # 0-1 범위로 제한
            return 0.5
        except:
            return 0.5  # 오류 시 중간 점수 