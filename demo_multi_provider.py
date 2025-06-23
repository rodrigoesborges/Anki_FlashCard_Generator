#!/usr/bin/env python3
"""
여러 LLM 제공자 데모
"""
import sys
import os
import time

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.Config.llm_config import LLMConfig
from src.Service.llm_service import LLMService


def demo_provider(provider_name: str):
    """특정 제공자로 플래시카드 생성 데모"""
    print(f"\n{'='*60}")
    print(f"제공자: {provider_name}")
    print('='*60)
    
    # 임시로 provider 설정
    os.environ['LLM_PROVIDER'] = provider_name
    
    try:
        config = LLMConfig()
        llm_service = LLMService(config)
        
        # 테스트 텍스트
        test_text = """
        인공지능(AI)은 기계가 인간의 지능을 모방하여 학습, 추론, 자가 수정 등을 수행하는 기술입니다.
        머신러닝은 AI의 한 분야로, 명시적으로 프로그래밍하지 않아도 데이터로부터 패턴을 학습합니다.
        딥러닝은 머신러닝의 하위 분야로, 인공 신경망을 사용하여 복잡한 패턴을 학습합니다.
        """
        
        # 플래시카드 생성 요청
        messages = [
            {"role": "system", "content": """당신은 Anki 플래시카드 전문가입니다.
            주어진 텍스트에서 핵심 개념을 추출하여 효과적인 플래시카드를 만드세요.
            형식: Q: [질문] / A: [답변]"""},
            {"role": "user", "content": f"다음 텍스트에서 3개의 플래시카드를 생성하세요:\n\n{test_text}"}
        ]
        
        start_time = time.time()
        response = llm_service.call_api_with_retry(messages)
        end_time = time.time()
        
        print(f"\n✅ 성공!")
        print(f"응답 시간: {end_time - start_time:.2f}초")
        print(f"\n생성된 플래시카드:")
        print("-" * 60)
        print(response)
        print("-" * 60)
        
        # 모델 정보 출력
        if provider_name == 'openai':
            print(f"사용된 모델: {config.openai_model}")
        elif provider_name == 'ollama':
            print(f"사용된 모델: {config.ollama_model}")
        elif provider_name == 'openrouter':
            print(f"사용된 모델: {config.openrouter_model}")
            
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("\n해결 방법:")
        if provider_name == 'ollama':
            print("- Ollama가 실행 중인지 확인: ollama serve")
            print("- 모델이 설치되어 있는지 확인: ollama list")
        elif provider_name == 'openai':
            print("- OpenAI API 키 확인")
            print("- API 크레딧 확인")
        elif provider_name == 'openrouter':
            print("- OpenRouter API 키 확인")
            print("- 선택한 모델의 사용 가능 여부 확인")


def main():
    """메인 데모 실행"""
    print("=== 멀티 LLM 제공자 플래시카드 생성 데모 ===")
    print("\n이 데모는 다양한 LLM 제공자를 사용하여 동일한 텍스트에서")
    print("플래시카드를 생성하는 예제를 보여줍니다.")
    
    # 원래 설정 백업
    original_provider = os.getenv('LLM_PROVIDER', 'ollama')
    
    # 테스트할 제공자 목록
    providers = ['ollama', 'openai', 'openrouter']
    
    for provider in providers:
        try:
            demo_provider(provider)
        except Exception as e:
            print(f"\n{provider} 데모 실패: {e}")
    
    # 원래 설정 복원
    os.environ['LLM_PROVIDER'] = original_provider
    
    print("\n\n=== 데모 완료 ===")
    print("각 제공자의 출력 스타일과 응답 시간을 비교해보세요.")


if __name__ == "__main__":
    main()