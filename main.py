import os
import time
import execjs
import base64
import ddddocr
import feapder
import argparse
import configparser


class CQ(feapder.AirSpider):
    __custom_setting__ = dict(
        SPIDER_MAX_RETRY_TIMES=0,
        LOG_LEVEL="INFO"
    )

    def start_requests(self):
        url = "https://ids.gzist.edu.cn/lyuapServer/kaptcha"
        yield feapder.Request(
            url=url,
            callback=self.parse_Login)

    def parse_Login(self, request, response):
        url = "https://ids.gzist.edu.cn/lyuapServer/v1/tickets"
        uid = response.json["uid"]
        code_base64_str = response.json["content"].split(",")[-1]
        code_result = code_ocr(code_base64_str)
        print(f"验证码结果：{code_result}")
        post_data = {
            "username": USERNAME,
            "password": encrypt_password(PASSWORD),
            "service": "https://xsfw.gzist.edu.cn/xsfw/sys/swmzncqapp/*default/index.do",
            "id": uid,
            "code": code_result
        }
        yield feapder.Request(
            url=url,
            callback=self.parse_getCookie,
            data=post_data)

    def parse_getCookie(self, request, response):
        url = "https://xsfw.gzist.edu.cn/xsfw/sys/swmzncqapp/*default/index.do"
        params = {"ticket": response.json["ticket"]}
        yield feapder.Request(
            url=url,
            callback=self.parse_getSelRoleConfig,
            params=params)

    def parse_getSelRoleConfig(self, request, response):
        url = "https://xsfw.gzist.edu.cn/xsfw/sys/swpubapp/MobileCommon/getSelRoleConfig.do"
        cookies = response.cookies
        json = {
            "APPID": "5405362541914944",
            "APPNAME": "swmzncqapp"
        }
        yield feapder.Request(
            url,
            callback=self.parse_done,
            cookies=cookies,
            json=json)

    def parse_done(self, request, response):
        url = "https://xsfw.gzist.edu.cn/xsfw/sys/swmzncqapp/modules/studentCheckController/uniFormSignUp.do"
        cookies = response.cookies
        yield feapder.Request(
            url,
            callback=self.parse,
            cookies=cookies)

    def parse(self, request, response):
        result = response.json["msg"]
        print(fr"查寝结果：{result}")


# 识别验证码
def code_ocr(code_base64_str):
    replace_str = {"o": "0", "O": "0", "l": "1", "i": "1", "I": "1", "s": "5", "S": "5", "b": "6", "B": "8"}
    ocr = ddddocr.DdddOcr(show_ad=False)
    res = ocr.classification(base64_to_byte(code_base64_str))
    for key, value in replace_str.items():
        if key in res:
            res = res.replace(key, value)
    print(f"验证码：{res}")
    code_result = eval(res[0:-1])
    return code_result


# base64字符串转二进制流
def base64_to_byte(s):
    """
    将base64字符串转换为二进制流
    :param s:
    :return byte:
    """
    base64_byte = base64.b64decode(s)
    return base64_byte


def js_from_file(file_name):
    """
    读取js文件
    :return:
    """
    with open(file_name, 'r', encoding='UTF-8') as file:
        result = file.read()
    return result


def encrypt_password(password):
    # 编译加载js字符串
    context1 = execjs.compile(js_from_file('./login.js'))
    encrypted_password = context1.call("encrypt", password)
    return encrypted_password


def get_username_password_from_env():
    username = os.environ.get("loginUserName")
    password = os.environ.get("loginPassword")
    if username and password:
        return username, password
    else:
        return None, None


def get_username_password_from_config(config_file, section):
    config = configparser.ConfigParser()
    config.read(config_file)
    if config.has_section(section):
        username = config.get(section, 'username')
        password = config.get(section, 'password')
        return username, password
    else:
        return None, None


def get_username_password_manually():
    username = input("请输入用户名: ")
    password = input("请输入密码: ")
    return username, password


def get_username_password():
    parser = argparse.ArgumentParser(description='获取用户名和密码')
    parser.add_argument('-e', '--env', action='store_true', help='从环境变量中获取用户名和密码')
    parser.add_argument('-c', '--config', type=str, help='读取配置文件获取用户名和密码')
    args = parser.parse_args()

    if args.env:
        return get_username_password_from_env()
    elif args.config:
        return get_username_password_from_config(args.config, 'loginInfo')
    else:
        return get_username_password_manually()


if __name__ == '__main__':
    # 命令行参数 -e 获取环境变量作为输入，-c 读取配置文件,默认手动输入
    USERNAME, PASSWORD = get_username_password()
    print(f"当前时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}")
    print(f"用户名：{USERNAME}")
    CQ().start()
