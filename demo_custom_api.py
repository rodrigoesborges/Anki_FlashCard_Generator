#!/usr/bin/env python3
"""
커스텀 API (localhost:3284) 연동 데모
"""
import asyncio
import sys
import os

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.dirname(__file__))

from src.Config.llm_config import LLMConfig
from src.Service.custom_api_service import CustomApiService


async def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("🚀 커스텀 API (localhost:3284) 연동 테스트")
    print("=" * 50)
    
    # 설정 초기화
    try:
        config = LLMConfig()
        api_service = CustomApiService(config)
        
        print(f"📡 API 주소: {api_service.base_url}")
        print(f"⏱️  타임아웃: {api_service.timeout}초")
        print(f"✅ 활성화 상태: {api_service.enabled}")
        print()
        
        # 1. API 가용성 확인
        print("🔍 API 가용성 확인 중...")
        is_available = api_service.is_api_available()
        print(f"   결과: {'✅ 사용 가능' if is_available else '❌ 사용 불가능'}")
        print()
        
        if not is_available:
            print("⚠️  API가 사용 불가능합니다. localhost:3284가 실행 중인지 확인하세요.")
            print("   curl localhost:3284/messages 명령으로 직접 테스트해보세요.")
            return
        
        # 2. 메시지 조회
        print("📨 메시지 조회 중...")
        try:
            response = await api_service.get_messages()
            print(f"   총 메시지 수: {len(response.messages)}개")
            
            if response.messages:
                # 최신 메시지 표시
                latest = response.get_latest_message()
                if latest:
                    print(f"   최신 메시지 ID: {latest.id}")
                    print(f"   최신 메시지 역할: {latest.role}")
                    print(f"   최신 메시지 시간: {latest.time}")
                    print(f"   최신 메시지 내용: {latest.content[:200]}...")
                    print()
                
                # 메시지 분류 통계
                user_msgs = response.get_user_messages()
                agent_msgs = response.get_agent_messages()
                print(f"   👤 사용자 메시지: {len(user_msgs)}개")
                print(f"   🤖 에이전트 메시지: {len(agent_msgs)}개")
                print()
                
                # 최근 5개 메시지 미리보기
                print("📋 최근 메시지 미리보기:")
                recent_messages = sorted(response.messages, key=lambda x: x.time, reverse=True)[:5]
                for i, msg in enumerate(recent_messages, 1):
                    role_icon = "👤" if msg.role == "user" else "🤖"
                    content_preview = msg.content.replace('\n', ' ')[:100]
                    print(f"   {i}. {role_icon} [{msg.role}] {content_preview}...")
                print()
                
            else:
                print("   📭 메시지가 없습니다.")
                
        except Exception as e:
            print(f"   ❌ 메시지 조회 실패: {e}")
            return
        
        # 3. 메시지 전송 테스트
        print("📤 메시지 전송 테스트...")
        try:
            test_message = "안녕하세요! 플래시카드 생성 시스템에서 보내는 테스트 메시지입니다."
            result = await api_service.send_message(test_message, "user")
            if result:
                print("   ✅ 메시지 전송 성공 (로그 기록됨)")
            else:
                print("   ❌ 메시지 전송 실패")
        except Exception as e:
            print(f"   ❌ 메시지 전송 오류: {e}")
        
        print()
        print("🎉 테스트 완료!")
        print()
        print("💡 사용 방법:")
        print("   1. 환경 변수 설정: env_example.txt 파일을 참고하여 .env 파일을 생성하세요")
        print("   2. 의존성 설치: pip install -r requirements.txt")
        print("   3. API 활성화: CUSTOM_API_ENABLED=true로 설정")
        print("   4. 코드에서 사용: CustomApiService 클래스를 임포트하여 사용")
        
    except Exception as e:
        print(f"❌ 초기화 오류: {e}")
        print("   .env 파일이 올바르게 설정되었는지 확인하세요.")


if __name__ == "__main__":
    print("🔧 Python 가상환경 사용을 권장합니다: python -m venv .venv && source .venv/bin/activate")
    print()
    asyncio.run(main()) 