#! /usr/bin/env python3

import json, argparse, shared
from shared import command 

def parse_args():
    parser = argparse.ArgumentParser(description='SSH tunnel manager client')
    parser.add_argument('action', choices=('open', 'close', 'kill'), 
        help='open or close tunnel with a give name or kill dameon')
    parser.add_argument('tunnel_name', nargs='?', 
        help='name of a target tunnel', default=None)
    parser.add_argument('-l', '--local-port', type=int, 
        help='number of a local port to open tunnel to')
    parser.add_argument('-r', '--remote-port', type=int,
        help='number of a remote port to open tunnel from')
    parser.add_argument('-u', '--user', help='remote host username')
    parser.add_argument('-n', '--host', help='remote host')
    parser.add_argument('-s', '--ssh-port', help='remote ssh port', type=int)
    return parser.parse_args()


class Client:

    def __init__(self, path):
        self.path = path
        self._actions = {
            'kill': self.kill_daemon,
            'open': self.open_tunnel,
            'close': self.close_tunnel,
        }

    def perform_action(self, action, name, **kwargs):
        self._actions[action](name, **kwargs)
        
    @command
    def open_tunnel(self, name, **kwargs):
        command = {
            'name': 'topen',
            'args': {
                'name': name,
                'kwargs': kwargs,
            },
        }
        self.send(command)

    @command
    def debug(self):
        self.send({
            'name': 'debug',
            'args': { 'debug': True },
        })

    @command
    def kill_daemon(self):
        self.send({
            'name': 'die',
            'args': None,
        })

    @command
    def close_tunnel(self, name):
        self.send({
            'name': 'tclose',
            'args': {
                'name': name,
            },
        })

    def send(self, cmd):
        with open(self.path, 'w') as fifo:
            cmd_text = json.dumps(cmd)
            print('Sending ' + cmd_text)
            fifo.write(cmd_text + '\n')


if __name__ == '__main__':
    kwargs = vars(parse_args())
    action = kwargs.pop('action')
    tunnel_name = kwargs.pop('tunnel_name')

    c = Client(shared.FIFO_PATH)
    c.perform_action(action, tunnel_name, **kwargs)

