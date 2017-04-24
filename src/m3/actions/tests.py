# coding: utf-8
import mock
from django.test import TestCase
from m3.actions import Action


class ActionTestCase(TestCase):

    def test_action_run_signature(self):
        with self.assertRaises(NotImplementedError):
            Action().run(request='request', context='context')

    def test_action_context_declaration_signature(self):
        # call context declaration method to be sure signature has not changed
        Action().context_declaration()

    @mock.patch('m3.actions.Action.get_short_name')
    def test_get_verbose_name(self, mock_short_name_method):
        # setting up the get_short_name mock method
        mock_short_name_method.return_value = 'some short name'

        # check the get_short_name() call
        self.assertEqual(Action.get_verbose_name(), 'some short name')
        # setting up value for verbose_name attr
        Action.verbose_name = 'some verb name'
        self.assertEqual(Action.get_verbose_name(), 'some verb name')

    @mock.patch('m3.actions._name_of')
    def test_get_short_name(self, mock_name_of):
        # setting up the inner method mock
        mock_name_of.return_value = 'some name'
        # testing inner method call
        self.assertEqual(Action.get_short_name(), 'some name')
