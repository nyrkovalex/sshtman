import json, time, subprocess, os, logging

FIFO_PATH = '/tmp/sshtman_daemon_in'
CHECK_INTERVAL = 0.5

def command(function):
    def decorator(*args, **kwargs):
        stripped_kwargs = _strip_empty_values(kwargs)
        stripped_args = [a for a in args if a is not None]
        return function(*stripped_args, **stripped_kwargs)
    return decorator

def value_or_error(value, message=None):
    if value is None:
        raise ValueError(message)
    return value

def _strip_empty_values(dictionary):
    return dict(((k, v) for k, v in dictionary.items() if v is not None))

def _create_fifo(path):
    if os.path.exists(path):
        os.unlink(path)
    os.mkfifo(path)

def create_tunnel(**kwargs):
    return Tunnel(**kwargs)


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
        self.send({
            'name': 'topen',
            'args': {
                'name': name,
                'kwargs': kwargs,
            },
        })

    @command
    def debug(self):
        self.send({
            'name': 'debug',
            'args': {'debug': True},
        })

    @command
    def kill_daemon(self):
        self.send({
            'name': 'die',
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


class Daemon:

    def __init__(self):
        self._manager = TunnelManager(logging)
        commands = {
            'debug': self.debug,
            'die': self.die,
            'topen': self.topen,
            'tclose': self.tclose,
        }
        self._listener = Listener(commands)
        self._pipe = None

    def run(self):
        _create_fifo(FIFO_PATH)
        with open(FIFO_PATH, 'r') as fifo:
            self._pipe = Pipe(fifo)
            self._listener.listen(self._pipe)
        os.unlink(FIFO_PATH)

    @command
    def debug(self, args):
        print('Debug command called with\n' + str(args))

    @command
    def die(self):
        self._manager.close_all()
        self._pipe.close()

    @command
    def topen(self, args):
        self._manager.open(args['name'], **args['kwargs'])

    @command
    def tclose(self, args):
        self._manager.close(args['name'])


class Pipe:

    def __init__(self, pipe_file):
        self._pipe_file = pipe_file
        self._running = True

    def __iter__(self):
        return self

    def close(self):
        self._running = False

    def __next__(self):
        while self._running:
            line = self._pipe_file.readline()
            if line:
                return json.loads(line)
            time.sleep(CHECK_INTERVAL)
        raise StopIteration

class Listener:

    def __init__(self, commands):
        self._commands = commands

    def listen(self, pipe):
        for cmd_spec in pipe:
            self._exec_command(cmd_spec)

    def _exec_command(self, cmd_spec):
        cmd = self._commands[cmd_spec['name']]
        if 'args' in cmd_spec:
            cmd(cmd_spec['args'])
        else:
            cmd()


class TunnelManager:

    def __init__(self, logger):
        self._tunnels = {}
        self._logger = logger

    def open(self, name, **targs):
        try:
            tunnel = create_tunnel(**targs)
            tunnel.open()
            self._tunnels[name] = tunnel
            self._logger.debug('Tunnel %s opened' % name)
        except:
            self._logger.exception('Failed to create tunnel')

    def close(self, name):
        if name not in self._tunnels:
            self._logger.warning('Trying to close nonexisting tunnel ' + name)
            return
        self._tunnels[name].close()
        self._logger.debug('Tunnel %s close' % name)

    def close_all(self):
        for name in self._tunnels:
            self.close(name)


class Tunnel:

    def __init__(self, user=None, host=None, remote_port=None, local_port=None,
                 ssh_port=22):
        self.user = value_or_error(user, 'No user provided')
        self.host = value_or_error(host, 'No host provided')
        self.remote_port = str(value_or_error(remote_port,
                                              'No remote_port provided'))
        self.local_port = str(value_or_error(local_port,
                                             'No local_port provided'))
        self.ssh_port = str(ssh_port)
        self._process = None

    def open(self):
        args = self._create_ssh_command()
        self._process = self._open_process(args)

    def close(self):
        self._process.terminate()

    def _create_ssh_command(self):
        return ('ssh',
                # Ignore fingerprnt check
                '-o', 'StrictHostKeyChecking=no',
                # Suppress unknow host output
                '-o', 'UserKnownHostsFile=/dev/null',
                '-N', '-L',
                self.local_port + ':127.0.0.1:' + self.remote_port,
                self.user + '@' + self.host)

    def _open_process(self, args):
        return subprocess.Popen(args, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
