from datetime import datetime
from utils import date2rfc822
from generator import AtomGenerator, cdata
from datapipeline import DataPipeline


USE_USERTAG: bool = True


class AtomFeed(AtomGenerator):
    accept_flows = ["InfoFlow"]  # or accept_flows = [InfoFlow]
    pipeline: DataPipeline

    def __init__(self, pipeline: DataPipeline):
        super().__init__()
        self.pipeline = pipeline

    def url(self) -> str:
        return "/atom/" + self.__class__.__name__ + "." + self.__module__ + "/feed"

    def header(self) -> dict[str, object]:
        return self.pipeline.__dict__

    def generate(self) -> str:
        _pipeline = self.pipeline
        self.begin()
        self.node("title", cdata(_pipeline.title))
        self.node("link", cdata(_pipeline.page_url))
        self.node("description", cdata(_pipeline.description))
        self.node("lastBuildDate", date2rfc822(datetime.now()))
        if self.node_open("image"):
            self.node("url", _pipeline.favicon_url)
            self.node("title", cdata(_pipeline.title))
            self.node_close()
        self.node("language", "en-us")
        # try:
        # self.header()
        _node_position = self.node_position()
        for item in _pipeline.items():
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

                for user_key in userkeys:
                    self.node(f"usr:{user_key}", item[user_key])

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
