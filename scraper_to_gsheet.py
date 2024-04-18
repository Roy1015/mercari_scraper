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
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name("YOUR DIRECTORY OF JSON FILE.json", scopes) #access the json key you downloaded earlier 
file = gspread.authorize(credentials) # authenticate the JSON key with gspread
sheet = file.open("resell list") #open sheet
sheetL = sheet.sheet1

skus = sheetL.col_values(7)[1:] 
SKUs = [str(x) for x in skus if x != '']  # Use list comprehension to filter out empty values

data=[]

for sku in SKUs:
    url = "https://www.mercari.com/jp/search/?keyword=" + sku
    browser = webdriver.Chrome()
    time.sleep(5)

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
            match = re.search(r'(\d{1,3}(,\d{3})*(\.\d+)?)yen', aria_label)
            if match:
                price = float(match.group(1).replace(',', ''))   
                title = aria_label.replace(match.group(0), '').strip()
            print(price)
            print(title)
            # 購入済みであれば1、未購入であれば0になるように設定
            sold = 1 if 'Sold' in title else 0
            print(sold)

            data.append({"SKU": sku, "Name": title, "Price": price, "Sold": sold})
        else: continue

    browser.close()

df = pd.DataFrame(data)
df = df.groupby('SKU').agg({'Price':['min','mean','max'],'Name':'count','Sold':'sum'}).reset_index()

print(df)
        
# Export to Gsheet
sheetL.update('A2', df.values.tolist(), value_input_option='RAW')
