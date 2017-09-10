import mock
import unittest

from helga_alias import find_alias, get_aliases, is_alias


class PluginTest(unittest.TestCase):

    def setUp(self):

        self.aliases_data = [{
            'recommended_nick': 'nick1',
            'aliases': ['nick1', 'nick2']
        }, {
            'recommended_nick': 'nick3',
            'aliases': ['nick3'],
        }]

    @mock.patch('helga_alias.get_aliases')
    def test_is_alias(self, mock_aliases):

        mock_aliases.return_value = ['nick1', 'nick2']

        self.assertTrue(is_alias('nick2'))
        self.assertFalse(is_alias('nick3'))

    @mock.patch('helga_alias.db')
    def test_get_aliases(self, mock_db):

        mock_db.alias.find.return_value = self.aliases_data

        nicks = get_aliases()

        self.assertEqual(len(nicks), 3)
        self.assertListEqual(
            nicks,
            ['nick1', 'nick2', 'nick3']
        )

    @mock.patch('helga_alias.db')
    def test_find_alias(self, mock_db):

        mock_db.alias.find.return_value = self.aliases_data

        nick, aliases = find_alias('nick2')

        self.assertEqual(nick, 'nick1')
        self.assertListEqual(aliases, ['nick1', 'nick2'])

    @mock.patch('helga_alias.db')
    def test_create_alias(self, mock_db):

        mock_db.alias.find.return_value = self.aliases_data

        nick, aliases = find_alias('newnick')

        self.assertEqual(nick, 'newnick')
        self.assertEqual(aliases, ['newnick'])

        mock_db.alias.insert.assert_called()


    @mock.patch('helga_alias.db')
    def test_dont_create_alias(self, mock_db):

        mock_db.alias.find.return_value = self.aliases_data

        nick, aliases = find_alias('newnick', create_new=False)

        self.assertEqual(nick, 'newnick')
        self.assertEqual(aliases, ['newnick'])

        mock_db.alias.insert.assert_not_called()
