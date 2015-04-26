#!/usr/bin/env python
# -*- coding: utf-8 -*-
# xbzbing on 15/4/13

"""
    批量获取网站标题
    需要BeautifulSoup的支持来解析title（这里不使用正则）
    pip install BeautifulSoup
"""

import sys
import time
import multiprocessing
import requests
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')


def get_targets(file_path):
    try:
        url_file = open(file_path)
        targets = []

        for line in url_file:
            targets.append(line.strip("\n"))

        return targets
    except Exception, e:
        print e
        sys.exit(-1)


def get_title(target):
    global index
    url = target
    if not target.startswith(("http://", "https://")):
        url = "http://" + target
    try:
        headers = {
            'User_Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'
        }
        response = requests.get(url, headers=headers, timeout=30)

        html = BeautifulSoup(response.text)

        # 大小写、html5
        # <meta charset='xx'>
        meta_tag = html.find('meta', {'http-equiv': 'Content-Type'})
        if not meta_tag:
            meta_tag = html.find('meta', {'http-equiv': 'content-type'})

        if meta_tag:
            charset = meta_tag.get('content').lower()
            if 'gbk' in charset:
                response.encoding = 'gbk'
            elif 'gb2312' in charset:
                response.encoding = 'gb2312'
            elif 'utf-8' in charset:
                response.encoding = 'utf-8'
            else:
                response.encoding = 'utf-8'
        else:
            response.encoding = 'utf-8'
        html = BeautifulSoup(response.text)
        title = html.find('title')
        if title:
            title = title.string
        elif response.status_code == 200:
            title = '未获取到标题'
        print '[%s][%s]%s: %s' % (time.strftime('%X'), response.status_code, url, title)
        result = '%s^|^%s^|^%s^|^%s^|^%s' % (1, time.strftime('%X'), response.status_code, url, title)
    except Exception, e:
        print '[%s][错误]%s: %s' % (time.strftime('%X'), url, e.message)
        result = '%s^|^%s^|^%s^|^%s^|^%s' % (0, time.strftime('%X'), '错误', url, e.message)

    return result


def get_titles(targets, threads=5):
    results = []
    threads = int(threads) if int(threads) > 0 else 5
    pool = multiprocessing.Pool(processes=threads)
    for url in targets:
        if not url:
            continue
        results.append(pool.apply_async(get_title, (url,)))
    pool.close()
    pool.join()
    info = {'success': [], 'fail': []}
    for res in results:
        r = str(res.get()).split('^|^')
        if r[0]:
            info['success'].append(r)
        else:
            info['fail'].append(r)

    return info


if __name__ == "__main__":
    if len(sys.argv) == 2 or len(sys.argv) == 3:
        n = sys.argv[2] if len(sys.argv) == 3 else 5
        urls = get_targets(sys.argv[1])
        if len(urls) < 1:
            print "None"
            sys.exit(-2)
        titles = get_titles(urls, n)
        print '=' * 100
        index = 1
        print '抓取完毕!'
        print '成功%d个' % len(titles['success'])
        for tmp in titles['success']:
            print '[%s][%s][%s][%s]%s: %s' % (index, tmp[0], tmp[1], tmp[2], tmp[3], tmp[4])
            index += 1
        index = 1
        print '失败%d个' % len(titles['fail'])
        for tmp in titles['fail']:
            print '[%s][%s][%s][%s]%s: %s' % (index, tmp[0], tmp[1], tmp[2], tmp[3], tmp[4])
            index += 1
    else:
        print ("usage: %s url_file_path [threads]" % sys.argv[0])