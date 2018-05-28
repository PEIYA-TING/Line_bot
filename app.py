import requests
from bs4 import BeautifulSoup 
from lxml import html, etree
import os
import re

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

##
arg_ss = "桃園"
arg_checkin_year = 2018
arg_checkin_month = 6
arg_checkin_monthday= 14
arg_checkout_year = 2018
arg_checkout_month = 6
arg_ckeckout_monthday = 20
arg_adults = 2
arg_group_children = 0
url = 'https://www.booking.com/searchresults.zh-tw.html?ss=\"' + str(arg_ss) + '\"&checkin_year=' + str(arg_checkin_year) + '&checkin_month=' + str(arg_checkin_month) + '&checkin_monthday=' + str(arg_checkin_monthday) + '&checkout_year=' + str(arg_checkout_year) +  '&checkout_month=' + str(arg_checkout_month) + '&ckeckout_monthday=' + str(arg_ckeckout_monthday) + '&group_adults=' + str(arg_adults) + '&group_children=' + str(arg_group_children)

##

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    ####
    result = requests.get(url)  
    result.encoding = 'utf8'
    root = etree.fromstring(result.content, etree.HTMLParser())  
    # print(root)
    mode = re.compile(r'\d+\.?\d*')

    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')

    name = soup.select('.sr-hotel__name')
    name_list = []

    for i in range(len(name)):
        a = name[i].contents
        name_list.append(a[0].split("\n")[1])
        
    # print(name_list)
    # print(len(name_list))
    output = name_list

    ####
    message = TextSendMessage(text=output)
    line_bot_api.reply_message(
        event.reply_token,
        message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
