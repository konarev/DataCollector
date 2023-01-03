import time
from datetime import datetime
from functools import lru_cache
from typing import Iterable

import requests

from template import RSSTemplate, cdata, date2rfc822

# import scrapy

USE_USERTAG: bool = True

# by example
# https://stackoverflow.com/questions/31771286/python-in-memory-cache-with-time-to-live
def _get_page(url: str, timeout: int = 10) -> requests.Response:
    @lru_cache(maxsize=100)
    def get_page(url, time_arg):
        del time_arg
        # HEADERS = {
        #     "User-Agent": """\
        #         Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
        # Chrome/44.0.2403.157 Safari/537.36""",
        #     "Accept-Language": "en-US, en;q=0.5",
        # }
        # return requests.get(url, headers=HEADERS, timeout=10)
        # scrapy.Request(url)
        return requests.get(url, timeout=10)

    return get_page(url, round(time.time() / timeout))


class RSSFeed(RSSTemplate):
    page_url: str
    favicon_url: str
    description: str
    title: str
    cache_page_timeout = 5
    rel = ""

    def url(self) -> str:
        return "/rss/" + self.__class__.__name__ + "." + self.__module__ + "/feed"

    def generate(self) -> str:
        self.begin()
        if self.node_open("channel"):
            self.node("title", cdata(self.title))
            self.node("link", cdata(self.page_url))
            self.node("description", cdata(self.description))
            self.node("lastBuildDate", date2rfc822(datetime.now()))
            if self.node_open("image"):
                self.node("url", self.favicon_url)
                self.node("title", cdata(self.title))
                self.node_close()
            self.node("language", "en-us")
        # try:
        # self.header()
        _node_position = self.node_position()
        for item in self.items():
            if self.node_open("item"):
                self.node("title", cdata(item["title"]))
                self.node("link", item["link"])
                self.node("description", cdata(item["description"]))
                self.node("guid", item["guid"])

            if item.get("pubDate"):
                self.node("pubDate", date2rfc822(item["pubDate"]))
            if item.get("creator"):
                self.node("dc:creator", item["creator"])
            if item.get("category"):
                for category in item["category"]:
                    if category is not None:
                        self.node("category", cdata(category))

            if USE_USERTAG:
                userkeys = set(item.keys()) - {
                    "title",
                    "link",
                    "description",
                    "guid",
                    "pubDate",
                    "creator",
                    "category",
                }

                for userkey in userkeys:
                    self.node(f"usr:{userkey}", item[userkey])

            self.node_close(to_position=_node_position)
        # except Exception as err:  # pylint: disable=W
        #     # self.header()
        #     if self.node_open("<item>"):
        #         self.node("title", "Error generation feed!")
        #         self.node("link")
        #         self.node("description", str(err))
        #         self.node("guid")
        #     self.node_close()
        #     raise err

        return self.end()

    #
    # def header(self):
    #     self.begin()
    #     if self.node_open("channel"):
    #         self.node("title", cdata(self.title))
    #         self.node("link", cdata(self.page_url))
    #         self.node("description", cdata(self.description))
    #         self.node("lastBuildDate", date2rfc822(datetime.now()))
    #         if self.node_open("image"):
    #             self.node("url", self.favicon_url)
    #             self.node("title", cdata(self.title))
    #             self.node_close()
    #         self.node("language", "en-us")

    def get_page(self, url: str) -> requests.Response:
        return _get_page(url, self.cache_page_timeout)

    def items(self) -> Iterable[dict]:
        raise NotImplementedError
