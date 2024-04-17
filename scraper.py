#Mercari scraper
import pandas as pd
from selenium import webdriver
import time
import os
import re
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from sqlalchemy import true
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

SKU="your item to search"
url = "https://www.mercari.com/jp/search/?keyword=" + SKU

browser = webdriver.Chrome()
time.sleep(5)

# 表示ページ
page = 1
# リストを作成
columns = ["Name", "Price", "Sold", "Url"]
# 配列名を指定する
list=[]

# ブラウザで検索
browser.get(url)
time.sleep(5)
def scroll_to_bottom():
    actions = ActionChains(browser)
    actions.send_keys(Keys.END).perform()
for _ in range(5):  # Adjust the number of scrolls as needed
    scroll_to_bottom()
    time.sleep(2) 

# 商品ごとのHTMLを全取得
soup = bs(browser.page_source, "html.parser")
posts = soup.find_all("li",{"class":"sc-bcd1c877-2 cvAXgx"})

# 商品ごとに名前と値段、購入済みかどうか、URLを取得
for post in posts:    
    # Assuming 'element' is the WebElement representing the div
    div_element = post.find("div", class_="merItemThumbnail fluid__a6f874a2")
    if div_element:
        aria_label = div_element['aria-label']
        # Use regex to find the price pattern
        # Extract title and price
        match = re.search(r'(\d{1,3}(,\d{3})*(\.\d+)?yen)', aria_label)
        if match:
            price = match.group(0)
            title = aria_label.replace(price, '').strip()
        print(price)
        print(title)
        # 購入済みであれば1、未購入であれば0になるように設定
        sold = 1 if 'Sold' in title else 0
        print(sold)
        # 商品のURLを取得
        url = "https://jp.mercari.com" + post.find('a', class_='sc-bcd1c877-1 lpjZwE').get('href')
        print(url)
        data = {
        'Name': title,
        'Price': price,
        'Sold': sold,
        'Url': url
        }
        list.append(data)
    else: continue
    
df=pd.DataFrame(list)
df