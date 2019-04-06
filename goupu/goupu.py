import requests
import codecs
import matplotlib
import matplotlib.pyplot as plt #绘图
import json
import os
import re
from fake_useragent import UserAgent
import threading
import time
from scrapy.selector import Selector
from queue import Queue
ua = UserAgent()
gLock = threading.Lock()


class Produter(threading.Thread):
    def __init__(self,produter,consuter,draw,*args,**kwargs):
        super(Produter,self).__init__(*args,**kwargs)
        self.headers = {'User-Agent': ua.random}
        self.produter = produter
        self.consumer = consuter
        self.draw = draw

    def run(self):
        while True:
            if self.produter.empty():
                print('%s已经退出' % threading.current_thread())
                break
            url = self.produter.get()
            self.parse_index(url)

    def parse_index(self,url):
        try:
            response = requests.get(url =url,headers = self.headers )
            selector = Selector(text = response.text)
            index_url = selector.css('li .d1 a::attr(href)').extract()
            for i in range(len(index_url)):
                url = index_url[i]
                result = self.detail_index(url)
                self.consumer.put((result))
                self.draw.put(result['中文名字  ：'][0],result[ '身      高：'])
        except :
            print('请求超时！')


    def detail_index(self,index_url):
        response = requests.get(url = index_url,headers =self.headers)
        selector = Selector(text = response.text)
        img_url = selector.css('.type_production img::attr(src)').extract()[1]
        zh_name = selector.css('.pro_tit .a1::text').extract()
        us_name = selector.css('.pro_tit .a2::text').extract()
        jianjie = selector.css('.produc_table .a2::text').extract()
        cankaojiage = selector.css('.produc_table .a3::text').extract_first('')
        hengliangbiaozhui = selector.css('.pingfen .sp2 em::attr(style)').extract()
        text = selector.css('.prod_slidebox ul li .text p::text').extract()
        for x in range(len(hengliangbiaozhui)):
            nianren = hengliangbiaozhui[0].replace('width:','')
            xijiao = hengliangbiaozhui[1].replace('width:','')
            diaomao = hengliangbiaozhui[2].replace('width:','')
            tiwei = hengliangbiaozhui[3].replace('width:','')
            meirong = hengliangbiaozhui[4].replace('width:','')
            youxian = hengliangbiaozhui[5].replace('width:','')
            shengren = hengliangbiaozhui[6].replace('width:','')
            dongwu = hengliangbiaozhui[7].replace('width:','')
            yundongliang = hengliangbiaozhui[8].replace('width:','')
            kexunxing = hengliangbiaozhui[9].replace('width:','')
            koushui = hengliangbiaozhui[10].replace('width:','')
            naihan = hengliangbiaozhui[11].replace('width:','')
            naire = hengliangbiaozhui[12].replace('width:','')
            shiying = hengliangbiaozhui[13].replace('width:','')




        for i in range(len(jianjie)):
            bieming = jianjie[0].replace('\xa0','')
            fenbuquyu = jianjie[1].replace('\xa0','')
            yuanchandi = jianjie[2].replace('\xa0','')
            tixing = jianjie[3].replace('\xa0','')
            gongneng = jianjie[4].replace('\xa0','')
            fenzu = jianjie[5].replace('\xa0','')
            shengao = jianjie[6].replace('\xa0','')
            tizhong = jianjie[7].replace('\xa0','')
            souming = jianjie[8].replace('\xa0','')
            tidian = jianjie[10].replace('\xa0','')
        return {
                '封      面：':img_url,
                '中文名字  ：':zh_name,
                '英文名字  ：':us_name,
                '别      名：':bieming,
                '分布区域  ：':fenbuquyu,
                '原  产  地：':yuanchandi,
                '体      型：':tixing,
                '功      能：':gongneng,
                '分      组：':fenzu,
                '身      高：':shengao,
                '体      重：':tizhong,
                '寿      命：':souming,
                '参考价格  ：':cankaojiage,
                '特      点：':tidian,
                '粘人程度  ：':nianren ,
                '喜叫程度：': xijiao,
                '掉毛程度：':diaomao ,
                '体味程度：': tiwei,
                '美容程度：': meirong,
                '对小孩友善程度：': youxian,
                '对生人程度：': shengren,
                '对动物程度：':dongwu ,
                '运动量：':yundongliang ,
                '可训练性：': kexunxing,
                '口水程度：：': koushui,
                '耐寒程度：': naihan,
                '耐热程度：':naire ,
                '城市适应度：':shiying,
                '简介：     ':str(text)
            
            }



class Consumer(threading.Thread):
    def __init__(self,produter,consuter,*args,**kwargs):
        super(Consumer,self).__init__(*args,**kwargs)
        self.f = codecs.open(os.path.join(os.getcwd(),'dog.json'),'a',encoding = 'utf-8')
        self.produter = produter
        self.consumer = consuter        

    def run(self):
        while True:
            if self.consumer.empty():
                print('%s抓取完成,写入完成\n' % threading.current_thread()) 
                self.f.close()
                break
            a = self.consumer.get()
            lines = json.dumps(dict(a),ensure_ascii = False)
            #必须加锁，避免写入出现各种问题
            gLock.acquire()
            self.f.write(lines +'\n\n')
            print('%s正在抓取数据\n' % threading.current_thread())
            gLock.release()

            



def main():
    produter = Queue(100)
    consuter = Queue(1000)
    draw = Queue(1000)
    for i in range(1,2):
        url = 'http://www.goupu.com.cn/dog/search-htm-page-%d-catid-4-sort-.html' % i
        produter.put(url)
    for i in range(3):
        t = Produter(produter,consuter,draw,name = '生产者%d号' % i)
        t.start()
    #保存文件
    time.sleep(15)
    for i in range(4):
        t = Consumer(produter,consuter,name = '消费者%d号' % i)
        t.start()

if __name__ == '__main__':
    main()

