import requests
import re
import json
from io import BytesIO


class QualityError(Exception):
    def __str__(self):
        return "quality error: no such quality"


def downloader(avid, **options):
    """
    bilibili的下载器，用于下载bilibili的视频和音频
    :param avid: 需要下载的av号
    :param quality: 需要下载的视频或音频的质量
    :param content_type: 指明要下载视频或音频
    :return: 一个包含status和BytesIO的dict
    """
    cookies = {
        "buvid3": "3E7ED94E-C707-4FDF-B170-01D0F46CD1FB4075infoc",
    }
    download_url = ""
    html = requests.get("https://www.bilibili.com/video/av{}".format(avid), cookies=cookies).text
    cid = re.findall(r'"cid":(.*?),"', html)[0]
    url = "https://api.bilibili.com/x/player/playurl?avid={}&cid={}&type=&otype=json&fnver=0&fnval=16".format(avid, cid)
    try:
        info = json.loads(requests.get(url, cookies=cookies).content)["data"]["dash"]
        items = info[options["content_type"]]
        flag = True
        for item in items:
            if item["id"] == options["quality"]:
                download_url = item["baseUrl"]
                flag = False
                break
        if flag:
            raise QualityError
        status = "OK"
    except KeyError:
        download_url = re.findall(r'"url":"(.*?)"', requests.get("https://www.bilibili.com/video/av{}".format(avid), cookies=cookies).text)[0]
        status = "Warning"
    headers = {
        "Origin": "https://www.bilibili.com",
        "Referer": "https://www.bilibili.com/video/av{}".format(avid),
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36"
    }
    file = requests.get(download_url, headers=headers).content
    return {"status": status, "io_obj": BytesIO(file)}


if __name__ == '__main__':
    content_type = input("请输入下载选项（audio表示音频，video表示视频）：")
    avid = input("请输入av号：")
    quality = int(input("请输入视频或音频质量："))
    dic = downloader(avid, quality=quality, content_type=content_type)
    with open("av{}.{}".format(avid, "flv" if content_type == "video" or dic["status"] == "Warning" else "mp3"), "wb") as f:
        f.write(dic["io_obj"].getvalue())
