#! /usr/bin/env python3

import json, argparse, settings


def parse_args():
    parser = argparse.ArgumentParser(description='SSH tunnel manager client')
    parser.add_argument('action', choices=('open', 'close', 'kill'), help='open or close tunnel with a give name or kill dameon')
    parser.add_argument('tunnel_name', nargs='?', help='name of a target tunnel', default=None)
    parser.add_argument('-l', '--local-port', type=int, help='number of a local port to open tunnel to')
    parser.add_argument('-r', '--remote-port', type=int, help='number of a remote port to open tunnel from')
    parser.add_argument('-u', '--user', help='remote host username')
    parser.add_argument('-n', '--host', help='remote host')
    parser.add_argument('-s', '--ssh-port', help='remote ssh port', type=int, default=22)
    return vars(parser.parse_args())


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

    def open_tunnel(self, name, **kwargs):
        command = {
            'name': 'topen',
            'args': {
                'name': name,
                'kwargs': kwargs,
            },
        }
        self.send(command)

    def debug(self):
        self.send({
            'name': 'debug',
            'args': { 'debug': True },
        })

    def kill_daemon(self, name, **kwargs):
        self.send({
            'name': 'die',
            'args': {},
        })

    def close_tunnel(self, name, **kwargs):
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
    args = parse_args()
    action = args.pop('action')
    tunnel_name = args.pop('tunnel_name')
    
    c = Client(settings.FIFO_PATH)
    c.perform_action(action, tunnel_name, **args)

