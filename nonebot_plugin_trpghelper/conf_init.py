from typing import TYPE_CHECKING

from .utils import JsonIO

if TYPE_CHECKING:
    from pathlib import Path


def reply_generator(path: "Path") -> None:
    json_file = JsonIO(path)
    reply = {
    "ask_rule": "接下来请输入您要发车的规则\n输入取消以结束流程",
    "publish_tip": "接下来请输入开团信息，例：\n[游戏规则] 老派要典\n[跑团方式] 文字\n[平台] QQ\n[模组]橡树洞\n[开团时间]每周五晚上8点\n[人数] 1=3\n[导引剧情] 很久很久以前\n[GM名称与联系方式] XX-Q号或Q群号 \n请提前准备好录入信息粘贴，1分后超时后您需要重新发车\n不再有必填项目，且现支持html语言，如要使用请私聊'/测试模板 发车内容'优先调试再发车。\n输入取消以结束流程",
    "time_tip": "接下来请输入自动封团的时间，如\n18:00\n2026-01-01 19:19\n当您仅输入时间时，默认为当天\n输入取消以结束流程",
    "nobody_update_rule": "暂无人录入该规则的介绍",
    "rule_already_exist": "添加失败！规则'{rule}'已存在",
    "add_rule_ok": "添加规则'{rule}'成功",
    "rule_not_exist": "失败！规则'{rule}'不存在",
    "del_rule_ok": "删除规则'{rule}'成功",
    "existed_rules": "当前存在以下规则：\n{rules}",
    "add_alias_ok": "为规则'{rule}'添加别名'{alias}'成功",
    "alias_already_exist": "为规则'{rule}'添加别名'{alias}'失败：别名已存在",
    "del_alias_ok": "为规则'{rule}'删除别名'{alias}'成功",
    "alias_not_exist": "为规则'{rule}'删除别名'{alias}'失败：别名不存在",
    "rule_has_alias": "规则'{rule}'拥有以下别名：\n{alias}",
    "add_introduce_ok": "为规则'{rule}'添加介绍成功",
    "del_introduce_ok": "为规则'{rule}'删除介绍成功",
    "find_rule": "规则确认为：'{rule}'",
    "not_find_rule": "机器人尚未录入该规则，将以'{rule}'为规则名发布公告",
    "publish_missing_sth": "您的发团信息缺少条目：\n{missing}\n请检查后重新发团",
    "date_missing_sth": "您的结束时间有以下问题：\n{missing}\n请检查后重新发团",
    "time_too_long": "超过{limit}天的车请使用'/宣群 <规则>'命令",
    "open_broadcast_success": "本群开启了全群广播",
    "close_broadcast_success": "本群关闭了全群广播",
    "published": "您的发车信息已经存入数据库并广播至其他群",
    "post_oneday": "以下为今日招募截止的团",
    "post_after": "以下为14天以内结束招募的团",
    "what_rule_you_search": "您正在查询的规则是：{rule}",
    "no_post_on_you": "封团失败：\n团库里没有您发的团呢",
    "delete_bc_success": "封团完成",
    "ask_for_uuid": "请输入想要封团的团ID",
    "timeout": "超时",
    "wrong_post_code": "您并非此ID的团的发车人，请确认后重新封车",
    "force_del_bc_success": "强制封团成功",
    "no_such_post": "强制封团失败，车库里没有该编号的团",
    "test_tip": "不要太频繁的使用机器人测试模板哦，会有风控风险",
    "sign_in_too_soon": "签到太频繁啦！下次可签到时间：{next_sign}",
    "sign_in_success": "签到成功！本条宣群消息已续期 30 天 ",
    "new_publish_info": "🔔请/查车！新「{rule}」车开放载客🔔",
    "ask_rule_for_longterm": "接下来请输入您要发车的规则\n\n输入取消以结束流程",
    "publish_tip_for_longterm": "接下来请输入宣群信息\n请提前准备好录入信息粘贴，1分后超时后您需要重新发车\n不再有必填项目，且现支持html语言\n\n输入取消以结束流程",
    "published_for_longterm": "您的宣群信息已经存入数据库",
    "sign_wrong_post_code": "签到失败，你不是这个ID的发车人",
    "cancelled": "已取消",
    "rule_too_long": "规则字数太长啦！请控制在{length}以内",
    "new_group_pub_info": "🔔请/查宣群！有新的「{rule}」宣群消息🔔",
    "update_failed_no_post": "更新失败！没有发现您的车车",
    "update_ask_for_uuid": "请输入想要更新的团ID",
    "update_wrong_post_code": "您并非此ID的团的发车人，请确认后重新更新",
    "update_tip": "现在请输入更新后的内容",
    "unknown_wrong": "发生未知错误",
    "update_success": "更新完成",
    "ask_for_sure": "确认宣群内容无误吗，输入'确认'进行宣群，输入其他任意内容重新宣群",
    "count_tip": "当前有 {count} 个条目",
    "file_not_found": "未找到编号为 {file} 的文档",
    "you_are_looking_at": "你正在查看编号为 {file} 的文档",
    "you_are_already_request": "你今天已经请求过文档了，再给你看一遍\n你正在查看编号为 {file} 的文档"
    }

    json_file.save(reply)
