"""
커스텀 API 서비스 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..Entity.custom_api_message import CustomApiMessage, CustomApiResponse


class CustomApiServiceInterface(ABC):
    """커스텀 API 서비스 인터페이스"""
    
    @abstractmethod
    async def get_messages(self) -> CustomApiResponse:
        """
        메시지 목록 조회
        
        Returns:
            CustomApiResponse: API 응답 데이터
        """
        pass
    
    @abstractmethod
    async def send_message(self, content: str, role: str = 'user') -> bool:
        """
        메시지 전송
        
        Args:
            content (str): 메시지 내용
            role (str): 메시지 역할 (user/agent)
            
        Returns:
            bool: 전송 성공 여부
        """
        pass
    
    @abstractmethod
    async def get_latest_message(self) -> Optional[CustomApiMessage]:
        """
        최신 메시지 조회
        
        Returns:
            Optional[CustomApiMessage]: 최신 메시지 또는 None
        """
        pass
    
    @abstractmethod
    def is_api_available(self) -> bool:
        """
        API 사용 가능 여부 확인
        
        Returns:
            bool: API 사용 가능 여부
        """
        pass 