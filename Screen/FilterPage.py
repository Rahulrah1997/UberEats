import streamlit as st
import pandas as pd
from BackEnd.backend import Database 
import os

db = Database()

if not os.path.exists("ubereats.db"):
    db.insert_data()
    db.insert_json()


def fliterpage():

    with db.connect_db() as conn:

        st.header(body="Search Your Favourite Foods and Restaurant",text_alignment='center',divider='green')

        query = "select distinct location from restaurant_details"
        loc_fetch = pd.read_sql(query,conn)
        st.subheader("Where would you like to eat:")
        loc_selection = st.selectbox(label="",options=loc_fetch, index=None,placeholder="Select Location")

        if loc_selection:

            query = "select distinct listed_in_city from restaurant_details where location=:loc_selection"
            city_fetch = pd.read_sql(query,conn,params={'loc_selection':loc_selection})
            st.subheader("Select the city:")
            City_selection = st.selectbox("",city_fetch,index=None,placeholder="Select City")

            if City_selection:
                query = "select distinct rest_type from restaurant_details where location=:loc_selection and listed_in_city =:City_selection"
                restype_fetch = pd.read_sql(query,conn,params={'loc_selection':loc_selection,'City_selection':City_selection})
                st.subheader("Select Your Favourite Restaurant Type")
                restype_selection = st.multiselect(label="",options=restype_fetch)

                
        
                if restype_selection:

                    search_button = st.button(label="Click To search",use_container_width=True)

                    if search_button:
                        placeholders = ", ".join(["?"] * len(restype_selection))
                    
                        query = f"""select rest_name AS Restaurant, online_order AS OnlineOrder, book_table AS TableBooking,
                            cuisines,listed_in_type as TypeListed,rest_type AS RestaurantType,listed_in_city AS City, rate AS Rating,phone AS ContactNo
                            from restaurant_details where location=? and listed_in_city =? and rest_type IN ({placeholders})"""
                        param_value = [loc_selection, City_selection] + list(restype_selection)
                        data_fetch = pd.read_sql(query,conn,params=param_value)
                        st.dataframe(data_fetch,hide_index=True)

    
