# -*- coding: UTF-8 -*-

import os
import re
import copy
import math
import json
import time
import uuid
import yaml
import js2py
import urllib
import base64
import random
import asyncio
import datetime
import pyrogram
import aiosqlite
import mimetypes
import unicodedata
import nest_asyncio
from loguru import logger
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import BotCommand, CallbackQuery, Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ChosenInlineResult, InputRichMessage, ReplyParameters
from curl_cffi.requests import AsyncSession

import logging
logging.getLogger("pyrogram").setLevel(logging.ERROR)

def js2py_monkey_patch():
    from js2py.constructors.jsobject import Object
    fn = Object.own["getOwnPropertyNames"]["value"].code
    def wraps(*args, **kwargs):
        result = fn(*args, **kwargs)
        return list(result)
    Object.own["getOwnPropertyNames"]["value"].code = wraps

js2py_monkey_patch()
nest_asyncio.apply()

version_content = "1.0.18"
version_id = 2026092601
version_source = "Official"

command_description = {
    '.': {
        'Description': '配置文件',
        'type': 'dict',
        'Branch': ['SuAdmin', 'Admin', 'Bot', 'Network', 'Other', 'AI', 'User'],
        'Default': {},
    },
    'Config': {
        'Description': '配置文件',
        'type': 'dict',
        'Branch': ['SuAdmin', 'Admin', 'Bot', 'Network', 'AI', 'User', 'Other'],
        'Default': {},
    },
    'SuAdmin': {
        'Description': '超级管理员列表',
        'type': 'list',
        'Branch': None,
        'Default': [],
    },
    'Admin': {
        'Description': '管理员列表',
        'type': 'list',
        'Branch': None,
        'Default': [],
    },
    'Bot': {
        'Description': '机器人相关',
        'type': 'dict',
        'Branch': ['ApiHash', 'ApiId', 'CreateSession', 'Token', 'Proxy', 'SleepThreshold', 'HideCommand'],
        'Default': {},
    },
    'Bot.ApiHash': {
        'Description': 'ApiHash',
        'type': 'str',
        'Branch': None,
        'Default': {},
        'Hide': True,
    },
    'Bot.ApiId': {
        'Description': 'ApiId',
        'type': 'int',
        'Branch': None,
        'Default': {},
        'Hide': True,
    },
    'Bot.CreateSession': {
        'Description': '是否保存Session',
        'type': 'bool',
        'Branch': None,
        'Default': True,
    },
    'Bot.Token': {
        'Description': '机器人密钥',
        'type': 'str',
        'Branch': None,
        'Default': None,
        'Hide': True,
    },
    'Bot.Proxy': {
        'Description': '机器人代理',
        'type': 'dict',
        'Branch': None,
        'Default': None,
    },
    'Bot.SleepThreshold': {
        'Description': '休眠阈值',
        'type': 'int',
        'Branch': None,
        'Default': 10,
    },
    'Bot.HideCommand': {
        'Description': '是否隐藏命令',
        'type': 'bool',
        'Branch': None,
        'Default': False,
    },
    'Network': {
        'Description': '网络相关',
        'type': 'dict',
        'Branch': ['Proxy', 'Timeout', 'Retry', 'Thread', 'OverridedUA'],
        'Default': {},
    },
    'Network.Proxy': {
        'Description': '代理',
        'type': 'list',
        'Branch': None,
        'Default': None,
    },
    'Network.Timeout': {
        'Description': '超时时间',
        'type': 'int',
        'Branch': None,
        'Default': 5,
    },
    'Network.Retry': {
        'Description': '重试次数',
        'type': 'int',
        'Branch': None,
        'Default': 3,
    },
    'Network.Thread': {
        'Description': '线程数量',
        'type': 'int',
        'Branch': None,
        'Default': 8,
    },
    'Network.OverridedUA': {
        'Description': '覆写UA',
        'type': 'str',
        'Branch': None,
        'Default': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
    },
    'Other': {
        'Description': '其他配置',
        'type': 'dict',
        'Branch': ['Log', 'Intro', 'Password', 'AvoidJoinGroups', 'RefreshFrequency', 'MaxTextLength'],
        'Default': {},
    },
    'Other.Log': {
        'Description': '日志相关',
        'type': 'dict',
        'Branch': ['Enable', 'Name'],
        'Default': {},
    },
    'Other.Log.Enable': {
        'Description': '是否保存日志',
        'type': 'bool',
        'Branch': None,
        'Default': True,
    },
    'Other.Log.Name': {
        'Description': '日志文件名称',
        'type': 'str',
        'Branch': None,
        'Default': 'Bot.log',
    },
    'Other.Intro': {
        'Description': '机器人介绍',
        'type': 'dict',
        'Branch': ['Enable', 'Text'],
        'Default': {},
    },
    'Other.Intro.Enable': {
        'Description': '是否开启介绍',
        'type': 'bool',
        'Branch': None,
        'Default': True,
    },
    'Other.Intro.Text': {
        'Description': '介绍文本',
        'type': 'str',
        'Branch': None,
        'Default': '这是一个用 `Telegram Bot Api` 来提供 AI 的平台捏 ~',
    },
    'Other.Password': {
        'Description': '密码',
        'type': 'str',
        'Branch': None,
        'Default': '1145141919810',
        'Hide': True,
    },
    'Other.AvoidJoinGroups': {
        'Description': '防拉群模式',
        'type': 'int',
        'Branch': None,
        'Default': 0,
    },
    'Other.RefreshFrequency': {
        'Description': '进度条刷新频率',
        'type': 'int',
        'Branch': None,
        'Default': 5,
    },
    'Other.MaxTextLength': {
        'Description': '最长消息长度',
        'type': 'int',
        'Branch': None,
        'Default': 3000,
    },
    'AI': {
        'Description': 'AI相关',
        'type': 'dict',
        'Branch': ['Vendor', 'ChunkStrategy', 'Tool', 'Memory', 'WhiteList', 'DefaultModel', 'FallbackModel', 'SystemPrompt', 'ExtraSystemPrompt', 'ReasoningEffort', 'MaxContext', 'MaxFileSize', 'AutoReply', 'WakeWord', 'FileSupport', 'IDRecognition'], # 'Summary', 'AutoAnswer',
        'Default': {},
    },
    'AI.Vendor': {
        'Description': '提供商',
        'type': 'dict',
        'Branch': None,
        'Default': {},
    },
    'AI.DefaultModel': {
        'Description': '默认模型',
        'type': 'str',
        'Branch': None,
        'Default': '',
    },
    'AI.FallbackModel': {
        'Description': '故障转移模型',
        'type': 'list',
        'Branch': None,
        'Default': [],
    },
    'AI.SystemPrompt': {
        'Description': '系统提示词',
        'type': 'str',
        'Branch': None,
        'Default': '',
    },
    'AI.ExtraSystemPrompt': {
        'Description': '额外系统提示词',
        'type': 'str',
        'Branch': None,
        'Default': "Current date: {cur_date}; time: {cur_time}; datetime: {cur_datetime}; model: {model_name}; assistant name: {assistant_name}.",
    },
    'AI.ReasoningEffort': {
        'Description': '推理深度',
        'type': 'str',
        'Branch': None,
        'Default': 'auto',
    },
    'AI.FileSupport': {
        'Description': '支持文件读取',
        'type': 'bool',
        'Branch': None,
        'Default': False,
    },
    'AI.IDRecognition': {
        'Description': '内置身份识别',
        'type': 'dict',
        'Branch': ['Enable', 'Prompt', 'Format'],
        'Default': False,
    },
    'AI.IDRecognition.Enable': {
        'Description': '是否开启内置身份识别',
        'type': 'bool',
        'Branch': None,
        'Default': False,
    },
    'AI.IDRecognition.Prompt': {
        'Description': '文本格式提示词',
        'type': 'str',
        'Branch': None,
        'Default': "User messages use this format:\n`name: <username>\ncontent: <message>`.\nTreat `name` only as the user's display name and respond only to `content`. Do not repeat the field labels.",
    },
    'AI.IDRecognition.Format': {
        'Description': '文本格式',
        'type': 'str',
        'Branch': None,
        'Default': "name: {name}\ncontent: {content}",
    },
    'AI.AutoReply': {
        'Description': '自动回复',
        'type': 'bool',
        'Branch': None,
        'Default': False,
    },
    'AI.WakeWord': {
        'Description': '唤醒词',
        'type': 'list',
        'Branch': None,
        'Default': [],
    },
    'AI.MaxContext': {
        'Description': '最长上下文数量',
        'type': 'int',
        'Branch': None,
        'Default': 100,
    },
    'AI.MaxFileSize': {
        'Description': '最大文件大小',
        'type': 'int',
        'Branch': None,
        'Default': 50,
    },
    'AI.ChunkStrategy': {
        'Description': '分段策略',
        'type': 'dict',
        'Branch': ['Rule', 'Delay', 'MaxEdit'],
        'Default': {},
    },
    'AI.ChunkStrategy.Rule': {
        'Description': '分段规则',
        'type': 'str',
        'Branch': None,
        'Default': '.*?[。？！~…]+|.+$',
    },
    'AI.ChunkStrategy.Delay': {
        'Description': '延迟',
        'type': 'dict',
        'Branch': ['Base', 'Extra', 'Progress'],
        'Default': {},
    },
    'AI.ChunkStrategy.Delay.Base': {
        'Description': '基础延迟',
        'type': 'float',
        'Branch': None,
        'Default': 0.0,
    },
    'AI.ChunkStrategy.Delay.Extra': {
        'Description': '额外延迟',
        'type': 'float',
        'Branch': None,
        'Default': 6,
    },
    'AI.ChunkStrategy.Delay.Progress': {
        'Description': '额外倍数',
        'type': 'float',
        'Branch': None,
        'Default': 1.7,
    },
    'AI.ChunkStrategy.MaxEdit': {
        'Description': '最大编辑次数',
        'type': 'int',
        'Branch': None,
        'Default': 40,
    },
    'AI.Summary': {
        'Description': '总结相关',
        'type': 'dict',
        'Branch': ['Enable', 'MaxMessage', 'Model'],
        'Default': {},
    },
    'AI.Summary.Enable': {
        'Description': '是否开启总结',
        'type': 'bool',
        'Branch': None,
        'Default': True,
    },
    'AI.Summary.MaxMessage': {
        'Description': '最大总结消息',
        'type': 'int',
        'Branch': None,
        'Default': 100,
    },
    'AI.Summary.Model': {
        'Description': '总结模型',
        'type': 'str',
        'Branch': None,
        'Default': '',
    },
    'AI.AutoAnswer': {
        'Description': '自动回复相关',
        'type': 'dict',
        'Branch': ['Enable', 'MaxContext', 'Model', 'Keyword', 'Threshold‌', 'Group'],
        'Default': {},
    },
    'AI.AutoAnswer.Enable': {
        'Description': '是否开启自动回复',
        'type': 'bool',
        'Branch': None,
        'Default': True,
    },
    'AI.AutoAnswer.MaxContext': {
        'Description': '最大自动回复上下文',
        'type': 'int',
        'Branch': None,
        'Default': 100,
    },
    'AI.AutoAnswer.Model': {
        'Description': '自动回复模型',
        'type': 'str',
        'Branch': None,
        'Default': '',
    },
    'AI.AutoAnswer.Keyword': {
        'Description': '自动回复关键词',
        'type': 'list',
        'Branch': None,
        'Default': ['?', '？', '吗', '为什么', '提问', '问题'],
    },
    'AI.AutoAnswer.Threshold‌': {
        'Description': '自动回复阈值',
        'type': 'int',
        'Branch': None,
        'Default': 100,
    },
    'AI.AutoAnswer.Group': {
        'Description': '自动回复群组',
        'type': 'list',
        'Branch': None,
        'Default': [],
    },
    'AI.Tool': {
        'Description': '工具调用',
        'type': 'dict',
        'Branch': ['Enable', 'MaxToolCall', 'WebSearch', 'FetchURL', 'JSExecution'],
        'Default': {},
    },
    'AI.Tool.Enable': {
        'Description': '是否启用工具',
        'type': 'bool',
        'Branch': None,
        'Default': True,
    },
    'AI.Tool.MaxToolCall': {
        'Description': '最大工具调用轮数',
        'type': 'int',
        'Branch': None,
        'Default': 5,
    },
    'AI.Tool.WebSearch': {
        'Description': '网页搜索',
        'type': 'dict',
        'Branch': ['Enable', 'ApiKey'],
        'Default': {},
    },
    'AI.Tool.WebSearch.Enable': {
        'Description': '是否启用网页搜索',
        'type': 'bool',
        'Branch': None,
        'Default': False,
    },
    'AI.Tool.WebSearch.ApiKey': {
        'Description': 'Tavily API密钥',
        'type': 'str',
        'Branch': None,
        'Default': '',
        'Hide': True,
    },
    'AI.Tool.FetchURL': {
        'Description': 'URL抓取',
        'type': 'dict',
        'Branch': ['Enable'],
        'Default': {},
    },
    'AI.Tool.FetchURL.Enable': {
        'Description': '是否启用URL抓取',
        'type': 'bool',
        'Branch': None,
        'Default': True,
    },
    'AI.Tool.JSExecution': {
        'Description': 'JS代码执行',
        'type': 'dict',
        'Branch': ['Enable'],
        'Default': {},
    },
    'AI.Tool.JSExecution.Enable': {
        'Description': '是否启用JS代码执行',
        'type': 'bool',
        'Branch': None,
        'Default': True,
    },
    'AI.Memory': {
        'Description': '长期记忆',
        'type': 'dict',
        'Branch': ['Enable'],
        'Default': {},
    },
    'AI.Memory.Enable': {
        'Description': '是否启用长期记忆',
        'type': 'bool',
        'Branch': None,
        'Default': True,
    },
    'AI.WhiteList': {
        'Description': '白名单群组',
        'type': 'list',
        'Branch': None,
        'Default': [],
    },
    'User': {
        'Description': '用户相关',
        'type': 'dict',
        'Branch': None,
        'Default': {},
    },
}

TOOLS_DEFINITION = {
    "web_fetch": {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Fetch the content of a web page given a URL. Use this when you need to retrieve information from a specific webpage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the web page to fetch."
                    }
                },
                "required": ["url"]
            }
        }
    },
    "web_search": {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "A web search tool that uses search engine to search the web for relevant content. "
                "Ideal for gathering current information, news, and detailed web content analysis and real-time web retrieval."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string."
                    }
                },
                "required": ["query"]
            }
        }
    },
    "executejscode": {
        "type": "function",
        "function": {
            "name": "executejscode",
            "description": (
                "Execute ECMAScript 5.1 JavaScript code and return the js2py execution result."
                "The provided code must define a global function `handler(data)`, "
                "and all logic should be implemented inside `handler(data)`. "
                "The system will call `handler(data)` with the provided input. "
                "Built-in helpers and features available inside the JavaScript runtime: "
                "`fetch(url, params)` for HTTP requests; "
                "`get(data, path, defaults)` for safe nested property access; "
                "`safeStringify(data)` for JSON serialization; "
                "`safeParse(data)` for JSON parsing; "
                "The JavaScript code must explicitly return a result from `handler(data)`."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": (
                            "The full ECMAScript 5.1 JavaScript source code to execute. "
                            "It must define `function handler(data) { ... }`."
                            "The code may use the built-in helpers: fetch get safeStringify safeParse"
                        )
                    },
                    "data": {
                        "type": "string",
                        "description": (
                            "The input passed to `handler(data)` as a JSON-encoded string. "
                            "It should be valid JSON, such as an object, array, string, "
                            "number, boolean, or null encoded as text."
                        )
                    }
                },
                "required": ["content", "data"],
                "additionalProperties": False
            }
        }
    },
    "memory_save": {
        "type": "function",
        "function": {
            "name": "memory_save",
            "description": "Save a long-term memory that will be shown to you in future conversations. Use it for stable facts and preferences worth remembering, not for transient details. Saving an existing topic overwrites it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Short unique key, e.g. 'preferred_language'."},
                    "content": {"type": "string", "description": "What to remember."},
                    "scope": {"type": "string", "enum": ["user", "chat"], "description": "'user' = about the current user (default); 'chat' = shared by this chat."}
                },
                "required": ["topic", "content"]
            }
        }
    },
    "memory_delete": {
        "type": "function",
        "function": {
            "name": "memory_delete",
            "description": "Delete a long-term memory by topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The topic to delete."},
                    "scope": {"type": "string", "enum": ["user", "chat"]}
                },
                "required": ["topic"]
            }
        }
    }
}

def convert_space(s: str) -> str:
    temp = ""
    i = 0
    while i < len(s):
        try:
            if s[i] == "\\" and s[i + 1] == "s":
                temp = temp + " "
                i = i + 2
            elif s[i] == "\\" and s[i + 1] == "\\":
                temp = temp + "\\"
                i = i + 2
            else:
                temp = temp + s[i]
                i = i + 1
        except:
            temp = temp + s[i]
            i = i + 1
    return temp

def load_config(conf, path, lastpath):
    describe = command_description.get(path, 'None')
    if describe is None:
        logger.error("Config Error: Empty Path")
        os._exit(0)
    if describe['Branch'] is None:
        try:
            val = conf.get(path.split('.')[-1], None)
        except:
            return describe['Default']
        if val is None:
            return describe['Default']
        else:
            try:
                if describe['type'] == 'bool':
                    if str(val).lower() == 'true' or str(val) == '1':
                        return True
                    elif str(val).lower() == 'false' or str(val) == '0':
                        return False
                    else:
                        return bool(val)
                elif describe['type'] == 'int':
                    return int(val)
                elif describe['type'] == 'float':
                    return float(val)
                elif describe['type'] == 'str':
                    return str(val)
                elif describe['type'] == 'list':
                    return list(val)
                elif describe['type'] == 'dict':
                    return dict(val)
                else:
                    return val
            except:
                logger.error(f"Config Error: Path {path} supposed to be {describe['type']} Instead of {type(val).__name__}")
                os._exit(0)
    else:
        thisbranch = {}
        for branch in describe['Branch']:
            if not describe['type'] == type(conf).__name__:
                logger.error(f"Config Error: Path {lastpath} supposed to be {describe['type']} Instead of {type(conf).__name__}")
                os._exit(0)
            if path == 'Config':
                thisbranch[branch] = load_config(conf, branch, branch)
            else:
                thisbranch[branch] = load_config(conf.get(path.split('.')[-1], describe['Default']), path + '.' + branch, path)
        return thisbranch

class SafeFormatDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"

class Config:
    def __init__(self, configpath="./config.yaml"):
        logger.info('Initializing Config')
        tempconfig = {}
        try:
            with open(configpath, "r", encoding="UTF-8") as fp:
                tempconfig = yaml.safe_load(fp)
            self.config = load_config(tempconfig, 'Config', 'Config')
            with open(configpath, "w", encoding="UTF-8") as fp:
                yaml.safe_dump(self.config, fp, sort_keys = False, allow_unicode = True)
        except FileNotFoundError:
            logger.error("Config not found")
            os._exit(0)
    
    def Reload(self, configpath="./config.yaml"):
        logger.info('Reloading Config')
        tempconfig = {}
        try:
            with open(configpath, "r", encoding="UTF-8") as fp:
                tempconfig = yaml.safe_load(fp)
            self.config = load_config(tempconfig, 'Config', 'Config')
            with open(configpath, "w", encoding="UTF-8") as fp:
                yaml.safe_dump(self.config, fp, sort_keys = False, allow_unicode = True)
        except FileNotFoundError:
            logger.error("Config not found")
            os._exit(0)

    def Save(self, configpath="./config.yaml"):
        with open(configpath, "w", encoding="UTF-8") as fp:
            yaml.safe_dump(self.config, fp, sort_keys = False, allow_unicode = True)
    
    def LoadApiId(self):
        try:
            logger.info('Obtaining Bot ApiId')
            return self.config['Bot']['ApiId']
        except:
            logger.error("Bot ApiId not found")
            os._exit(0)
    
    def LoadApiHash(self):
        try:
            logger.info('Obtaining Bot ApiHash')
            return self.config['Bot']['ApiHash']
        except:
            logger.error("Bot ApiHash not found")
            os._exit(0)

    def LoadBotToken(self):
        try:
            logger.info('Obtaining Bot Token')
            return self.config['Bot']['Token']
        except:
            logger.error("Bot Token not found")
            os._exit(0)
    
    def LoadBotProxy(self):
        try:
            logger.info('Obtaining Bot Proxy')
            return self.config['Bot']['Proxy']
        except:
            logger.error("Bot Token not found")
            os._exit(0)
    
    def LoadSuAdmin(self):
        try:
            logger.info('Obtaining SuAdmin')
            return list(set(self.config['SuAdmin']))
        except:
            logger.error("SuAdmin not found")
            os._exit(0)
    
    def LoadAdmin(self):
        try:
            logger.info('Obtaining Admin')
            for userid in list(set(self.config['SuAdmin'] + self.config['Admin'])):
                conf_temp = {
                    "Model": "",
                    "SystemPrompt": "",
                    "ReasoningEffort": "",
                    "Context": True
                }
                if self.config['User'].get(userid, None) is None:
                    self.config['User'][userid] = {}
                for k, v in conf_temp.items():
                    self.config['User'][userid].setdefault(k, v)
            self.Save()
            return list(set(self.config['SuAdmin'] + self.config['Admin']))
        except:
            return []
    
    def GetSleepThreshold(self):
        try:
            logger.info('Obtaining SleepThreshold')
            return self.config['Bot']['SleepThreshold']
        except:
            return False
    
    def GetCreateSession(self):
        try:
            logger.info('Obtaining CreateSession')
            return bool((self.config['Bot']['CreateSession'] + 1) % 2)
        except:
            return False

config = Config()

app = Client("AIBot", api_id = config.LoadApiId(), api_hash = config.LoadApiHash(), bot_token = config.LoadBotToken(), in_memory = config.GetCreateSession(), proxy = config.LoadBotProxy(), sleep_threshold = config.GetSleepThreshold(), max_concurrent_transmissions = 1024)

admin_list = config.LoadAdmin()
su_admin_list = config.LoadSuAdmin()

bot_me = None

semaphore = asyncio.Semaphore(config.config['Network']['Thread'])

test_prune_flag = False
stop_prune_flag = False

prune_history = None

already_check = 0

wait_send = {}

proxy_pos = 0

model_list = {}

view_content = {}

generating_content = {}

stop_generate_flag = {}

def safe_ai_text(text: str) -> str:
    return unicodedata.normalize("NFC", str(text))
    #return ''.join(re.findall(r'[\u3400-\u4DBF\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF\uFF66-\uFF9F\uAC00-\uD7A3A-Za-z0-9_-]+', name))

def remove_bot_username(message: str, bot_username: str) -> str:
    if not message or not bot_username:
        return message
    message = safe_ai_text(message)
    bot_username = safe_ai_text(bot_username)
    n = len(bot_username)
    name_cmp = bot_username.casefold()
    def match_at(i: int) -> bool:
        return (
            0 <= i <= len(message) - n
            and message[i:i + n].casefold() == name_cmp
        )
    def skip_spaces_right(i: int) -> int:
        while i < len(message) and message[i] == ' ':
            i += 1
        return i
    def skip_spaces_left(i: int) -> int:
        while i >= 0 and message[i] == ' ':
            i -= 1
        return i
    # 1. 优先删开头：@bot + 空格 + 正文
    if match_at(0):
        j = n
        if j < len(message) and message[j] == ' ':
            j = skip_spaces_right(j)
            if j < len(message):  # 后面要有正文
                return message[j:]
    # 2. 其次删结尾：正文 + 空格 + @bot
    end_pos = len(message) - n
    if end_pos >= 0 and match_at(end_pos):
        j = end_pos - 1
        if j >= 0 and message[j] == ' ':
            j = skip_spaces_left(j)
            if j >= 0:  # 前面要有正文
                return message[:j + 1]
    # 3. 最后删中间：正文 + 空格 + @bot + 空格 + 正文
    best = None
    msg_len = len(message)
    for i in range(1, msg_len - n):
        if not match_at(i):
            continue
        if message[i - 1] != ' ':
            continue
        if i + n >= msg_len or message[i + n] != ' ':
            continue
        left_space_start = i - 1
        while left_space_start > 0 and message[left_space_start - 1] == ' ':
            left_space_start -= 1
        right_space_end = i + n
        while right_space_end < msg_len and message[right_space_end] == ' ':
            right_space_end += 1
        if left_space_start == 0 or right_space_end == msg_len:
            continue
        # 距离开头或结尾谁更近就优先谁；同距离取更靠前的
        dist = min(i, msg_len - (i + n))
        item = (dist, i, left_space_start, right_space_end)
        if best is None or item < best:
            best = item
    if best is None:
        return message
    _, _, left_space_start, right_space_end = best
    return message[:left_space_start] + ' ' + message[right_space_end:]

def get_model_list():
    global model_list
    temp_list = {}
    for aivendor in config.config['AI']['Vendor']:
        for modelname in config.config['AI']['Vendor'][aivendor].get('Model', []):
            temp_list[modelname] = aivendor
    model_list = temp_list

chat_db = None
#topic_db = None

def quote_table_name(chatid) -> str:
    """
    SQLite 表名不能用 ? 占位，所以这里手动安全转义。
    """
    name = str(chatid)
    name = name.replace('"', '""')
    return f'"{name}"'
async def init_db():
    global chat_db, topic_db
    chat_db = await aiosqlite.connect("Chat.db")
    #topic_db = await aiosqlite.connect("Topic.db")
    chat_db.row_factory = aiosqlite.Row
    #topic_db.row_factory = aiosqlite.Row
    await chat_db.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            scope TEXT NOT NULL,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            updated INTEGER NOT NULL,
            PRIMARY KEY (scope, topic)
        )
    """)
    await chat_db.commit()
async def close_db():
    if chat_db:
        await chat_db.close()
    #if topic_db:
    #    await topic_db.close()

async def add_chat(chatid, name: str, content: str):
    """
    传入 chatid, name, content
    以 chatid 作为表名，不存在则创建
    在表最后添加 name 和 content
    """
    table = quote_table_name(chatid)
    await chat_db.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            name TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)
    await chat_db.execute(
        f"INSERT INTO {table} (name, content) VALUES (?, ?)",
        (name, content)
    )
    await chat_db.commit()
async def get_chat(chatid) -> list[dict]:
    """
    传入 chatid
    获取该表内所有 name 和 content
    如果表不存在，返回空列表
    """
    table = quote_table_name(chatid)
    async with chat_db.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (str(chatid),)
    ) as cursor:
        exists = await cursor.fetchone()
    if not exists:
        return []
    async with chat_db.execute(
        f"SELECT name, content FROM {table} ORDER BY rowid"
    ) as cursor:
        rows = await cursor.fetchall()
    return [
        {
            "name": row["name"],
            "content": row["content"]
        }
        for row in rows
    ]
async def clear_chat(chatid):
    """
    传入 chatid
    删除该表内全部内容
    如果表不存在则什么都不做
    """
    table = quote_table_name(chatid)
    async with chat_db.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (str(chatid),)
    ) as cursor:
        exists = await cursor.fetchone()
    if not exists:
        return
    await chat_db.execute(f"DELETE FROM {table}")
    await chat_db.commit()
async def keep_last_chat(chatid, count: int):
    """
    传入 chatid 和数量 count
    删除该 chatid 表中除了最后 count 行以外的所有前面记录
    然后 VACUUM 压缩 Chat.db
    """
    table = quote_table_name(chatid)
    count = max(0, int(count))
    async with chat_db.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (str(chatid),)
    ) as cursor:
        exists = await cursor.fetchone()
    if not exists:
        return
    await chat_db.execute(f"""
        DELETE FROM {table}
        WHERE rowid NOT IN (
            SELECT rowid FROM {table}
            ORDER BY rowid DESC
            LIMIT ?
        )
    """, (count,))
    await chat_db.commit()
    # VACUUM 不能在未提交事务中执行，所以要先 commit
    await chat_db.execute("VACUUM")
    await chat_db.commit()

async def save_memory(scope: str, topic: str, content: str):
    await chat_db.execute(
        "INSERT INTO memories (scope, topic, content, updated) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(scope, topic) DO UPDATE SET content = excluded.content, updated = excluded.updated",
        (scope, topic, content, int(time.time()))
    )
    await chat_db.commit()

async def delete_memory(scope: str, topic: str) -> bool:
    cursor = await chat_db.execute(
        "DELETE FROM memories WHERE scope = ? AND topic = ?",
        (scope, topic)
    )
    await chat_db.commit()
    return cursor.rowcount > 0

async def list_memories(scope: str) -> list[dict]:
    async with chat_db.execute(
        "SELECT topic, content FROM memories WHERE scope = ? ORDER BY updated",
        (scope,)
    ) as cursor:
        return [dict(row) for row in await cursor.fetchall()]

async def clear_memories(scope: str):
    await chat_db.execute("DELETE FROM memories WHERE scope = ?", (scope,))
    await chat_db.commit()

def memory_scope(user_id, chatid, scope: str = "user") -> str:
    return f"chat:{chatid}" if scope == "chat" else f"user:{user_id}"

async def get_memory_prompt(user_id, chatid) -> str:
    memories = [("user", item) for item in await list_memories(memory_scope(user_id, chatid))]
    memories += [("chat", item) for item in await list_memories(memory_scope(user_id, chatid, "chat"))]
    if not memories:
        return ""
    return "Long-term memories (manage with memory_save / memory_delete):\n" + "\n".join(
        f"- [{scope}] {item['topic']}: {item['content']}" for scope, item in memories
    )

async def memory_text(user_id, chatid, argument: str) -> str:
    argument = argument.strip()
    if argument == "clear":
        await clear_memories(memory_scope(user_id, chatid))
        return "✔ 已清除你的长期记忆 ~"
    if argument == "clear chat":
        if int(user_id) not in admin_list:
            return "❌ 您没有权限呢 请联系超管授权 ~"
        await clear_memories(memory_scope(user_id, chatid, "chat"))
        return "✔ 已清除本聊天的长期记忆 ~"
    mine = await list_memories(memory_scope(user_id, chatid))
    shared = await list_memories(memory_scope(user_id, chatid, "chat"))
    def format_memories(rows):
        return "\n".join(f"- `{item['topic']}`: {item['content']}" for item in rows) or "(无)"
    return (
        f"🧠 你的长期记忆:\n{format_memories(mine)}\n\n"
        f"💬 本聊天的长期记忆:\n{format_memories(shared)}\n\n"
        "使用方法:\n\n`/memory clear 清除你的记忆`\n`/memory clear chat 清除本聊天的记忆[管理员]`"
    )

async def set_topic(chatid, topic: str, content: str):
    """
    传入 chatid, topic, content
    以 chatid 作为表名，不存在则创建
    如果 topic 已存在，则更新 content
    否则添加到表最后
    """
    table = quote_table_name(chatid)
    await topic_db.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            topic TEXT NOT NULL UNIQUE,
            content TEXT NOT NULL
        )
    """)
    await topic_db.execute(f"""
        INSERT INTO {table} (topic, content)
        VALUES (?, ?)
        ON CONFLICT(topic) DO UPDATE SET
            content = excluded.content
    """, (topic, content))
    await topic_db.commit()
async def get_topics(chatid) -> list[dict]:
    """
    传入 chatid
    获取该表内所有 topic 和 content
    如果表不存在，返回空列表
    """
    table = quote_table_name(chatid)
    async with topic_db.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (str(chatid),)
    ) as cursor:
        exists = await cursor.fetchone()
    if not exists:
        return []
    async with topic_db.execute(
        f"SELECT topic, content FROM {table} ORDER BY rowid"
    ) as cursor:
        rows = await cursor.fetchall()
    return [
        {
            "topic": row["topic"],
            "content": row["content"]
        }
        for row in rows
    ]
async def delete_topic(chatid, topic: str):
    """
    传入 chatid, topic
    删除该表内 topic 为传入值的行
    如果表不存在则什么都不做
    """
    table = quote_table_name(chatid)
    async with topic_db.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (str(chatid),)
    ) as cursor:
        exists = await cursor.fetchone()
    if not exists:
        return
    await topic_db.execute(
        f"DELETE FROM {table} WHERE topic = ?",
        (topic,)
    )
    await topic_db.commit()

predefined = """function get(data, path, defaults) {
    defaults = (typeof defaults !== 'undefined') ? defaults : null;
    var paths = path.split('.');
    for (var i = 0; i < paths.length; i++) {
        if (data === null || data === undefined) return defaults;
        data = data[paths[i]];
    }
	if (data === null || data === undefined) return defaults;
    return data;
}

function __json_stringify(data) {
	try {
		return JSON.stringify(data);
	} catch (err) { return ''; }
}

function __json_parse(data) {
	try {
		return JSON.parse(data);
	} catch (err) { return {}; }
}

function __netloc_parse(data) {
    try {
        data = data.replace('https://', '').replace('http://', '');
		if (data.indexOf('.') != -1) {
            data = data.split(':')[0].split('/')[0];
        }
        return data;
	} catch (err) { return ''; }
}

const safeStringify = __json_stringify;
const safeParse = __json_parse;
const netlocParse = __netloc_parse;

"""

def js2pystr(s):
    return str(s).lstrip("'").rstrip("'")

async def get_fetch_req(method, body, noredir, retry_time, timeout, headers, url, round):
    try:
        proxy = get_proxy()
        async with AsyncSession(impersonate="chrome", timeout=timeout) as session:
            if method.upper() == "POST":
                res = await session.post(url, headers=headers, data=body, allow_redirects=not noredir, proxy=proxy)
            else:
                res = await session.get(url, headers=headers, allow_redirects=not noredir, proxy=proxy)
            content = res.text
            return content, res
    except:
        if round >= retry_time:
            return None, None
        return await get_fetch_req(method, body, noredir, retry_time, timeout, headers, url, round + 1)

def fetch_url(temp_url, temp_params):
    try:
        params = {}
        for item in temp_params:
            params[js2pystr(item)] = temp_params[item]
        url = js2pystr(temp_url)
        method = js2pystr(params.get('method', 'GET'))
        body = js2pystr(params.get('body', None))
        try:
            noredir = js2pystr(params.get('noRedir', False))
            noredir = noredir.lower() == "true" or noredir == "1"
        except:
            noredir = False
        try:
            retry_time = int(js2pystr(params.get('retry', '0')))
        except:
            retry_time = 0
        try:
            timeout = int(js2pystr(params.get('timeout', '3000')))
        except:
            timeout = 3000
        headers = {}
        if params.get('headers', None) is not None:
            for item in params['headers']:
                headers[js2pystr(item)] = js2pystr(params['headers'][item])
        if headers == {}:
            headers = {
                'User-Agent': config.config['Network']['OverridedUA']
            }
        loop = asyncio.get_running_loop()
        content, res = loop.run_until_complete(get_fetch_req(method, body, noredir, retry_time, timeout, headers, url, 0))
        try:
            content = {
                "status": res.reason,
                "statusCode": res.status_code,
                "cookies": "; ".join(f"{k}={v}" for k, v in res.cookies.items()),
                "headers": dict(res.headers),
                "redirects": res.history,
                "method": res.request.method,
                "url": str(res.url),
                "body": content,
            }
        except:
            content = {
                'method': method,
                'url': url,
            }
        return content
    except Exception as e:
        return {'Exception': e}

def executejscode(content, data):
    func = js2py.EvalJs()
    func.fetch = fetch_url
    func.execute(predefined + content)
    try:
        result = func.handler(data)
    except Exception as e:
        result = f"Execute Failed: {e}"
    if result is None:
        result = "No Response"
    if hasattr(result, 'to_dict'):
        result = result.to_dict()
    elif hasattr(result, 'to_list'):
        result = result.to_list()
    return str(result)

async def tool_web_fetch(url: str) -> str:
    if not url:
        return "Error: No URL provided."
    try:
        fetch_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Cache-Control": "max-age=0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Priority": "u=0, i",
            "Sec-Ch-Ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": config.config['Network']['OverridedUA']
        }
        content, res = await get_fetch_req(
            method="GET",
            body=None,
            noredir=False,
            retry_time=config.config['Network']['Retry'],
            timeout=config.config['Network']['Timeout'],
            headers=fetch_headers,
            url=url,
            round=0,
        )
        if content is None:
            return f"Error: Failed to fetch {url} after retries."

        content_type = res.headers.get("content-type", "") if res else ""
        if "text/html" in content_type:
            soup = BeautifulSoup(content, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            if len(text) > 15000:
                text = text[:15000] + "\n...[content truncated]"
            return f"Fetched content from {url}:\n\n{text}"
        else:
            if len(content) > 15000:
                content = content[:15000] + "\n...[content truncated]"
            return f"Fetched content from {url} (type: {content_type}):\n\n{content}"
    except Exception as e:
        return f"Error fetching {url}: {str(e)}"

async def tool_web_search_tavily(query: str) -> str:
    if not query:
        return False, "Error: No query provided."
    logger.info(f"Use Tavily Search {query}")
    try:
        search_url = "https://api.tavily.com/search"
        fetch_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        body = json.dumps({
            "api_key": config.config['AI']['Tool']['WebSearch']['ApiKey'],
            "query": query,
            "search_depth": "basic",
            "include_answer": True,
            "include_raw_content": False,
            "max_results": 8,
        })
        content, res = await get_fetch_req(
            method="POST",
            body=body,
            noredir=False,
            retry_time=config.config['Network']['Retry'],
            timeout=config.config['Network']['Timeout'],
            headers=fetch_headers,
            url=search_url,
            round=0,
        )
        if content is None:
            return False, f"Error: Tavily search request failed after retries."
        data = json.loads(content)
        parts = []
        # Tavily 直接给的总结答案
        answer = data.get("answer")
        if answer:
            parts.append(f"Summary: {answer}")
        # 搜索结果列表
        results = data.get("results", [])
        for i, r in enumerate(results):
            title = r.get("title", "No title")
            url = r.get("url", "")
            snippet = r.get("content", "No content")
            score = r.get("score", 0)
            entry = f"{i+1}. {title}\n   URL: {url}\n   Relevance: {score:.2f}\n   {snippet}"
            parts.append(entry)
        if parts:
            return True, f"Search results for '{query}':\n\n" + "\n\n".join(parts)
        else:
            return False, f"No results found for '{query}'."
    except json.JSONDecodeError:
        return False, f"Error: Failed to parse Tavily response."
    except Exception as e:
        return False, f"Search error: {str(e)}"

async def tool_web_search_duck_duck_go(query: str) -> str:
    if not query:
        return False, "Error: No query provided."
    logger.info(f"Use DuckDuckGo Search {query}")
    try:
        search_url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote_plus(query)
        fetch_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Cache-Control": "max-age=0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://html.duckduckgo.com",
            "Priority": "u=0, i",
            "Referer": "https://html.duckduckgo.com/",
            "Sec-Ch-Ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
        }
        content, res = await get_fetch_req(
            method="GET",
            body=None,
            noredir=False,
            retry_time=config.config['Network']['Retry'],
            timeout=config.config['Network']['Timeout'],
            headers=fetch_headers,
            url=search_url,
            round=0,
        )
        if content is None:
            return False, f"Error: DuckDuckGo Search request failed after retries."
        soup = BeautifulSoup(content, "html.parser")
        results = []
        for i, result in enumerate(soup.select(".result")):
            if i >= 8:
                break
            title_tag = result.select_one(".result__title a, .result__a")
            snippet_tag = result.select_one(".result__snippet")
            url_tag = result.select_one(".result__url")
            title = title_tag.get_text(strip=True) if title_tag else "No title"
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else "No snippet"
            link = ""
            if title_tag and title_tag.get("href"):
                link = title_tag["href"]
            elif url_tag:
                link = url_tag.get_text(strip=True)
            try:
                link = urllib.parse.unquote(link.replace('//duckduckgo.com/l/?uddg=', '').split('&rut=')[0])
            except:
                pass
            results.append(f"{i+1}. {title}\n   URL: {link}\n   {snippet}")
        if results:
            return True, f"DuckDuckGo Search results for '{query}':\n\n" + "\n\n".join(results)
        else:
            return False, f"No DuckDuckGo results found for '{query}'."
    except Exception as e:
        return False, f"DuckDuckGo Search error: {str(e)}"

async def tool_web_search(query: str):
    web_search_func = [tool_web_search_duck_duck_go, tool_web_search_tavily]
    for wbfunc in web_search_func:
        search_flag, result = await wbfunc(query)
        if search_flag == True:
            return result
    result = f"No results found for '{query}'"
    return result

async def execute_tool_call(tool_name: str, tool_args: dict, user_id=None, chatid=None) -> str:
    try:
        if tool_name == "web_fetch":
            return await tool_web_fetch(tool_args.get("url", ""))
        elif tool_name == "web_search":
            return await tool_web_search(tool_args.get("query", ""))
        elif tool_name == "executejscode":
            return executejscode(tool_args.get("content", ""), tool_args.get("data", ""))
        elif tool_name == "memory_save":
            topic = str(tool_args.get("topic", "")).strip()[:100]
            content = str(tool_args.get("content", "")).strip()[:2000]
            if not topic or not content:
                return "Error: topic and content are required."
            await save_memory(memory_scope(user_id, chatid, tool_args.get("scope", "user")), topic, content)
            return f"Saved memory '{topic}'."
        elif tool_name == "memory_delete":
            topic = str(tool_args.get("topic", "")).strip()[:100]
            if not topic:
                return "Error: topic is required."
            deleted = await delete_memory(memory_scope(user_id, chatid, tool_args.get("scope", "user")), topic)
            return "Deleted." if deleted else "No such memory."
        else:
            return f"Unknown tool: {tool_name}"
    except Exception as e:
        return f"Tool execution error: {str(e)}"

def get_reasoning_effort_name(name):
    effort_name = {
        "auto": "默认",
        "none": "关闭",
        "minimal": "最小",
        "low": "低",
        "medium": "中",
        "high": "高",
        "xhigh": "极高"
    }
    return effort_name.get(name, effort_name[config.config['AI']['ReasoningEffort']])

def get_proxy():
    global proxy_pos
    proxy = None
    if not config.config['Network']['Proxy'] is None:
        proxy = config.config['Network']['Proxy'][proxy_pos]
        if proxy_pos + 1 == len(config.config['Network']['Proxy']):
            proxy_pos = 0
        else:
            proxy_pos = 1
    return proxy

def set_config(data: dict, pos: list, value):
    if len(pos) == 1:
        data[pos[0]] = value
    else:
        data[pos[0]] = set_config(data[pos[0]], pos[1:], value)
    return data

def rm_config(data: dict, pos: list, idt):
    if len(pos) == 1:
        data[pos[0]] = data[pos[0]][:idt] + data[pos[0]][idt + 1:]
    else:
        data[pos[0]] = rm_config(data[pos[0]], pos[1:], idt)
    return data

def add_config(data: dict, pos: list, value):
    if len(pos) == 1:
        data[pos[0]].append(value)
    else:
        data[pos[0]] = add_config(data[pos[0]], pos[1:], value)
    return data

async def deletecommand(msg, message, t: int):
    await asyncio.sleep(t)
    try:
        await app.delete_messages(msg.chat.id, msg.id)
    except:
        pass
    try:
        await app.delete_messages(message.chat.id, message.id)
    except:
        pass

async def reloadbot():
    global admin_list, su_admin_list
    admin_list = config.LoadAdmin()
    su_admin_list = config.LoadSuAdmin()
    get_model_list()
    if config.config['Bot']['HideCommand'] == False:
        await app.set_bot_commands([
            BotCommand("help", "获取帮助菜单"), 
            BotCommand("version", f"获取版本信息 - {version_content} ({version_id})"),
            BotCommand("stats", "获取权限状态"),
            BotCommand("chat", "发送聊天内容"),
            BotCommand("model", "修改聊天模型"),
            BotCommand("prune", "测试模型可用性"),
            BotCommand("clear", "清除上下文记录"),
            BotCommand("memory", "查看或清除记忆"),
            BotCommand("effort", "设置思维链深度"),
            BotCommand("prompt", "设置系统提示词"),
            BotCommand("context", "开关上下文记录"),
        ])
    else:
        await app.set_bot_commands([])

@app.on_message(filters.command(['help']))
async def help_bot(client: Client, message: Message):
    logger.info(f"{str(message.from_user.id)} Get Help")
    content = f"欢迎使用 `{bot_me.first_name}` 呢 你可以使用以下指令呢 ~\n\n/help `获取帮助菜单`\n/version `获取版本信息 - {version_content} ({version_id})`\n/stats `获取权限状态`"
    if message.from_user.id in admin_list:
        content = content + "\n/chat `[管理]发送聊天内容`\n/model `[管理]修改聊天模型`\n/prune `[管理]测试模型可用性`\n/clear `[管理]清除上下文记录`\n/memory `[管理]查看或清除记忆`\n/effort `[管理]设置思维链深度`\n/prompt `[管理]设置系统提示词`\n/context `[管理]开关上下文记录`"
    if message.from_user.id in su_admin_list:
        content = content + "\n/trust `[超管]添加白名单群组`\n/distrust `[超管]删除白名单群群组`\n/grant `[超管]授权一个用户`\n/ungrant `[超管]取消用户授权`\n/grantscan `[超管]扫描清理授权`\n/stop `[超管]停止运行程序`"
    msg = await client.send_message(chat_id = message.chat.id, text = content, reply_parameters = ReplyParameters(message_id = message.id))
    if not message.chat.type == pyrogram.enums.ChatType.PRIVATE:
        await deletecommand(msg, message, 10)

@app.on_message(filters.command(['version']))
async def get_version(client: Client, message: Message):
    logger.info(f"{str(message.from_user.id)} Get Version")
    cont = f"Version: `{version_content} ({str(version_id)})`\nSource: `{version_source}`"
    msg = await client.send_message(chat_id = message.chat.id, text = cont, reply_parameters = ReplyParameters(message_id = message.id))
    await deletecommand(msg, message, 10)

@app.on_message(filters.command(['stats']))
async def get_stats(client: Client, message: Message):
    logger.info(f"{str(message.from_user.id)} Get Stats")
    content = "你当前的权限状态是:\n\n管理权限: "
    if int(message.from_user.id) in admin_list:
        content = content + "✔"
    else:
        content = content + "❌"
    content = content + "\n超管权限: "
    if int(message.from_user.id) in su_admin_list:
        content = content + "✔"
    else:
        content = content + "❌"
    if int(message.from_user.id) in su_admin_list:
        content = content + f"\n\n超管数量: `{len(su_admin_list)}`" + f"\n管理数量: `{len(admin_list) - len(su_admin_list)}`\n模型数量: `{len(list(model_list.keys()))}`\n群组数量: `{len(config.config['AI']['WhiteList']):}`"
    if int(message.from_user.id) in admin_list:
        #topics = await get_topics(message.chat.id)
        contexts = await get_chat(message.chat.id)
        content = content + f"\n\n当前对话数量: `{len(contexts)}`" #+ f"\n当前话题数量: `{len(topics)}`"
        content = content + "\n\n上下文记录: "
        if config.config['User'][message.from_user.id]['Context'] == True:
            content = content + "✔"
        else:
            content = content + "❌"
        content = content + "\n长期记忆: "
        if config.config['AI']['Memory']['Enable'] == True:
            content = content + "✔"
        else:
            content = content + "❌"
        content = content + f"\n当前模型: `{config.config['User'][message.from_user.id]['Model']}`\n默认模型: `{config.config['AI']['DefaultModel']}`\n当前思维链深度: `{get_reasoning_effort_name(config.config['User'][message.from_user.id]['ReasoningEffort'])}`\n默认思维链深度: `{get_reasoning_effort_name(config.config['AI']['ReasoningEffort'])}`\n\n网络搜索: "
        if config.config['AI']['Tool']['Enable'] == True and config.config['AI']['Tool']['WebSearch']['Enable'] == True:
            content = content + "✔"
        else:
            content = content + "❌"
        content = content + "\n链接请求: "
        if config.config['AI']['Tool']['Enable'] == True and config.config['AI']['Tool']['FetchURL']['Enable'] == True:
            content = content + "✔"
        else:
            content = content + "❌"
        content = content + "\n代码执行: "
        if config.config['AI']['Tool']['Enable'] == True and config.config['AI']['Tool']['JSExecution']['Enable'] == True:
            content = content + "✔"
        else:
            content = content + "❌"
        content = content + "\n文件读取: "
        if config.config['AI']['FileSupport'] == True:
            content = content + "✔"
        else:
            content = content + "❌"
    msg = await client.send_message(chat_id = message.chat.id, text = content, reply_parameters = ReplyParameters(message_id = message.id))
    await deletecommand(msg, message, 10)

#@app.on_message(filters.command(['ping']))
async def pub_ping(client: Client, message: Message):
    if not int(message.from_user.id) in admin_list:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限呢 请联系超管授权 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    logger.info(f"{str(message.from_user.id)} Ping Bot")
    try:
        start = time.time() * 1000
        msg = await client.send_message(chat_id = message.chat.id, text = f"✔ Ping:", reply_parameters = ReplyParameters(message_id = message.id))
        end = time.time() * 1000
        msg_delay = (end-start)
        start = time.time() * 1000
        await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = f"✔ Ping: `{msg_delay:.2f}ms`")
        end = time.time() * 1000
        msg_delay = (msg_delay + (end-start)) / 2
        start = time.time() * 1000
        await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = f"✔ Ping: `{msg_delay:.2f}ms`")
        end = time.time() * 1000
        msg_delay = (msg_delay + (end-start)) / 2
        await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = f"✔ Ping: `{msg_delay:.2f}ms`")
        await deletecommand(msg, message, 10)
    except Exception as e:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 测试延迟失败呢 ~\n\n错误: `{e}`", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)

def message_has_image(message: Message) -> bool:
    if message.photo:
        if message.photo.file_size >= config.config['AI']['MaxFileSize']  * 1024 * 1024:
            return False
        return True
    if message.document and message.document.mime_type and message.document.mime_type.startswith("image/"):
        if message.document.file_size >= config.config['AI']['MaxFileSize']  * 1024 * 1024:
            return False
        return True
    if message.sticker:
        if message.sticker.file_size >= config.config['AI']['MaxFileSize']  * 1024 * 1024:
            return False
        return True
    return False

def message_has_file(message: Message) -> bool:
    if config.config['AI']['FileSupport'] == False:
        return False
    if message.document:
        if message.document.file_size >= config.config['AI']['MaxFileSize']  * 1024 * 1024:
            return False
        return True
    return False

async def get_media_group_messages(client: Client, message: Message) -> list[Message]:
    """获取 media group 中的所有消息"""
    if not message.media_group_id:
        return [message]
    try:
        group_messages = await client.get_media_group(message.chat.id, message.id)
        return group_messages
    except:
        return [message]

def detect_mime(b64_data: str, message: Message) -> str:
    if message.document and message.document.mime_type:
        return message.document.mime_type
    raw = base64.b64decode(b64_data[:32])
    if raw[:8] == b'\x89PNG\r\n\x1a\n':
        return "image/png"
    if raw[:2] == b'\xff\xd8':
        return "image/jpeg"
    if raw[:4] == b'RIFF' and raw[8:12] == b'WEBP':
        return "image/webp"
    if raw[:3] == b'GIF':
        return "image/gif"
    if message.document and message.document.file_name:
        mime_type, _ = mimetypes.guess_type(message.document.file_name)
        return mime_type
    return "image/jpeg"

async def ai_send_chat(client: Client, message: Message, send_text):
    files = []
    reply_files = []
    have_file = False
    msg = None
    identifier = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_', k=10))
    if message_has_image(message) or message_has_file(message):
        current_files = []
        group_msgs = await get_media_group_messages(client, message)
        for gmsg in group_msgs:
            if stop_generate_flag.get(identifier, False):
                break
            if message_has_image(gmsg):
                if have_file == False:
                    have_file = True
                    msg = await client.send_message(chat_id = message.chat.id, text = f"⏳ 获取图片中 ...", reply_parameters = ReplyParameters(message_id = message.id), reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]))
                try:
                    buf = await client.download_media(gmsg, in_memory=True)
                    buf.seek(0)
                    img_content = base64.b64encode(buf.read()).decode("utf-8")
                    current_files.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{detect_mime(img_content, gmsg)};base64,{img_content}"
                        }
                    })
                except:
                    pass
            elif message_has_file(gmsg):
                if have_file == False:
                    have_file = True
                    msg = await client.send_message(chat_id = message.chat.id, text = f"⏳ 获取文件中 ...", reply_parameters = ReplyParameters(message_id = message.id), reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]))
                try:
                    buf = await client.download_media(gmsg, in_memory=True)
                    buf.seek(0)
                    file_content = base64.b64encode(buf.read()).decode("utf-8")
                    if gmsg.document and gmsg.document.file_name:
                        file_name = gmsg.document.file_name
                    else:
                        file_name = "file"
                    current_files.append({
                        "type": "file",
                        "file": {
                            "filename": file_name,
                            "file_data": f"data:{detect_mime(file_content, gmsg)};base64,{file_content}"
                        }
                    })
                except:
                    pass
        files.extend(current_files)
    if stop_generate_flag.get(identifier, False) == True:
        del stop_generate_flag[identifier]
        if msg:
            await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = f"❌ 获取消息失败呢 ~")
        else:
            await client.send_message(chat_id = message.chat.id, text = f"❌ 获取消息失败呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
        return
    if message.reply_to_message and message.reply_to_message.from_user.is_self == False:
        current_files = []
        group_msgs = await get_media_group_messages(client, message.reply_to_message)
        for gmsg in group_msgs:
            if stop_generate_flag.get(identifier, False):
                break
            if message_has_image(gmsg):
                if have_file == False:
                    have_file = True
                    msg = await client.send_message(chat_id = message.chat.id, text = f"⏳ 获取图片中 ...", reply_parameters = ReplyParameters(message_id = message.id), reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]))
                try:
                    buf = await client.download_media(gmsg, in_memory=True)
                    buf.seek(0)
                    img_content = base64.b64encode(buf.read()).decode("utf-8")
                    current_files.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{detect_mime(img_content, gmsg)};base64,{img_content}"
                        }
                    })
                except:
                    pass
            elif message_has_file(gmsg):
                if have_file == False:
                    have_file = True
                    msg = await client.send_message(chat_id = message.chat.id, text = f"⏳ 获取文件中 ...", reply_parameters = ReplyParameters(message_id = message.id), reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]))
                try:
                    buf = await client.download_media(gmsg, in_memory=True)
                    buf.seek(0)
                    file_content = base64.b64encode(buf.read()).decode("utf-8")
                    if gmsg.document and gmsg.document.file_name:
                        file_name = gmsg.document.file_name
                    else:
                        file_name = "file"
                    current_files.append({
                        "type": "file",
                        "file": {
                            "filename": file_name,
                            "file_data": f"data:{detect_mime(file_content, gmsg)};base64,{file_content}"
                        }
                    })
                except:
                    pass
        reply_files.extend(current_files)
    if stop_generate_flag.get(identifier, False) == True:
        del stop_generate_flag[identifier]
        if msg:
            await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = f"❌ 获取消息失败呢 ~")
        else:
            await client.send_message(chat_id = message.chat.id, text = f"❌ 获取消息失败呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
        return
    user_text = safe_ai_text(send_text)
    reply_content = None
    if len(files) == 0:
        if config.config['AI']['IDRecognition']['Enable'] == True and message.chat.type != pyrogram.enums.ChatType.PRIVATE:
            user_name = message.from_user.first_name
            if message.from_user.last_name:
                user_name += message.from_user.last_name
            user_name = safe_ai_text(user_name)
            user_content = config.config['AI']['IDRecognition']['Format'].format_map(SafeFormatDict(name=user_name, content=user_text))
        else:
            user_content = user_text
    else:
        if config.config['AI']['IDRecognition']['Enable'] == True and message.chat.type != pyrogram.enums.ChatType.PRIVATE:
            user_name = message.from_user.first_name
            if message.from_user.last_name:
                user_name += message.from_user.last_name
            user_name = safe_ai_text(user_name)
            user_content = [{"type": "text", "text": config.config['AI']['IDRecognition']['Format'].format_map(SafeFormatDict(name=user_name, content=user_text))}]
        else:
            user_content = [{"type": "text", "text": user_text}]
        user_content.extend(files)
    if message.reply_to_message and message.reply_to_message.from_user.is_self == False:
        reply_send_text = ""
        if message.reply_to_message.text:
            reply_send_text = message.reply_to_message.text
        elif message.reply_to_message.caption:
            reply_send_text = message.reply_to_message.caption
        reply_send_text = safe_ai_text(reply_send_text)
        if len(reply_send_text) != 0:
            if len(reply_files) == 0:
                if config.config['AI']['IDRecognition']['Enable'] == True and message.chat.type != pyrogram.enums.ChatType.PRIVATE:
                    user_name = message.reply_to_message.from_user.first_name
                    if message.reply_to_message.from_user.last_name:
                        user_name += message.reply_to_message.from_user.last_name
                    user_name = safe_ai_text(user_name)
                    reply_content = config.config['AI']['IDRecognition']['Format'].format_map(SafeFormatDict(name=user_name, content=reply_send_text))
                else:
                    reply_content = reply_send_text
            else:
                if config.config['AI']['IDRecognition']['Enable'] == False or message.chat.type == pyrogram.enums.ChatType.PRIVATE:
                    user_name = message.reply_to_message.from_user.first_name
                    if message.reply_to_message.from_user.last_name:
                        user_name += message.reply_to_message.from_user.last_name
                    user_name = safe_ai_text(user_name)
                    reply_content = [{"type": "text", "text": config.config['AI']['IDRecognition']['Format'].format_map(SafeFormatDict(name=user_name, content=reply_send_text))}]
                else:
                    reply_content = [{"type": "text", "text": reply_send_text}]
                reply_content.extend(reply_files)
        elif len(reply_files) != 0:
            reply_content = reply_files
    systemprompt = config.config['User'].get(message.from_user.id, {}).get('SystemPrompt', config.config['AI']['SystemPrompt'])
    use_model = config.config['User'].get(message.from_user.id, {}).get('Model', config.config['AI']['DefaultModel'])
    if use_model not in list(model_list.keys()):
        use_model = config.config['AI']['DefaultModel']
    reasoneffort = config.config['User'].get(message.from_user.id, {}).get('ReasoningEffort', config.config['AI']['ReasoningEffort'])
    if reasoneffort == "":
        reasoneffort = config.config['AI']['ReasoningEffort']
    ai_url = f"{config.config['AI']['Vendor'][model_list[use_model]]['BaseUrl'].rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.config['AI']['Vendor'][model_list[use_model]]['Key']}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    ai_messages = []
    if len(systemprompt) == 0:
        systemprompt = config.config['AI']['SystemPrompt']
    if len(config.config['AI']['ExtraSystemPrompt']) != 0:
        ai_messages.append({"role": "system", "content": config.config['AI']['ExtraSystemPrompt'].format_map(SafeFormatDict(cur_date=datetime.datetime.now().strftime("%Y-%m-%d"), cur_time=datetime.datetime.now().strftime("%H:%M:%S"), cur_datetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), model_name=use_model.split(':', 1)[1] if ':' in use_model else use_model, assistant_name=bot_me.first_name))})
    if config.config['AI']['IDRecognition']['Enable'] == True and len(config.config['AI']['IDRecognition']['Prompt']) != 0:
        ai_messages.append({"role": "system", "content": config.config['AI']['IDRecognition']['Prompt']})
    if len(systemprompt) != 0:
        ai_messages.append({"role": "system", "content": systemprompt})
    if config.config['AI']['Memory']['Enable'] == True:
        memory_prompt = await get_memory_prompt(message.from_user.id, message.chat.id)
        if memory_prompt:
            ai_messages.append({"role": "system", "content": memory_prompt})
    if config.config['User'].get(message.from_user.id, {}).get('Context', True) == True or message.chat.type != pyrogram.enums.ChatType.PRIVATE:
        await keep_last_chat(message.chat.id, config.config['AI']['MaxContext'])
        contexts = await get_chat(message.chat.id)
        for ctext in contexts:
            his_content = ctext['content']
            try:
                his_content = json.loads(his_content)
            except:
                pass
            if ctext['name'] in ['user', 'assistant']:
                ai_messages.append({"role": ctext['name'], "content": his_content})
            else:
                if config.config['AI']['IDRecognition']['Enable'] == True and message.chat.type != pyrogram.enums.ChatType.PRIVATE:
                    ai_messages.append({"role": "user", "content": config.config['AI']['IDRecognition']['Format'].format_map(SafeFormatDict(name=ctext['name'], content=his_content))})
                else:
                    ai_messages.append({"role": "user", "name": ctext['name'], "content": his_content})
    if message.reply_to_message and message.reply_to_message.from_user.is_self == False:
        if config.config['AI']['IDRecognition']['Enable'] == True or message.chat.type == pyrogram.enums.ChatType.PRIVATE:
            user_name = "user"
            ai_messages.append({"role": "user", "content": reply_content})
        else:
            user_name = message.reply_to_message.from_user.first_name
            if message.reply_to_message.from_user.last_name:
                user_name += message.reply_to_message.from_user.last_name
            user_name = safe_ai_text(user_name)
            ai_messages.append({"role": "user", "name": user_name, "content": reply_content})
    if config.config['AI']['IDRecognition']['Enable'] == True or message.chat.type == pyrogram.enums.ChatType.PRIVATE:
        user_name = "user"
        ai_messages.append({"role": "user", "content": user_content})
    else:
        user_name = message.from_user.first_name
        if message.from_user.last_name:
            user_name += message.from_user.last_name
        user_name = safe_ai_text(user_name)
        ai_messages.append({"role": "user", "name": user_name, "content": user_content})
    used_tools = []
    if config.config['AI']['Tool']['Enable'] == True and config.config['AI']['Tool']['WebSearch']['Enable'] == True:
        used_tools.append(TOOLS_DEFINITION['web_search'])
    if config.config['AI']['Tool']['Enable'] == True and config.config['AI']['Tool']['FetchURL']['Enable'] == True:
        used_tools.append(TOOLS_DEFINITION['web_fetch'])
    if config.config['AI']['Tool']['Enable'] == True and config.config['AI']['Tool']['JSExecution']['Enable'] == True:
        used_tools.append(TOOLS_DEFINITION['executejscode'])
    if config.config['AI']['Memory']['Enable'] == True:
        used_tools.extend([TOOLS_DEFINITION['memory_save'], TOOLS_DEFINITION['memory_delete']])
    if ":" in use_model:
        use_model = use_model.split(':')[1]
    if len(used_tools) == 0:
        payload = {
            "model": use_model,
            "messages": ai_messages,
            "stream": True,
        }
    else:
        payload = {
            "model": use_model,
            "messages": ai_messages,
            "stream": True,
            "tools": used_tools,
            "tool_choice": "auto",
        }
    if reasoneffort not in ['', 'auto']:
        payload['reasoning_effort'] = reasoneffort
    max_tool_rounds = config.config['AI']['Tool']['MaxToolCall']
    logger.info(f"Admin {str(message.from_user.id)} Use Model {use_model}")
    valid_tool_names = set()
    for tool in used_tools:
        try:
            valid_tool_names.add(tool["function"]["name"])
        except Exception:
            pass
    def create_tool_collector():
        """
        每一轮 stream 单独创建一个 tool collector。
        重点：
        1. 优先按 tool_call id 分流
        2. id 缺失时再按 index
        3. index 异常重复时，不把不同 id 的 tool call 拼一起
        """
        tool_calls_map = {}
        id_to_key = {}
        index_to_key = {}
        last_tool_key = None
        def new_key():
            return len(tool_calls_map)
        def create_tool_call(key, tc_id="", tc_type="function"):
            tool_calls_map[key] = {
                "id": tc_id or "",
                "type": tc_type or "function",
                "function": {
                    "name": "",
                    "arguments": "",
                },
            }
        def get_tool_key(tc_delta: dict):
            nonlocal last_tool_key
            tc_id = tc_delta.get("id")
            idx = tc_delta.get("index")
            tc_type = tc_delta.get("type", "function")
            # 最可靠：有 id 就按 id 分
            if tc_id:
                if tc_id in id_to_key:
                    key = id_to_key[tc_id]
                else:
                    key = new_key()
                    create_tool_call(key, tc_id=tc_id, tc_type=tc_type)
                    id_to_key[tc_id] = key
                    # index 只作为辅助。
                    # 如果 index 已经被别的 id 占了，不复用，避免 web_searchweb_fetch。
                    if idx is not None:
                        old_key = index_to_key.get(idx)
                        if old_key is None:
                            index_to_key[idx] = key
                        else:
                            old_id = tool_calls_map.get(old_key, {}).get("id", "")
                            if old_id == tc_id:
                                index_to_key[idx] = key
                last_tool_key = key
                return key
            # 没 id，有 index
            if idx is not None:
                if idx in index_to_key:
                    key = index_to_key[idx]
                else:
                    key = new_key()
                    create_tool_call(key, tc_id="", tc_type=tc_type)
                    index_to_key[idx] = key
                last_tool_key = key
                return key
            # id/index 都没有，只能续到上一个
            if last_tool_key is not None:
                return last_tool_key
            key = new_key()
            create_tool_call(key, tc_id="", tc_type=tc_type)
            last_tool_key = key
            return key
        def append_tool_delta(tc_delta: dict):
            key = get_tool_key(tc_delta)
            if key not in tool_calls_map:
                create_tool_call(key)
            if tc_delta.get("id"):
                tool_calls_map[key]["id"] = tc_delta["id"]
                id_to_key[tc_delta["id"]] = key
            if tc_delta.get("type"):
                tool_calls_map[key]["type"] = tc_delta["type"]
            func_delta = tc_delta.get("function", {}) or {}
            name_part = func_delta.get("name")
            args_part = func_delta.get("arguments")
            if name_part:
                tool_calls_map[key]["function"]["name"] += name_part
            if args_part:
                tool_calls_map[key]["function"]["arguments"] += args_part
        def split_json_objects(text: str):
            result = []
            decoder = json.JSONDecoder()
            pos = 0
            while pos < len(text):
                while pos < len(text) and text[pos].isspace():
                    pos += 1
                if pos >= len(text):
                    break
                try:
                    obj, end = decoder.raw_decode(text, pos)
                    result.append(json.dumps(obj, ensure_ascii=False))
                    pos = end
                except Exception:
                    return []
            return result
        def split_tool_name_sequence(name: str):
            """
            处理这种情况：
            web_searchweb_fetch -> ["web_search", "web_fetch"]
            """
            if not valid_tool_names:
                return []
            names = sorted(valid_tool_names, key=len, reverse=True)
            remain = name
            result = []
            while remain:
                matched = False
                for tool_name in names:
                    if remain.startswith(tool_name):
                        result.append(tool_name)
                        remain = remain[len(tool_name):]
                        matched = True
                        break
                if not matched:
                    return []
            return result
        def normalize_tool_calls():
            raw_list = []
            for key in sorted(tool_calls_map.keys()):
                tc = tool_calls_map[key]
                name = tc.get("function", {}).get("name", "")
                arguments = tc.get("function", {}).get("arguments", "")
                if not name and not arguments:
                    continue
                if not tc.get("id"):
                    tc["id"] = f"call_local_{key}"
                raw_list.append(tc)
            normalized = []
            for tc in raw_list:
                name = tc["function"]["name"]
                arguments = tc["function"]["arguments"]
                # 正常工具名，直接保留
                if not valid_tool_names or name in valid_tool_names:
                    normalized.append(tc)
                    continue
                # 尝试拆开 web_searchweb_fetch
                name_parts = split_tool_name_sequence(name)
                arg_parts = split_json_objects(arguments)
                if len(name_parts) >= 2 and len(name_parts) == len(arg_parts):
                    for i, tool_name in enumerate(name_parts):
                        normalized.append({
                            "id": tc["id"] if i == 0 else f"{tc['id']}_split_{i}",
                            "type": tc.get("type", "function"),
                            "function": {
                                "name": tool_name,
                                "arguments": arg_parts[i],
                            },
                        })
                else:
                    logger.warning(f"Drop invalid tool call: {tc}")
            # 去重，避免同一个 tool_call 被重复执行
            deduped = []
            seen = set()
            for tc in normalized:
                mark = (
                    tc["function"].get("name", ""),
                    tc["function"].get("arguments", ""),
                )
                if mark in seen:
                    continue
                seen.add(mark)
                deduped.append(tc)
            return deduped
        return append_tool_delta, normalize_tool_calls
    first_send = True
    page_send = False
    draft_finish = False
    last_edit = 0
    edit_count = 0
    retry_time = 0
    brk_toolr = False
    fbmodel_pos = 0
    fallback_model = [config.config['User'].get(message.from_user.id, {}).get('Model', config.config['AI']['DefaultModel'])]
    fallback_model.extend(config.config['AI']['FallbackModel'])
    fallback_model = list(set(fallback_model))
    if have_file:
        await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = f"⏳ 思考中 ...", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]))
        if message.chat.type != pyrogram.enums.ChatType.PRIVATE:
            edit_count += 1
    else:
        msg = await client.send_message(chat_id = message.chat.id, text = f"⏳ 思考中 ...", reply_parameters = ReplyParameters(message_id = message.id), reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]))
    for tool_round in range(max_tool_rounds + 1):
        if brk_toolr == True:
            break
        brk_toolr = False
        while retry_time <= config.config['Network']['Retry']:
            if retry_time >= 1:
                fbmodel_pos += 1
                if fbmodel_pos >= len(fallback_model):
                    fbmodel_pos = 0
                use_model = fallback_model[fbmodel_pos]
                while use_model not in list(model_list.keys()):
                    fbmodel_pos += 1
                    if fbmodel_pos >= len(fallback_model):
                        fbmodel_pos = 0
                    use_model = fallback_model[fbmodel_pos]
                ai_url = f"{config.config['AI']['Vendor'][model_list[use_model]]['BaseUrl'].rstrip('/')}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {config.config['AI']['Vendor'][model_list[use_model]]['Key']}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream",
                }
                if ":" in use_model:
                    use_model = use_model.split(':')[1]
                payload["model"] = use_model
            try:
                full_text = ""
                current_text = ""
                buffer = ""
                draft_id = client.rnd_id()
                append_tool_delta, get_tool_calls_list = create_tool_collector()
                async with AsyncSession(retry=config.config['Network']['Retry']) as session:
                    if tool_round == max_tool_rounds:
                        payload.pop("tools", None)
                        payload.pop("tool_choice", None)
                    async with session.stream(
                        "POST",
                        ai_url,
                        headers=headers,
                        json=payload,
                        timeout=config.config['Network']['Timeout'],
                        impersonate="chrome",
                        proxy=get_proxy(),
                    ) as resp:
                        resp.raise_for_status()
                        async for chunk in resp.aiter_content():
                            if stop_generate_flag.get(identifier, False) == True:
                                await resp.aclose()
                                break
                            if not chunk:
                                continue
                            if isinstance(chunk, bytes):
                                chunk = chunk.decode("utf-8", errors="ignore")
                            buffer += chunk
                            buffer = buffer.replace("\r\n", "\n")
                            while "\n\n" in buffer:
                                raw_event, buffer = buffer.split("\n\n", 1)
                                raw_event = raw_event.strip()
                                if not raw_event:
                                    continue
                                for line in raw_event.splitlines():
                                    line = line.strip()
                                    if not line.startswith("data:"):
                                        continue
                                    data = line[5:].strip()
                                    if data == "[DONE]":
                                        break
                                    try:
                                        choices = json.loads(data).get("choices", [])
                                        if not choices:
                                            continue
                                        delta = choices[0].get("delta", {})
                                        content = choices[0].get("delta", {}).get("content")
                                        if content:
                                            full_text += content
                                            current_text += content
                                            now = time.time()
                                            if message.chat.type == pyrogram.enums.ChatType.PRIVATE:
                                                if first_send == True:
                                                    first_send = False
                                                    await deletecommand(msg, None, 0)
                                                if now - last_edit >= get_delay(edit_count, config.config['AI']['ChunkStrategy']['MaxEdit']) and re.search(config.config['AI']['ChunkStrategy']['Rule'], current_text):
                                                    if len(full_text) > config.config['Other']['MaxTextLength']:
                                                        if page_send == False:
                                                            page_send = True
                                                            msgtext = ""
                                                            for i in full_text[0:config.config['Other']['MaxTextLength']]:
                                                                msgtext = msgtext + i
                                                            leng = len(full_text) // config.config['Other']['MaxTextLength']
                                                            if len(full_text) % config.config['Other']['MaxTextLength'] > 0:
                                                                leng = leng + 1
                                                            view_content[str(msg.chat.id) + str(msg.id)] = full_text
                                                            current_page = 1
                                                            keyboard = []
                                                            keyboard_row = []
                                                            if current_page == 1:
                                                                keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank prev"))
                                                            else:
                                                                keyboard_row.append(InlineKeyboardButton('上一页', callback_data="info jump " + str(current_page - 1)))
                                                            keyboard_row.append(InlineKeyboardButton(f'{current_page} / {leng}', callback_data=f'info page_info {current_page} {leng}'))
                                                            if current_page == leng:
                                                                keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank next"))
                                                            else:
                                                                keyboard_row.append(InlineKeyboardButton('下一页', callback_data="info jump " + str(current_page + 1)))
                                                            keyboard.append(keyboard_row)
                                                            keyboard.append([InlineKeyboardButton('停止', callback_data='stop ' + identifier)])
                                                            msg = await client.send_rich_message(chat_id = message.chat.id, rich_message = InputRichMessage(markdown=msgtext), reply_markup=InlineKeyboardMarkup(keyboard), reply_parameters = ReplyParameters(message_id = message.id))
                                                            generating_content[str(msg.chat.id) + str(msg.id)] = identifier
                                                        else:
                                                            view_content[str(msg.chat.id) + str(msg.id)] = full_text
                                                        edit_count += 1
                                                        last_edit = now
                                                        current_text = ""
                                                    else:
                                                        await client.send_rich_message_draft(message.chat.id, draft_id, InputRichMessage(markdown=full_text))
                                                        edit_count += 1
                                                        last_edit = now
                                                        draft_finish = False
                                                        current_text = ""
                                            else:
                                                if first_send == True:
                                                    first_send = False
                                                if edit_count < config.config['AI']['ChunkStrategy']['MaxEdit'] and now - last_edit >= get_delay(edit_count, config.config['AI']['ChunkStrategy']['MaxEdit']) and re.search(config.config['AI']['ChunkStrategy']['Rule'], current_text):
                                                    if len(full_text) > config.config['Other']['MaxTextLength']:
                                                        if page_send == False:
                                                            page_send = True
                                                            msgtext = ""
                                                            for i in full_text[0:config.config['Other']['MaxTextLength']]:
                                                                msgtext = msgtext + i
                                                            leng = len(full_text) // config.config['Other']['MaxTextLength']
                                                            if len(full_text) % config.config['Other']['MaxTextLength'] > 0:
                                                                leng = leng + 1
                                                            view_content[str(msg.chat.id) + str(msg.id)] = full_text
                                                            current_page = 1
                                                            keyboard = []
                                                            keyboard_row = []
                                                            if current_page == 1:
                                                                keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank prev"))
                                                            else:
                                                                keyboard_row.append(InlineKeyboardButton('上一页', callback_data="info jump " + str(current_page - 1)))
                                                            keyboard_row.append(InlineKeyboardButton(f'{current_page} / {leng}', callback_data=f'info page_info {current_page} {leng}'))
                                                            if current_page == leng:
                                                                keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank next"))
                                                            else:
                                                                keyboard_row.append(InlineKeyboardButton('下一页', callback_data="info jump " + str(current_page + 1)))
                                                            keyboard.append(keyboard_row)
                                                            keyboard.append([InlineKeyboardButton('停止', callback_data='stop ' + identifier)])
                                                            await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, rich_message = InputRichMessage(markdown=msgtext), reply_markup=InlineKeyboardMarkup(keyboard))
                                                            generating_content[str(msg.chat.id) + str(msg.id)] = identifier
                                                        else:
                                                            view_content[str(msg.chat.id) + str(msg.id)] = full_text
                                                        edit_count += 1
                                                        last_edit = now
                                                        current_text = ""
                                                    else:
                                                        await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, rich_message = InputRichMessage(markdown=full_text), reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]))
                                                        edit_count += 1
                                                        last_edit = now
                                                        current_text = ""
                                        tc_deltas = delta.get("tool_calls") or []
                                        for tc_delta in tc_deltas:
                                            try:
                                                append_tool_delta(tc_delta)
                                            except:
                                                pass
                                    except:
                                        pass
                if len(full_text) != 0 and message.chat.type == pyrogram.enums.ChatType.PRIVATE:
                    draft_finish = True
                    if len(full_text) > config.config['Other']['MaxTextLength']:
                        msgtext = ""
                        for i in full_text[0:config.config['Other']['MaxTextLength']]:
                            msgtext = msgtext + i
                        leng = len(full_text) // config.config['Other']['MaxTextLength']
                        if len(full_text) % config.config['Other']['MaxTextLength'] > 0:
                            leng = leng + 1
                        view_content[str(msg.chat.id) + str(msg.id)] = full_text
                        current_page = 1
                        keyboard = []
                        keyboard_row = []
                        if current_page == 1:
                            keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank prev"))
                        else:
                            keyboard_row.append(InlineKeyboardButton('上一页', callback_data="info jump " + str(current_page - 1)))
                        keyboard_row.append(InlineKeyboardButton(f'{current_page} / {leng}', callback_data=f'info page_info {current_page} {leng}'))
                        if current_page == leng:
                            keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank next"))
                        else:
                            keyboard_row.append(InlineKeyboardButton('下一页', callback_data="info jump " + str(current_page + 1)))
                        keyboard.append(keyboard_row)
                        if generating_content.get(str(msg.chat.id) + str(msg.id), None) is not None:
                            del generating_content[str(msg.chat.id) + str(msg.id)]
                        if first_send == True:
                            await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, rich_message = InputRichMessage(markdown=msgtext), reply_markup=InlineKeyboardMarkup(keyboard))
                        else:
                            first_send = True
                            msg = await client.send_rich_message(chat_id = message.chat.id, rich_message = InputRichMessage(markdown=msgtext), reply_markup=InlineKeyboardMarkup(keyboard), reply_parameters = ReplyParameters(message_id = message.id))
                    else:
                        first_send = True
                        await client.send_rich_message(chat_id = message.chat.id, rich_message = InputRichMessage(markdown=full_text), reply_parameters = ReplyParameters(message_id = message.id))
                tool_calls_list = get_tool_calls_list()
                if not tool_calls_list:
                    brk_toolr = True
                    break
                if len(full_text) != 0 and message.chat.type != pyrogram.enums.ChatType.PRIVATE:
                    if first_send == False:
                        first_send = True
                        edit_count = 0
                        await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, rich_message = InputRichMessage(markdown=full_text))
                        msg = await client.send_message(chat_id = message.chat.id, text = f"⏳ 思考中 ...", reply_parameters = ReplyParameters(message_id = message.id), reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]))
                assistant_msg = {
                    "role": "assistant",
                    "content": full_text if full_text else None,
                    "tool_calls": tool_calls_list,
                }
                payload["messages"].append(assistant_msg)
                for tc in tool_calls_list:
                    if stop_generate_flag.get(identifier, False):
                        break
                    func_name = tc["function"]["name"]
                    try:
                        func_args = json.loads(tc["function"]["arguments"])
                    except (json.JSONDecodeError, TypeError):
                        func_args = {}
                    try:
                        if func_name == "web_search":
                            if first_send == True:
                                if message.chat.type != pyrogram.enums.ChatType.PRIVATE:
                                    edit_count += 1
                                await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = f"⏳ 搜索 `{func_args.get('query', '')}` 中 ...", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]))
                            else:
                                first_send = True
                                page_send = False
                                msg = await client.send_message(chat_id = message.chat.id, text = f"⏳ 搜索 `{func_args.get('query', '')}` 中 ...", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]), reply_parameters = ReplyParameters(message_id = message.id))
                        elif func_name == "web_fetch":
                            if first_send == True:
                                if message.chat.type != pyrogram.enums.ChatType.PRIVATE:
                                    edit_count += 1
                                await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = f"⏳ 请求 `{func_args.get('url', '')}` 中 ...", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]))
                            else:
                                first_send = True
                                page_send = False
                                msg = await client.send_message(chat_id = message.chat.id, text = f"⏳ 请求 `{func_args.get('url', '')}` 中 ...", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]), reply_parameters = ReplyParameters(message_id = message.id))
                        elif func_name == "executejscode":
                            if first_send == True:
                                if message.chat.type != pyrogram.enums.ChatType.PRIVATE:
                                    edit_count += 1
                                await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = f"⏳ 执行脚本中 ...", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]))
                            else:
                                first_send = True
                                page_send = False
                                msg = await client.send_message(chat_id = message.chat.id, text = f"⏳ 执行脚本中 ...", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]), reply_parameters = ReplyParameters(message_id = message.id))
                    except:
                        pass
                    tool_result = await execute_tool_call(func_name, func_args, message.from_user.id, message.chat.id)
                    payload["messages"].append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": tool_result,
                    })
                break
            except Exception as e:
                retry_time += 1
                if retry_time <= config.config['Network']['Retry']:
                    continue
                if first_send == False:
                    await client.send_message(chat_id = message.chat.id, text = f"❌ 获取消息失败呢 ~\n\n错误: `{e}`", reply_parameters = ReplyParameters(message_id = message.id))
                else:
                    try:
                        await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = f"❌ 获取消息失败呢 ~\n\n错误: `{e}`")
                    except:
                        await client.send_message(chat_id = message.chat.id, text = f"❌ 获取消息失败呢 ~\n\n错误: `{e}`", reply_parameters = ReplyParameters(message_id = message.id))
                return
    if stop_generate_flag.get(identifier, False) == True:
        del stop_generate_flag[identifier]
    if len(full_text) == 0:
        if first_send == False:
            await client.send_message(chat_id = message.chat.id, text = f"❌ 获取消息失败呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
        else:
            await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = f"❌ 获取消息失败呢 ~")
    else:
        if message.chat.type != pyrogram.enums.ChatType.PRIVATE or draft_finish == False:
            if len(full_text) > config.config['Other']['MaxTextLength']:
                msgtext = ""
                for i in full_text[0:config.config['Other']['MaxTextLength']]:
                    msgtext = msgtext + i
                leng = len(full_text) // config.config['Other']['MaxTextLength']
                if len(full_text) % config.config['Other']['MaxTextLength'] > 0:
                    leng = leng + 1
                view_content[str(msg.chat.id) + str(msg.id)] = full_text
                current_page = 1
                keyboard = []
                keyboard_row = []
                if current_page == 1:
                    keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank prev"))
                else:
                    keyboard_row.append(InlineKeyboardButton('上一页', callback_data="info jump " + str(current_page - 1)))
                keyboard_row.append(InlineKeyboardButton(f'{current_page} / {leng}', callback_data=f'info page_info {current_page} {leng}'))
                if current_page == leng:
                    keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank next"))
                else:
                    keyboard_row.append(InlineKeyboardButton('下一页', callback_data="info jump " + str(current_page + 1)))
                keyboard.append(keyboard_row)
                if generating_content.get(str(msg.chat.id) + str(msg.id), None) is not None:
                    del generating_content[str(msg.chat.id) + str(msg.id)]
                await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, rich_message = InputRichMessage(markdown=msgtext), reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, rich_message = InputRichMessage(markdown=full_text))
        if config.config['User'].get(message.from_user.id, {}).get('Context', True) == True or message.chat.type != pyrogram.enums.ChatType.PRIVATE:
            if type(user_content) is list:
                await add_chat(message.chat.id, user_name, json.dumps(user_content))
            else:
                await add_chat(message.chat.id, user_name, user_text)
            await add_chat(message.chat.id, "assistant", full_text)

@app.on_message(filters.command(['chat', 'c']))
async def send_chat(client: Client, message: Message):
    if not int(message.from_user.id) in admin_list and not int(message.chat.id) in config.config['AI']['WhiteList']:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限或本群并未加入白名单呢 请联系超管授权 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    send_text = ""
    if message.text:
        send_text = message.text
    elif message.caption:
        send_text = message.caption
    if len(send_text.split()) >= 2:
        send_text = send_text[send_text.find(" ") + 1:]
        await ai_send_chat(client, message, send_text)
    else:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 命令格式不对哦 ~ 要这样使用呢: `/chat <内容>`", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)

@app.on_message(filters.command(['clear']))
async def clear_current_chat(client: Client, message: Message):
    if not int(message.from_user.id) in admin_list and not int(message.chat.id) in config.config['AI']['WhiteList']:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限或本群并未加入白名单呢 请联系超管授权 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    await clear_chat(message.chat.id)
    msg = await client.send_message(chat_id = message.chat.id, text = f"✔ 已清除当前聊天的记录呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
    await deletecommand(msg, message, 10)

@app.on_message(filters.command(['memory']))
async def show_memory(client: Client, message: Message):
    if not int(message.from_user.id) in admin_list and not int(message.chat.id) in config.config['AI']['WhiteList']:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限或本群并未加入白名单呢 请联系超管授权 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    argument = message.text.split(" ", 1)[1] if message.text and " " in message.text else ""
    msg = await client.send_message(chat_id = message.chat.id, text = await memory_text(message.from_user.id, message.chat.id, argument), reply_parameters = ReplyParameters(message_id = message.id))

@app.on_message(filters.command(['page', 'p']))
async def page_sub(client: Client, message: Message):
    if not int(message.from_user.id) in admin_list and not int(message.chat.id) in config.config['AI']['WhiteList']:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限或本群并未加入白名单呢 请联系超管授权 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    if len(message.text.split()) >= 2:
        if message.reply_to_message:
            if view_content.get(str(message.reply_to_message.chat.id) + str(message.reply_to_message.id), None) is not None:
                msg = message.reply_to_message
                content = view_content[str(msg.chat.id) + str(msg.id)]
                try:
                    current_page = int(message.text.split()[1])
                except:
                    msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 页数必须是 `int` 类型呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
                    await deletecommand(msg, message, 10)
                    return
                leng = len(content) // config.config['Other']['MaxTextLength']
                if len(content) % config.config['Other']['MaxTextLength'] > 0:
                    leng = leng + 1
                if current_page <= 0:
                    current_page = 1
                if current_page > leng:
                    current_page = leng
                try:
                    await client.delete_messages(message.chat.id, message.id)
                except:
                    pass
                msgtext = ""
                for i in content[((current_page - 1) * config.config['Other']['MaxTextLength']):(min(current_page * config.config['Other']['MaxTextLength'], len(content)) - 0)]:
                    msgtext = msgtext + i
                leng = len(content) // config.config['Other']['MaxTextLength']
                if len(content) % config.config['Other']['MaxTextLength'] > 0:
                    leng = leng + 1
                keyboard = []
                keyboard_row = []
                if current_page == 1:
                    keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank prev"))
                else:
                    keyboard_row.append(InlineKeyboardButton('上一页', callback_data="info jump " + str(current_page - 1)))
                keyboard_row.append(InlineKeyboardButton(f'{current_page} / {leng}', callback_data=f'info page_info {current_page} {leng}'))
                if current_page == leng:
                    keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank next"))
                else:
                    keyboard_row.append(InlineKeyboardButton('下一页', callback_data="info jump " + str(current_page + 1)))
                keyboard.append(keyboard_row)
                if generating_content.get(str(msg.chat.id) + str(msg.id), None) is not None:
                    stop_identifier = generating_content.get(str(msg.chat.id) + str(msg.id), '')
                    keyboard.append([InlineKeyboardButton('停止', callback_data='stop ' + stop_identifier)])
                await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, rich_message = InputRichMessage(markdown=msgtext), reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 请回复包含查询内容的消息呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
                await deletecommand(msg, message, 10)
        else:
            msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 请回复一条消息呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
            await deletecommand(msg, message, 10)
    else:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 命令格式不对哦 ~ 要这样使用呢: `/page <页数>`", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)

@app.on_message(filters.command(['context']))
async def change_context(client: Client, message: Message):
    if not int(message.from_user.id) in admin_list:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限呢 请联系超管授权 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    context_stat = config.config['User'][message.from_user.id]['Context']
    if context_stat == True:
        config.config['User'][message.from_user.id]['Context'] = False
        config.Save()
        msg = await client.send_message(chat_id = message.chat.id, text = f"✔ 已关闭上下文记录呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
    else:
        config.config['User'][message.from_user.id]['Context'] = True
        config.Save()
        msg = await client.send_message(chat_id = message.chat.id, text = f"✔ 已开启上下文记录呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)

@app.on_message(filters.command(['prompt']))
async def change_prompt(client: Client, message: Message):
    if not int(message.from_user.id) in admin_list:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限呢 请联系超管授权 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    prompt = config.config['User'][message.from_user.id]['SystemPrompt']
    if len(message.text.split()) >= 2:
        user_content = message.text[message.text.find(" ") + 1:]
        config.config['User'][message.from_user.id]['SystemPrompt'] = user_content
        config.Save()
        msg = await client.send_message(chat_id = message.chat.id, text = f"✔ 已修改系统提示词 ~\n\n修改前: `{prompt}`\n修改后: `{user_content}`", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
    else:
        config.config['User'][message.from_user.id]['SystemPrompt'] = ""
        config.Save()
        msg = await client.send_message(chat_id = message.chat.id, text = f"✔ 已删除系统提示词 ~\n\n修改前: `{prompt}`", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)

@app.on_message(filters.command(['reason', 'effort', 'reasoneffort']))
async def change_reasoningeffort(client: Client, message: Message):
    if not int(message.from_user.id) in admin_list:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限呢 请联系超管授权 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    button = [
        [InlineKeyboardButton('默认', callback_data=f"r {message.from_user.id} s auto"), InlineKeyboardButton('关闭', callback_data=f"r {message.from_user.id} s none")],
        [InlineKeyboardButton('最小', callback_data=f"r {message.from_user.id} s minimal"), InlineKeyboardButton('极高', callback_data=f"r {message.from_user.id} s xhigh")],
        [InlineKeyboardButton('低', callback_data=f"r {message.from_user.id} s low"), InlineKeyboardButton('中', callback_data=f"r {message.from_user.id} s medium"), InlineKeyboardButton('高', callback_data=f"r {message.from_user.id} s high")],
        [InlineKeyboardButton('关闭', callback_data=f"r {message.from_user.id} c")]
    ]
    await client.send_message(chat_id = message.chat.id, text = f"🔗 当前思维链深度为 `{get_reasoning_effort_name(config.config['User'][message.from_user.id]['ReasoningEffort'])}` 请选择要修改的思维链深度:", reply_markup=InlineKeyboardMarkup(button), reply_parameters = ReplyParameters(message_id = message.id))
    
@app.on_message(filters.command(['model']))
async def change_model(client: Client, message: Message):
    if not int(message.from_user.id) in admin_list:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限呢 请联系超管授权 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    result = list(model_list.keys())
    if len(result) == 0:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您还没有配置任何模型哦 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    if len(message.text.split()) == 1:
        pages = [result[i:i + 20] for i in range(0, len(result), 20)]
        total = len(pages)
        current_page = 1
        current_items = pages[current_page - 1]

        button = []
        brow = []
        for mdname in current_items:
            brow.append(InlineKeyboardButton(mdname, callback_data=f"m {message.from_user.id} s {mdname}"))
            if len(brow) == 2:
                button.append(brow)
                brow = []
        if not len(brow) == 0:
            button.append(brow)
        keyboard_row = []
        if current_page == 1:
            keyboard_row.append(InlineKeyboardButton('      ', callback_data=f"m {message.from_user.id} b p"))
        else:
            keyboard_row.append(InlineKeyboardButton('上一页', callback_data=f"m {message.from_user.id} j " + str(current_page - 1)))
        keyboard_row.append(InlineKeyboardButton(f'{current_page} / {total}', callback_data=f'm {message.from_user.id} i {current_page} {total}'))
        if current_page == total:
            keyboard_row.append(InlineKeyboardButton('      ', callback_data=f"m {message.from_user.id} b n"))
        else:
            keyboard_row.append(InlineKeyboardButton('下一页', callback_data=f"m {message.from_user.id} j " + str(current_page + 1)))
        button.append(keyboard_row)
        button.append([InlineKeyboardButton("关闭", callback_data=f"m {message.from_user.id} c")])
        await client.send_message(chat_id = message.chat.id, text = f"🔗 当前模型为 `{config.config['User'][message.from_user.id]['Model']}` 当前有 `{len(result)}` 个模型 请选择要更换的模型:", reply_markup=InlineKeyboardMarkup(button), reply_parameters = ReplyParameters(message_id = message.id))
    else:
        model_name = message.text.split()[1]
        if model_name not in result:
            all_model = '`\n`'.join(result)
            msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您选择的模型不存在哦 ~\n\n当前可用模型有: \n\n`{all_model}`", reply_parameters = ReplyParameters(message_id = message.id))
            await deletecommand(msg, message, 10)
            return
        config.config['User'][message.from_user.id]['Model'] = model_name
        config.Save()
        msg = await client.send_message(chat_id = message.chat.id, text = f"✔ 已将模型 `{config.config['User'][message.from_user.id]['Model']}` 更换为模型 `{model_name}` ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)

async def test_model_ava(ai_url, ai_key, ai_model, total, msg):
    global semaphore, already_check, stop_prune_flag
    if stop_prune_flag == True:
        return
    temp_model = ai_model
    if ":" in ai_model:
        ai_model = ai_model.split(':')[1]
    headers = {
        "Authorization": f"Bearer {ai_key}",
        "Content-Type": "application/json",
    }
    json_data = {
        "model": ai_model,
        "messages": [{"role": "user", "content": "hi"}]
    }
    try:
        async with semaphore:
            if stop_prune_flag == True:
                return
            start_time = datetime.datetime.now()
            async with AsyncSession(retry=config.config['Network']['Retry']) as session:
                cont = await session.post(ai_url, headers=headers, impersonate="chrome", json=json_data, proxy=get_proxy(), timeout=config.config['Network']['Timeout'])
                elapsed_ms = int((datetime.datetime.now() - start_time).total_seconds() * 1000)
                req = json.loads(cont.text)
                if len(req.get("choices", [])) > 0 and len(req.get("choices", [])[0].get("message", {}).get("content", {})) > 0:
                    already_check = already_check + 1
                    cal = already_check * 100 / total
                    cal_old = (already_check - 1) * 100 / total
                    if int(cal / config.config['Other']['RefreshFrequency']) > int(cal_old / config.config['Other']['RefreshFrequency']) or already_check == total:
                        equal_signs = int(cal / 5)
                        space_count = 20 - equal_signs
                        temp_text = "⏳ 测试模型可用性中 ...\n\n[`" + "=" * equal_signs + " " * space_count + "`]\n\n目前剩余任务数量为: `" + str(total - already_check + 1) + "`"
                        await app.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = temp_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='prune')]]))
                    return {"model": temp_model, "delay": elapsed_ms, "status": True}
        already_check = already_check + 1
        cal = already_check * 100 / total
        cal_old = (already_check - 1) * 100 / total
        if int(cal / config.config['Other']['RefreshFrequency']) > int(cal_old / config.config['Other']['RefreshFrequency']) or already_check == total:
            equal_signs = int(cal / 5)
            space_count = 20 - equal_signs
            temp_text = "⏳ 测试模型可用性中 ...\n\n[`" + "=" * equal_signs + " " * space_count + "`]\n\n目前剩余任务数量为: `" + str(total - already_check + 1) + "`"
            await app.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = temp_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='prune')]]))
        return {"model": temp_model, "delay": -1, "status": False}
    except:
        already_check = already_check + 1
        cal = already_check * 100 / total
        cal_old = (already_check - 1) * 100 / total
        if int(cal / config.config['Other']['RefreshFrequency']) > int(cal_old / config.config['Other']['RefreshFrequency']) or already_check == total:
            equal_signs = int(cal / 5)
            space_count = 20 - equal_signs
            temp_text = "⏳ 测试模型可用性中 ...\n\n[`" + "=" * equal_signs + " " * space_count + "`]\n\n目前剩余任务数量为: `" + str(total - already_check + 1) + "`"
            await app.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = temp_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='prune')]]))
        return {"model": temp_model, "delay": -1, "status": False}

@app.on_message(filters.command(['prune']))
async def prune_model(client: Client, message: Message):
    global semaphore, already_check, test_prune_flag, stop_prune_flag, prune_history
    if not int(message.from_user.id) in admin_list:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限呢 请联系超管授权 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    if not int(message.from_user.id) in su_admin_list:
        if prune_history is None:
            msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 当前没有模型可用性结果呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
            await deletecommand(msg, message, 10)
            return
        msg = await client.send_message(chat_id = message.chat.id, text = f"✏️ **模型可用性测试** - `{prune_history['time']}`\n{prune_history['content']}", reply_parameters = ReplyParameters(message_id = message.id))
        return
    if test_prune_flag == True:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 正在检测模型可用性哦 ~ 请过会再尝试吧 ~", reply_to_message_id = message.id)
        await deletecommand(msg, message, 10)
        return
    prune_keyword = None
    if len(message.text.split()) >= 2:
        prune_keyword = message.text.split()[1]
    if prune_keyword is None:
        logger.info(f"SuAdmin {str(message.from_user.id)} Prune")
    else:
        logger.info(f"SuAdmin {str(message.from_user.id)} Prune {prune_keyword}")
    test_prune_flag = True
    stop_prune_flag = False
    msg = await client.send_message(chat_id = message.chat.id, text = f"⏳ 测试模型可用性中 ...", reply_parameters = ReplyParameters(message_id = message.id))
    model_name = []
    model_task = []
    for aivendor in config.config['AI']['Vendor']:
        for modelname in config.config['AI']['Vendor'][aivendor].get('Model', []):
            if prune_keyword is not None and not re.search(prune_keyword, modelname, re.IGNORECASE):
                continue
            model_name.append(modelname)
    for aivendor in config.config['AI']['Vendor']:
        for modelname in config.config['AI']['Vendor'][aivendor].get('Model', []):
            if prune_keyword is not None and not re.search(prune_keyword, modelname, re.IGNORECASE):
                continue
            model_task.append(asyncio.create_task(test_model_ava(f"{config.config['AI']['Vendor'][aivendor]['BaseUrl'].rstrip('/')}/chat/completions", config.config['AI']['Vendor'][aivendor]['Key'], modelname, len(model_name), msg)))
    semaphore = asyncio.Semaphore(config.config['Network']['Thread'])
    already_check = 0
    temp_results = await asyncio.gather(*model_task)
    if stop_prune_flag == True:
        test_prune_flag = False
        stop_prune_flag = False
        await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = f"✔ 任务已停止 ~")
        await deletecommand(msg, message, 10)
        return
    test_prune_flag = False
    stop_prune_flag = False
    results = {}
    for res in temp_results:
        results[res['model']] = res
    content = ""
    for modelname in model_name:
        content += f"\n**{modelname}**: "
        if results[modelname]['status'] == True:
            content += f"✔ - `{results[modelname]['delay']}ms`"
        else:
            content += "❌"
    prune_history = {"time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "content": content}
    await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = "✏️ **模型可用性测试**\n" + content)

@app.on_message(filters.command(['trust']))
async def trust_group(client: Client, message: Message):
    if not int(message.from_user.id) in su_admin_list:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限呢 请在配置文件中设置呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    if message.chat.type == pyrogram.enums.ChatType.PRIVATE:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 私聊无需加入白名单哦 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    try:
        if message.chat.id in config.config['AI']['WhiteList']:
            msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 此群组已被加入白名单了哦 ~", reply_parameters = ReplyParameters(message_id = message.id))
            await deletecommand(msg, message, 10)
            return
        logger.info(f"SuAdmin {str(message.from_user.id)} Trust {message.chat.id}")
        config.config['AI']['WhiteList'].append(message.chat.id)
        config.Save()
        await reloadbot()
        msg = await client.send_message(chat_id = message.chat.id, text = f"✔ 已添加白名单群组 `{message.chat.id}` ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
    except:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 添加白名单群组失败哦 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)

@app.on_message(filters.command(['distrust']))
async def distrust_group(client: Client, message: Message):
    if not int(message.from_user.id) in su_admin_list:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限呢 请在配置文件中设置呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    try:
        if message.chat.id not in config.config['AI']['WhiteList']:
            msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 此群组还未被加入白名单哦 ~", reply_parameters = ReplyParameters(message_id = message.id))
            await deletecommand(msg, message, 10)
            return
        logger.info(f"SuAdmin {str(message.from_user.id)} DisTrust {message.chat.id}")
        config.config['AI']['WhiteList'].remove(message.chat.id)
        config.Save()
        await reloadbot()
        msg = await client.send_message(chat_id = message.chat.id, text = f"✔ 已删除白名单群组 `{message.chat.id}` ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
    except:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 删除白名单群组失败哦 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)

@app.on_message(filters.command(['reload']))
async def reload_config(client: Client, message: Message):
    if not int(message.from_user.id) in su_admin_list:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限呢 请在配置文件中设置呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    config.Reload()
    msg = await client.send_message(chat_id = message.chat.id, text = f"✔ 配置重载完毕啦 ~", reply_parameters = ReplyParameters(message_id = message.id))
    await reloadbot()
    await deletecommand(msg, message, 10)

@app.on_message(filters.command(['grant']))
async def grant(client: Client, message: Message):
    if not int(message.from_user.id) in su_admin_list:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限呢 请在配置文件中设置呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    if message.reply_to_message is not None:
        if message.reply_to_message.from_user.id in su_admin_list:
            msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 对象已经是超管了呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
            await deletecommand(msg, message, 10)
        elif message.reply_to_message.from_user.id in admin_list:
            msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 对象已经是管理员了呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
            await deletecommand(msg, message, 10)
        else:
            config.config['Admin'].append(message.reply_to_message.from_user.id)
            config.Save()
            await reloadbot()
            msg = await client.send_message(chat_id = message.chat.id, text = f"✔ 已将 `{message.reply_to_message.from_user.id}` 授权为管理员 ~", reply_parameters = ReplyParameters(message_id = message.id))
            await deletecommand(msg, message, 10)
    else:
        if len(message.text.split()) >= 2:
            content = ""
            grant_list = []
            for i in message.text.split()[1:]:
                try:
                    i = int(i)
                    if i not in su_admin_list and i not in admin_list:
                        config.config['Admin'].append(i)
                        grant_list.append(i)
                        content = content + "`" + str(i) + "` "
                except:
                    pass
            config.Save()
            await reloadbot()
            if len(grant_list) > 0:
                msg = await client.send_message(chat_id = message.chat.id, text = f"✔ 已将 {content} 授权为管理员 ~", reply_parameters = ReplyParameters(message_id = message.id))
                await deletecommand(msg, message, 10)
            else:
                msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 没有可授权的id呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
                await deletecommand(msg, message, 10)
        else:
            msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 命令格式不对哦 ~ 要这样使用呢: `/grant <可选:id>`", reply_parameters = ReplyParameters(message_id = message.id))
            await deletecommand(msg, message, 10)

@app.on_message(filters.command(['ungrant']))
async def ungrant(client: Client, message: Message):
    if not int(message.from_user.id) in su_admin_list:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限呢 请在配置文件中设置呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    if message.reply_to_message is not None:
        if message.reply_to_message.from_user.id in su_admin_list:
            msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 对象已经是超管了呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
            await deletecommand(msg, message, 10)
        elif message.reply_to_message.from_user.id not in admin_list:
            msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 对象还不是管理员哦 ~", reply_parameters = ReplyParameters(message_id = message.id))
            await deletecommand(msg, message, 10)
        else:
            config.config['Admin'].remove(message.reply_to_message.from_user.id)
            config.Save()
            await reloadbot()
            msg = await client.send_message(chat_id = message.chat.id, text = f"✔ 已取消 `{message.reply_to_message.from_user.id}` 的授权 ~", reply_parameters = ReplyParameters(message_id = message.id))
            await deletecommand(msg, message, 10)
    else:
        if len(message.text.split()) >= 2:
            content = ""
            grant_list = []
            for i in message.text.split()[1:]:
                try:
                    i = int(i)
                    if i not in su_admin_list and i in admin_list:
                        config.config['Admin'].remove(i)
                        grant_list.append(i)
                        content = content + "`" + str(i) + "` "
                except:
                    pass
            config.Save()
            await reloadbot()
            if len(grant_list) > 0:
                msg = await client.send_message(chat_id = message.chat.id, text = f"✔ 已取消 {content} 的授权 ~", reply_parameters = ReplyParameters(message_id = message.id))
                await deletecommand(msg, message, 10)
            else:
                msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 没有可取消授权的id呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
                await deletecommand(msg, message, 10)
        else:
            msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 命令格式不对哦 ~ 要这样使用呢: `/ungrant <可选:id>`", reply_parameters = ReplyParameters(message_id = message.id))
            await deletecommand(msg, message, 10)

@app.on_message(filters.command(['grantscan']))
async def grantscan(client: Client, message: Message):
    if not int(message.from_user.id) in su_admin_list:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限呢 请在配置文件中设置呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    logger.info(f"SuAdmin {str(message.from_user.id)} ScanGrant")
    msg = await client.send_message(chat_id = message.chat.id, text = f"✔ 扫描中 ~", reply_parameters = ReplyParameters(message_id = message.id))
    old_len = len(config.config['Admin'])
    for userid in config.config['Admin']:
        try:
            try:
                result = await client.get_users(userid)
                if result.is_deleted == True:
                    config.config['Admin'].remove(userid)
            except pyrogram.errors.exceptions.bad_request_400.PeerIdInvalid as e:
                config.config['Admin'].remove(userid)
        except:
            pass
    config.Save()
    await reloadbot()
    await client.edit_message_text(chat_id = msg.chat.id, message_id = msg.id, text = f"✔ 扫描完毕 已清除 `{old_len - len(config.config['Admin'])}` 个授权 ~")
    await deletecommand(msg, message, 10)

@app.on_message(filters.command(['stop']))
async def stop_bot(client: Client, message: Message):
    if not int(message.from_user.id) in su_admin_list:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限呢 请在配置文件中设置呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    try:
        logger.info(f"SuAdmin {str(message.from_user.id)} Stop Bot")
        if config.config['Other']['Password'] != message.text.split()[1]:
            msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 密码错误哦 ~", reply_parameters = ReplyParameters(message_id = message.id))
            await deletecommand(msg, message, 10)
        else:
            msg = await client.send_message(chat_id = message.chat.id, text = f"✔ 正在关闭 `Bot` ~", reply_parameters = ReplyParameters(message_id = message.id))
            os._exit(1)
    except:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 密码错误哦 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)

@app.on_message(filters.command(['leave']))
async def leave_group(client: Client, message: Message):
    if not int(message.from_user.id) in su_admin_list:
        msg = await client.send_message(chat_id = message.chat.id, text = f"❌ 您没有权限呢 请在配置文件中设置呢 ~", reply_parameters = ReplyParameters(message_id = message.id))
        await deletecommand(msg, message, 10)
        return
    logger.info(f"Leave Group {str(message.chat.id)}")
    await client.leave_chat(chat_id = message.chat.id)
@app.on_message(filters.command(['start']))
async def start_command(client: Client, message: Message):
    if len(message.text.split()) == 1:
        if config.config['Other']['Intro']['Enable'] == True:
            logger.info(f"{str(message.from_user.id)} Start Bot")
            await client.send_message(chat_id = message.chat.id, text = config.config['Other']['Intro']['Text'], reply_parameters = ReplyParameters(message_id = message.id))

@app.on_message(filters.command(['id']))
async def get_user_id(client: Client, message: Message):
    if not int(message.from_user.id) in su_admin_list:
        return
    if message.reply_to_message:
        content = f"**Chat**: `{message.chat.id}`\n**RID**: `{message.reply_to_message.from_user.id}`"
        if message.reply_to_message.from_user.language_code:
            content = content + f"\n**RLocale**: `{message.reply_to_message.from_user.language_code}`"
        if message.reply_to_message.from_user.dc_id:
            content = content + f"\n**RDC**: `{message.reply_to_message.from_user.dc_id}`"
    else:
        content = f"**Chat**: `{message.chat.id}`\n**ID**: `{message.from_user.id}`"
        if message.from_user.language_code:
            content = content + f"\n**Locale**: `{message.from_user.language_code}`"
        if message.from_user.dc_id:
            content = content + f"\n**DC**: `{message.from_user.dc_id}`"
    msg = await client.send_message(chat_id = message.chat.id, text = content, reply_parameters = ReplyParameters(message_id = message.id))
    await deletecommand(msg, message, 10)

@app.on_message(filters.new_chat_members)
async def auto_leave(client: Client, message: Message):
    for member in message.new_chat_members:
        if member.is_self == True:
            if config.config['Other']['AvoidJoinGroups'] == 1 and message.from_user.id not in admin_list:
                await client.send_message(chat_id = message.chat.id, text = f"❌ 机器人已启动防拉群模式 请联系管理员拉群", reply_parameters = ReplyParameters(message_id = message.id))
                await client.leave_chat(chat_id = message.chat.id)
            elif config.config['Other']['AvoidJoinGroups'] == 2 and message.from_user.id not in su_admin_list:
                await client.send_message(chat_id = message.chat.id, text = f"❌ 机器人已启动防拉群模式 请联系超管拉群", reply_parameters = ReplyParameters(message_id = message.id))
                await client.leave_chat(chat_id = message.chat.id)

@app.on_message()
async def msg_handler(client: Client, message: Message):
    if (int(message.from_user.id) in admin_list or int(message.chat.id) in config.config['AI']['WhiteList']) and config.config['AI']['AutoReply'] == True :
        send_text = ""
        if message.text:
            send_text = message.text
        elif message.caption:
            send_text = message.caption
        if ('@' + bot_me.username).lower() in send_text.lower():
            send_text = remove_bot_username(send_text, '@' + bot_me.username)
            await ai_send_chat(client, message, send_text)
        elif ('@' + bot_me.first_name).lower() in send_text.lower():
            send_text = remove_bot_username(send_text, '@' + bot_me.first_name)
            await ai_send_chat(client, message, send_text)
        elif message.chat.type == pyrogram.enums.ChatType.PRIVATE:
            await ai_send_chat(client, message, send_text)
        elif message.reply_to_message and message.reply_to_message.from_user.is_self == True:
            await ai_send_chat(client, message, send_text)
        else:
            for wakeword in config.config['AI']['WakeWord']:
                if re.search(wakeword, send_text, re.IGNORECASE):
                    send_text = remove_bot_username(send_text, wakeword)
                    await ai_send_chat(client, message, send_text)
                    break

@app.on_inline_query()
async def inline_query_handler(client: Client, inline_query: InlineQuery):
    if not inline_query.from_user.id in admin_list:
        await client.answer_inline_query(inline_query_id = inline_query.id, results = [InlineQueryResultArticle(title = '您没有权限使用这个命令呢', description = '请联系超管授权', input_message_content = InputTextMessageContent(f"❌ 您没有权限呢 请联系超管授权 ~"))], cache_time = 1)
        return
    if len(inline_query.query.split()) == 0:
        await client.answer_inline_query(inline_query_id = inline_query.id, results = [InlineQueryResultArticle(title = '请输入内容呢', description = f"请填写需要发送的内容", input_message_content = InputTextMessageContent(f"❌ 请按照 `@{bot_me.username} 内容` 的格式填写呢 ~"))], cache_time = 1)
        return
    await client.answer_inline_query(inline_query_id = inline_query.id, results = [InlineQueryResultArticle(id = str(uuid.uuid4()), title = '点我发送消息', description = inline_query.query, input_message_content = InputTextMessageContent(f"⏳ 思考中 ..."), reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data=f'stop')]]))], cache_time = 1, is_personal=True)

def get_delay(edit_index: int, total_edits: int) -> float:
    if total_edits <= 1:
        return 0
    progress = edit_index / total_edits
    return config.config['AI']['ChunkStrategy']['Delay']['Base'] + config.config['AI']['ChunkStrategy']['Delay']['Extra'] * (1 - math.e ** (- progress * config.config['AI']['ChunkStrategy']['Delay']['Progress']))

@app.on_guest_message()
async def on_guest_message_handler(client: Client, message: Message):
    current_chat_id = message.chat.id
    if message.chat.type == pyrogram.enums.ChatType.PRIVATE:
        if message.chat.id != message.from_user.id:
            current_chat_id = int(str(min(message.chat.id, message.from_user.id)) + str(max(message.chat.id, message.from_user.id)))
    if (int(message.from_user.id) not in admin_list and current_chat_id not in config.config['AI']['WhiteList']):
        return
    send_text = ""
    if message.text:
        send_text = message.text
    elif message.caption:
        send_text = message.caption
    send_text = remove_bot_username(send_text, '@' + bot_me.username)
    if send_text.split(' ')[0] == "/id":
        if message.reply_to_message:
            content = f"**Chat**: `{message.chat.id}`\n**RID**: `{message.reply_to_message.from_user.id}`"
            if message.reply_to_message.from_user.language_code:
                content = content + f"\n**RLocale**: `{message.reply_to_message.from_user.language_code}`"
            if message.reply_to_message.from_user.dc_id:
                content = content + f"\n**RDC**: `{message.reply_to_message.from_user.dc_id}`"
        else:
            content = f"**Chat**: `{message.chat.id}`\n**ID**: `{message.from_user.id}`"
            if message.from_user.language_code:
                content = content + f"\n**Locale**: `{message.from_user.language_code}`"
            if message.from_user.dc_id:
                content = content + f"\n**DC**: `{message.from_user.dc_id}`"
        await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle(content, input_message_content = InputTextMessageContent(content)))
        return
    elif send_text.split(' ')[0] == "/clear":
        await clear_chat(current_chat_id)
        await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle("✔ 已清除当前聊天的记录呢 ~", input_message_content = InputTextMessageContent(f"✔ 已清除当前聊天的记录呢 ~")))
        return
    elif send_text.split(' ')[0] == "/memory":
        argument = send_text.split(" ", 1)[1] if " " in send_text else ""
        content = await memory_text(message.from_user.id, current_chat_id, argument)
        await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle(content, input_message_content = InputTextMessageContent(content)))
        return
    elif send_text.split(' ')[0] == "/stats":
        content = "你当前的权限状态是:\n\n管理权限: "
        if int(message.from_user.id) in admin_list:
            content = content + "✔"
        else:
            content = content + "❌"
        content = content + "\n超管权限: "
        if int(message.from_user.id) in su_admin_list:
            content = content + "✔"
        else:
            content = content + "❌"
        if int(message.from_user.id) in su_admin_list:
            content = content + f"\n\n超管数量: `{len(su_admin_list)}`" + f"\n管理数量: `{len(admin_list) - len(su_admin_list)}`\n模型数量: `{len(list(model_list.keys()))}`\n群组数量: `{len(config.config['AI']['WhiteList']):}`"
        if int(message.from_user.id) in admin_list:
            #topics = await get_topics(message.chat.id)
            contexts = await get_chat(current_chat_id)
            content = content + f"\n\n当前对话数量: `{len(contexts)}`" #+ f"\n当前话题数量: `{len(topics)}`"
            content = content + "\n\n上下文记录: "
            if config.config['User'][message.from_user.id]['Context'] == True:
                content = content + "✔"
            else:
                content = content + "❌"
            content = content + "\n长期记忆: "
            if config.config['AI']['Memory']['Enable'] == True:
                content = content + "✔"
            else:
                content = content + "❌"
            content = content + f"\n当前模型: `{config.config['User'][message.from_user.id]['Model']}`\n默认模型: `{config.config['AI']['DefaultModel']}`\n当前思维链深度: `{get_reasoning_effort_name(config.config['User'][message.from_user.id]['ReasoningEffort'])}`\n默认思维链深度: `{get_reasoning_effort_name(config.config['AI']['ReasoningEffort'])}`\n\n网络搜索: "
            if config.config['AI']['Tool']['Enable'] == True and config.config['AI']['Tool']['WebSearch']['Enable'] == True:
                content = content + "✔"
            else:
                content = content + "❌"
            content = content + "\n链接请求: "
            if config.config['AI']['Tool']['Enable'] == True and config.config['AI']['Tool']['FetchURL']['Enable'] == True:
                content = content + "✔"
            else:
                content = content + "❌"
            content = content + "\n代码执行: "
            if config.config['AI']['Tool']['Enable'] == True and config.config['AI']['Tool']['JSExecution']['Enable'] == True:
                content = content + "✔"
            else:
                content = content + "❌"
            content = content + "\n文件读取: "
            if config.config['AI']['FileSupport'] == True:
                content = content + "✔"
            else:
                content = content + "❌"
        await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle(content, input_message_content = InputTextMessageContent(content)))
        return
    elif send_text.split(' ')[0] in ['/reason', '/effort', '/reasoneffort']:
        button = [
            [InlineKeyboardButton('默认', callback_data=f"r {message.from_user.id} s auto"), InlineKeyboardButton('关闭', callback_data=f"r {message.from_user.id} s none")],
            [InlineKeyboardButton('最小', callback_data=f"r {message.from_user.id} s minimal"), InlineKeyboardButton('极高', callback_data=f"r {message.from_user.id} s xhigh")],
            [InlineKeyboardButton('低', callback_data=f"r {message.from_user.id} s low"), InlineKeyboardButton('中', callback_data=f"r {message.from_user.id} s medium"), InlineKeyboardButton('高', callback_data=f"r {message.from_user.id} s high")],
        ]
        await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle(f"🔗 当前思维链深度为 `{get_reasoning_effort_name(config.config['User'][message.from_user.id]['ReasoningEffort'])}` 请选择要修改的思维链深度:", input_message_content = InputTextMessageContent(f"🔗 当前思维链深度为 `{get_reasoning_effort_name(config.config['User'][message.from_user.id]['ReasoningEffort'])}` 请选择要修改的思维链深度:"), reply_markup=InlineKeyboardMarkup(button)))
        return
    elif send_text.split(' ')[0] == "/model":
        result = list(model_list.keys())
        if len(result) == 0:
            await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle(f"❌ 您还没有配置任何模型哦 ~", input_message_content = InputTextMessageContent(f"❌ 您还没有配置任何模型哦 ~")))
            return
        if len(send_text.split()) == 1:
            pages = [result[i:i + 20] for i in range(0, len(result), 20)]
            total = len(pages)
            current_page = 1
            current_items = pages[current_page - 1]

            button = []
            brow = []
            for mdname in current_items:
                brow.append(InlineKeyboardButton(mdname, callback_data=f"m {message.from_user.id} s {mdname}"))
                if len(brow) == 2:
                    button.append(brow)
                    brow = []
            if not len(brow) == 0:
                button.append(brow)
            keyboard_row = []
            if current_page == 1:
                keyboard_row.append(InlineKeyboardButton('      ', callback_data=f"m {message.from_user.id} b p"))
            else:
                keyboard_row.append(InlineKeyboardButton('上一页', callback_data=f"m {message.from_user.id} j " + str(current_page - 1)))
            keyboard_row.append(InlineKeyboardButton(f'{current_page} / {total}', callback_data=f'm {message.from_user.id} i {current_page} {total}'))
            if current_page == total:
                keyboard_row.append(InlineKeyboardButton('      ', callback_data=f"m {message.from_user.id} b n"))
            else:
                keyboard_row.append(InlineKeyboardButton('下一页', callback_data=f"m {message.from_user.id} j " + str(current_page + 1)))
            button.append(keyboard_row)
            await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle(f"🔗 当前模型为 `{config.config['User'][message.from_user.id]['Model']}` 当前有 `{len(result)}` 个模型 请选择要更换的模型:", input_message_content = InputTextMessageContent(f"🔗 当前模型为 `{config.config['User'][message.from_user.id]['Model']}` 当前有 `{len(result)}` 个模型 请选择要更换的模型:"), reply_markup = InlineKeyboardMarkup(button)))
        else:
            model_name = send_text.split()[1]
            if model_name not in result:
                all_model = '`\n`'.join(result)
                await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle(f"❌ 您选择的模型不存在哦 ~\n\n当前可用模型有: \n\n`{all_model}`", input_message_content = InputTextMessageContent(f"❌ 您选择的模型不存在哦 ~\n\n当前可用模型有: \n\n`{all_model}`")))
                return
            config.config['User'][message.from_user.id]['Model'] = model_name
            config.Save()
            await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle(f"✔ 已将模型 `{config.config['User'][message.from_user.id]['Model']}` 更换为模型 `{model_name}` ~", input_message_content = InputTextMessageContent(f"✔ 已将模型 `{config.config['User'][message.from_user.id]['Model']}` 更换为模型 `{model_name}` ~")))
        return
    elif send_text.split(' ')[0] == "/trust":
        if int(message.from_user.id) not in su_admin_list:
            await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle(f"❌ 您没有权限呢 请在配置文件中设置呢 ~", input_message_content = InputTextMessageContent(f"❌ 您没有权限呢 请在配置文件中设置呢 ~")))
            return
        try:
            if current_chat_id in config.config['AI']['WhiteList']:
                await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle(f"❌ 此群组已被加入白名单了哦 ~", input_message_content = InputTextMessageContent(f"❌ 此群组已被加入白名单了哦 ~")))
                return
            logger.info(f"SuAdmin {str(message.from_user.id)} Trust {current_chat_id}")
            config.config['AI']['WhiteList'].append(current_chat_id)
            config.Save()
            await reloadbot()
            await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle(f"✔ 已添加白名单群组 `{current_chat_id}` ~", input_message_content = InputTextMessageContent(f"✔ 已添加白名单群组 `{current_chat_id}` ~")))
        except:
            await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle(f"❌ 添加白名单群组失败哦 ~", input_message_content = InputTextMessageContent(f"❌ 添加白名单群组失败哦 ~")))
        return
    elif send_text.split(' ')[0] == "/distrust":
        if int(message.from_user.id) not in su_admin_list:
            await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle(f"❌ 您没有权限呢 请在配置文件中设置呢 ~", input_message_content = InputTextMessageContent(f"❌ 您没有权限呢 请在配置文件中设置呢 ~")))
            return
        try:
            if current_chat_id not in config.config['AI']['WhiteList']:
                await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle(f"❌ 此群组还未被加入白名单哦 ~", input_message_content = InputTextMessageContent(f"❌ 此群组还未被加入白名单哦 ~")))
                return
            logger.info(f"SuAdmin {str(message.from_user.id)} DisTrust {current_chat_id}")
            config.config['AI']['WhiteList'].remove(current_chat_id)
            config.Save()
            await reloadbot()
            await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle(f"✔ 已删除白名单群组 `{current_chat_id}` ~", input_message_content = InputTextMessageContent(f"✔ 已删除白名单群组 `{current_chat_id}` ~")))
        except:
            await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle(f"❌ 删除白名单群组失败哦 ~", input_message_content = InputTextMessageContent(f"❌ 删除白名单群组失败哦 ~")))
        return
    identifier = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_', k=10))
    files = []
    reply_files = []
    have_file = False
    class tempmsg:
        def __init__(self, inline_message_id):
            self.inline_message_id = inline_message_id
    msg = tempmsg(0)
    if message_has_image(message) or message_has_file(message):
        current_files = []
        group_msgs = await get_media_group_messages(client, message)
        for gmsg in group_msgs:
            if stop_generate_flag.get(identifier, False):
                break
            if message_has_image(gmsg):
                if have_file == False:
                    have_file = True
                    msg = await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle("⏳ 获取图片中 ...", input_message_content = InputTextMessageContent(f"⏳ 获取图片中 ..."), reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data=f'stop ' + identifier)]])))
                try:
                    buf = await client.download_media(gmsg, in_memory=True)
                    buf.seek(0)
                    img_content = base64.b64encode(buf.read()).decode("utf-8")
                    current_files.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{detect_mime(img_content, gmsg)};base64,{img_content}"
                        }
                    })
                except:
                    pass
            elif message_has_file(gmsg):
                if have_file == False:
                    have_file = True
                    msg = await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle("⏳ 获取文件中 ...", input_message_content = InputTextMessageContent(f"⏳ 获取图片中 ..."), reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data=f'stop ' + identifier)]])))
                try:
                    buf = await client.download_media(gmsg, in_memory=True)
                    buf.seek(0)
                    file_content = base64.b64encode(buf.read()).decode("utf-8")
                    if gmsg.document and gmsg.document.file_name:
                        file_name = gmsg.document.file_name
                    else:
                        file_name = "file"
                    current_files.append({
                        "type": "file",
                        "file": {
                            "filename": file_name,
                            "file_data": f"data:{detect_mime(file_content, gmsg)};base64,{file_content}"
                        }
                    })
                except:
                    pass
        files.extend(current_files)
    if stop_generate_flag.get(identifier, False) == True:
        del stop_generate_flag[identifier]
        if msg:
            await client.edit_inline_text(inline_message_id = msg.inline_message_id, text = f"❌ 获取消息失败呢 ~")
        else:
            await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle("❌ 获取消息失败呢 ~", input_message_content = InputTextMessageContent(f"❌ 获取消息失败呢 ~")))
        return
    if message.reply_to_message and message.reply_to_message.from_user.is_self == False:
        current_files = []
        group_msgs = await get_media_group_messages(client, message.reply_to_message)
        for gmsg in group_msgs:
            if stop_generate_flag.get(identifier, False):
                break
            if message_has_image(gmsg):
                if have_file == False:
                    have_file = True
                    msg = await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle("⏳ 获取图片中 ...", input_message_content = InputTextMessageContent(f"⏳ 获取图片中 ..."), reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data=f'stop ' + identifier)]])))
                try:
                    buf = await client.download_media(gmsg, in_memory=True)
                    buf.seek(0)
                    img_content = base64.b64encode(buf.read()).decode("utf-8")
                    current_files.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{detect_mime(img_content, gmsg)};base64,{img_content}"
                        }
                    })
                except:
                    pass
            elif message_has_file(gmsg):
                if have_file == False:
                    have_file = True
                    msg = await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle("⏳ 获取文件中 ...", input_message_content = InputTextMessageContent(f"⏳ 获取图片中 ..."), reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data=f'stop ' + identifier)]])))
                try:
                    buf = await client.download_media(gmsg, in_memory=True)
                    buf.seek(0)
                    file_content = base64.b64encode(buf.read()).decode("utf-8")
                    if gmsg.document and gmsg.document.file_name:
                        file_name = gmsg.document.file_name
                    else:
                        file_name = "file"
                    current_files.append({
                        "type": "file",
                        "file": {
                            "filename": file_name,
                            "file_data": f"data:{detect_mime(file_content, gmsg)};base64,{file_content}"
                        }
                    })
                except:
                    pass
        reply_files.extend(current_files)
    if stop_generate_flag.get(identifier, False) == True:
        del stop_generate_flag[identifier]
        if msg:
            await client.edit_inline_text(inline_message_id = msg.inline_message_id, text = f"❌ 获取消息失败呢 ~")
        else:
            await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle("❌ 获取消息失败呢 ~", input_message_content = InputTextMessageContent(f"❌ 获取消息失败呢 ~")))
        return
    user_text = safe_ai_text(send_text)
    reply_content = None
    if len(files) == 0:
        if config.config['AI']['IDRecognition']['Enable'] == True:
            user_name = message.from_user.first_name
            if message.from_user.last_name:
                user_name += message.from_user.last_name
            user_name = safe_ai_text(user_name)
            user_content = config.config['AI']['IDRecognition']['Format'].format_map(SafeFormatDict(name=user_name, content=user_text))
        else:
            user_content = user_text
    else:
        if config.config['AI']['IDRecognition']['Enable'] == True:
            user_name = message.from_user.first_name
            if message.from_user.last_name:
                user_name += message.from_user.last_name
            user_name = safe_ai_text(user_name)
            user_content = [{"type": "text", "text": config.config['AI']['IDRecognition']['Format'].format_map(SafeFormatDict(name=user_name, content=user_text))}]
        else:
            user_content = [{"type": "text", "text": user_text}]
        user_content.extend(files)
    if message.reply_to_message and message.reply_to_message.from_user.is_self == False:
        reply_send_text = ""
        if message.reply_to_message.text:
            reply_send_text = message.reply_to_message.text
        elif message.reply_to_message.caption:
            reply_send_text = message.reply_to_message.caption
        reply_send_text = safe_ai_text(reply_send_text)
        if len(reply_send_text) != 0:
            if len(reply_files) == 0:
                if config.config['AI']['IDRecognition']['Enable'] == True:
                    user_name = message.reply_to_message.from_user.first_name
                    if message.reply_to_message.from_user.last_name:
                        user_name += message.reply_to_message.from_user.last_name
                    user_name = safe_ai_text(user_name)
                    reply_content = config.config['AI']['IDRecognition']['Format'].format_map(SafeFormatDict(name=user_name, content=reply_send_text))
                else:
                    reply_content = reply_send_text
            else:
                if config.config['AI']['IDRecognition']['Enable'] == False:
                    user_name = message.reply_to_message.from_user.first_name
                    if message.reply_to_message.from_user.last_name:
                        user_name += message.reply_to_message.from_user.last_name
                    user_name = safe_ai_text(user_name)
                    reply_content = [{"type": "text", "text": config.config['AI']['IDRecognition']['Format'].format_map(SafeFormatDict(name=user_name, content=reply_send_text))}]
                else:
                    reply_content = [{"type": "text", "text": reply_send_text}]
                reply_content.extend(reply_files)
        elif len(reply_files) != 0:
            reply_content = reply_files
    systemprompt = config.config['User'].get(message.from_user.id, {}).get('SystemPrompt', config.config['AI']['SystemPrompt'])
    use_model = config.config['User'].get(message.from_user.id, {}).get('Model', config.config['AI']['DefaultModel'])
    if use_model not in list(model_list.keys()):
        use_model = config.config['AI']['DefaultModel']
    reasoneffort = config.config['User'].get(message.from_user.id, {}).get('ReasoningEffort', config.config['AI']['ReasoningEffort'])
    if reasoneffort == "":
        reasoneffort = config.config['AI']['ReasoningEffort']
    ai_url = f"{config.config['AI']['Vendor'][model_list[use_model]]['BaseUrl'].rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.config['AI']['Vendor'][model_list[use_model]]['Key']}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    ai_messages = []
    if len(systemprompt) == 0:
        systemprompt = config.config['AI']['SystemPrompt']
    if len(config.config['AI']['ExtraSystemPrompt']) != 0:
        ai_messages.append({"role": "system", "content": config.config['AI']['ExtraSystemPrompt'].format_map(SafeFormatDict(cur_date=datetime.datetime.now().strftime("%Y-%m-%d"), cur_time=datetime.datetime.now().strftime("%H:%M:%S"), cur_datetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), model_name=use_model.split(':', 1)[1] if ':' in use_model else use_model, assistant_name=bot_me.first_name))})
    if config.config['AI']['IDRecognition']['Enable'] == True and len(config.config['AI']['IDRecognition']['Prompt']) != 0:
        ai_messages.append({"role": "system", "content": config.config['AI']['IDRecognition']['Prompt']})
    if len(systemprompt) != 0:
        ai_messages.append({"role": "system", "content": systemprompt})
    if config.config['AI']['Memory']['Enable'] == True:
        memory_prompt = await get_memory_prompt(message.from_user.id, current_chat_id)
        if memory_prompt:
            ai_messages.append({"role": "system", "content": memory_prompt})
    if config.config['User'].get(message.from_user.id, {}).get('Context', True) == True:
        await keep_last_chat(current_chat_id, config.config['AI']['MaxContext'])
        contexts = await get_chat(current_chat_id)
        for ctext in contexts:
            his_content = ctext['content']
            try:
                his_content = json.loads(his_content)
            except:
                pass
            if ctext['name'] in ['user', 'assistant']:
                ai_messages.append({"role": ctext['name'], "content": his_content})
            else:
                if config.config['AI']['IDRecognition']['Enable'] == True:
                    ai_messages.append({"role": "user", "content": config.config['AI']['IDRecognition']['Format'].format_map(SafeFormatDict(name=ctext['name'], content=his_content))})
                else:
                    ai_messages.append({"role": "user", "name": ctext['name'], "content": his_content})
    if message.reply_to_message and message.reply_to_message.from_user.is_self == False:
        if config.config['AI']['IDRecognition']['Enable'] == True:
            user_name = "user"
            ai_messages.append({"role": "user", "content": reply_content})
        else:
            user_name = message.reply_to_message.from_user.first_name
            if message.reply_to_message.from_user.last_name:
                user_name += message.reply_to_message.from_user.last_name
            user_name = safe_ai_text(user_name)
            ai_messages.append({"role": "user", "name": user_name, "content": reply_content})
    if config.config['AI']['IDRecognition']['Enable'] == True:
        user_name = "user"
        ai_messages.append({"role": "user", "content": user_content})
    else:
        user_name = message.from_user.first_name
        if message.from_user.last_name:
            user_name += message.from_user.last_name
        user_name = safe_ai_text(user_name)
        ai_messages.append({"role": "user", "name": user_name, "content": user_content})
    used_tools = []
    if config.config['AI']['Tool']['Enable'] == True and config.config['AI']['Tool']['WebSearch']['Enable'] == True:
        used_tools.append(TOOLS_DEFINITION['web_search'])
    if config.config['AI']['Tool']['Enable'] == True and config.config['AI']['Tool']['FetchURL']['Enable'] == True:
        used_tools.append(TOOLS_DEFINITION['web_fetch'])
    if config.config['AI']['Tool']['Enable'] == True and config.config['AI']['Tool']['JSExecution']['Enable'] == True:
        used_tools.append(TOOLS_DEFINITION['executejscode'])
    if config.config['AI']['Tool']['Enable'] == True and config.config['AI']['Memory']['Enable'] == True:
        used_tools.extend([TOOLS_DEFINITION['memory_save'], TOOLS_DEFINITION['memory_delete']])
    if ":" in use_model:
        use_model = use_model.split(':')[1]
    if len(used_tools) == 0:
        payload = {
            "model": use_model,
            "messages": ai_messages,
            "stream": True,
        }
    else:
        payload = {
            "model": use_model,
            "messages": ai_messages,
            "stream": True,
            "tools": used_tools,
            "tool_choice": "auto",
        }
    if reasoneffort not in ['', 'auto']:
        payload['reasoning_effort'] = reasoneffort
    max_tool_rounds = config.config['AI']['Tool']['MaxToolCall']
    logger.info(f"Admin {str(message.from_user.id)} Use Model {use_model}")
    valid_tool_names = set()
    for tool in used_tools:
        try:
            valid_tool_names.add(tool["function"]["name"])
        except Exception:
            pass
    def create_tool_collector():
        """
        每一轮 stream 单独创建一个 tool collector。
        重点：
        1. 优先按 tool_call id 分流
        2. id 缺失时再按 index
        3. index 异常重复时，不把不同 id 的 tool call 拼一起
        """
        tool_calls_map = {}
        id_to_key = {}
        index_to_key = {}
        last_tool_key = None
        def new_key():
            return len(tool_calls_map)
        def create_tool_call(key, tc_id="", tc_type="function"):
            tool_calls_map[key] = {
                "id": tc_id or "",
                "type": tc_type or "function",
                "function": {
                    "name": "",
                    "arguments": "",
                },
            }
        def get_tool_key(tc_delta: dict):
            nonlocal last_tool_key
            tc_id = tc_delta.get("id")
            idx = tc_delta.get("index")
            tc_type = tc_delta.get("type", "function")
            # 最可靠：有 id 就按 id 分
            if tc_id:
                if tc_id in id_to_key:
                    key = id_to_key[tc_id]
                else:
                    key = new_key()
                    create_tool_call(key, tc_id=tc_id, tc_type=tc_type)
                    id_to_key[tc_id] = key
                    # index 只作为辅助。
                    # 如果 index 已经被别的 id 占了，不复用，避免 web_searchweb_fetch。
                    if idx is not None:
                        old_key = index_to_key.get(idx)
                        if old_key is None:
                            index_to_key[idx] = key
                        else:
                            old_id = tool_calls_map.get(old_key, {}).get("id", "")
                            if old_id == tc_id:
                                index_to_key[idx] = key
                last_tool_key = key
                return key
            # 没 id，有 index
            if idx is not None:
                if idx in index_to_key:
                    key = index_to_key[idx]
                else:
                    key = new_key()
                    create_tool_call(key, tc_id="", tc_type=tc_type)
                    index_to_key[idx] = key
                last_tool_key = key
                return key
            # id/index 都没有，只能续到上一个
            if last_tool_key is not None:
                return last_tool_key
            key = new_key()
            create_tool_call(key, tc_id="", tc_type=tc_type)
            last_tool_key = key
            return key
        def append_tool_delta(tc_delta: dict):
            key = get_tool_key(tc_delta)
            if key not in tool_calls_map:
                create_tool_call(key)
            if tc_delta.get("id"):
                tool_calls_map[key]["id"] = tc_delta["id"]
                id_to_key[tc_delta["id"]] = key
            if tc_delta.get("type"):
                tool_calls_map[key]["type"] = tc_delta["type"]
            func_delta = tc_delta.get("function", {}) or {}
            name_part = func_delta.get("name")
            args_part = func_delta.get("arguments")
            if name_part:
                tool_calls_map[key]["function"]["name"] += name_part
            if args_part:
                tool_calls_map[key]["function"]["arguments"] += args_part
        def split_json_objects(text: str):
            result = []
            decoder = json.JSONDecoder()
            pos = 0
            while pos < len(text):
                while pos < len(text) and text[pos].isspace():
                    pos += 1
                if pos >= len(text):
                    break
                try:
                    obj, end = decoder.raw_decode(text, pos)
                    result.append(json.dumps(obj, ensure_ascii=False))
                    pos = end
                except Exception:
                    return []
            return result
        def split_tool_name_sequence(name: str):
            """
            处理这种情况：
            web_searchweb_fetch -> ["web_search", "web_fetch"]
            """
            if not valid_tool_names:
                return []
            names = sorted(valid_tool_names, key=len, reverse=True)
            remain = name
            result = []
            while remain:
                matched = False
                for tool_name in names:
                    if remain.startswith(tool_name):
                        result.append(tool_name)
                        remain = remain[len(tool_name):]
                        matched = True
                        break
                if not matched:
                    return []
            return result
        def normalize_tool_calls():
            raw_list = []
            for key in sorted(tool_calls_map.keys()):
                tc = tool_calls_map[key]
                name = tc.get("function", {}).get("name", "")
                arguments = tc.get("function", {}).get("arguments", "")
                if not name and not arguments:
                    continue
                if not tc.get("id"):
                    tc["id"] = f"call_local_{key}"
                raw_list.append(tc)
            normalized = []
            for tc in raw_list:
                name = tc["function"]["name"]
                arguments = tc["function"]["arguments"]
                # 正常工具名，直接保留
                if not valid_tool_names or name in valid_tool_names:
                    normalized.append(tc)
                    continue
                # 尝试拆开 web_searchweb_fetch
                name_parts = split_tool_name_sequence(name)
                arg_parts = split_json_objects(arguments)
                if len(name_parts) >= 2 and len(name_parts) == len(arg_parts):
                    for i, tool_name in enumerate(name_parts):
                        normalized.append({
                            "id": tc["id"] if i == 0 else f"{tc['id']}_split_{i}",
                            "type": tc.get("type", "function"),
                            "function": {
                                "name": tool_name,
                                "arguments": arg_parts[i],
                            },
                        })
                else:
                    logger.warning(f"Drop invalid tool call: {tc}")
            # 去重，避免同一个 tool_call 被重复执行
            deduped = []
            seen = set()
            for tc in normalized:
                mark = (
                    tc["function"].get("name", ""),
                    tc["function"].get("arguments", ""),
                )
                if mark in seen:
                    continue
                seen.add(mark)
                deduped.append(tc)
            return deduped
        return append_tool_delta, normalize_tool_calls
    page_send = False
    last_edit = 0
    edit_count = 0
    retry_time = 0
    brk_toolr = False
    fbmodel_pos = 0
    fallback_model = [config.config['User'].get(message.from_user.id, {}).get('Model', config.config['AI']['DefaultModel'])]
    fallback_model.extend(config.config['AI']['FallbackModel'])
    fallback_model = list(set(fallback_model))
    if have_file:
        await client.edit_inline_text(inline_message_id = msg.inline_message_id, text = f"⏳ 思考中 ...", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]))
        edit_count += 1
    else:
        msg = await client.answer_guest_query(message.guest_query_id, result = InlineQueryResultArticle("⏳ 思考中 ...", input_message_content = InputTextMessageContent(f"⏳ 思考中 ..."), reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data=f'stop ' + identifier)]])))
    for tool_round in range(max_tool_rounds + 1):
        if brk_toolr == True:
            break
        brk_toolr = False
        while retry_time <= config.config['Network']['Retry']:
            if retry_time >= 1:
                fbmodel_pos += 1
                if fbmodel_pos >= len(fallback_model):
                    fbmodel_pos = 0
                use_model = fallback_model[fbmodel_pos]
                while use_model not in list(model_list.keys()):
                    fbmodel_pos += 1
                    if fbmodel_pos >= len(fallback_model):
                        fbmodel_pos = 0
                    use_model = fallback_model[fbmodel_pos]
                ai_url = f"{config.config['AI']['Vendor'][model_list[use_model]]['BaseUrl'].rstrip('/')}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {config.config['AI']['Vendor'][model_list[use_model]]['Key']}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream",
                }
                if ":" in use_model:
                    use_model = use_model.split(':')[1]
                payload["model"] = use_model
            try:
                full_text = ""
                current_text = ""
                buffer = ""
                draft_id = client.rnd_id()
                append_tool_delta, get_tool_calls_list = create_tool_collector()
                async with AsyncSession(retry=config.config['Network']['Retry']) as session:
                    if tool_round == max_tool_rounds:
                        payload.pop("tools", None)
                        payload.pop("tool_choice", None)
                    async with session.stream(
                        "POST",
                        ai_url,
                        headers=headers,
                        json=payload,
                        timeout=config.config['Network']['Timeout'],
                        impersonate="chrome",
                        proxy=get_proxy(),
                    ) as resp:
                        resp.raise_for_status()
                        async for chunk in resp.aiter_content():
                            if stop_generate_flag.get(identifier, False) == True:
                                await resp.aclose()
                                break
                            if not chunk:
                                continue
                            if isinstance(chunk, bytes):
                                chunk = chunk.decode("utf-8", errors="ignore")
                            buffer += chunk
                            buffer = buffer.replace("\r\n", "\n")
                            while "\n\n" in buffer:
                                raw_event, buffer = buffer.split("\n\n", 1)
                                raw_event = raw_event.strip()
                                if not raw_event:
                                    continue
                                for line in raw_event.splitlines():
                                    line = line.strip()
                                    if not line.startswith("data:"):
                                        continue
                                    data = line[5:].strip()
                                    if data == "[DONE]":
                                        break
                                    try:
                                        choices = json.loads(data).get("choices", [])
                                        if not choices:
                                            continue
                                        delta = choices[0].get("delta", {})
                                        content = choices[0].get("delta", {}).get("content")
                                        if content:
                                            full_text += content
                                            current_text += content
                                            now = time.time()
                                            
                                            if edit_count < config.config['AI']['ChunkStrategy']['MaxEdit'] and now - last_edit >= get_delay(edit_count, config.config['AI']['ChunkStrategy']['MaxEdit']) and re.search(config.config['AI']['ChunkStrategy']['Rule'], current_text):
                                                if len(full_text) > config.config['Other']['MaxTextLength']:
                                                    if page_send == False:
                                                        page_send = True
                                                        msgtext = ""
                                                        for i in full_text[0:config.config['Other']['MaxTextLength']]:
                                                            msgtext = msgtext + i
                                                        leng = len(full_text) // config.config['Other']['MaxTextLength']
                                                        if len(full_text) % config.config['Other']['MaxTextLength'] > 0:
                                                            leng = leng + 1
                                                        view_content[identifier] = full_text
                                                        current_page = 1
                                                        keyboard = []
                                                        keyboard_row = []
                                                        if current_page == 1:
                                                            keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank prev"))
                                                        else:
                                                            keyboard_row.append(InlineKeyboardButton('上一页', callback_data="info jump " + str(current_page - 1) + " " + identifier))
                                                        keyboard_row.append(InlineKeyboardButton(f'{current_page} / {leng}', callback_data=f'info page_info {current_page} {leng}'))
                                                        if current_page == leng:
                                                            keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank next"))
                                                        else:
                                                            keyboard_row.append(InlineKeyboardButton('下一页', callback_data="info jump " + str(current_page + 1) + " " + identifier))
                                                        keyboard.append(keyboard_row)
                                                        keyboard.append([InlineKeyboardButton('停止', callback_data='stop ' + identifier)])
                                                        generating_content[identifier] = identifier
                                                        await client.edit_inline_text(inline_message_id = msg.inline_message_id, rich_message = InputRichMessage(markdown=msgtext), reply_markup=InlineKeyboardMarkup(keyboard))
                                                    else:
                                                        view_content[identifier] = full_text
                                                    edit_count += 1
                                                    last_edit = now
                                                    current_text = ""
                                                else:
                                                    await client.edit_inline_text(inline_message_id = msg.inline_message_id, rich_message = InputRichMessage(markdown=full_text), reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]))
                                                    edit_count += 1
                                                    last_edit = now
                                                    current_text = ""
                                        tc_deltas = delta.get("tool_calls") or []
                                        for tc_delta in tc_deltas:
                                            try:
                                                append_tool_delta(tc_delta)
                                            except:
                                                pass
                                    except:
                                        pass
                tool_calls_list = get_tool_calls_list()
                if not tool_calls_list:
                    brk_toolr = True
                    break
                assistant_msg = {
                    "role": "assistant",
                    "content": full_text if full_text else None,
                    "tool_calls": tool_calls_list,
                }
                payload["messages"].append(assistant_msg)
                for tc in tool_calls_list:
                    if stop_generate_flag.get(identifier, False):
                        break
                    func_name = tc["function"]["name"]
                    try:
                        func_args = json.loads(tc["function"]["arguments"])
                    except (json.JSONDecodeError, TypeError):
                        func_args = {}
                    try:
                        if func_name == "web_search":
                            await client.edit_inline_text(inline_message_id = msg.inline_message_id, text = f"⏳ 搜索 `{func_args.get('query', '')}` 中 ...", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]))
                            edit_count += 1
                        elif func_name == "web_fetch":
                            await client.edit_inline_text(inline_message_id = msg.inline_message_id, text = f"⏳ 请求 `{func_args.get('url', '')}` 中 ...", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]))
                            edit_count += 1
                        elif func_name == "executejscode":
                            await client.edit_inline_text(inline_message_id = msg.inline_message_id, text = f"⏳ 执行脚本中 ...", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop ' + identifier)]]))
                            edit_count += 1
                    except:
                        pass
                    tool_result = await execute_tool_call(func_name, func_args, message.from_user.id, current_chat_id)
                    payload["messages"].append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": tool_result,
                    })
                break
            except Exception as e:
                retry_time += 1
                if retry_time <= config.config['Network']['Retry']:
                    continue
                await client.edit_inline_text(inline_message_id = msg.inline_message_id, text = f"❌ 获取消息失败呢 ~\n\n错误: `{e}`")
                return
    if stop_generate_flag.get(identifier, False) == True:
        del stop_generate_flag[identifier]
    if len(full_text) == 0:
        await client.edit_inline_text(inline_message_id = msg.inline_message_id, text = f"❌ 获取消息失败呢 ~")
    else:
        if len(full_text) > config.config['Other']['MaxTextLength']:
            msgtext = ""
            for i in full_text[0:config.config['Other']['MaxTextLength']]:
                msgtext = msgtext + i
            leng = len(full_text) // config.config['Other']['MaxTextLength']
            if len(full_text) % config.config['Other']['MaxTextLength'] > 0:
                leng = leng + 1
            view_content[identifier] = full_text
            current_page = 1
            keyboard = []
            keyboard_row = []
            if current_page == 1:
                keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank prev"))
            else:
                keyboard_row.append(InlineKeyboardButton('上一页', callback_data="info jump " + str(current_page - 1) + " " + identifier))
            keyboard_row.append(InlineKeyboardButton(f'{current_page} / {leng}', callback_data=f'info page_info {current_page} {leng}'))
            if current_page == leng:
                keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank next"))
            else:
                keyboard_row.append(InlineKeyboardButton('下一页', callback_data="info jump " + str(current_page + 1) + " " + identifier))
            keyboard.append(keyboard_row)
            if generating_content.get(identifier, None) is not None:
                del generating_content[identifier]
            await client.edit_inline_text(inline_message_id = msg.inline_message_id, rich_message = InputRichMessage(markdown=msgtext), reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await client.edit_inline_text(inline_message_id = msg.inline_message_id, rich_message = InputRichMessage(markdown=full_text))
        if config.config['User'].get(message.from_user.id, {}).get('Context', True) == True:
            if type(user_content) is list:
                await add_chat(current_chat_id, user_name, json.dumps(user_content))
            else:
                await add_chat(current_chat_id, user_name, user_text)
            await add_chat(current_chat_id, "assistant", full_text)

@app.on_chosen_inline_result()
async def on_chosen_inline_result_handler(client: Client, chosen_inline_result: ChosenInlineResult):
    global stop_generate_flag, generating_content
    systemprompt = config.config['User'].get(chosen_inline_result.from_user.id, {}).get('SystemPrompt', config.config['AI']['SystemPrompt'])
    use_model = config.config['User'].get(chosen_inline_result.from_user.id, {}).get('Model', config.config['AI']['DefaultModel'])
    if use_model not in list(model_list.keys()):
        use_model = config.config['AI']['DefaultModel']
    reasoneffort = config.config['User'].get(chosen_inline_result.from_user.id, {}).get('ReasoningEffort', config.config['AI']['ReasoningEffort'])
    if reasoneffort == "":
        reasoneffort = config.config['AI']['ReasoningEffort']
    ai_url = f"{config.config['AI']['Vendor'][model_list[use_model]]['BaseUrl'].rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.config['AI']['Vendor'][model_list[use_model]]['Key']}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    ai_messages = []
    if len(systemprompt) == 0:
        systemprompt = config.config['AI']['SystemPrompt']
    if len(config.config['AI']['ExtraSystemPrompt']) != 0:
        ai_messages.append({"role": "system", "content": config.config['AI']['ExtraSystemPrompt'].format_map(SafeFormatDict(cur_date=datetime.datetime.now().strftime("%Y-%m-%d"), cur_time=datetime.datetime.now().strftime("%H:%M:%S"), cur_datetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), model_name=use_model.split(':', 1)[1] if ':' in use_model else use_model, assistant_name=bot_me.first_name))})
    if len(systemprompt) != 0:
        ai_messages.append({"role": "system", "content": systemprompt})
    if config.config['AI']['Memory']['Enable'] == True:
        memory_prompt = await get_memory_prompt(chosen_inline_result.from_user.id, chosen_inline_result.from_user.id)
        if memory_prompt:
            ai_messages.append({"role": "system", "content": memory_prompt})
    if config.config['User'].get(chosen_inline_result.from_user.id, {}).get('Context', True) == True:
        await keep_last_chat(chosen_inline_result.from_user.id, config.config['AI']['MaxContext'])
        contexts = await get_chat(chosen_inline_result.from_user.id)
        for ctext in contexts:
            his_content = ctext['content']
            try:
                his_content = json.loads(his_content)
            except:
                pass
            ai_messages.append({"role": ctext['name'], "content": his_content})
    ai_messages.append({"role": "user", "content": safe_ai_text(chosen_inline_result.query)})
    used_tools = []
    if config.config['AI']['Tool']['Enable'] == True and config.config['AI']['Tool']['WebSearch']['Enable'] == True:
        used_tools.append(TOOLS_DEFINITION['web_search'])
    if config.config['AI']['Tool']['Enable'] == True and config.config['AI']['Tool']['FetchURL']['Enable'] == True:
        used_tools.append(TOOLS_DEFINITION['web_fetch'])
    if config.config['AI']['Tool']['Enable'] == True and config.config['AI']['Tool']['JSExecution']['Enable'] == True:
        used_tools.append(TOOLS_DEFINITION['executejscode'])
    if config.config['AI']['Memory']['Enable'] == True:
        used_tools.extend([TOOLS_DEFINITION['memory_save'], TOOLS_DEFINITION['memory_delete']])
    if ":" in use_model:
        use_model = use_model.split(':')[1]
    if len(used_tools) == 0:
        payload = {
            "model": use_model,
            "messages": ai_messages,
            "stream": True,
        }
    else:
        payload = {
            "model": use_model,
            "messages": ai_messages,
            "stream": True,
            "tools": used_tools,
            "tool_choice": "auto",
        }
    if reasoneffort not in ['', 'auto']:
        payload['reasoning_effort'] = reasoneffort
    max_tool_rounds = config.config['AI']['Tool']['MaxToolCall']
    logger.info(f"Admin {str(chosen_inline_result.from_user.id)} Use Model {use_model}")
    valid_tool_names = set()
    for tool in used_tools:
        try:
            valid_tool_names.add(tool["function"]["name"])
        except Exception:
            pass
    def create_tool_collector():
        """
        每一轮 stream 单独创建一个 tool collector。
        重点：
        1. 优先按 tool_call id 分流
        2. id 缺失时再按 index
        3. index 异常重复时，不把不同 id 的 tool call 拼一起
        """
        tool_calls_map = {}
        id_to_key = {}
        index_to_key = {}
        last_tool_key = None
        def new_key():
            return len(tool_calls_map)
        def create_tool_call(key, tc_id="", tc_type="function"):
            tool_calls_map[key] = {
                "id": tc_id or "",
                "type": tc_type or "function",
                "function": {
                    "name": "",
                    "arguments": "",
                },
            }
        def get_tool_key(tc_delta: dict):
            nonlocal last_tool_key
            tc_id = tc_delta.get("id")
            idx = tc_delta.get("index")
            tc_type = tc_delta.get("type", "function")
            # 最可靠：有 id 就按 id 分
            if tc_id:
                if tc_id in id_to_key:
                    key = id_to_key[tc_id]
                else:
                    key = new_key()
                    create_tool_call(key, tc_id=tc_id, tc_type=tc_type)
                    id_to_key[tc_id] = key
                    # index 只作为辅助。
                    # 如果 index 已经被别的 id 占了，不复用，避免 web_searchweb_fetch。
                    if idx is not None:
                        old_key = index_to_key.get(idx)
                        if old_key is None:
                            index_to_key[idx] = key
                        else:
                            old_id = tool_calls_map.get(old_key, {}).get("id", "")
                            if old_id == tc_id:
                                index_to_key[idx] = key
                last_tool_key = key
                return key
            # 没 id，有 index
            if idx is not None:
                if idx in index_to_key:
                    key = index_to_key[idx]
                else:
                    key = new_key()
                    create_tool_call(key, tc_id="", tc_type=tc_type)
                    index_to_key[idx] = key
                last_tool_key = key
                return key
            # id/index 都没有，只能续到上一个
            if last_tool_key is not None:
                return last_tool_key
            key = new_key()
            create_tool_call(key, tc_id="", tc_type=tc_type)
            last_tool_key = key
            return key
        def append_tool_delta(tc_delta: dict):
            key = get_tool_key(tc_delta)
            if key not in tool_calls_map:
                create_tool_call(key)
            if tc_delta.get("id"):
                tool_calls_map[key]["id"] = tc_delta["id"]
                id_to_key[tc_delta["id"]] = key
            if tc_delta.get("type"):
                tool_calls_map[key]["type"] = tc_delta["type"]
            func_delta = tc_delta.get("function", {}) or {}
            name_part = func_delta.get("name")
            args_part = func_delta.get("arguments")
            if name_part:
                tool_calls_map[key]["function"]["name"] += name_part
            if args_part:
                tool_calls_map[key]["function"]["arguments"] += args_part
        def split_json_objects(text: str):
            result = []
            decoder = json.JSONDecoder()
            pos = 0
            while pos < len(text):
                while pos < len(text) and text[pos].isspace():
                    pos += 1
                if pos >= len(text):
                    break
                try:
                    obj, end = decoder.raw_decode(text, pos)
                    result.append(json.dumps(obj, ensure_ascii=False))
                    pos = end
                except Exception:
                    return []
            return result
        def split_tool_name_sequence(name: str):
            """
            处理这种情况：
            web_searchweb_fetch -> ["web_search", "web_fetch"]
            """
            if not valid_tool_names:
                return []
            names = sorted(valid_tool_names, key=len, reverse=True)
            remain = name
            result = []
            while remain:
                matched = False
                for tool_name in names:
                    if remain.startswith(tool_name):
                        result.append(tool_name)
                        remain = remain[len(tool_name):]
                        matched = True
                        break
                if not matched:
                    return []
            return result
        def normalize_tool_calls():
            raw_list = []
            for key in sorted(tool_calls_map.keys()):
                tc = tool_calls_map[key]
                name = tc.get("function", {}).get("name", "")
                arguments = tc.get("function", {}).get("arguments", "")
                if not name and not arguments:
                    continue
                if not tc.get("id"):
                    tc["id"] = f"call_local_{key}"
                raw_list.append(tc)
            normalized = []
            for tc in raw_list:
                name = tc["function"]["name"]
                arguments = tc["function"]["arguments"]
                # 正常工具名，直接保留
                if not valid_tool_names or name in valid_tool_names:
                    normalized.append(tc)
                    continue
                # 尝试拆开 web_searchweb_fetch
                name_parts = split_tool_name_sequence(name)
                arg_parts = split_json_objects(arguments)
                if len(name_parts) >= 2 and len(name_parts) == len(arg_parts):
                    for i, tool_name in enumerate(name_parts):
                        normalized.append({
                            "id": tc["id"] if i == 0 else f"{tc['id']}_split_{i}",
                            "type": tc.get("type", "function"),
                            "function": {
                                "name": tool_name,
                                "arguments": arg_parts[i],
                            },
                        })
                else:
                    logger.warning(f"Drop invalid tool call: {tc}")
            # 去重，避免同一个 tool_call 被重复执行
            deduped = []
            seen = set()
            for tc in normalized:
                mark = (
                    tc["function"].get("name", ""),
                    tc["function"].get("arguments", ""),
                )
                if mark in seen:
                    continue
                seen.add(mark)
                deduped.append(tc)
            return deduped
        return append_tool_delta, normalize_tool_calls
    last_edit = 0
    edit_count = 0
    page_send = False
    retry_time = 0
    brk_toolr = False
    fbmodel_pos = 0
    fallback_model = [config.config['User'].get(chosen_inline_result.from_user.id, {}).get('Model', config.config['AI']['DefaultModel'])]
    fallback_model.extend(config.config['AI']['FallbackModel'])
    fallback_model = list(set(fallback_model))
    for tool_round in range(max_tool_rounds + 1):
        if brk_toolr == True:
            break
        brk_toolr = False
        while retry_time <= config.config['Network']['Retry']:
            if retry_time >= 1:
                fbmodel_pos += 1
                if fbmodel_pos >= len(fallback_model):
                    fbmodel_pos = 0
                use_model = fallback_model[fbmodel_pos]
                while use_model not in list(model_list.keys()):
                    fbmodel_pos += 1
                    if fbmodel_pos >= len(fallback_model):
                        fbmodel_pos = 0
                    use_model = fallback_model[fbmodel_pos]
                ai_url = f"{config.config['AI']['Vendor'][model_list[use_model]]['BaseUrl'].rstrip('/')}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {config.config['AI']['Vendor'][model_list[use_model]]['Key']}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream",
                }
                if ":" in use_model:
                    use_model = use_model.split(':')[1]
                payload["model"] = use_model
            try:
                full_text = ""
                current_text = ""
                buffer = ""
                append_tool_delta, get_tool_calls_list = create_tool_collector()
                async with AsyncSession(retry=config.config['Network']['Retry']) as session:
                    if tool_round == max_tool_rounds:
                        payload.pop("tools", None)
                        payload.pop("tool_choice", None)
                    async with session.stream(
                        "POST",
                        ai_url,
                        headers=headers,
                        json=payload,
                        timeout=config.config['Network']['Timeout'],
                        impersonate="chrome",
                        proxy=get_proxy(),
                    ) as resp:
                        resp.raise_for_status()
                        async for chunk in resp.aiter_content():
                            if stop_generate_flag.get(chosen_inline_result.inline_message_id, False) == True:
                                await resp.aclose()
                                break
                            if not chunk:
                                continue
                            if isinstance(chunk, bytes):
                                chunk = chunk.decode("utf-8", errors="ignore")
                            buffer += chunk
                            buffer = buffer.replace("\r\n", "\n")
                            while "\n\n" in buffer:
                                raw_event, buffer = buffer.split("\n\n", 1)
                                raw_event = raw_event.strip()
                                if not raw_event:
                                    continue
                                for line in raw_event.splitlines():
                                    line = line.strip()
                                    if not line.startswith("data:"):
                                        continue
                                    data = line[5:].strip()
                                    if data == "[DONE]":
                                        break
                                    try:
                                        choices = json.loads(data).get("choices", [])
                                        if not choices:
                                            continue
                                        delta = choices[0].get("delta", {})
                                        content = choices[0].get("delta", {}).get("content")
                                        if content:
                                            full_text += content
                                            current_text += content
                                            now = time.time()
                                            if edit_count < config.config['AI']['ChunkStrategy']['MaxEdit'] and now - last_edit >= get_delay(edit_count, config.config['AI']['ChunkStrategy']['MaxEdit']) and re.search(config.config['AI']['ChunkStrategy']['Rule'], current_text):
                                                if len(full_text) > config.config['Other']['MaxTextLength']:
                                                    if page_send == False:
                                                        page_send = True
                                                        msgtext = ""
                                                        for i in full_text[0:config.config['Other']['MaxTextLength']]:
                                                            msgtext = msgtext + i
                                                        leng = len(full_text) // config.config['Other']['MaxTextLength']
                                                        if len(full_text) % config.config['Other']['MaxTextLength'] > 0:
                                                            leng = leng + 1
                                                        view_content[chosen_inline_result.inline_message_id] = full_text
                                                        current_page = 1
                                                        keyboard = []
                                                        keyboard_row = []
                                                        if current_page == 1:
                                                            keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank prev"))
                                                        else:
                                                            keyboard_row.append(InlineKeyboardButton('上一页', callback_data="info jump " + str(current_page - 1)))
                                                        keyboard_row.append(InlineKeyboardButton(f'{current_page} / {leng}', callback_data=f'info page_info {current_page} {leng}'))
                                                        if current_page == leng:
                                                            keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank next"))
                                                        else:
                                                            keyboard_row.append(InlineKeyboardButton('下一页', callback_data="info jump " + str(current_page + 1)))
                                                        keyboard.append(keyboard_row)
                                                        keyboard.append([InlineKeyboardButton('停止', callback_data='stop')])
                                                        generating_content[chosen_inline_result.inline_message_id] = ""
                                                        await client.edit_inline_text(inline_message_id = chosen_inline_result.inline_message_id, rich_message = InputRichMessage(markdown=msgtext), reply_markup=InlineKeyboardMarkup(keyboard))
                                                    else:
                                                        view_content[chosen_inline_result.inline_message_id] = full_text
                                                else:
                                                    await client.edit_inline_text(inline_message_id = chosen_inline_result.inline_message_id, rich_message = InputRichMessage(markdown=full_text), reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop')]]))
                                                edit_count += 1
                                                last_edit = now
                                                current_text = ""
                                        tc_deltas = delta.get("tool_calls") or []
                                        for tc_delta in tc_deltas:
                                            try:
                                                append_tool_delta(tc_delta)
                                            except:
                                                pass
                                    except:
                                        pass
                tool_calls_list = get_tool_calls_list()
                if not tool_calls_list:
                    brk_toolr = True
                    break
                assistant_msg = {
                    "role": "assistant",
                    "content": full_text if full_text else None,
                    "tool_calls": tool_calls_list,
                }
                payload["messages"].append(assistant_msg)
                for tc in tool_calls_list:
                    if stop_generate_flag.get(chosen_inline_result.inline_message_id, False):
                        break

                    func_name = tc["function"]["name"]
                    try:
                        func_args = json.loads(tc["function"]["arguments"])
                    except (json.JSONDecodeError, TypeError):
                        func_args = {}
                    try:
                        if func_name == "web_search":
                            edit_count += 1
                            await client.edit_inline_text(inline_message_id = chosen_inline_result.inline_message_id, text = f"⏳ 搜索 `{func_args.get('query', '')}` 中 ...", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop')]]))
                        elif func_name == "web_fetch":
                            edit_count += 1
                            await client.edit_inline_text(inline_message_id = chosen_inline_result.inline_message_id, text = f"⏳ 请求 `{func_args.get('url', '')}` 中 ...", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop')]]))
                        elif func_name == "executejscode":
                            edit_count += 1
                            await client.edit_inline_text(inline_message_id = chosen_inline_result.inline_message_id, text = f"⏳ 执行脚本中 ...", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('停止', callback_data='stop')]]))
                    except:
                        pass
                    
                    tool_result = await execute_tool_call(func_name, func_args, chosen_inline_result.from_user.id, chosen_inline_result.from_user.id)
                    payload["messages"].append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": tool_result,
                    })
                break
            except Exception as e:
                retry_time += 1
                if retry_time <= config.config['Network']['Retry']:
                    continue
                await client.edit_inline_text(inline_message_id = chosen_inline_result.inline_message_id, text = f"❌ 获取消息失败呢 ~\n\n错误: `{e}`")
                return
    if stop_generate_flag.get(chosen_inline_result.inline_message_id, False) == True:
        del stop_generate_flag[chosen_inline_result.inline_message_id]
    if len(full_text) == 0:
        await client.edit_inline_text(inline_message_id = chosen_inline_result.inline_message_id, text = "❌ 获取消息失败呢 ~")
    else:
        if len(full_text) > config.config['Other']['MaxTextLength']:
            msgtext = ""
            for i in full_text[0:config.config['Other']['MaxTextLength']]:
                msgtext = msgtext + i
            leng = len(full_text) // config.config['Other']['MaxTextLength']
            if len(full_text) % config.config['Other']['MaxTextLength'] > 0:
                leng = leng + 1
            view_content[chosen_inline_result.inline_message_id] = full_text
            current_page = 1
            keyboard = []
            keyboard_row = []
            if current_page == 1:
                keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank prev"))
            else:
                keyboard_row.append(InlineKeyboardButton('上一页', callback_data="info jump " + str(current_page - 1)))
            keyboard_row.append(InlineKeyboardButton(f'{current_page} / {leng}', callback_data=f'info page_info {current_page} {leng}'))
            if current_page == leng:
                keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank next"))
            else:
                keyboard_row.append(InlineKeyboardButton('下一页', callback_data="info jump " + str(current_page + 1)))
            keyboard.append(keyboard_row)
            if generating_content.get(chosen_inline_result.inline_message_id, None) is not None:
                del generating_content[chosen_inline_result.inline_message_id]
            await client.edit_inline_text(inline_message_id = chosen_inline_result.inline_message_id, rich_message = InputRichMessage(markdown=msgtext), reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await client.edit_inline_text(inline_message_id = chosen_inline_result.inline_message_id, rich_message = InputRichMessage(markdown=full_text))
        if config.config['User'].get(chosen_inline_result.from_user.id, {}).get('Context', True) == True:
            await add_chat(chosen_inline_result.from_user.id, "user", chosen_inline_result.query)
            await add_chat(chosen_inline_result.from_user.id, "assistant", full_text)

@app.on_callback_query()
async def callback_query_handler(client: Client, callback_query: CallbackQuery):
    if callback_query.data.split()[0] == 'info':
        if callback_query.data.split()[1] == 'page_info':
            await client.answer_callback_query(callback_query.id, f"第 {callback_query.data.split()[2]} 页  共 {callback_query.data.split()[3]} 页", show_alert=True)
        elif callback_query.data.split()[1] == 'jump':
            current_page = int(callback_query.data.split()[2])
            try:
                identifier = callback_query.data.split()[3]
                content = view_content[identifier]
                identifier = identifier
            except:
                identifier = ""
                try:
                    content = view_content[str(callback_query.message.chat.id) + str(callback_query.message.id)]
                except:
                    content = view_content[callback_query.inline_message_id]
            leng = len(content) // config.config['Other']['MaxTextLength']
            if len(content) % config.config['Other']['MaxTextLength'] > 0:
                leng = leng + 1
            if current_page <= 0:
                current_page = 1
            if current_page > leng:
                current_page = leng
            msgtext = ""
            for i in content[((current_page - 1) * config.config['Other']['MaxTextLength']):(min(current_page * config.config['Other']['MaxTextLength'], len(content)) - 0)]:
                msgtext = msgtext + i
            leng = len(content) // config.config['Other']['MaxTextLength']
            if len(content) % config.config['Other']['MaxTextLength'] > 0:
                leng = leng + 1
            keyboard = []
            keyboard_row = []
            if current_page == 1:
                keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank prev"))
            else:
                keyboard_row.append(InlineKeyboardButton('上一页', callback_data="info jump " + str(current_page - 1) + " " + identifier))
            keyboard_row.append(InlineKeyboardButton(f'{current_page} / {leng}', callback_data=f'info page_info {current_page} {leng}'))
            if current_page == leng:
                keyboard_row.append(InlineKeyboardButton('      ', callback_data="info blank next"))
            else:
                keyboard_row.append(InlineKeyboardButton('下一页', callback_data="info jump " + str(current_page + 1) + " " + identifier))
            keyboard.append(keyboard_row)
            try:
                if generating_content.get(str(callback_query.message.chat.id) + str(callback_query.message.id), None) is not None:
                    stop_identifier = generating_content.get(str(callback_query.message.chat.id) + str(callback_query.message.id), '')
                    keyboard.append([InlineKeyboardButton('停止', callback_data='stop ' + stop_identifier)])
            except:
                pass
            try:
                if generating_content.get(callback_query.inline_message_id, None) is not None:
                    keyboard.append([InlineKeyboardButton('停止', callback_data='stop')])
            except:
                pass
            try:
                if generating_content.get(identifier, None) is not None:
                    stop_identifier = generating_content.get(identifier, '')
                    keyboard.append([InlineKeyboardButton('停止', callback_data='stop ' + stop_identifier)])
            except:
                pass
            await callback_query.edit_message_text(rich_message = InputRichMessage(markdown=msgtext), reply_markup=InlineKeyboardMarkup(keyboard))
    elif callback_query.data.split()[0] == 'stop':
        if not callback_query.from_user.id in admin_list:
            await client.answer_callback_query(callback_query.id, text = "❌ 您没有权限呢 ~ 请不要点击哦 ~", show_alert = True)
            return
        if len(callback_query.data.split()) == 1:
            if stop_generate_flag.get(callback_query.inline_message_id, False) == True:
                await client.answer_callback_query(callback_query.id, text = "❌ 任务正在清理中 ~", show_alert = True)
            else:
                stop_generate_flag[callback_query.inline_message_id] = True
                await client.answer_callback_query(callback_query.id, text = "✔ 已接收到停止任务指令 任务正在停止中 ~", show_alert = True)
        else:
            identifier = callback_query.data.split()[1]
            if stop_generate_flag.get(identifier, False) == True:
                await client.answer_callback_query(callback_query.id, text = "❌ 任务正在清理中 ~", show_alert = True)
            else:
                stop_generate_flag[identifier] = True
                await client.answer_callback_query(callback_query.id, text = "✔ 已接收到停止任务指令 任务正在停止中 ~", show_alert = True)
    elif callback_query.data.split()[0] == 'r':
        if callback_query.from_user.id != int(callback_query.data.split()[1]):
            await client.answer_callback_query(callback_query.id, text = "❌ 请不要点击别人的按钮哦 ~", show_alert = True)
            return
        elif callback_query.data.split()[2] == 's':
            reasoneffort = callback_query.data.split()[3]
            config.config['User'][callback_query.from_user.id]['ReasoningEffort'] = reasoneffort
            config.Save()
            await callback_query.edit_message_text(text = f"✔ 已更换为 `{get_reasoning_effort_name(reasoneffort)}` 思维链深度 ~")
            if callback_query.message:
                await deletecommand(callback_query.message, callback_query.message.reply_to_message, 10)
            return
        elif callback_query.data.split()[2] == 'c':
            await deletecommand(callback_query.message, callback_query.message.reply_to_message, 0)
    elif callback_query.data.split()[0] == 'm':
        if callback_query.from_user.id != int(callback_query.data.split()[1]):
            await client.answer_callback_query(callback_query.id, text = "❌ 请不要点击别人的按钮哦 ~", show_alert = True)
            return
        elif callback_query.data.split()[2] == 'b':
            return
        elif callback_query.data.split()[2] == 'c':
            await deletecommand(callback_query.message, callback_query.message.reply_to_message, 0)
        elif callback_query.data.split()[2] == 'i':
            await client.answer_callback_query(callback_query.id, f"第 {callback_query.data.split()[3]} 页  共 {callback_query.data.split()[4]} 页", show_alert=True)
        elif callback_query.data.split()[2] == 'j':
            result = list(model_list.keys())
            pages = [result[i:i + 20] for i in range(0, len(result), 20)]
            total = len(pages)
            current_page = int(callback_query.data.split()[3])
            current_items = pages[current_page - 1]

            button = []
            brow = []
            for mdname in current_items:
                brow.append(InlineKeyboardButton(mdname, callback_data=f"m {callback_query.from_user.id} s {mdname}"))
                if len(brow) == 2:
                    button.append(brow)
                    brow = []
            if not len(brow) == 0:
                button.append(brow)
            keyboard_row = []
            if current_page == 1:
                keyboard_row.append(InlineKeyboardButton('      ', callback_data=f"m {callback_query.from_user.id} b p"))
            else:
                keyboard_row.append(InlineKeyboardButton('上一页', callback_data=f"m {callback_query.from_user.id} j " + str(current_page - 1)))
            keyboard_row.append(InlineKeyboardButton(f'{current_page} / {total}', callback_data=f'm {callback_query.from_user.id} i {current_page} {total}'))
            if current_page == total:
                keyboard_row.append(InlineKeyboardButton('      ', callback_data=f"m {callback_query.from_user.id} b n"))
            else:
                keyboard_row.append(InlineKeyboardButton('下一页', callback_data=f"m {callback_query.from_user.id} j " + str(current_page + 1)))
            button.append(keyboard_row)
            if callback_query.message:
                button.append([InlineKeyboardButton("关闭", callback_data=f"m {callback_query.from_user.id} c")])
            await callback_query.edit_message_text(text = f"🔗 当前模型为 `{config.config['User'][callback_query.from_user.id]['Model']}` 当前有 `{len(result)}` 个模型 请选择要更换的模型:", reply_markup=InlineKeyboardMarkup(button))
        elif callback_query.data.split()[2] == 's':
            cmodel = callback_query.data.split()[3]
            config.config['User'][callback_query.from_user.id]['Model'] = cmodel
            config.Save()
            await callback_query.edit_message_text(text = f"✔ 已更换为模型 `{cmodel}` ~")
            if callback_query.message:
                await deletecommand(callback_query.message, callback_query.message.reply_to_message, 10)
        else:
            await client.answer_callback_query(callback_query.id, text = "❌ 未知错误", show_alert = True)
    elif callback_query.data.split()[0] == 'prune':
        if not callback_query.from_user.id in su_admin_list:
            await client.answer_callback_query(callback_query.id, text = "❌ 您没有权限呢 ~ 请不要点击哦 ~", show_alert = True)
            return
        global stop_prune_flag
        if stop_prune_flag == True:
            await client.answer_callback_query(callback_query.id, text = "❌ 任务正在清理中 ~", show_alert = True)
        else:
            stop_prune_flag = True
            await client.answer_callback_query(callback_query.id, text = "✔ 已接收到停止任务指令 任务正在停止中 ~", show_alert = True)
    else:
        await client.answer_callback_query(callback_query.id, text = "❌ 未知错误", show_alert = True)

def init():
    get_model_list()
    if config.config['Bot']['HideCommand'] == False:
        app.set_bot_commands([
            BotCommand("help", "获取帮助菜单"), 
            BotCommand("version", f"获取版本信息 - {version_content} ({version_id})"),
            BotCommand("stats", "获取权限状态"),
            BotCommand("chat", "发送聊天内容"),
            BotCommand("model", "修改聊天模型"),
            BotCommand("prune", "测试模型可用性"),
            BotCommand("clear", "清除上下文记录"),
            BotCommand("memory", "查看或清除记忆"),
            BotCommand("effort", "设置思维链深度"),
            BotCommand("prompt", "设置系统提示词"),
            BotCommand("context", "开关上下文记录"),
        ])
    else:
        app.set_bot_commands([])
    if config.config['Other']['Log']['Enable'] == True:
        logger.add(config.config['Other']['Log']['Name'])
        logger.enable(config.config['Other']['Log']['Name'])
    else:
        logger.disable(config.config['Other']['Log']['Name'])

def main():
    global bot_me
    while True:
        try:
            app.start()
            logger.info('Initializing Bot')
            bot_me = app.get_me()
            init()
            loop = asyncio.get_event_loop()
            loop.create_task(init_db())
            for admin_id in su_admin_list:
                try:
                    app.send_message(chat_id = admin_id, text = "`Bot` 启动啦 ~")
                except:
                    pass
            logger.info('Bot Start')
            pyrogram.idle()
        except:
            app.stop()
            loop = asyncio.get_event_loop()
            loop.create_task(close_db())
            os._exit(0)

if __name__ == '__main__':
    main()
