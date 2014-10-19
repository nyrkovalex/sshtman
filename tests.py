import unittest
from unittest.mock import MagicMock, Mock, patch
from libsshtman import *


class ListenerTest(unittest.TestCase):

    def setUp(self):
        self.cmd = Mock()
        commands = {'test': self.cmd}
        self.listener = Listener(commands)

    def test_should_call_target_command(self):
        self.listener.listen([{'name': 'test'}])
        self.assertTrue(self.cmd.called)

    def test_should_pass_arguments_to_command(self):
        self.listener.listen([{'name': 'test', 'args': 'foo'}])
        self.cmd.assert_called_with('foo')


@patch('libsshtman.create_tunnel')
class TunnelManagerTest(unittest.TestCase):

    def setUp(self):
        self.tunnel = Mock()
        self.logger = Mock()
        self.manager = TunnelManager(self.logger)

    def test_should_create_new_tunnel(self, create_tunnel):
        self.manager.open('test')
        self.assertTrue(create_tunnel.called)

    def test_should_add_tunnel_to_inner_dict(self, create_tunnel):
        create_tunnel.return_value = self.tunnel
        self.manager.open('test')
        self.assertTrue(self.tunnel in self.manager._tunnels.values())

    def test_should_not_fall_on_any_error(self, create_tunnel):
        create_tunnel.side_effect = Exception()
        self.manager.open('test')

    def test_should_log_error_on_tunnel_creation_failure(self, create_tunnel):
        create_tunnel.side_effect = ValueError()
        self.manager.open('test')
        self.logger.exception.assert_called()

    def test_should_log_warning_closing_nonexisting_tunnel(self, create_tunnel):
        self.manager.open('test')
        self.manager.close('foo')
        self.logger.warning.assert_called()

    def test_should_close_all_tunnels(self, create_tunnel):
        self.manager._tunnels = {
            'first': None,
            'second': None,
        }
        self.manager.close = Mock()
        self.manager.close_all()
        self.manager.close.assert_any_call('first')
        self.manager.close.assert_any_call('second')


class TunnelTest(unittest.TestCase):

    def test_should_raise_error_if_no_user_provided(self):
        self.assertRaises(ValueError, create_tunnel,
            host='test',
            remote_port=23,
            local_port=23
        )

    def test_should_raise_error_if_no_host_provided(self):
        self.assertRaises(ValueError, create_tunnel,
            user='test',
            remote_port=23,
            local_port=23
        )

    def test_should_raise_error_if_no_remote_port_provided(self):
        self.assertRaises(ValueError, create_tunnel,
            user='test',
            host='test',
            local_port=23
        )

    def test_should_raise_error_if_no_local_port_provided(self):
        self.assertRaises(ValueError, create_tunnel,
            user='test',
            host='test',
            remote_port=23
        )

