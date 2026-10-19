import re
from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class PtCitizenCardRecognizer(PatternRecognizer):
    """
    Recognize the document number of the Portuguese Cartão de Cidadão.

    The printed document number has 12 alphanumeric characters, usually written
    as ``12345678 9 ZZ4``: the 8-digit civil identification number (NIC), its
    check digit, a two-character document version, and a final check digit
    covering the whole number.

    The final check digit is computed with a Luhn-style algorithm over the
    base-36 alphabet (0-9, A-Z): working from the right, every second
    character value is doubled (subtracting 9 if the result exceeds 9), and
    the check digit is ``(10 - sum) % 10``.
    Reference: Validação de Número de Documento do Cartão de Cidadão,
    https://www.autenticacao.gov.pt/documents/20126/115760/Validação+de+Número+de+Documento+do+Cartão+de+Cidadão.pdf

    The check digit is part of the document number, so a failing checksum
    discards the match and a passing one raises it to the maximum score.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
        for different strings to be used during pattern matching.
    :param name: Name of the recognizer
    """

    COUNTRY_CODE = "pt"

    ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    PATTERNS = [
        Pattern(
            "Citizen card (medium)",
            r"(?<![\w-])\d{8}[ -]?\d[ -]?[A-Z0-9]{2}\d(?![\w-])",
            0.3,
        ),
    ]

    CONTEXT = [
        "cidadão",
        "cidadao",
        "citizen",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "pt",
        supported_entity: str = "PT_CITIZEN_CARD",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        name: Optional[str] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs if replacement_pairs else [("-", ""), (" ", "")]
        )
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
            name=name,
        )

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """Validate the final check digit of the document number."""
        sanitized = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        ).upper()
        if not re.fullmatch(r"\d{9}[A-Z0-9]{2}\d", sanitized):
            return None
        total = 0
        for i, char in enumerate(reversed(sanitized[:-1])):
            value = self.ALPHABET.index(char)
            if i % 2 == 0:
                value *= 2
                if value > 9:
                    value -= 9
            total += value
        return str((10 - total) % 10) == sanitized[-1]
