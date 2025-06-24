"""
커스텀 API 서비스 구현
"""
import asyncio
import json
import logging
from typing import List, Optional
import aiohttp
from ..IService.custom_api_service_interface import CustomApiServiceInterface
from ..Entity.custom_api_message import CustomApiMessage, CustomApiResponse
from ..Config.llm_config import LLMConfig


class CustomApiService(CustomApiServiceInterface):
    """커스텀 API 서비스 구현 클래스"""
    
    def __init__(self, config: LLMConfig):
        """
        커스텀 API 서비스 초기화
        
        Args:
            config (LLMConfig): LLM 설정 객체
        """
        self.config = config
        self.base_url = getattr(config, 'custom_api_base_url', 'http://localhost:3284')
        self.timeout = getattr(config, 'custom_api_timeout', 30)
        self.enabled = getattr(config, 'custom_api_enabled', True)
        self.logger = logging.getLogger(__name__)
        
    async def get_messages(self) -> CustomApiResponse:
        """
        메시지 목록 조회
        
        Returns:
            CustomApiResponse: API 응답 데이터
            
        Raises:
            Exception: API 호출 실패 시
        """
        if not self.enabled:
            raise Exception("커스텀 API가 비활성화되어 있습니다")
            
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(f"{self.base_url}/messages") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 메시지 파싱
                        messages = []
                        for msg_data in data.get('messages', []):
                            message = CustomApiMessage(
                                id=msg_data['id'],
                                content=msg_data['content'],
                                role=msg_data['role'],
                                time=msg_data['time']
                            )
                            messages.append(message)
                        
                        return CustomApiResponse(
                            schema=data.get('$schema', ''),
                            messages=messages
                        )
                    else:
                        raise Exception(f"API 호출 실패: HTTP {response.status}")
                        
        except aiohttp.ClientError as e:
            self.logger.error(f"커스텀 API 연결 오류: {e}")
            raise Exception(f"API 연결 실패: {e}")
        except Exception as e:
            self.logger.error(f"메시지 조회 오류: {e}")
            raise
    
    async def send_message(self, content: str, role: str = 'user') -> bool:
        """
        메시지 전송 (구현 예정)
        
        Args:
            content (str): 메시지 내용
            role (str): 메시지 역할
            
        Returns:
            bool: 전송 성공 여부
        """
        if not self.enabled:
            self.logger.warning("커스텀 API가 비활성화되어 있습니다")
            return False
            
        # 현재 API에 POST 엔드포인트가 없으므로 로그만 남김
        self.logger.info(f"메시지 전송 시도: {role} - {content[:50]}...")
        
        # TODO: POST /messages 엔드포인트 구현 시 실제 전송 로직 추가
        return True
    
    async def get_latest_message(self) -> Optional[CustomApiMessage]:
        """
        최신 메시지 조회
        
        Returns:
            Optional[CustomApiMessage]: 최신 메시지 또는 None
        """
        try:
            response = await self.get_messages()
            return response.get_latest_message()
        except Exception as e:
            self.logger.error(f"최신 메시지 조회 실패: {e}")
            return None
    
    def is_api_available(self) -> bool:
        """
        API 사용 가능 여부 확인
        
        Returns:
            bool: API 사용 가능 여부
        """
        if not self.enabled:
            return False
            
        try:
            # 동기 방식으로 간단한 연결 테스트
            import requests
            response = requests.get(f"{self.base_url}/messages", timeout=5)
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"API 연결 테스트 실패: {e}")
            return False 