#!/usr/bin/env python3
"""
LLM 제공자 연결 테스트
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.Config.llm_config import LLMConfig
from src.Service.llm_service import LLMService


def test_current_provider():
    """현재 설정된 LLM 제공자 테스트"""
    config = LLMConfig()
    llm_service = LLMService(config)
    
    print(f"현재 LLM 제공자: {config.provider}")
    print(f"테스트 중...")
    
    try:
        # 간단한 테스트 메시지
        messages = [
            {"role": "system", "content": "당신은 도움이 되는 AI 어시스턴트입니다."},
            {"role": "user", "content": "안녕하세요! 간단히 자기소개를 해주세요."}
        ]
        
        response = llm_service.call_api_with_retry(messages)
        print(f"\n응답 성공!")
        print(f"응답 내용: {response[:200]}...")
        
        # 연결 정보 출력
        if config.provider == 'openai':
            print(f"\nOpenAI 모델: {config.openai_model}")
        elif config.provider == 'ollama':
            print(f"\nOllama URL: {config.ollama_base_url}")
            print(f"Ollama 모델: {config.ollama_model}")
        elif config.provider == 'openrouter':
            print(f"\nOpenRouter 모델: {config.openrouter_model}")
            
    except Exception as e:
        print(f"\n오류 발생: {e}")
        print("\n가능한 해결 방법:")
        
        if config.provider == 'ollama':
            print("1. Ollama가 실행 중인지 확인하세요: ollama serve")
            print("2. 모델이 설치되어 있는지 확인하세요: ollama pull llama3.2")
        elif config.provider == 'openai':
            print("1. OpenAI API 키가 올바른지 확인하세요")
            print("2. API 키에 크레딧이 있는지 확인하세요")
        elif config.provider == 'openrouter':
            print("1. OpenRouter API 키가 올바른지 확인하세요")
            print("2. 선택한 모델이 사용 가능한지 확인하세요")


def test_all_providers():
    """모든 LLM 제공자 테스트 (선택사항)"""
    providers = ['ollama', 'openai', 'openrouter']
    
    for provider in providers:
        print(f"\n{'='*50}")
        print(f"테스트: {provider}")
        print('='*50)
        
        # 임시로 provider 변경
        os.environ['LLM_PROVIDER'] = provider
        
        try:
            test_current_provider()
        except Exception as e:
            print(f"{provider} 테스트 실패: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='LLM 제공자 연결 테스트')
    parser.add_argument('--all', action='store_true', help='모든 제공자 테스트')
    
    args = parser.parse_args()
    
    if args.all:
        test_all_providers()
    else:
        test_current_provider()