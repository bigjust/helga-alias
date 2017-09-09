import mock
import unittest

from helga_alias import is_alias


class PluginTest(unittest.TestCase):

    def setUp(self):
        pass

    @mock.patch('helga_alias.get_aliases')
    def test_is_alias(self, mock_aliases):

        mock_aliases.return_value = ['nick1', 'nick2']

        self.assertTrue(is_alias('nick2'))
        self.assertFalse(is_alias('nick3'))
