import urllib2
import datetime
import time
from threading import Timer

from Cryptsy import Cryptsy

MARKET_IDS = {u'FRK/BTC': 33, u'CGB/BTC': 70, u'FRC/BTC': 39, u'SBC/BTC': 51, u'BTB/BTC': 23, u'NET/XPM': 104, u'ANC/BTC': 66, u'UNO/BTC': 133, u'GLC/BTC': 76, u'ASC/XPM': 112, u'IXC/BTC': 38, u'MEC/BTC': 45, u'DOGE/LTC': 135, u'CLR/BTC': 95, u'WDC/LTC': 21, u'MST/LTC': 62, u'CMC/BTC': 74, u'Points/BTC': 120, u'XNC/LTC': 67, u'CPR/LTC': 91, u'MOON/LTC': 145, u'NET/BTC': 134, u'BTG/BTC': 50, u'CRC/BTC': 58, u'XJO/BTC': 115, u'EMD/BTC': 69, u'42/BTC': 141, u'TAG/BTC': 117, u'NVC/BTC': 13, u'FTC/BTC': 5, u'QRK/BTC': 71, u'DVC/BTC': 40, u'DBL/LTC': 46, u'PHS/BTC': 86, u'PTS/BTC': 119, u'NEC/BTC': 90, u'ZET/BTC': 85, u'CAP/BTC': 53, u'PPC/BTC': 28, u'TIPS/LTC': 147, u'TRC/BTC': 27, u'LTC/BTC': 3, u'SRC/BTC': 88, u'OSC/BTC': 144, u'STR/BTC': 83, u'BUK/BTC': 102, u'CSC/BTC': 68, u'GLD/BTC': 30, u'AMC/BTC': 43, u'TIX/LTC': 107, u'RYC/LTC': 37, u'CNC/BTC': 8, u'MEM/LTC': 56, u'DGC/BTC': 26, u'ORB/BTC': 75, u'LKY/BTC': 34, u'XPM/BTC': 63, u'CAT/BTC': 136, u'MNC/BTC': 7, u'DVC/LTC': 52, u'LOT/BTC': 137, u'ARG/BTC': 48, u'JKC/LTC': 35, u'NRB/BTC': 54, u'DEM/BTC': 131, u'ELP/LTC': 93, u'GLD/LTC': 36, u'WDC/BTC': 14, u'IFC/LTC': 60, u'CGB/LTC': 123, u'RED/LTC': 87, u'HBN/BTC': 80, u'ELC/BTC': 12, u'XPM/LTC': 106, u'DGC/LTC': 96, u'DVC/XPM': 122, u'GDC/BTC': 82, u'COL/LTC': 109, u'PXC/LTC': 101, u'PYC/BTC': 92, u'EZC/LTC': 55, u'ANC/LTC': 121, u'NET/LTC': 108, u'BCX/BTC': 142, u'ASC/LTC': 111, u'FST/BTC': 44, u'KGC/BTC': 65, u'SBC/LTC': 128, u'MOON/BTC': 146, u'LK7/BTC': 116, u'FST/LTC': 124, u'ZET/LTC': 127, u'TEK/BTC': 114, u'SPT/BTC': 81, u'MEC/LTC': 100, u'YBC/BTC': 73, u'BTE/BTC': 49, u'CNC/LTC': 17, u'TIX/XPM': 103, u'SXC/LTC': 98, u'RPC/BTC': 143, u'QRK/LTC': 126, u'PPC/LTC': 125, u'DMD/BTC': 72, u'NMC/BTC': 29, u'GME/LTC': 84, u'COL/XPM': 110, u'TGC/BTC': 130, u'NBL/BTC': 32, u'NAN/BTC': 64, u'EAC/BTC': 139, u'IFC/XPM': 105, u'FFC/BTC': 138, u'ALF/BTC': 57, u'PXC/BTC': 31, u'DOGE/BTC': 132, u'FLO/LTC': 61, u'BQC/BTC': 10, u'CENT/XPM': 118, u'GLX/BTC': 78, u'BET/BTC': 129}


def retry_request(func, *args, **kwargs):
    sleep_retry = 1
    times = 2
    for _ in range(times):
        try:
            response = func(*args, **kwargs)
            if int(response['success']) == 1:
                return response
            else:
                print response
                raise urllib2.HTTPError()
        except urllib2.HTTPError as e:
            print "%s; Retrying in %s seconds" % (e, sleep_retry)
            time.sleep(sleep_retry)
    print "Failed %s times; raising" % times
    raise

class CryptsyTrade(object):
    def __init__(self, data):
        self.id = data["id"]
        self.time = data["time"]
        self.price = data["price"]
        self.quantity = data["quantity"]
        self.total = data["total"]

    def __repr__(self):
        return "%s\nPrice: %s\nQuantity: %s\nTotal: %s" % (
            self.time, self.price, self.quantity, self.total)


class CryptsyOrder(object):
    def __init__(self, data, order_type, marketid, created=None, orderid=None, exchange=None):
        self.orderid = orderid
        self.created = created
        self.order_type = order_type
        self.marketid = marketid
        self.price = data['price']
        self.quantity = data['quantity']
        self.total = data['total']

        self.exchange = exchange

    def place(self):
        if self.exchange is not None:
            self.result = self.exchange.createOrder(self.marketid, self.order_type, self.quantity, self.price)
        else:
            raise Exception("No exchange set!")
        if self.result:
            self.orderid = self.result
        return self.result

    def cancel(self):
        if self.exchange is not None:
            self.result = self.exchange.cancelOrder(self.orderid)
        else:
            raise Exception("No exchange set!")
        return self.result

    def calculate_fees(self):
        if self.exchange is not None:
            fee, net = self.exchange.calculateFees(self.order_type, self.quantity, self.price)
            self.fees = {'fee': fee, 'net': net}
        else:
            raise Exception("No exchange set!")
        return self.fees

    def __repr__(self):
        return "%s\nPrice: %s\nQuantity: %s\nTotal: %s" % (
            self.order_type, self.price, self.quantity, self.total)


class CryptsyMarket(object):
    def __init__(self, data):
        self.data = data
        self.fetched = datetime.datetime.now()
        self.marketid = data["marketid"]
        self.label = data["label"]
        self.lasttradeprice = data["lasttradeprice"]
        self.volume = data["volume"]
        self.lasttradetime = data["lasttradetime"]
        self.primaryname = data["primaryname"]
        self.primarycode = data["primarycode"]
        self.secondaryname = data["secondaryname"]
        self.secondarycode = data["secondarycode"]
        self.recent_trade_data = self.trade_factory(data['recenttrades'])
        self.sell_order_data = self.order_factory(data['sellorders'], "Sell", self.marketid)
        self.buy_order_data = self.order_factory(data['buyorders'], "Buy", self.marketid)

    def trade_factory(self, trade_data):
        return [CryptsyTrade(data) for data in trade_data]

    def recent_trades(self, limit=100):
        return self.recent_trade_data[:limit]

    def order_factory(self, order_data, order_type, marketid, orderid=None):
        return [CryptsyOrder(data, order_type, marketid, orderid=orderid) for data in order_data]

    def sell_orders(self, limit=20):
        return self.sell_order_data[:limit]

    def buy_orders(self, limit=20):
        return self.buy_order_data[:limit]

    def last_trade(self):
        return self.recent_trade_data[0]

    def __repr__(self):
        return self.label


class CryptsyMarkets(object):
    def __init__(self, data):
        self.data = data
        self.fetched = datetime.datetime.now()
        if data['success'] == 1:
            self.markets = self.market_factory(data['return']['markets'])

    def market_factory(self, market_data):
        markets = {}
        for market, data in market_data.iteritems():
            markets[market] = CryptsyMarket(data)
        return markets

    def market(self, market):
        return self.markets[market]

    def __repr__(self):
        return "%s" % self.fetched

    def __iter__(self):
        return self.markets.itervalues()


class ChaChing(object):

    def __init__(self, public_key, private_key, auto_trade=False, trade_timer=60):
        self.exchange = Cryptsy(public_key, private_key)
        self._market_cache = []
        self._all_markets_cache = []
        self._markets_to_cache = 10
        self.trade_timer = trade_timer
        self.timer = None
        if auto_trade:
            self.execute_trade()

    def stop_trading(self):
        if self.timer is not None:
            self.timer.cancel()
        else:
            raise Exception("Trading is not running!")

    def start_trading(self):
        if self.timer is None:
            self.timer = Timer(self.trade_timer, self.execute_trade).start()
        else:
            raise Exception("Trading is already running! stop it first if you want to restart")

    def _cache_market(self, market):
        if len(self._market_cache) >= self._markets_to_cache:
            _ = self._market_cache.pop()
        self._market_cache.reverse()
        self._market_cache.append(market)
        self._market_cache.reverse()

    def _cache_all_markets(self, markets):
        if len(self._all_markets_cache) >= self._markets_to_cache:
            _ = self._all_markets_cache.pop()
        self._all_markets_cache.reverse()
        self._all_markets_cache.append(markets)
        self._all_markets_cache.reverse()

    def my_orders(self, market):
        response = retry_request(self.exchange.myOrders, MARKET_IDS[market])
        orders = [CryptsyOrder(
            order, order['ordertype'], MARKET_IDS[market], created=order['created'], orderid=order['orderid'], exchange=self.exchange
            ) for order in response['return']]
        response = orders
        return response

    def balances_available(self):
        response = retry_request(self.exchange.getInfo)
        balances = response['return']['balances_available']
        return balances

    def balance(self, coin):
        balances = self.balances_available()
        return balances[coin]

    def openordercount(self):
        response = retry_request(self.exchange.getInfo)
        openordercount = response['return']['openordercount']
        return openordercount

    def fetch_all_markets(self):
        market_data = retry_request(self.exchange.getMarketDataV2)
        markets = CryptsyMarkets(market_data)
        self._cache_all_markets(markets)
        return markets

    def get_all_markets(self):
        try:
            markets = self._all_markets_cache[0]
        except IndexError:
            markets = self.fetch_all_markets()
        return markets

    def fetch_market(self, market):
        market_data = retry_request(self.exchange.getSingleMarketData, MARKET_IDS[market])
        market = CryptsyMarket(market_data['return']['markets'].itervalues().next())
        self._cache_market(market)
        return market

    def get_market(self, market):
        try:
            market = self._market_cache[0]
        except IndexError:
            market = self.fetch_market(market)
        return market

    def trade(self):
        raise NotImplementedError

    def execute_trade(self):
        self.trade()
        self.timer = Timer(self.trade_timer, self.execute_trade).start()


class TradeBot2000(ChaChing):
    """
    In order to implement a bot just subclass ChaChing
    The only requirement is that you define a method "trade"
    This is where you can spawn your logic to manage and execute your trades
    or whatever you want to do.

    If you set 'auto_trade' to true during initialization this method will be
    called once every 'trade_timer' seconds (default of 60)
    """
    def trade(self):
        pass
