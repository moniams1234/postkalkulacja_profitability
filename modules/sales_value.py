import pandas as pd
import numpy as np
from .helpers import find_col, safe_num, extract_invoice_fragment

def add_sales_value_and_invoice_date(df_profit, df_zlec=None, df_fry=None):
    df = df_profit.copy()
    df["Sales Value"] = np.nan
    df["Data faktury"] = pd.NaT

    # first source: zlec + faktury
    if df_zlec is not None:
        nzp = find_col(df_zlec, ["Numer Zlecenia produkcyjnego", "Numer zlecenia produkcyjnego"])
        val = find_col(df_zlec, ["Wartosc w linii FV netto", "Wartość w linii FV netto"])
        date = find_col(df_zlec, ["Data wystawienia faktury", "Data wystawienia FV"])
        if nzp and val:
            tmp = df_zlec.copy()
            tmp["_zp"] = tmp[nzp].astype(str).str.strip()
            agg = {"_sv": (val, "sum")}
            if date:
                agg["_dt"] = (date, "first")
            grouped = tmp.groupby("_zp", dropna=False).agg(**agg).reset_index()
            df = df.merge(grouped, left_on="Zlecenie produkcyjne", right_on="_zp", how="left")
            mask = df["_sv"].notna()
            df.loc[mask, "Sales Value"] = df.loc[mask, "_sv"]
            if date:
                df.loc[mask, "Data faktury"] = pd.to_datetime(df.loc[mask, "_dt"], errors="coerce")
            df.drop(columns=["_zp", "_sv", "_dt"], inplace=True, errors="ignore")

    # fallback: faktury linie using fragment after "| " and before " ["
    if df_fry is not None:
        name = find_col(df_fry, ["Nazwa linii faktury", "Nazwa lini faktury"])
        val = find_col(df_fry, ["Wartosc w linii FV netto", "Wartość w linii FV netto"])
        qty = find_col(df_fry, ["Ilosc w linii FV", "Ilość w linii FV"])
        date = find_col(df_fry, ["Data wystawienia FV", "Data wystawienia faktury"])
        order_col = find_col(df, ["Zamówienie", "Zamowienie"])
        prof_qty = find_col(df, ["Zamawiana ilość", "Zamawiana ilosc"])

        if name and val and order_col:
            names = df_fry[name].astype(str)
            for idx in df[df["Sales Value"].isna()].index:
                fragment = extract_invoice_fragment(df.at[idx, order_col])
                if not fragment:
                    continue
                mask = names.str.contains(fragment, case=False, na=False, regex=False)
                if not mask.any():
                    continue
                row = df_fry[mask].iloc[0]
                invoice_value = safe_num(row[val])
                invoice_qty = safe_num(row[qty]) if qty else 0
                order_qty = safe_num(df.at[idx, prof_qty]) if prof_qty else 0
                if invoice_qty > 0 and order_qty > 0:
                    df.at[idx, "Sales Value"] = invoice_value / invoice_qty * order_qty
                else:
                    df.at[idx, "Sales Value"] = invoice_value
                if date:
                    df.at[idx, "Data faktury"] = pd.to_datetime(row[date], errors="coerce")

    df["Sales Value"] = pd.to_numeric(df["Sales Value"], errors="coerce").fillna(0)
    df["Data faktury"] = pd.to_datetime(df["Data faktury"], errors="coerce")
    df["Miesiąc faktury"] = df["Data faktury"].dt.strftime("%Y-%m").fillna("")
    return df
