import streamlit as st
from ResDataExtract import Data_clean
import pandas as pd
import datetime

# df = pd.read_csv("E:/AIML/PojectUberEats/DataSet/Uber_Eats_data.csv")
df = pd.read_csv("D:/Rahul/AIML/Uber_Eats_data.csv")
jsonfile = "D:/Rahul/AIML/orders.json"

QA_df = {'Q1':'1. Which Bangalore locations have the highest average restaurant ratings?',
         'Q2':'2. Which locations are over-saturated with restaurants?',
         'Q3':'3. Does online ordering improve restaurant ratings?',
         'Q4':'4. Does table booking correlate with higher customer ratings?',
         'Q5':'5. What price range delivers the best customer satisfaction?',
         'Q6':'6. Which cuisines receive the highest average ratings?',
         'Q7':'7. What is the relationship between restaurant cost and rating?',
         'Q8':'8. Do restaurants offering both online ordering and table booking perform better?',
         'Q9':'9. What combination of factors maximizes restaurant success on Uber Eats?',
         'Q10':'10. Which restaurants are top performers within each pricing segment?'}

getdata = Data_clean(df,jsonfile)
getdata.init_sql()

PageSelection = st.sidebar.selectbox("Select Page",['Filter Page','Q&A Page', 'OrderDetails'])

if PageSelection == 'OrderDetails':    

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
    res_data = pd.read_sql(query,getdata.conn)

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


            answer = pd.read_sql(query,getdata.conn,params=params)
            st.dataframe(answer,hide_index=True)

        else:

            st.error("Choose any value to search or select correct date",width='stretch')
   

        
            
if PageSelection == 'Filter Page':

    st.header("Search Your Favourite Foods and Restaurant")

    query = "select distinct location from restaurant_details"
    loc_fetch = pd.read_sql(query,getdata.conn)
    loc_selection = st.selectbox("Where would you like to eat:",loc_fetch, index=None,placeholder="Select Location")

    if loc_selection:

        query = "select distinct listed_in_city from restaurant_details where location=:loc_selection"
        city_fetch = pd.read_sql(query,getdata.conn,params={'loc_selection':loc_selection})
        City_selection = st.selectbox("Select the city:",city_fetch,index=None,placeholder="Select City")

        if City_selection:
            query = "select distinct rest_type from restaurant_details where location=:loc_selection and listed_in_city =:City_selection"
            restype_fetch = pd.read_sql(query,getdata.conn,params={'loc_selection':loc_selection,'City_selection':City_selection})
            restype_selection = st.multiselect(label="Select Your Favourite Restaurant Type",options=restype_fetch)

            
     
            if restype_selection:

                search_button = st.button(label="Click To search",use_container_width=True)

                if search_button:
                    placeholders = ", ".join(["?"] * len(restype_selection))
                
                    query = f"""select rest_name AS Restaurant, online_order AS OnlineOrder, book_table AS TableBooking,
                        cuisines,listed_in_type as TypeListed,rest_type AS RestaurantType,listed_in_city AS City, rate AS Rating,phone AS ContactNo
                        from restaurant_details where location=? and listed_in_city =? and rest_type IN ({placeholders})"""
                    param_value = [loc_selection, City_selection] + list(restype_selection)
                    data_fetch = pd.read_sql(query,getdata.conn,params=param_value)
                    st.dataframe(data_fetch,hide_index=True)
                
                

if PageSelection == 'Q&A Page':

    st.title("Q&A Page")

    qn_selection = st.selectbox("Select Question",QA_df.values())


    if qn_selection == QA_df['Q1']:

        query = "select AVG(rate) AS Rating,location AS Location from restaurant_details group by location LIMIT 1"
        answer = pd.read_sql(query,getdata.conn)
        answer['Rating'] = answer['Rating'].round(1)
        st.dataframe(answer,hide_index=True)

    if qn_selection == QA_df['Q2']:

        query = """SELECT location, COUNT(*) AS total_restaurants,ROUND(AVG(CAST(votes AS INT)), 0) AS average_votes_per_restaurant
            FROM restaurant_details
            GROUP BY location
            HAVING
            COUNT(*) > (SELECT COUNT(*) FROM restaurant_details) / (SELECT COUNT(DISTINCT location) FROM restaurant_details)
            AND AVG(CAST(votes AS INT)) < (SELECT AVG(CAST(votes AS INT)) FROM restaurant_details)
            ORDER BY total_restaurants DESC"""
        answer = pd.read_sql(query,getdata.conn)
        st.dataframe(answer,hide_index=True)

    if qn_selection == QA_df['Q3']:

        query = """SELECT online_order, COUNT(*) AS Total_Restaurant,
            ROUND(AVG(CAST(rate AS real)),2) AS Average_Rating,
            SUM(CAST(votes as int)) AS Total_votes FROM restaurant_details
            GROUP BY online_order"""
        answer = pd.read_sql(query,getdata.conn)
        st.dataframe(answer,hide_index=True)

    if qn_selection == QA_df['Q4']:

        query = """select book_table AS table_booking,
            COUNT(*) AS total_restaurant,
            ROUND(AVG(CAST(rate AS real)),2)AS average_rating,
            SUM(CAST(votes AS int)) AS total_voting,
            ROUND(AVG(CAST(votes AS int)),2) AS average_voting from restaurant_details
            GROUP BY book_table ORDER BY average_rating desc"""
        answer = pd.read_sql(query,getdata.conn)
        st.dataframe(answer,hide_index=True)

    if qn_selection == QA_df['Q5']:

        s_query = "select approx_cost from restaurant_details"
        q_details = pd.read_sql(s_query,getdata.conn)
        q1 = q_details['approx_cost'].quantile(0.25)
        q2 = q_details['approx_cost'].quantile(0.50)
        q3 = q_details['approx_cost'].quantile(0.75)

        query = """SELECT CASE
            WHEN approx_cost <= :q1 THEN '1. Budget (Under ₹:'||:q1||')'
            WHEN approx_cost > :q1 and approx_cost<= :q2 THEN '2. Mid-Range (₹:'||:q1||' - '||:q2||')'
            WHEN approx_cost > :q2 and approx_cost<= :q3 THEN '2. Premium (₹:'||:q2||' - '||:q3||')'
            ELSE 'Luxuary (Above ₹:'||:q3||')'
            END AS Pricing_segment,
            COUNT(*) AS total_restaurants,ROUND(AVG(CAST(rate AS REAL)), 2) AS average_customer_rating,
            SUM(CAST(votes AS INT)) AS total_customer_votes
            FROM restaurant_details
            GROUP BY pricing_segment
            ORDER BY pricing_segment ASC"""
        answer = pd.read_sql(query,getdata.conn,params={'q1':q1,'q2':q2,'q3':q3})
        st.dataframe(answer,hide_index=True)

    if qn_selection ==QA_df['Q6']:

        query = "select cuisines,rate from restaurant_details  group by cuisines"
        answer = pd.read_sql(query,getdata.conn)
        answer['cuisines'] = answer['cuisines'].str.split(',')
        answer = answer.explode('cuisines')
        answer['cuisines'] = answer['cuisines'].str.strip()
        avg_rate_cusines = answer.groupby('cuisines')['rate'].mean().reset_index()
        avg_rate_cusines = avg_rate_cusines.sort_values(by='rate',ascending=False)
        st.dataframe(avg_rate_cusines.head(10),hide_index=True)


    if qn_selection ==QA_df['Q7']:

        #query = "select distinct(rest_name),rate,approx_cost from restaurant_details WHERE  rate IS NOT NULL"
        query = "select rest_name,rate,approx_cost from restaurant_details WHERE  rate IS NOT NULL"
        answer = pd.read_sql(query,getdata.conn)
        correlation = answer['approx_cost'].corr(answer['rate'])

        corr_dic = {'Total Restaurants Analyzed':len(answer),'Correlation Score':f"{correlation:.2f}"}
        corr_df = pd.DataFrame([corr_dic])
        st.dataframe(corr_df,hide_index=True)

    if qn_selection == QA_df['Q8']:

        query = "select CASE WHEN online_order='Yes' and book_table='Yes' THEN 'Both service' WHEN online_order='Yes' and book_table='No' THEN 'online order' WHEN online_order='No' and book_table='Yes' THEN 'table booking'ELSE 'No online service'END AS Service_type, count (DISTINCT rest_name) AS Total_Restaurant, ROUND(AVG(rate),2) AS average_rating from restaurant_details GROUP BY Service_type ORDER by average_rating desc"
        answer = pd.read_sql(query,getdata.conn)
        st.dataframe(answer,hide_index=True)

    if qn_selection == QA_df['Q9']:

        query = """SELECT location,approx_cost AS pricing_level,cuisines, online_order,book_table, ROUND(AVG(rate), 2) AS average_rating,
            SUM(votes) AS total_engagement, COUNT(*) AS restaurant_count
            FROM restaurant_details
            GROUP BY location, approx_cost, cuisines, online_order,book_table
            HAVING COUNT(*) >= 2
            ORDER BY average_rating DESC,total_engagement DESC
            LIMIT 10"""
        answer = pd.read_sql(query,getdata.conn)
        st.dataframe(answer,hide_index=True)

    if qn_selection == QA_df['Q10']:

        s_query = "select approx_cost from restaurant_details"
        q_details = pd.read_sql(s_query,getdata.conn)
        q1 = q_details['approx_cost'].quantile(0.25)
        q2 = q_details['approx_cost'].quantile(0.50)
        q3 = q_details['approx_cost'].quantile(0.75)

        query = """WITH PricingSegment AS (
                    SELECT rest_name,approx_cost,location,cuisines,rate,votes,
                    CASE
                    WHEN approx_cost <= :q1 THEN '1. Budget (Under ₹:'||:q1||')'
                    WHEN approx_cost > :q1 AND approx_cost <= :q2 THEN '2. Mid-Range (₹:'||:q1|| '- ₹:'||:q2||')'
                    WHEN approx_cost > :q2 AND approx_cost <= :q3 THEN '3. Premium (₹:'||:q2||' - ₹:'||:q3||')'
                    ELSE '4. Luxury (Above ₹:'||:q3||')'
                    END AS pricing_segment
                    FROM  restaurant_details GROUP BY rest_name, approx_cost, location, cuisines
                ),
                    RestaurantRank AS (
                        SELECT rest_name,approx_cost, location,cuisines,rate,votes, pricing_segment,
                        DENSE_RANK() OVER (
                        PARTITION BY pricing_segment
                        ORDER BY rate DESC, votes DESC
                            ) AS price_rank
                        FROM PricingSegment
                    )
                    SELECT  rest_name,pricing_segment,approx_cost AS exact_cost,location,cuisines,rate AS rating,votes
                    FROM RestaurantRank
                    WHERE price_rank <= 3
                    ORDER BY pricing_segment ASC,price_rank ASC"""
        answer = pd.read_sql(query,getdata.conn,params={'q1':q1,'q2':q2,'q3':q3})
        st.dataframe(answer,hide_index=True)











