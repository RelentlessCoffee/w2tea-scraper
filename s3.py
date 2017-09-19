import pathlib
DEFAULT_CACHE_DIR = pathlib.Path("~/.cache/teascraper/raw_data")


# noinspection PyUnresolvedReferences
class Cache:
    """
    Usage:
        cache = Cache(pathlib.Path("~/.cache/s3/"))
        for item in s3.list_objects(Prefix="foo-bar"):
            data = cache.get(item)
            print(len(data))
    """
    def __init__(self, cache_dir: pathlib.Path=DEFAULT_CACHE_DIR):
        self.cache_dir = cache_dir.expand_user().resolve()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, item):
        if not self._has_local(item):
            self._save(item)
        return self._local_get(item)

    def _has_local(self, item):
        path = self.cache_dir / item["Bucket"] / item["Key"]
        return path.exists()

    def _save(self, item):
        path = self.cache_dir / item["Bucket"] / item["Key"]
        data = item.get()["Body"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data.read())

    def _local_get(self, item):
        path = self.cache_dir / item["Bucket"] / item["Key"]
        return path.read_text()

