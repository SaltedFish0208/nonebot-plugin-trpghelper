<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-boardgamehelper

_✨ NoneBot 跑团约车助手 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/SaltedFish0208/nonebot-plugin-boardgamehelper.svg" alt="license">
</a>
<!--
<a href="https://pypi.python.org/pypi/nonebot-plugin-boardgamehelper">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-boardgamehelper.svg" alt="pypi">
</a>
-->
<img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="python">

</div>


## 📖 介绍

该插件是一个 NoneBot2 跑团约车助手插件，提供跑团群招募、发车、封车等功能。

## 💿 安装

<details>
<summary>使用源代码安装</summary>
打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分配置路径

    plugin_dirs = ["path/for/plugin"]

然后将源代码复制到"path/for/plugin"下，完成安装
</details>

<!--<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-boardgamehelper

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-boardgamehelper
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-boardgamehelper
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-boardgamehelper
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-boardgamehelper
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_boardgamehelper"]

</details>--->

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

|               配置项               |  必填 |                       默认值                      | 说明                      |
| :-----------------------------: | :-: | :--------------------------------------------: | :---------------------- |


## 🎉 使用
### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
| :--- | :--- | :---: | :---: | :--- |
| 查车 规则名[可选] | 用户 | 否 | 群聊 | 查看当前正在公开的招募信息，当加入规则名时将会只显示对应的规则的招募信息 |
| 查规 规则名 | 用户 | 否 | 群聊 | 显示某一规则的内容 |
| 查宣群 规则名[可选] | 用户 | 否 | 群聊 | 查看当前正在公开的固定时间限制的招募信息，当加入规则名时将会只显示对应的规则的招募信息 |
| 查询别名 规则名 | 超级用户 | 否 | 群聊 | 查询该规则的所有别名 |
| 测试模板 内容 | 用户 | 否 | 群聊 | 将内容渲染成测试图片 |
| 发车 规则名[可选] | 用户 | 否 | 群聊 | 发布一条新的招募信息 |
| 封车 ID[可选] | 用户 | 否 | 群聊 | 关闭自己的招募，当有多条招募时需加入ID |
| 更新车 ID[可选] | 用户 | 否 | 群聊 | 更新一条招募的内容 |
| 更新宣群 ID[可选] | 用户 | 否 | 群聊 | 更新一条固定时间限制的招募的内容 |
| 控制广播开关 | 超级用户/群主/管理员 | 否 | 群聊 | 开启/关闭招募广播 |
| 强制封车 | 超级用户 | 否 | 群聊 | 强制关闭一条招募 |
| 强制停止宣群 | 超级用户 | 否 | 群聊 | 强制关闭一条招募 |
| 删除别名 规则名 别名 | 超级用户 | 否 | 群聊 | 为规则删除别名 |
| 删除规则 规则名 | 超级用户 | 否 | 群聊 | 在数据库中删除规则条目以及其相关的所有内容 |
| 删除介绍 规则名 | 超级用户 | 否 | 群聊 | 为规则删除介绍 |
| 添加别名 规则名 别名 | 超级用户 | 否 | 群聊 | 为规则增加别名 |
| 添加规则 规则名 | 超级用户 | 否 | 群聊 | 向数据库中添加规则条目 |
| 添加介绍 规则名 介绍内容 | 超级用户 | 否 | 群聊 | 为规则增加或更新介绍 |
| 停止宣群 ID[可选] | 用户 | 否 | 群聊 | 关闭自己的固定时间限制的招募，当有多条招募时需加入ID |
| 现有规则 | 超级用户 | 否 | 群聊 | 列出数据库存储的所有规则 |
| 宣群 规则名[可选] | 用户 | 否 | 群聊 | 发布一条时间限制固定为30天的、新的招募信息 |
| 宣群签到 ID[可选] | 用户 | 否 | 群聊 | 将固定时间限制的招募重置到30天，当有多条招募时需加入ID |

## 一些提示
参考[nonebot->数据存储](https://nonebot.dev/docs/best-practice/data-storing)确认插件数据默认的存储位置

回复文件存放在config目录

## 📋 TODO