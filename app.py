import requests
from bs4 import BeautifulSoup 
from lxml import html, etree
import os
import re
import pandas as pd
from urllib.parse import quote
import urllib.request
import ssl
from chatbase import Message


from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
# from linebot.models import (
#     MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
# )
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, LocationMessage, TemplateSendMessage,
    ButtonsTemplate, CarouselTemplate, PostbackTemplateAction, CarouselColumn , URITemplateAction , SourceUser
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

    profile = line_bot_api.get_profile(event.source.user_id)

    input_str = event.message.text

    print(profile.display_name)
    ##
    arg_ss = input_str.split()[0]
    arg_checkin_year = input_str.split()[1]
    arg_checkin_month = input_str.split()[2]
    arg_checkin_monthday= input_str.split()[3]
    arg_checkout_year = input_str.split()[4]
    arg_checkout_month = input_str.split()[5]
    arg_ckeckout_monthday = input_str.split()[6]
    arg_adults = input_str.split()[7]
    arg_group_children = input_str.split()[8]
    url = 'https://www.booking.com/searchresults.zh-tw.html?ss=\"' + quote(str(arg_ss)) + '\"&checkin_year=' + quote(str(arg_checkin_year)) + '&checkin_month=' + quote(str(arg_checkin_month)) + '&checkin_monthday=' + quote(str(arg_checkin_monthday)) + '&checkout_year=' + quote(str(arg_checkout_year)) +  '&checkout_month=' + quote(str(arg_checkout_month)) + '&ckeckout_monthday=' + quote(str(arg_ckeckout_monthday)) + '&group_adults=' + quote(str(arg_adults)) + '&group_children=' + quote(str(arg_group_children))
    ##
    print("===================================")
    print(url)
    print("===================================")
    ####
    context = ssl._create_unverified_context()

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
    #headers = {"User-Agent": "curl/7.19.7 (universal-apple-darwin10.0) libcurl/7.19.7 OpenSSL/0.9.8r zlib/1.2.3"}

    request = urllib.request.Request(url, headers = headers)

    response = urllib.request.urlopen(request, context = context)

    soup = BeautifulSoup(response, 'html.parser')

    ##
    ### Hotel Title ###
    name = soup.select('.sr-hotel__name')
    name_list = []

    for i in range(len(name)):
        a = name[i].contents
        name_list.append(a[0].split("\n")[1])

    ### Hotel Price ###
    #price availprice no_rack_rate
    price_list = soup.find_all("strong", {"class":"price"})
    prices_list = []

    for price in price_list:  
    #     print(price.text.replace(u'\xa0', u' ').replace("\n", "").split()[1])
        p = price.text.replace(u'\xa0', u' ').replace("\n", "").split()[1]
        
        if len(p) > 3:
            c = p.split(',')
            Price = c[0] + c[1]
            Price = int(Price)
        
        else:
            Price = int(p)
            
        prices_list.append(Price)

    ### Hotel Score ###
    star = soup.find_all("span",{"class":"review-score-badge"})
    score_list = []


    for i in range(len(star)):
    #     print(star[i].text.split()[0])
        score_list.append(star[i].text.split()[0])

    ### Hotel URL ###
    link = soup.find_all("a",{"class":"hotel_name_link url"})
    url1 = "https://www.booking.com/"
    url_list = []

    for i in range(len(link)):
        url2 = link[i].get('href').split("\n")[1]
        url3 = link[i].get('href').split("\n")[2]
        url = url1 + url2 + url3
        url_list.append(url)

    ### Hotel Image URL ###
    img_url = soup.find_all("img",{"class":"hotel_image"})
    img_list = []

    for i in range(len(img_url)):
        img_list.append(img_url[i].get('src'))


    try:
        # length = min(len(name_list),len(prices_list),len(star),len(link),len(img_url))
        length = min(len(name_list),len(star),len(link),len(img_url))


        print("===================================")
        print(length)
        print(len(name_list))
        print(len(star))
        print(len(link))
        print(len(img_url))
        print("===================================")

        end = length - 2
        name_list = name_list[0:end]
        # prices_list = prices_list[0:end]
        url_list = url_list[0:end]
        score_list = score_list[0:end]
        img_list = img_list[0:end]

        hotel_df = pd.DataFrame({"Hotel_name":name_list,"Hotel_url":url_list,"Hotel_score":score_list,"Hotel_pic":img_list}) #"Hotel_price":prices_list,
        hotel_df = hotel_df.sort_values(by = ['Hotel_score'],ascending=False).reset_index(drop=True)

        hotel_df = hotel_df[:6]
        hotel_df = hotel_df[["Hotel_name","Hotel_url","Hotel_score","Hotel_pic"]]
        print(hotel_df.iloc[0,0])
        print(hotel_df.iloc[0,1])
        print(hotel_df.iloc[0,2])
        print(hotel_df.iloc[0,3])

        carousel_template = CarouselTemplate(

            columns=[
                CarouselColumn(
                    thumbnail_image_url=hotel_df.iloc[0,3],
                    title = hotel_df.iloc[0,0][:20],
                    text = '(⊙０⊙)首推訂房(⊙０⊙)',
                    actions=[
                        URITemplateAction(
                            label='評分為：'+str(hotel_df.iloc[0,2]),
                            uri=hotel_df.iloc[0,1]
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url=hotel_df.iloc[1,3],
                    title = hotel_df.iloc[1,0][:20],
                    text = '(⊙ˍ⊙)激推訂房(⊙ˍ⊙)',
                    actions=[
                        URITemplateAction(
                            label='評分為：'+str(hotel_df.iloc[1,2]),
                            uri=hotel_df.iloc[1,1]
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url=hotel_df.iloc[2,3],
                    title = hotel_df.iloc[2,0][:20],
                    text = '(ˊ● ω ●ˋ)再推訂房(ˊ● ω ●ˋ)',
                    actions=[
                        URITemplateAction(
                            label='評分為：'+str(hotel_df.iloc[2,2]),
                            uri=hotel_df.iloc[2,1]
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url=hotel_df.iloc[3,3],
                    title = hotel_df.iloc[3,0][:20],
                    text = '(♡∀♡)再推一個(♡∀♡)',
                    actions=[
                        URITemplateAction(
                            label='評分為：'+str(hotel_df.iloc[3,2]),
                            uri=hotel_df.iloc[3,1]
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url=hotel_df.iloc[4,3],
                    title = hotel_df.iloc[4,0][:20],
                    text = '(´･ω･`)選我選我(´･ω･`)',
                    actions=[
                        URITemplateAction(
                            label='評分為：'+str(hotel_df.iloc[4,2]),
                            uri=hotel_df.iloc[4,1]
                        )
                    ]
                )
            ]     
        )

    except:
        error_message = "天啊!出錯了!\n您可能是遇到了以下問題。\n1.你的指令打錯了。\n指令是：訂房地點(ex:桃園) 訂房日期(ex:2018 6 30) 退房日期(ex:2018 7 2) 訂房人數，分別為大人個數與小孩個數(ex:4 2)\n每個之間都有空格噢\n範例：桃園 2018 6 30 2018 7 2 4 2\n2.您所蒐尋的日期還未提供訂房資訊，要再等一等噢!\n3.沒有相關訂房資訊，建議您換個關鍵字。\n"
        message = TextSendMessage(text=error_message)
        line_bot_api.reply_message(event.reply_token,message)\

        msg = Message(api_key="bf6041f2-134c-4c38-a42e-6540684311d0",
              type="user",
              platform="Line",
              version="1.0",
              user_id=profile.display_name,
              message=error_message,
              intent="LinebotSearchPostion",  
              not_handled=True,           
              )            
        resp = msg.send()


    ##################
    # output = ""
    # for i in range(6):
    #     tmp = hotel_df.iloc[i,0] + " " + hotel_df.iloc[i,1] + " " + hotel_df.iloc[i,2]
    #     output = output + tmp
    #     output = output + "\n"
    #     tmp = ""
    # output = hotel_df.iloc[0,1]

    ####
    # Carousel_template = hotel_df.iloc[0,3]
    # message = TextSendMessage(text=output)
    template_message = TemplateSendMessage(
        alt_text = '距離最近的五間旅館', 
        template = carousel_template
    )
    
    line_bot_api.reply_message(event.reply_token, template_message)

    msg = Message(api_key="bf6041f2-134c-4c38-a42e-6540684311d0",
              type="user",
              platform="Line",
              version="1.0",
              user_id=profile.display_name,
              message=event.message.text,
              intent="LinebotSearchPostion",  
              not_handled=False,           
              )            
    resp = msg.send()


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
