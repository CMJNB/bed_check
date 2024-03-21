# 获取所有系统环境变量
import configparser
import os
import feapder.utils.tools as tools

from feapder import setting


def set_setting_from_env():
    """
    从系统环境变量中获取配置
    :return:
    """
    system_env_list = os.environ
    setting_string = system_env_list.get("SETTING_STRING")
    if setting_string:
        set_setting_from_envString(setting_string)
    else:
        setting_env_list = vars(setting).keys()
        for key, value in system_env_list.items():
            if key in setting_env_list:
                setattr(setting, key, value)


def set_setting_from_envString(config_json):
    """
    从系统环境变量中获取SETTING_STRING配置，JSON格式字符串
    :return:
    """
    setting_env_list = vars(setting).keys()
    if config_json:
        data = tools.get_json(config_json)
        for key, value in data.items():
            if key in setting_env_list:
                setattr(setting, key, value)


def set_setting_from_config(config_file, section):
    """
    从配置文件获取环境变量
    :return:
    """
    setting_env_list = vars(setting).keys()
    if config_file and section:
        config = configparser.ConfigParser()
        config.read(config_file)
        if config.has_section(section):
            for key, value in config.items(section):
                if key in setting_env_list:
                    setattr(setting, key, value)
