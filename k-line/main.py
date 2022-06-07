from basic_usage import get_k_data,axis_date,ma_line,add_vol,kline_demo,run
from recognize_form import two_crow
def main():
    get_k_data(code="sz002241",name='歌尔股份2020.xlsx')
    kline_demo()
    axis_date()
    ma_line()
    add_vol()
    two_crow()
    run()

if __name__ == '__main__':
    main()