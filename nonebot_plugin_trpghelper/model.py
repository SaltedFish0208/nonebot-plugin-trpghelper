from datetime import datetime
from typing import Optional

from nonebot_plugin_orm import Model
from sqlalchemy import INTEGER, DateTime, ForeignKey, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


# 以下为存储招募信息的内容
class Post(Model):
    __tablename__ = "post"
    code: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String)
    user_name: Mapped[str] = mapped_column(String)
    rule: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(String)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    info_pic: Mapped[bytes] = mapped_column(LargeBinary)


class Group(Model):
    __tablename__ = "group"
    code: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String)
    user_name: Mapped[str] = mapped_column(String)
    rule: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(String)
    info_pic: Mapped[bytes] = mapped_column(LargeBinary)
    sign_in: Mapped[datetime] = mapped_column(DateTime(timezone=True))

# 以下为广播相关的内容
class Broadcast(Model):
    __tablename__ = "broadcast_groups"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(INTEGER)
    group_name: Mapped[str] = mapped_column(String)


# 以下为规则相关的内容
class RuleAlias(Model):
    __tablename__ = "rule_alias"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("rule.id", ondelete="CASCADE"))
    alias: Mapped[str] = mapped_column(String, index=True, unique=True)
    rule = relationship("Rule", back_populates="aliases")


class Rule(Model):
    __tablename__ = "rule"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, index=True, unique=True)
    aliases = relationship(RuleAlias, back_populates="rule")
    introduce: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class LearnCount(Model):
    __tablename__ = "learn_count"
    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    last_request: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_pic: Mapped[str] = mapped_column(String)

class InspirationCount(Model):
    __tablename__ = "inspiration_count"
    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    last_request: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_pic: Mapped[str] = mapped_column(String)
