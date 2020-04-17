import os

import work_wechat

corpid = os.environ.get("CORPID")
corpsecret = os.environ.get("CORPSECRET")
content = "hello world"

ww = work_wechat.WorkWeChat(corpid=corpid, corpsecret=corpsecret)
chatid = ww.appchat_create(
    userlist=("zhangsan", "lisi", "wangwu"),
    chatid="BigNewRoom",
    owner="zhangsan",
    name="搞个大新闻",
)

ww.appchat_get(chatid=chatid)

ww.appchat_send(chatid=chatid, content="hello world")
