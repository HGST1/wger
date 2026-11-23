# Standard Library
from unittest.mock import patch

# Django
from django.core.mail import EmailMultiAlternatives
from django.test import SimpleTestCase, override_settings

# wger
from wger.utils.mail import (
    get_delivery_connection,
    message_from_dict,
    message_to_dict,
)


class MailUtilsTestCase(SimpleTestCase):
    def test_message_round_trip(self):
        message = EmailMultiAlternatives(
            subject='Subject',
            body='Plain text',
            from_email='sender@example.com',
            to=['user@example.com'],
            cc=['copy@example.com'],
            bcc=['blind-copy@example.com'],
            reply_to=['reply@example.com'],
            headers={'X-Test': 'yes'},
        )
        message.attach_alternative('<p>HTML</p>', 'text/html')

        restored = message_from_dict(message_to_dict(message))

        self.assertEqual(restored.subject, message.subject)
        self.assertEqual(restored.body, message.body)
        self.assertEqual(restored.to, message.to)
        self.assertEqual(restored.cc, message.cc)
        self.assertEqual(restored.bcc, message.bcc)
        self.assertEqual(restored.reply_to, message.reply_to)
        self.assertEqual(restored.extra_headers, message.extra_headers)
        self.assertEqual(list(restored.alternatives), list(message.alternatives))

    def test_messages_with_attachments_are_not_serialized(self):
        message = EmailMultiAlternatives(
            subject='Subject',
            body='Body',
            to=['user@example.com'],
        )
        message.attach('test.txt', 'content', 'text/plain')

        self.assertIsNone(message_to_dict(message))

    @override_settings(EMAIL_DELIVERY_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_delivery_connection_uses_configured_backend(self):
        with patch('wger.utils.mail.get_connection') as get_connection_mock:
            get_delivery_connection(fail_silently=True)

        get_connection_mock.assert_called_once_with(
            backend='django.core.mail.backends.locmem.EmailBackend',
            fail_silently=True,
        )
