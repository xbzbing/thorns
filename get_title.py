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
    url = target
    if not target.startswith(("http://", "https://")):
        url = "http://" + target
    try:
        request = urllib2.Request(url)
        request.add_header("User_Agent", "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; chromeframe/12.0.742.112)")
        response = urllib2.urlopen(request, timeout=10)
        if response.getcode() == 200:
            html = response.read()
            soup = BeautifulSoup(html)
            title = str(soup.find("title")).strip("<title>").strip("</title>").strip("\r\n").strip("\n")
            print "[%s][%s]%s: %s" % (get_time_now("%H:%M:%S"), response.getcode(), url, title)
            return title
        else:
            print "[%s][%s]%s: 请求错误" % (get_time_now("%H:%M:%S"), response.getcode(), url)
            return "Error %s" % response.getcode()
    except Exception, e:
        print "[%s]%s: %s" % (get_time_now("%H:%M:%S"), url, e.message)
        return "Error:%s" % e.message


def get_titles(targets, threads=5):
    results = []
    threads = int(threads) if int(threads) > 0 else 5
    pool = multiprocessing.Pool(processes=threads)
    for url in targets:
        results.append(pool.apply_async(get_title, (url,)))
    pool.close()
    pool.join()

    return results


def get_time_now(time_format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(time_format, time.localtime(time.time()))

if __name__ == "__main__":
    if len(sys.argv) == 2 or len(sys.argv) == 3:
        n = sys.argv[2] if len(sys.argv) == 3 else 5
        urls = get_targets(sys.argv[1])
        if len(urls) < 1:
            print "None"
            sys.exit(-2)
        get_titles(urls, n)
    else:
        print ("usage: %s url_file_path [threads]" % sys.argv[0])