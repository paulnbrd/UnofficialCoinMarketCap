import cmca
import time

# Get cryptos from bsc
print(cmca.CoinMarketCap.get_crypto_with_api(tag_slugs=["binance-smart-chain"]))

# Get coins
print(cmca.CoinMarketCap.get_coin_ids())

# Get data of main page
print(cmca.CoinMarketCap.get_parsed_index_data())

# Subscribe to token price change


def handle_change(data_received: dict):
    print("DATA RECEIVED", data_received)


print("Subscribing...")
cmca.WebsocketConnection().start(handle_change, [1])  # 1 is BTC
# The thread is launched as daemon (change it in the as_daemon arg of start())
# So we wait before closing it all. The websocket is not properly closed, but
# the same is done when you are on the website
time.sleep(10)
print("Done !")
