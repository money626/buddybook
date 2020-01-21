from django import template
from datetime import datetime
from django.utils.safestring import mark_safe
from asyncio_socket import json_and_dict as jd
from asyncio_socket import asyncio_server

register = template.Library()

@register.filter(is_safe=True)
def date(value):
    return_value = datetime.strptime(value, "%Y.%m.%d.%H.%M.%S")
    return_value = return_value.strftime("%Y{y}%m{m}%d{d}{br}%H{H}%M{M}%S{S}").format(y="年", m="月", d="日",br="<br>", H="時", M="分", S="秒")
    return mark_safe(return_value)

@register.filter(is_safe=True)
def comments(comment_list):
    return_value = []
    handler = asyncio_server.handler

    for comment_id in comment_list:
        comment = jd.json2dict(f'../learn/jsons/{comment_id}.json')
        user_data = handler.user_data_dict.get(comment['owner_ID'])
        comment_html = f'<li><div class="comment"><table><tbody><tr><td><img src="/buddybook/media/{user_data["profile_picture"]}"></td><td colspan="4">{user_data["user_name"]}</td><td></td></tr><tr><td colspan="6" class="contents">{comment["content"]}</td></tr><tr><td colspan="3" class="like {comment["article_ID"]}" onclick="like("{comment["article_ID"]}")">like</td><td colspan="3" class="make_comment" onclick="comment("{comment["article_ID"]}")">Comment</td></tr></tbody></table></div></li>'
        comment_html += f'<li><ul class="{comment["article_ID"]}" style="display: none;"><li><div class="add_comment"><table><tbody><tr><td colspan="6"><input type="text" class="{comment["article_ID"]}"></td><td class="send_comment" onclick="send_comment("{comment["article_ID"]}")">Send</td></tr></tbody></table></div></li></li></ul>'
        return_value.append(comment_html)
    return mark_safe("".join(return_value))


