"""
LLM 설정 관리
"""
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


class LLMConfig:
    """LLM 제공자 설정 클래스"""
    
    def __init__(self):
        # 기본 설정
        self.provider = os.getenv('LLM_PROVIDER', 'ollama')
        
        # OpenAI 설정
        self.openai_api_key = os.getenv('OPENAI_API_KEY', 'YOUR-OPENAI-API-KEY')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        # Ollama 설정
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        
        # OpenRouter 설정
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY', 'YOUR-OPENROUTER-API-KEY')
        self.openrouter_model = os.getenv('OPENROUTER_MODEL', 'meta-llama/llama-3.2-3b-instruct:free')
        self.openrouter_base_url = 'https://openrouter.ai/api/v1'
        
        # 공통 설정
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.retry_delay = int(os.getenv('RETRY_DELAY', '2'))
        self.temperature = float(os.getenv('TEMPERATURE', '0.3'))
        self.max_tokens = int(os.getenv('MAX_TOKENS', '2048'))
        
        # 플래시카드 생성 설정
        self.cards_per_section = int(os.getenv('CARDS_PER_SECTION', '5'))
        self.min_card_quality = float(os.getenv('MIN_CARD_QUALITY', '0.7'))
        
        # 커스텀 API 설정 (localhost:3284)
        self.custom_api_base_url = os.getenv('CUSTOM_API_BASE_URL', 'http://localhost:3284')
        self.custom_api_enabled = os.getenv('CUSTOM_API_ENABLED', 'true').lower() == 'true'
        self.custom_api_timeout = int(os.getenv('CUSTOM_API_TIMEOUT', '30')) 