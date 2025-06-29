import streamlit as st
import pandas as pd
import sqlite3
from utils import DB_PATH
from utils import check_login

check_login()
st.set_page_config(page_title="レシート編集", layout="wide")

# 編集IDがない場合はストップ
if "edit_receipt_id" not in st.session_state or not st.session_state["edit_receipt_id"]:
    st.warning("編集するレシートが選択されていません。")
    st.stop()

receipt_id = st.session_state["edit_receipt_id"]
receipt_label = st.session_state.get("edit_receipt_label", receipt_id)

st.title(f"✏️ レシート編集 - {receipt_label}")

# DB から既存データ取得
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM receipts WHERE receipt_id = ?", conn, params=(receipt_id,))
conn.close()

# 基本情報
shop_category = df["shop_category"].iloc[0]
shop_name = df["shop_name"].iloc[0]
date = pd.to_datetime(df["date"].iloc[0])

st.write("## 基本情報")
date = st.date_input("購入日", value=date)
shop_category = st.text_input("店カテゴリ", value=shop_category)
shop_name = st.text_input("店名", value=shop_name)

# 商品情報
st.write("## 商品情報（表編集）")
items_df = df[["item_category", "item_name", "price"]].copy()
items_df.columns = ["商品カテゴリ", "商品名", "価格"]

edited_df = st.data_editor(
    items_df,
    num_rows="dynamic",
    use_container_width=True,
    key="edit_items"
)

# 更新ボタン
if st.button("更新完了"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM receipts WHERE receipt_id = ?", (receipt_id,))
    conn.commit()

    for _, row in edited_df.iterrows():
        if row["商品カテゴリ"] == "" and row["商品名"] == "" and row["価格"] == 0:
            continue
        c.execute('''
            INSERT INTO receipts (receipt_id, date, shop_category, shop_name, item_category, item_name, price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            receipt_id,
            date.strftime("%Y-%m-%d"),
            shop_category,
            shop_name,
            row["商品カテゴリ"],
            row["商品名"],
            int(row["価格"])
        ))
    conn.commit()
    conn.close()

    st.session_state["edit_receipt_id"] = None
    st.session_state["edit_receipt_label"] = None
    st.success("更新が完了しました！")
    st.switch_page("app.py")
