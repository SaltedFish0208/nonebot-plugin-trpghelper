from typing import Optional

from nonebot_plugin_orm import async_scoped_session
from sqlalchemy import or_, select

from .model import Rule, RuleAlias


async def get_rule(session: async_scoped_session, user_input: str) -> Optional[Rule]:
    """
    通过输入的字段查询规则名
    Attr:
        session[async_scoped_session]: 会话
        input[str]: 输入的字符串

    Return:
        Sequence[Rule]: 查询结果
    """
    stmt = select(Rule).where(
        or_(
            Rule.name == user_input.lower(),
            Rule.aliases.any(RuleAlias.alias == user_input.lower())
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
