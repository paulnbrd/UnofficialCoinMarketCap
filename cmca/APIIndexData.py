from dataclasses import dataclass


@dataclass
class CurrencyData:
    id: int
    name: str
    symbol: str
    token: str


@dataclass
class IndexDataInitialState:
    locale: str
    theme: str
    lang: str
    country: str
    currency: CurrencyData
    message: str
    is_in_app: bool


@dataclass
class CryptocurrencyData:
    ath: float
    atl: float
    circulating_supply: int
    coin_market_cap_rank: int
    date_added: str
    has_ad_listing_button: bool
    has_filters: bool
    high_24h: float
    id: int
    is_active: bool
    last_updated: str
    low_24h: float
    market_pair_count: int
    max_supply: int
    name: str

    rank: int
    slug: str
    symbol: str
    total_supply: int
    tvl: float

    raw: dict


@dataclass
class IndexData:
    raw: dict
    is_server: bool
    initial_state: IndexDataInitialState
    cryptocurrency: list[CryptocurrencyData]


def get_initial_state(data: dict) -> IndexDataInitialState:
    return IndexDataInitialState(
            data["props"]["initialState"]["app"]["locale"],
            data["props"]["initialState"]["app"]["theme"],
            data["props"]["initialState"]["app"]["lang"],
            data["props"]["initialState"]["app"]["country"],
            CurrencyData(
                data["props"]["initialState"]["app"]["currency"]["id"],
                data["props"]["initialState"]["app"]["currency"]["name"],
                data["props"]["initialState"]["app"]["currency"]["symbol"],
                data["props"]["initialState"]["app"]["currency"]["token"]
            ),
            data["props"]["initialState"]["app"]["message"],
            data["props"]["initialState"]["app"]["isInApp"],
        )


def parse_cryptos(data: dict):
    data_keys = data["props"]["initialState"]["cryptocurrency"]["listingLatest"]["data"][0]["keysArr"]
    crypto_list = data["props"]["initialState"]["cryptocurrency"]["listingLatest"]["data"].copy()
    crypto_list.pop(0)
    cryptos = []
    for crypto in crypto_list:
        crypto_data = dict(zip(data_keys, crypto))
        cryptos.append(
            CryptocurrencyData(
                crypto_data["ath"],
                crypto_data["atl"],
                crypto_data["circulatingSupply"],
                crypto_data["cmcRank"],
                crypto_data["dateAdded"],
                crypto_data["hasAdListingButton"],
                crypto_data["hasFilters"],
                crypto_data["high24h"],
                crypto_data["id"],
                crypto_data["isActive"],
                crypto_data["lastUpdated"],
                crypto_data["low24h"],
                crypto_data["marketPairCount"],
                crypto_data["maxSupply"],
                crypto_data["name"],
                crypto_data["rank"],
                crypto_data["slug"],
                crypto_data["symbol"],
                crypto_data["totalSupply"],
                crypto_data["tvl"],
                crypto_data
            )
        )
    return cryptos


def parse_index_data(data: dict, with_raw: bool = False) -> IndexData:
    d = IndexData(
        data,
        data['props']['isServer'],
        get_initial_state(data),
        parse_cryptos(data)
    )
    if with_raw:
        return d
    d.raw = None
    return d
