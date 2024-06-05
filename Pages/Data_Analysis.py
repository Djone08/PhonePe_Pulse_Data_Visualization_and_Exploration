import streamlit as st
import pandas as pd
import plotly.express as px
from Main import set_creds


db = set_creds()

ques = st.selectbox("**Select the Question**",
                    ['Top Brands Of Mobiles Used', 'States With Lowest Transaction Amount',
                     'Districts With Highest Transaction Amount', 'Top 10 Districts With Lowest Transaction Amount',
                     'Top 10 States With AppOpens', 'Least 10 States With AppOpens',
                     'States With Lowest Transaction Count',
                     'States With Highest Transaction Count', 'States With Highest Transaction Amount',
                     'Top 50 Districts With Lowest Transaction Amount'])

Aggre_user = db.fetch_data('select * from aggregated_user')
Aggre_transaction = db.fetch_data('select * from aggregated_transaction')
Map_user = db.fetch_data('select * from map_user')
Map_transaction = db.fetch_data('select * from map_transaction')


if ques == "Top Brands Of Mobiles Used":
    brand = Aggre_user[["user_brand", "user_count"]]
    brand1 = brand.groupby(["user_brand"])["user_count"].sum().sort_values(ascending=False)
    brand2 = pd.DataFrame(brand1).reset_index()

    fig_brands = px.pie(brand2, values="user_count", names="user_brand",
                        color_discrete_sequence=px.colors.sequential.dense_r,
                        title="Top Mobile Brands of trans_count")
    st.plotly_chart(fig_brands)

elif ques == "States With Lowest Transaction Amount":
    lt = Aggre_transaction[["state", "trans_amount"]]
    lt1 = lt.groupby(["state"])["trans_amount"].sum().sort_values(ascending=True)
    lt2 = pd.DataFrame(lt1).reset_index().head(10)

    fig_lts = px.bar(lt2, x="state", y="trans_amount", title="LOWEST TRANSACTION AMOUNT and STATES",
                     color_discrete_sequence=px.colors.sequential.Oranges_r)
    st.plotly_chart(fig_lts)

elif ques == "Districts With Highest Transaction Amount":
    htd = Map_transaction[["district", "trans_amount"]]
    htd1 = htd.groupby("district")["trans_amount"].sum().sort_values(ascending=False)
    htd2 = pd.DataFrame(htd1).head(10).reset_index()

    fig_htd = px.pie(htd2, values="trans_amount", names="district",
                     title="TOP 10 DISTRICTS OF HIGHEST TRANSACTION AMOUNT",
                     color_discrete_sequence=px.colors.sequential.Emrld_r)
    st.plotly_chart(fig_htd)

elif ques == "Top 10 Districts With Lowest Transaction Amount":
    htd = Map_transaction[["district", "trans_amount"]]
    htd1 = htd.groupby("district")["trans_amount"].sum().sort_values(ascending=True)
    htd2 = pd.DataFrame(htd1).head(10).reset_index()

    fig_htd = px.pie(htd2, values="trans_amount", names="district",
                     title="TOP 10 DISTRICTS OF LOWEST TRANSACTION AMOUNT",
                     color_discrete_sequence=px.colors.sequential.Greens_r)
    st.plotly_chart(fig_htd)

elif ques == "Top 10 States With AppOpens":
    sa = Map_user[["state", "user_opens"]]
    sa1 = sa.groupby("state")["user_opens"].sum().sort_values(ascending=False)
    sa2 = pd.DataFrame(sa1).reset_index().head(10)

    fig_sa = px.bar(sa2, x="state", y="user_opens", title="Top 10 state With AppOpens",
                    color_discrete_sequence=px.colors.sequential.deep_r)
    st.plotly_chart(fig_sa)

elif ques == "Least 10 States With AppOpens":
    sa = Map_user[["state", "user_opens"]]
    sa1 = sa.groupby("state")["user_opens"].sum().sort_values(ascending=True)
    sa2 = pd.DataFrame(sa1).reset_index().head(10)

    fig_sa = px.bar(sa2, x="state", y="user_opens", title="lowest 10 state With AppOpens",
                    color_discrete_sequence=px.colors.sequential.dense_r)
    st.plotly_chart(fig_sa)

elif ques == "States With Lowest Transaction Count":
    stc = Aggre_transaction[["state", "trans_count"]]
    stc1 = stc.groupby("state")["trans_count"].sum().sort_values(ascending=True)
    stc2 = pd.DataFrame(stc1).reset_index()

    fig_stc = px.bar(stc2, x="state", y="trans_count", title="STATES WITH LOWEST TRANSACTION COUNT",
                     color_discrete_sequence=px.colors.sequential.Jet_r)
    st.plotly_chart(fig_stc)

elif ques == "States With Highest Transaction Count":
    stc = Aggre_transaction[["state", "trans_count"]]
    stc1 = stc.groupby("state")["trans_count"].sum().sort_values(ascending=False)
    stc2 = pd.DataFrame(stc1).reset_index()

    fig_stc = px.bar(stc2, x="state", y="trans_count", title="STATES WITH HIGHEST TRANSACTION COUNT",
                     color_discrete_sequence=px.colors.sequential.Magenta_r)
    st.plotly_chart(fig_stc)

elif ques == "States With Highest Transaction Amount":
    ht = Aggre_transaction[["state", "trans_amount"]]
    ht1 = ht.groupby("state")["trans_amount"].sum().sort_values(ascending=False)
    ht2 = pd.DataFrame(ht1).reset_index().head(10)

    fig_lts = px.bar(ht2, x="state", y="trans_amount", title="HIGHEST TRANSACTION AMOUNT and STATES",
                     color_discrete_sequence=px.colors.sequential.Oranges_r)
    st.plotly_chart(fig_lts)

elif ques == "Top 50 Districts With Lowest Transaction Amount":
    dt = Map_transaction[["district", "trans_amount"]]
    dt1 = dt.groupby("district")["trans_amount"].sum().sort_values(ascending=True)
    dt2 = pd.DataFrame(dt1).reset_index().head(50)

    fig_dt = px.bar(dt2, x="district", y="trans_amount", title="DISTRICTS WITH LOWEST TRANSACTION AMOUNT",
                    color_discrete_sequence=px.colors.sequential.Mint_r)
    st.plotly_chart(fig_dt)

