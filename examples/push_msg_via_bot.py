import base64
import hashlib
import os

import work_wechat

webhook_key = os.environ.get("WEBHOOK_KEY")


def push_txt():
    msg = "hello world"
    work_wechat.WorkWeChat().webhook_send(
        key=webhook_key,
        text_content=msg,
    )


def push_md():
    msg = '''# github down
We investigating it.

**blob**
'''

    work_wechat.WorkWeChat().webhook_send(
        key=webhook_key,
        markdown_content=msg,
    )


def push_img():
    img_blob = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAoAAAABCAYAAADn9T9+AAAAEElEQVR42mNkYPhfz0AEAAA4hwGA8wQHOAAAAABJRU5ErkJggg==')
    """
    or  
        with open("path/to/img.png", "rb") as f:
            img_blob = f.read()
    """

    image_base64 = base64.b64encode(img_blob).decode('utf8')
    image_md5 = hashlib.md5(img_blob).hexdigest()

    work_wechat.WorkWeChat().webhook_send(
        key=webhook_key,
        image_base64=image_base64,
        image_md5=image_md5,
    )


def push_news():
    a1 = work_wechat.NewsArticle(**dict(
        title='WorkWeChat SDK Part 1',
        description='A WorkWeChat SDK written in Python.',
        url='https://work.weixin.qq.com/',
        picurl="https://wwcdn.weixin.qq.com/node/wwnl/wwnl/style/images/independent/index/caselist/mdl_pic@2x$4713c09f.png",
    ))

    a2 = work_wechat.NewsArticle(**dict(
        title='WorkWeChat SDK Part 2',
        description='A WorkWeChat SDK written in Python.',
        url='https://work.weixin.qq.com/',
        picurl="https://wwcdn.weixin.qq.com/node/wwnl/wwnl/style/images/independent/index/caselist/mdl_pic@2x$4713c09f.png",
    ))

    work_wechat.WorkWeChat().webhook_send(
        key=webhook_key,
        news_articles=[a1, a2],
    )
