from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class PtNissRecognizer(PatternRecognizer):
    """
    Recognize Portuguese NISS (Número de Identificação da Segurança Social).

    The NISS has 11 digits: the first is 1 for individuals or 2 for
    legal entities, followed by nine sequence digits and a check digit.
    Reference: https://www.seg-social.pt (Instituto da Segurança Social, I.P.)

    The check digit is commonly documented (the Instituto da Segurança Social
    does not publish the algorithm) as ``9 - (sum % 10)`` where ``sum`` is the
    first ten digits multiplied by the weights 29, 23, 19, 17, 13, 11, 7, 5, 3,
    2. Because that algorithm is not from an official specification, it is
    only used to *raise* confidence: a passing checksum returns the maximum
    score, while a failing one leaves the pattern score untouched instead of
    discarding the match.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
        for different strings to be used during pattern matching.
    :param name: Name of the recognizer
    """

    COUNTRY_CODE = "pt"

    WEIGHTS = (29, 23, 19, 17, 13, 11, 7, 5, 3, 2)

    PATTERNS = [
        Pattern(
            "NISS (very weak)",
            r"(?<![\w-])(?<!\d\.)[12]\d{10}(?![\w-]|\.?\d)",
            0.1,
        ),
        Pattern(
            "NISS grouped (weak)",
            r"(?<![\w-])(?<!\d\.)[12]\d{2}[ -]\d{4}[ -]\d{4}(?![\w-]|\.?\d)",
            0.2,
        ),
    ]

    CONTEXT = [
        "niss",
        "segurança",
        "seguranca",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "pt",
        supported_entity: str = "PT_NISS",
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
        """Raise confidence when the check digit matches; never discard."""
        sanitized = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        )
        if len(sanitized) != 11 or not sanitized.isdigit():
            return None
        total = sum(w * int(d) for w, d in zip(self.WEIGHTS, sanitized[:10]))
        if 9 - total % 10 == int(sanitized[10]):
            return True
        return None
