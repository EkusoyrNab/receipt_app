import streamlit as st
from utils import add_receipt, get_shop_categories, get_shop_names

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("ログインしてください")
    st.stop()

st.title("新規レシート登録")

date = st.date_input("購入日")

# 店カテゴリ
categories = get_shop_categories()
shop_category = st.selectbox("店カテゴリ（新規の場合は直接入力）", options=["新規入力"] + categories)
if shop_category == "新規入力":
    shop_category = st.text_input("新しい店カテゴリ")

# 店名
names = get_shop_names()
shop_name = st.selectbox("店名（新規の場合は直接入力）", options=["新規入力"] + names)
if shop_name == "新規入力":
    shop_name = st.text_input("新しい店名")

total = st.number_input("合計金額", min_value=0, step=100)

if st.button("登録"):
    add_receipt(str(date), shop_category, shop_name, int(total))
    st.success("レシートが登録されました！")
    st.switch_page("app.py")
