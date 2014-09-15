#! /usr/bin/env python3

import os, json, settings


class Client:
    def __init__(self, path):
        self.path = path
        
    def open_tunnel(self, name, **kwargs):
        command = {
            'name': 'open',
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
    
    def kill_daemon(self):
        self.send({
            'name': 'die',
            'args': {},
        })

    def send(self, cmd):
        with open(self.path, 'w') as fifo:
            cmd_text = json.dumps(cmd)
            print('Sending ' + cmd_text)
            fifo.write(cmd_text + '\n')
            

if __name__ == '__main__':
    c = Client(os.path.expanduser(settings.FIFO_PATH))
    #c.open_tunnel('test tunnel', user='Dude')
    c.debug()
    c.kill_daemon()
