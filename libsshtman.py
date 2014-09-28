import os, json, time

FIFO_PATH = '/tmp/sshtman_daemon_in'
CHECK_INTERVAL = 0.5

def command(fn):
    def decorator(*args, **kwargs):
        stripped_kwargs = _strip_empty_values(kwargs)
        stripped_args = [a for a in args if a is not None]
        return fn(*stripped_args, **stripped_kwargs)
    return decorator

def _strip_empty_values(d):
    return dict(((k, v) for k, v in d.items() if v is not None))


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


class Listener:

    def __init__(self, path, manager):
        self.path = path
        self.manager = manager
        self._commands = {
            'debug': self._debug,
            'die': self._die,
            'topen': self._topen,
            'tclose': self._tclose,
        }

    def listen(self):
        self._create_fifo()
        with open(self.path, 'r') as fifo:
            self._loop(fifo)
        os.unlink(self.path)

    def _loop(self, fifo):
        self._running = True
        while self._running:
            for line in fifo:
                self._exec_command(line)
            time.sleep(CHECK_INTERVAL)

    def _create_fifo(self):
        if os.path.exists(self.path):
            os.unlink(self.path)
        os.mkfifo(self.path)

    def _exec_command(self, cmd_text):
        cmd_spec = json.loads(cmd_text)
        cmd = self._commands[cmd_spec['name']]
        cmd(cmd_spec['args'])

    @command
    def _debug(self, args):
        print('Debug command called with')
        print(str(args))

    @command
    def _die(self):
        self._running = False

    @command
    def _topen(self, args):
        self.manager.open(args['name'], **args['kwargs'])

    @command
    def _tclose(self, args):
        self.manager.close(args['name'])



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
        self.remote_port = str(remote_port)
        self.local_port = str(local_port)
        self.ssh_port = str(ssh_port)

    def open(self):
        args = self._create_ssh_command()
        self._process = self._open_process(args)
        print('SSH tunnel opened')

    def _create_ssh_command(self):
        return ('ssh', '-N', '-L',
                self.local_port + ':127.0.0.1:' + self.remote_port,
                self.user + '@' + self.host)

    def _open_process(self, args):
        return subprocess.Popen(args, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

    def close(self):
        self._process.terminate()
        print('SSH tunnel closed')