import sys

from dateutil import parser as dateparser
from dataclasses import dataclass, field

# pylint: disable=C0413
from scrapy.selector import Selector

if __name__ == "__main__":
    sys.path.append("../rss_service")

from datapipeline import DataPipeline, Item  # pylint: disable=C0413
import utils


@dataclass
class MistaItem(Item):
    forum: str = field(default_factory=str)
    section: str = field(default_factory=str)
    page: int = field(default=1)


class Forum(DataPipeline):
    page_url = "https://forum.mista.ru"
    favicon_url = "https://forum.mista.ru/favicon.ico"
    description = "Форум Mista.ru"
    title = "Форум Mista.ru"

    def items(self):  # pylint: disable=R0914
        url_list, params_list = utils.parse_url(self.page_url)
        for page_num in range(1, 2):
            print(f"{page_num=}")
            params_list.update(page=str(page_num))
            url = utils.merge_url(url_list, params_list)
            if not (page := self.get_page(url)).ok:
                return
            selector = Selector(text=page.text, type="html")
            for topic in selector.xpath(query="//tr[starts-with(@class,'forum-')]"):
                title = topic.css("td.ct.col_main").xpath("a/text()").get()
                href = topic.css("td.ct.col_main").xpath("a/@href").get()
                forum = topic.css("td.cc.col_forum").xpath("a/text()").get()
                section = topic.css("td.cl.col_section").xpath("a/text()").get()
                creator = topic.css("td.cl.col_author").xpath("span/text()").get()
                updated_sel = topic.css("td.cl.col_updated")
                updated_time = dateparser.parse(updated_sel.css("::text").get())
                # updated_author = (
                #     updated_sel.xpath("a/userlink/@href"),
                #     updated_sel.css("a.userlink::text"),
                # )
                page = self.get_page(link := "https://forum.mista.ru/" + href)
                guid = link
                selector_msg = Selector(text=page.text, type="html")
                description = utils.strip_tag(
                    selector_msg.xpath("//div[@class='message-text']").get()
                )
                pub_date = dateparser.parse(
                    selector_msg.xpath("//td [@id='tduser0']")
                    .css("div.message-info::text")
                    .get()
                )
                yield MistaItem(
                    guid,
                    url=link,
                    title=title,
                    tags=(forum, section),
                    description=description,
                    page=page_num,
                )

                yield dict(
                    link=link,
                    title=title,
                    category=(forum, section),
                    forum=forum,
                    section=section,
                    updated_time=updated_time,
                    # updated_author=updated_author,
                    creator=creator,
                    description=description,
                    pubDate=pub_date,
                    guid=guid,
                    page=page_num,
                )


class Forum1C(Forum):
    page_url = "https://forum.mista.ru/index.php?forum=1c"
    title = "Форум 1C Mista.ru"
    description = title


# class Forum_1C_v8(Forum):
#     page_url = "https://forum.mista.ru/index.php?section=v8"
#     title = "Форум 1C:Предприятие 8 общая Mista.ru"
#     description = title

# class Forum_1C_v7(Forum):
#     page_url = "https://forum.mista.ru/index.php?section=v7"
#     title = "Форум 1С:Предприятие 7.7 и ранее Mista.ru"
#     description = title


class ForumLife(Forum):
    page_url = "https://forum.mista.ru/index.php?forum=life"
    title = "Форум Life Mista.ru"
    description = title


class ForumJob(Forum):
    page_url = "https://forum.mista.ru/index.php?forum=job"
    title = "Форум Job Mista.ru"
    description = title


class ForumIT(Forum):
    page_url = "https://forum.mista.ru/index.php?forum=it"
    title = "Форум IT Mista.ru"
    description = title


export = [Forum(), Forum1C(), ForumIT(), ForumJob(), ForumLife()]

if __name__ == "__main__":
    for item in Forum().items():
        print(item)
