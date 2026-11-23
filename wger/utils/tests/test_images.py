# Standard Library
from io import BytesIO
from unittest.mock import MagicMock, patch

# Django
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

# Third Party
from PIL import Image

# wger
from wger.utils.images import validate_image_static_no_animation


class ImageValidatorTestCase(SimpleTestCase):
    def make_png(self):
        output = BytesIO()
        Image.new('RGB', (2, 2), 'red').save(output, format='PNG')
        return SimpleUploadedFile('image.png', output.getvalue(), content_type='image/png')

    def test_valid_png_is_accepted(self):
        validate_image_static_no_animation(self.make_png())

    def test_oversized_file_is_rejected(self):
        image = SimpleUploadedFile('large.png', b'x' * (20 * 1024 * 1024 + 1))

        with self.assertRaisesMessage(ValidationError, 'maximum image file size'):
            validate_image_static_no_animation(image)

    def test_invalid_image_is_rejected(self):
        image = SimpleUploadedFile('not-an-image.txt', b'not an image')

        with self.assertRaisesMessage(ValidationError, 'not a valid image'):
            validate_image_static_no_animation(image)

    @patch('wger.utils.images.Image.open')
    def test_unsupported_format_is_rejected(self, open_mock):
        image = self.make_png()
        open_mock.return_value = MagicMock(format='gif')

        with self.assertRaisesMessage(ValidationError, 'not supported'):
            validate_image_static_no_animation(image)

    @patch('wger.utils.images.Image.open')
    def test_animated_webp_is_rejected(self, open_mock):
        image = self.make_png()
        open_mock.return_value = MagicMock(format='webp', is_animated=True)

        with self.assertRaisesMessage(ValidationError, 'Animated images'):
            validate_image_static_no_animation(image)
