import streamlit as st
from utils import get_receipt, update_receipt

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("ログインしてください")
    st.stop()

receipt_id = st.session_state.get("edit_receipt_id", None)

if not receipt_id:
    st.error("編集対象が選択されていません。")
    st.stop()

receipt_df = get_receipt(receipt_id)
if receipt_df.empty:
    st.error("該当レシートが存在しません。")
    st.stop()

data = receipt_df.iloc[0]

st.title("レシート編集")

date = st.date_input("購入日", value=pd.to_datetime(data["date"]))
shop_category = st.text_input("店カテゴリ", value=data["shop_category"])
shop_name = st.text_input("店名", value=data["shop_name"])
total = st.number_input("合計金額", value=int(data["total"]), min_value=0, step=100)

if st.button("更新"):
    update_receipt(receipt_id, str(date), shop_category, shop_name, int(total))
    st.success("レシートが更新されました！")
    st.switch_page("app.py")
