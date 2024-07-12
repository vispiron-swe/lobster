import unittest
from unittest.mock import Mock, patch

from lobster.tools.codebeamer.codebeamer import get_single_item, get_many_items, to_lobster, \
    import_tagged
from lobster.errors import Message_Handler


class QueryCodebeamerTest(unittest.TestCase):

    @patch('lobster.tools.codebeamer.codebeamer.query_cb_single')
    def test_get_single_item(self, mock_get):
        _item_id = 11693324
        _cb_config = {'base': 'https://test.com'}
        _moch_response = Mock()
        _expected_test_result = {
            'page': 1,
            'pageSize': 100,
            'total': 1,
            'items': [{'item': {'id': 11693324, 'name': 'ShutOffPathTest - SOPT'}}]
        }
        _moch_response.return_value = _expected_test_result

        mock_get.return_value = _moch_response

        query_result = get_single_item(_cb_config, _item_id)
        self.assertEqual(query_result, _moch_response)

    @patch('lobster.tools.codebeamer.codebeamer.query_cb_single')
    def test_get_many_items(self, mock_get):
        _item_ids = {24406947, 21747817}
        _cb_config = {'base': 'https://test.com', 'page_size': 100}
        _response_itemas = [
                {'id': 24406947, 'name': 'Systempresssure degradation'},
                {'id': 21747817, 'name': 'DsABrk = 15 - AutoP and automatic braking OFF'}
            ]
        _moch_response = {
            'page': 1,
            'pageSize': 100,
            'total': 2,
            'items': _response_itemas
        }

        mock_get.return_value = _moch_response

        query_result = get_many_items(_cb_config, _item_ids)
        self.assertEqual(query_result, _response_itemas)

if __name__ == '__main__':
    unittest.main()
