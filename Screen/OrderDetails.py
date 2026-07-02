import streamlit as st
import pandas as pd
from BackEnd.backend import Database 
import os
import datetime

db = Database()

if not os.path.exists("ubereats.db"):
    db.insert_data()
    db.insert_json()



def OrderData():

    with db.connect_db() as conn:

        is_error = True
        res_selection = None
        fromdate = None
        todate = None
        discount_selection = None
        payment_selection= None

        def clearbutton():
            st.session_state.res_key = None          
            st.session_state.discount_key = []     
            st.session_state.payment_key = []      
            st.session_state.StartDate = None  
            st.session_state.EndDate = None   
            st.session_state.is_error = True

        query = "select restaurant_name location from order_details"
        res_data = pd.read_sql(query,conn)

        st.header(body="Order Details Search",text_alignment='center',divider='green')

        st.subheader("Select Restaurant Name")
        
        res_selection = st.selectbox(label="", options=res_data,index=None,placeholder="Select Name",key='res_key')
        

        col1,col2 = st.columns(2)

        with col1:

            st.subheader("Select From Date")
            today = datetime.date.today()
            fromdate = st.date_input(label="",value=None,key="StartDate")
            
            if fromdate!=None and fromdate> today :
                st.error("From date should not be future date")
                is_error = False
            
            st.subheader("Select To Date")
            todate = st.date_input(label="",value=None,key="EndDate")

            if todate!=None and todate > today   :
                st.error("To date should not be future date")
                is_error = False

            elif fromdate!=None and todate!=None and todate < fromdate:
                st.error("To date should not greater than From Date")  
                is_error = False

            search_button = st.button(label="Click to search",use_container_width=True)   
            

        with col2:

            st.subheader("Select Discount Used")
            discount_selection = st.multiselect(label="",options=['Yes','No'],default=None,key='discount_key')

            st.subheader("Select Payment type")
            payment_selection = st.multiselect(label="",options=['Card','Cash','UPI'],default=None,key='payment_key')

            Clear_button = st.button(label="Click to Clear",use_container_width=True,on_click=clearbutton)  

        if search_button:

            if is_error == True and (res_selection is not None or fromdate is not None or todate is not None or discount_selection or payment_selection )  :

                search_values = {'res_selection':res_selection,'fromdate':fromdate,'todate':todate,
                                'discount_selection':discount_selection,'payment_selection':payment_selection}
                query = "select * from order_details where 1=1 "
                params = []

                from_date = search_values.get('fromdate')
                to_date = search_values.get('todate')
                dis_selection = search_values.get('discount_selection')
                pay_selection = search_values.get('payment_selection')

                if search_values.get('res_selection')is not None:
                    query += "AND restaurant_name =?"                
                    params.append(search_values['res_selection'])

                if from_date is not None and to_date is not None:
                    query += "AND order_date between ? and ?"                
                    params.append(search_values['fromdate'])
                    params.append(search_values['todate'])

                elif from_date is not None:

                    query += "AND order_date = ?"                
                    params.append(search_values['fromdate'])

                elif to_date is not None:

                    query += "AND order_date = ?"                   
                    params.append(search_values['todate'])

                if  dis_selection:

                    placeholders_dis = ", ".join(["?"] * len(dis_selection))               
                    query += f"AND discount_used In ({placeholders_dis})"
                    params.extend(dis_selection)

                if pay_selection :

                    placeholders_pay = ", ".join(["?"] * len(pay_selection))               
                    query += f"AND payment_method In ({placeholders_pay})"
                    params.extend(pay_selection)


                answer = pd.read_sql(query,conn,params=params)
                st.dataframe(answer,hide_index=True)

            else:

                st.error("Choose any value to search or select correct date",width='stretch')

   