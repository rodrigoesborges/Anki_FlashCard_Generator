"""
LLM 서비스 구현
"""
import time
import logging
import requests
from typing import List, Dict
import openai

from src.IService.llm_service_interface import ILLMService
from src.Config.llm_config import LLMConfig


class LLMService(ILLMService):
    """통합 LLM 서비스"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        if config.provider == 'openai':
            openai.api_key = config.openai_api_key
    
    def call_api_with_retry(self, messages: List[Dict]) -> str:
        """재시도 로직이 포함된 API 호출"""
        for attempt in range(self.config.max_retries):
            try:
                if self.config.provider == 'openai':
                    return self._call_openai(messages)
                elif self.config.provider == 'ollama':
                    return self._call_ollama(messages)
                elif self.config.provider == 'openrouter':
                    return self._call_openrouter(messages)
                else:
                    raise ValueError(f"지원되지 않는 LLM 제공자: {self.config.provider}")
                    
            except Exception as e:
                logging.warning(f"API 호출 실패 (시도 {attempt+1}/{self.config.max_retries}): {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                else:
                    raise
        
        # 모든 시도가 실패한 경우 (이론적으로 도달하지 않음)
        raise RuntimeError("모든 API 호출 시도가 실패했습니다.")
    
    def generate_prompt(self, system_prompt: str, user_prompt: str) -> List[Dict]:
        """프롬프트 생성"""
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def _call_openai(self, messages: List[Dict]) -> str:
        """OpenAI API 호출"""
        response = openai.ChatCompletion.create(
            model=self.config.openai_model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        return response['choices'][0]['message']['content']
    
    def _call_ollama(self, messages: List[Dict]) -> str:
        """Ollama API 호출"""
        prompt = self._format_messages_to_prompt(messages)
        
        url = f"{self.config.ollama_base_url}/api/generate"
        payload = {
            "model": self.config.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }
        
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        return response.json().get('response', '')
    
    def _call_openrouter(self, messages: List[Dict]) -> str:
        """OpenRouter API 호출"""
        url = f"{self.config.openrouter_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.openrouter_model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        
        return response.json()['choices'][0]['message']['content']
    
    def _format_messages_to_prompt(self, messages: List[Dict]) -> str:
        """메시지를 프롬프트로 변환"""
        prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                prompt += f"System: {msg['content']}\n\n"
            elif msg["role"] == "user":
                prompt += f"User: {msg['content']}\n\n"
            elif msg["role"] == "assistant":
                prompt += f"Assistant: {msg['content']}\n\n"
        return prompt 