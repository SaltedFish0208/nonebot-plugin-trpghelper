import re

from nonebot_plugin_htmlrender import render_html

from .model import Group, Post


async def from_html_to_pic(post: Post) -> bytes:
    content = post.content
    if re.search(r"<[a-zA-Z][^>]*>", content):
        pass
    else:
        content = content.replace("\r\n", "<br>").replace("\r", "<br>").replace("\n", "<br>")
    end_time = post.end_time
    end_time = end_time.strftime("%Y-%m-%d %H:%M")
    msg = f"""
        <head>
        <style>
            body {{
                padding: 16px !important;
                width: 820px !important;
                box-sizing: border-box !important;
            }}
            body > hr {{
                border: none !important;
                border-top: 1px solid #ccc !important;
                margin: 12px 0 !important;
            }}
            body > h2 {{
                font-size: 1.5em !important;
                font-weight: bold !important;
                margin: 0.83em 0 !important;
            }}
            body > .meta {{
                font-size: 13px !important;
            }}
        </style>
        </head>

        <body>
        <h2>{post.rule}</h2>
        <hr />
        {content}<br />
        <hr />
        <div class="meta">
            结束时间： {end_time}<br />
            发车人：{post.user_name}({post.user_id})<br />
            车车ID：{post.code}<br />
        </div>
        </body>
    """
    image = await render_html(html=msg, width=820, height=None)
    return bytes(image)


async def from_html_to_pic_only_content(content: str) -> bytes:
    if re.search(r"<[a-zA-Z][^>]*>", content):
        pass
    else:
        content = content.replace("\n", "<br>")
    msg = f"""
        <head>
                <style>
            body {{
                padding: 16px !important;
                width: 820px !important;
                box-sizing: border-box !important;
            }}
            body > hr {{
                border: none !important;
                border-top: 1px solid #ccc !important;
                margin: 12px 0 !important;
            }}
            body > h2 {{
                font-size: 1.5em !important;
                font-weight: bold !important;
                margin: 0.83em 0 !important;
            }}
            body > .meta {{
                font-size: 13px !important;
                color: #555 !important;
                line-height: 1.8 !important;
                font-family: sans-serif !important;
            }}
        </style>
        </head>

        <body>
        <h2>测试规则</h2>
        <hr />
        {content}<br />
        <hr />
        结束时间： 难说<br />
        发车人：我不到啊<br />
        车车ID：现在还没有哦<br />
        </body>
    """
    image = await render_html(html=msg, width=820, height=None)
    return bytes(image)


async def from_html_to_pic_for_group(group: Group) -> bytes:
    content = group.content
    if re.search(r"<[a-zA-Z][^>]*>", content):
        pass
    else:
        content = content.replace("\n", "<br>")
    msg = f"""
        <head>
        <style>
            body {{
                padding: 16px !important;
                width: 820px !important;
                box-sizing: border-box !important;
            }}
            body > hr {{
                border: none !important;
                border-top: 1px solid #ccc !important;
                margin: 12px 0 !important;
            }}
            body > h2 {{
                font-size: 1.5em !important;
                font-weight: bold !important;
                margin: 0.83em 0 !important;
            }}
            body > .meta {{
                font-size: 13px !important;
            }}
        </style>
        </head>

        <body>
        <h2>{group.rule}</h2>
        <hr />
        {content}<br />
        <hr />
        <div class="meta">
            发车人：{group.user_name}({group.user_id})<br />
            宣群ID：{group.code}<br />
        </div>
        </body>
    """
    image = await render_html(html=msg, width=820, height=None)
    return bytes(image)
