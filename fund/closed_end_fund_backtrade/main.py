# 作者公众号：可转债量化分析

import fire
from backtrade_fund_weekly_share_increment import Runner


def main(func):
    app = Runner(func)
    app.run()


if __name__ == '__main__':
    fire.Fire(main)
