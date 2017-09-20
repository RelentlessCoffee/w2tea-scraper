import pathlib
import socket
DEFAULT_CACHE_DIR = pathlib.Path("~/.cache/teascraper/raw_data")
WHITELIST_HOSTNAMES = [
    "ubuntu",
]


def cache_for_host():
    hostname = socket.gethostname()
    if hostname in WHITELIST_HOSTNAMES:
        cls = Cache
    else:
        cls = NoopCache
    return cls()


class Cache:
    """
    Usage:
        cache = Cache(pathlib.Path("~/.cache/s3/"))
        for item in s3.list_objects(Prefix="foo-bar"):
            data = cache.get(item)
            print(len(data))
    """
    def __init__(self, cache_dir: pathlib.Path=DEFAULT_CACHE_DIR):
        self.cache_dir = cache_dir.expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = self.cache_dir.resolve()

    def get(self, item):
        if not self._has_local(item):
            return self._get_remote(item)
        return self._get_local(item)

    def _has_local(self, item) -> bool:
        path = self.cache_dir / item.bucket_name / item.key
        return path.exists()

    def _get_remote(self, item) -> str:
        data = item.get()["Body"].read().decode("utf-8")
        path = self.cache_dir / item.bucket_name / item.key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data)
        return data

    def _get_local(self, item) -> str:
        path = self.cache_dir / item.bucket_name / item.key
        return path.read_text()


class NoopCache(Cache):
    """Always uses S3"""
    def __init__(self):
        pass

    def _get_remote(self, item) -> str:
        return item.get()["Body"].read().decode("utf-8")

    def _has_local(self, item) -> bool:
        return False

    def _get_local(self, item) -> str:
        raise NotImplementedError
