import os
from collections import defaultdict
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# from rssfeed import RSSFeed
from datapipeline import DataPipeline
from generator import HTMLGenerator, XMLGenerator
from utils import date2rfc822


class RequestHandler(BaseHTTPRequestHandler):
    feeds: dict[str, DataPipeline] = {}

    def server_url(self) -> str:
        server_addr = self.server.socket.getsockname()
        return f"http://{server_addr[0]}:{server_addr[1]}"

    def do_GET(self):
        print(self.path)
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            template = HTMLGenerator()
            template.begin()
            template.node("title", "RSS feeds catalog")
            for href, item in self.feeds.items():
                template.tag(
                    "link",
                    attr=(
                        f'rel=alternate href="{self.server_url()}{href}"'
                        f' type="application/rss+xml" title="{item.title}"'
                    ),
                )
            self.wfile.write(template.end().encode())

        elif self.path in self.feeds:
            self.send_response(200)
            self.send_header("Content-Type", "text/xml; charset=utf-8")
            self.end_headers()
            _feed = self.feeds[self.path].generate()
            self.wfile.write(_feed.encode())
        else:
            self.send_error(404)


def export2opml(feeds: list[RSSFeed], server_url: str) -> str:
    modules: dict[str, list[RSSFeed]] = defaultdict(list)
    for feed in feeds:
        modules[feed.__module__].append(feed)

    template = XMLGenerator()
    template.begin()
    if template.node_open("opml", attr='version="2.0"'):
        if template.node_open("head"):
            template.node("title", "RSS generator")
            template.node("dateModified", date2rfc822(datetime.now()))
            template.node_close()
        if template.node_open("body"):
            for module_name, feeds in modules.items():
                template.node_open("outline", attr=dict(text=module_name))
                for feed in feeds:
                    template.tag(
                        "outline",
                        attr=dict(
                            text=feed.title,
                            type="rss",
                            htmlUrl=feed.page_url,
                            xmlUrl=server_url + feed.url(),
                            description=feed.description,
                        ),
                    )
    return template.end()


def server_url(server, port) -> str:
    return f"http://{server}:{port}"


# def hot_reload_adapters():
#     adapter_list = adapters.load_feeds()


if __name__ == "__main__":

    import sys

    import adapters

    server_address = ("localhost", 8080)

    server_address_str = server_url(*server_address)
    for adapter in adapters.load_list_pipeline(os.getcwd() + "/adapters"):
        RequestHandler.feeds[adapter.url()] = adapter
        print(
            f"Loaded adapter {adapter.title} url='{adapter.page_url}'"
            f" feed_url='{server_address_str}{adapter.url()}'"
        )

    if not RequestHandler.feeds:
        print("Not found RSS adapter.")
        sys.exit()

    opml_file = "generator.opml"
    if os.path.exists(opml_file):
        os.remove(opml_file)

    # server_address = ("localhost", 8080)
    try:
        with open(opml_file, "w", encoding="utf-8") as f:
            f.write(
                export2opml(
                    list(RequestHandler.feeds.values()),
                    server_address_str,
                )
            )
    except FileExistsError as err:
        pass

    webServer = HTTPServer(server_address, RequestHandler)

    print(f"Server started {webServer.socket.getsockname()}")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
