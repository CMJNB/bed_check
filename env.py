# 获取所有系统环境变量
import configparser
import os

from feapder import setting


def set_setting_from_env():
    """
    从系统环境变量中获取配置
    :return:
    """
    setting_env_list = vars(setting).keys()
    system_env_list = os.environ
    for key, value in system_env_list.items():
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
