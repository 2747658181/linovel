import src
from lxml import etree
import constant
from tenacity import retry, stop_after_attempt, wait_fixed


@retry(stop=stop_after_attempt(7), wait=wait_fixed(0.5))
def get(api_url: str, gbk: bool = False, params: dict = None, method: str = "GET"):
    try:
        return etree.HTML(src.request(method=method, api_url=api_url, gbk=gbk, params=params))
    except Exception as error:
        print(error)
        raise Exception("[error] method:{} api_url: {}".format(method, api_url))


class XbookbenAPI:
    xbookben_host = "https://www.xbookben.net"
    book_info_by_book_id = "/txt/{}.html"
    book_info_by_keyword = "/search"

    @staticmethod
    def get_book_info_by_book_id(book_id: str):
        return get(api_url=XbookbenAPI.xbookben_host + XbookbenAPI.book_info_by_book_id.format(book_id))

    @staticmethod
    def get_chapter_info_by_chapter_id(chapter_url: str):
        return get(api_url=XbookbenAPI.xbookben_host + chapter_url)

    @staticmethod
    def get_book_info_by_keyword(keyword: str):
        response = get(
            method="POST", params={"searchkey": keyword},
            api_url=XbookbenAPI.xbookben_host + XbookbenAPI.book_info_by_keyword
        )
        return list(zip(
            response.xpath(constant.rule.XbookbenRule.Search.book_name),
            response.xpath(constant.rule.XbookbenRule.Search.book_img),
            response.xpath(constant.rule.XbookbenRule.Search.book_id)
        ))


class LinovelAPI:
    linovel_host = "https://www.linovel.net"
    book_info_by_book_id = "/book/{}.html"
    book_info_by_keyword = "/search/"

    @staticmethod
    def get_book_info_by_book_id(book_id: str):
        return get(LinovelAPI.linovel_host + LinovelAPI.book_info_by_book_id.format(book_id))

    @staticmethod
    def get_chapter_info_by_chapter_id(chapter_url: str):
        return get(api_url=LinovelAPI.linovel_host + chapter_url)

    @staticmethod
    def get_book_info_by_keyword(keyword: str, page: int = 1):
        params = {'kw': keyword} if page < 2 else {
            'kw': keyword, 'page': page, 'sort': 'hot', 'target': 'complex', 'mio': 1, 'ua': 'Mozilla/5.0'}
        response = get(api_url=LinovelAPI.linovel_host + LinovelAPI.book_info_by_keyword, params=params)
        return list(zip(
            response.xpath(constant.rule.LinovelRule.Search.book_img),
            response.xpath(constant.rule.LinovelRule.Search.book_name)
        ))


class DingdianAPI:
    @staticmethod
    def get_book_info_by_book_id(book_id: str):
        return get(api_url="https://www.ddyueshu.com/{}".format(book_id), gbk=True)

    @staticmethod
    def get_chapter_info_by_chapter_id(chapter_url):
        return get(api_url='https://www.ddyueshu.com' + chapter_url, gbk=True)


def get_sort(tag_name: str, page: int, retry: int = 0):  # get sort from url by page
    params = {"sort": "words", "sign": "-1", "page": page}
    response = get(api_url="https://www.linovel.net/cat/-1.html", params=params)
    sort_html_list = response.xpath('//a[@class="book-name"]')
    sort_info_list = [i.get('href').split('/')[-1][:-5] for i in sort_html_list]
    if sort_info_list and len(sort_info_list) != 0:
        return sort_info_list


def get_chapter_cover(html_string: [str, etree.ElementTree]) -> [list, None]:
    img_url_list = [
        img_url.get('src') for img_url in html_string.xpath('//div[@class="article-text"]//img')
    ]
    if isinstance(img_url_list, list) and len(img_url_list) != 0:
        return img_url_list
    else:
        return []
