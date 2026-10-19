from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class PtSnsNumberRecognizer(PatternRecognizer):
    """
    Recognize the Portuguese SNS user number (Número de Utente do SNS).

    The Serviço Nacional de Saúde (SNS) user number identifies a patient in
    the national health service and has 9 digits. It has no distinguishing
    structure and cannot be told apart from a NIF or phone number by format,
    so the pattern is very weak and the score is raised by context words only.
    Reference: SNS, https://www.sns.gov.pt (Número de Utente)

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param name: Name of the recognizer
    """

    COUNTRY_CODE = "pt"

    PATTERNS = [
        Pattern(
            "SNS number (very weak)",
            r"(?<![\w-])(?<!\d\.)\d{9}(?![\w-]|\.?\d)",
            0.05,
        ),
    ]

    CONTEXT = [
        "utente",
        "sns",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "pt",
        supported_entity: str = "PT_SNS_NUMBER",
        name: Optional[str] = None,
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
            name=name,
        )
