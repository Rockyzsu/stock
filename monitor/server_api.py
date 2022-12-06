from monitor.jsl_monitor import ReachTargetJSL


class ServerAPI(ReachTargetJSL):

    def __init__(self):
        super(ServerAPI, self).__init__()

    def update(self):
        ret = self.fetch_data()
        new_result = []
        for item in ret:
            tmp_dict = {
                "code": item[''],
                "name": item[''],
                "price": item[''],
                "percent": item[''],
                "premium_rt": item[''],
                "redeem_icon": item[''],
                "curr_iss_amt": item[''],
                "zg_price": item[''],
                "zg_code": item[''],
                "zg_percent": item[''],
                "zg_vol": item[''],
                "convert_price": item[''],
                "dead_line": item[''],
                "volume": item[''],
                "rating": item[''],
                "down_covert_p_time": item[''],
                "convert_start_date": item[''],
                "double_low": item[''],
                "convert_value": item[''],
                "change_down_condition": item[''],
                "turn_over_rate": item[''],
                "ytm": item['']}
            new_result.append(tmp_dict)

        self.send_redis(new_result, "ptrade")


if __name__ == '__main__':
    app = ServerAPI()
    app.update()
