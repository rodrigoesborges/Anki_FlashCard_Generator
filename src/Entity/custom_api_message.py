"""
커스텀 API 메시지 엔티티
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class CustomApiMessage:
    """커스텀 API 메시지 클래스"""
    id: int
    content: str
    role: str
    time: str
    
    def __post_init__(self):
        """메시지 유효성 검증"""
        if not isinstance(self.id, int):
            raise ValueError("메시지 ID는 정수여야 합니다")
        if not self.content.strip():
            raise ValueError("메시지 내용은 비어있을 수 없습니다")
        if self.role not in ['user', 'agent']:
            raise ValueError("역할은 'user' 또는 'agent'여야 합니다")


@dataclass
class CustomApiResponse:
    """커스텀 API 응답 클래스"""
    schema: str
    messages: List[CustomApiMessage]
    
    def get_latest_message(self) -> Optional[CustomApiMessage]:
        """최신 메시지 반환"""
        if not self.messages:
            return None
        return max(self.messages, key=lambda msg: msg.time)
    
    def get_user_messages(self) -> List[CustomApiMessage]:
        """사용자 메시지만 반환"""
        return [msg for msg in self.messages if msg.role == 'user']
    
    def get_agent_messages(self) -> List[CustomApiMessage]:
        """에이전트 메시지만 반환"""
        return [msg for msg in self.messages if msg.role == 'agent'] 