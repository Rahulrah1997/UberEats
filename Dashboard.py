import streamlit as st
from Screen.OrderDetails import OrderData
from Screen.FilterPage import fliterpage
from Screen.QAPage import QA

st.header(body="Uber Eats Project",text_alignment='center',divider='green')
st.subheader("Select the Screen")
PageSelection = st.selectbox(label="",options=['Q&A Page','Filter Page', 'OrderDetails'],index=None,placeholder="Select Screen")

if PageSelection == 'OrderDetails':    

   OrderData()
            
elif PageSelection == 'Filter Page':


    fliterpage()
                
                

elif PageSelection == 'Q&A Page':

   QA()


    











