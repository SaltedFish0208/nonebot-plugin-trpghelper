from datetime import datetime, timedelta
from typing import Optional

import nonebot_plugin_localstore as storage
import shortuuid
from nonebot import exception, get_plugin_config, require
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_orm import async_scoped_session, get_scoped_session
from sqlalchemy import delete, or_, select
from sqlalchemy.orm import selectinload

require("nonebot_plugin_access_control_api")
require("nonebot_plugin_alconna")

import contextlib

from arclet.alconna import AllParam, CommandMeta
from nonebot.adapters.onebot.v11 import (
    GROUP_ADMIN,
    GROUP_OWNER,
    Bot,
    GroupMessageEvent,
    MessageEvent,
)
from nonebot_plugin_access_control_api.service import create_plugin_service
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    CustomNode,
    Match,
    SupportScope,
    Target,
    UniMessage,
    on_alconna,
)

from .conf_init import reply_generator
from .config import Config
from .db_encap import get_rule
from .model import Broadcast, Group, Post, Rule, RuleAlias
from .to_pic import (
    from_html_to_pic,
    from_html_to_pic_for_group,
    from_html_to_pic_only_content,
)
from .utils import JsonIO
from .validator import (
    BJ_TZ,
    ContentCheckResult,
    DateCheckResult,
    days_from_now,
    validate_content,
    validate_datetime,
)

__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_trpghelper",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)
reply_path = storage.get_plugin_config_file("reply.json")
ALPHABET = "abcdefghigklmnopqrstuvwxyz0123456789"
RULE_MAX_LENGTH = 10

plugin_service = create_plugin_service("nonebot_plugin_trpghelper")

if not reply_path.exists():
    reply_generator(reply_path)

reply = JsonIO(reply_path).load()


#------
#添加规则
#------
add_rule = on_alconna(
    Alconna(
        "添加规则",
        Args["rule", str]
    ),
    permission=SUPERUSER,
    skip_for_unmatch=False
)

@add_rule.handle()
async def _(rule: str, session: async_scoped_session):
    try:
        rule_orm = Rule(name=rule)
        session.add(rule_orm)
        await session.commit()
        await UniMessage.text(reply["add_rule_ok"].format(rule=rule)).send()
    except:  # noqa: E722
        await session.rollback()
        await UniMessage.text(reply["rule_already_exist"].format(rule=rule)).send()


#------
#删除规则
#------
del_rule = on_alconna(
    Alconna(
        "删除规则",
        Args["rule", str]
    ),
    permission=SUPERUSER,
    skip_for_unmatch=False
)

@del_rule.handle()
async def _(rule: str, session: async_scoped_session):
    result = await session.execute(select(Rule).where(Rule.name == rule))
    rule_orm = result.scalar_one_or_none()
    if rule_orm:
        await session.delete(rule_orm)
        await session.commit()
        await UniMessage.text(reply["del_rule_ok"].format(rule=rule)).send()
    else:
        await UniMessage.text(reply["rule_not_exist"].format(rule=rule)).send()


#------
#查询现有规则
#------
query_rule = on_alconna(
    Alconna(
        "现有规则"
    ),
    permission=SUPERUSER,
    skip_for_unmatch=False
)

@query_rule.handle()
async def _(session: async_scoped_session):
    result = await session.execute(select(Rule))
    rules = result.scalars().all()
    await UniMessage.text(reply["existed_rules"].format(
            rules=[
                f"{rule.id}:{rule.name}"
                for rule in rules
                ]
        )).send()


#------
#添加规则别名
#------
add_alias = on_alconna(
    Alconna(
        "添加别名",
        Args["rule", str],
        Args["alias", str]
    ),
    permission=SUPERUSER,
    skip_for_unmatch=False
)

@add_alias.handle()
async def _(rule: str, alias: str, session: async_scoped_session):
    result = await session.execute(select(Rule).where(Rule.name == rule))
    rule_orm = result.scalar_one_or_none()
    if rule_orm:
        try:
            alias_orm = RuleAlias(rule_id=rule_orm.id, alias=alias)
            session.add(alias_orm)
            await session.commit()
            await UniMessage.text(reply["add_alias_ok"].format(
                rule=rule,
                alias=alias
                )).send()
        except:  # noqa: E722
            await session.rollback()
            await UniMessage.text(reply["alias_already_exist"].format(
                rule=rule,
                alias=alias
                )).send()
    else:
        await UniMessage.text(reply["rule_not_exist"].format(rule=rule)).send()


#------
#删除规则别名
#------
del_alias = on_alconna(
    Alconna(
        "删除别名",
        Args["rule", str],
        Args["alias", str]
    ),
    permission=SUPERUSER,
    skip_for_unmatch=False
)

@del_alias.handle()
async def _(rule: str, alias: str, session: async_scoped_session):
    result = await session.execute(select(Rule).where(Rule.name == rule))
    rule_orm = result.scalar_one_or_none()
    if rule_orm:
        result = await session.execute(
            select(RuleAlias).where(
                RuleAlias.alias == alias,
                RuleAlias.rule_id == rule_orm.id
            )
        )
        alias_orm = result.scalar_one_or_none()
        if alias_orm:
            await session.delete(alias_orm)
            await session.commit()
            await UniMessage.text(reply["del_alias_ok"].format(
                rule=rule,
                alias=alias
                )).send()
        else:
            await UniMessage.text(reply["alias_not_exist"].format(
                rule=rule,
                alias=alias
                )).send()
    else:
        await UniMessage.text(reply["rule_not_exist"].format(rule=rule)).send()


#------
#查询规则别名
#-----
query_alias = on_alconna(
    Alconna(
        "查询别名",
        Args["rule", str],
    ),
    permission=SUPERUSER,
    skip_for_unmatch=False
)

@query_alias.handle()
async def _(rule: str, session: async_scoped_session):
    result = await session.execute(
        select(Rule).options(selectinload(Rule.aliases)).where(Rule.name == rule)
)
    rule_orm = result.scalar_one_or_none()
    if rule_orm:
        alias_list = [alias.alias for alias in rule_orm.aliases]
        await UniMessage.text(reply["rule_has_alias"].format(
            rule=rule,
            alias=alias_list
            )).send()
    else:
        await UniMessage.text(reply["rule_not_exist"].format(rule=rule)).send()


#------
#查询规则介绍
#-----
query_introduce = on_alconna(
    Alconna(
        "查规",
        Args["rule", str],
    ),
    skip_for_unmatch=False
)

@query_introduce.handle()
async def _(rule: str, session: async_scoped_session):
    rule_orm = await get_rule(session, rule)
    if rule_orm and rule_orm.introduce:
        await UniMessage.text(rule_orm.introduce).send()
    else:
        await UniMessage.text(reply["nobody_update_rule"].format(rule=rule)).send()


#------
#添加规则介绍
#------
add_introduce = on_alconna(
    Alconna(
        "添加介绍",
        Args["rule", str],
        Args["introduce", AllParam(str)],
        meta=CommandMeta(keep_crlf=True)
    ),
    permission=SUPERUSER,
    skip_for_unmatch=False
)


@add_introduce.handle()
async def _(rule: str, introduce: UniMessage, session: async_scoped_session):
    result = await session.execute(
        select(Rule)
        .outerjoin(Rule.aliases)
        .where(or_(Rule.name == rule, RuleAlias.alias == rule))
    )
    rule_orm = result.scalar_one_or_none()
    if rule_orm:
        rule_orm.introduce = str(introduce)
        await session.commit()
        await UniMessage.text(reply["add_introduce_ok"].format(rule=rule)).send()
    else:
        await UniMessage.text(reply["rule_not_exist"].format(rule=rule)).send()


#------
#删除规则介绍
#------
del_introduce = on_alconna(
    Alconna(
        "删除介绍",
        Args["rule", str],
    ),
    permission=SUPERUSER,
    skip_for_unmatch=False
)

@del_introduce.handle()
async def _(rule: str, session: async_scoped_session):
    result = await session.execute(
        select(Rule)
        .outerjoin(Rule.aliases)
        .where(or_(Rule.name == rule, RuleAlias.alias == rule))
    )
    rule_orm = result.scalar_one_or_none()
    if rule_orm and rule_orm.introduce:
        rule_orm.introduce = None
        await session.commit()
        await UniMessage.text(reply["del_introduce_ok"].format(rule=rule)).send()
    else:
        await UniMessage.text(reply["nobody_update_rule"].format(rule=rule)).send()


#------
#开启/关闭广播功能
#------
broadcast_switch = on_alconna(
    Alconna("控制广播开关"),
    permission=SUPERUSER|GROUP_ADMIN|GROUP_OWNER
)

@broadcast_switch.handle()
async def _(
        bot: Bot,
        event: GroupMessageEvent,
        session: async_scoped_session
    ):
    existing = await session.scalar(
        select(Broadcast).where(Broadcast.group_id == event.group_id)
    )
    if existing:
        await session.delete(existing)
        msg = UniMessage.text(reply["close_broadcast_success"])
    else:
        group_info = await bot.call_api("get_group_info", group_id=event.group_id)
        session.add(
            Broadcast(
                group_id=event.group_id,
                group_name=group_info["group_name"]
            ))
        msg = UniMessage.text(reply["open_broadcast_success"])
    await session.commit()
    await msg.finish()


#------
#发车功能
#------
add_bc = on_alconna(
    Alconna(
        "发车",
        Args["rule?", str],
        Args["content?", str],
        Args["time?", str],
    )
)

@add_bc.handle()
async def _(rule: Match[str], session: async_scoped_session):
    if rule.available:
        # ✅ 字数检查
        if is_cancel(rule.result):
            await UniMessage.text(reply["cancelled"]).finish()
        if len(rule.result) > RULE_MAX_LENGTH:
            await UniMessage.text(
                reply["rule_too_long"].format(length=RULE_MAX_LENGTH)
            ).finish()
        query = await get_rule(session, rule.result)
        if query:
            add_bc.set_path_arg("rule", query.name)
        else:
            add_bc.set_path_arg("rule", rule.result)


@add_bc.got_path("rule", prompt=reply["ask_rule"])
async def _(rule: str, session: async_scoped_session):
    # ✅ 字数检查
    if is_cancel(rule):
        await UniMessage.text(reply["cancelled"]).finish()
    if len(rule) > RULE_MAX_LENGTH:
        await UniMessage.text(
            reply["rule_too_long"].format(length=RULE_MAX_LENGTH)
        ).finish()

    query = await get_rule(session, rule)
    if query:
        add_bc.set_path_arg("rule", query.name)
        await UniMessage.text(reply["find_rule"].format(rule=query.name)).send()
    else:
        await UniMessage.text(reply["not_find_rule"].format(rule=rule)).send()


@add_bc.got_path("content", prompt=reply["publish_tip"])
async def _(content: str):
    if is_cancel(content):
        await UniMessage.text(reply["cancelled"]).finish()

    result = validate_content(content)
    if ContentCheckResult.OK not in result[0]:
        error_list = [r.value for r in result[0]]
        missing = "\n".join(error_list)
        await UniMessage.text(reply["publish_missing_sth"].format(
            missing=missing
            )).finish()


@add_bc.got_path("time", prompt=reply["time_tip"])
async def _(time: str, state: T_State):
    if is_cancel(time):
        await UniMessage.text(reply["cancelled"]).finish()
    days_limit = 14
    result = validate_datetime(time)

    if DateCheckResult.OK not in result[0] or result[1] is None:
        error_list = [r.value for r in result[0]]
        missing = "\n".join(error_list)
        await UniMessage.text(reply["date_missing_sth"].format(
            missing=missing
            )).finish()

    if days_from_now(result[1]) > days_limit:
        await UniMessage.text(reply["time_too_long"].format(
            limit=days_limit
            )).finish()

    state["time"] = result[1]


@add_bc.handle()
async def _(
        event: MessageEvent,
        rule: str,
        content: str,
        state: T_State,
        session: async_scoped_session
    ):
    post = Post(
        code = shortuuid.ShortUUID(alphabet=ALPHABET).random(4),
        user_id = event.user_id,
        user_name = event.sender.nickname,
        rule = rule,
        content = content,
        end_time = state["time"],
        info_pic = None
    )
    post.info_pic = await from_html_to_pic(post)
    # 第一步：写库，失败则回滚并终止
    try:
        session.add(post)
    except:  # noqa: E722
        await session.rollback()

    # 第二步：广播，写库已完成，广播失败不影响发车结果
    result = await session.scalars(select(Broadcast.group_id))
    group_ids = result.all()
    for group in group_ids:
        target = Target(str(group), scope=SupportScope.qq_client)
        try:
            await UniMessage.text(
                reply["new_publish_info"].format(rule=rule)
            ).send(target=target)
        except exception.ActionFailed:
            await session.execute(
                delete(Broadcast).where(Broadcast.group_id == group)
            )
    await session.commit()
    await UniMessage.text(reply["published"]).finish()



#------
#查车功能
#------
query_bc = on_alconna(
    Alconna(
        "查车",
        Args["rule?", Optional[str]]
    )
)

@query_bc.handle()
async def _(bot:Bot, rule: Optional[str], session: async_scoped_session):
    now = datetime.now(BJ_TZ)
    post_oneday = []
    post_after = []
    if rule is None:
        result = await session.execute(select(Post.end_time, Post.info_pic))
        posts = result.all()
    else:
        rule_orm = await get_rule(session, rule)
        if rule_orm is not None:
            rule = rule_orm.name
        result = await session.execute(
            select(Post.end_time, Post.info_pic).where(Post.rule == rule)
        )
        posts = result.all()
    #按时间分拣发车消息
    for post in posts:
        if abs(now - post[0]) <= timedelta(days=1):
            post_oneday.append(UniMessage.image(raw=post[1]))

        else:
            post_after.append(UniMessage.image(raw=post[1]))

    post_oneday.insert(0, UniMessage.text(reply["post_oneday"]))
    post_after.insert(0, UniMessage.text(reply["post_after"]))
    sequence = post_oneday + post_after
    sequence.insert(
        0, UniMessage.text(
            reply["what_rule_you_search"].format(rule=rule or "所有规则")
        )
    )
    await UniMessage.reference(*[
            CustomNode(uid=bot.self_id, name="Amadeus", content=msg)
            for msg in sequence
        ]
    ).finish()


#------
#封车功能
#------
delete_bc = on_alconna(
    Alconna(
        "封车",
        Args["code?", Optional[str]]
    )
)

@delete_bc.handle()
async def _(event: MessageEvent, code: Optional[str], session: async_scoped_session):
    targets = (await session.scalars(
        select(Post).where(Post.user_id == str(event.user_id))
    )).all()

    if not targets:
        await UniMessage.text(reply["no_post_on_you"]).finish()

    if code is None and len(targets) == 1:
        await session.delete(targets[0])
        await session.commit()
        await UniMessage.text(reply["delete_bc_success"]).finish()

    if code is None and len(targets) > 1:
        resp = await delete_bc.prompt(reply["ask_for_uuid"], timeout=30)
        if resp is None:
            await UniMessage.text(reply["timeout"]).finish()
        code = resp.extract_plain_text().strip()

    if code and any(post.code == code for post in targets):
        post = next(p for p in targets if p.code == code)
        await session.delete(post)
        await session.commit()
        await UniMessage.text(reply["delete_bc_success"]).finish()
    elif code:
        await UniMessage.text(reply["wrong_post_code"]).finish()


#------
#强制封车功能
#------
force_del_bc =  on_alconna(
    Alconna(
        "强制封车",
        Args["code", str]
    ),
    permission=SUPERUSER,
    skip_for_unmatch=False
)

@force_del_bc.handle()
async def _(code: str, session: async_scoped_session):
    post = await session.scalar(select(Post).where(Post.code == code))
    if not post:
        await UniMessage.text(reply["no_such_post"]).finish()
    await session.delete(post)
    await session.commit()
    await UniMessage.text(reply["force_del_bc_success"]).finish()


#------
#测试模板功能
#------
test_template = on_alconna(
    Alconna(
        "测试模板",
        Args["content", AllParam(str)],
        meta=CommandMeta(keep_crlf=True)
    ),
    skip_for_unmatch=False
)

@test_template.handle()
async def _(content: UniMessage):
    pic = await from_html_to_pic_only_content(str(content))
    await (
        UniMessage
        .image(raw=pic)
        .text(reply["test_tip"])
    ).finish()


#------
# 取消关键词常量
#------
CANCEL_KEYWORDS = {"取消", "cancel", "quit", "退出"}

def is_cancel(text: str) -> bool:
    return text.strip() in CANCEL_KEYWORDS

#------
# 确认关键词常量
#------
CONFIRM_KEYWORDS = {"确认", "confirm", "确定"}

def is_confirm(text: str) -> bool:
    return text.strip() in CONFIRM_KEYWORDS

#------
# 宣群功能
#------
add_group = on_alconna(
    Alconna(
        "宣群",
        Args["rule?", str],
        Args["content?", str],
    )
)

@add_group.handle()
async def _(rule: Match[str], session: async_scoped_session):
    if rule.available:
        # ✅ 字数检查
        if len(rule.result) > RULE_MAX_LENGTH:
            await UniMessage.text(
                reply["rule_too_long"].format(length=RULE_MAX_LENGTH)
            ).finish()
        query = await get_rule(session, rule.result)
        if query:
            add_group.set_path_arg("rule", query.name)
        else:
            add_group.set_path_arg("rule", rule.result)


@add_group.got_path("rule", prompt=reply["ask_rule_for_longterm"])
async def _(rule: str, session: async_scoped_session):
    if is_cancel(rule):
        await UniMessage.text(reply["cancelled"]).finish()
    if len(rule) > RULE_MAX_LENGTH:
        await UniMessage.text(
            reply["rule_too_long"].format(length=RULE_MAX_LENGTH)
        ).finish()

    query = await get_rule(session, rule)
    if query:
        add_group.set_path_arg("rule", query.name)
        await UniMessage.text(reply["find_rule"].format(rule=query.name)).send()
    else:
        await UniMessage.text(reply["not_find_rule"].format(rule=rule)).send()


@add_group.got_path("content", prompt=reply["publish_tip_for_longterm"])
async def _(content: str):
    if is_cancel(content):
        await UniMessage.text(reply["cancelled"]).finish()

    result = validate_content(content)
    if ContentCheckResult.OK not in result[0]:
        error_list = [r.value for r in result[0]]
        missing = "\n".join(error_list)
        await UniMessage.text(reply["publish_missing_sth"].format(
            missing=missing
        )).finish()


@add_group.handle()
async def _(
        event: MessageEvent,
        rule: str,
        content: str,
        session: async_scoped_session
    ):
    final_confirm = await add_group.prompt(reply["ask_for_sure"], timeout=30)
    if final_confirm is None:
        await UniMessage.text(reply["timeout"]).finish()
    resp = final_confirm.extract_plain_text().strip()
    if is_confirm(resp):
        pass
    else:
        await UniMessage.text(reply["cancelled"]).finish()

    group = Group(
        code=shortuuid.ShortUUID(alphabet=ALPHABET).random(4),
        user_id=event.user_id,
        user_name=event.sender.nickname,
        rule=rule,
        content=content,
        info_pic=None,
        sign_in=datetime.now(BJ_TZ)
    )
    group.info_pic = await from_html_to_pic_for_group(group)
    try:
        session.add(group)
        await session.commit()
    except:  # noqa: E722
        await session.rollback()

    # 广播：通知所有订阅了广播的群（新群建立的消息）
    result = await session.scalars(select(Broadcast.group_id))
    group_ids = result.all()
    for target_gid in group_ids:
        target = Target(str(target_gid), scope=SupportScope.qq_client)
        try:
            await UniMessage.text(
            reply["new_group_pub_info"].format(rule=rule)
                ).send(target=target)
        except exception.ActionFailed:
            await session.execute(
                delete(Broadcast).where(Broadcast.group_id == target_gid)
            )
    await session.commit()
    await UniMessage.text(reply["published_for_longterm"]).finish()


#------
# 查群功能
#------
query_group = on_alconna(
    Alconna(
        "查宣群",
        Args["rule?", Optional[str]]
    )
)

@query_group.handle()
async def _(bot: Bot, rule: Optional[str], session: async_scoped_session):
    if rule is None:
        result = await session.execute(select(Group.info_pic))
        groups = result.all()
    else:
        rule_orm = await get_rule(session, rule)
        if rule_orm is not None:
            rule = rule_orm.name
        result = await session.execute(
            select(Group.info_pic).where(Group.rule == rule)
        )
        groups = result.all()

    sequence: list[UniMessage] = [UniMessage.image(raw=g[0]) for g in groups]
    sequence.insert(
        0, UniMessage.text(
            reply["what_rule_you_search"].format(rule=rule or "所有规则")
        )
    )

    await UniMessage.reference(*[
            CustomNode(uid=bot.self_id, name="Amadeus", content=msg)
            for msg in sequence
        ]
    ).finish()


#------
# 封群功能
#------
delete_group = on_alconna(
    Alconna(
        "停止宣群",
        Args["code?", Optional[str]]
    )
)

@delete_group.handle()
async def _(event: MessageEvent, code: Optional[str], session: async_scoped_session):
    targets = (await session.scalars(
        select(Group).where(Group.user_id == str(event.user_id))
    )).all()

    if not targets:
        await UniMessage.text(reply["no_post_on_you"]).finish()

    if code is None and len(targets) == 1:
        await session.delete(targets[0])
        await session.commit()
        await UniMessage.text(reply["delete_bc_success"]).finish()

    if code is None and len(targets) > 1:
        resp = await delete_group.prompt(reply["ask_for_uuid"], timeout=30)
        if resp is None:
            await UniMessage.text(reply["timeout"]).finish()
        code = resp.extract_plain_text().strip()

    if code and any(g.code == code for g in targets):
        target = next(g for g in targets if g.code == code)
        await session.delete(target)
        await session.commit()
        await UniMessage.text(reply["delete_bc_success"]).finish()
    elif code:
        await UniMessage.text(reply["wrong_post_code_for_longterm"]).finish()


#------
# 强制封群功能
#------
force_del_group = on_alconna(
    Alconna(
        "强制停止宣群",
        Args["code", str]
    ),
    permission=SUPERUSER,
    skip_for_unmatch=False
)

@force_del_group.handle()
async def _(code: str, session: async_scoped_session):
    group = await session.scalar(select(Group).where(Group.code == code))
    if not group:
        await UniMessage.text(reply["no_such_post"]).finish()
    await session.delete(group)
    await session.commit()
    await UniMessage.text(reply["force_del_bc_success"]).finish()


#------
# 签到功能
#------
sign_in_group = on_alconna(
    Alconna(
        "宣群签到",
        Args["code?", Optional[str]]
    )
)

@sign_in_group.handle()
async def _(event: MessageEvent, code: Optional[str], session: async_scoped_session):
    targets = (await session.scalars(
        select(Group).where(Group.user_id == str(event.user_id))
    )).all()

    if not targets:
        await UniMessage.text(reply["no_post_on_you"]).finish()

    # 只有一条记录时无需填写 code
    if code is None and len(targets) == 1:
        target = targets[0]
    elif code is None and len(targets) > 1:
        resp = await sign_in_group.prompt(reply["ask_for_uuid"], timeout=30)
        if resp is None:
            await UniMessage.text(reply["timeout"]).finish()
        code = resp.extract_plain_text().strip()
        target = next((g for g in targets if g.code == code), None)
        if target is None:
            await UniMessage.text(reply["sign_wrong_post_code"]).finish()
    else:
        target = next((g for g in targets if g.code == code), None)
        if target is None:
            await UniMessage.text(reply["sign_wrong_post_code"]).finish()

    now = datetime.now(BJ_TZ)
    # 距离上次签到不足 1 个月时，拒绝重复签到
    if (now - target.sign_in) < timedelta(days=20):
        next_sign = target.sign_in + timedelta(days=20)
        await UniMessage.text(
            reply["sign_in_too_soon"].format(
                next_sign=next_sign.strftime("%Y-%m-%d %H:%M")
            )
        ).finish()

    target.sign_in = now
    await session.commit()
    await UniMessage.text(reply["sign_in_success"]).finish()


#------
# 每分钟检查过期发车
#------
@scheduler.scheduled_job("interval", minutes=1)
async def check_expired_posts() -> None:
    session = get_scoped_session()
    now = datetime.now(BJ_TZ)
    expired = (await session.scalars(
        select(Post).where(Post.end_time <= now)
    )).all()
    for post in expired:
        await session.delete(post)
    if expired:
        await session.commit()


#------
# 每小时检查过期宣群
#------
@scheduler.scheduled_job("interval", hours=1)
async def check_expired_groups() -> None:
    session = get_scoped_session()
    now = datetime.now(BJ_TZ)
    expired = (await session.scalars(
        select(Group).where(Group.sign_in <= now - timedelta(days=30))
    )).all()
    for group in expired:
        await session.delete(group)
    if expired:
        await session.commit()


#------
# 更新车部分
#------
update_bc = on_alconna(
    Alconna(
        "更新车",
        Args["code?", Optional[str]],
        Args["content?", str],
    )
)

@update_bc.handle()
async def _(
    event: MessageEvent,
    code: Optional[str],
    state: T_State,
    session: async_scoped_session
    ):
    targets = (await session.scalars(
        select(Post).where(Post.user_id == str(event.user_id))
    )).all()

    if not targets:
        await UniMessage.text(reply["update_failed_no_post"]).finish()

    if code is None and len(targets) == 1:
        state["posted"] = targets[0]

    if code is None and len(targets) > 1:
        resp = await update_bc.prompt(reply["update_ask_for_uuid"], timeout=30)
        if resp is None:
            await UniMessage.text(reply["timeout"]).finish()
        code = resp.extract_plain_text().strip()

    if code and any(post.code == code for post in targets):
        post = next(p for p in targets if p.code == code)
        state["posted"] = post

    elif code:
        await UniMessage.text(reply["update_wrong_post_code"]).finish()


@update_bc.got_path("content", prompt=reply["update_tip"])
async def _(content: str):
    if is_cancel(content):
        await UniMessage.text(reply["cancelled"]).finish()

    result = validate_content(content)
    if ContentCheckResult.OK not in result[0]:
        error_list = [r.value for r in result[0]]
        missing = "\n".join(error_list)
        await UniMessage.text(reply["publish_missing_sth"].format(
            missing=missing
        )).finish()

@update_bc.handle()
async def _(
        content: str,
        state: T_State,
        session: async_scoped_session
    ):
    post = state["posted"]
    post_new = await session.get(Post, post.code)
    if post_new is None:
        await UniMessage.text(reply["unknown_wrong"]).finish()
    post_new.content = content
    post_new.info_pic = await from_html_to_pic(post_new)
    await session.commit()
    await UniMessage.text(reply["update_success"]).finish()


#------
# 更新宣群部分
#------
update_group = on_alconna(
    Alconna(
        "更新宣群",
        Args["code?", Optional[str]],
        Args["content?", str],
    )
)

@update_group.handle()
async def _(
    event: MessageEvent,
    code: Optional[str],
    state: T_State,
    session: async_scoped_session
    ):
    targets = (await session.scalars(
        select(Group).where(Group.user_id == str(event.user_id))
    )).all()

    if not targets:
        await UniMessage.text(reply["update_failed_no_post"]).finish()

    if code is None and len(targets) == 1:
        state["posted"] = targets[0]

    if code is None and len(targets) > 1:
        resp = await update_bc.prompt(reply["update_ask_for_uuid"], timeout=30)
        if resp is None:
            await UniMessage.text(reply["timeout"]).finish()
        code = resp.extract_plain_text().strip()

    if code and any(post.code == code for post in targets):
        group = next(p for p in targets if p.code == code)
        state["posted"] = group

    elif code:
        await UniMessage.text(reply["update_wrong_post_code"]).finish()


@update_group.got_path("content", prompt=reply["update_tip"])
async def _(content: str):
    if is_cancel(content):
        await UniMessage.text(reply["cancelled"]).finish()

    result = validate_content(content)
    if ContentCheckResult.OK not in result[0]:
        error_list = [r.value for r in result[0]]
        missing = "\n".join(error_list)
        await UniMessage.text(reply["publish_missing_sth"].format(
            missing=missing
        )).finish()

@update_group.handle()
async def _(
        content: str,
        state: T_State,
        session: async_scoped_session
    ):
    post = state["posted"]
    post_new = await session.get(Group, post.code)
    if post_new is None:
        await UniMessage.text(reply["unknown_wrong"]).finish()
    post_new.content = content
    post_new.info_pic = await from_html_to_pic_for_group(post_new)
    await session.commit()
    await UniMessage.text(reply["update_success"]).finish()

#------
# 这里引入一些不应被公开的api
#------
__all__ = ["unfinished"]

with contextlib.suppress(ImportError):
    from . import unfinished
