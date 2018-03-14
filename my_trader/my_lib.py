


from my_trader import *
from mongo_lib import *
yf.pdr_override()
#********************************************************

# Class File

#********************************************************


class write_my_csv:
    def __init__(self, filename, header_list,new_flag=True):
        self.filename = filename
        if new_flag:
            with open(self.filename,"wb") as myfile:
                writer = csv.writer(myfile,delimiter=',')
                writer.writerows(header_list)
    
    def write_row(self,data_list_tuple):
        with open(self.filename,"ab") as myfile:
            writer = csv.writer(myfile,delimiter=',')
            writer.writerows(data_list_tuple)



def get_price_data(tic_list,method,interval = 1, freq = 'minutes',start_date = datetime.now()-timedelta(days =210),end_date=datetime.now()):
    
    def get_ondemand_data(sym, interval = 1,freq = 'minutes' ,start_date=(datetime.now()-timedelta(days=10))\
                    ,end_date=datetime.now()):

        try:

            api_key = 'b59b144a62e058b6c4e265c049dc679f'
            start_date=start_date.strftime("%Y%m%d%H%M%S")
            end_date=end_date.strftime("%Y%m%d%H%M%S")
            # This is the required format for datetimes to access the API

            api_url = 'http://marketdata.websol.barchart.com/getHistory.csv?' + \
                                    'key={}&symbol={}&type={}&startDate={}&endDate={}&interval={}'\
                                     .format(api_key, sym, freq, start_date,end_date,interval)

            csvfile = pd.read_csv(api_url, parse_dates=['timestamp'])
            csvfile.set_index('timestamp', inplace=True)

            return csvfile
                    
        except Exception as e:
            print e
    
    error = []
    price = pd.DataFrame()
    if method == "robinhood":
        robinhood = get_robinhood()
        
        for i in tic_list:
            trial = 0
            while trial <3:
                try:
                    temp = robinhood.get_historical(i,interval="10minute",span = "week")
                    #temp.index = temp.begins_at
                    temp = temp.drop(["session","interpolated"],axis=1)
                    for j in temp.columns[1:]:
                        temp[j] = temp[j].astype(float)
                   # index= pd.MultiIndex.from_product([[i],temp.index])
                    temp["Ticker"] = np.repeat(i,len(temp))
                    price = price.append(temp)

                    print "Finished", i 
                    #time.sleep(5)
                    trial=3

                except:
                    print "error occorded in getting yahool historicals for ", i
                    trial +=1
                    time.sleep(10)
                    if trial == 3:
                        error.append([i,'get_yahoo_historicals'])
        # get rid of the multiindex 
       # price.to_csv("file/temp.csv")
       # price = pd.read_csv("file/temp.csv")

        price = price.reset_index()
        price["Close"] = price["close_price"]
        price = price.rename(columns={'begins_at':"TimeStamp","high_price":"High","low_price":"Low","open_price":"Open","volume":"Volume"})
        price["Return"]= (price.Close.diff(1)/price.Close)


    elif method == "ondemand":


        #freq = minutes, daily
        save_file_name = "Trade_suggestion_ondemand"
        for i in tic_list:
            trial = 0
            while trial <3:
                try:
                    temp = get_ondemand_data(i, interval = interval , freq = freq,start_date = start_date, end_date = end_date)

                    #index= pd.MultiIndex.from_product([[i],temp.index])
                    #temp=pd.DataFrame(data=temp.values,index=index,columns=temp.columns)
                    
                    price = price.append(temp)

                    print "Finished", i 
                    #time.sleep(5)
                    trial=3
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
                except:
                    print "error occorded in getting yahool historicals for ", i
                    trial +=1
                    time.sleep(10)
                    if trial == 3:
                        error.append([i,'get_yahoo_historicals'])


        price = price.reset_index()
        price["Close"] = price["close"]
        price = price.rename(columns={'symbol':'Ticker','timestamp':"TimeStamp","high":"High","low":"Low","open":"Open","volume":"Volume"})
        price["Return"]=( price.Close.diff(1)/price.Close)
    
    elif method == "day":
        save_file_name = "Trade_suggestion_day"
        mongodb = mongo()
        for i in tic_list:
            trial = 0
            while trial <3:
                try:
                    temp = mongodb.query_database(i,start_date=start_date,end_date=end_date)
                    index= pd.MultiIndex.from_product([[i],temp.index])
                    temp=pd.DataFrame(data=temp.values,index=index,columns=temp.columns)
                    price = price.append(temp)
                    print "Finished", i
                    trial = 3
                except Exception as e:
                    try:
                        print (e)
                        print ("Switching from Mongodb to yahoo")
                        temp = da.DataReader(i,"yahoo",start_date ,end_date)
                        index= pd.MultiIndex.from_product([[i],temp.index])
                        temp=pd.DataFrame(data=temp.values,index=index,columns=temp.columns)
                        price = price.append(temp)

                        print "Finished", i 
                        #time.sleep(5)
                        trial=3
                        
                        
                    except Exception as e:
                        print "error occorded in getting yahool historicals for ", i
                        trial =3
                        trial +=1
                        time.sleep(10)
                    if trial == 3:
                        error.append([i,'get_yahoo_historicals'])
        # get rid of the multiindex 
    elif method == "realtimeday":
        save_file_name = "Trade_suggestion_day"
        mongodb = mongo()
        for i in tic_list:
            trial = 0
            while trial <3:
                try:
                    temp = da.DataReader(i,"yahoo",start_date ,end_date)
                    index= pd.MultiIndex.from_product([[i],temp.index])
                    temp=pd.DataFrame(data=temp.values,index=index,columns=temp.columns)
                    price = price.append(temp)
                    print "Finished", i
                    trial = 3
                except Exception as e:
                    try:
                        print (e)
                        print "Finished", i 
                        #time.sleep(5)
                        trial=3
                        print e
                        
                    except Exception as e:
                        print "error occorded in getting yahool historicals for ", i
                        trial =3
                        trial +=1
                        time.sleep(10)
                    if trial == 3:
                        error.append([i,'get_yahoo_historicals'])
        price = price.reset_index()

        
        price["Close"] = price["Adj Close"]
        price = price.rename(columns={'level_0':'Ticker','level_1':"TimeStamp"})
        price["Return"]= (price.Close.diff(1)/price.Close)
    #price = price.dropna()
    return price





class finviz:
    
    def get_finviz(self,symbol, data):
        try:
            base_url = 'http://finviz.com/quote.ashx?t={}'\
                .format(symbol.lower())
        
            html = r.get(base_url)
            soup = bs(html.content, "html.parser")
            main_div = soup.find('div', attrs = {'id':'screener-content'})
            pb =  soup.find(text = data)
            pb_ = pb.find_next(class_='snapshot-td2').text
            
            return pb_
        
        except:
            return np.NaN

    def get_finviz_sector(self,symbol):
        
        try:
            base_url = 'http://finviz.com/quote.ashx?t={}'\
            .format(symbol.lower())
            
            html = r.get(base_url)
            soup = bs(html.content, "html.parser")
            main_div = soup.find_all('td','fullview-links')
            sector = main_div[1].contents[0].text
            industry = main_div[1].contents[2].text
                
            return str(sector)
        except:
            return np.NaN

    def get_finviz_industry(self, symbol):
        try:
            base_url = 'http://finviz.com/quote.ashx?t={}'\
            .format(symbol.lower())
            
            html = r.get(base_url)
            soup = bs(html.content, "html.parser")
            main_div = soup.find_all('td','fullview-links')
            sector = main_div[1].contents[0].text
            industry = main_div[1].contents[2].text
                
            return str(industry)
        except:
            return np.NaN

    def get_marketcap(self,symbol):
        mkcap=self.get_finviz(symbol,"Market Cap")
        if type(mkcap) != unicode:
            return np.NaN
        else:
            if mkcap[-1]=="B":
                return float(mkcap[:-1])*1000000000
            elif mkcap[-1]=="M":
                return float(mkcap[:-1])*1000000
            else:
                return float(mkcap)


    def all_in_one(self, symbol):

        base_url = 'http://finviz.com/quote.ashx?t={}'\
            .format(symbol.lower())
            
        html = r.get(base_url)
        soup = bs(html.content, "html.parser")
        main_div = soup.find_all('td','fullview-links')
        sector = main_div[1].contents[0].text
        industry = main_div[1].contents[2].text
        
        def get_text(data, check = True):
            get = soup.find(text = data)
            #get = get.find_next(class_='snapshot-td2').text
            get = get.find_next().text
            if check:
                if  get =="-":
                    get = 0
                else:
                    if get[-1]=="B":
                        get = float(get[:-1])*1000000000
                    elif get[-1]=="M":
                        get = float(get[:-1])*1000000
                    elif get[-1] =="K":
                        get = float(get[:-1])*1000
                    elif get[-1]=="%":
                        get = float (get[:-1])*0.01
                    else:
                        get = float(get)
            return get
        
        def conver_cap (mkt_cap):
            if type(mkt_cap) != unicode or mkt_cap =="-":
                mkt_cap = np.NaN
            else:
                if mkt_cap[-1]=="B":
                    mkt_cap = float(mkt_cap[:-1])*1000000000
                elif mkt_cap[-1]=="M":
                    mkt_cap = float(mkt_cap[:-1])*1000000
                else:
                    mkt_cap = float(mkt_cap)
#
#
#        def conver_pet(data):
#            
#                return data
#            else:
#                return float (data[:-1])*0.01
#        
#        def none_result(data):
#            if data== "-":
#                data = 0
#                return data
            
        main_div = soup.find('div', attrs = {'id':'screener-content'})
#        mkt_cap =  soup.find(text = "Market Cap")
#        mkt_cap = mkt_cap.find_next(class_='snapshot-td2').text
#        mkt_cap = conver_cap(mkt_cap)
        mkt_cap = get_text("Market Cap")
        earning_date = soup.find(text = "Earnings")
        earning_date = earning_date.find_next(class_='snapshot-td2').text
        PEG = get_text("PEG")

#        P_E = soup.find(text = "P/E")
#        P_E = P_E.find_next(class_='snapshot-td2').text

        Profit_Margin = get_text("Profit Margin")
#        Profit_Margin = conver_pet(Profit_Margin)
        Avg_Volume = get_text("Avg Volume")
#        Avg_Volume = conver_cap(Avg_Volume)
        Current_Ratio = get_text("Current Ratio")
#        Current_Ratio = conver_pet(Current_Ratio)
        Inst_Own = get_text("Inst Own")
#        Inst_Own = conver_pet(Inst_Own)
        Beta = get_text("Beta")
#        if type(mkt_cap) != unicode:
#            mkt_cap = np.NaN
#        else:
#            if mkt_cap[-1]=="B":
#                mkt_cap = float(mkt_cap[:-1])*1000000000
#            elif mkt_cap[-1]=="M":
#                mkt_cap = float(mkt_cap[:-1])*1000000
#            else:
#                mkt_cap = float(mkt_cap)

        return str(industry), str(sector), mkt_cap,earning_date,\
                            float(PEG), Profit_Margin,\
                            Avg_Volume,\
                            float(Inst_Own),float(Beta), float(Current_Ratio)
                            
    

finviz = finviz()
        

#yahoo finance 




class yahoo_historicals:
    
        

    def get_historicals(self,stock, start,end):
    
        # download dataframe
        #start ="2017-01-01"
        #end="2017-04-30"
        data = pdr.get_data_yahoo(stock, start, end)

        return data

        






# def update_price():
#     tradeable = pd.read_csv("file/cantrade.csv")
#     tradeable = tradeable.dropna()

#     error = []


#     yahoo = yahoo_historicals()
#     start ="2017-10-1"
#     end=datetime.now()
#     price=pd.DataFrame()




#     for i in list(tradeable.Ticker):
#         trial = 0
#         while trial <3:
#             try:
#                 temp = da.DataReader(i,"yahoo",start,end)
#                 index= pd.MultiIndex.from_product([[i],temp.index])
#                 temp=pd.DataFrame(data=temp.values,index=index,columns=temp.columns)
#                 price = price.append(temp)

#                 print "Finished", i 
#                 #time.sleep(5)
#                 trial=3

#             except:
#                 print "error occorded in getting yahool historicals for ", i
#                 trial +=1
#                 if trial == 3:
#                     error.append([i,'get_yahoo_historicals'])
#     # get rid of the multiindex 
#     price = price.reset_index()

    
#     price.Close = price["Adj Close"]
#     price = price.rename(columns={'Unnamed: 0':'Ticker','Unnamed: 1':"TimeStamp"})
#     price["Return"]= price.Close.diff(1)/price.Close

#     '''
#     # make sure DataFrames are the same length

#     price_date = pd.DataFrame()

#     min_date = max(price.loc[price.Ticker==i].TimeStamp.iloc[0] for i in price.Ticker)
#     max_date = min(price.loc[price.Ticker==i].TimeStamp.iloc[-1] for i in price.Ticker)
#     print "2"
#     for i in price.Ticker:
#         price_date = price_date.append(price.loc[price.Ticker==i][(price.loc[price.Ticker==i].TimeStamp>= min_date) & (price.loc[price.Ticker==i].TimeStamp <= max_date)] )

#     price = price_date

#     print "done"

#     '''


#     industry_sector_earnings = pd.read_csv("file/my_universe_industry_sector_marketcap_earnings.csv")
#     #earnings = pd.read_csv("my_universe_earnings.csv")

#     industry_sector_earnings = industry_sector_earnings.dropna()  
        


#     for i in list(set(price.Ticker)):
        
#         #print price .loc[price.Ticker==i]

#         #price.groupby('Ticker').get_group(list(set(price.Ticker))[i])
#         #price.loc[price.Ticker==i,"ADX"]= ta.ADX(price.loc[price.Ticker==i].High.values, price.loc[price.Ticker==i].Low.values, price.loc[price.Ticker==i].Close.values, timeperiod=14)
#         price.loc[price.Ticker==i,"ADXR"]= ta.ADXR(price.loc[price.Ticker==i].High.values, price.loc[price.Ticker==i].Low.values, price.loc[price.Ticker==i].Close.values, timeperiod=14)
#         price.loc[price.Ticker==i,"APO"]= ta.APO(price.loc[price.Ticker==i].Close.values, fastperiod=12, slowperiod=26, matype=0)
#         price.loc[price.Ticker==i,"AROONOSC"]= ta.AROONOSC(price.loc[price.Ticker==i].High.values,price.loc[price.Ticker==i].Close.values, timeperiod=14)
#         price.loc[price.Ticker==i,"CCI"]= ta.CCI(price.loc[price.Ticker==i].High.values,price.loc[price.Ticker==i].Low.values,price.loc[price.Ticker==i].Close.values, timeperiod=14)
#         price.loc[price.Ticker==i,"MFI"]= ta.MFI(price.loc[price.Ticker==i].High.values, price.loc[price.Ticker==i].Low.values, price.loc[price.Ticker==i].Close.values, price.loc[price.Ticker==i].loc[price.Ticker==i].Volume.values.astype(float),timeperiod=14)
#         price.loc[price.Ticker==i,"MACD"], price.loc[price.Ticker==i,"MACD_signal"], price.loc[price.Ticker==i,"MACD_hist"] = ta.MACD(price.loc[price.Ticker==i].Close.values, fastperiod=12, slowperiod=26, signalperiod=9)
#         price.loc[price.Ticker==i,"ROCP"]= ta.ROCP(price.loc[price.Ticker==i].Close.values, timeperiod=10)
#         #price.loc[price.Ticker==i,"ROCR100"]= ta.ROCR100(price.loc[price.Ticker==i].Close.values, timeperiod=10)
#         price.loc[price.Ticker==i,"RSI"]= ta.RSI(price.loc[price.Ticker==i].Close.values, timeperiod=14)

#         print "\nDone:", i



#     final_update = pd.DataFrame()

#     for i in list(set(price.Ticker)):

#         final_update = final_update.append(price.loc[price.Ticker==i].iloc[-1])


#     final_update["Industry"] = np.NaN
#     final_update["Sector"] = np.NaN
#     final_update["Earnings_date"] = np.NaN
#     final_update["Market_cap"] = np.NaN
#     final_update["Industry_weight"] = np.NaN

    # for i in list(set(final_update.Ticker)):
    #     try:
    #         final_update.loc[final_update.Ticker==i,"Industry"] = industry_sector_earnings.loc[industry_sector_earnings.Ticker == i, "Industry"].values[0]
    #     except:
            
    #         print "nan occorded"

    # for i in list(set(final_update.Ticker)):    
    #     try:
    #         final_update.loc[final_update.Ticker==i,"Sector"] = industry_sector_earnings.loc[industry_sector_earnings.Ticker == i, "Sector"].values[0]
    #     except:
            
    #         print "nan occorded"
    # for i in list(set(final_update.Ticker)):    
    #     try:
    #         final_update.loc[final_update.Ticker==i,"Earnings_date"] = industry_sector_earnings.loc[industry_sector_earnings.Ticker == i, "Earnings_date"].values[0] 
    #     except:
            
    #         print "nan occorded"

    # for i in list(set(final_update.Ticker)):    
    #     try:
    #         final_update.loc[final_update.Ticker==i,"Market_cap"] = industry_sector_earnings.loc[industry_sector_earnings.Ticker == i, "Market_cap"].values[0] 
    #     except:
            
    #         print "nan occorded"



#     #final_update.to_csv("final"+str(price.loc[price.Ticker==i][-1]["Date"])+".csv")


#     #get industrial makcap_weight

#     for ind in set(final_update.Industry):
#         for tic in set(final_update.loc[final_update.Industry==ind].Ticker):
#             final_update.loc[final_update.Ticker==tic,'Industry_weight']=final_update.loc[final_update.Ticker==tic,"Market_cap"] / final_update.loc[final_update.Industry==ind,"Market_cap"].sum()


#     #final_update = final_update[['Ticker','TimeStamp', 'Open', 'High', 'Low', 'Close', 'Volume',
#     #        'Return','ADXR','AROONOSC','APO','CCI','MACD', 'MACD_hist',
#     #       'MACD_signal','MFI','ROCP','RSI','Industry','Sector']]
#     final_update = final_update[['Ticker','TimeStamp', 'Open', 'High', 'Low', 'Close', 'Volume',
#             'Return','ADXR','AROONOSC','APO','CCI','MACD', 'MACD_hist',
#            'MACD_signal','MFI','ROCP','RSI','Industry','Sector','Market_cap','Industry_weight','Earnings_date']]

#     final_update =final_update.set_index("Ticker")

#     #final_update= final_update.dropna()




#     # Technical points rule

#     final_update["Technical_points"]=0
#     for i in final_update.index:
#         if final_update.loc[i].ADXR >= final_update.loc[final_update.Sector==final_update.loc[i].Sector].max().ADXR:
#             final_update.loc[i,'Technical_points'] += 1
#         if final_update.loc[i].APO >0:
#             final_update.loc[i,'Technical_points'] += 1
#         if final_update.loc[i].AROONOSC >= final_update.loc[final_update.Sector==final_update.loc[i].Sector].max().AROONOSC:
#             final_update.loc[i,'Technical_points'] += 1
#         if final_update.loc[i].CCI <-100:
#             final_update.loc[i,'Technical_points'] += 1
#         if final_update.loc[i].MACD > final_update.loc[i].MACD_signal:
#             final_update.loc[i,'Technical_points'] += 1
#         if final_update.loc[i].MFI <20:
#             final_update.loc[i,'Technical_points'] += 1
#         if final_update.loc[i].ROCP >0:
#             final_update.loc[i,'Technical_points'] += 1

#         print "Technical_points done: ", i
#     final_update= final_update.dropna()

#     final_update.to_csv("file/final_update.csv")
#     #***************************************

#     # get result

#     #***************************************

#     result = pd.DataFrame()
#     for i in set(final_update.Sector):
#         print i
#         print final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-1].name
#         result = result.append(final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-1])

#     result.to_csv("file/Trade_suggestion_1st" + str(result.TimeStamp[0])+".csv")

#     result = pd.DataFrame()
#     for i in set(final_update.Sector):
#         print i
#         print final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-2].name
#         result = result.append(final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-2])

#     result.to_csv("file/Trade_suggestion_2nd" + str(result.TimeStamp[0])+".csv")

#     result = pd.DataFrame()
#     for i in set(final_update.Sector):
#         print i
#         print final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-2].name
#         result = result.append(final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-2])

#     result.to_csv("file/Trade_suggestion_3rd" + str(result.TimeStamp[0])+".csv")
#     #"file/Trade_suggestion_minute_1st" + str(datetime.now())[0:10]+".csv"


#################################################################

def update_price(method = "robinhood",test = False, interval = 1, freq = 'minutes',start_date = datetime.now()-timedelta(days =90),end_date=datetime.now(),save_file = True):
    tradeable = pd.read_csv(directory + universe_file_name)
    
# =============================================================================
    #select universe 
    tradeable["volume_rank"] = tradeable["Avg_Volume"].rank(ascending = False)
    tradeable = tradeable.loc[tradeable["volume_rank"]<=1000]     
# =============================================================================
    
    tradeable = tradeable.dropna()
    robinhood = get_robinhood()
    error = []

    if test:
    	test = ""
    	print "Test mode is on!!"
        #save_file = False
    	tic_list = tradeable.Ticker[0:50]
    else:
    	test = ""
    	tic_list = tradeable.Ticker
    price=pd.DataFrame()

    


########################################################################################################
#Data Collection Method

    if method == "robinhood":
    	save_file_name = "Trade_suggestion_robinhood"
        for i in tic_list:
            trial = 0
            while trial <3:
                try:
                    temp = robinhood.get_historical(i,interval="10minute",span = "week")
                    #temp.index = temp.begins_at
                    temp = temp.drop(["session","interpolated"],axis=1)
                    for j in temp.columns[1:]:
                        temp[j] = temp[j].astype(float)
                   # index= pd.MultiIndex.from_product([[i],temp.index])
                    temp["Ticker"] = np.repeat(i,len(temp))
                    price = price.append(temp)

                    print "Finished", i 
                    #time.sleep(5)
                    trial=3

                except:
                    print "error occorded in getting yahool historicals for ", i
                    trial +=1
                    if trial == 3:
                        error.append([i,'get_yahoo_historicals'])
        # get rid of the multiindex 
       # price.to_csv("file/temp.csv")
       # price = pd.read_csv("file/temp.csv")

        price = price.reset_index()
        price["Close"] = price["close_price"]
        price = price.rename(columns={'begins_at':"TimeStamp","high_price":"High","low_price":"Low","open_price":"Open","volume":"Volume"})
        price["Return"]= price.Close.diff(1)/price.Close

    elif method == "ondemand":
        #freq = minutes, daily
    	save_file_name = "Trade_suggestion_ondemand"
        for i in tic_list:
            trial = 0
            while trial <3:
                try:
                    temp = get_ondemand_data(i, interval = interval , freq = freq,start_date = start_date, end_date = end_date)

                    #index= pd.MultiIndex.from_product([[i],temp.index])
                    #temp=pd.DataFrame(data=temp.values,index=index,columns=temp.columns)
                    
                    price = price.append(temp)

                    print "Finished", i 
                    #time.sleep(5)
                    trial=3

                except:
                    print "error occorded in getting yahool historicals for ", i
                    trial +=1
                    if trial == 3:
                        error.append([i,'get_yahoo_historicals'])


        price = price.reset_index()
        price["Close"] = price["close"]
        price = price.rename(columns={'symbol':'Ticker','timestamp':"TimeStamp","high":"High","low":"Low","open":"Open","volume":"Volume"})
        price["Return"]= price.Close.diff(1)/price.Close
    
    elif method == "day":
    	save_file_name = "Trade_suggestion_day"
        for i in tic_list:
            trial = 0
            while trial <3:
                try:
                    temp = da.DataReader(i,"yahoo",start_date ,end_date)
                    index= pd.MultiIndex.from_product([[i],temp.index])
                    temp=pd.DataFrame(data=temp.values,index=index,columns=temp.columns)
                    price = price.append(temp)

                    print "Finished", i 
                    #time.sleep(5)
                    trial=3

                except Exception as e:
                    print e
                    print "error occorded in getting yahool historicals for ", i
                    trial +=1
                    if trial == 3:
                        error.append([i,'get_yahoo_historicals'])
        # get rid of the multiindex 
        price = price.reset_index()

        
        price.Close = price["Adj Close"]
        price = price.rename(columns={'level_0':'Ticker','level_1':"TimeStamp"})
        price["Return"]= price.Close.diff(1)/price.Close

    # make sure DataFrames are the same length

    # price_date = pd.DataFrame()

    # min_date = max(price.loc[price.Ticker==i].TimeStamp.iloc[0] for i in price.Ticker)
    # max_date = min(price.loc[price.Ticker==i].TimeStamp.iloc[-1] for i in price.Ticker)
    # print "2"
    # for i in price.Ticker:
    #     price_date = price_date.append(price.loc[price.Ticker==i][(price.loc[price.Ticker==i].TimeStamp>= min_date) & (price.loc[price.Ticker==i].TimeStamp <= max_date)] )

    # price = price_date

    # print "done"

    
########################################################################################################

    industry_sector_earnings = pd.read_csv("file/my_universe_industry_sector_marketcap_earnings.csv")
    #earnings = pd.read_csv("my_universe_earnings.csv")

    industry_sector_earnings = industry_sector_earnings.dropna()  
        


    for i in list(set(price.Ticker)):
        
        #print price .loc[price.Ticker==i]

        #price.groupby('Ticker').get_group(list(set(price.Ticker))[i])
        #price.loc[price.Ticker==i,"ADX"]= ta.ADX(price.loc[price.Ticker==i].High.values, price.loc[price.Ticker==i].Low.values, price.loc[price.Ticker==i].Close.values, timeperiod=14)
        price.loc[price.Ticker==i,"ADXR"]= ta.ADXR(price.loc[price.Ticker==i].High.values, price.loc[price.Ticker==i].Low.values, price.loc[price.Ticker==i].Close.values, timeperiod=14)
        price.loc[price.Ticker==i,"APO"]= ta.APO(price.loc[price.Ticker==i].Close.values, fastperiod=12, slowperiod=26, matype=0)
        price.loc[price.Ticker==i,"AROONOSC"]= ta.AROONOSC(price.loc[price.Ticker==i].High.values,price.loc[price.Ticker==i].Close.values, timeperiod=14)
        price.loc[price.Ticker==i,"CCI"]= ta.CCI(price.loc[price.Ticker==i].High.values,price.loc[price.Ticker==i].Low.values,price.loc[price.Ticker==i].Close.values, timeperiod=14)
        price.loc[price.Ticker==i,"MFI"]= ta.MFI(price.loc[price.Ticker==i].High.values, price.loc[price.Ticker==i].Low.values, price.loc[price.Ticker==i].Close.values, price.loc[price.Ticker==i].loc[price.Ticker==i].Volume.values.astype(float),timeperiod=14)
        price.loc[price.Ticker==i,"MACD"], price.loc[price.Ticker==i,"MACD_signal"], price.loc[price.Ticker==i,"MACD_hist"] = ta.MACD(price.loc[price.Ticker==i].Close.values, fastperiod=12, slowperiod=26, signalperiod=9)
        price.loc[price.Ticker==i,"ROCP"]= ta.ROCP(price.loc[price.Ticker==i].Close.values, timeperiod=10)
        #price.loc[price.Ticker==i,"ROCR100"]= ta.ROCR100(price.loc[price.Ticker==i].Close.values, timeperiod=10)
        price.loc[price.Ticker==i,"RSI"]= ta.RSI(price.loc[price.Ticker==i].Close.values, timeperiod=14)
        price.loc[price.Ticker==i,"MA_fast"] = price.Close.rolling(10).mean()
        price.loc[price.Ticker==i,"MA_slow"] = price.Close.rolling(30).mean()

        print "\nDone:", i



    final_update = pd.DataFrame()

    for i in list(set(price.Ticker)):

        final_update = final_update.append(price.loc[price.Ticker==i].iloc[-1])


    final_update["Industry"] = np.NaN
    final_update["Sector"] = np.NaN
    final_update["Earnings_date"] = np.NaN
    final_update["Market_cap"] = np.NaN
    final_update["Industry_weight"] = np.NaN
    
    for i in list(set(final_update.Ticker)):
        try:
            final_update.loc[final_update.Ticker==i,"Industry"] = industry_sector_earnings.loc[industry_sector_earnings.Ticker == i, "Industry"].values[0]
            final_update.loc[final_update.Ticker==i,"Sector"] = industry_sector_earnings.loc[industry_sector_earnings.Ticker == i, "Sector"].values[0]
            final_update.loc[final_update.Ticker==i,"Earnings_date"] = industry_sector_earnings.loc[industry_sector_earnings.Ticker == i, "Earnings_date"].values[0]
            final_update.loc[final_update.Ticker==i,"Market_cap"] = industry_sector_earnings.loc[industry_sector_earnings.Ticker == i, "Market_cap"].values[0]
        except:
                
            print "nan occorded"



    #final_update.to_csv("final"+str(price.loc[price.Ticker==i][-1]["Date"])+".csv")


    #get industrial makcap_weight

    for ind in set(final_update.Industry):
        for tic in set(final_update.loc[final_update.Industry==ind].Ticker):
            final_update.loc[final_update.Ticker==tic,'Industry_weight']=final_update.loc[final_update.Ticker==tic,"Market_cap"] / final_update.loc[final_update.Industry==ind,"Market_cap"].sum()


    #final_update = final_update[['Ticker','TimeStamp', 'Open', 'High', 'Low', 'Close', 'Volume',
    #        'Return','ADXR','AROONOSC','APO','CCI','MACD', 'MACD_hist',
    #       'MACD_signal','MFI','ROCP','RSI','Industry','Sector']]
    final_update = final_update[['Ticker','TimeStamp', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Return','ADXR','AROONOSC','APO','CCI','MACD', 'MACD_hist',
           'MACD_signal','MFI','ROCP','RSI','Industry','Sector','Market_cap','Industry_weight','Earnings_date']]


    
    final_update =final_update.set_index("Ticker")

    #final_update= final_update.dropna()




    # Technical points rule

    final_update["Technical_points"]=0
    for i in final_update.index:
        if final_update.loc[i].ADXR >= final_update.loc[final_update.Sector==final_update.loc[i].Sector].max().ADXR:
            final_update.loc[i,'Technical_points'] += 1
        if final_update.loc[i].APO >0:
            final_update.loc[i,'Technical_points'] += 1
        if final_update.loc[i].AROONOSC >= final_update.loc[final_update.Sector==final_update.loc[i].Sector].max().AROONOSC:
            final_update.loc[i,'Technical_points'] += 1
        if final_update.loc[i].CCI <-100:
            final_update.loc[i,'Technical_points'] += 1
        if final_update.loc[i].MACD > final_update.loc[i].MACD_signal:
            final_update.loc[i,'Technical_points'] += 1
        if final_update.loc[i].MFI <20:
            final_update.loc[i,'Technical_points'] += 1
        if final_update.loc[i].ROCP >0:
            final_update.loc[i,'Technical_points'] += 1

        print "Technical_points done: ", i
    final_update= final_update.dropna()
    if save_file:
        final_update.to_csv(directory + save_file_name)

    #***************************************

    # get result

    #***************************************

    result = final_update.sort_values("Technical_points").iloc[-3:]
    result.to_csv( directory + save_file_name + "_1st"  +test + str(result.TimeStamp[0])[0:10].replace(":","-")+".csv")
    

#FOLLOWING IS BY SECTORS

#    result = pd.DataFrame()
#    for i in set(final_update.Sector):
#        try:
#            print i
#            print final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-1].name
#            result = result.append(final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-1])
#        
#        except Exception as e:
#            result = result.append(pd.Series(([np.NaN])),ignore_index=True)
#            print e," no 1st suggestion", i
#            raise
#    if save_file:
#        result.to_csv( directory + save_file_name + "_1st"  +test + str(result.TimeStamp[0])[0:10].replace(":","-")+".csv")
#    
#    result_1 = result
#
#    result = pd.DataFrame(columns = result.columns)
#    for i in set(final_update.Sector):
#        try:
#            print i
#            print final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-2].name
#            result = result.append(final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-2])
#        except Exception as e:
#            print e," no 2nd suggestion", i
#            result = result.append(pd.Series(pd.Series([np.NaN])),ignore_index=True)
#            pass
#    if save_file:
#        result.to_csv(directory + save_file_name + "_2nd" +test+ str(result.TimeStamp[0])[0:10].replace(":","-")+".csv")
#
#
#    result_2 = result
#
#    result = pd.DataFrame(columns = result.columns)
#    for i in set(final_update.Sector):
#        try:
#            print i
#            print final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-3].name
#            result = result.append(final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-3])
#        except Exception as e:
#            print e," no 3rd suggestion, ", i
#            result = result.append(pd.Series([np.NaN]),ignore_index=True)
#            pass
#    if save_file:
#        result.to_csv(directory + save_file_name + "_3rd" +test+ str(result.TimeStamp[0])[0:10]+".csv")
#
#    result_3 = result
#
#    return result_1, result_2,result_3


#################################################################




#################################################################

def update_fundamentals(my_list = False, test_mode=False,skip_can=False):
    error=[]
    if not skip_can:
        robinhood=get_robinhood()
        #test.login()
        if type(my_list) ==bool:
            if test_mode:
                universe = robinhood.get_universe()[1:10]
            else:   
                universe = robinhood.get_universe()
        else:
            universe = my_list
        stock = list();
    
    
    
        print "checking robinhood cantrade\n"
       
        tradeable = universe.loc[list(robinhood.istradeable(str(universe.iloc[i]))[0] for i in range(len(universe.index)) )]
    
        tradeable = DataFrame(tradeable,columns=['Ticker'])
    
        tradeable["Price"]=np.NaN
    
        for i in tradeable.Ticker:
            try:
                tradeable.loc[tradeable.Ticker == i,"Price"]= robinhood.get_last_price(i)
            except Exception as e:
                print e
                continue
        
        tradeable = tradeable.loc[tradeable.Price >7.00]
    
        #get stock volumn
        tradeable = tradeable.reset_index()
#        tradeable["Volume"]= np.NaN
#        robinhood = get_robinhood()
#        for i in tradeable.Ticker:
#            try:
#                tradeable.loc[tradeable.Ticker==i,"Volume"] = float(robinhood.my_trader.fundamentals(i)["volume"])
#            except:
#                tradeable.drop(tradeable.Ticker ==i)
#                print "Drop", i
#                continue
        tradeable = tradeable.dropna()
        
        tradeable.to_csv('file/cantrade.csv')
        tradeable.to_csv("file/cantrade_update.csv")
    
        #select top 1000 volume
#        tradeable["Rank"]=tradeable.Volume.rank(ascending=False)
#        tradeable_2 = tradeable.loc[tradeable.Rank <=1000]
#        tradeable_2.to_csv("file/cantrade_1000.csv")
#    
#        tradeable_2 = tradeable.loc[tradeable.Rank <= 2000]
#        tradeable_2.to_csv("file/cantrade_2000.csv")
    
        print "cantrade done!\n"


    start = timeit.default_timer()
    if  type(my_list) ==bool:
        tradeable = pd.read_csv(directory +"cantrade.csv")
    else:
        tradeable = pd.DataFrame(my_list,columns=["Ticker"])
#        tradeable = tradeable.rename(columns={"0":"Ticker"})
        
    tradeable['Industry']=np.NaN
    tradeable['Sector']=np.NaN
    tradeable['Market_cap']=np.NaN
    tradeable['Earnings_date']=np.NaN
    tradeable["PEG"]=np.NaN
    tradeable["Avg_Volume"]=np.NaN
    tradeable["Current_Ratio"]=np.NaN
    tradeable["Inst_Own"]=np.NaN
    tradeable["Beta"]=np.NaN
    tradeable["Current_ratio"]=np.NaN
#
#Avg_Volume = get_text("Avg Volume")
#        Current_Ratio = get_text("Current Ratio")
#        Inst_Own = get_text("Inst Own")
#        Beta = get_text("Beta")

    for i in range(len(tradeable.index)):
        try:
            tradeable['Industry'].iloc[i],\
            tradeable['Sector'].iloc[i],\
            tradeable['Market_cap'].iloc[i],\
            tradeable['Earnings_date'].iloc[i],\
            tradeable["PEG"].iloc[i],\
            tradeable["Profit_Margin"].iloc[i],\
            tradeable["Volume"].iloc[i],\
            tradeable["In"].iloc[i],\
            tradeable["Inst_Own"].iloc[i],\
            tradeable["Beta"].iloc[i],\
            tradeable["Current_ratio"].iloc[i]\
            =finviz.all_in_one(tradeable['Ticker'].iloc[i])
            
            print "get done! ", tradeable['Ticker'].iloc[i]
            if i % 8 == 0 and i != 0:
                time.sleep(20)
        except Exception as e:
            if test_mode:
                raise
            print "get error ", tradeable['Ticker'].iloc[i]
            print e
            error.append([tradeable['Ticker'].iloc[i],'get_S_I_M_E'])

    error = pd.DataFrame(error)
    if  type(my_list) == "bool":
        tradeable.to_csv(directory + "from_error_my_universe_industry_sector_marketcap_earnings.csv")
        error.to_csv(directory + "from_error.csv")
    else:
        tradeable.to_csv(directory + "my_universe_industry_sector_marketcap_earnings.csv")
        error.to_csv(directory + "error.csv")

    stop = timeit.default_timer()

    runtime = stop - start
    print  runtime


#################################################################




#################################################################



# def update_price_ondemand(interval = 1, freq = 'minutes',start_date = datetime.now()-timedelta(days =10),end_date=datetime.now()):
#     tradeable = pd.read_csv(directory+universe_file_name)
#     tradeable = tradeable.dropna()
#     robinhood = get_robinhood()
#     error = []


#     price=pd.DataFrame()


#     for i in list(tradeable.Ticker)[0:2]:
#         trial = 0
#         while trial <3:
#             try:
#                 temp = get_ondemand_data(i, interval = interval , freq = freq,start_date = start_date, end_date = end_date)

#                 #index= pd.MultiIndex.from_product([[i],temp.index])
#                 #temp=pd.DataFrame(data=temp.values,index=index,columns=temp.columns)
                
#                 price = price.append(temp)

#                 print "Finished", i 
#                 #time.sleep(5)
#                 trial=3

#             except:
#                 print "error occorded in getting yahool historicals for ", i
#                 trial +=1
#                 if trial == 3:
#                     error.append([i,'get_yahoo_historicals'])
#     # get rid of the multiindex 
#    # price.to_csv("file/temp.csv")
#     #price = pd.read_csv("file/temp.csv")

#     price = price.reset_index()
#     price["Close"] = price["close"]
#     price = price.rename(columns={'symbol':'Ticker','timestamp':"TimeStamp","high":"High","low":"Low","open":"Open","volume":"Volume"})
#     price["Return"]= price.Close.diff(1)/price.Close



#     industry_sector_earnings = pd.read_csv("file/my_universe_industry_sector_marketcap_earnings.csv")
#     #earnings = pd.read_csv("my_universe_earnings.csv")

#     industry_sector_earnings = industry_sector_earnings.dropna()  
        


#     for i in list(set(price.Ticker)):
        
#         #print price .loc[price.Ticker==i]

#         #price.groupby('Ticker').get_group(list(set(price.Ticker))[i])
#         #price.loc[price.Ticker==i,"ADX"]= ta.ADX(price.loc[price.Ticker==i].High.values, price.loc[price.Ticker==i].Low.values, price.loc[price.Ticker==i].Close.values, timeperiod=14)
#         price.loc[price.Ticker==i,"ADXR"]= ta.ADXR(price.loc[price.Ticker==i].High.values, price.loc[price.Ticker==i].Low.values, price.loc[price.Ticker==i].Close.values, timeperiod=14)
#         price.loc[price.Ticker==i,"APO"]= ta.APO(price.loc[price.Ticker==i].Close.values, fastperiod=12, slowperiod=26, matype=0)
#         price.loc[price.Ticker==i,"AROONOSC"]= ta.AROONOSC(price.loc[price.Ticker==i].High.values,price.loc[price.Ticker==i].Close.values, timeperiod=14)
#         price.loc[price.Ticker==i,"CCI"]= ta.CCI(price.loc[price.Ticker==i].High.values,price.loc[price.Ticker==i].Low.values,price.loc[price.Ticker==i].Close.values, timeperiod=14)
#         price.loc[price.Ticker==i,"MFI"]= ta.MFI(price.loc[price.Ticker==i].High.values, price.loc[price.Ticker==i].Low.values, price.loc[price.Ticker==i].Close.values, price.loc[price.Ticker==i].loc[price.Ticker==i].Volume.values.astype(float),timeperiod=14)
#         price.loc[price.Ticker==i,"MACD"], price.loc[price.Ticker==i,"MACD_signal"], price.loc[price.Ticker==i,"MACD_hist"] = ta.MACD(price.loc[price.Ticker==i].Close.values, fastperiod=12, slowperiod=26, signalperiod=9)
#         price.loc[price.Ticker==i,"ROCP"]= ta.ROCP(price.loc[price.Ticker==i].Close.values, timeperiod=10)
#         #price.loc[price.Ticker==i,"ROCR100"]= ta.ROCR100(price.loc[price.Ticker==i].Close.values, timeperiod=10)
#         price.loc[price.Ticker==i,"RSI"]= ta.RSI(price.loc[price.Ticker==i].Close.values, timeperiod=14)

#         print "\nDone:", i



#     final_update = pd.DataFrame()

#     for i in list(set(price.Ticker)):

#         final_update = final_update.append(price.loc[price.Ticker==i].iloc[-1])


#     final_update["Industry"] = np.NaN
#     final_update["Sector"] = np.NaN
#     final_update["Earnings_date"] = np.NaN
#     final_update["Market_cap"] = np.NaN
#     final_update["Industry_weight"] = np.NaN

#     for i in list(set(final_update.Ticker)):
#         try:
#             final_update.loc[final_update.Ticker==i,"Industry"] = industry_sector_earnings.loc[industry_sector_earnings.Ticker == i, "Industry"].values[0]
#             final_update.loc[final_update.Ticker==i,"Sector"] = industry_sector_earnings.loc[industry_sector_earnings.Ticker == i, "Sector"].values[0]
#             final_update.loc[final_update.Ticker==i,"Earnings_date"] = industry_sector_earnings.loc[industry_sector_earnings.Ticker == i, "Earnings_date"].values[0]
#             final_update.loc[final_update.Ticker==i,"Market_cap"] = industry_sector_earnings.loc[industry_sector_earnings.Ticker == i, "Market_cap"].values[0]
#         except:
            
#             print "nan occorded"

   



#     #final_update.to_csv("final"+str(price.loc[price.Ticker==i][-1]["Date"])+".csv")


#     #get industrial makcap_weight

#     for ind in set(final_update.Industry):
#         for tic in set(final_update.loc[final_update.Industry==ind].Ticker):
#             final_update.loc[final_update.Ticker==tic,'Industry_weight']=final_update.loc[final_update.Ticker==tic,"Market_cap"] / final_update.loc[final_update.Industry==ind,"Market_cap"].sum()


#     #final_update = final_update[['Ticker','TimeStamp', 'Open', 'High', 'Low', 'Close', 'Volume',
#     #        'Return','ADXR','AROONOSC','APO','CCI','MACD', 'MACD_hist',
#     #       'MACD_signal','MFI','ROCP','RSI','Industry','Sector']]
#     # final_update = final_update[['Ticker','TimeStamp', 'Open', 'High', 'Low', 'Close', 'Volume',
#     #         'Return','ADXR','AROONOSC','APO','CCI','MACD', 'MACD_hist',
#     #        'MACD_signal','MFI','ROCP','RSI','Industry','Sector','Market_cap','Industry_weight','Earnings_date']]

#     final_update =final_update.set_index("Ticker")

#     #final_update= final_update.dropna()




#     # Technical points rule

#     final_update["Technical_points"]=0
#     for i in final_update.index:
#         if final_update.loc[i].ADXR >= final_update.loc[final_update.Sector==final_update.loc[i].Sector].max().ADXR:
#             final_update.loc[i,'Technical_points'] += 1
#         if final_update.loc[i].APO >0:
#             final_update.loc[i,'Technical_points'] += 1
#         if final_update.loc[i].AROONOSC >= final_update.loc[final_update.Sector==final_update.loc[i].Sector].max().AROONOSC:
#             final_update.loc[i,'Technical_points'] += 1
#         if final_update.loc[i].CCI <-100:
#             final_update.loc[i,'Technical_points'] += 1
#         if final_update.loc[i].MACD > final_update.loc[i].MACD_signal:
#             final_update.loc[i,'Technical_points'] += 1
#         if final_update.loc[i].MFI <20:
#             final_update.loc[i,'Technical_points'] += 1
#         if final_update.loc[i].ROCP >0:
#             final_update.loc[i,'Technical_points'] += 1

#         print "Technical_points done: ", i
#     final_update= final_update.dropna()

#     final_update.to_csv("file/final_update_minute.csv")
#     #***************************************

#     # get result

#     #***************************************

#     result = pd.DataFrame()
#     for i in set(final_update.Sector):
#         print i
#         print final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-1].name
#         result = result.append(final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-1])

#     result.to_csv("file/Trade_suggestion_minute_1st" + str(datetime.now())[0:10]+".csv")

#     # result = pd.DataFrame()
#     # for i in set(final_update.Sector):
#     #     print i
#     #     print final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-2].name
#     #     result = result.append(final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-2])

#     # result.to_csv("file/Trade_suggestion_minute_2nd" + str(result.TimeStamp[0]).replace(":","-")+".csv")

#     # result = pd.DataFrame()
#     # for i in set(final_update.Sector):
#     #     print i
#     #     print final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-3].name
#     #     result = result.append(final_update.groupby("Sector").get_group(i).sort_values("Technical_points").iloc[-3])

#     # result.to_csv("file/Trade_suggestion_minute_3rd" + str(result.TimeStamp[0]).replace(":","-")+".csv")

#     return result







# =============================================================================
# def mean_reversion(stock,ival):
# 
#     result = []
# 
#     #***************************************
# 
#     # load price data
# 
#     #***************************************
#     start ="2017-01-01"
#     end=datetime.now()
# 
#     if ival == "day":
#         st_price = da.DataReader(stock,"yahoo",start,end)
#         st_price = st_price.dropna()
#         usr_input = st_price["Adj Close"]
# 
#     elif ival == "minute":
#         robinhood = get_robinhood()
# 
#     # use robinhood data for 10 minute interval
#         st_price = robinhood.get_historical(stock,interval="10minute",span="week")
#         usr_input = st_price.close_price.astype("float")
#     else:
#         raise "interval not support yet"
# 
# 
# 
#     #***************************************
# 
#     #Augmented Dickey Fuller test
# 
#     #***************************************
# 
# 
#     
# 
#     cadf = ts.adfuller(usr_input)
#     print 'Augmented Dickey Fuller test statistic =',cadf[0]
#     print 'Augmented Dickey Fuller p-value =',cadf[1]
#     print 'Augmented Dickey Fuller 1%, 5% and 10% test statistics =',cadf[4]
# 
#     #cadf[4]['1%'] get 1% statistic value
#     print ('''
#     p value should < 0.05
# 
#     ADF test statistic is larger than the benchmark in absolute value means we can reject 
#     the null hypothesis that there is a unit root in the  time series, 
#     and is therefore not mean reverting. We should look for a smaller value than benchmark to 
#     keep the null hypothesis to confirm mean-reverting
# 
#     ''')
#     
# 
# 
#     if cadf[1] < 0.05 and (abs(cadf[0]) < abs(cadf[4]['1%']) or abs(cadf[0]) < abs(cadf[4]['10%']) or abs(cadf[0]) < abs(cadf[4]['5%'])):
# 
#         cadf_interpret = True
#     else:
#         cadf_interpret = False
# 
#     result.append(cadf_interpret)
# 
#     #***************************************
# 
#     # Calculate Hurst Exponent
# 
#     #***************************************
# 
# 
#     """Returns the Hurst Exponent of the time series vector ts"""
#     # Create the range of lag values
#     lags = range(2, 100)
# 
# 
#     # Calculate the array of the variances of the lagged differences
#     tau = [sqrt(np.std(np.subtract(usr_input[lag:], usr_input[:-lag]))) for lag in lags]
#      
#     # Use a linear fit to estimate the Hurst Exponent
#     lags = [log(i) for i in lags]
#     tau = [log(i) for i in tau]
#     poly = np.polyfit(lags,tau , 1)
#      
#     # Return the Hurst exponent from the polyfit output
# 
# 
#     # print the result
#     print "Hurst Exponent =",round(poly[0]*2.0,2)
# 
#     if round(poly[0]*2.0,2)< 0.5:
#         result.append("mean reverting")
#     elif round(poly[0]*2.0,2)>0.5:
#         result.append("trending")
#     else:
#         result.append("Geometric Brownian Motion ")
# 
#     #result.append(np.where(round(poly[0]*2.0,2)<0.5,"mean reverting","trending"))
# 
#     
#     #H < 0.5  The time series is mean reverting 
#     #H = 0.5  The time series is a Geometric Brownian Motion 
#     #H > 0.5  The time series is trending
#     
# 
# 
# 
#     #***************************************
# 
#     # Calculate Half life
# 
#     #***************************************
# 
# 
#     #Run OLS regression on spread series and lagged version of itself
# 
#     df1 = usr_input
# 
#     lag = df1.shift(1)
#     lag.iloc[0] = lag.iloc[1]
#     ret = df1 - lag
#     ret.iloc[0] = ret.iloc[1]
#     lag2 = sm.add_constant(lag)
#      
#     model = sm.OLS(ret,lag2)
#     res = model.fit()
#      
#      
#     halflife = round(-np.log(2) / res.params[1],0)
#      
#     print  'Halflife = ', halflife
# 
#     result.append(halflife)
# 
#     if result[0] and result[1] == "mean reverting" and reverting[2]<30:
# 
#         result.append("Can trade")
#     else:
#         result.append("Can not trade")
#     return result
# =============================================================================
