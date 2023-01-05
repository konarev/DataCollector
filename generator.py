def cdata(content: str) -> str:
    return f"<![CDATA[{content}]]>"


class XMLGenerator:
    spaces_tab = 4
    _tab_count = 0
    _nodes_open: list = []
    _sheet = ""

    def begin(self):
        self._sheet = '<?xml version="1.0" encoding="utf-8"?>\n'

    def _left_margin(self) -> str:
        return self.spaces_tab * " " * self._tab_count

    def node(
        self, tagname: str, content: str = "", attr: str | dict = "", after_newline=True
    ):
        if isinstance(attr, dict):
            attr = " ".join(f'{key}="{value}"' for key, value in attr.items())
        self._sheet += (
            self._left_margin()
            + f"<{tagname}"
            + (">" if not attr.strip() else f" {attr}>")
            + f"{content}"
            + f"</{tagname}>"
            + ("\n" if after_newline else "")
        )

    def tag(self, tagname: str, attr: str | dict = "", after_newline=True):
        if isinstance(attr, dict):
            attr = " ".join(f'{key}="{value}"' for key, value in attr.items())
        self._sheet += (
            self._left_margin()
            + f"<{tagname}"
            + ("/>" if not attr.strip() else f" {attr}/>")
            + ("\n" if after_newline else "")
        )

    def node_open(
        self, tagname: str, attr: str | dict = "", after_newline=True
    ) -> bool:
        if isinstance(attr, dict):
            attr = " ".join(f'{key}="{value}"' for key, value in attr.items())
        self._sheet += (
            self._left_margin()
            + f"<{tagname}"
            + (">" if not attr.strip() else f" {attr}>")
            + ("\n" if after_newline else "")
        )
        self._tab_count += 1
        self._nodes_open.append(tagname)
        return True

    def node_close(self, to_position: int = -1, after_newline=True):
        def close():
            tagkey = self._nodes_open.pop()
            self._tab_count -= 1
            self._sheet += (
                self._left_margin() + f"</{tagkey}>" + ("\n" if after_newline else "")
            )

        if to_position == -1:
            close()
        else:
            while self.node_position() != to_position:
                close()

    def end(self) -> str:
        self.node_close(0)  # close all node
        return self._sheet

    def node_position(self):
        return len(self._nodes_open)

    def generate(self) -> str:
        raise NotImplementedError


class RSSGenerator(XMLGenerator):
    def begin(self):
        super().begin()
        self.node_open(
            "rss",
            attr={
                "version": "2.0",
                "xmlns:dc": "http://purl.org/dc/elements/1.1/",
                "xmlns:usr": "https:/github.com/konarev/",
            },
        )

    def header(self) -> dict[str, object]:
        raise NotImplementedError

    def generate(self) -> str:
        _head = self.header()
        self.begin()
        self.node("title", cdata(_head["title"]))
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


class AtomGenerator(XMLGenerator):
    def begin(self):
        super().begin()
        self.node_open(
            "feed",
            attr={
                "xmlns:atom": "http://www.w3.org/2005/Atom",
                "xmlns:usr": "https:/github.com/konarev/",
            },
        )


class HTMLGenerator(XMLGenerator):
    def begin(self):
        self._sheet = "<!doctype html>\n"
        self.tag(
            "html",
            attr={
                "lang": "en",
            },
        )
        if self.node_open("html"):
            self.tag("meta", attr="charset=utf-8")
            self.tag("meta", attr='http-equiv=x-ua-compatible content="IE=edge"')
            self.tag(
                "meta",
                attr={
                    "name": "viewport",
                    "content": "width=device-width",
                    "initial-scale": 1,
                    "maximum-scale": 1,
                },
            )
