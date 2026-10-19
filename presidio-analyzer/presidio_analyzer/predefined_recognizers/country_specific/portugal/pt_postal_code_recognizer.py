from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class PtPostalCodeRecognizer(PatternRecognizer):
    """
    Recognize Portuguese postal codes (código postal).

    The format is ``NNNN-NNN``: a four-digit code identifying the delivery
    area and a three-digit code identifying the street or delivery point.
    There is no check digit and not every combination is assigned, so the
    pattern is weak; context words raise it.
    Reference: CTT - Correios de Portugal, https://www.ctt.pt/particulares/codigo-postal

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param name: Name of the recognizer
    """

    COUNTRY_CODE = "pt"

    PATTERNS = [
        Pattern(
            "Postal code (weak)",
            r"(?<![\w-])[1-9]\d{3}-\d{3}(?![\w-])",
            0.1,
        ),
    ]

    CONTEXT = [
        "postal",
        "morada",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "pt",
        supported_entity: str = "PT_POSTAL_CODE",
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
