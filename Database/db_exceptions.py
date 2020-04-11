class InvalidDBError(Exception):
    def __init__(self, message='Invalid DB'):
        self.message = message

    def __str__(self):
        return repr(self.message)