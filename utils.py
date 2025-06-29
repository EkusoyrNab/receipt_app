import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st
import time

DB_PATH = "data/receipts.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id TEXT,
            date TEXT,
            shop_category TEXT,
            shop_name TEXT,
            item_category TEXT,
            item_name TEXT,
            price INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_receipt(date, shop_category, shop_name, items):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    receipt_id = datetime.now().strftime("%Y%m%d%H%M%S")
    for item in items:
        c.execute('''
            INSERT INTO receipts (receipt_id, date, shop_category, shop_name, item_category, item_name, price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (receipt_id, date.strftime("%Y-%m-%d"), shop_category, shop_name, item["category"], item["name"], item["price"]))
    conn.commit()
    conn.close()

def get_receipts_by_month(year, month):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM receipts", conn, parse_dates=["date"])
    conn.close()
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    return df[(df["year"] == year) & (df["month"] == month)]

def get_total_by_month(year, month):
    df = get_receipts_by_month(year, month)
    return df["price"].sum()

def get_category_summary(year, month):
    df = get_receipts_by_month(year, month)
    if df.empty:
        return pd.DataFrame()
    summary = df.groupby("shop_category")["price"].sum().reset_index().rename(columns={"price": "total", "shop_category": "category"})
    return summary

def get_shop_categories():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT DISTINCT shop_category FROM receipts", conn)
    conn.close()
    return df["shop_category"].dropna().tolist()

def get_shop_names():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT DISTINCT shop_name FROM receipts", conn)
    conn.close()
    return df["shop_name"].dropna().tolist()

def get_receipt_details(receipt_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT item_category, item_name, price FROM receipts WHERE receipt_id = ?", conn, params=(receipt_id,))
    conn.close()
    return df

def delete_receipt(receipt_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM receipts WHERE receipt_id = ?", (receipt_id,))
    conn.commit()
    conn.close()

def get_item_categories():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT DISTINCT item_category FROM receipts", conn)
    conn.close()
    return df["item_category"].dropna().tolist()


def check_login():
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.switch_page("app.py")
    else:
        last_login_time = st.session_state.get("login_time", 0)
        current_time = time.time()

        if current_time - last_login_time > 1800:  # 30分
            st.session_state["authenticated"] = False
            st.session_state["username"] = ""
            st.session_state["login_time"] = None
            st.warning("セッションの有効期限が切れました。再度ログインしてください。")
            st.switch_page("app.py")
        else:
            # ログイン更新（アクションあるたびにリセット）
            st.session_state["login_time"] = current_time
