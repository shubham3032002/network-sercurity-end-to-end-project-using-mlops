import os
import sys
import json
from dotenv import load_dotenv
import certifi
import pandas as pd
import numpy as np
from pymongo.mongo_client import MongoClient
import pymongo
from  networksercurity.Exception import custom_expection
from networksercurity.logging import logger
load_dotenv()

MONGODB_URL=os.getenv('MONGODB_URL')

ca=certifi.where()

class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise custom_expection(e,sys)
        
    def cv_to_json(self,file_path):
        try:
            data=pd.read_csv(file_path)
            data.reset_index(drop=True,inplace=True)
            records=list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise custom_expection(e,sys)    
        
        
    def insert_data_mongodb(self,records,database,collection):
        try:
            self.database=database
            self.records=records
            self.collection=collection
            
            self.mongo_client=pymongo.MongoClient(MONGODB_URL)
            self.database=self.mongo_client[self.database]
            self.collection=self.database[self.collection]
            self.collection.insert_many(self.records)
            return (len(self.records))
        except Exception as e:
            raise custom_expection(e,sys) 
            
            
if __name__ =='__main__':
    FILE_PATH ='D:\\DATA SCIENCE\\ML project\\network project\\network_data\\phisingData.csv'            
    DATABASE='Network'
    Collection='NetworkData'
    
    network_obj=NetworkDataExtract()
    records=network_obj.cv_to_json(file_path=FILE_PATH)
    print(records)
    no_of_records=network_obj.insert_data_mongodb(records,DATABASE,Collection)
    print(no_of_records)