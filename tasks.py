#!/usr/bin/env python
# encoding: utf-8
# tasks.py
# email: ringzero@0x557.org

"""
    Thorns Project 分布式任务控制脚本
    tasks
        -- nmap_dispath			# nmap 扫描调度函数
"""

import subprocess
from celery import Celery, platforms
import os

# 初始化芹菜对象
app = Celery()

# 允许celery以root权限启动
platforms.C_FORCE_ROOT = True

# 修改celery的全局配置
app.conf.update(
    CELERY_IMPORTS=("tasks", ),
    # BROKER_URL='redis://127.0.0.1:6379/0',
    # CELERY_RESULT_BACKEND = 'db+scheme://user:password@host:port/dbname'
    # CELERY_RESULT_BACKEND='db+mysql://celery:celery1@127.0.0.1:3306/wscan',
    BROKER_URL="amqp://guest:guest@172.16.146.145:5672//",
    CELERY_RESULT_BACKEND="redis://172.16.146.145:6379/0",
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TIMEZONE='Asia/Shanghai',
    CELERY_ENABLE_UTC=True,
    CELERY_REDIS_MAX_CONNECTIONS=5000,  # Redis 最大连接数
    BROKER_TRANSPORT_OPTIONS={'visibility_timeout': 3600},  # 如果任务没有在 可见性超时 内确认接收，任务会被重新委派给另一个Worker并执行  默认1 hour.
    # BROKER_TRANSPORT_OPTIONS = {'fanout_prefix': True},		# 设置一个传输选项来给消息加上前缀
)

# 失败任务重启休眠时间300秒，最大重试次数5次
# @app.task(bind=True, default_retry_delay=300, max_retries=5)


@app.task
def nmap_dispath(targets, task_id=None):
    run_script_path = get_current_path()
    # nmap环境参数配置
    if task_id:
        cmdline = 'python wyportmap.py %s %s' % (targets, task_id)
    else:
        cmdline = 'python wyportmap.py %s' % targets

    nmap_proc = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 cwd=run_script_path)
    process_output = nmap_proc.stdout.readlines()
    return process_output


def get_current_path():
    return os.path.dirname(os.path.abspath(__file__))




