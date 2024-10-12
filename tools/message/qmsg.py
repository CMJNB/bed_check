from feapder.utils.tools import *


def qmsg_warning(
        message,
        message_prefix=None,
        rate_limit=None,
        url=None,
        user_qq=None,
        bot_qq=None
):
    """qmsg报警"""

    # 为了加载最新的配置
    rate_limit = rate_limit if rate_limit is not None else setting.WARNING_INTERVAL
    url = url or setting.QMSG_WARNING_URL
    user_qq = user_qq or setting.QMSG_WARNING_QQ
    bot_qq = bot_qq or setting.QMSG_WARNING_BOT

    if isinstance(user_qq, list):
        user_qq = ','.join(map(str, user_qq))

    if not all([url, message]):
        return

    if reach_freq_limit(rate_limit, url, user_qq, message_prefix or message):
        log.info("报警时间间隔过短，此次报警忽略。 内容 {}".format(message))
        return

    data = {
        "msg": message,
        "qq": user_qq,
        "bot": bot_qq,
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(
            url, headers=headers, data=json.dumps(data).encode("utf8")
        )
        result = response.json()
        response.close()
        if result.get("code") == 0:
            return True
        else:
            raise Exception(result.get("reason"))
    except Exception as e:
        log.error("报警发送失败。 报警内容 {}, error: {}".format(message, e))
        return False
