"""
서비스 인터페이스 모듈
"""
from .llm_service_interface import ILLMService
from .pdf_reader_interface import IFileReaderService
from .flashcard_generator_interface import IFlashcardGeneratorService
from .export_service_interface import IExportService

__all__ = [
    'ILLMService',
    'IFileReaderService',
    'IFlashcardGeneratorService',
    'IExportService'
] 