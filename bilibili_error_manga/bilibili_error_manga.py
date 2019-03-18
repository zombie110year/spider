import requests
import time

def getMangaURLList(list_url):

    headers = {
        'host': "www.bilibili.com",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
        'accept': "image/webp,*/*",
        'accept-language': "zh,en-US;q=0.5",
        'accept-encoding': "gzip, deflate, br",
        'dnt': "1",
        'connection': "keep-alive",
        'referer': "https://www.bilibili.com/video/av"
        }

    response = requests.request("GET", list_url, headers=headers)
    raw = response.json().get('data').get('list')
    """
    {
        id,
        vid: 31,
        name,
        data: {img}
    }
    """
    return [item.get('data').get('img') for item in raw]

def download(url):
    """下载图片并保存
    url 没有协议, 类似于 //i0.hdslb.com/bfs/activity-plat/cover/20171215/o6y3r7or6z.png
    """

    filename = url.split("/")[-1]
    response = requests.get("https:" + url)

    with open(filename, "wb") as file:
        for Byte in response.iter_content():
            file.write(Byte)

def main():
    url_list = getMangaURLList("http://www.bilibili.com/activity/web/view/data/31")

    count = len(url_list)
    print("查找到 {} 张图片".format(count))

    current = 0
    for url in url_list:
        download(url)
        current += 1
        print("{}/{}".format(current, count))
        time.sleep(3)

if __name__ == "__main__":
    main()
