import os

import work_wechat

corpid = os.environ.get("CORPID")
corpsecret = os.environ.get("CORPSECRET")
mydepartid = os.environ.get("MYDEPARTID")

ww = work_wechat.WorkWeChat(corpid=corpid, corpsecret=corpsecret)
rs = ww.user_simplelist(department_id=mydepartid, fetch_child=True)
print(rs)
