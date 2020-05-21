import os
from datetime import datetime

import mongoengine as mongo

MONGO_URI = os.getenv('MONGO_URI')
DATABASE_NAME = 'monitor'

connection = mongo.connect(DATABASE_NAME, host=MONGO_URI)

class StockStatus(mongo.EmbeddedDocument):
    log_time = mongo.DateTimeField()
    symbol = mongo.StringField()
    last_close = mongo.StringField()
    current = mongo.StringField()
    change = mongo.StringField()
    percent_change = mongo.StringField()

class StockTrade(mongo.EmbeddedDocument):
    log_time = mongo.DateTimeField()
    symbol = mongo.StringField()
    volume = mongo.StringField()
    value = mongo.StringField()

class Snapshot(mongo.EmbeddedDocument):
    log_time = mongo.DateTimeField()
    asi = mongo.StringField()
    deals = mongo.StringField()
    volume = mongo.StringField()
    value = mongo.StringField()
    equity_cap = mongo.StringField()
    bond_cap = mongo.StringField()
    etf_cap = mongo.StringField()

class Snapshots(mongo.Document):
    log_time = mongo.DateTimeField()
    snapshot = mongo.EmbeddedDocumentField(Snapshot)

class Trades(mongo.Document):
    log_time = mongo.DateTimeField()
    stocks = mongo.ListField(mongo.EmbeddedDocumentField(StockTrade))

class Advancers(mongo.Document):
    log_time = mongo.DateTimeField()
    stocks = mongo.ListField(mongo.EmbeddedDocumentField(StockStatus))

class Decliners(mongo.Document):
    log_time = mongo.DateTimeField()
    stocks = mongo.ListField(mongo.EmbeddedDocumentField(StockStatus))


def save_snapshot(snapshot, log_time=None):
    if not log_time:
        log_time = str(datetime.now())
    
    snapshot_data = Snapshot(
        log_time = log_time,
        asi = snapshot['asi'],
        deals = snapshot['deals'],
        volume = snapshot['volume'],
        value = snapshot['value'],
        equity_cap = snapshot['equity_cap'],
        bond_cap = snapshot['bond_cap'],
        etf_cap = snapshot['etf_cap']
    )
    
    Snapshots(
        log_time = log_time,
        snapshot = snapshot_data
    ).save()

def save_trades(trades, log_time=None):
    if not log_time:
        log_time = str(datetime.now())
    
    trades_data = Trades(log_time=log_time)
    for trade in trades:
        stock_trade = StockTrade(
            log_time = log_time,
            symbol = trade[0],
            volume = trade[1],
            value = trade[2],
        )
        trades_data.stocks.append(stock_trade)
    trades_data.save()

def save_advancers(advancers, log_time=None):
    if not log_time:
        log_time = str(datetime.now())
    
    advancers_data = Advancers(log_time=log_time)
    for stock in advancers:
        stock_status = StockStatus(
            log_time = log_time,
            symbol = stock[0],
            last_close = stock[1],
            current = stock[2],
            change = stock[3],
            percent_change = stock[4],
        )
        advancers_data.stocks.append(stock_status)
    advancers_data.save()

def save_decliners(decliners, log_time=None):
    if not log_time:
        log_time = str(datetime.now())
    
    decliners_data = Decliners(log_time=log_time)
    for stock in decliners:
        stock_status = StockStatus(
            log_time = log_time,
            symbol = stock[0],
            last_close = stock[1],
            current = stock[2],
            change = stock[3],
            percent_change = stock[4],
        )
        decliners_data.stocks.append(stock_status)
    decliners_data.save()
