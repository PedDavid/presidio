"""Tests for the Portugal-specific recognizers."""

from pathlib import Path

import pytest
import spacy
import yaml

import presidio_analyzer
from presidio_analyzer import AnalyzerEngine, EntityRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts
from presidio_analyzer.predefined_recognizers import (
    PtCitizenCardRecognizer,
    PtNifRecognizer,
    PtNissRecognizer,
    PtPassportRecognizer,
    PtPhoneNumberRecognizer,
    PtPostalCodeRecognizer,
    PtSnsNumberRecognizer,
    PtVehicleRegistrationRecognizer,
)
from presidio_analyzer.recognizer_registry import RecognizerRegistryProvider
from tests.mocks import NlpEngineMock

MAX_SCORE = EntityRecognizer.MAX_SCORE


class _PtNlpEngineMock(NlpEngineMock):
    """Tokenizes with a blank Portuguese pipeline; lemmas are lowercased tokens."""

    def __init__(self):
        super().__init__()
        self._nlp = spacy.blank("pt")

    def process_text(self, text, language):
        doc = self._nlp(text)
        return NlpArtifacts(
            entities=[],
            tokens=doc,
            tokens_indices=[token.idx for token in doc],
            lemmas=[token.text.lower() for token in doc],
            nlp_engine=self,
            language="pt",
            scores=[],
        )


def _nif_check_digit(first_eight: str) -> str:
    total = sum((9 - i) * int(d) for i, d in enumerate(first_eight))
    return str((11 - total) % 11 % 10)


def _niss_check_digit(first_ten: str) -> str:
    weights = (29, 23, 19, 17, 13, 11, 7, 5, 3, 2)
    return str(9 - sum(w * int(d) for w, d in zip(weights, first_ten)) % 10)


def _assert_single(results, entity, start, end, score):
    assert len(results) == 1, results
    result = results[0]
    assert result.entity_type == entity
    assert (result.start, result.end) == (start, end)
    assert result.score == pytest.approx(score)


NIF_VALID = "501964843"


@pytest.mark.parametrize(
    "text, start, end",
    [
        (NIF_VALID, 0, 9),
        ("501 964 843", 0, 11),
        ("PT501964843", 0, 11),
        ("PT 501 964 843", 0, 14),
        ("O NIF 501964843, obrigado", 6, 15),
        ("O NIF é 501964843.", 8, 17),
        ("NIF 501964843 2023", 4, 13),
        # non-resident individual (prefix 45) and special entity (prefix 70)
        ("45123456" + _nif_check_digit("45123456"), 0, 9),
        ("70123456" + _nif_check_digit("70123456"), 0, 9),
    ],
)
def test_when_valid_nif_then_detected_with_max_score(text, start, end):
    results = PtNifRecognizer().analyze(text, ["PT_NIF"])
    _assert_single(results, "PT_NIF", start, end, MAX_SCORE)


@pytest.mark.parametrize(
    "text",
    [
        "501964842",  # wrong check digit
        "PT501964842",
        "NIF: 501964842",
        "50196484",  # 8 digits
        "5019648431",  # 10 digits
        "12345678901",  # 11 digits, a lookalike NISS
        "41234567" + _nif_check_digit("41234567"),  # invalid prefix 41
        "01234567" + _nif_check_digit("01234567"),  # prefix 0
        "2024-01-15",
        "501.964.8431",
    ],
)
def test_when_invalid_nif_then_not_detected(text):
    assert PtNifRecognizer().analyze(text, ["PT_NIF"]) == []


CC_VALID = "12345678 9 ZZ1"


@pytest.mark.parametrize(
    "text, start, end",
    [
        (CC_VALID, 0, 14),
        ("123456789ZZ1", 0, 12),
        ("000000000ZZ4", 0, 12),
        ("CC nº 12345678 9 ZZ1.", 6, 20),
        ("12345678-9-ZZ1", 0, 14),
    ],
)
def test_when_valid_citizen_card_then_detected_with_max_score(text, start, end):
    results = PtCitizenCardRecognizer().analyze(text, ["PT_CITIZEN_CARD"])
    _assert_single(results, "PT_CITIZEN_CARD", start, end, MAX_SCORE)


@pytest.mark.parametrize(
    "text",
    [
        "12345678 9 ZZ4",  # wrong check digit
        "123456789ZZ",  # missing check digit
        "1234567890123",  # 13 digits
        "12345678 9 ZZ12",  # too long
        "ORDER-123456789ZZ1X",
    ],
)
def test_when_invalid_citizen_card_then_not_detected(text):
    assert PtCitizenCardRecognizer().analyze(text, ["PT_CITIZEN_CARD"]) == []


NISS_VALID = "21206104409"


@pytest.mark.parametrize(
    "text, start, end",
    [
        (NISS_VALID, 0, 11),
        ("212 0610 4409", 0, 13),
        ("1234567890" + _niss_check_digit("1234567890"), 0, 11),
        ("NISS 21206104409.", 5, 16),
    ],
)
def test_when_valid_niss_then_detected_with_max_score(text, start, end):
    results = PtNissRecognizer().analyze(text, ["PT_NISS"])
    _assert_single(results, "PT_NISS", start, end, MAX_SCORE)


def test_when_niss_checksum_fails_then_keeps_pattern_score():
    # The NISS algorithm is not from an official specification, so a failing
    # checksum must not discard the match.
    results = PtNissRecognizer().analyze("21206104400", ["PT_NISS"])
    _assert_single(results, "PT_NISS", 0, 11, 0.1)


@pytest.mark.parametrize("text", ["31206104409", "2120610440", "212061044091"])
def test_when_not_niss_shaped_then_not_detected(text):
    assert PtNissRecognizer().analyze(text, ["PT_NISS"]) == []


_PHONE = (PtPhoneNumberRecognizer, "PT_PHONE_NUMBER")
_VEHICLE = (PtVehicleRegistrationRecognizer, "PT_VEHICLE_REGISTRATION")


@pytest.mark.parametrize(
    "recognizer_cls, entity, text, start, end, score",
    [
        (PtPassportRecognizer, "PT_PASSPORT", "N123456", 0, 7, 0.05),
        (PtPassportRecognizer, "PT_PASSPORT", "Passaporte: N123456.", 12, 19, 0.05),
        (*_PHONE, "+351 912 345 678", 0, 16, 0.4),
        (*_PHONE, "00351912345678", 0, 14, 0.4),
        (*_PHONE, "+351 213 456 789", 0, 16, 0.4),
        (*_PHONE, "912 345 678", 0, 11, 0.2),
        (*_PHONE, "912345678", 0, 9, 0.05),
        (PtPostalCodeRecognizer, "PT_POSTAL_CODE", "1100-053", 0, 8, 0.1),
        (PtPostalCodeRecognizer, "PT_POSTAL_CODE", "4000-001 Porto", 0, 8, 0.1),
        (PtSnsNumberRecognizer, "PT_SNS_NUMBER", "123456789", 0, 9, 0.05),
        (*_VEHICLE, "AB-12-CD", 0, 8, 0.2),
        (*_VEHICLE, "12-AB-34", 0, 8, 0.2),
        (*_VEHICLE, "12-34-AB", 0, 8, 0.2),
        (*_VEHICLE, "AB-12-34", 0, 8, 0.2),
        (*_VEHICLE, "A matrícula é 12-AB-34!", 14, 22, 0.2),
    ],
)
def test_when_pattern_only_entity_then_detected_with_pattern_score(
    recognizer_cls, entity, text, start, end, score
):
    results = recognizer_cls().analyze(text, [entity])
    _assert_single(results, entity, start, end, score)


@pytest.mark.parametrize(
    "recognizer_cls, entity, text",
    [
        (PtPassportRecognizer, "PT_PASSPORT", "N1234567"),
        (PtPassportRecognizer, "PT_PASSPORT", "sha256"),
        (PtPassportRecognizer, "PT_PASSPORT", "covid19"),
        (*_PHONE, "812345678"),
        (*_PHONE, "+351 812 345 678"),
        (*_PHONE, "9123456789"),
        (PtPostalCodeRecognizer, "PT_POSTAL_CODE", "11000-053"),
        (PtPostalCodeRecognizer, "PT_POSTAL_CODE", "0100-053"),
        (PtPostalCodeRecognizer, "PT_POSTAL_CODE", "2024-01-15"),
        (PtSnsNumberRecognizer, "PT_SNS_NUMBER", "1234567890"),
        (*_VEHICLE, "AB-12-C"),
        (*_VEHICLE, "AB-12-CD-34"),
        (*_VEHICLE, "12-34-56"),
    ],
)
def test_when_lookalike_then_not_detected(recognizer_cls, entity, text):
    assert recognizer_cls().analyze(text, [entity]) == []


ALL_RECOGNIZERS = [
    PtNifRecognizer,
    PtCitizenCardRecognizer,
    PtNissRecognizer,
    PtPassportRecognizer,
    PtPhoneNumberRecognizer,
    PtPostalCodeRecognizer,
    PtSnsNumberRecognizer,
    PtVehicleRegistrationRecognizer,
]


@pytest.mark.parametrize("recognizer_cls", ALL_RECOGNIZERS)
def test_defaults_and_loader_kwargs(recognizer_cls):
    assert recognizer_cls().supported_language == "pt"
    assert recognizer_cls.COUNTRY_CODE == "pt"
    assert recognizer_cls(name="Custom").name == "Custom"


@pytest.mark.parametrize("recognizer_cls", ALL_RECOGNIZERS)
def test_adversarial_long_input_completes(recognizer_cls):
    recognizer = recognizer_cls()
    text = ("1 " * 20000) + ("AB-12-" * 5000) + ("9" * 50000)
    recognizer.analyze(text, recognizer.supported_entities)


CONFIG_CASES = [
    ("PtNifRecognizer", "PT_NIF", f"NIF: {NIF_VALID}", 1.0),
    (
        "PtCitizenCardRecognizer",
        "PT_CITIZEN_CARD",
        f"Cartão de cidadão {CC_VALID}",
        1.0,
    ),
    ("PtNissRecognizer", "PT_NISS", f"NISS {NISS_VALID}", 1.0),
    ("PtPassportRecognizer", "PT_PASSPORT", "Passaporte N123456", 0.4),
    ("PtPhoneNumberRecognizer", "PT_PHONE_NUMBER", "Telefone +351 912 345 678", 0.75),
    ("PtPostalCodeRecognizer", "PT_POSTAL_CODE", "Código postal 1100-053", 0.45),
    ("PtSnsNumberRecognizer", "PT_SNS_NUMBER", "Utente 123456789", 0.4),
    (
        "PtVehicleRegistrationRecognizer",
        "PT_VEHICLE_REGISTRATION",
        "Matrícula 12-AB-34",
        0.55,
    ),
]


@pytest.mark.parametrize("name, entity, text, score", CONFIG_CASES)
def test_recognizer_loads_and_detects_when_enabled_in_yaml(
    tmp_path, name, entity, text, score
):
    """Detection must work through the path users actually configure.

    The top-level ``supported_languages`` must include ``pt``: it defaults to
    ``["en"]`` and silently filters out Portuguese recognizers otherwise.
    """
    conf = tmp_path / "recognizers.yaml"
    conf.write_text(
        f"""
supported_languages:
  - pt
recognizers:
  - name: {name}
    supported_languages:
      - pt
    type: predefined
    enabled: true
    country_code: pt
"""
    )
    registry = RecognizerRegistryProvider(conf_file=conf).create_recognizer_registry()
    analyzer = AnalyzerEngine(
        registry=registry,
        nlp_engine=_PtNlpEngineMock(),
        supported_languages=["pt"],
    )

    results = analyzer.analyze(text, language="pt", entities=[entity])

    assert [result.entity_type for result in results] == [entity]
    assert results[0].score == pytest.approx(score)


def test_default_yaml_ships_all_portugal_recognizers_disabled():
    conf = Path(presidio_analyzer.__file__).parent / "conf" / "default_recognizers.yaml"
    entries = [
        r
        for r in yaml.safe_load(conf.read_text(encoding="utf-8"))["recognizers"]
        if r.get("country_code") == "pt"
    ]
    assert len(entries) == len(ALL_RECOGNIZERS)
    assert all(entry["enabled"] is False for entry in entries)
    assert all(entry["supported_languages"] == ["pt"] for entry in entries)
