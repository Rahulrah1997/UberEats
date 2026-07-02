import sqlite3
from BackEnd.ResDataExtract import Data_clean
import pandas as pd

df = pd.read_csv("DataSet/Uber_Eats_data.csv")
jsonfile = "DataSet/orders.json"

data = Data_clean(df,jsonfile)

class Database:

    
    def connect_db(self):
        return sqlite3.connect("ubereats.db")

            
    def insert_data(self):

        conn = self.connect_db()
        
        data.CleanData().to_sql(
            "restaurant_details",
            conn,
            if_exists="replace",
            index=False
        )

        conn.commit()
        conn.close()

    def insert_json(self):

        conn = self.connect_db()       
        data.jsonextract().to_sql(
            "order_details",
            conn,
            if_exists="replace",
            index=False
        )
        conn.commit()
        conn.close()