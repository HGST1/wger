# Django
from django.core.exceptions import ValidationError

# wger
from wger.core.models import Language
from wger.core.tests.base_testcase import WgerTestCase
from wger.utils.validators import (
    validate_iso_date,
    validate_language_code,
)


class ValidatorsTestCase(WgerTestCase):
    def test_existing_language_code_is_valid(self):
        language = Language.objects.first()

        validate_language_code(language.short_name)

    def test_unknown_language_code_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_language_code('xx')

    def test_iso_date_and_datetime_are_valid(self):
        validate_iso_date('2026-04-01')
        validate_iso_date('2026-04-01T12:30:00Z')

    def test_invalid_iso_date_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_iso_date('01/04/2026')
