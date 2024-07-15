import unittest
from unittest.mock import Mock, patch

from lobster.tools.codebeamer.codebeamer import get_single_item, get_many_items, to_lobster, \
    import_tagged
from lobster.errors import Message_Handler

list_of_compared_attributes = ['name', 'kind', 'status', 'just_down', 'just_up', 'just_global']


class QueryCodebeamerTest(unittest.TestCase):

    def assertListEqualByAttributes(self, list1, list2):
        self.assertEqual(len(list1), len(list2), "Lists length are not the same")
        for obj1, obj2 in zip(list1, list2):
            for attr in list_of_compared_attributes:
                self.assertEqual(getattr(obj1, attr), getattr(obj2, attr), f"{obj1} is not like {obj2} in {attr}")

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

    @patch('lobster.tools.codebeamer.codebeamer.query_cb_single')
    def test_import_tagged(self, mock_get):
        _mh = Message_Handler()
        _item_ids = {24406947, 21747817}
        _cb_config = {'root': 'https://test.com/', 'base': 'https://test.com/base', 'page_size': 100}
        _response_itemas = [
            {
                'id': 24406947,
                'name': 'Systempresssure degradation',
                'typeName': 'Requirement',
                'version': 7,
                'status': {'name': 'Content Review'},
                'tracker': {'id': 29782591}
            },
            {
                'id': 21747817,
                'name': 'DsABrk = 15 - AutoP and automatic braking OFF',
                'typeName': 'Requirement',
                'version': 10,
                'status': {'name': 'Content Review'},
                'tracker': {'id': 29782591}
            }
        ]
        _mock_response = {
            'page': 1,
            'pageSize': 100,
            'total': 2,
            'items': _response_itemas
        }
        mock_get.return_value = _mock_response

        _expected_result = [to_lobster(_cb_config, items) for items in _response_itemas]

        import_tagged_result = import_tagged(_mh, _cb_config, _item_ids)

        self.assertListEqualByAttributes(import_tagged_result, _expected_result)


if __name__ == '__main__':
    unittest.main()
