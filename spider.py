import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from config import *

# 浏览器对象
browser = webdriver.PhantomJS(
    service_args=SERVICE_ARGS,
    executable_path=r'D:\Program Files\PhantomJs\phantomjs-2.1.1-windows\bin\phantomjs.exe')  # 注意:这里路径前面要加r，否则报错
# 设置浏览器窗口大小， 过小可能会影响结果
browser.set_window_size(1400, 900)
# wait方法，以下会多次用到，为了方便使用，封装成变量
wait = WebDriverWait(browser, 10)

# 访问淘宝首页并在搜索框中搜索'美食'关键字


def search():
    print('正在搜索...')
    try:
        brow  ser.get('https://www.taobao.com')
        # 搜索框
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#q'))
        )
        # 搜索按钮
        submit = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        # 搜索框输入
        input.send_keys(KEYWORD)
        # 点击搜索
        submit.click()
        # 得到总页数
        total = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        get_products()
        return total.text
    except TimeoutException:
        return search()

# 翻页


def next_page(page_num):
    print('正在翻页', page_num)
    try:
        # 到第几页的输入框
        input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        # 确定按钮
        submit = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        # 清空页数输入框
        input.clear()
        input.send_keys(page_num)
        submit.click()
        # 高亮的页数与输入框输入的页数相等则说明翻页成功
        wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR,
                 '#mainsrp-pager > div > div > div > ul > li.item.active > span'),
                str(page_num)))
        get_products()
    except TimeoutException:
        next_page(page_num)

# 解析产品


def get_products():
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
    # 获取网页源代码
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        print(product)


def main():
    try:
        total = search()
        # 总页数
        total = int(re.compile('(\d+)').search(total).group(1))
        for i in range(2, total + 1):
            next_page(i)
    except Exception:
        print('出错了')
    finally:
        browser.close()


if __name__ == '__main__':
    main()
