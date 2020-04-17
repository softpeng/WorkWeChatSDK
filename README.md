# About

A non-official WorkWeChat SDK in Pythonic Python.

非官方 Python 企业微信SDK 。
(懒，实现接口不完整，需要在加了。)


特点：

 - Pythonic
   - 没有异常就是 Keep It Simple Stupid ： 比如获取某个讨论组不存在的时候，返回 None 而不是抛出异常；
   - 可自定义官方接口 errcode 哪些情况抛出异常，哪些不抛出，具体见 SDK 中 `appchat_get` 函数实现；
   - 非写/修改类操作，默认空返回表示成功
 - 函数和参数命名尽可能和官方接口一直，比如 通讯录 创建成员 "/user/create" 对应 SDK 函数为 "user_create"；


## 如何使用

通过 [pipenv](https://pipenv.kennethreitz.org/) 安装 WorkWeChatSDK

    pipenv install WorkWeChatSDK


例子：创建自定义讨论群组

    import os

    import work_wechat

    corpid = os.environ.get("CORPID")
    corpsecret = os.environ.get("CORPSECRET")
    content = "hello world"

    ww = work_wechat.WorkWeChat(
        corpid=corpid,
        corpsecret=corpsecret,
        debug=True, # 打印请求 URL
        http_timeout=5,
    )

    # 可选，调用其他需要token的API时，会自动检测 token 是否存在、过期决定是否需要刷新
    token = ww.get_access_token()
    print('token=%s' % token)

    chatid = ww.appchat_create(
        userlist=("zhangsan", "lisi", "wangwu"),
        chatid="BigNewRoom",
        owner="zhangsan",
        name="搞个大新闻",
    )


例子：通过[群机器人](https://work.weixin.qq.com/api/doc/90000/90136/91770)推送信息

    import os

    import work_wechat

    webhook_key = os.environ.get("WEBHOOK_KEY")
    content = "hello world"

    work_wechat.WorkWeChat().webhook_send(
        key=webhook_key,
        content=content,
    )


异常处理

    import os

    import work_wechat

    webhook_key = os.environ.get("WEBHOOK_KEY")
    content = "hello world"

    try:
        work_wechat.WorkWeChat().webhook_send(
            key=webhook_key,
            content=content,
        )
    except work_wechat.WorkWeChatException as ex:
        # errcode 和 errmsg 分别对应接口响应中字段，ex.rs 为完整 HTTP response
        print(ex.errcode, ex.errmsg, ex.rs)



其他例子见目录 examples/ .
