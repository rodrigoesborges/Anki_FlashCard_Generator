#!/usr/bin/env python3
"""
다중 LLM 제공자 데모 스크립트
다양한 LLM 제공자를 사용하여 플래시카드 생성을 시연합니다.
"""

import os
from dotenv import load_dotenv
from Anki_flashcards_creator import LLMConfig, call_llm_api

# 환경 변수 로드
load_dotenv()

def demo_with_provider(provider_name, model_name=None):
    """특정 제공자로 데모 실행"""
    print(f"\n=== {provider_name.upper()} 데모 ===")
    
    # 환경 변수 임시 설정
    original_provider = os.getenv('LLM_PROVIDER')
    os.environ['LLM_PROVIDER'] = provider_name
    
    if model_name:
        if provider_name == 'ollama':
            os.environ['OLLAMA_MODEL'] = model_name
        elif provider_name == 'openai':
            os.environ['OPENAI_MODEL'] = model_name
        elif provider_name == 'openrouter':
            os.environ['OPENROUTER_MODEL'] = model_name
    
    # 새로운 설정으로 LLMConfig 생성
    config = LLMConfig()
    
    # 테스트 텍스트
    test_text = """
    머신러닝은 인공지능의 한 분야로, 컴퓨터가 명시적으로 프로그래밍되지 않고도 
    데이터로부터 학습할 수 있게 하는 기술입니다. 지도학습, 비지도학습, 강화학습의 
    세 가지 주요 유형이 있습니다.
    """
    
    messages = [
        {"role": "system", "content": "당신은 효과적인 학습 도구를 만드는 전문가입니다."},
        {"role": "user", "content": f"다음 텍스트를 바탕으로 3개의 Anki 플래시카드를 생성해주세요. 형식: 질문;답변 (각 카드는 새 줄에 작성)\\n\\n텍스트: {test_text}"}
    ]
    
    try:
        print(f"모델: {config.ollama_model if provider_name == 'ollama' else config.openai_model if provider_name == 'openai' else config.openrouter_model}")
        
        response = call_llm_api(messages)
        print(f"✅ 성공!")
        print(f"생성된 플래시카드:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ 실패: {e}")
    
    # 원래 설정 복원
    if original_provider:
        os.environ['LLM_PROVIDER'] = original_provider

def main():
    print("다중 LLM 제공자 데모")
    print("현재 사용 가능한 제공자들로 플래시카드 생성을 테스트합니다.")
    
    # Ollama 테스트 (gemma3:latest)
    demo_with_provider('ollama', 'gemma3:latest')
    
    # 다른 Ollama 모델들도 테스트해볼 수 있습니다
    # demo_with_provider('ollama', 'llama3.2')
    # demo_with_provider('ollama', 'mistral')
    
    # OpenAI 테스트 (API 키가 있는 경우)
    if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your-openai-api-key-here':
        demo_with_provider('openai', 'gpt-3.5-turbo')
    else:
        print("\\n=== OPENAI 데모 ===")
        print("❌ OpenAI API 키가 설정되지 않았습니다.")
    
    # OpenRouter 테스트 (API 키가 있는 경우)
    if os.getenv('OPENROUTER_API_KEY') and os.getenv('OPENROUTER_API_KEY') != 'your-openrouter-api-key-here':
        demo_with_provider('openrouter', 'meta-llama/llama-3.2-3b-instruct:free')
    else:
        print("\\n=== OPENROUTER 데모 ===")
        print("❌ OpenRouter API 키가 설정되지 않았습니다.")

if __name__ == "__main__":
    main()