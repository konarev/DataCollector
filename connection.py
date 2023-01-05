from functools import lru_cache
from requests import Response, get
import time

# from datetime import datetime


# by example
# https://stackoverflow.com/questions/31771286/python-in-memory-cache-with-time-to-live
def get_page(url: str, timeout: int = 10) -> Response:
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
        return get(url, timeout=10)

    return get_page(url, round(time.time() / timeout))
