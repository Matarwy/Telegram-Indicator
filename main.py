from helpers import *

CONFIG = read_crypto_data('config.json')
API_KEY = CONFIG['CMC_API_KEY']
TE_API_ID = CONFIG['TELEGRAM_API_ID']
TE_API_HASH = CONFIG['TELEGRAM_API_HASH']
TE_PHONE = CONFIG['TELEGRAM_PHONE']
new_coins_data = get_new_coin(API_KEY)

coin_id_in = input("Please Enter COIN ID: ")
# window1 = int(input("Enter Window Size Period 1: "))
# window2 = int(input("Enter Window Size Period 2: "))
# window3 = int(input("Enter Window Size Period 3: "))
for coin in new_coins_data['data']:
    if coin['id'] == int(coin_id_in):
        msgcounts = get_telegram_chat(API_KEY, TE_API_ID, TE_API_HASH, TE_PHONE, coin['id'])
        plot_telegram_chat(msgcounts)
        # print(f"Price Change for {coin['name']} ({coin['symbol']}) ({coin['id']})")
        # get_price_change(API_KEY, coin['id'], coin['quote']['USD']['price'])
        # mva1 = get_moving_average(API_KEY, coin['id'], window1)
        # mva2 = get_moving_average(API_KEY, coin['id'], window2)
        # mva3 = get_moving_average(API_KEY, coin['id'], window3)
        # print(f"Moving Average for {coin['name']} ({coin['symbol']}) ({coin['id']})")
        # plot_price_with_moving_average(mva1, mva2, mva3, window1, window2, window3)
        break

