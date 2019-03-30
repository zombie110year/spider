import json
from pathlib import Path
from time import strftime, localtime

import requests as r

HEADERS = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    'accept-language': "zh,en-US;q=0.5",
    'accept-encoding': "gzip, deflate, br",
    'dnt': "1",
    'connection': "keep-alive",
    'upgrade-insecure-requests': "1",
    'referer': "http://www.bilibili.com/",
    'cache-control': "max-age=0"
}


class Favorate:
    """一个收藏夹, 传入此部分 json 实例化"""

    def __init__(self, obj: dict):
        self.id = obj.get("id")         # 该收藏夹的唯一标识
        self.fid = obj.get("fid")
        self.title = obj.get("title")
        self.media_count = obj.get("media_count")
        self.member = []

    def get_videos(self, session, total, id):
        """获取此收藏夹下的所有视频信息

        :param session: 已登录的会话
        :param total: 该收藏夹中的视频数量
        :param id: 用于查找收藏夹的唯一代码
        """
        package = {
            "media_id": id,
            "pn": 0,  # 当前页数
            "ps": 20,  # 一页多少个视频
            "keyword": None,
            "order": "mtime",
            "type": 0,
            "tid": 0,
            "jsonp": "jsonp",
        }

        for i in range(0, total // package["ps"] + 1):
            package["pn"] = i + 1
            res = session.get(
                "http://api.bilibili.com/medialist/gateway/base/spaceDetail", headers=HEADERS, params=package)
            medias = res.json().get("data").get("medias")  # list

            for m in medias:
                self.member.append(Video(m))

        return self.member

    def save(self):
        """将收藏夹保存到文件
        """
        root = Path("download/" + self.title)

        if root.exists():
            pass
        else:
            root.mkdir(parents=True)

        json_content = {"medias": [
            m.tojson() for m in self.member
        ]}

        for m in self.member:
            m.save_cover(root)

        json_file = root / "{}.json".format(
            strftime("%Y%m%d%H%M%S", localtime())
        )

        with json_file.open("wt", encoding="utf-8", newline="\n") as file:
            json.dump(json_content, file, indent=1, sort_keys=True, ensure_ascii=False)


class Video:
    """一个视频"""

    def __init__(self, obj: dict):
        self.aid = obj.get("id")   # av号
        self.title = obj.get("title")
        self.author = obj.get("upper").get("name")
        self.author_uid = obj.get("upper").get("mid")
        self.cover = obj.get("cover")      # 封面图片地址
        self.intro = obj.get("intro")
        if self.title == "已失效视频":
            self.is_blocked = True
            self.title = None
        else:
            self.is_blocked = False

    def save_cover(self, root: Path):
        "收藏夹所在的地址"
        filename = self.cover.split("/")[-1]
        file_path = root / filename
        if not file_path.exists():
            response = r.get(self.cover)
            with file_path.open("wb") as file:
                for byte in response.iter_content():
                    file.write(byte)
            print("{} Downlaoded".format(filename))
        else:
            print("{} Exists".format(filename))

    def tojson(self):
        return {
            "aid": self.aid,
            "title": self.title,
            "intro": self.intro,
            "author": self.author,
            "author_uid": self.author_uid,
            "cover": self.cover,
            "is_blocked": self.is_blocked,
        }


class Application:
    """Bilibili Client"""
    url = "https://bilibili.com"
    cookie_file = "cookie.txt"

    def __init__(self):
        cookie = Path(self.cookie_file).read_text().rstrip()
        uid = dict([
            item.split("=") for item in cookie.split("; ")
        ]).get("DedeUserID")
        self.__session = r.Session()
        self.__session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
            "Cookie": cookie,
        })

        self.__uid = uid

    def run(self):
        package = {
            "pn": 1,
            "ps": 100,
            "up_mid": self.__uid,      # 用户 UID
            "is_space": 0,
            "jsonp": "jsonp",
        }
        response = self.__session.get(
            "http://api.bilibili.com/medialist/gateway/base/created", headers=HEADERS, params=package)
        favlists = response.json().get("data").get("list")

        stack_fav = []

        for d in favlists:
            stack_fav.append(
                Favorate(d)
            )

        for fav in stack_fav:
            fav.get_videos(self.__session, fav.media_count, fav.id)
        for fav in stack_fav:
            fav.save()
