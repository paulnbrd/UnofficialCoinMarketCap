import websocket
from random_user_agent.user_agent import UserAgent
import logging
import typing
import json
import threading
import time

logger = logging.getLogger(__name__)


class WebsocketConnection:
    def __init__(self):
        ua = UserAgent().get_random_user_agent()
        logger.debug("WS connection avec ua {}".format(ua))
        self.conn = websocket.create_connection("wss://stream.coinmarketcap.com/price/latest",
                                                header=[
                                                    "User-Agent: {}".format(ua)
                                                ])
        self.running = True

    def start(self, callback: typing.Callable, crypto_ids: typing.List[int] = None, as_daemon: bool = True):
        """
        Démarrer le ws
        :param callback: la fonction appellée quand de nouvelle données arrivent
        :param crypto_ids: les ids des cryptos
        :param as_daemon: Lancer le thread en daemon ou pas
        :return: Rien, jamais
        """
        if crypto_ids is None:
            crypto_ids = [1]
        message = {"method": "subscribe", "id": "price", "data": {"cryptoIds": crypto_ids, "index": None}}
        message = json.dumps(message)
        self.conn.send(message)
        logger.debug("Starting")
        threading.Thread(target=self._handle_messages, args=(callback,), daemon=as_daemon).start()

    def _handle_messages(self, callback: typing.Callable):
        while self.running:
            callback(self.conn.recv())


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    ws = WebsocketConnection()
    ws.start(lambda x: print(x), [1])
    print("Resume")
    time.sleep(10)  # On récupère les messages pendant 10 secondes, et après ça s'arrête
    print("STOP !")
