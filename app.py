import streamlit as st
import pandas as pd
import plotly.express as px
import bcrypt
import time
from utils import (
    init_db,
    get_receipts_by_month,
    get_total_by_month,
    get_category_summary,
    get_receipt_details,
    delete_receipt
)

st.set_page_config(page_title="レシート管理", layout="wide")

# --- 固定ユーザー情報（ハッシュ化済みパスワード） ---
USER_CREDENTIALS = {
    "kaimonojouzu": "$2b$12$cPwRgJbwZ3jL1Uf5iPlCOefFJbLwtZYptaUS598Fiyk8B8jMOqB6e"
}

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- セッションタイムアウト（30分） ---
if st.session_state["authenticated"]:
    last_login_time = st.session_state.get("login_time", 0)
    current_time = time.time()
    if current_time - last_login_time > 1800:
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.session_state["login_time"] = None
        st.warning("セッションの有効期限が切れました。再度ログインしてください。")
    else:
        st.session_state["login_time"] = current_time

if st.session_state.get("force_refresh", False):
    st.session_state["force_refresh"] = False

# --- ログイン画面 ---
if not st.session_state["authenticated"]:
    st.title("ログイン")

    username = st.text_input("ユーザー名", key="login_username")
    password = st.text_input("パスワード", type="password", key="login_password")
    login_button = st.button("ログイン")

    if login_button:
        if username in USER_CREDENTIALS:
            hashed_pw = USER_CREDENTIALS[username]
            if bcrypt.checkpw(password.encode(), hashed_pw.encode()):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["login_time"] = time.time()
                st.success(f"ようこそ、{username} さん！")
                st.session_state["force_refresh"] = True
            else:
                st.error("パスワードが間違っています")
        else:
            st.error("ユーザー名が間違っています")

else:
    st.sidebar.write(f"ログイン中: {st.session_state['username']} さん")
    if st.sidebar.button("ログアウト"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.session_state["login_time"] = None
        st.experimental_rerun()

    # --- アプリ本体 -----------------
    st.title("🧾 レシート管理アプリ")

    init_db()

    current_year = pd.Timestamp.now().year
    years = list(range(2020, current_year + 1))
    year = st.sidebar.selectbox("年", options=years, index=len(years) - 1)

    months = list(range(1, 13))
    month = st.sidebar.selectbox("月", options=months, index=pd.Timestamp.now().month - 1)

    total = get_total_by_month(year, month)
    st.metric("合計出費額", f"{total:,} 円")

    category_df = get_category_summary(year, month)
    if not category_df.empty:
        st.subheader("カテゴリ別割合")
        fig = px.pie(
            category_df,
            values="total",
            names="category",
            title="カテゴリ別割合",
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("データがありません。")

    st.markdown(f"### {year}年 {month}月のレシート一覧")

    receipts_df = get_receipts_by_month(year, month)
    if receipts_df.empty:
        st.write("レシートが登録されていません。")
    else:
        summary_list = []
        for rid, group in receipts_df.groupby("receipt_id"):
            summary_list.append({
                "レシートID": rid,
                "店名": group["shop_name"].iloc[0],
                "購入日": group["date"].iloc[0],
                "合計金額": group["price"].sum()
            })
        summary_df = pd.DataFrame(summary_list)

        for idx, row in summary_df.iterrows():
            st.write(f"#### {row['店名']} - {row['購入日']} - 合計: {row['合計金額']:,} 円")
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("参照", key=f"view_{row['レシートID']}"):
                    details_df = get_receipt_details(row['レシートID'])
                    st.write("商品一覧（プレビュー）")
                    st.table(details_df)

            with col2:
                if st.button("編集", key=f"edit_{row['レシートID']}"):
                    st.session_state["edit_receipt_id"] = row['レシートID']
                    st.session_state["edit_receipt_label"] = f"{row['店名']} ({row['購入日']})"
                    st.switch_page("pages/edit_receipt.py")

            with col3:
                if st.button("削除", key=f"delete_{row['レシートID']}"):
                    if st.confirm(f"このレシートを削除しますか？（ID: {row['レシートID']}）"):
                        delete_receipt(row['レシートID'])
                        st.success("削除が完了しました。")
                        st.rerun()

    if st.button("新規登録"):
        st.switch_page("pages/new_receipt_info.py")
