
import csv
import time
import timeit
import talib as ta
import numpy as np
from Robinhood import Robinhood
from pandas import *
import xlrd
from datetime import datetime
from pandas_datareader import data as da
import pandas as pd
import numpy as np
from numpy import log, polyfit, sqrt, std, subtract
import statsmodels.tsa.stattools as ts
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import pprint
from datetime import timedelta
from scipy import stats
from pandas_datareader._utils import RemoteDataError
from IPython.display import clear_output
import pymongo
import requests as r
from bs4 import BeautifulSoup as bs
import yahoo_finance
from yahoo_finance import Share
from pandas_datareader import data as pdr
import fix_yahoo_finance as yf

directory = "file/"
working_suggestion = "Trade_suggestion_minute_1st"
universe_file_name = "my_universe_industry_sector_marketcap_earnings.csv"





#
#def hedge(self,hedge_int = "UVXY"):
#    robinhood = get_robinhood()
#    hedge_int_beta =beta([hedge_int],interval ="minute")[0].iloc[0][0]
#    hedge_int_price = robinhood.get_ask_price(hedge_int)
#    position_beta = robinhood.get_my_position_beta_minute()[0]
#    position_value = robinhood.my_trader.market_value()
#    shares = abs(np.floor(position_value*position_beta/hedge_int_beta/hedge_int_price))
#
#    return shares

def beta(ticker_list,bench = "SPY", interval="day"):    
    # will return a dataframe
    robinhood = get_robinhood()
    betas = []
    volos = []
    ben_mark=pd.DataFrame()
    if interval == "day":
        ben_mark= da.DataReader(bench,"yahoo",datetime.now()-timedelta(days=90),datetime.now())
        ben_mark=ben_mark.rename(columns ={"Adj Close":bench})
    elif interval == "minute":
        ben_mark = robinhood.get_historical(bench,interval="10minute",span = "week")
        ben_mark=ben_mark.rename(columns ={"close_price":bench})
        ben_mark[bench]=ben_mark[bench].astype(float)
        ben_mark.index = ben_mark.begins_at
    ben_mark[bench + "_bench_re"] = log(ben_mark[bench]/ben_mark[bench].shift(1))
    for i in list(ticker_list):

        new=[]
        ticker = str(i)
        try:
            if interval =="day":

                stock = da.DataReader(str(ticker),"yahoo",datetime.now()-timedelta(days=90),datetime.now())
                stock = stock.rename(columns = {"Adj Close":ticker})
            elif interval == "minute":
                stock= robinhood.get_historical(ticker,interval="10minute",span = "week")
                stock=stock.rename(columns ={"close_price":ticker})
                stock[ticker] = stock[ticker].astype(float)
                stock.index = stock.begins_at
        except:
            print (str(i)+" ticker maybe wrong. Error in getting data")
            betas.append(np.NaN)
            continue

        # get return and put them in a new dataframe
        
        stock[ticker + "_stock_re"] = log(stock[ticker]/stock[ticker].shift(1))
        new = pd.concat([ben_mark,stock],axis =1)
        new = new[[bench,bench + "_bench_re",ticker, ticker + "_stock_re" ]]
        new = new.dropna()
        #calculate beta using covariance matrix
        covmat = np.cov(new[bench+ "_bench_re"],new[ticker+ "_stock_re"])
        beta = covmat[0,1]/  np.sqrt(covmat[1,1]*covmat[0,0])
        volotity = sqrt(covmat[1,1])
        betas.append(beta)
        volos.append(volotity)
    betas = pd.DataFrame(betas)
    betas.index = ticker_list
    betas.columns=["Beta"]
    return betas, covmat, volos

class get_robinhood:

    my_trader = Robinhood()

    # Placing buy orders (Robinhood.place_buy_order)
    # Placing sell order (Robinhood.place_sell_order)
    # Quote information (Robinhood.quote_data)
    # User portfolio data (Robinhood.portfolios)
    # User positions data (Robinhood.positions)
    # Examples:
    # stock_instrument = my_trader.instruments("GEVO")[0]
    # quote_info = my_trader.quote_data("GEVO")
    # buy_order = my_trader.place_buy_order(stock_instrument, 1)
    # sell_order = my_trader.place_sell_order(stock_instrument, 1)

    def get_universe(self):
        # must inclue Stock.xlsx in the dir
        self.universe=pd.read_csv(directory + 'Stock.csv',header=0)
        self.universe.columns.astype(str)
        return self.universe['Ticker']


    def get_historical(self,stock,interval='day',span='year',ifprint=False):
        
        
        #fetch historical data for stock

        #Note: valid interval/span configs
        #interval = 5minute | 10minute + span = day, week
        #interval = day + span = year
        #interval = week
        #TODO: NEEDS TESTS

        

        quote_info = self.my_trader.get_historical_quotes(stock,interval,span)['results']

        get_historical= DataFrame(quote_info[0]['historicals'])

        if (ifprint == True):

            get_historical.to_csv(stock + '.csv')


        return get_historical

    #Setup


    #Get stock information
    #Note: Sometimes more than one instrument may be returned for a given stock symbol

    #login
    def login(self,username,password):
        #username=str(input("Please input username"))
        #password = str(input("Please input password"))
        self.my_trader.login(username, password)

    def logout(self):
        self.my_trader.logout()


    def get_instrument(self,stock):


        profile = self.my_trader.instruments(stock)
        #profile = DataFrame(profile[0])
        profile = DataFrame(profile[0],index=[stock])


        return profile

    def get_fundamentals(self,stock):

        fundamentals = self.my_trader.get_fundamentals(stock)
        fundamentals = DataFrame(fundamentals,index=[stock])
        return fundamentals


    def get_stock_data(self,stock):

        quote = self.my_trader.quote_data(stock)

        quote = DataFrame(quote,index=[stock])

        return quote    

    def get_last_price(self,stock):

        quote = self.my_trader.quote_data(stock)

        quote = DataFrame(quote,index=[stock])

        return quote['last_trade_price'].astype(float)[0]

    def get_ask_price(self,stock):

        quote = self.my_trader.quote_data(stock)

        quote = pd.DataFrame(quote,index=[stock])

        return quote['ask_price'].astype(float)[0]

    def get_bid_price(self,stock):

        quote = self.my_trader.quote_data(stock)

        quote = DataFrame(quote,index=[stock])

        return quote['bid_price'].astype(float)[0]

    def order_history(self):

        orders = self.my_trader.order_history()
        orders = DataFrame(orders['results']).T
        

        return orders

    def positions_symbol(self):
        data = self.my_trader.positions()
        data = DataFrame(data['results'])
        data = data['instrument']
        out=list()
        
        for i in data:

            out.append(self.my_trader.get_url(i)['symbol'])

        return out

    def istradeable(self,stock):
        profile = self.my_trader.instruments(stock)
   
        if(profile == []):
            return Series(False,[str(stock)])

        profile_temp = DataFrame(profile[0],index=[stock])
        

        if (profile_temp['tradeable'][0]!= False | profile_temp['tradeable'][0] != True):
            i = i +1
            print "Connection may fail ", i

            return Series(False,[str(stock)])

        return profile_temp['tradeable']

    def place_buy(self, ticker,num,price=None,order_type="limit",slippage = 0.05):
        if price ==None:
            price = self.get_bid_price(ticker)
            price = round(price * (1+slippage),2)
        try:
            for i in self.my_trader.instruments(ticker):
                stock_inst = i
                if stock_inst["symbol"]==ticker:
                    print ("Ticker found in instruments :", ticker)
                    if str(self.my_trader.place_order(stock_inst,num,price,"buy",order=order_type)) == "<Response [201]>":
                         print ("Trade Success!: " + ticker)
                    else:
                         print ("Trade Fail: " + ticker)
                    time.sleep(5)
                    return
            print ("Ticker not found in instruments")
        except Exception as e:
            print e
            print ("Trade Fail: " + ticker)
            pass

    def place_sell(self, ticker,num,price=None,order_type="limit",slippage = 0.05):
        if price ==None:
            price = self.get_last_price(ticker)
            price = round(price * (1-slippage),2)
        try:
            for i in self.my_trader.instruments(ticker):
                stock_inst = i
                if stock_inst["symbol"]==ticker:
                    print ("Ticker found in instruments", ticker)
                    if str(self.my_trader.place_order(stock_inst,num,price,"sell",order=order_type)) == "<Response [201]>":
                         print ("Trade Success!: " + ticker)
                    else:
                         print ("Trade Fail: " + ticker)
                    time.sleep(2)
                    return
            print ("Ticker not found in instruments")
        except Exception as e:
            print e
            print ("Trade Fail: " + ticker)
            pass

    def get_my_positions(self):   
        my_positions=[]
        position_quantity = []
        for i in self.my_trader.positions()["results"]:
            if float(i["quantity"])>0:
                position_quantity.append(float(i["quantity"]))
                ticker = self.my_trader.get_url(i["instrument"])
                my_positions.append(ticker["symbol"])
                print ticker["symbol"] + " "+ str(i["quantity"])
        return my_positions, position_quantity
    def get_buying_power(self):
        buy = self.my_trader.get_account()["buying_power"]
        print str(buy)
        return float(buy)

    def get_my_position_beta(self):
        stocks, quantity =self.get_my_positions()
        quantity = pd.DataFrame(quantity,index = stocks,columns=["Quantity"])
        #quantity = quantity.astype(int)
        betas = beta(stocks)
        #betas = pd.DataFrame(betas[0])
        data = pd.concat([betas[0],quantity],axis=1)
        data = data.fillna(0)
        for i in data.index:
            data.loc[data.index == i,"Last_price"]=self.my_trader.quote_data(i)["last_trade_price"]
        data.Last_price = data.Last_price.astype(float)
        data["Volotity"] = sqrt(betas[2])
        data["Weight"] = data.Last_price * data.Quantity/np.dot(data.Last_price,data.Quantity)
        sum_beta=np.dot(data.Beta,data.Quantity)
        
        print data
        return data

    def get_my_position_beta_minute(self):
        stocks, quantity =self.get_my_positions()
        quantity = pd.DataFrame(quantity,index = stocks,columns=["Quantity"])
        betas = beta(stocks,interval="minute")
        #betas = pd.DataFrame(betas[0])
        data = pd.concat([betas[0],quantity],axis=1)
        data = data.fillna(0)
        data["Last_price"]=np.NaN
        for i in data.index:
            data.loc[data.index == i,"Last_price"]=self.my_trader.quote_data(i)["last_trade_price"]
        data.Last_price = data.Last_price.astype(float)
        data["Volotity"] = sqrt(betas[2])
        data["Weight"] = data.Last_price * data.Quantity/np.dot(data.Last_price,data.Quantity)
        
        
        
       
        print data
        return data
    


    def place_buy_bulk_checkup(self, ticker_list, quantity_list,price_list=None ):
        my_positions = self.get_my_positions()[0]
        if price_list == None:
            for t, q in zip(ticker_list, quantity_list):
                if t not in my_positions:
                    self.place_buy(t,q)
        else:
            for t, q,p in zip(ticker_list, quantity_list,price_list):
                if t not in my_positions:
                    self.place_buy(t,q,p)           

    def place_sell_bulk_checkup(self, ticker_list, quantity_list,price_list=None ):
        my_positions = self.get_my_positions()[0]
        if price_list == None:
            for t, q in zip(ticker_list, quantity_list):
                if t  in my_positions:
                    self.place_sell(t,q)
        else:
            for t, q,p in zip(ticker_list, quantity_list,price_list):
                if t  in my_positions:
                    self.place_sell(t,q,p)  


    def get_protfolio(self,tickers,quantity,interval = "day",bench_ticker = "SPY"):
        if interval  == "day":
            temp = da.DataReader(tickers[0],"yahoo",datetime.now()-timedelta(days=90),datetime.now())
            bench = da.DataReader(bench_ticker,"yahoo",datetime.now()-timedelta(days=90),datetime.now())
            bench = bench.rename(columns={"Adj Close":str(bench_ticker) + "_Close"})
            data = pd.DataFrame(index=temp.index)
            temp = temp.rename(columns={"Adj Close":str(tickers[0]) + "_Close"})
            temp = temp.rename(columns={"High":str(tickers[0]) + "_High"})
            temp = temp.rename(columns={"Low":str(tickers[0]) + "_Low"})
            temp = temp.rename(columns={"Open":str(tickers[0]) + "_Open"})
            data = pd.concat([data,temp[[str(tickers[0]) + "_Close",str(tickers[0]) + "_High",str(tickers[0]) + "_Low",str(tickers[0]) + "_Open"]]], axis=1)
        
            for i in tickers[1:]:
                temp = da.DataReader(i,"yahoo",datetime.now()-timedelta(days=90),datetime.now())
                temp = temp.rename(columns={"Adj Close":str(i) + "_Close"})
                temp = temp.rename(columns={"High":str(i) + "_High"})
                temp = temp.rename(columns={"Low":str(i) + "_Low"})
                temp = temp.rename(columns={"Open":str(i) + "_Open"})
                data = pd.concat([data,temp[[str(i) + "_Close",str(i) + "_High",str(i) + "_Low",str(i) + "_Open"]]], axis=1)
        elif interval == "minute":
            temp = robinhood.get_historical(tickers[0],interval="10minute",span = "week")
            bench = robinhood.get_historical(bench,interval="10minute",span = "week")
            bench = bench.index("begin_at")
            temp = temp.index("begin_at")
            bench = bench.rename(columns={"close_price":str(bench_ticker) + "_Close"})
            bench = bench[str(bench_ticker) + "_Close"].astype(float)
            bench["Bench_rte"] = log(bench[str(bench_ticker) + "_Close"]/bench[str(bench_ticker) + "_Close"].shift(1))
            data = pd.DataFrame(index=temp.index)
            temp = temp.rename(columns={"close_price":str(tickers[0]) + "_Close"})
            temp = temp.rename(columns={"high_price":str(tickers[0]) + "_High"})
            temp = temp.rename(columns={"low_price":str(tickers[0]) + "_Low"})
            temp = temp.rename(columns={"open_price":str(tickers[0]) + "_Open"})
            temp = temp[str(tickers[0]) + "_Close"].astype(float)
            temp = temp[str(tickers[0]) + "_High"].astype(float)
            temp = temp[str(tickers[0]) + "_Low"].astype(float)
            temp = temp[str(tickers[0]) + "_Open"].astype(float)
            data = pd.concat([data,temp[[str(tickers[0]) + "_Close",str(tickers[0]) + "_High",str(tickers[0]) + "_Low",str(tickers[0]) + "_Open"]]], axis=1)
        
            for i in tickers[1:]:
                temp = robinhood.get_historical(i,interval="10minute",span = "week")
                temp = temp.index("begin_at")
                temp = temp.rename(columns={"close_price":str(i) + "_Close"})
                temp = temp.rename(columns={"high_price":str(i) + "_High"})
                temp = temp.rename(columns={"low_price":str(i) + "_Low"})
                temp = temp.rename(columns={"open_price":str(i) + "_Open"})
                temp = temp[str(i) + "_Close"].astype(float)
                temp = temp[str(i) + "_High"].astype(float)
                temp = temp[str(i) + "_Low"].astype(float)
                temp = temp[str(i) + "_Open"].astype(float)
                data = pd.concat([data,temp[[str(i) + "_Close",str(i) + "_High",str(i) + "_Low",str(i) + "_Open"]]], axis=1)
        
        data_weighted = pd.DataFrame(index = data.index)
        for i, j in zip(data.columns,range(len(data.columns))):
            #j = int(np.ceil(j / 3))
            j = j/4
            data_weighted = pd.concat([data_weighted,data[i] * quantity[j]],axis=1)
        data_weighted["Sum_Close"] = data_weighted.filter(regex="Close").sum(axis=1)
        data_weighted["Sum_High"] = data_weighted.filter(regex="High").sum(axis=1)
        data_weighted["Sum_Low"] = data_weighted.filter(regex="Low").sum(axis=1)
        data_weighted["Sum_Open"] = data_weighted.filter(regex="Open").sum(axis=1)
        print "Length: ", len(data_weighted)
        data_weighted = data_weighted.dropna()
        print "Length after drop ", len(data_weighted)
        #one day trade backtest
        data_weighted = pd.concat([data_weighted,bench[str(bench_ticker) + "_Close"]],axis = 1)
        data_weighted["intraday_return"] = log(data_weighted.Sum_Close / data_weighted.Sum_Close.shift(1))
        data_weighted["Bench_rte"] = log(data_weighted[str(bench_ticker) + "_Close"] / data_weighted[str(bench_ticker) + "_Close"].shift(1))
        #data_weighted["intraday_return_prt"] = (data_weighted.Sum_Close - data_weighted.Sum_Close.shift(1))/data_weighted.Sum_Close.shift(1)
        
        print "Length: ", len(data_weighted)
        data_weighted = data_weighted.dropna()
        print "Length after drop ", len(data_weighted)
        
        covmat = np.cov(data_weighted["intraday_return"],data_weighted["Bench_rte"])
        beta = covmat[0,1]/  np.sqrt(covmat[1,1]*covmat[0,0])
        volatility = sqrt(covmat[0,0])
        
        
        
        return (data_weighted,beta,volatility)

    def get_last_order_ticker(self,date):
        history = self.my_trader.order_history()
        history = pd.DataFrame.from_dict(history["results"])
        for i in history.index:
            history.loc[i, "created_at"] = history.iloc[i].created_at[0:10]
        #recent_dates = list(set(history.created_at))[-1]
        last_order = history.loc[history.created_at==date]
        last_order_ticker =[]
        quantity = []
        for i in range(len(last_order)):
            if last_order.iloc[i].side == "buy" and last_order.iloc[i].executions:
                last_order_ticker.append(self.my_trader.get_url(last_order.iloc[i].instrument)["symbol"])
                quantity.append(last_order.iloc[i].cumulative_quantity)
        print "DONE"
        result = pd.DataFrame( [list(last_order_ticker),quantity]).T
        result.columns = ["Ticker","Quantity"]
        result = result.dropna()
        return result
    def hedge(self,hedge_int = "UVXY",target_beta =0.0):
        hedge_int_beta =beta([hedge_int],interval ="minute")[0].iloc[0][0]
        hedge_int_price = self.get_ask_price(hedge_int)
        stocks, quantity =self.get_my_positions()
        position_beta = self.get_protfolio(stocks, quantity,interval = "minute")
        position_value = float(self.my_trader.portfolios()["last_core_equity"])
        shares = abs(np.floor(position_value*(target_beta-position_beta)/hedge_int_beta/hedge_int_price))

        return shares       