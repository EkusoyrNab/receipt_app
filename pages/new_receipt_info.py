import streamlit as st
from utils import get_shop_categories, get_shop_names
from utils import check_login

check_login()
st.set_page_config(page_title="基本情報登録", layout="wide")
st.title("📝 レシート基本情報登録")

if "receipt_info" not in st.session_state:
    st.session_state["receipt_info"] = {}

date = st.date_input("購入日")

shop_categories = get_shop_categories()
category = st.selectbox("店カテゴリ", shop_categories + ["新規追加"])
if category == "新規追加":
    category = st.text_input("新しい店カテゴリを入力", "")

shop_names = get_shop_names()
shop = st.selectbox("店名", shop_names + ["新規追加"])
if shop == "新規追加":
    shop = st.text_input("新しい店名を入力", "")

if st.button("次へ"):
    st.session_state["receipt_info"] = {
        "date": date,
        "shop_category": category,
        "shop_name": shop
    }
    st.switch_page("pages/new_receipt_items.py")
