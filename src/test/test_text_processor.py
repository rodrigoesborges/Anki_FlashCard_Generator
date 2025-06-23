"""
텍스트 프로세서 테스트
"""
import unittest
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.Utils.text_processor import TextProcessor


class TestTextProcessor(unittest.TestCase):
    """TextProcessor 클래스 테스트"""
    
    def test_clean_text(self):
        """텍스트 정리 기능 테스트"""
        dirty_text = "  Hello   World!  \n\n  This is   a test.  "
        clean_text = TextProcessor.clean_text(dirty_text)
        self.assertEqual(clean_text, "Hello World! This is a test.")
    
    def test_extract_key_concepts(self):
        """핵심 개념 추출 테스트"""
        text = "Python Programming is great. Machine Learning and Deep Learning are important."
        concepts = TextProcessor.extract_key_concepts(text)
        self.assertIn("Python Programming", concepts)
        self.assertIn("Machine Learning", concepts)
        self.assertIn("Deep Learning", concepts)
    
    def test_smart_divide_text(self):
        """텍스트 분할 테스트"""
        text = "First sentence. Second sentence. Third sentence."
        sections = TextProcessor.smart_divide_text(text, max_tokens=50)
        self.assertTrue(len(sections) > 0)
        self.assertTrue(all(isinstance(s, str) for s in sections))


if __name__ == '__main__':
    unittest.main() 