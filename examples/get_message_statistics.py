import os

import work_wechat

corpid = os.environ.get("CORPID")
corpsecret = os.environ.get("CORPSECRET")
agentid = os.environ.get("AGENTID")

ww = work_wechat.WorkWeChat(corpid=corpid, corpsecret=corpsecret)

data = ww.message_get_statistics(time_type=work_wechat.TimeType.TODAY)
for d in data:
    print("应用: %s 发送消息次数：%d" % (d["app_name"], d["count"]))
