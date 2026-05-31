import numpy as np
import pandas as pd
from pandas import DataFrame

def get_t_value_results(df):
    # 日本語の全角文字（漢字・ひらがな）の幅を正しく計算して表示を揃える設定
    pd.set_option('display.unicode.east_asian_width', True)

    # ついでに列が途中で折り返されないようにする設定（必要に応じて）
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    data = pd.read_csv('output.csv')
    df = DataFrame(data)

    df_t = df[["科目","単位数","評価"]].copy()

    # 2. 前後の空白を削除
    df_t["単位数"] = df_t["単位数"].astype(str).str.strip()
    df_t["評価"] = df_t["評価"].astype(str).str.strip()

    # 3. 評価を数値にマッピング
    score_map = {
        "Ｓ": 7, "A": 6, "Ａ": 6, "Ｂ": 3, "Ｃ": 1, "Ｄ": 0,
        "S": 7, "B": 3, "C": 1, "D": 0
    }
    df_t["評価"] = df_t["評価"].map(score_map)

    # 4. 【ココが重要】「単位数」と「評価」を数値に強制変換！
    # errors='coerce' をつけると、空欄 '' や変換できなかったゴミが自動的に「NaN」になる
    df_t["単位数"] = pd.to_numeric(df_t["単位数"], errors='coerce')
    df_t["評価"] = pd.to_numeric(df_t["評価"], errors='coerce')

    df_t = df_t.dropna(subset=["単位数", "評価"])


    df_t["単位数"] = df_t["単位数"].astype(float)
    df_t["評価"] = df_t["評価"].astype(float)

    df_t["point"] = df_t["単位数"]*df_t["評価"]

    tanni_sum = int(df_t["単位数"].sum())
    t_value = int(df_t["point"].sum())

    return df_t ,tanni_sum, t_value
