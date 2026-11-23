# Standard Library
from unittest.mock import patch

# Django
from django.test import SimpleTestCase

# wger
from wger.utils.requests import (
    get_all_paginated,
    get_paginated,
    wger_headers,
    wger_user_agent,
)


class RequestsUtilsTestCase(SimpleTestCase):
    @patch('wger.utils.requests.requests.get')
    def test_get_all_paginated_follows_next_links(self, get_mock):
        get_mock.side_effect = [
            MockResponse({'results': [1, 2], 'next': 'https://example.com/page-2'}),
            MockResponse({'results': [3], 'next': None}),
        ]

        results = get_all_paginated('https://example.com/page-1')

        self.assertEqual(results, [1, 2, 3])
        self.assertEqual(get_mock.call_count, 2)
        get_mock.assert_any_call('https://example.com/page-1', headers={})
        get_mock.assert_any_call('https://example.com/page-2', headers={})

    @patch('wger.utils.requests.requests.get')
    def test_get_paginated_yields_results_and_passes_headers(self, get_mock):
        get_mock.side_effect = [
            MockResponse({'results': ['a'], 'next': 'page-2'}),
            MockResponse({'results': ['b'], 'next': None}),
        ]
        headers = {'Authorization': 'Bearer token'}

        self.assertEqual(
            list(get_paginated('page-1', headers=headers)),
            ['a', 'b'],
        )
        get_mock.assert_any_call('page-1', headers=headers)
        get_mock.assert_any_call('page-2', headers=headers)

    def test_wger_headers_contains_user_agent(self):
        self.assertEqual(wger_headers(), {'User-Agent': wger_user_agent()})
        self.assertTrue(wger_user_agent().startswith('wger/'))


class MockResponse:
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data
