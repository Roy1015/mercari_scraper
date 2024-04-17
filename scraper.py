#Mercari scraper using selenium and beautifulsoup to search product on Mercari and get the title, price, sold out or not, and the URL.
#メルカリで商品検索をかけて、商品名・価格・売り切れか否か・URLを取得し一覧化する。※検索結果の１ページ目のみ取得。
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

#Define SKU and URL　検索ワードとURLの設定
SKU="your item to search"
url = "https://www.mercari.com/jp/search/?keyword=" + SKU

#run browser ブラウザを起動
browser = webdriver.Chrome()
time.sleep(5)

#make a data list リストを作成
columns = ["Name", "Price", "Sold", "Url"]
list=[]

#run browser and scroll till the bottom ブラウザで検索、ページ最下部までスクロールさせる
browser.get(url)
time.sleep(5)
def scroll_to_bottom():
    actions = ActionChains(browser)
    actions.send_keys(Keys.END).perform()
for _ in range(5):  # Adjust the number of scrolls as needed
    scroll_to_bottom()
    time.sleep(2) 

#obtain the html elements per product 商品ごとのHTMLを全取得。当該のクラス名は将来変わる可能性もあるため、都度確認する。
#as of 17 Apr 2024, the element is under class named "sc-bcd1c877-2 cvAXgx". You minght need to adjust the class name in case Mercari changes the web structure.
soup = bs(browser.page_source, "html.parser")
posts = soup.find_all("li",{"class":"sc-bcd1c877-2 cvAXgx"})

#get the information div tag and extract title, price, selling status, and href out of it. 
#商品のタイトル、値段、売り切れか、URLを当該のdivタグから抽出する
for post in posts:    
    #find the class to get title, price, and selling status.タイトル、値段、売り切れかの情報を含むタグを見つける。
    div_element = post.find("div", class_="merItemThumbnail fluid__a6f874a2")
    
    #if browser can find it, extract items. if not, skip the post and move onto the next one.
    #もし見つからなければ、抽出せずに次のpostへ移動する。
    if div_element:
        aria_label = div_element['aria-label']
        #Title and price in the same tag. Use regex to separate them and extract each item.
        #タイトルと値段が同じタグにいるので、正規表現で炙り出す。
        match = re.search(r'(\d{1,3}(,\d{3})*(\.\d+)?yen)', aria_label)
        if match:
            price = match.group(0)
            title = aria_label.replace(price, '').strip()
        print(price)
        print(title)

        #mark as 1 if sold out, 0 if not.　売り切れであれば1、購入可であれば0になるように設定
        sold = 1 if 'Sold' in title else 0
        print(sold)
        
        #get the href for the product page. 商品ページのURLを取得
        url = "https://jp.mercari.com" + post.find('a', class_='sc-bcd1c877-1 lpjZwE').get('href')
        print(url)

        #put the data into a list, append it to the list. データをリスト化し、格納する。
        data = {
        'Name': title,
        'Price': price,
        'Sold': sold,
        'Url': url
        }
        list.append(data)
    else: continue

#Export data (supposing pandas) 結果の出力。
df=pd.DataFrame(list)
df
