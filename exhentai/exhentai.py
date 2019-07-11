"""Exhentai 本子下载器

使用方法:

1. 获取当前在 exhentai 登录的账户使用的 cookie（使用纯文本格式，形如: `ipb_member_id=4*****2; ipb_pass_hash=*********************; igneous=df******; sk=; yay=0`

    可以在开发者工具的 Console 栏中执行 `document.cookie` 语句得到 cookie 的纯文本格式.

2. 复制漫画第一页的 url， 形如 `https://exhentai.org/s/**********/********-1`

3. 在命令行中输入以下命令执行::

    python exhentai.py <url>

cookie 将从当前工作目录下的 cookie.txt 文件中读取.
"""
from pathlib import Path, PurePath
from sys import argv, stderr
from time import sleep
from threading import Thread, Lock
from queue import Queue

import requests as r
from bs4 import BeautifulSoup


class ExHentaiPageParser:

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

    def __init__(self, first):
        self.cookie = Path("cookie.txt").read_text().strip()

        self.session = r.session()
        self.session.headers.update(self.EH_HEADER)
        self.session.headers.update({"referer": first})
        self.session.headers.update({"cookie": self.cookie})

        self.urls = Queue()
        self._lock = Lock()
        self.urls.put(first)
        # 等待初始化
        self.title = None
        self.downloader = None
        self._end = False

    def connectImageDownloader(self, downloader):
        self.downloader = downloader
        downloader.ehs = self

    def setEnd(self):
        self._end = True

    def end(self):
        return self._end

    def setTitle(self, title):
        self.title = title
        self.downloader.set_title(self.title)
        if not Path(self.title).exists():
            Path(self.title).mkdir()

    def getUrl(self):
        self._lock.acquire()
        try:
            url = self.urls.get()
        finally:
            self._lock.release()

        return url

    def parse(self):
        url = self.getUrl()
        try:
            response = self.session.get(url)
        except:
            print(f"\x1b[31merror for {url}\x1b[0m")
            self.setEnd()
            return

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            next_page = soup.select("#i3 > a")[0]["href"]
            img_url = soup.select("#img")[0]["src"]

            if next_page == url:
                print("end")
                self.setEnd()
                return

            if self.title is None:
                self.setTitle(soup.select("#i1 > h1")[0].string)

            self._lock.acquire()
            try:
                self.urls.put(next_page)
                self.downloader.add(img_url)
            finally:
                self._lock.release()

            print(f"\x1b[33mfetching {url}\x1b[0m")
            self.session.headers.update({"referer": next_page})

        else:
            print(f"\x1b[31merror for {url}\x1b[0m")


class ImageDownloader:

    def __init__(self):

        self.imgs = Queue()
        self._lock = Lock()

        # 等待初始化
        self.title = None
        self.ehs = None

    def download(self):

        self._lock.acquire()
        try:
            url = self.imgs.get()
        finally:
            self._lock.release()
        try:
            response = r.get(url)
        except:
            print(f"\x1b[31merror for {url}\x1b[0m")
            return

        if response.status_code == 200:
            filename = f"{PurePath(url).name}"
            with open(f"{self.title}/{filename}", "wb") as file:
                file.write(response.content)

            print(f"\x1b[32mdownload {url}\n  => {self.title}/{filename}\x1b[0m")

    def set_title(self, title):
        self.title = title

    def add(self, url):
        self._lock.acquire()
        try:
            self.imgs.put(url)
        finally:
            self._lock.release()

    def end(self):
        if self.imgs.empty() and self.ehs.end():
            return True
        else:
            return False


def parse(ehs: ExHentaiPageParser):
    while not ehs.end():
        # print("parse")
        ehs.parse()
        sleep(3)


def download(dl: ImageDownloader):
    while not dl.end():
        if not dl.imgs.empty():
            # print("download")
            dl.download()
        else:
            sleep(3)


def main(url):
    ehs = ExHentaiPageParser(url)
    dl = ImageDownloader()
    ehs.connectImageDownloader(dl)

    parse_worker = Thread(target=parse, name="parse", args=(ehs,))
    download_worker = Thread(target=download, name="download", args=(dl,))
    # print("prebuild threading")
    parse_worker.start()
    download_worker.start()

    parse_worker.join()
    download_worker.join()


if __name__ == "__main__":
    main(argv[1])
