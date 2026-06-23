import streamlit as st
from ResDataExtract import Data_clean
import pandas as pd

# df = pd.read_csv("E:/AIML/PojectUberEats/DataSet/Uber_Eats_data.csv")
df = pd.read_csv("D:/Rahul/AIML/Uber_Eats_data.csv")

QA_df = {'Q1':'Which Bangalore locations have the highest average restaurant ratings?',
         'Q2':'Which locations are over-saturated with restaurants?',
         'Q3':'Does online ordering improve restaurant ratings?',
         'Q4':'Does table booking correlate with higher customer ratings?',
         'Q8':'Which cuisines receive the highest average ratings?',
         'Q9':'Which cuisines perform well despite having fewer restaurants?',
         'Q10':'What is the relationship between restaurant cost and rating?',
         'Q13':'Do restaurants offering both online ordering and table booking perform better?',
         'Q14':'What combination of factors maximizes restaurant success on Uber Eats?',
         'Q15':'Which restaurants are top performers within each pricing segment?'}

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

    if qn_selection ==QA_df['Q8']:

        query = "select cuisines,rate from restaurant_details  WHERE cuisines IS NOT NULL AND rate IS NOT NULL group by cuisines"
        answer = pd.read_sql(query,getdata.conn)
        answer['cuisines'] = answer['cuisines'].str.split(',')   
        answer = answer.explode('cuisines')
        answer['cuisines'] = answer['cuisines'].str.strip()
        avg_rate_cusines = answer.groupby('cuisines')['rate'].mean().reset_index()
        avg_rate_cusines = avg_rate_cusines.sort_values(by='rate',ascending=False)
        st.dataframe(avg_rate_cusines.head(10),hide_index=True)

    if qn_selection ==QA_df['Q9']:

        query = "select rest_name,cuisines,rate from restaurant_details"
        answer = pd.read_sql(query,getdata.conn)
        answer['cuisines'] = answer['cuisines'].str.split(',')   
        answer = answer.explode('cuisines')
        answer['cuisines'] = answer['cuisines'].str.strip()

    

    if qn_selection ==QA_df['Q10']:

        #query = "select distinct(rest_name),rate,approx_cost from restaurant_details WHERE  rate IS NOT NULL"
        query = "select rest_name,rate,approx_cost from restaurant_details WHERE  rate IS NOT NULL"
        answer = pd.read_sql(query,getdata.conn)
        correlation = answer['approx_cost'].corr(answer['rate'])

        corr_dic = {'Total Restaurants Analyzed':len(answer),'Correlation Score':f"{correlation:.2f}"}
        corr_df = pd.DataFrame([corr_dic])
        st.dataframe(corr_df,hide_index=True)
        
    if qn_selection == QA_df['Q13']:

        query = "select CASE WHEN online_order='Yes' and book_table='Yes' THEN 'Both service' WHEN online_order='Yes' and book_table='No' THEN 'online order' WHEN online_order='No' and book_table='Yes' THEN 'table booking'ELSE 'No online service'END AS Service_type, count (DISTINCT rest_name) AS Total_Restaurant, ROUND(AVG(rate),2) AS average_rating from restaurant_details GROUP BY Service_type ORDER by average_rating desc"
        answer = pd.read_sql(query,getdata.conn)
        st.dataframe(answer,hide_index=True)

    if qn_selection == QA_df['Q14']:

        query = """SELECT location,approx_cost AS pricing_level,cuisines, online_order,book_table, ROUND(AVG(rate), 2) AS average_rating,
            SUM(votes) AS total_engagement, COUNT(*) AS restaurant_count
            FROM restaurant_details
            GROUP BY location, approx_cost, cuisines, online_order,book_table
            HAVING COUNT(*) >= 2
            ORDER BY average_rating DESC,total_engagement DESC
            LIMIT 10"""
        answer = pd.read_sql(query,getdata.conn)
        st.dataframe(answer,hide_index=True)

    if qn_selection == QA_df['Q15']:

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


       

        
        





