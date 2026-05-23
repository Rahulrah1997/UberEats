import streamlit as st
from ResDataExtract import Data_clean
import pandas as pd

df = pd.read_csv("Uber_Eats_data.csv")
QA_df = {'Q1':'Which Bangalore locations have the highest average restaurant ratings?',
         'Q2':'Which locations are over-saturated with restaurants?',
         'Q3':'Does online ordering improve restaurant ratings?',
         'Q4':'Does table booking correlate with higher customer ratings?'}

getdata = Data_clean(df)
getdata.insert_sql()

PageSelection = st.sidebar.selectbox("Select Page",['Filter Page','Q&A Page'])

if PageSelection == 'Q&A Page':

    st.title("Q&A Page")

    qn_selection = st.selectbox("Select Question",QA_df.values())

   
    if qn_selection == QA_df['Q1']:

        query = "select AVG(rate) AS Rating,location AS Location from restaurant_details group by location LIMIT 1"
        answer = pd.read_sql(query,getdata.conn)
        answer['Rating'] = answer['Rating'].round(1)
        st.dataframe(answer,hide_index=True)


