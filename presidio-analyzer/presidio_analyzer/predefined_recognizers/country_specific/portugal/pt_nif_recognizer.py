import re
from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class PtNifRecognizer(PatternRecognizer):
    """
    Recognize Portuguese NIF/NIPC (Número de Identificação Fiscal) numbers.

    The NIF is a 9-digit tax number issued by the Autoridade Tributária e
    Aduaneira (AT) to individuals and legal entities (where it is also called
    NIPC). The first digit(s) encode the holder type: 1-3 individuals, 45
    non-resident individuals, 5 companies, 6 public administration, 70-79
    special entities (heritages, non-resident entities, investment funds),
    8 sole proprietors (discontinued), 90/91/98/99 other entities.

    The last digit is a modulo-11 check digit: the first eight digits are
    multiplied by the weights 9 down to 2 and summed; the check digit is
    ``11 - (sum % 11)``, taken as 0 when the result is 10 or 11.
    Reference: https://pt.wikipedia.org/wiki/N%C3%BAmero_de_identifica%C3%A7%C3%A3o_fiscal

    The check digit is mandatory for every NIF, so a failing checksum discards
    the match and a passing one raises it to the maximum score. About one in
    ten arbitrary 9-digit numbers passes, hence the low base score of the bare
    pattern.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
        for different strings to be used during pattern matching.
    :param name: Name of the recognizer
    """

    COUNTRY_CODE = "pt"

    _PREFIX = r"(?:[1235689]\d|45|7[01245789])"

    PATTERNS = [
        Pattern(
            "NIF (very weak)",
            r"(?<![\w-])(?<!\d\.)" + _PREFIX + r"\d{7}(?![\w-]|\.?\d)",
            0.1,
        ),
        Pattern(
            "NIF grouped (weak)",
            r"(?<![\w-])(?<!\d\.)[1235689]\d{2}[ .-]\d{3}[ .-]\d{3}(?![\w-]|\.?\d)",
            0.2,
        ),
        Pattern(
            "NIF with PT prefix (medium)",
            r"(?<![\w-])(?<!\d\.)PT[ -]?[1235689]\d{2}[ .-]?\d{3}[ .-]?\d{3}"
            r"(?![\w-]|\.?\d)",
            0.4,
        ),
    ]

    CONTEXT = [
        "nif",
        "nipc",
        "contribuinte",
        "fiscal",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "pt",
        supported_entity: str = "PT_NIF",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        name: Optional[str] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs
            if replacement_pairs
            else [("-", ""), (" ", ""), (".", "")]
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
        """Validate the modulo-11 check digit of the NIF."""
        sanitized = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        ).upper()
        sanitized = re.sub(r"^PT", "", sanitized)
        if len(sanitized) != 9 or not sanitized.isdigit():
            return None
        total = sum((9 - i) * int(digit) for i, digit in enumerate(sanitized[:8]))
        check_digit = (11 - total) % 11 % 10
        return check_digit == int(sanitized[8])
