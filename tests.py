#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Xiang Wang @ 2019-09-26 10:42:41


from baidu.api import TextCensor
from baidu.client import BaiduClient
from baidu.session.redisstorage import RedisStorage
import logging
import os
from redis import Redis
import unittest


logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger()
# ch = logging.StreamHandler()
# logger.addHandler(ch)

app_id = input("请输入你的app_id(默认读取环境变量BAIDU_APP_ID): ")
if not app_id:
    app_id = os.environ.get("BAIDU_APP_ID")
if not app_id:
    raise Exception("请输入app_id或者设置系统的环境变量BAIDU_APP_ID")
api_key = input("请输入你的api_key(默认读取环境变量BAIDU_API_KEY): ")
if not api_key:
    api_key = os.environ.get("BAIDU_API_KEY")
if not api_key:
    raise Exception("请输入api_key或者设置系统的环境变量BAIDU_API_KEY")
secret_key = input("请输入你的secret_key(默认读取环境变量BAIDU_SECRET_KEY): ")
if not secret_key:
    secret_key = os.environ.get("BAIDU_SECRET_KEY")
if not secret_key:
    raise Exception("请输入secret_key或者设置系统的环境变量BAIDU_SECRET_KEY")


class ClientTest(unittest.TestCase):

    def setUp(self):
        self.client = BaiduClient(
            app_id=app_id, api_key=api_key, secret_key=secret_key)

    def test_access_token(self):
        logger.info("test_access_token")
        self.assertIsInstance(self.client.access_token, str)

    def test_redis_session(self):
        logger.info("test_redis_session")
        redis_client = Redis.from_url("redis://localhost:6379/0")
        session_interface = RedisStorage(redis_client, prefix="baiduapi")
        baidu_client = BaiduClient(app_id, api_key, secret_key,
                                   session=session_interface)
        access_token = baidu_client.access_token
        self.assertIsInstance(access_token, str)
        self.assertEqual(access_token, baidu_client.access_token)
        baidu_client2 = BaiduClient(
            app_id, api_key, secret_key, session=session_interface)
        self.assertEqual(access_token, baidu_client2.access_token)
        self.assertNotEqual(access_token, self.client.access_token)


class ApiTest(unittest.TestCase):

    def setUp(self):
        self.client = BaiduClient(
            app_id=app_id, api_key=api_key, secret_key=secret_key)

    def test_text_censor(self):
        check, detail = TextCensor(self.client).is_allowed("苟利国家生死以")
        self.assertEqual(check, "check")
        allowed, detail = TextCensor(self.client).is_allowed("小明在上英语课")
        self.assertEqual(allowed, "allowed")
        rejected, detail = TextCensor(self.client).is_allowed("在线阅读色情小说,在线赌博,枪支弹药购买: https://iqiyi.com")
        self.assertEqual(rejected, "rejected")
        logger.info(detail)


if __name__ == "__main__":
    unittest.main()
