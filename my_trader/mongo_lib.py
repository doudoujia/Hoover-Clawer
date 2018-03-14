
from my_trader import *


class mongo:

    def __init__(self,freq = "stocks_daily"):
        self.client = pymongo.MongoClient()
        self.db = self.client[freq]
        self.stock_list = "cantrade.csv"
        self.ETF_list = "ETFList.csv"
        self.initiate_list = [self.stock_list,self.ETF_list]

    def get_ondemand_quote(self,sym):
        api_key = 'b59b144a62e058b6c4e265c049dc679f'
        sym = "%2C".join(sym)
        # This is the required format for datetimes to access the API

        api_url = 'https://marketdata.websol.barchart.com/getQuote.csv?' +\
                        'apikey={}&symbols={}&mode=D'\
                             .format(api_key,sym)

        csvfile = pd.read_csv(api_url)
        csvfile = csvfile.rename(columns={"symbol":"Ticker","serverTimestamp":"TimeStamp",\
                           "open":"Open","high":"High","low":"Low","close":"Close",\
                           "volume":"Volume","lastPrice":"Adj Close","netChange":"net_Return","percentChange":"Return"})
        #csvfile.set_index('timestamp', inplace=True)
        return csvfile

    def get_all_quote(self):
        result = pd.DataFrame()
        all_stock_1 = pd.read_csv(directory + self.stock_list)
        all_stock_2 = pd.read_csv(directory + self.ETF_list)
        all_stock_2 = all_stock_2.rename(columns={"Symbol":"Ticker"})
        all_stock = all_stock_1.append(all_stock_2)
        all_stock = all_stock.reset_index()
        for i in range(99,len(all_stock),100):
            tic_list = all_stock.Ticker.iloc[i-99:i].astype(str)
            result = result.append(self.get_ondemand_quote(tic_list))   
        return result

    def query_database(self,stock, start_date = datetime.now()-timedelta(days =190),end_date=datetime.now()):
        
        collection = self.db[stock]
        self.delete_duplicates(stock)
        start_date=(start_date-datetime.utcfromtimestamp(0)).total_seconds()*1000

        end_date = (end_date-datetime.utcfromtimestamp(0)).total_seconds()*1000
        get = collection.find({"Ticker":stock,"TimeStamp":{"$gte":start_date,"$lt":end_date}}).sort("TimeStamp",pymongo.ASCENDING)
        get_frame = pd.DataFrame(list(get))
        if len(get_frame) == 0:
            print ("no data for " + stock)
        get_frame[u'TimeStamp'] = get_frame[u'TimeStamp'].apply(lambda x: datetime.utcfromtimestamp(0) + timedelta(milliseconds= x))
        get_frame = get_frame.loc[:,["TimeStamp",'Adj Close','High','Low','Open','Ticker',"Volume"]]
        get_frame = get_frame.dropna()
        get_frame = get_frame.reindex()
        return get_frame

    def frame_to_mongo(sefl,data,collection):
        records = json.loads(data.T.to_json()).values()
        collection.insert(records)

    def update_db(self,stock):
        for i in stock.Ticker:
            try:
                client = pymongo.MongoClient()
                db = client["stocks_daily"]
                collection = db[i]
                quote = stock.loc[stock.Ticker==i]
                quote.loc[:,'TimeStamp']  = datetime.strptime(quote['TimeStamp'].values[0][0:10],"%Y-%m-%d")
                quote = json.loads(quote.T.to_json()).values()[0]
                collection.update_many({"TimeStamp":quote[u'TimeStamp']},{"$set": quote },upsert=True)
                clear_output()
                print ("successed " + i)
            except Exception as e:
                print e
                print ("error occored in updating "+ str(i))
                continue 

    def delete_duplicates(self,stock):

        collection = self.db[stock]
        cursor = collection.aggregate(
            [
                {"$group": {"_id": "$TimeStamp", "unique_id": {"$addToSet": "$_id"}, "count": {"$sum": 1}}},
                {"$match": {"count": { "$gte": 2 }}}
            ]
        )

        response = []
        for doc in cursor:
            del doc["unique_id"][0]
            for id in doc["unique_id"]:
                response.append(id)

        collection.delete_many({"_id": {"$in": response}})

    def initiate_db(self):
        for i in self.initiate_list:
            all_stock = pd.read_csv(directory+i)
            count = 0.0
            client = pymongo.MongoClient()
            db = client["stocks_daily"]
            for i in all_stock.Symbol:
                trial=0
                success = False
                while not success and trial<2:
                    try:
                        print ("getting "+str(i))
                        price_table = get_price_data([i],"day")
                        
                        this_collection = db[i]
                        frame_to_mongo(price_table,this_collection)
                        print ("\nfinished inserting db "+str(i))
                        clear_output()
                        print ("Finished "+str(int(count)))
                        print ("{0:0.2f}%".format( count/len(all_stock)*100))
                        delete_duplicates(i)
                        count +=1
                        success = True
                    except Exception as e:
                        print e
                        trial += 1
                        time.sleep(3)
                        print ("Tring again")
                        continue
