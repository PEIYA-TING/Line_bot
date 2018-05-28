from selenium import webdriver
import re  
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('gXcZroHsNzZfIaB4SczZTH2Iv6RI8tXGVyNqWJSBaCd7vfwwuTlW1qr4DOlv1AWHJy4Xs+EIGp3UKxmUtxyubD8XKsIRozgbbgPARcWAaw8NA4lsFkOHkH1LEj1FTsVYHsD8n7QmcD7d/792pvA9lQdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('3bac752e3fcb40bcd0d75e6a0d456902')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text) #event.message.text
    ###

    arg_ss = "桃園"
    arg_checkin_year = 2018
    arg_checkin_month = 6
    arg_checkin_monthday= 14
    arg_checkout_year = 2018
    arg_checkout_month = 6
    arg_ckeckout_monthday = 20
    arg_adults = 2
    arg_group_children = 0

    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    browser = webdriver.Chrome('C:/Users/DING/chromedriver.exe',chrome_options=option) #'C:/Users/DING/chromedriver.exe'

    url = 'https://www.booking.com/searchresults.zh-tw.html?ss=\"' + str(arg_ss) + '\"&checkin_year=' + str(arg_checkin_year) + '&checkin_month=' + str(arg_checkin_month) + '&checkin_monthday=' + str(arg_checkin_monthday) + '&checkout_year=' + str(arg_checkout_year) +  '&checkout_month=' + str(arg_checkout_month) + '&ckeckout_monthday=' + str(arg_ckeckout_monthday) + '&group_adults=' + str(arg_adults) + '&group_children=' + str(arg_group_children)

    browser.get(url)

    hotel_list = browser.find_elements_by_class_name("sr-hotel__title")
    mode = re.compile(r'\d+\.?\d*')
    num = browser.find_elements_by_xpath("//span[@class='review-score-badge']")

    price = browser.find_elements_by_xpath("//strong[contains(@class,'price')]") #//strong[@class='availprice']/b[1]
    pic = browser.find_elements_by_xpath("//img[@class='hotel_image']")

    cnt = 0
    cnt_2 = 0

    hotel_title = []
    score = []
    Price =[]
    hotel_url = []
    img_url = []

    for hotel in hotel_list:
        element = hotel.find_elements_by_class_name("hotel_name_link")[0]

        hotel_title1 = element.get_attribute("text").split()[0]
        hotel_title.append(element.get_attribute("text").split()[0])
        hotel_url1 = element.get_attribute("href")
        hotel_url.append(element.get_attribute("href"))
        
        number = mode.findall(num[cnt].text)
        score.append(number[0])
    #     print(number[0])
        
    #     print(cnt)
    #     print(price[cnt])
        
        Price1 = price[cnt].text
        Price.append(Price1)
        
        
        cnt += 1
        
        if cnt > 5:
            break
        
    #     print("title:")
    #     print(hotel_title1)
    #     print("url:")
    #     print(hotel_url1)
    #     print("score")
    #     print(number)
    #     print("Price")
    #     print(Price1)

    for i in pic:
        img_src = i.get_attribute("src")
        img_url.append(i.get_attribute("src"))
        
        cnt_2 += 1
    #     print("img_src")
    #     print(img_src)
        
        if cnt_2 > 5:
            break
    

    output = hotel_title[0]

    ###

    line_bot_api.reply_message(
        event.reply_token,
        output)


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
