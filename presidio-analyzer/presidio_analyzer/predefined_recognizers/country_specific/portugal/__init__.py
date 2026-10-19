"""Portugal-specific recognizers package."""

from .pt_citizen_card_recognizer import PtCitizenCardRecognizer
from .pt_nif_recognizer import PtNifRecognizer
from .pt_niss_recognizer import PtNissRecognizer
from .pt_passport_recognizer import PtPassportRecognizer
from .pt_phone_number_recognizer import PtPhoneNumberRecognizer
from .pt_postal_code_recognizer import PtPostalCodeRecognizer
from .pt_sns_number_recognizer import PtSnsNumberRecognizer
from .pt_street_address_recognizer import PtStreetAddressRecognizer
from .pt_vehicle_registration_recognizer import PtVehicleRegistrationRecognizer

__all__ = [
    "PtCitizenCardRecognizer",
    "PtNifRecognizer",
    "PtNissRecognizer",
    "PtPassportRecognizer",
    "PtPhoneNumberRecognizer",
    "PtPostalCodeRecognizer",
    "PtSnsNumberRecognizer",
    "PtStreetAddressRecognizer",
    "PtVehicleRegistrationRecognizer",
]
