from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class PtVehicleRegistrationRecognizer(PatternRecognizer):
    """
    Recognize Portuguese vehicle registration plates (matrícula).

    Plates are written as three hyphen-separated pairs, in the order of
    introduction:

    * ``AA-00-00`` (1937-1992)
    * ``00-00-AA`` (1992-2005)
    * ``00-AA-00`` (2005-2020)
    * ``AA-00-AA`` (2020 onwards)

    The format has no check digit, so the patterns are weak.
    Reference: Instituto da Mobilidade e dos Transportes (IMT),
    https://www.imt-ip.pt (Matrículas)

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param name: Name of the recognizer
    """

    COUNTRY_CODE = "pt"

    PATTERNS = [
        Pattern(
            "Plate AA-00-AA (weak)",
            r"(?<![\w-])[A-Z]{2}-\d{2}-[A-Z]{2}(?![\w-])",
            0.2,
        ),
        Pattern(
            "Plate 00-AA-00 (weak)",
            r"(?<![\w-])\d{2}-[A-Z]{2}-\d{2}(?![\w-])",
            0.2,
        ),
        Pattern(
            "Plate 00-00-AA (weak)",
            r"(?<![\w-])\d{2}-\d{2}-[A-Z]{2}(?![\w-])",
            0.2,
        ),
        Pattern(
            "Plate AA-00-00 (weak)",
            r"(?<![\w-])[A-Z]{2}-\d{2}-\d{2}(?![\w-])",
            0.2,
        ),
    ]

    CONTEXT = [
        "matrícula",
        "matricula",
        "viatura",
        "veículo",
        "veiculo",
        "plate",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "pt",
        supported_entity: str = "PT_VEHICLE_REGISTRATION",
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
