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
import urllib2
from BeautifulSoup import BeautifulSoup


def get_targets(file_path):
    url_file = open(file_path)
    targets = []

    for line in url_file:
        targets.append(line.strip("\n"))

    return targets


def get_title(target):
    url = target
    if not target.startswith(("http://", "https://")):
        url = "http://" + target
    try:
        request = urllib2.Request(url)
        request.add_header("User_Agent", "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; GTB7.4; InfoPath.2; SV1; .NET CLR 3.3.69573; WOW64; en-US)")
        html = urllib2.urlopen(request, timeout=30).read()
        soup = BeautifulSoup(html)
        title = str(soup.find("title")).strip("<title>").strip("</title>").strip("\n")
        print "[%s]%s: %s" % (get_time_now("%H:%M:%S"), url, title)
        return title
    except urllib2.HTTPError, e:
        print "请求错误：%s" % e


def get_titles(targets, threads=5):
    threads = int(threads) if int(threads) > 0 else 5
    pool = multiprocessing.Pool(processes=threads)
    results = []
    for url in targets:
        results.append(pool.apply_async(get_title, (url,)))
    pool.close()
    pool.join()

    return results


def get_time_now(time_format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(time_format, time.localtime(time.time()))

if __name__ == "__main__":
    if len(sys.argv) == 3:
        urls = get_targets(sys.argv[1])
        if len(urls) < 1:
            print "None"
        else:
            titles = get_titles(urls)
            for title in titles:
                print title
    else:
        print ("usage: %s url_file_path threads" % sys.argv[0])