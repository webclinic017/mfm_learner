import warnings

import tushare

import conf
import yaml
import logging
import os

logger = logging.getLogger(__name__)


def load_config():
    if not os.path.exists(conf.CONF_PATH):
        raise ValueError("指定的环境配置文件不存在:" + conf.CONF_PATH)
    f = open(conf.CONF_PATH, 'r', encoding='utf-8')
    result = f.read()
    # 转换成字典读出来
    data = yaml.load(result, Loader=yaml.FullLoader)
    logger.info("读取配置文件:%r", conf.CONF_PATH)
    return data


def tushare_login():
    conf = load_config()
    tushare.set_token(conf['tushare']['token'])
    return tushare.pro_api()


def init_logger():
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger('matplotlib.font_manager').disabled = True
    logging.getLogger('matplotlib').disabled = True
    warnings.filterwarnings("ignore")
    warnings.filterwarnings("ignore", module="matplotlib")
    logging.basicConfig(format='%(asctime)s:%(filename)s:%(lineno)d:%(levelname)s : %(message)s',
                        level=logging.DEBUG,
                        handlers=[logging.StreamHandler()])
