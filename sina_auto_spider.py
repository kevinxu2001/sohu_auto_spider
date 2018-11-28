#-*- coding:utf-8 -*-
import os
import sys

import time
from configparser import ConfigParser
from urllib import urlencode
import requests
from requests.exceptions import RequestException
import json
from utils.logger import Logger
import logging

reload(sys)
sys.setdefaultencoding( "utf-8" )

conf = ConfigParser()
conf.read('application.conf', encoding='UTF-8')
version = conf['system']['version']

logger = Logger()
logger.printLogs()


def read_json_file(path):
    file = open(path, 'rb')
    jsonData = json.load(file)
    return jsonData

def get_url_content(url, encode=None):
    if encode == None:
        response = requests.get(url)
    else:
        response = requests.get(url + urlencode(encode))
    try:
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        logging.error("### Get Url Content Error : url=[" + url + "] ###")
        return None



def write_to_file(file_name, file_content):
    fo = open(file_name, "w")
    rs = fo.write(file_content)
    if rs == False:
        logging.error("Write File Error, file_name : " + file_name)
    else:
        logging.info("Write File Success, file_name : " + file_name)
    fo.close()

def makedir_x(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise

def sleep_x():
    sec = 1
    logging.info("### Sleep [" + bytes(sec) + "] Second! ###")
    time.sleep(sec)

'''
' ************************* Functions for geting Model Files ************************
'''
def gen_url_model():
    dict_path=conf['dict_path']
    source_models_file = dict_path['root_path'] + version + '/' + dict_path['source_model_dict_file']
    modelJson = read_json_file(source_models_file)
    ''' sample data:
    [{
        "d": "audi",
        "s": [{
            "d": "yiqiaudi",
            "b": [{
                "d": "4207",
                "n": "A3 Sportback",
                "i": 4207
            }]
        }]
    }]
    '''
    modelList = []
    for model in modelJson:
        brand = model['d']
        for m in model['s']:
            model_cat = m['d']
            model_id = m['b'][0]['d']
            file_name = brand + '_' + model_cat + '_' + model_id
            modelList.append((file_name, 'http://db.auto.sohu.com/api/model/select/trims_%s.json'%(model_id) ))
    return modelList

def parse_model(json_str):
    return json_str
    '''
    if json_str == None:
        return None
    return json.loads(json_str)
    '''

def process_model():
    logging.info("================ Start ModelList Spider Process ================")
    url_list = gen_url_model()
    logging.info("### Urllist: count=[" + bytes(len(url_list)) + "] ###")

    dict_path=conf['dict_path']
    sink_path = dict_path['root_path'] + version + '/'+ dict_path['source_trims_dict_path']

    for url in url_list:
        file_name = sink_path + url[0] + '.json'
        file_content = parse_model(get_url_content(url[1]))
        write_to_file(file_name, file_content)
    logging.info("================ End ModelList Spider Process ================")
    pass


'''
' ************************  Functions for geting Trims Files ************************
'''
def process_trims():

    logging.info("================ Start Trim Spider Process ================")
    dict_path=conf['dict_path']
    source_models_file = dict_path['root_path'] + version + '/' + dict_path['source_trims_dict_path']

    sink_path = dict_path['root_path'] + version + '/'+ dict_path['sink_trims_profile_path']

    file_list = os.listdir(source_models_file)
    logging.info("### source_trims : count=[" + bytes(len(file_list)) + "] ###")
    i = 0
    for i in range(0, len(file_list)):
        file_name = os.path.join(source_models_file, file_list[i])
        if os.path.isfile(file_name):
            logging.info("#### Start source_trim : file=[" + file_name + "] ###")
            url_list = gen_url_trims(file_name)
            logging.info("#### UrlList count=[" + bytes(len(url_list)) + "] ###")
            print url_list
            for url in url_list:
                logging.info("##### Start Get Data : url=[" + url[1] + "] ###")
                # 切分子目录，以trim_id 取余，防止文件数量溢出
                sub_dir = gen_trim_subdir(url[0])
                trims_name = sink_path + bytes(sub_dir)
                makedir_x(trims_name)

                file_name = trims_name + '/' + url[0] + '.json'
                file_content = get_url_content(url[1])
                write_to_file(file_name, file_content)
                i += 1
            # sleep every 1000 times request
            if i >= 1000:
                sleep_x()
                i = 0
        else:
            logging.error("### Not A File : file_name=[" + file_name + "] ###")

    logging.info("================ End Trim Spider Process ================")


    pass

def gen_trim_subdir(file_name):
    # file_name = modelid_year_trimid
    row = file_name.split('_')
    trim_id = int(row[2])
    return trim_id % 20

def gen_url_trims(path):
    json = read_json_file(path)
    ''' sample data:
    {
        "mid": 2190,
        "trimyears": [
            {
                "y": 2016,
                "trims": [
                    {
                        "status": 1,
                        "tid": 131575,
                        "tname": "300C 3.0L 超越版",
                        "price": 39.99
                    }
                ]
            }
        ]
    }
    '''
    trimsUrlList = []
    model_id = json['mid']
    for t in json['trimyears']:
        year = t['y']
        for i in t['trims']:
            trim_id = i['tid']
            price = i['price']
            file_name = bytes(model_id) + '_' + bytes(year) + '_' + bytes(trim_id) # modelid_year_trimid
            trimsUrlList.append((file_name, 'http://db.auto.sohu.com/api/para/data/trim_%s.json'%(trim_id) ))
    return trimsUrlList



if __name__ == '__main__':
    argv = sys.argv[1]
    print argv
    if argv == None:
        print 'usage: sina_auto_spider.py <model|trim>'
        sys.exit(2)
    elif argv == 'model':
        process_model()
    elif argv == 'trim':
        process_trims()
    else:
        print 'usage: sina_auto_spider.py <model|trim>'
        sys.exit(1)