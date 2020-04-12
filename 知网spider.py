from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time
from pyquery import PyQuery as pq
import os
import csv

user_input = str(input('请输入要检索的关键词:\n'))
MAX_PAGE = 17
browser = webdriver.PhantomJS()
wait = WebDriverWait(browser, 6)
url = 'https://kns.cnki.net/kns/brief/default_result.aspx'
browser.get(url)
input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.research input')))
input.send_keys(user_input)
input.send_keys(Keys.ENTER)
browser.switch_to.frame('iframeResult')
def get_index_page(page):
    print('正在爬取%d页'%(page))
    if page>1:
        try:
            next = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'div.TitleLeftCell a:last-child')))
            next.click()
        except TimeoutException:
            get_index_page(page)
    wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'div.TitleLeftCell font.Mark'), str(page)))
    parse_page(page)
def parse_page(page):
    html = browser.page_source
    doc = pq(html)
    # 一个生成器
    tr_list = doc('table.GridTableContent tbody tr').items()
    for tr in tr_list:
        # 文章标题
        title = tr.find('a.fz14').text().replace('\n', '')
        if title =='':
            continue
        # 作者
        author = tr.find('td.author_flag').text()
        # 来源------选择target='_blank'和href属性中包含ridge子串所有节点。
        source = tr.find('a[target=_blank][href*="ridge"]').text()
        # 发表时间-----选择align='center'的所有节点。
        data = tr.find('td[align=center]').text().split(' ')[0]
        # 被引量
        KnowledgeNetcont = tr.find('span.KnowledgeNetcont a').text()
        if KnowledgeNetcont=='':
            KnowledgeNetcont = KnowledgeNetcont.replace('','0')
        # 下载量
        downloadCount = tr.find('span.downloadCount a').text()
        if downloadCount=='':
            downloadCount = downloadCount.replace('','0')

        item = {
            'title':title,
            'author':author,
            'source':source,
            'data':data,
            'KnowledgeNetcont':KnowledgeNetcont,
            'downloadCount':downloadCount,
        }
        save(item)
    print('保存第%d页成功'%(page))

def save(item):
    '''
    进行判断，如果文件第一次写入就加上字段头，如果不是就不加，防止文件重复写头。
    :param item: 解析的内容
    :return: 保存的CSV文件
    '''
    if os.path.exists('%s.csv' %(user_input)):
        with open('%s.csv' %(user_input), 'a', encoding='utf-8') as csvfile:
            fieldname = ['title', 'author', 'source', 'data', 'KnowledgeNetcont', 'downloadCount']
            writer = csv.DictWriter(csvfile, fieldname)
            writer.writerow(item)
    else:
        with open('%s.csv' %(user_input),'a',encoding='utf-8') as csvfile:
            fieldname = ['title', 'author', 'source', 'data', 'KnowledgeNetcont', 'downloadCount']
            writer = csv.DictWriter(csvfile,fieldname) #DictWriter方法使csv文件可以写入字典
            writer.writeheader()
            writer.writerow(item)

def man(MAX_PAGE):
    for page in range(1,MAX_PAGE):
        get_index_page(page)

if __name__=='__main__':
    man(MAX_PAGE)


'''
本爬虫脚本在翻页时用的点击下一页的方法，因为该网站没有输入页码的输入框，
无法直接输入页码获取内容，只能将检索内容的代码放入函数外，用全局变量，
否则代码运行时，网站地址会被重复请求，一直获取的是第一第二页的内容，其他获取不到。
希望理解！！
'''