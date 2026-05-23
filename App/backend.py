import streamlit as st
import sqlite3
from ResDataExtract import Data_clean

class QAPage():
    
    def ResData(self):
        cleaned_Data = Data_clean.Res_DataExtract()
        conn = sqlite3.connect('ubereats.db')
        cursor = conn.cursor()
        try:
            cursor.execute("Begin")
            cursor.execute('''CREATE TABLE IF NOT EXISTS restaurant_details(
                        id INTEGER PRIMARY KEY, rest_name TEXT, online_order VARCHAR(3), 
                        book_table VARCHAR(3), rate REAL, votes REAL, phone TEXT,location TEXT,rest_type TEXT,
                        dish_liked TEXT, cuisines TEXT, approx_cost TEXT, listed_in_type TEXT, listed_in_city TEXT, country_code VARCHAR(3))''')

            cleaned_Data.to_sql('restaurant_details',conn,if_exists='replace',index=False)
            
            conn.commit()

        except sqlite3.Error as err:
            conn.rollback()
            print(err)
        return self.conn


    
    
