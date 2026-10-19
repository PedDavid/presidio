from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class PtStreetAddressRecognizer(PatternRecognizer):
    """
    Recognize Portuguese street addresses (morada).

    A Portuguese postal address is written as::

        <street type> <street name>, <door number>, <floor and door>,
        <postal code> <locality>

    for example ``Rua 25 de Abril, nº 39, 2º B, 1075-654 Lourinhã``. The
    door number, floor and locality are optional. The match spans from the
    street type through the last part found, so the door number, floor and
    locality are covered too.
    Reference: CTT - Correios de Portugal, Normas de endereçamento postal,
    https://www.ctt.pt/particulares/codigo-postal

    There is no check digit and street names are free text, so every pattern is
    weak and the score is only raised by the structure that was found
    (postal code > door number > bare number):

    * The street type (Rua, Avenida, Av., Travessa, Tv., Largo, Praça,
      Estrada, Alameda, Beco, Calçada, Urbanização) must be capitalised, or
      written in capitals. Lowercase ``rua``, ``largo`` or ``praça`` are
      ordinary words in prose and would match sentences like ``a rua é longa,
      3 vezes``. ``Quinta`` and ``Caminho`` are left out for the same reason
      (``Quinta, 14 de março``).
    * The locality must start with a capital letter, so a lowercase word
      following the postal code is not swallowed.

    All repetition is bounded, so the patterns do not backtrack catastrophically
    on long inputs.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param name: Name of the recognizer
    """

    COUNTRY_CODE = "pt"

    # Case-sensitive on purpose (the recognizer is IGNORECASE by default).
    _STREET_TYPE = (
        r"(?-i:(?:Rua|RUA|Avenida|AVENIDA|Av\.|AV\.|Travessa|TRAVESSA|Tv\.|TV\."
        r"|Largo|LARGO|Praça|PRAÇA|Estrada|ESTRADA|Alameda|ALAMEDA|Beco|BECO"
        r"|Calçada|CALÇADA|Urbanização|URBANIZAÇÃO)(?=\s))"
    )
    _WORD = r"[\wÀ-ÿ.'’-]+"
    _NAME = r"(?:" + _WORD + r"\s+){0,5}" + _WORD
    _NUMBER = r"(?:(?:n|lote)\s*(?:[º°ª.]|\.º|o\b)?\s*)?\d{1,4}[A-Za-z]?(?![\w-])"
    _FLOOR = (
        r"(?:r/c|rc|cave|\d{1,2}\s*(?:[º°ª]|\.º|o\b)?)"
        r"(?:\s*(?:andar|esq|esquerdo|dto|dir|direito|frente|fte|[A-Za-z]\b)\.?)?"
    )
    _SEP = r"\s*,\s*"
    _POSTAL = r"[1-9]\d{3}-\d{3}"
    _LOCALITY_WORD = r"(?-i:[A-ZÀ-Ý][\wÀ-ÿ'’-]*)"
    _LOCALITY = (
        _LOCALITY_WORD
        + r"(?:\s+(?:(?:de|da|do|das|dos|e)\s+)?"
        + _LOCALITY_WORD
        + r"){0,2}"
    )

    PATTERNS = [
        Pattern(
            "Street address with postal code (weak)",
            _STREET_TYPE
            + r"\s+"
            + _NAME
            + r"(?:"
            + _SEP
            + _NUMBER
            + r"(?:"
            + _SEP
            + _FLOOR
            + r"){0,2})?\s*,?\s*"
            + _POSTAL
            + r"(?:\s*,?\s*"
            + _LOCALITY
            + r")?",
            0.3,
        ),
        Pattern(
            "Street address with door number (weak)",
            _STREET_TYPE
            + r"\s+"
            + _NAME
            + _SEP
            + _NUMBER
            + r"(?:"
            + _SEP
            + _FLOOR
            + r"){0,2}",
            0.2,
        ),
        Pattern(
            "Street address, number without comma (very weak)",
            _STREET_TYPE + r"\s+(?:[a-zÀ-ÿ'’.-]+\s+){1,5}" + _NUMBER,
            0.1,
        ),
    ]

    CONTEXT = [
        "morada",
        "endereço",
        "endereco",
        "entrega",
        "residência",
        "residencia",
        "domicílio",
        "domicilio",
        "address",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "pt",
        supported_entity: str = "PT_STREET_ADDRESS",
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
