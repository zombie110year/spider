import requests
from pathlib import Path
from argparse import ArgumentParser

HEADERS = {
    'cookie': "BL_D_PROV=undefined; BL_T_PROV=undefined; mip_performance_stats_level1=1",
    'host': "c.mipcdn.com",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    'accept-language': "zh,en-US;q=0.5",
    'accept-encoding': "gzip, deflate, br",
    'dnt': "1",
    'connection': "keep-alive",
    'upgrade-insecure-requests': "1"
}

def download(url: str, a: int, b: int):
    """下载指定 URL 下从 a 到 b 的文件"""
    for i in range(a, b + 1):
        urlx = url.format(i)
        response = requests.request("GET", urlx, headers=HEADERS)
        save(response)
        print(urlx)

def save(response: requests.Response):
    """保存 response 得到的二进制文件"""
    dir_ = Path("download")
    filename = response.url.split("/")[-1]

    if not dir_.exists():
        dir_.mkdir()

    with (dir_ / filename).open("wb") as file:
        file.write(response.content)
