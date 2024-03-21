import os
import time
import execjs
import base64
import ddddocr
import feapder
import argparse
import configparser
import requests


class CQ(feapder.AirSpider):
    __custom_setting__ = dict(
        SPIDER_MAX_RETRY_TIMES=3,
        LOG_LEVEL="INFO",
    )

    def start_requests(self):
        code_url = "https://ids.gzist.edu.cn/lyuapServer/kaptcha"
        yield feapder.Request(url=code_url, callback=self.parse_tryLogin)

    def parse_tryLogin(self, request, response):
        login_url = "https://ids.gzist.edu.cn/lyuapServer/v1/tickets"
        uid = response.json["uid"]
        code_base64_str = response.json["content"].split(",")[-1]
        code_result = self.code_ocr(code_base64_str)
        print(f"验证码结果：{code_result}")
        post_data = {
            "username": USERNAME,
            "password": self.encrypt_password(PASSWORD),
            "service": "https://xsfw.gzist.edu.cn/xsfw/sys/swmzncqapp/*default/index.do",
            "id": uid,
            "code": code_result
        }
        login_response = feapder.Request(url=login_url, data=post_data).get_response().json
        try:
            params = {"ticket": login_response["ticket"]}
        except KeyError:
            if login_response["data"]["code"] == 'NOUSER':
                print("用户名错误")
                send_data(f"{USERNAME}: 用户名错误")
                return
            elif login_response["data"]["code"] == 'PASSERROR':
                print("密码错误")
                send_data(f"{USERNAME}: 密码错误")
                return
            elif login_response["data"]["code"] == 'CODEFALSE':
                print("验证码错误")
                send_data(f"{USERNAME}: 验证码错误")
                raise Exception(fr"验证码错误,尝试重新运行,{request.retry_times}")
            raise Exception(fr"发生未知错误,尝试重新运行,{request.retry_times}")
        jump_url = "https://xsfw.gzist.edu.cn/xsfw/sys/swmzncqapp/*default/index.do"
        yield feapder.Request(
            url=jump_url,
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
        send_data(f"{USERNAME}查寝结果：{result}")

    # 识别验证码
    def code_ocr(self, code_base64_str):
        replace_str = {"o": "0", "O": "0", "l": "1", "i": "1", "I": "1", "s": "5", "S": "5", "b": "6", "B": "8"}
        ocr = ddddocr.DdddOcr(show_ad=False)
        res = ocr.classification(self.base64_to_byte(code_base64_str))
        for key, value in replace_str.items():
            if key in res:
                res = res.replace(key, value)
        print(f"验证码：{res}")
        code_result = eval(res[0:-1])
        return code_result

    # base64字符串转二进制流
    @staticmethod
    def base64_to_byte(s):
        """
        将base64字符串转换为二进制流
        :param s:
        :return byte:
        """
        base64_byte = base64.b64decode(s)
        return base64_byte

    @staticmethod
    def js_from_file(file_name):
        """
        读取js文件
        :return:
        """
        with open(file_name, 'r', encoding='UTF-8') as file:
            result = file.read()
        return result

    def encrypt_password(self, password):
        # 编译加载js字符串
        context1 = execjs.compile(self.js_from_file('./login.js'))
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
    parser.add_argument('-u', '--username', type=str, help='命令行输入用户名')
    parser.add_argument('-p', '--password', type=str, help='命令行输入密码')
    args = parser.parse_args()

    if args.env:
        return get_username_password_from_env()
    elif args.config:
        return get_username_password_from_config(args.config, 'loginInfo')
    elif args.username and args.password:
        return args.username, args.password
    else:
        return get_username_password_manually()


def send_data(string):
    url = os.environ.get("keyUrl")
    data = {
        "msgtype": "text",
        "text": {
            "content": f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))} {string}",
        }
    }
    requests.post(url, json=data)

if __name__ == '__main__':
    # 命令行参数 -e 获取环境变量作为输入，-c 读取配置文件,默认手动输入
    USERNAME, PASSWORD = get_username_password()
    print(f"当前时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}")
    CQ().start()
