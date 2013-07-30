class NoSuchGroup(Exception):
    """
    Raised when a group of unknown name is requested.
    """
    pass


class NoSuchNode(Exception):
    """
    Raised when a node of unknown name is requested.
    """
    pass


class RemoteException(Exception):
    """
    Raised when a shell command on a node fails.
    """
    pass


class RepositoryError(Exception):
    """
    Indicates that somethings is wrong with the current repository.
    """
    pass


class BundleError(RepositoryError):
    """
    Indicates an error in a bundle.
    """
    pass


class ItemDependencyError(RepositoryError):
    """
    Indicates a problem with item dependencies (e.g. loops).
    """
    pass


class UsageException(Exception):
    """
    Raised when command line options don't make sense.
    """
    pass


class WorkerException(Exception):
    """
    Raised when a worker process has encountered an exception while
    executing.
    """
    def __init__(self, traceback):
        self.traceback = traceback

    def __str__(self):
        output = "\n\n+----- traceback from worker ------\n|\n"
        for line in self.traceback.strip().split("\n"):
            output += "|  {}\n".format(line)
        output += "|\n+----------------------------------\n"
        return output
