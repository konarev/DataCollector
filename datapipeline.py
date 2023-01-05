import datetime
from typing import Iterable
from requests import Response
from singleton import Singleton
import connection
from dataclasses import dataclass, field , KW_ONLY


@dataclass()
class Item:
    id: str
    title: str
    url: str
    _: KW_ONLY
    description: str = field(default=None)
    date_create: datetime.datetime = field(default=None)
    tags: tuple[str] = field(default_factory=tuple)

    def __new__(cls, *args, **kwargs):
        if cls is Item:
            raise RuntimeError(f"{cls.__name__} of {cls.__module__} is abstract class")
        if not hasattr(cls, "_instances"):
            cls._instances: dict[str, Item] = {}
        if len(args):
            instance_key = args[0]
        elif not (instance_key := kwargs.get("id")):
            raise RuntimeError("Id argument missing")
        instance_key = f"{cls.__module__}:{cls.__name__}:{instance_key}"
        if not (instance := cls._instances.get(instance_key)):  # noqa
            instance = super(Item, cls).__new__(cls)
            cls._instances[instance_key] = instance  # noqa
        return instance


#class DataPipeline(metaclass=Singleton):
class DataPipeline():
    page_url: str
    favicon_url: str
    description: str
    title: str
    cache_page_timeout = 5
    rel = ""

    def url(self) -> str:
        raise NotImplementedError

    def get_page(self, url: str) -> Response:
        return connection.get_page(url, self.cache_page_timeout)

    def items(self) -> Iterable[Item]:
        raise NotImplementedError

    def request_handler(
        self,
        id: str,
        title: str,
        descripton: str,
        date_create,
        tags: list[str],
        **kwargs,
    ):
        pass
