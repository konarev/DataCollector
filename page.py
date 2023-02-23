import datetime
from typing import Iterable, Any

import pydantic
from requests import Response
from singleton import Singleton
import connection
from dataclasses import dataclass, field, KW_ONLY

from pydantic import BaseModel
from pydantic.dataclasses import dataclass


_cached_page: dict[str, "Item"] = {}


def _current_time() -> datetime.datetime:
    return datetime.datetime.now()


def get_cached_page(url: str) -> "Item":
    # return connection.get_page(url, self.cache_page_timeout)
    # if (page:=_cached_page.get(url)) and (_current_time()>page.lives_until):
    #     page=None
    return (
        page
        if (page := _cached_page.get(url)) and (_current_time() < page.lives_until)
        else None
    )


def get_page(url: str) -> "Item":
    return page if (page := get_cached_page(url)) else None


class Action(pydantic.BaseModel):
    """
    Описывает действие для экземпляра им владеющего
    """

    pass


class OpenSubPage(Action):
    """
    Действие открывает подстраницу для с владельца действия
    """

    # Адрес подстраницы
    url: pydantic.AnyHttpUrl


# class ActionsList(BaseModel):
#     """
#     Список возможных действий для экземпляра-владельца
#     """
#
#     actions: list


# @dataclass()
class Item(pydantic.BaseModel):
    """
    Элемент страницы, может иметь действия
    """

    # id: str
    # Заголовок элемента
    title: str
    _: KW_ONLY
    # url: str | None
    # text: str | None = field(default=None)
    # this_action: bool = False
    # date_create: datetime.datetime | None = field(default=None)

    actions: tuple[Action]
    tags: tuple[str]  # = field(default_factory=tuple)
    # raw_text: str | None = None
    lives_until: datetime.datetime = None

    # def __new__(cls, *args, **kwargs):
    #     if cls is Page:
    #         raise RuntimeError(f"{cls.__name__} of {cls.__module__} is abstract class")
    #     if not hasattr(cls, "_instances"):
    #         cls._instances: dict[str, Page] = {}
    #     if len(args):
    #         instance_key = args[0]
    #     elif not (instance_key := kwargs.get("id")):
    #         raise RuntimeError("Id argument missing")
    #     instance_key = f"{cls.__module__}:{cls.__name__}:{instance_key}"
    #     if not (instance := cls._instances.get(instance_key)):  # noqa
    #         instance = super(Page, cls).__new__(cls)
    #         cls._instances[instance_key] = instance  # noqa
    #     return instance

    # def __init__(self, title: str, text: str = None, tags: tuple[str] = tuple()):
    #     super().__init__()
    #     self.title = title
    #     # self.url = url
    #     self.tags = tags
    #     self.text = text
    #     # self.raw_text=raw_text

    #
    # @classmethod
    # def from_connection(cls,title:str,url:str)->'Page':
    #     pass
    #

    # @classmethod
    # def from_raw(cls, raw: Any) -> "Item":
    #     cls.raw_text
    #     raise NotImplementedError

    @classmethod
    def from_url(cls, url: str) -> "Item":
        if page := get_cached_page(url):
            return page
        # TODO: timeout сделать не константой
        resp = connection.get_page(url, 10)
        return cls.from_raw(resp.raw)

    def get_subpages(self) -> Iterable["Item"] | None:
        yield None

    def __hash__(self):
        return hash(self.url)

    # def get_page(self, url: str) -> "Page":
    #     return page if (page := get_cached_page(url)) else None

    # def get_page_fromconnection(self):

    # return connection.get_page(url, self.cache_page_timeout)

    # def get_text(self) -> str | None:
    #    return None

    # def get_url(self) -> str | None:
    #    return None


# class RSSPage(Item):
#     def __init__(self, title: str, date_create: datetime.datetime, **kwargs):
#         super().__init__(title, **kwargs)
#         self.date_create = date_create


# class DataPipeline(metaclass=Singleton):
class Page(pydantic.BaseModel):
    page_url: str
    favicon_url: pydantic.HttpUrl
    description: str
    title: str
    cache_page_timeout = 5
    # rel = ""

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
        # descripton: str,
        date_create,
        tags: list[str],
        **kwargs,
    ):
        pass
