import pandas as pd
import numpy as np
import re
import sqlite3

class Data_clean:

    def __init__(self, df_copy: pd.DataFrame):
        self.df = df_copy
        self.conn = None
       

    def Res_DataExtract(self):
        df_copy = self.df    

        df_copy['rate'] = df_copy['rate'].str.replace(" ", "").str.split("/").str[0]
        df_copy['rate'] = pd.to_numeric(df_copy['rate'], errors='coerce')
        df_copy['rate'] = (df_copy.groupby(['name', 'location'])['rate'].transform(lambda x: x.fillna(x.median()))
                           .fillna(df_copy.groupby('name')['rate'].transform(lambda x: x.fillna(x.median()))
                                   .fillna(df_copy['rate'].median())))
        df_copy['rate'] = df_copy['rate'].round(1)

        df_copy['votes'] = np.log1p(df_copy['votes'])

        df_copy['rest_type'] = df_copy['rest_type'].str.replace(r'\s*,\s*', ',', regex=True)
        df_copy['listed_in(type)'] = df_copy['listed_in(type)'].str.strip().str.title()

        df_copy['approx_cost(for two people)'] = df_copy['approx_cost(for two people)'].str.replace(',', '')
        df_copy['approx_cost(for two people)'] = df_copy['approx_cost(for two people)'].astype('float')
        df_copy['approx_cost(for two people)'] = df_copy['approx_cost(for two people)'].round(1).apply(lambda x: f"{x:.1f}")

        return df_copy

    def MobileNo_Clean(self, mobileNo):

        if mobileNo is None or (isinstance(mobileNo, float) and np.isnan(mobileNo)):
            return pd.Series([np.nan, np.nan])
        
        if isinstance(mobileNo, np.ndarray):
            numbers = mobileNo.tolist()
        elif isinstance(mobileNo, list):
            numbers = mobileNo
        else:
            numbers = str(mobileNo).split('\r\n')

        country_codes = []
        mobile_numbers = []

        for num in numbers:
            num = re.sub(r'\D', '', str(num)) 
            if len(num) > 10:
                number = num[-10:] 
            else:
                number = num
            country_codes.append('+91') 
            mobile_numbers.append(number)

        return pd.Series([', '.join(country_codes), ', '.join(mobile_numbers)])

    def CleanData(self):
       
        df_copy = self.Res_DataExtract()

        df_copy[['country_code', 'phone']] = df_copy['phone'].apply(self.MobileNo_Clean)

        return df_copy
    
    def insert_sql(self):
        self.conn = sqlite3.connect('ubereats.db')
        cursor = self.conn.cursor()
        df_copy = self.CleanData()
        try:
            cursor.execute("Begin")
            cursor.execute('''CREATE TABLE IF NOT EXISTS restaurant_details(
                        id INTEGER PRIMARY KEY, rest_name TEXT, online_order VARCHAR(3), 
                        book_table VARCHAR(3), rate REAL, votes REAL, phone TEXT,location TEXT,rest_type TEXT,
                        dish_liked TEXT, cuisines TEXT, approx_cost TEXT, listed_in_type TEXT, listed_in_city TEXT, country_code VARCHAR(3))''')

            df_copy.to_sql('restaurant_details',self.conn,if_exists='replace',index=False)
            
            self.conn.commit()

        except sqlite3.Error as err:
            self.conn.rollback()
            print(err)
        return self.conn

