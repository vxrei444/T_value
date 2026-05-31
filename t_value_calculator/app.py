import streamlit as st
import pdfplumber
import pandas as pd

# T_Value.py から関数をインポート
from t_value_calculator.T_Value import get_t_value_results

# ファイルアップローダーのみを配置
uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type=["pdf"])

if uploaded_file is not None:
    # 2. アップロードされたファイルをその場でダイレクトに開く（ダウンロード処理は不要）
    all_rows = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                all_rows.extend(table)
    
# ◯ 修正後（1行目を確実に列名として認識させる安全な書き方）
if all_rows:
    # 1行目をヘッダー（列名）として抽出し、前後の余計な空白をカット
    headers = [str(cell).strip() if cell is not None else "" for cell in all_rows[0]]
    
    # 2行目以降をデータとして読み込み、列名を指定
    df_raw = pd.DataFrame(all_rows[1:], columns=headers)
    
    # 【デバッグ用のお守り】もし列名が「単位数」になっていたら「単位」に自動変換
    df_raw = df_raw.rename(columns={"単位数": "単位"})
        
    try:
            # 3. T_Value.py の厳密なロジックを叩き、3つのデータを取得
            # （中で int型 へのキャストや不要行のカットが完結している前提）
            df_clean, tanni_sum, t_value = get_t_value_results(df_raw)
            
            # 4. データフレーム（df_t）を画面一杯の幅で表示
            st.dataframe(df_clean, use_container_width=True)
            
            # 5. T_Value.py から受け取った値のみを横並びで表示
            col1, col2 = st.columns(2)
            col1.metric("総修得単位数", f"{tanni_sum} 単位")
            col2.metric("T値", f"{t_value} pt")
            
    except Exception as e:
            st.error(f"エラーが発生しました: {e}")