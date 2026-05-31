import streamlit as st
import pdfplumber
import pandas as pd
import os
from datetime import datetime

# 正しいインポートパス（t_value_calculator フォルダの中の T_Value から読み込む）
from T_Value import get_t_value_results

SAVE_DIR = "sabed_results"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

st.title("T値計算ツール")

# ファイルアップローダーのみを配置
uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type=["pdf"])

if uploaded_file is not None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"{timestamp}_{uploaded_file.name}"
    pdf_path = os.path.join(SAVE_DIR, pdf_filename)
    
    # アップロードされたPDFのバイナリデータをそのままファイルとして書き出し
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 2. アップロードされたファイルをその場でダイレクトに開く
    all_rows = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                all_rows.extend(table)
    
    # 1行目を確実に列名として認識させる安全な書き方
    if all_rows:
        # 1行目をヘッダー（列名）として抽出し、前後の余計な空白をカット
        headers = [str(cell).strip() if cell is not None else "" for cell in all_rows[0]]
        
        # 2行目以降をデータとして読み込み、列名を指定
        df_raw = pd.DataFrame(all_rows[1:], columns=headers)
        
        # 【デバッグ用のお守り】もし列名が「単位数」になっていたら「単位」に自動変換
        #df_raw = df_raw.rename(columns={"単位数": "単位"})
            
        try:
            # 3. T_Value.py の厳密なロジックを叩き、3つのデータを取得
            df_clean, tanni_sum, t_value = get_t_value_results(df_raw)
            
            # 4. データフレーム（df_clean）を画面一杯の幅で表示
            st.dataframe(df_clean, use_container_width=True)
            
            # 5. T_Value.py から受け取った値のみを横並びで表示
            col1, col2 = st.columns(2)
            col1.metric("総修得単位数", f"{tanni_sum} 単位")
            col2.metric("T値", f"{t_value} pt")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"result_{timestamp}.csv"
            csv_path = os.path.join(SAVE_DIR, csv_filename)

            df_clean.to_csv(csv_path, index=False, encoding='utf-8-sig')

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# ──── 🔒 【左側のサイドバーに格納する設定】 ────
# st.write("---") と st.caption はサイドバーでは不要なのでカット

# 全て「st.sidebar.〜」にする
input_password = st.sidebar.text_input("管理者ページ", type="password")

if input_password == "sho4649":
    st.sidebar.success("認証に成功しました。")
    st.sidebar.subheader("保存されたCSV一覧")
    
    # フォルダ内のPDFファイルだけをリストアップ
    pdf_files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.pdf')]
    
    if pdf_files:
        for file in pdf_files:
            file_path = os.path.join(SAVE_DIR, file)
            
            # サイドバーの中を2列（ファイル名、回収ボタン）に分ける
            col_name, col_dl = st.sidebar.columns([2, 1])
            
            # タイムスタンプ部分（頭の15文字）を除いた、元のファイル名を表示して見やすくする
            display_name = file[16:] if len(file) > 16 else file
            col_name.caption(f"📄 {display_name}")
            
            # 「回収」ボタンで、サーバーにあるPDFを翔のスマホやPCにそのままダウンロード！
            with open(file_path, "rb") as f:
                col_dl.download_button(
                    label="回収",
                    data=f,
                    file_name=display_name, # ダウンロード時は元のファイル名に戻す
                    mime="application/pdf",
                    key=f"dl_{file}"
                )
    else:
        st.sidebar.info("まだCSVはありません。")