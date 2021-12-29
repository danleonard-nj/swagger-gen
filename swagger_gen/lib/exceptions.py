class NullReferenceException(Exception):
    def __init__(self, parameter):
        self.message = parameter
