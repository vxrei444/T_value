import streamlit as st
import pdfplumber
import pandas as pd
import os
from datetime import datetime

from T_Value import get_t_value_results

SAVE_DIR = "sabed_results"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

st.title("T値計算ツール")


uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type=["pdf"])

if uploaded_file is not None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"{timestamp}_{uploaded_file.name}"
    pdf_path = os.path.join(SAVE_DIR, pdf_filename)
    
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    
    all_rows = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                all_rows.extend(table)
    if all_rows:
        headers = [str(cell).strip() if cell is not None else "" for cell in all_rows[0]]        
        df_raw = pd.DataFrame(all_rows[1:], columns=headers)

            
        try:
            df_clean, tanni_sum, t_value = get_t_value_results(df_raw)
            
            st.dataframe(df_clean, use_container_width=True)
            
            col1, col2 = st.columns(2)
            col1.metric("総修得単位数", f"{tanni_sum} 単位")
            col2.metric("T値", f"{t_value} pt")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"result_{timestamp}.csv"
            csv_path = os.path.join(SAVE_DIR, csv_filename)

            df_clean.to_csv(csv_path, index=False, encoding='utf-8-sig')

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")


input_password = st.sidebar.text_input("管理者ページ", type="password")

if input_password == st.secrets["ADMIN_PASSWORD"]:
    
    pdf_files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.pdf')]
    
    if pdf_files:
        for file in pdf_files:
            file_path = os.path.join(SAVE_DIR, file)
            col_name, col_dl = st.sidebar.columns([2, 1])
            display_name = file[16:] if len(file) > 16 else file
            col_name.caption(f"📄 {display_name}")
            
            with open(file_path, "rb") as f:
                col_dl.download_button(
                    label="回収",
                    data=f,
                    file_name=display_name,
                    mime="application/pdf",
                    key=f"dl_{file}"
                )
    else:
        st.sidebar.info("まだデータはありません。")