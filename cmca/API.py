import logging
from functools import lru_cache

import requests
from bs4 import BeautifulSoup
import json
from .APIIndexData import parse_index_data

logger = logging.getLogger(__name__)


# TODO: https://api.coinmarketcap.com/data-api/v3/map/all?listing_status=active, pour avoir tous les coins

class CoinMarketCap:
    @staticmethod
    @lru_cache(maxsize=None)
    def get_coin_ids(rep: int = 1, lim: int = 10000):
        """
        Récupérer les coin ids
        :param rep: Le nombre de pages à get (*lim)
        :param lim: Limite par page (0<lim<=10000)
        :return: Les coin ids
        """
        assert type(rep) is int
        assert rep >= 1
        assert type(lim) is int
        assert 0 < lim <= 10000

        aux = "platform,first_historical_data,last_historical_data,is_active,status"
        url = "https://api.coinmarketcap.com/data-api/v3/map/all?listing_status=active," \
              "untracked&exchangeAux=is_active,status&cryptoAux="+aux+"&start={start}&limit=" + str(lim)
        ranges: list = [1]
        for i in range(rep - 1):
            ranges.append(ranges[i] + lim + 1)
        urls = [url.format(start=index) for index in ranges]
        logging.debug("Start values: " + str(ranges))

        coins = []
        for u in urls:
            request = requests.get(u)
            if request.status_code != 200:
                logger.error("Could not fetch {} (code {})".format(u, request.status_code))
                continue
            data = request.json()
            if data["status"]["error_message"] != "SUCCESS":
                logger.error("Server error for URL {}".format(u))
            data_coins = data.get("data").get("exchangeMap")
            coins.extend(data_coins)
        logger.info("Fetched {} coins".format(len(coins)))
        return coins

    @staticmethod
    @lru_cache(maxsize=None)
    def get_index_data(url: str = None):
        """
        Get the raw index data (on the index page of coinmarketcap, english)
        :param url: You can try https://coinmarketcap.com/{COUNTRY_CODE}/ or just let it None
            (default to https://coinmarketcap.com/)
        :return: The dictionnary of raw data
        """
        if url is None:
            url = "https://coinmarketcap.com/"
        request = requests.get(url)
        soup = BeautifulSoup(request.text, "html.parser")
        contents = soup.find("script", {"id": "__NEXT_DATA__"}).contents
        return json.loads(contents[0])

    @staticmethod
    def get_parsed_index_data(url: str = None, with_raw: bool = False):
        """
        Get self.get_index_data() as dataclass
        :param url: The url to fetch from (let it None to have the least problems possible), or try with country codes
        :param with_raw: Include the raw data in the dataclass
        :return: IndexData dataclass, explore by yourself
        """
        data = CoinMarketCap.get_index_data(url)
        return parse_index_data(data, with_raw=with_raw)

    @staticmethod
    def get_crypto_with_api(
            start: int = 1,
            limit: int = 10000,
            sort_by: str = "market_cap",
            sort_type: str = "desc",
            convert: list[str] = None,
            crypto_type: str = "all",
            tag_type: str = "all",
            audited: bool = False,
            aux: list[str] = None,
            tag_slugs: list[str] = None
    ):
        """
        Make your own api call with specific arguments
        :param start: The starting crypto
        :param limit: The limit of result (no idea what is the limit of the limit)
        :param sort_by: Sorting order, idk the possible values
        :param sort_type: Self explanatory, desc, asc
        :param convert: The tokens you want the cryptos in (USD, ETH, BTC, ...)
        :param crypto_type: no idea, put all
        :param tag_type: no idea, put all
        :param audited: no idea, put all (I guess)
        :param aux: The infos you want on the crypto (ath,atl,high24h,...)
        :param tag_slugs: The ecosystems to search on (polkadot-ecosystem, avalanche-ecosystem, ...)
        :return: dict of the cryptos (explore yourself !)
        """
        if tag_slugs is None:
            tag_slugs = ["avalanche-ecosystem", "polkadot-ecosystem"]
        if aux is None:
            aux = "ath,atl,high24h," \
                  "low24h,num_market_pairs,cmc_rank,date_added,tags,platform,max_supply,circulating_supply,total_supply," \
                  "volume_7d,volume_30d"
            aux = aux.split(",")
        if convert is None:
            convert = ["USD", "BTC", "ETH"]
        base_url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?"

        url = base_url + \
              "start=" + str(start) + \
              "&limit=" + str(limit) + \
              "&sortBy=" + str(sort_by) + \
              "&sortType=" + str(sort_type) + \
              "&convert=" + ",".join(convert) + \
              "&cryptoType=" + str(crypto_type) + \
              "&tagType=" + str(tag_type) + \
              "&audited=" + ("true" if audited else "false") + \
              "&aux=" + ",".join(aux) + \
              "&tagSlugs=" + ",".join(tag_slugs)
        request = requests.get(url)
        if request.status_code != 200:
            return None
        return request.json()


if __name__ == "__main__":
    print(json.dumps(CoinMarketCap.get_index_data()))
    exit()
    logging.basicConfig(level="DEBUG")
    _coins = CoinMarketCap.get_coin_ids(lim=5)
    print(_coins)
