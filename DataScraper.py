from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import datetime as dt
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains 


GPU_ID = {'GTX1070':'B01H0WU884', 'GTX1650':'B0881YZJ45','RTX2080':'B07W3P4PC2', 'RTX3060':'B08WTFG5BX', 'RTX3060ti':'B097YW4FW9', 'RTX3070':'B097MYTZMW'}


# 日期处理函数
def date_process(date_hist):
    chin2eng = {'一月':'1', '二月':'2', '三月':'3', '四月':'4', '五月':'5', '六月':'6', \
                '七月':'7', '八月':'8', '九月':'9', '十月':'10', '十一月':'11', '十二月':'12'}
    date_num = []
    date_processed = []
    year = dt.datetime.now().year
    
    # 文字转数字
    for date in date_hist:
        date_num.append(chin2eng[date.split(' ')[1]] + '-' + date.split(' ')[2]) 

    # 增加年份
    date_num.reverse()
    for i in range(0, len(date_num)):
        date_processed.append(str(year) + '-' + date_num[i])
        if date_num[i][0:2] == '1-' and date_num[i+1][0:3] == '12-':
            year -= 1
    date_processed.reverse()

    return date_processed


# 售价处理函数
def price_process(price_hist):
    price_processed = []

    for price in price_hist:
        if '' == price:
            price_processed.append(float('nan'))
        else:
            price_processed.append(price.split(' ')[1].replace(',', ''))

    return price_processed


# 爬取单个显卡历史价格并保存成csv
def get_price(GPU_item):
    # 打开窗口并设置大小
    my_url = 'https://keepa.com/#!product/1-' + GPU_item[1]
    option = Options()
    option.headless = False
    option.add_argument("--incognito")
    driver = webdriver.Chrome(options=option)

    driver.get(my_url)
    driver.set_window_position(0, 0)
    driver.set_window_size(1024, 768)

    # 等待到加载出走势图
    element = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, "//canvas[@class='flot-overlay']")))

    action = ActionChains(driver) 

    # “全部”按钮
    button_all = driver.find_element(By.XPATH, "//*[@class='legendTable']/tbody/tr/td/table/tbody/tr[last()]/td[2]")
    action.move_to_element(button_all).click(button_all).perform()

    # 指针移到图标最左端
    action.move_to_element_with_offset(element, 50, 200).perform()
    action.move_to_element_with_offset(element, 44, 200).perform()

    # 从左到右读取价格
    price_new_hist = []
    price_2nd_hist = []
    date_hist = []

    for step, x_now in enumerate(range(44, 590)):
        # 向右移动指针一步
        action.move_to_element_with_offset(element, x_now, 200).perform()
        
        # 获得售价及日期
        value_new = driver.find_element(By.XPATH, "//*[@id='flotTip1']").text
        value_2nd = driver.find_element(By.XPATH, "//*[@id='flotTip2']").text
        date = driver.find_element(By.XPATH, "//*[@id='flotTipDate']").text

        # 日期为空的数据跳过
        if '' == date:
            continue

        price_new_hist.append(value_new)
        price_2nd_hist.append(value_2nd)
        date_hist.append(date) 

    # 退出浏览器
    driver.quit()

    # 将爬取的数据保存为csv文件
    date_processed = date_process(date_hist)
    price_new_processed = price_process(price_new_hist)
    price_2nd_processed = price_process(price_2nd_hist)
    df = pd.DataFrame({'date':date_processed, 'price_new':price_new_processed, 'price_2nd':price_2nd_processed,})
    df.to_csv('./data/' + GPU_item[0] + '.csv', index=None)


if __name__ == "__main__":
    for step, GPU_item in enumerate(GPU_ID.items()):
        print('正在爬取[{}]数据，进度{}/{}'.format(GPU_item[0], step+1, len(GPU_ID)))
        get_price(GPU_item)
        