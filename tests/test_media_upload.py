import hashlib
import mimetypes
import os

import requests

import work_wechat


def get_md5(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


corpid = os.environ.get("CORPID")
corpsecret = os.environ.get("CORPSECRET")
agentid = os.environ.get("AGENTID")

mimetypes.add_type("audio/amr", ".amr")

ww = work_wechat.WorkWeChat(corpid=corpid, corpsecret=corpsecret, verbose=True)
token = ww.get_access_token()
print("token=%s" % token)

MIMETYPE2WWTYPE = {
    "image/jpeg": "image",
    "audio/amr": "voice",
    "video/mp4": "video",
}
DEFAULT_CONTENT_TYPE = "file"


def test_media_uploadimg():
    filepath = "d:/中文.jpg"

    filename = os.path.basename(filepath)
    filedata = open(filepath, "rb")
    content_type = mimetypes.guess_type(filepath)[0]

    files = {
        "media": (filename, filedata, content_type)
    }

    r = requests.post(
        url="https://qyapi.weixin.qq.com/cgi-bin/media/uploadimg?access_token={access_token}".format(
            access_token=token,
        ),
        timeout=5,
        files=files,
    )
    rs = r.json()
    assert rs["errcode"] == work_wechat.ErrCode.SUCCESS
    url_pic = rs["url"]

    r = requests.get(url=url_pic, timeout=5)
    got_ct = r.headers["content-type"]
    assert content_type == got_ct

    filedata_blob = open(filepath, "rb").read()
    got_cl = int(r.headers["content-length"])
    got_cl_body = len(r.content)
    want_cl = len(filedata_blob)
    assert want_cl == got_cl == got_cl_body

    want_md5, got_md5 = get_md5(filedata_blob), get_md5(r.content)
    assert want_md5 == got_md5


def test_media_upload():
    for filepath in (
            "d:/中文.jpg",
            "d:/中文.txt",
            "d:/gs-16b-1c-8000hz.amr",
            "d:/file_example_MP4_480_1_5MG.mp4",
    ):
        filename = os.path.basename(filepath)
        filedata = open(filepath, "rb")
        content_type = mimetypes.guess_type(filepath)[0]
        files = {
            "media": (filename, filedata, content_type)
        }

        r = requests.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type={type}'.format(
                access_token=token,
                type=MIMETYPE2WWTYPE.get(content_type, DEFAULT_CONTENT_TYPE),
            ),
            timeout=5,
            files=files,
        )
        rs = r.json()
        assert rs["errcode"] == work_wechat.ErrCode.SUCCESS
        media_id = rs["media_id"]

        r = requests.get(
            url="https://qyapi.weixin.qq.com/cgi-bin/media/get?access_token={access_token}&media_id={media_id}".format(
                access_token=token,
                media_id=media_id,
            ),
            timeout=5,
        )

        got_ct = r.headers["content-type"]
        assert content_type == got_ct

        filedata_blob = open(filepath, "rb").read()
        got_cl = int(r.headers["content-length"])
        got_cl_body = len(r.content)
        want_cl = len(filedata_blob)
        assert want_cl == got_cl == got_cl_body

        want_md5, got_md5 = get_md5(filedata_blob), get_md5(r.content)
        assert want_md5 == got_md5

test_media_uploadimg()
test_media_upload()
