#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'iambocai'

from datetime import datetime
import json
import time
import socket
import os
import re
import sys
import commands
import urllib2, base64

platform_queue = {'库存更新队列': 'updatestock:jrc2ckgu',
                  '库存本地数据库更新队列': 'currentstock:jrc2ckgu',
                  '库存平台更新队列': 'ptmstock:jrc2ckgu:goumangapp'
                  }
platform_sku_re = [('平台库存更新队列Q3', '*:es.ptm.stock:*'), ('平台库存错误队列Q3', '*:es.ptm.stock.error:*'),
                   ('平台库存无效队列Q3', '*:es.ptm.stock.invalid:*')]


class RedisStats:
    # 如果你是自己编译部署到redis，请将下面的值替换为你到redis-cli路径
    _redis_cli = '/usr/bin/redis-cli'
    _stat_regex = re.compile(ur'(\w+):([0-9]+\.?[0-9]*)\r')

    def __init__(self, port='16379', passwd=None, host='10.46.209.54'):
        self._cmd = '%s -h %s -p %s info' % (self._redis_cli, host, port)
        self._ping_cmd = '%s -h %s -p %s ping' % (self._redis_cli, host, port)
        self._latency_latest_cmd = '%s -h %s -p %s latency latest' % (self._redis_cli, host, port)
        self._hlen_queue_cmd = '%s -h %s -p %s hlen ' % (self._redis_cli, host, port)
        self._zlen_queue_cmd = '%s -h %s -p %s zcount ' % (self._redis_cli, host, port)
        self._strlen_queue_cmd = '%s -h %s -p %s strlen ' % (self._redis_cli, host, port)
        self._keys_re_cmd = '%s -h %s -p %s keys \* ' % (self._redis_cli, host, port)
        if passwd not in ['', None]:
            self._cmd = "%s -a %s" % (self._cmd, passwd)
            self._ping_cmd = "%s -a %s" % (self._ping_cmd, passwd)
            self._latency_latest_cmd = '%s -a %s' % (self._latency_latest_cmd, passwd)
            self._hlen_queue_cmd = '%s -a %s' % (self._hlen_queue_cmd, passwd)
            self._keys_re_cmd = '%s -a %s' % (self._keys_re_cmd, passwd)

    def stats(self):
        ' Return a dict containing redis stats '
        info = commands.getoutput(self._cmd)
        return dict(self._stat_regex.findall(info))

    def ping(self):
        'Check whether redis server is alive'
        return commands.getoutput(self._ping_cmd)

    # 延迟监控
    def latency_latest(self):
        'latency monitor'
        return commands.getoutput(self._latency_latest_cmd)

    # 获取hash队列的长度
    def get_hqueue(self, hkey):
        get_hqueue_cmd = self._hlen_queue_cmd + re_queue
        return commands.getoutput(get_hqueue_cmd)

    # 获取zset队列的长度
    def get_zqueue(self, zkey):
        get_zqueue_cmd = self._zlen_queue_cmd + zkey + ' -9999999999 9999999999'
        return commands.getoutput(get_zqueue_cmd)

    # 获取string队列的长度
    def get_strqueue(self, strkey):
        get_strqueue_cmd = self._strlen_queue_cmd + strkey
        return commands.getoutput(get_strqueue_cmd)

    # 获取商户和门店
    def get_keys(self, re_keys):
        get_keys_cmd = self._keys_re_cmd + '|grep ' + re_keys
        hkeys = commands.getoutput(get_keys_cmd).split('\n')
        # for key in keys:
        #    tenant,platform = key.split()
        #    dict_key = [{tenant:platform}]
        #    dict_keys.append(dict_key)
        return hkeys


def main():
    ip = "dly-node-ecs3"
    timestamp = int(time.time())
    step = 60
    # inst_list中保存了redis配置文件列表，程序将从这些配置中读取port和password，建议使用动态发现的方法获得，如：
    # inst_list = [ i for i in commands.getoutput("find  /etc/ -name 'redis*.conf'" ).split('\n') ]
    insts_list = ['/hdapp/8002/redis/conf/redis.conf']
    p = []

    monit_keys = [
        ('connected_clients', 'GAUGE'),
        ('blocked_clients', 'GAUGE'),
        ('used_memory', 'GAUGE'),
        ('used_memory_rss', 'GAUGE'),
        ('mem_fragmentation_ratio', 'GAUGE'),
        ('total_commands_processed', 'COUNTER'),
        ('rejected_connections', 'COUNTER'),
        ('expired_keys', 'COUNTER'),
        ('evicted_keys', 'COUNTER'),
        ('keyspace_hits', 'COUNTER'),
        ('keyspace_misses', 'COUNTER'),
        ('keyspace_hit_ratio', 'GAUGE'),
    ]

    for inst in insts_list:
        port = '16379'
        passwd = commands.getoutput("sed -n 's/^requirepass *\([^ ]*\)/\\1/p' %s" % inst)
        metric = "redis"
        endpoint = ip
        tags = 'port=%s' % port

        try:
            conn = RedisStats(port, passwd)
            stats = conn.stats()
        except Exception, e:
            continue

        for key, vtype in monit_keys:
            if key == 'keyspace_hit_ratio':
                try:
                    value = float(stats['keyspace_hits']) / (
                    int(stats['keyspace_hits']) + int(stats['keyspace_misses']))
                except ZeroDivisionError:
                    value = 0
            elif key == 'mem_fragmentation_ratio':
                value = float(stats[key])
            else:
                try:
                    value = int(stats[key])
                except:
                    continue

            i = {
                'Metric': '%s.%s' % (metric, key),
                'Endpoint': endpoint,
                'Timestamp': timestamp,
                'Step': step,
                'Value': value,
                'CounterType': vtype,
                'TAGS': tags
            }
            p.append(i)

        ping = conn.ping()
        key = 'alive'
        if ping == 'PONG':
            value = 1
        else:
            value = 0
        i = {
            'Metric': '%s.%s' % (metric, key),
            'Endpoint': endpoint,
            'Timestamp': timestamp,
            'Step': step,
            'Value': value,
            'CounterType': vtype,
            'TAGS': tags
        }
        p.append(i)

        # 延迟监控
        latency = conn.latency_latest()
        latncy_lt = latency.split('\n')
        latncy_len = len(latncy_lt) / 4 + 1
        latncy_lt_new = []
        for n in range(1, latncy_len):
            pre_forth_key = latncy_lt[4 * (n - 1):4 * n]
            latncy_lt_new.append(tuple(pre_forth_key))
        for key in latncy_lt_new:
            event, ts, latest, maximum = key
            i = {
                'Metric': '%s.latency' % metric,
                'Endpoint': endpoint,
                'Timestamp': timestamp,
                'Step': step,
                'Value': latest,
                'CounterType': vtype,
                'TAGS': 'event=%s,type=latest' % event
            }
            p.append(i)
            i = {
                'Metric': '%s.latency' % metric,
                'Endpoint': endpoint,
                'Timestamp': timestamp,
                'Step': step,
                'Value': maximum,
                'CounterType': vtype,
                'TAGS': 'event=%s,type=maximum' % event
            }
            p.append(i)

        # 获取指定hash值的队列长度
        for name in platform_queue.keys():
            patt = platform_queue[name]
            keys = conn.get_keys(patt)
            len_sum = 0
            for key in keys:
                l_key = key.split(':')
                if l_key[-1] == 'data':
                    len_key = conn.get_hqueue(key)
                    type = l_key[-1]
                elif l_key[-1] == 'zkeys':
                    len_key = conn.get_zqueue(key)
                    type = l_key[-1]
                elif l_key[-1] == 'score':
                    len_key = conn.get_strqueue(key)
                    type = l_key[-1]
                len_sum += len_key
                value = len_key
                tenant = l_key[2]
                stock = l_key[1]
                tags = 'tenant=%s,stock=%s,type=%s' % (tenant,stock,type)
                i = {
                    'Metric': '%s.queue' % metric,
                    'Endpoint': endpoint,
                    'Timestamp': timestamp,
                    'Step': step,
                    'Value': value,
                    'CounterType': vtype,
                    'TAGS': tags
                }
                p.append(i)
            value = len_sum
            tags = 'tenant=%s,stock=%s,type=%s' % (tenant,stock,'sum')
            i = {
                'Metric': '%s.queue' % metric,
                'Endpoint': endpoint,
                'Timestamp': timestamp,
                'Step': step,
                'Value': value,
                'CounterType': vtype,
                'TAGS': tags
            }
            p.append(i)

    # print json.dumps(p,ensure_ascii=False, sort_keys=True,indent=4)
    method = "POST"
    handler = urllib2.HTTPHandler()
    opener = urllib2.build_opener(handler)
    url = 'http://10.46.209.54:1988/v1/push'
    request = urllib2.Request(url, data=json.dumps(p, ensure_ascii=False, indent=4))
    request.add_header("Content-Type", 'application/json')
    request.get_method = lambda: method
    try:
        connection = opener.open(request, timeout=10)
    except urllib2.HTTPError, e:
        connection = e

    # check. Substitute with appropriate HTTP code.
    if connection.code == 200:
        print connection.read()
    else:
        print '{"err":1,"msg":"%s"}' % connection


if __name__ == '__main__':
    print(datetime.now())
    proc = commands.getoutput(' ps -ef|grep %s|grep -v grep|wc -l ' % os.path.basename(sys.argv[0]))
    if int(proc) < 5:
        main()