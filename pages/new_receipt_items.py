import streamlit as st
import pandas as pd
from utils import save_receipt, get_item_categories
from utils import check_login

check_login()
st.set_page_config(page_title="商品登録", layout="wide")
st.title("🛒 商品登録")

# 基本情報確認
if "receipt_info" not in st.session_state or not st.session_state["receipt_info"]:
    st.warning("まず基本情報を入力してください。")
    st.stop()

# 商品表データ
if "items_df" not in st.session_state:
    st.session_state["items_df"] = pd.DataFrame(columns=["商品カテゴリ", "商品名", "価格"])

# 再描画用フラグ
if "rerun_flag" not in st.session_state:
    st.session_state["rerun_flag"] = False

st.write("### 商品一覧（表編集）")

existing_categories = get_item_categories()

new_category = st.selectbox("商品カテゴリ", existing_categories + ["新規追加"])
if new_category == "新規追加":
    new_category = st.text_input("新しい商品カテゴリを入力", "")

new_name = st.text_input("商品名")
new_price = st.number_input("価格", min_value=0, value=0, step=1)

if st.button("商品を追加"):
    new_row = pd.DataFrame([{"商品カテゴリ": new_category, "商品名": new_name, "価格": new_price}])
    st.session_state["items_df"] = pd.concat([st.session_state["items_df"], new_row], ignore_index=True)
    # フラグをトグルして再描画を強制
    st.session_state["rerun_flag"] = not st.session_state["rerun_flag"]

# 表を表示
st.data_editor(
    st.session_state["items_df"],
    num_rows="dynamic",
    use_container_width=True,
    key="new_items"
)

if st.button("登録完了"):
    items = []
    for _, row in st.session_state["items_df"].iterrows():
        if row["商品カテゴリ"] == "" and row["商品名"] == "" and row["価格"] == 0:
            continue
        items.append({
            "category": row["商品カテゴリ"],
            "name": row["商品名"],
            "price": row["価格"]
        })
    if not items:
        st.warning("商品が1つも登録されていません。")
    else:
        info = st.session_state["receipt_info"]
        save_receipt(info["date"], info["shop_category"], info["shop_name"], items)
        st.session_state["items_df"] = pd.DataFrame(columns=["商品カテゴリ", "商品名", "価格"])
        st.session_state["receipt_info"] = {}
        st.success("登録が完了しました！")
        st.switch_page("app.py")
