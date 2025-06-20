#!/usr/bin/env python3
"""
LLM 제공자 테스트 스크립트
각 LLM 제공자의 연결과 기본 기능을 테스트합니다.
"""

import os
from dotenv import load_dotenv
from Anki_flashcards_creator import LLMConfig, call_llm_api

# 환경 변수 로드
load_dotenv()

def test_llm_provider():
    """현재 설정된 LLM 제공자 테스트"""
    config = LLMConfig()
    
    print(f"=== {config.provider.upper()} 테스트 ===")
    
    # 테스트 메시지
    test_messages = [
        {"role": "system", "content": "당신은 도움이 되는 어시스턴트입니다."},
        {"role": "user", "content": "안녕하세요! 간단한 테스트입니다. '안녕하세요'라고 답변해주세요."}
    ]
    
    try:
        response = call_llm_api(test_messages)
        print(f"✅ 연결 성공!")
        print(f"응답: {response}")
        return True
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return False

def test_flashcard_generation():
    """플래시카드 생성 테스트"""
    print("\n=== 플래시카드 생성 테스트 ===")
    
    test_text = """
    파이썬은 1991년 귀도 반 로섬이 개발한 프로그래밍 언어입니다. 
    파이썬은 간결하고 읽기 쉬운 문법을 가지고 있으며, 다양한 분야에서 사용됩니다.
    특히 데이터 과학, 웹 개발, 인공지능 분야에서 널리 사용됩니다.
    """
    
    messages = [
        {"role": "system", "content": "당신은 효과적인 학습 도구를 만드는 전문가입니다."},
        {"role": "user", "content": f"다음 텍스트를 바탕으로 Anki 플래시카드를 생성해주세요. 형식: 질문;답변 (각 카드는 새 줄에 작성)\n\n텍스트: {test_text}"}
    ]
    
    try:
        response = call_llm_api(messages)
        print(f"✅ 플래시카드 생성 성공!")
        print(f"생성된 플래시카드:\n{response}")
        return True
    except Exception as e:
        print(f"❌ 플래시카드 생성 실패: {e}")
        return False

if __name__ == "__main__":
    print("LLM 제공자 테스트 시작...\n")
    
    # 기본 연결 테스트
    connection_success = test_llm_provider()
    
    if connection_success:
        # 플래시카드 생성 테스트
        test_flashcard_generation()
    else:
        print("\n연결 테스트에 실패했습니다. 설정을 확인해주세요.")
        print("\n설정 확인사항:")
        print("1. .env 파일이 존재하는지 확인")
        print("2. LLM_PROVIDER 값이 올바른지 확인 (openai, ollama, openrouter)")
        print("3. 해당 제공자의 API 키 또는 서비스가 활성화되어 있는지 확인")
        
        if os.getenv('LLM_PROVIDER') == 'ollama':
            print("4. Ollama가 실행 중인지 확인: ollama serve")
            print("5. 모델이 다운로드되어 있는지 확인: ollama list")