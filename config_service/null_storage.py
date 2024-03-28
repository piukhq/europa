from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible()
class NullStorage(Storage):
    """
    Satisfies the Django Storage interface but does not save the file anywhere.
    """
    def url(self, name: str | None) -> str:
        return ""

    def _open(self, name, mode="rb"):
        pass

    def _save(self, name, content):
        pass

    def exists(self, name):
        return False
