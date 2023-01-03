from datetime import datetime


def date2rfc822(date: datetime) -> str:
    return datetime.strftime(date, "%a, %d %b %Y %H:%M:%S")


def cdata(content: str) -> str:
    return f"<![CDATA[{content}]]>"


class XMLTemplate:
    spaceintab = 4
    _tabcount = 0
    _nodes_open: list = []
    _sheet = ""

    def begin(self):
        self._sheet = '<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n'

    def _left_margin(self) -> str:
        return self.spaceintab * " " * self._tabcount

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
        self._tabcount += 1
        self._nodes_open.append(tagname)
        return True

    def node_close(self, to_position: int = -1, after_newline=True):
        def close():
            tagkey = self._nodes_open.pop()
            self._tabcount -= 1
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


class RSSTemplate(XMLTemplate):
    def begin(self):
        super().begin()
        self.node_open(
            "rss",
            attr=(
                'version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"'
                ' xmlns:dc="http://purl.org/dc/elements/1.1/"'
                ' xmlns:usr="https:/github.com/konarev/"'
            ),
        )


class HTMLTemplate(XMLTemplate):
    def begin(self):
        self._sheet = "<!doctype html>\n"
        self.tag("html", attr="lang=en itemscope itemtype=http://schema.org/WebPage")
        if self.node_open("html"):
            self.tag("meta", attr="charset=utf-8")
            self.tag("meta", attr='http-equiv=x-ua-compatible content="IE=edge"')
            self.tag(
                "meta",
                attr='name=viewport content="width=device-width,initial-scale=1,maximum-scale=1"',
            )
