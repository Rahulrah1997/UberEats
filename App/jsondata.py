import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import json

#Extract data from the json
with open("D:/Rahul/AIML/orders.json","r",encoding="utf-8")as file:
    order_data = json.load(file)

bulkorderdata = [(order['order_id'],order['restaurant_name'],order['order_date'],
                  order['order_value'],order['discount_used'],order['payment_method']) for order in order_data]

#Create DB connection

conn = sqlite3.connect('ubereats.db')
cursor = conn.cursor()

#create table and Insert the order details in sql
try:
    cursor.execute("Begin")
    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS order_details(
                        id INTEGER PRIMARY KEY, order_id TEXT, restaurant_name TEXT, 
                        order_date DATE, order_value REAL, discount_used TEXT, payment_method TEXT)''')

    cursor.executemany('''INSERT INTO order_details ( order_id , restaurant_name, order_date , order_value , discount_used, payment_method )
    VALUES(?,?,?,?,?,?)''',bulkorderdata)

    conn.commit()

except sqlite3.Error as err:
    conn.rollback()
    print(err)

# finally:
#     if cursor:
#         cursor.close()

#     if conn:
#         conn.close()
