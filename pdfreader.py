import pdfplumber
import pandas as pd

# 引数はパス（文字列）ではなく、アップロードされたファイルオブジェクトを受け取る
def extract_pdf_table(uploaded_file):
    all_tables = []
    
    # パスを開く代わりに、アップロードされたファイルをそのまま開く！
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                df_page = pd.DataFrame(table)
                all_tables.append(df_page)
                
    if all_tables:
        final_df = pd.concat(all_tables, ignore_index=True)
        final_df.columns = final_df.iloc[0]
        return final_df[1:]
    return None