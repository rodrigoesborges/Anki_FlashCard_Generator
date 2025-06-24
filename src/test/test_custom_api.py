"""
커스텀 API 서비스 테스트
"""
import asyncio
import sys
import os

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.Config.llm_config import LLMConfig
from src.Service.custom_api_service import CustomApiService


class TestCustomApiService:
    """커스텀 API 서비스 테스트 클래스"""
    
    def setup_method(self):
        """테스트 초기화"""
        self.config = LLMConfig()
        self.api_service = CustomApiService(self.config)
    
    def test_api_service_initialization(self):
        """API 서비스 초기화 테스트"""
        assert self.api_service.base_url == 'http://localhost:3284'
        assert self.api_service.timeout == 30
        assert self.api_service.enabled is True
    
    async def test_get_messages(self):
        """메시지 조회 테스트"""
        try:
            response = await self.api_service.get_messages()
            assert response.messages is not None
            assert isinstance(response.messages, list)
            print(f"메시지 수: {len(response.messages)}")
            
            if response.messages:
                latest = response.get_latest_message()
                if latest:
                    print(f"최신 메시지: {latest.content[:50]}...")
                
        except Exception as e:
            print(f"API 테스트 실패 (예상 가능): {e}")
    
    def test_api_availability(self):
        """API 가용성 테스트"""
        is_available = self.api_service.is_api_available()
        print(f"API 사용 가능: {is_available}")
        
    async def test_send_message(self):
        """메시지 전송 테스트"""
        result = await self.api_service.send_message("테스트 메시지", "user")
        assert result is True
        print("메시지 전송 테스트 완료")


async def main():
    """비동기 테스트 실행"""
    print("=== 커스텀 API 서비스 테스트 시작 ===")
    
    config = LLMConfig()
    api_service = CustomApiService(config)
    
    # API 가용성 확인
    print(f"API 가용성: {api_service.is_api_available()}")
    
    try:
        # 메시지 조회 테스트
        response = await api_service.get_messages()
        print(f"총 메시지 수: {len(response.messages)}")
        
        if response.messages:
            latest = response.get_latest_message()
            if latest:
                print(f"최신 메시지 ID: {latest.id}")
                print(f"최신 메시지 역할: {latest.role}")
                print(f"최신 메시지 내용: {latest.content[:100]}...")
            
            # 사용자/에이전트 메시지 분류
            user_msgs = response.get_user_messages()
            agent_msgs = response.get_agent_messages()
            print(f"사용자 메시지: {len(user_msgs)}개")
            print(f"에이전트 메시지: {len(agent_msgs)}개")
        
        # 메시지 전송 테스트
        await api_service.send_message("플래시카드 생성 요청", "user")
        print("메시지 전송 완료")
        
    except Exception as e:
        print(f"테스트 실패: {e}")
    
    print("=== 테스트 완료 ===")


if __name__ == "__main__":
    asyncio.run(main()) 