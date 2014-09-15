#! /usr/bin/env python3

import sys, subprocess, os, json, settings


class Listener:

    def __init__(self, path, manager):
        self.path = path
        self.manager = manager
        self._commands = {
            'debug': lambda args: self._debug(args),
            'die': lambda args: self.die(),
        }
       
    def die(self):
        # TODO: shutdown gracefully
        sys.exit(0)
    
    def listen(self):
        self._create_fifo()
        with open(self.path, 'r') as fifo:
            self._loop(fifo)
        os.unlink(self.path)
           
    def _loop(self, fifo):
        while True:
            for line in fifo:
                self._exec_command(line)
                    
    def _create_fifo(self):
        sshtman_home = os.path.expanduser(settings.SSHTMAN_HOME)
        if not os.path.exists(sshtman_home):
            os.makedirs(sshtman_home)
        if os.path.exists(self.path):
            os.unlink(self.path)
        os.mkfifo(self.path)
        
    def _exec_command(self, cmd_text):
        cmd_spec = json.loads(cmd_text)
        cmd = self._commands[cmd_spec['name']]
        cmd(cmd_spec['args'])
        
    def _debug(self, args):
        print('Debug command called with')
        print(str(args))


class TunnelManager:
    
    def __init__(self):
        self._tunnels = {}

    def open(self, name, **targs):
        t = Tunnel(**targs)
        t.open()
        self._tunnels[name] = t
        
    def close(self, name):
        self._tunnels[name].close()


class Tunnel:

    def __init__(self, user=None, host=None, remote_port=None, local_port=None,
                 ssh_port=22):
        self.user = user
        self.host = host
        self.remote_port = remote_port
        self.local_port = local_port
        self.ssh_port = str(ssh_port)
    
    def open(self):
        args = ('ssh', self.user + '@' + self.host)
        self._process = subprocess.Popen(args, stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT)
        print('SSH tunnel opened, server said: ' +
              str(self._process.communicate()))

    def close(self):
        self._process.terminate()
        print('Process completed with code ' + str(self._process.returncode))


if __name__ == '__main__':
    l = Listener(os.path.expanduser(settings.FIFO_PATH), None)
    l.listen()
