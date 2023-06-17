import requests
import json
import matplotlib.pyplot as plt
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime, timezone, timedelta


def read_crypto_data(filename):
    try:
        with open(filename, 'r') as c:
            data = json.load(c)
    except FileNotFoundError:
        data = {}
    return data


def write_crypto_data(data, filename):
    with open(filename, 'w') as d:
        json.dump(data, d)


def get_new_coin(api_key):
    url_new = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/new"
    # Set the parameters to filter recently added tokens
    params = {
        'start': '1',
        'limit': '100',  # You can adjust this value based on your requirements
        'sort_dir': 'desc'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }
    try:
        # Send the request and retrieve the response
        response = requests.get(url_new, headers=headers, params=params)
        # Parse the JSON response
        new_coins = response.json()
    except Exception as e:
        print(e)
        new_coins = {}
    return new_coins


def get_price_change(api_key, coin_id, price):
    url_price = "https://pro-api.coinmarketcap.com/v3/cryptocurrency/quotes/historical"
    intervals = [
        "5m",
        "10m",
        "30m",
        "24h",
        "7d",
        "30d",
    ]
    for interval in intervals:
        # Set the parameters to filter recently added tokens
        params = {
            'id': str(coin_id),
            'interval': interval,
            'count': '2',
            'convert': 'USD'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': api_key
        }
        try:
            # Send the request and retrieve the response
            response = requests.get(url_price, headers=headers, params=params)
            # Parse the JSON response
            price_change = response.json()
            previes_price = price_change['data'][str(coin_id)]['quotes'][0]['quote']['USD']['price']
            price_change_data = price - price_change['data'][str(coin_id)]['quotes'][0]['quote']['USD']['price']
            price_change_percentage = price_change_data / previes_price * 100
            print(f"({interval}) {'{:,.2f}'.format(price_change_percentage)}%")
        except Exception as e:
            print(e)


def get_moving_average(api_key, coin_id, window_size=5):
    url_price = "https://pro-api.coinmarketcap.com/v3/cryptocurrency/quotes/historical"
    params = {
        'id': str(coin_id),
        'interval': '5m',
        'count': '9000',
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }
    try:
        # Send the request and retrieve the response
        response = requests.get(url_price, headers=headers, params=params)
        # Parse the JSON response
        price_changes = response.json()
        if len(price_changes['data'][str(coin_id)]['quotes']) < window_size:
            print("Not enough data")
            return
        prices = []
        for i in range(len(price_changes['data'][str(coin_id)]['quotes'])):
            prices.append(price_changes['data'][str(coin_id)]['quotes'][i]['quote']['USD']['price'])
        moving_averages = []
        for i in range(len(prices) - window_size + 1):
            moving_averages.append(sum(prices[i:i + window_size]) / window_size)
        return moving_averages
    except Exception as e:
        print(e)


def plot_price_with_moving_average(moving_average1, moving_average2, moving_average3, win_size1, win_size2, win_size3):
    plt.plot(moving_average1, label=f'Moving Average {win_size1} periods')
    plt.plot(moving_average2, label=f'Moving Average {win_size2} periods')
    plt.plot(moving_average3, label=f'Moving Average {win_size3} periods')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title('Moving Average for Token 5m Prices')
    plt.legend()
    plt.show()


async def get_telegram_chat(api_key, te_api_id, te_api_hash, phone_number, coin_id):
    url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/info"
    params = {
        'id': str(coin_id),
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }
    try:
        # Send the request and retrieve the response
        response = requests.get(url, headers=headers, params=params)
        # Parse the JSON response
        telegram_chat = response.json()
        name = telegram_chat['data'][str(coin_id)]['name']
        symbol = telegram_chat['data'][str(coin_id)]['symbol']
        print(f"Telegram Chats for {name} ({symbol}) are: ")
        for chat in telegram_chat['data'][str(coin_id)]['urls']['chat']:
            if 't.me' in chat:
                print(chat)
        chat_username = input("Enter the chat @USERNAME: ")
        # Set the time intervals for historical data
        time_intervals = {
            '5m': 5 * 60,
            '30m': 30 * 60,
            '24h': 24 * 60 * 60,
            '7d': 7 * 24 * 60 * 60,
            '30d': 30 * 24 * 60 * 60
        }
        messagesCounts = {}
        # Connect to the Telegram client
        async with TelegramClient(phone_number, te_api_id, te_api_hash) as client:
            chat_entity = await client.get_entity(chat_username)
            for interval, duration in time_intervals.items():
                messages = []
                last_date = None
                current_date = datetime.now(timezone.utc)
                while True:
                    # Fetch messages with a specific time offset
                    result = await client(GetHistoryRequest(
                        peer=chat_entity,
                        limit=2500,
                        offset_date=last_date,
                        offset_id=0,
                        min_id=0,
                        max_id=0,
                        add_offset=0,
                        hash=0
                    ))
                    if not result.messages:
                        break
                    last_date = result.messages[-1].date.astimezone(timezone.utc)
                    wanted_date = current_date - timedelta(seconds=duration)
                    if last_date < wanted_date:
                        for message in result.messages:
                            message_data = message.date
                            if message_data >= wanted_date:
                                messages.append(message)
                            else:
                                break
                        break
                    else:
                        messages.extend(result.messages)
                # Process the retrieved messages for the specified duration
                print(f"Messages in the last {interval}: {len(messages)}")
                messagesCounts[interval] = len(messages)
                # Further processing or analysis of the retrieved messages can be performed here
        return messagesCounts
    except Exception as e:
        print(e)
        return None


def plot_telegram_chat(messages):
    keys = messages.keys()
    values = messages.values()
    plt.bar(keys, values)
    plt.xlabel('Time')
    plt.ylabel('Messages')
    plt.title('Messages Counts in Telegram Chat')
    plt.show()



