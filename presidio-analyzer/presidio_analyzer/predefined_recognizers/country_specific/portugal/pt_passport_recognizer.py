from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class PtPassportRecognizer(PatternRecognizer):
    """
    Recognize Portuguese passport numbers.

    Passports issued by the Portuguese Instituto dos Registos e do Notariado
    (IRN) since 2006 carry a number made of one letter followed by six digits
    (e.g. ``N123456``). The format has no check digit and no structure beyond
    its length, so the pattern is very weak and relies on context words.
    Reference: https://www.irn.mj.pt (Passaporte Eletrónico Português)

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param name: Name of the recognizer
    """

    COUNTRY_CODE = "pt"

    PATTERNS = [
        Pattern(
            "Passport (very weak)",
            r"(?<![\w-])[A-Z]\d{6}(?![\w-])",
            0.05,
        ),
    ]

    CONTEXT = [
        "passaporte",
        "passport",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "pt",
        supported_entity: str = "PT_PASSPORT",
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
