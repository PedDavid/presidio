from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class PtPhoneNumberRecognizer(PatternRecognizer):
    """
    Recognize Portuguese phone numbers.

    Portuguese numbers have 9 digits (national significant number): geographic
    numbers start with ``2`` (e.g. 21 Lisbon, 22 Porto) and mobile numbers
    with ``91``, ``92``, ``93`` or ``96``. They may be preceded by the country
    code ``+351`` or ``00351``. The format has no check digit.
    Reference: ANACOM, Plano Nacional de Numeração,
    https://www.anacom.pt/render.jsp?contentId=1070592

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param name: Name of the recognizer
    """

    COUNTRY_CODE = "pt"

    _NUMBER = r"(?:9[1236]\d|2\d{2})"

    PATTERNS = [
        Pattern(
            "Phone with country code (medium)",
            r"(?<![\w+])(?<!\d\.)(?:\+|00)351[ .-]?"
            + _NUMBER
            + r"[ .-]?\d{3}[ .-]?\d{3}(?!\d)",
            0.4,
        ),
        Pattern(
            "Phone grouped (weak)",
            r"(?<![\w+-])(?<!\d\.)" + _NUMBER + r"[ .-]\d{3}[ .-]\d{3}(?![\w-]|\.?\d)",
            0.2,
        ),
        Pattern(
            "Phone bare (very weak)",
            r"(?<![\w+-])(?<!\d\.)" + _NUMBER + r"\d{6}(?![\w-]|\.?\d)",
            0.05,
        ),
    ]

    CONTEXT = [
        "telefone",
        "telemóvel",
        "telemovel",
        "telefónico",
        "phone",
        "mobile",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "pt",
        supported_entity: str = "PT_PHONE_NUMBER",
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
