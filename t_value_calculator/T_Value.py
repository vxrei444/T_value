import numpy as np
import pandas as pd
from pandas import DataFrame

def get_t_value_results(df_raw):
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    df = DataFrame(df_raw)
    df_t = df[["科目","単位数","評価"]].copy()
    df_t["単位数"] = df_t["単位数"].astype(str).str.strip()
    df_t["評価"] = df_t["評価"].astype(str).str.strip()
    score_map = {
        "Ｓ": 7, "A": 6, "Ａ": 6, "Ｂ": 3, "Ｃ": 1, "Ｄ": 0,
        "S": 7, "B": 3, "C": 1, "D": 0
    }
    df_t["評価"] = df_t["評価"].map(score_map)

    df_t["単位数"] = pd.to_numeric(df_t["単位数"], errors='coerce')
    df_t["評価"] = pd.to_numeric(df_t["評価"], errors='coerce')

    df_t = df_t.dropna(subset=["単位数", "評価"])
    df_t["単位数"] = df_t["単位数"].astype(float)
    df_t["評価"] = df_t["評価"].astype(float)
    df_t["point"] = df_t["単位数"]*df_t["評価"]

    tanni_sum = int(df_t["単位数"].sum())
    t_value = int(df_t["point"].sum())

    return df_t ,tanni_sum, t_value
