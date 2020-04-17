import os

import work_wechat

webhook_key = os.environ.get("WEBHOOK_KEY")
content = "hello world"

try:
    work_wechat.WorkWeChat(http_timeout=5, verbose=True).webhook_send(
        key=webhook_key,
        content=content,
    )
except work_wechat.WorkWeChatException as ex:
    print(ex.errcode, ex.errmsg, ex.rs)
