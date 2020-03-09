from django.core.files.storage import Storage


class NullStorage(Storage):
    """
    Satisfies the Django Storage interface but does not save the file anywhere.
    """

    def _open(self, name, mode="rb"):
        pass

    def _save(self, name, content):
        pass

    def exists(self, name):
        return False
