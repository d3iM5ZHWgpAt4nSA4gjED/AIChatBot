# AIBot

AIBot 是一个基于 `Telegram Bot API` 与 OpenAI 兼容 `/chat/completions` 接口的 AI 对话机器人

它支持流式回复、上下文、图片与文件传入、模型工具调用、网络搜索、网页抓取、群组白名单、内联模式与访客模式等功能

> AIBot 本身不提供模型、API Key、Telegram Bot Token 或授权 Token 这些内容都需要自行准备与配置


## 关于数据安全

AIBot 的配置保存在本地 `config.yaml`，对话上下文保存在本地 `Chat.db`。日志功能开启时，日志会写入配置中 `Other.Log.Name` 指定的本地文件

机器人会连接以下服务：

- Telegram 服务器
- 你在 `AI.Vendor` 中配置的模型服务
- 开启网页搜索时的 DuckDuckGo，以及可选的 Tavily
- 开启链接请求或模型调用 `web_fetch` 时，模型指定的网页地址

图片和文件会在内存中下载、编码后发送给模型服务；请只向你信任的模型提供商发送敏感内容

`Token`、`Bot.ApiId`、`Bot.ApiHash`、`Bot.Token`、`Other.Password` 等敏感配置不能通过 `/get` 读取，但仍应妥善保存 `config.yaml`，不要提交到公开仓库


## 机器人安装方法

由于一些原因 机器人目前分为开源和闭源两个版本 具体区别如下

||js代码执行|配置可视化面板|配置热重载|版本更新介绍|离线授权|
|---|---|---|---|---|---|
|开源版本|✅|❌|❌|❌|❌|
|闭源版本|❌|✅|✅|✅|✅|

闭源版本直接以二进制单文件形式提供 目前仅支持 `Linux x86/Windows x86` 系统
如果需要其他架构的打包 请私聊我

> 

### 搭建

> 这里仅说明进行开源版本的搭建方法。关于如何持久化运行这里不会详细说，你可以参考 `screen`、`pm2`、`systemd`、Windows 任务计划程序等方法。

> 这里以 `Debian` 系统为例

由于 curl-cffi 从 0.15.0 才支持 AsyncSession 的 Retry ，而 0.15.0 的最低 Python 版本要求为 `3.10` 所以你需要最低 `3.10` 版本的 Python 才可以正常运行本机器人。 

你首先可能需要安装软件包

```bash
apt install git python3-pip -y
```

然后使用 `git clone` 拉取项目

安装依赖

```bash
pip install -r requirements.txt
```
> 对于高版本且非虚拟环境搭建的Bot你可能需要加上 `--break-system-packages`

由于本项目使用的 js2py 不维护也不 merge pr，对于 3.11 及以上的 Python 版本，你可能需要

```bash
git clone https://github.com/felixonmars/Js2Py/ -b py3.12

cd Js2Py

pip install .
```

3.13 要用 `http://github.com/a-j-albert/Js2Py---supports-python-3.13`

对于 3.11 以下的直接使用 `pip install js2py` 即可。

这样才能正常使用代码执行功能。

> 机器人的代码执行功能不带有执行命令和读取写入文件的的功能，仅会执行AI编写的 js 代码并返回结果，除非出现提权漏洞。

### 机器人配置说明

> 建议先参看 `readme.config.yaml` 内的逐项注释，也可以使用 `example.config.yaml` 的最简配置。首次加载时，Bot 会按默认值补全可选项。

#### 必要配置

`SuAdmin`：超级管理员的 Telegram 用户 ID 列表。不填入则 Bot 无法启动。

`Token`：闭源版本特有配置，Bot 的授权 Token。不填入或校验失败则 Bot 无法启动。

`Bot.ApiHash` 与 `Bot.ApiId`：在 <https://my.telegram.org/apps> 创建应用后获取。

`Bot.Token`：在 [@BotFather](https://t.me/BotFather) 创建 Bot 后获取。

`AI.Vendor`：至少需要配置一个模型提供商与模型名，同时将某个已配置的模型填入 `AI.DefaultModel`。模型服务目前需要支持 OpenAI 兼容的 `/chat/completions` 接口与流式响应。

最小可用示例：

```yaml
SuAdmin:
- 123456789
Token: 授权Token
Bot:
  ApiHash: 你的ApiHash
  ApiId: 你的ApiId
  Token: 你的BotToken
AI:
  Vendor:
    MyVendor:
      BaseUrl: https://example.com/v1
      Key: sk-xxxxxxxx
      Model:
      - gpt-5.5
  DefaultModel: gpt-5.5
```

#### 模型提供商配置

每个提供商由名称、接口地址、密钥和模型列表构成：

```yaml
AI:
  Vendor:
    MyVendor:
      BaseUrl: https://example.com/v1
      Key: sk-xxxxxxxx
      Model:
      - model-a
      - model-b
```

`BaseUrl` 填写 API 根地址，程序会自动拼接 `/chat/completions`。

如果不同提供商中有同名模型，后配置的同名模型会覆盖前面的映射。可以给模型名增加任意提供商前缀以区分，实际请求时前缀会自动去除：

```yaml
AI:
  Vendor:
    VendorA:
      BaseUrl: https://vendor-a.example/v1
      Key: sk-a
      Model:
      - VendorA:gpt-5.5
    VendorB:
      BaseUrl: https://vendor-b.example/v1
      Key: sk-b
      Model:
      - VendorB:gpt-5.5
  DefaultModel: VendorA:gpt-5.5
```

#### 可选配置

其他配置大多为可选，不影响基础对话功能。关于完整字段、默认值和说明可以参考 `readme.config.yaml`。

常用配置如下：

| 配置项 | 说明 |
| --- | --- |
| `Bot.CreateSession` | 是否使用内存 Session。默认开启；开启后不会在本地保存 Pyrogram Session 文件。 |
| `Bot.Proxy` | Bot 连接 Telegram 的 Pyrogram 代理配置，类型为 `dict`。 |
| `Bot.HideCommand` | 是否清空 Telegram 命令面板。 |
| `Network.Proxy` | 模型请求、网页搜索和网页抓取使用的代理列表，程序会轮询使用。 |
| `Network.Timeout` / `Retry` | 外部请求超时时间与重试次数。 |
| `Network.Thread` | `/prune` 模型测活的并发数量。 |
| `AI.DefaultModel` | 默认使用的模型名称，必须出现在 `AI.Vendor.*.Model` 中。 |
| `AI.SystemPrompt` | 全局系统提示词。 |
| `AI.ExtraSystemPrompt` | 每次请求附加的动态提示词，可使用 `{cur_date}`、`{cur_time}`、`{cur_datetime}`、`{timezone}`、`{model_name}`、`{assistant_name}`。 |
| `AI.ReasoningEffort` | 默认推理预算，可填 `auto`、`none`、`minimal`、`low`、`medium`、`high`、`xhigh`。模型服务需要支持该字段。 |
| `AI.MaxContext` | 每个会话保留的最大历史消息数。 |
| `AI.MaxFileSize` | 可传给模型的单个图片或文档最大体积，单位为 MB。 |
| `Other.MaxTextLength` | Bot 单条消息展示的最大长度；超出后会显示翻页按钮。 |
| `Other.AvoidJoinGroups` | 防拉群模式：`0` 关闭、`1` 仅管理员可拉群、`2` 仅超管可拉群。 |
| `Other.Intro` | `/start` 时发送的机器人介绍。 |
| `Other.Password` | `/stop` 命令的关机密码。 |

#### 对话、图片与文件

`AI.FileSupport` 控制是否允许把 Telegram 文档发送给模型；图片、图片文档与贴纸会作为图片内容传给模型。模型服务需要自行支持相应的多模态内容格式。

用户可直接发送图片或文档并附带 `/chat`，也可以回复一条含有文字、图片或文件的消息来提问。媒体组会一起传给模型。

#### 工具调用

开启 `AI.Tool.Enable` 后，模型可调用以下 OpenAI function tools：

- `web_fetch`：抓取指定 URL 的内容；由 `AI.Tool.FetchURL.Enable` 控制。
- `web_search`：搜索网页；由 `AI.Tool.WebSearch.Enable` 控制。

网页搜索会优先尝试 DuckDuckGo；配置 `AI.Tool.WebSearch.ApiKey` 后，还会在 DuckDuckGo 无结果时使用 Tavily。`AI.Tool.MaxToolCall` 用于限制一次对话允许的最大工具调用轮数。

工具会访问模型要求的 URL 或搜索词，请仅对可信模型提供商开启此功能。

#### 自动回复与群组身份识别

`AI.AutoReply` 开启后，管理员或已加入白名单的群组可以通过以下方式触发对话：

- 私聊直接发送消息；
- 在消息中提及 `@机器人用户名` 或机器人名称；
- 回复 Bot 的消息；
- 在群组消息中命中 `AI.WakeWord` 的正则表达式。

`AI.IDRecognition.Enable` 开启后，在普通消息的群聊中，发送者名称和正文会按 `AI.IDRecognition.Format` 组合，并附加 `AI.IDRecognition.Prompt` 给模型，使模型能够区分不同发言者。

#### 白名单群组

`AI.WhiteList` 中的群组 ID 可以使用 `/chat`、`/clear`、`/page` 等基础对话功能，即使发送者不是管理员。超级管理员可直接在群内使用 `/trust` 添加当前群，使用 `/distrust` 移除当前群。


## 权限相关

### 超级管理

超级管理员是最大的管理层级，可以授权或取消普通管理员、管理白名单群组、读写配置、重载配置、退出群组、关闭 Bot 等。

配置文件使用 YAML 数组；即使只有一个超管，也需要保留 `- ` 与其后的空格：

```yaml
SuAdmin:
- 11111
- 22222
```

### 普通管理

普通管理员可以与模型对话、切换模型、切换个人上下文、设置个人系统提示词和推理预算，并查看或读取模型可用性测试结果。

超管使用 `/grant` 授权普通管理员，使用 `/ungrant` 取消授权。超管本身自动具有普通管理员权限。

### 白名单群组

白名单群组不是用户权限。它允许群中的成员调用基础对话命令与自动回复功能，但模型、提示词、上下文等个人设置命令仍仅限管理员使用。

### 游客

游客可以使用 `/help`、`/version`、`/stats` 和 `/start` 等公共信息指令，但不能发起模型对话。


## 机器人使用方法

### 指令

#### 公共指令

##### /help

获取帮助菜单

##### /version

获取版本信息

##### /stats

查询自身权限状态。

管理员还会看到当前对话数量、上下文状态、模型、推理预算，以及搜索、链接请求、文件读取等功能是否开启；超管还会看到授权限制与功能授权状态。

##### /start

发送 `Other.Intro.Text` 配置的介绍文本；需要 `Other.Intro.Enable` 开启。

#### 对话指令

> 仅普通管理、超级管理或白名单群组可调用。

##### /chat <内容>

向当前模型发送消息。可以直接使用 `/c`：

```text
/chat 帮我解释这一段代码
/c 你好
```

模型回复使用流式更新。回复过长时可通过按钮或 `/page` 翻页，生成过程中可以点击“停止”取消。

##### /clear

清除当前聊天的上下文记录。

##### /page <页数>

回复 Bot 的长消息后可以进行页数跳转，也可以使用 `/p`。

```text
/page 2
```

#### 普通管理指令

> 仅普通管理、超级管理可调用。

##### /model <可选:模型名>

不带参数时显示模型选择面板；带参数时直接切换自己的模型。

```text
/model
/model gpt-5.5
```

##### /context

开关自己的私聊上下文记录。群聊上下文会持续记录，不受此开关影响。

##### /prompt <可选:系统提示词>

设置自己的系统提示词；不带参数时清除个人系统提示词，恢复使用全局 `AI.SystemPrompt`。

```text
/prompt 请使用简洁的中文回答
```

##### /memory <可选:清除长期记忆>

查看或清除长期记忆。

当仅使用 `/memory` 时查看个人及本群的长期记忆。

使用 `/memory clear` 清除个人长期记忆。

管理员可使用 `/memory clear chat` 清除本聊天的记忆。

##### /effort

打开推理预算选择面板。`/reason` 与 `/reasoneffort` 也可以使用。

##### /prune <可选:正则关键词>

普通管理员调用时只会查看最近一次模型可用性测试结果；超级管理员调用时会测试模型接口，并展示可用状态和请求耗时。

可以传入正则关键词，只检测匹配的模型：

```text
/prune gpt
```

#### 超级管理指令

> 仅超级管理可调用。

##### /grant <可选:id>

回复一个用户将其授权为管理员，也可在命令后跟着一个或多个 id，会被写入到 `Admin`。

```text
/grant 123456789 987654321
```

##### /ungrant <可选:id>

回复一个用户将其取消管理员，也可在命令后跟着一个或多个 id，会被从 `Admin` 移除。

##### /grantscan

扫描全部管理员，将死号清除。

##### /trust

在群内发送后会将此群组加入白名单。

##### /distrust

取消此群组的白名单。

##### /reload

从 `config.yaml` 重新加载配置，并刷新模型列表与 Telegram 命令面板。

##### /get <配置路径>

对配置文件进行读取。你需要对 `config.yaml` 配置文件非常熟悉，不同级的路径需要用 `.` 分开。例如，你想获取 默认模型 的值：

```
/get AI.DefaultModel
返回：
✔️ 读取配置成功啦 ~

描述 默认模型
键 AI.DefaultModel
值 gpt-5
```

再例如，你想获取工具调用是否开启：
```
/get AI.Tool.Enable
返回：
✔️ 读取配置成功啦 ~

描述 是否开启工具调用
键 AI.Tool.Enable
值 True
```
```

读取顶层配置可使用 `.` 或 `Config`。敏感字段不会被返回。

##### /set <配置路径> <值>

同上，只是这次我们设置这个值。空格会分隔参数，需要输入字面量 `\s` 来表示一个空格。

```text
/set AI.DefaultModel gpt-5.5
/set AI.AutoReply true
/set Other.MaxTextLength 3000
/set AI.SystemPrompt 你是一个\s有帮助的助手
```

##### /config <可选:配置路径>

直接使用 Bot 面板来对配置文件进行操作。可以浏览配置项、修改可编辑的值、切换布尔值、添加或删除列表元素、恢复默认值。该功能是否可用还取决于授权 Token 的功能权限。

```text
/config
/config AI
```

##### /id

显示当前聊天与自己的 Telegram ID；回复一条消息使用时还会显示被回复用户的 ID、语言和数据中心信息。

##### /leave

从此群聊中离开。

##### /stop <密码>

关闭 Bot 的程序，需要密码，密码为配置文件中 `Other.Password` 设置的文本：

```text
/stop 1145141919810
```


## 特殊模式

### 内联模式

开启后，仅管理员可以在任意聊天输入：

```text
@机器人用户名 需要发送给模型的内容
```

选择结果后，Bot 会在当前聊天中流式生成回答。内联模式使用自己的上下文记录。

还需要在 [@BotFather](https://t.me/BotFather) 中对 Bot 使用 `/setinline` 并设置内联提示文本，Telegram 才会显示内联入口。

### 访客模式

访客模式使用 Pyrogram 的 guest message 能力，让管理员或白名单群组在对应入口中发送消息、使用 `/clear`、`/stats`、`/model`、`/effort`、`/trust`、`/distrust` 等操作。


## 数据文件与更新

- `config.yaml`：运行配置；首次加载后会自动补全可选字段。
- `Chat.db`：SQLite 对话历史数据库；按聊天 ID 分表保存上下文。
- `Bot.log`：默认日志文件；可通过 `Other.Log` 调整或关闭。
- `AIBot.session`：仅在关闭 `Bot.CreateSession` 时可能由 Pyrogram 创建。

程序启动后会向超级管理员发送启动通知；版本升级时也会向超级管理员发送更新说明。更新 `main.py` 后建议检查 `readme.config.yaml` 是否有新增配置项，再执行 `/reload` 或重启 Bot。


## 注意事项

- `config.yaml` 中的 ID 应填写数字，而不是 Telegram 用户名。
- `AI.DefaultModel` 必须与 `AI.Vendor.*.Model` 中配置的名称完全一致。
- 若未配置模型或默认模型，发起对话时无法正确选择模型。
- 网络搜索、网页抓取、图片和文件功能需要模型提供商支持相应的 OpenAI 兼容格式。
- 配置文件中有语法错误或类型不正确时，Bot 会拒绝加载该配置；可以对照 `readme.config.yaml` 修正。
