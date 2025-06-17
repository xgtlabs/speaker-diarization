"""Exceptions personnalisées pour l'application"""

class DiarizationError(Exception):
    """Exception levée lors d'erreurs de diarisation"""
    pass

class SummarizationError(Exception):
    """Exception levée lors d'erreurs de génération de résumé"""
    pass

class AudioProcessingError(Exception):
    """Exception levée lors d'erreurs de traitement audio"""
    pass
