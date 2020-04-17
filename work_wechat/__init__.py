import copy
import json
import logging
import time
import typing
import urllib.parse

import requests


class ErrCode:
    ERROR = -1
    SUCCESS = 0

    INVALID_USERID_LIST = 40031
    DEPARTMENT_NOT_FOUND = 60003
    NO_PRIVILEGE_TO_ACCESS_OR_MODIFY = 60011
    USERID_NOT_FOUND = 60111

    CHATID_INVALID = 86001
    CHATID_EXISTED = 86215


class WorkWeChatException(Exception):
    def __init__(self, errcode: int, errmsg: str, rs: dict):
        self.errcode = errcode
        self.errmsg = errmsg
        self.rs = rs

    def __str__(self) -> str:
        return "%s" % self.rs


class WorkWeChat(object):

    def __init__(self, corpid: str = None, corpsecret: str = None, verbose: bool = False, http_timeout: int = 5):
        self._corpid = corpid
        self._corpsecret = corpsecret
        self._verbose = verbose

        self._url_prefix = "https://qyapi.weixin.qq.com/cgi-bin"
        self._http_timeout = http_timeout

        self._access_token_expires_in = 0
        self._access_token = None

    def _update_access_token(self):
        now = int(time.time())
        if not self._access_token or now > self._access_token_expires_in:
            rs = self.gettoken()

            self._access_token_expires_in = int(time.time()) + rs["expires_in"]
            self._access_token = rs["access_token"]

    def get_access_token(self) -> str:
        self._update_access_token()
        return self._access_token

    def _send_req(
            self,
            method: str,
            path: str,
            params_qs: dict = None,
            params_post: dict = None,
            errcodes_accepted: typing.Tuple[int, ...] = None,
            auto_update_token: bool = True,
    ) -> dict:
        if not errcodes_accepted:
            errcodes_accepted = (ErrCode.SUCCESS,)

        if not params_qs:
            params_qs = dict()

        if auto_update_token:
            params_qs["access_token"] = self.get_access_token()

        qs = urllib.parse.urlencode(params_qs)
        url = self._url_prefix + path + "?" + qs

        data_post = None
        if params_post:
            data_post = json.dumps(params_post)

        if self._verbose:
            logging.debug("%s %s" % (method, url))
        r = requests.request(method=method, url=url, timeout=self._http_timeout, data=data_post)
        rs = r.json()
        if rs["errcode"] not in errcodes_accepted:
            raise WorkWeChatException(errcode=rs["errcode"], errmsg=rs["errmsg"], rs=rs)

        return rs

    def gettoken(self) -> dict:
        """
        https://work.weixin.qq.com/api/doc/90000/90135/91039
        """
        params_qs = dict(
            corpid=self._corpid,
            corpsecret=self._corpsecret,
        )
        qs = urllib.parse.urlencode(params_qs)
        url = self._url_prefix + "/gettoken?" + qs
        r = requests.get(url=url, timeout=self._http_timeout)
        rs = r.json()
        assert rs["errcode"] == ErrCode.SUCCESS
        """
        {
           "errcode": 0,
           "errmsg": "ok",
           "access_token": "accesstoken000001",
           "expires_in": 7200
        }
        """
        return dict(
            access_token=rs["access_token"],
            expires_in=rs["expires_in"],
        )

    def appchat_get(self, chatid: str) -> typing.Optional[dict]:
        """
        https://work.weixin.qq.com/api/doc/90000/90135/90247
        """

        params_qs = dict(chatid=chatid)
        errcodes_accepted = (ErrCode.SUCCESS, ErrCode.CHATID_INVALID)
        rs = self._send_req(
            method="GET",
            path="/appchat/get",
            params_qs=params_qs,
            errcodes_accepted=errcodes_accepted,
        )
        """
         {
           "errcode" : 0,
           "errmsg" : "ok"
           "chat_info" : {
              "chatid" : "CHATID",
              "name" : "NAME",
              "owner" : "userid2",
              "userlist" : ["userid1", "userid2", "userid3"]
           }
         }
        """
        return rs["chat_info"]

    def appchat_send(self, chatid: str, content: str):
        """
        https://work.weixin.qq.com/api/doc/90000/90135/90248
        """
        data = dict(
            chatid=chatid,
            msgtype="text",
            text=dict(
                content=content,
            ),
            safe=0,
        )

        self._send_req(method="POST", path="/appchat/send", params_post=data)
        """
         {
           "errcode" : 0,
           "errmsg" : "ok",
         }
        """

    def appchat_create(
            self,
            userlist: typing.Tuple[str, ...],
            chatid: str = None,
            owner: str = None,
            name: str = None,
    ) -> str:
        """
        https://work.weixin.qq.com/api/doc/90000/90135/90245
        """
        data = dict(
            userlist=userlist,
        )
        if chatid:
            data["chatid"] = chatid
        if owner:
            data["owner"] = owner
        if name:
            data["name"] = name

        errcodes_accepted = (ErrCode.SUCCESS, ErrCode.CHATID_EXISTED)
        rs = self._send_req(
            method="POST",
            path="/appchat/create",
            params_post=data,
            errcodes_accepted=errcodes_accepted,
        )
        """
         {
           "errcode" : 0,
           "errmsg" : "ok",
           "chatid" : "CHATID"
         }
         """

        if rs["errcode"] == ErrCode.CHATID_EXISTED:
            return chatid

        return rs["chatid"]

    def appchat_update(
            self, chatid: str,
            name: str = None,
            owner: str = None,
            add_user_list: typing.Set[str] = None,
            del_user_list: typing.Set[str] = None,
    ):
        """
        https://work.weixin.qq.com/api/doc/90000/90135/90246
        """

        data = dict(chatid=chatid)

        if name is not None:
            data["name"] = name
        if owner is not None:
            data["owner"] = owner
        if add_user_list is not None:
            data["add_user_list"] = list(add_user_list)
        if del_user_list is not None:
            data["del_user_list"] = list(del_user_list)

        self._send_req(method="POST", path="/appchat/update", params_post=data)
        """
         {
           "errcode" : 0,
           "errmsg" : "ok"
         }

        """

    def user_simplelist(
            self,
            department_id: int,
            fetch_child: bool = False
    ) -> typing.Optional[typing.List[dict]]:
        """
        https://work.weixin.qq.com/api/doc/90000/90135/90200
        """
        data = dict(
            department_id=department_id,
            fetch_child=int(fetch_child),
        )
        rs = self._send_req(method="GET", path="/user/simplelist", params_qs=data)
        return rs["userlist"]

    def webhook_send(
            self,
            key: str,
            content: str,
            mentioned_list: typing.List[str] = None,
            mentioned_mobile_list: typing.List[str] = None,
    ):
        """
        https://work.weixin.qq.com/help?doc_id=13376
        """
        if key.startswith("https"):
            # user pass a url such as "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=..."
            key = key.split("key=")[-1]

        data_qs = dict(
            key=key,
        )
        data_post = dict(
            msgtype="text",
            text=dict(
                content=content,
            )
        )

        if mentioned_list:
            data_post["text"]["mentioned_list"] = mentioned_list
        if mentioned_mobile_list:
            data_post["text"]["mentioned_mobile_list"] = mentioned_mobile_list

        self._send_req(auto_update_token=False, method="POST", path="/webhook/send", params_qs=data_qs, params_post=data_post)

    def agent_get(
            self,
            agentid: int,
    ) -> dict:
        """
        https://work.weixin.qq.com/api/doc/90000/90135/90227
        """
        data_qs = dict(agentid=agentid)
        rs = self._send_req(method="POST", path="/agent/get", params_qs=data_qs)
        """
        {
           "errcode": 0,
           "errmsg": "ok",
           "agentid": 1000005,
           "name": "HR助手",
           "square_logo_url":  "https://p.qlogo.cn/bizmail/FicwmI50icF8GH9ib7rUAYR5kicLTgP265naVFQKnleqSlRhiaBx7QA9u7Q/0",
           "description": "HR服务与员工自助平台",
           "allow_userinfos": {
               "user": [
                     {"userid": "zhangshan"},
                     {"userid": "lisi"}
               ]
            },
           "allow_partys": {
               "partyid": [1]
            },
           "allow_tags": {
               "tagid": [1,2,3]
            },
           "close": 0,
           "redirect_domain": "open.work.weixin.qq.com",
           "report_location_flag": 0,
           "isreportenter": 0,
           "home_url": "https://open.work.weixin.qq.com"
        }
        """
        rs = copy.deepcopy(rs)
        for i in (
                "errcode",
                "errmsg",
        ):
            rs.pop(i)
        return rs

    def _drop_fields(self, rs: dict, fields=None) -> dict:
        fields_default = (
            "errcode",
            "errmsg",
        )
        if not fields:
            fields = fields_default
        rs = copy.deepcopy(rs)
        for i in fields:
            try:
                rs.pop(i)
            except KeyError:
                pass
            return rs

    def user_get(self, userid: str) -> typing.Optional[dict]:
        """
        注意：在通讯录同步助手中此接口可以读取企业通讯录的所有成员信息，而自建应用可以读取该应用设置的可见范围内的成员信息。
        https://open.work.weixin.qq.com/api/doc/90000/90135/90196
        """
        data_qs = dict(
            userid=userid,
        )
        errcodes_accepted = (ErrCode.SUCCESS, ErrCode.USERID_NOT_FOUND)
        rs = self._send_req(
            method="GET",
            path="/user/get",
            params_qs=data_qs,
            errcodes_accepted=errcodes_accepted,
        )
        if rs["errcode"] == ErrCode.USERID_NOT_FOUND:
            return
        """
        {
            "errcode": 0,
            "errmsg": "ok",
            "userid": "zhangsan",
            "name": "李四",
            "department": [1, 2],
            "order": [1, 2],
            "position": "后台工程师",
            "mobile": "13800000000",
            "gender": "1",
            "email": "zhangsan@gzdev.com",
            "is_leader_in_dept": [1, 0],
            "avatar": "http://wx.qlogo.cn/mmopen/ajNVdqHZLLA3WJ6DSZUfiakYe37PKnQhBIeOQBO4czqrnZDS79FH5Wm5m4X69TBicnHFlhiafvDwklOpZeXYQQ2icg/0",
            "thumb_avatar": "http://wx.qlogo.cn/mmopen/ajNVdqHZLLA3WJ6DSZUfiakYe37PKnQhBIeOQBO4czqrnZDS79FH5Wm5m4X69TBicnHFlhiafvDwklOpZeXYQQ2icg/100",
            "telephone": "020-123456",
            "alias": "jackzhang",
            "address": "广州市海珠区新港中路",
            "open_userid": "xxxxxx",
            "main_department": 1,
            "extattr": {
                "attrs": [
                    {
                        "type": 0,
                        "name": "文本名称",
                        "text": {
                            "value": "文本"
                        }
                    },
                    {
                        "type": 1,
                        "name": "网页名称",
                        "web": {
                            "url": "http://www.test.com",
                            "title": "标题"
                        }
                    }
                ]
            },
            "status": 1,
            "qr_code": "https://open.work.weixin.qq.com/wwopen/userQRCode?vcode=xxx",
            "external_position": "产品经理",
            "external_profile": {
                "external_corp_name": "企业简称",
                "external_attr": [{
                        "type": 0,
                        "name": "文本名称",
                        "text": {
                            "value": "文本"
                        }
                    },
                    {
                        "type": 1,
                        "name": "网页名称",
                        "web": {
                            "url": "http://www.test.com",
                            "title": "标题"
                        }
                    },
                    {
                        "type": 2,
                        "name": "测试app",
                        "miniprogram": {
                            "appid": "wx8bd80126147dFAKE",
                            "pagepath": "/index",
                            "title": "my miniprogram"
                        }
                    }
                ]
            }
        }        
        """
        return rs
