import streamlit as st
from utils import add_receipt

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("ログインしてください")
    st.stop()

st.title("新規レシート登録")

date = st.date_input("購入日")
shop_category = st.text_input("店カテゴリ")
shop_name = st.text_input("店名")
total = st.number_input("合計金額", min_value=0, step=100)

if st.button("登録"):
    add_receipt(str(date), shop_category, shop_name, int(total))
    st.success("レシートが登録されました！")
    st.switch_page("app.py")
