import fire
class ProfitTool:

    def __init__(self,codes) -> None:
        if isinstance(codes ,str):
            self.codes = [codes]
        elif isinstance(codes,list):
            self.codes = list(codes)

        else:
            raise TypeError('输入类型有误')



def main(codes):
    codes=codes.split(',')
    print(codes)

if __name__=='__main__':
    fire.Fire(main)


            