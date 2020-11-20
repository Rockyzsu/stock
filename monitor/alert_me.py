# -*-coding=utf-8-*-
# 估价达到自己的设定值,发邮件通知, 每天2.45发邮件
import fire
import sys
sys.path.append('..')
from jsl_monitor import ReachTargetJSL
from realtime_monitor_ts import ReachTarget

# 可转债市场的监控 和 自选池

def main(monitor_type='jsl'):
    # 监控方式
    if monitor_type == 'jsl':
        obj = ReachTargetJSL()
    else:
        obj = ReachTarget()

    obj.monitor()

if __name__ == '__main__':
    fire.Fire(main)