import telebot
import json
import requests
import re
import time
from telebot import types

#const data
TOKEN = 'YOUR_TOKEN'
bot_name = 'YOUR_BOT'
file_path = 'price_tracker.json'
headers = {"User-Agent" : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}

#create an instance of the bot
bot = telebot.TeleBot(TOKEN,parse_mode=None)

#get names and prices of products
def get_product(url):
    try:
        data = requests.get(url,headers=headers).text
        data = re.search('"a-price-whole">.*?<',data).group()
        pattern = r'(\d{1,3}(?:,\d{3})*)(?:\.\d+)?'
        price = re.search(pattern,data).group()
        name = url.split('/')[3]
        
        return name,price
    except:
        print('error')

#remove an url
def rmv_product(product):
    pass

#database connection
def get_data(file_path):
    try:
        with open(file_path,'r') as f:
            data = json.load(f) #convert json data to python string
    except:
        data ={}
    return data

#save the data back to the json file
def save_data(data,file_path):
    with open(file_path,'w') as f: #opens in write mode to completely write the data
        json.dump(data,f,indent=2) #dump python string as json data

#everyday sender
def everyday():
    print('everyday working')
    data = get_data('price_tracker.json')
    #print(data)
    for i in data: # i : user_id
        for j in range(len(data[i])):
            #print(data[i][j])
            p_name,p_price = get_product(data[i][j])
            bot.send_message(i,f'Hey,today the price for {p_name} is ₹{p_price}')

    time.sleep(120) #86400

#initiator
@bot.message_handler(commands =['start']) #decorator
def start_handler(msg): #only one param the msg
    print('every day hanlder')
    bot.reply_to(msg,'Hey,there!') #bot replies to the msg(start) with Hey,there!
    while True: #loop to execute everyday
        try:
            everyday() 
        except:
            #bot.send_message(msg.chat.id,'Ran into an error..try again in a bit')
            print('STOPPED !')
            continue


#url_handler
@bot.message_handler(commands=['url'])
def url_handler(msg):
    #get the url
    url = msg.text.replace('/url','').strip() #parses the url
    p_name,p_price = get_product(url)
    bot.send_message(msg.chat.id,f'The current price for {p_name} is ₹{p_price}')
    usr_id = str(msg.chat.id) #needs to be a string
    #print(usr_id)

    #sends data to database
    json_data = get_data(file_path)
    print(json_data)

    if usr_id in json_data: #if already exists then just append
        json_data[usr_id].append(url)
    else:
        json_data[usr_id] = [url] #if user doesnt exist then make it and put the url in a list
    
    save_data(json_data,file_path)


    bot.send_message(msg.chat.id,url)

#remove handler
@bot.message_handler(commands=['remove'])
def rmv_handler(msg):
    print('started')
    json_data = get_data(file_path)
    usr_id = str(msg.chat.id)
    markup = types.InlineKeyboardMarkup() #sets up inline options
    for i in range(len(json_data[usr_id])):
        item_btn = types.InlineKeyboardButton(json_data[usr_id][i], callback_data=str(i))
        markup.row(item_btn)

    bot.send_message(msg.chat.id, "Choose an option:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    json_data = get_data(file_path)
    usr_id = str(call.message.chat.id)
    json_data[usr_id].pop(int(call.data))
    save_data(json_data,file_path)
    bot.answer_callback_query(call.id, f'You selected Option {call.data}')

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id) #hide the option table once done

print('PriceTrackerBot...')
bot.polling()

