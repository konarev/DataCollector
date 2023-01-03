import importlib
import importlib.util
import os
import os.path
from typing import Iterable

from rssfeed import RSSFeed


def load_next_feed(adapters_folder: str) -> Iterable[RSSFeed]:
    feed_already_loaded = set()
    for root, _, files in os.walk(adapters_folder):
        for file in files:
            if not file.endswith(".py"):
                continue
            module_name = os.path.basename(os.path.splitext(file)[0])
            if not (
                module_spec := importlib.util.spec_from_file_location(
                    module_name, root + "/" + file
                )
            ):
                continue
            if not (loader := module_spec.loader):
                continue
            module_loaded = importlib.util.module_from_spec(module_spec)
            loader.exec_module(module_loaded)
            #            if not (export := module_loaded.__dict__.get("export")):
            if not (export := getattr(module_loaded, "export", None)):
                del module_loaded
                continue
            feed_obj: RSSFeed
            for feed_obj in export:
                if type(feed_obj) in feed_already_loaded:
                    print(
                        f"Feed with type {type(feed_obj)} already loaded. {feed_obj} not accepted"
                    )
                    del feed_obj
                    continue
                feed_already_loaded.add(type(feed_obj))
                yield feed_obj


def load_feeds(adapters_folder: str) -> list[RSSFeed]:
    return list(load_next_feed(adapters_folder))


if __name__ == "__main__":
    adapters = load_feeds(os.getcwd() + "/adapters")
    for adapter in adapters:
        print(adapter)
