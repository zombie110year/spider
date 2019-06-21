"""Exhentai 本子下载器

使用方法:

1. 获取当前在 exhentai 登录的账户使用的 cookie（使用纯文本格式，形如: `ipb_member_id=4*****2; ipb_pass_hash=*********************; igneous=df******; sk=; yay=0`
2. 复制漫画第一页的 url， 形如 `https://exhentai.org/s/**********/********-1`

3. 在命令行中输入以下命令执行::

    python exhentai.py <url> <cookie>
    # 由于 cookie 中含有空格，因此可能需要添加引号
"""
from pathlib import Path, PurePath
from sys import argv
from time import sleep

import requests as r
from bs4 import BeautifulSoup

EH_HEADER = {
    'cookie': "",
    'host': "exhentai.org",
    'connection': "keep-alive",
    'cache-control': "max-age=0",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3818.0 Safari/537.36 Edg/77.0.189.3",
    'sec-fetch-mode': "navigate",
    'sec-fetch-user': "?1",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    'referer': "https://exhentai.org",
    'sec-fetch-site': "none",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "zh-CN,zh;q=0.9,en;q=0.8"
}


def init_session(header: dict, start_page: str, cookie: str) -> r.Session:

    session = r.session()
    session.headers.update(header)
    session.headers.update({"referer": start_page})
    session.headers.update({"cookie": cookie})
    return session


def get_next_page(soup: BeautifulSoup) -> str:
    a = soup.select("#i3 > a")[0]
    url = a["href"]
    return url


def get_img_url(soup: BeautifulSoup) -> str:
    img = soup.select("#img")[0]
    url = img["src"]
    return url


def get_title(soup: BeautifulSoup) -> str:
    h1 = soup.select("#i1 > h1")[0]
    title = h1.string
    return title


def update_session(session: r.Session, next_page: str) -> r.Session:
    session.headers.update({"referer": next_page})
    return session


def fetch_source(session: r.Session, url: str) -> str:
    response = session.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise FileNotFoundError("无法下载资源")


def download_img(img_url: str, directory: str):
    response = r.get(img_url)
    img_url = PurePath(img_url)
    filename = f"{img_url.name}"
    with open(f"{directory}/{filename}", "wb") as file:
        file.write(response.content)


def main(url, cookie, header=EH_HEADER):
    session = init_session(header, url, cookie)

    last_url = url

    html = fetch_source(session, url)
    soup = BeautifulSoup(html, "lxml")
    title = get_title(soup)
    img_url = get_img_url(soup)
    url = get_next_page(soup)

    download_dir = Path(title)
    if not download_dir.exists():
        download_dir.mkdir()

    download_img(img_url, title)

    session.headers.update({"referer": url})

    while url != last_url:
        last_url = url
        print(url)
        html = fetch_source(session, url)
        soup = BeautifulSoup(html, "lxml")
        img_url = get_img_url(soup)
        download_img(img_url, title)

        url = get_next_page(soup)
        session.headers.update({"referer": url})
        sleep(2.0)


if __name__ == "__main__":
    main(argv[1], argv[2])
