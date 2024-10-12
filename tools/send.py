from feapder.utils.tools import *
from tools.message import *


def send_msg(msg, level="DEBUG", message_prefix="", keyword=""):
    if setting.WARNING_LEVEL == "ERROR":
        if level.upper() != "ERROR":
            return

    if setting.DINGDING_WARNING_URL:
        dingding_warning(keyword + msg, message_prefix=message_prefix)

    if setting.EMAIL_RECEIVER:
        title = message_prefix or msg
        if len(title) > 50:
            title = title[:50] + "..."
        email_warning(msg, message_prefix=message_prefix, title=title)

    if setting.WECHAT_WARNING_URL:
        wechat_warning(keyword + msg, message_prefix=message_prefix)

    if setting.FEISHU_WARNING_URL:
        feishu_warning(keyword + msg, message_prefix=message_prefix)

    if setting.QMSG_WARNING_URL:
        qmsg_warning(keyword + msg, message_prefix=message_prefix)


if __name__ == '__main__':
    send_msg("123")
