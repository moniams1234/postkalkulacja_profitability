import pandas as pd
from .helpers import find_col

def add_offset_costs(df_profit, df_farby):
    df_profit = df_profit.copy()
    if df_farby is None:
        df_profit["Offset inks"] = 0.0
        df_profit["Płyta offsetowa"] = 0.0
        return df_profit

    key = find_col(df_farby, ["Etykiety wierszy", "Etykieta wiersza"])
    ink = find_col(df_farby, ["Suma koszt farby2"])
    plate = find_col(df_farby, ["Suma koszt płyty", "Suma koszt plyty"])
    if not key:
        df_profit["Offset inks"] = 0.0
        df_profit["Płyta offsetowa"] = 0.0
        return df_profit

    tmp = df_farby.copy()
    tmp["_key"] = tmp[key].astype(str).str.strip()
    cols = ["_key"]
    if ink: cols.append(ink)
    if plate: cols.append(plate)
    tmp = tmp[cols].copy()
    if ink: tmp.rename(columns={ink: "Offset inks"}, inplace=True)
    else: tmp["Offset inks"] = 0.0
    if plate: tmp.rename(columns={plate: "Płyta offsetowa"}, inplace=True)
    else: tmp["Płyta offsetowa"] = 0.0

    df_profit = df_profit.merge(tmp, left_on="Lewy 10", right_on="_key", how="left")
    df_profit.drop(columns=["_key"], inplace=True, errors="ignore")
    df_profit["Offset inks"] = pd.to_numeric(df_profit["Offset inks"], errors="coerce").fillna(0)
    df_profit["Płyta offsetowa"] = pd.to_numeric(df_profit["Płyta offsetowa"], errors="coerce").fillna(0)
    return df_profit
