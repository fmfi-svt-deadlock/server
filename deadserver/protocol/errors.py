class BadMessageError(Exception): pass


class StatusError(Exception):
    def __init__(self, soft):
        self.soft = soft

class TryAgain(StatusError):
    def __init__(self):
        super().__init__(soft=True)

class HardError(Exception):
    def __init__(self):
        super().__init__(soft=False)
