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
