# Importing Libraries
import pandas as pd
import mysql.connector as sql
import streamlit as st
import plotly.express as px
import os
import json
from streamlit_option_menu import option_menu
from git.repo.base import Repo
import matplotlib.pyplot as plt
import numpy as np

# Setting up page configuration

st.set_page_config(page_title= "Phonepe Pulse Data Visualization",
                   layout= "wide",
                   initial_sidebar_state= "expanded"
                   )

st.sidebar.title("Phonepe Pulse Data Visualization")
st.sidebar.text("By Rafadh Rafeek")

# #To clone the Github Pulse repository use the following code
# Reference Syntax - Repo.clone_from("Clone Url", "Your working directory")
# Repo.clone_from("https://github.com/PhonePe/pulse.git", "Project_3_PhonepePulse/Phonepe_data/data")

# Creating connection with mysql workbench
mydb = sql.connect(host="localhost",
                   user="root",
                   password="root",
                   database= "phonepe_data1"
                  )
mycursor = mydb.cursor(buffered=True)


# Creating option menu in the side bar
with st.sidebar:
    options = st.selectbox('',
                                  ("Transaction",
                                   "User"
                                   ),
                                   key='options')
    year = st.selectbox('Year',
                                  ("2018",
                                   "2019",
                                   "2020",
                                   "2021",
                                   "2022",
                                   "2023",
                                   ),
                                   key='year')
    quarter = st.selectbox('Quater',
                                  ("1",
                                   "2",
                                   "3",
                                   "4",
                                   ),
                                   key='quater')
#USER DATA VISUALIZATION   
def user(type,year,quarter):
    #MAP VISUALIZATION
    toggle_map = st.radio(
                "Select Map Option",
                ["By Total User", "By Total App Open"])
    qry_map_user = f"select c_state, sum(RegisteredUsers) as Total_Users, sum(AppOpens) as Total_Appopens from map_user where year = {year} and quarter = {quarter} group by c_state order by Total_Users desc"
    if toggle_map == "By Total User":
        mycursor.execute(qry_map_user)
        df_user = pd.DataFrame(mycursor.fetchall(),columns= ['State', 'Total_User', 'Total_Appopen'])
        df_user['Total_Appopen']=df_user['Total_Appopen'].astype(np.int64)
        df_user['Total_User']=df_user['Total_User'].astype(np.int64)
        fig1 = px.choropleth(
            df_user,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM',
            locations='State',
            color='Total_User',
            color_continuous_scale='Blues'
        )

        fig1.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig1,use_container_width=True)
        df_user.index += 1
        st.write(df_user)
    else:
        mycursor.execute(qry_map_user)
        df_user = pd.DataFrame(mycursor.fetchall(),columns= ['State', 'Total_User', 'Total_Appopen'])
        df_user['Total_Appopen']=df_user['Total_Appopen'].astype(int)
        fig1 = px.choropleth(
            df_user,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM',
            locations='State',
            color='Total_Appopen',
            color_continuous_scale='Greens'
        )

        fig1.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig1,use_container_width=True)
        df_user.index += 1
        st.write(df_user)

    qry_total_appopen = f"select sum(total) from (select sum(AppOpens) as total from map_user where year = {year} and quarter = {quarter} group by state) as e;"
    qry_total_user = f"select sum(total) from (select sum(RegisteredUsers) as total from map_user where year = {year} and quarter = {quarter} group by state) as e;"
    qry_user_bycat = f"select Brands, sum(User_Registered) as Total_Count, avg(percentage)*100 as Avg_Percentage from agg_user where year = {year} and quarter = {quarter} group by brands order by Total_Count desc"
# TOTAL USER SIDE BAR
    mycursor.execute(qry_total_user)
    tot_user = "{:,}".format(mycursor.fetchall()[0][0])
    st.sidebar.header(':violet[Total Registerd Users]')
    st.sidebar.title(tot_user)
# APP OPEN SIDE BAR
    mycursor.execute(qry_total_appopen)
    tot_appopen = "{:,}".format(mycursor.fetchall()[0][0])
    st.sidebar.header(':violet[Total App Opens]')
    if tot_appopen != "0":
        st.sidebar.title(tot_appopen)
    else:
        st.sidebar.title("Unavailable")
# USER BY CAT SIDE BAR
    mycursor.execute(qry_user_bycat)
    df_user_bycat = pd.DataFrame(mycursor.fetchall(), columns=['Brand', 'Total_Users','Avg_Percentage'])
# CHECK IF AVAILABLE OR NO
    if df_user_bycat.empty:
        st.title(":red[Unavailable]")
    else:
        st.header(':violet[User Registered By Brands]')
        st.write(df_user_bycat)
        fig = px.pie(df_user_bycat, values='Total_Users',
                            names='Brand',
                            title='User Registered By Brands',
                            color_discrete_sequence=px.colors.sequential.Agsunset,
                            hover_data=['Brand'],
                            labels={'Brand':'Brand'})
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig,use_container_width=True)
# YEAR VISE VISUALIZATION
    year_vis_user = f"select year, sum(RegisteredUsers) as Total_Register, sum(AppOpens) as Total_appopen from map_user group by year order by year asc;"
    mycursor.execute(year_vis_user)
    df_year_vis_user = pd.DataFrame(mycursor.fetchall(),columns= ['Year', 'Total_Register', 'Total_AppOpen'])
    df_year_vis_user.index += 1

    fig = px.line(df_year_vis_user,
                x='Year',
                y='Total_Register', 
                title='Overall Yearly Perfomance By Total Registered User'
                )
    st.plotly_chart(fig,use_container_width=True)


    fig = px.line(df_year_vis_user,
                x='Year',
                y='Total_AppOpen', 
                title='Overall Yearly Perfomance By Total App Usage'
                )
    st.plotly_chart(fig,use_container_width=True)
    st.write(df_year_vis_user)

    








# TRANSACTION DATA VISUALIZATION  

def transaction(type,year,quarter):
    qry_df = f"select c_state, sum(Count_transaction) as Total_Transactions, sum(amount) as Total_amount from map_trans where year = {year} and quarter = {quarter} group by c_state order by Total_amount desc;"
    qry_total_amount = f"select sum(total) from (select sum(Transaction_amount) as total from agg_trans where year = {year} and quarter = {quarter} group by state) as e;"
    qry_total_trans = f"select sum(total) from (select sum(Transaction_count) as total from agg_trans where year = {year} and quarter = {quarter} group by state) as e;"
    qry_trans_bycat = f"select Transaction_type, sum(Transaction_amount) as Total_amount, sum(Transaction_count) as total_tr from agg_trans where year = {year} and quarter = {quarter} group by Transaction_type;"

# mAP VISUALIZATION  
    mycursor.execute(qry_df)
    df = pd.DataFrame(mycursor.fetchall(),columns= ['State', 'Total_Transactions', 'Total_amount'])
    df.index += 1
    fig = px.choropleth(
        df,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='State',
        color='Total_amount',
        color_continuous_scale='Reds'
    )

    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig,use_container_width=True)
    df['Total_amount'] = df['Total_amount'].round(2)
    st.markdown("## :violet[Total Transaction Amount By State]")
    st.write(df)

# TOTAL AMOUNT SIDE BAR 
    mycursor.execute(qry_total_amount)
    tot_amount = "₹ {:,.2f}".format(mycursor.fetchall()[0][0])
    st.sidebar.header(':violet[Total Amount of Transaction]')
    st.sidebar.title(tot_amount)

# TOTAL TRANS SIDE BAR 
    mycursor.execute(qry_total_trans)
    tot_trans = "{:,}".format(mycursor.fetchall()[0][0])
    st.sidebar.header(':violet[Total Transactions]')
    st.sidebar.title(tot_trans)

# TRANSACTION BY CATAGORY
    mycursor.execute(qry_trans_bycat)
    df_trans_bycat = pd.DataFrame(mycursor.fetchall(),columns= ['Category', 'Amount','Transactions'])
    df_trans_bycat['Amount'] = df_trans_bycat['Amount'].round(2)
    df_trans_bycat.index += 1
    
    st.header(':violet[Amount By Category]')
    st.write(df_trans_bycat)
    fig = px.pie(df_trans_bycat, values='Amount',
                        names='Category',
                        title='Amount By Category',
                        color_discrete_sequence=px.colors.sequential.Agsunset,
                        hover_data=['Category'],
                        labels={'Category':'Category'})
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig,use_container_width=True)

# TOP AND BOTTOM FILTER BARCHART
    top10 = st.selectbox('Filter',
                                  ("Top 10 State",
                                   "Bottom 10 State",
                                   "Top 10 District",
                                   "Bottom 10 District",
                                   "Top 10 Pincode",
                                   "Bottom 10 Pincode"
                                   ),
                                   key='top10')

    if top10 == "Top 10 State":
        qry_t10_state = f"select c_state, sum(Count_transaction) as Total_Transactions, sum(amount) as Total_amount from map_trans where year = {year} and quarter = {quarter} group by c_state order by Total_amount desc limit 10;"
        mycursor.execute(qry_t10_state)
        df_qry_t10_state = pd.DataFrame(mycursor.fetchall(),columns= ['State', 'Total_Transactions', 'Total_amount'])
        df_qry_t10_state['Total_amount'] = df_qry_t10_state['Total_amount'].round(2)
        df_qry_t10_state.index += 1
        fig = px.bar(df_qry_t10_state,
                        title='Top 10',
                        x="State",
                        y="Total_amount",
                        orientation='v',
                        color_continuous_scale=px.colors.sequential.Agsunset)
        st.plotly_chart(fig,use_container_width=True)
        st.write(df_qry_t10_state)

    elif top10 == "Bottom 10 State":
        qry_b10_state = f"select c_state, sum(Count_transaction) as Total_Transactions, sum(amount) as Total_amount from map_trans where year = {year} and quarter = {quarter} group by c_state order by Total_amount asc limit 10;"
        mycursor.execute(qry_b10_state)
        df_qry_b10_state = pd.DataFrame(mycursor.fetchall(),columns= ['State', 'Total_Transactions', 'Total_amount'])
        df_qry_b10_state['Total_amount'] = df_qry_b10_state['Total_amount'].round(2)
        df_qry_b10_state.index += 1
        fig = px.bar(df_qry_b10_state,
                        title='Top 10',
                        x="State",
                        y="Total_amount",
                        orientation='v',
                        color_continuous_scale=px.colors.sequential.Agsunset)
        st.plotly_chart(fig,use_container_width=True)
        st.write(df_qry_b10_state)

    elif top10 == "Top 10 District":
        qry_t10_dis = f"select District, sum(Count_transaction) as Total_Transactions, sum(amount) as Total_amount from map_trans where year = {year} and quarter = {quarter} group by District order by Total_amount desc limit 10;"
        mycursor.execute(qry_t10_dis)
        df_qry_t10_dis = pd.DataFrame(mycursor.fetchall(),columns= ['District', 'Total_Transactions', 'Total_amount'])
        df_qry_t10_dis['Total_amount'] = df_qry_t10_dis['Total_amount'].round(2)
        df_qry_t10_dis += 1
        fig = px.bar(df_qry_t10_dis,
                        title='Top 10',
                        x="District",
                        y="Total_amount",
                        orientation='v',
                        color_continuous_scale=px.colors.sequential.Agsunset)
        st.plotly_chart(fig,use_container_width=True)
        st.write(df_qry_t10_dis)

    elif top10 == "Bottom 10 District":
        qry_b10_dis = f"select District, sum(Count_transaction) as Total_Transactions, sum(amount) as Total_amount from map_trans where year = {year} and quarter = {quarter} group by District order by Total_amount asc limit 10;"
        mycursor.execute(qry_b10_dis)
        df_qry_b10_dis = pd.DataFrame(mycursor.fetchall(),columns= ['District', 'Total_Transactions', 'Total_amount'])
        df_qry_b10_dis['Total_amount'] = df_qry_b10_dis['Total_amount'].round(2)
        df_qry_b10_dis += 1
        fig = px.bar(df_qry_b10_dis,
                        title='Top 10',
                        x="District",
                        y="Total_amount",
                        orientation='v',
                        color_continuous_scale=px.colors.sequential.Agsunset)
        st.plotly_chart(fig,use_container_width=True)
        st.write(df_qry_b10_dis)

    elif top10 == "Top 10 Pincode":
        qry_t10_pin = f"select Pincode, sum(Transaction_Count) as Total_Transactions, sum(Transaction_amount) as Total_amount from top_trans where year = {year} and quarter = {quarter} group by Pincode order by Total_amount desc limit 10;"
        mycursor.execute(qry_t10_pin)
        df_qry_t10_pin = pd.DataFrame(mycursor.fetchall(),columns= ['Pincode', 'Total_Transactions', 'Total_amount'])
        df_qry_t10_pin['Total_amount'] = df_qry_t10_pin['Total_amount'].round(2)
        df_qry_t10_pin['Pincode'] = [f'Pin {item['Pincode']}' for i,item in df_qry_t10_pin.iterrows()]
        df_qry_t10_pin.index += 1
        fig = px.bar(df_qry_t10_pin,
                        title='Top 10',
                        x="Pincode",
                        y="Total_amount",
                        orientation='v',
                        color_continuous_scale=px.colors.sequential.Agsunset)
        st.plotly_chart(fig,use_container_width=True)
        st.write(df_qry_t10_pin)
    
    elif top10 == "Bottom 10 Pincode":
        qry_b10_pin = f"select Pincode, sum(Transaction_Count) as Total_Transactions, sum(Transaction_amount) as Total_amount from top_trans where year = {year} and quarter = {quarter} group by Pincode order by Total_amount asc limit 10;"
        mycursor.execute(qry_b10_pin)
        df_qry_b10_pin = pd.DataFrame(mycursor.fetchall(),columns= ['Pincode', 'Total_Transactions', 'Total_amount'])
        df_qry_b10_pin['Total_amount'] = df_qry_b10_pin['Total_amount'].round(2)
        df_qry_b10_pin['Pincode'] = [f'Pin {item['Pincode']}' for i,item in df_qry_b10_pin.iterrows()]
        df_qry_b10_pin.index += 1
        fig = px.bar(df_qry_b10_pin,
                        title='Top 10',
                        x="Pincode",
                        y="Total_amount",
                        orientation='v',
                        color_continuous_scale=px.colors.sequential.Agsunset)
        st.plotly_chart(fig,use_container_width=True)
        st.write(df_qry_b10_pin)

    year_vis = f"select year, sum(Transaction_Count) as Total_Transactions, sum(Transaction_amount) as Total_amount from agg_trans group by year order by year asc;"
    mycursor.execute(year_vis)
    df_year_vis = pd.DataFrame(mycursor.fetchall(),columns= ['Year', 'Total_Transactions', 'Total_Amount'])
    df_year_vis['Total_Amount'] = df_year_vis['Total_Amount'].round()
    df_year_vis.index += 1
    fig = px.line(df_year_vis,
                x='Year',
                y='Total_Amount', 
                title='Overall Yearly Perfomance By Total Amount'
                )
    st.plotly_chart(fig,use_container_width=True)
    fig = px.line(df_year_vis,
                x='Year',
                y='Total_Transactions', 
                title='Overall Yearly Perfomance By Trasactions'
                )
    st.plotly_chart(fig,use_container_width=True)
    st.write(df_year_vis)




if options == "Transaction":
    transaction(options,year,quarter)
else:
    user(options,year,quarter)



