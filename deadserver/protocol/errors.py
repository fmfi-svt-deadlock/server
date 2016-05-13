class BadMessageError(Exception): pass


class StatusError(Exception):
    def __init__(self, msg, soft):
        super().__init__(msg)
        self.message = msg
        self.soft = soft

class TransientError(StatusError):
    def __init__(self, msg):
        super().__init__(msg, soft=True)

class HardError(StatusError):
    def __init__(self, msg):
        super().__init__(msg, soft=False)
