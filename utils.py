import sqlite3
import pandas as pd
import uuid

DB_PATH = "receipts.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # receipts テーブル
    c.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            receipt_id TEXT,
            date TEXT,
            shop_category TEXT,
            shop_name TEXT,
            total INTEGER
        )
    ''')

    # shop_categories テーブル
    c.execute('''
        CREATE TABLE IF NOT EXISTS shop_categories (
            name TEXT PRIMARY KEY
        )
    ''')

    # shop_names テーブル
    c.execute('''
        CREATE TABLE IF NOT EXISTS shop_names (
            name TEXT PRIMARY KEY
        )
    ''')

    conn.commit()
    conn.close()

def add_receipt(date, shop_category, shop_name, total):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    receipt_id = str(uuid.uuid4())

    # レシート追加
    c.execute('''
        INSERT INTO receipts (receipt_id, date, shop_category, shop_name, total)
        VALUES (?, ?, ?, ?, ?)
    ''', (receipt_id, date, shop_category, shop_name, total))

    # shop_category 保存
    c.execute("INSERT OR IGNORE INTO shop_categories (name) VALUES (?)", (shop_category,))
    # shop_name 保存
    c.execute("INSERT OR IGNORE INTO shop_names (name) VALUES (?)", (shop_name,))

    conn.commit()
    conn.close()

def get_shop_categories():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT name FROM shop_categories", conn)
    conn.close()
    return df["name"].tolist()

def get_shop_names():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT name FROM shop_names", conn)
    conn.close()
    return df["name"].tolist()

# 他の関数（get_receipts_by_month など）は前のまま


def get_receipts_by_month(year, month):
    conn = sqlite3.connect(DB_PATH)
    query = f"""
        SELECT * FROM receipts
        WHERE strftime('%Y', date) = '{year}' AND strftime('%m', date) = '{month:02d}'
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_total_by_month(year, month):
    df = get_receipts_by_month(year, month)
    return df["total"].sum() if not df.empty else 0

def get_category_summary(year, month):
    df = get_receipts_by_month(year, month)
    if df.empty:
        return pd.DataFrame()
    return df.groupby("shop_category")["total"].sum().reset_index(name="total")

def get_receipt(receipt_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM receipts WHERE receipt_id = ?", conn, params=(receipt_id,))
    conn.close()
    return df

def update_receipt(receipt_id, date, shop_category, shop_name, total):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE receipts
        SET date = ?, shop_category = ?, shop_name = ?, total = ?
        WHERE receipt_id = ?
    ''', (date, shop_category, shop_name, total, receipt_id))
    conn.commit()
    conn.close()

def delete_receipt(receipt_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM receipts WHERE receipt_id = ?", (receipt_id,))
    conn.commit()
    conn.close()
