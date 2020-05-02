### Define Python custom exceptions ###

class customError(Exception):
    """
    Base class of custom exceptions
    """
    pass

class PathNotFoundError(customError):
    """
    Custom Excepttion: Path does not exist
    """
    def __init__(self, arg):
        self.message = "[ERROR] Path does not exist: '{}'".format(arg)

class WrongPathError(customError):
    """
    Custom Excepttion: Path points to a directory not a file
    """
    def __init__(self, x, arg):
        self.message = "[ERROR] Wrong path to {}: '{}'".format(x, arg)

class InFileSyntaxError(customError):
    """
    Custom Excepttion: Syntax error in the input file
    """
    def __init__(self, path, cpt, arg):
        self.message = "[ERROR] Syntax error in the input file: '{}'\nline {}:'{}'".format(path, cpt, arg)
        