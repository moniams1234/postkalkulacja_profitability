import pandas as pd
from .helpers import find_col, safe_num

def calculate_clicks(df_profit, df_inks, click_costs):
    df_profit = df_profit.copy()
    if df_inks is None:
        df_profit["Moje Kliki"] = 0.0
        return df_profit, None

    jn = find_col(df_inks, ["Job Name"])
    pn = find_col(df_inks, ["Press Name"])
    color = find_col(df_inks, ["Color"])
    sep = find_col(df_inks, ["Separations"])
    if not jn or not sep:
        df_profit["Moje Kliki"] = 0.0
        return df_profit, df_inks

    inks = df_inks.copy()
    inks["Zamówienie"] = inks[jn].astype(str).str[:10]
    inks["_separations"] = pd.to_numeric(inks[sep], errors="coerce").fillna(0)

    def unit_cost(row):
        press = str(row.get(pn, "")).strip() if pn else ""
        col = str(row.get(color, "")).strip() if color else "default"
        if press in click_costs:
            if col in click_costs[press]:
                return safe_num(click_costs[press][col])
            if "default" in click_costs[press]:
                return safe_num(click_costs[press]["default"])
        for m in click_costs.values():
            if isinstance(m, dict) and m:
                return safe_num(list(m.values())[0])
        return 0.05

    inks["Koszt klików"] = inks.apply(unit_cost, axis=1) * inks["_separations"]
    grp = inks.groupby("Zamówienie", dropna=False)["Koszt klików"].sum().reset_index()
    df_profit = df_profit.merge(grp.rename(columns={"Zamówienie": "_zam", "Koszt klików": "Moje Kliki"}),
                                left_on="Lewy 10", right_on="_zam", how="left")
    df_profit.drop(columns=["_zam"], inplace=True, errors="ignore")
    df_profit["Moje Kliki"] = pd.to_numeric(df_profit["Moje Kliki"], errors="coerce").fillna(0)

    kliki_col = find_col(df_profit, ["Kliki [48]"])
    if kliki_col:
        df_profit[kliki_col] = pd.to_numeric(df_profit[kliki_col], errors="coerce").fillna(0)
        df_profit["Kliki final"] = df_profit[[kliki_col, "Moje Kliki"]].max(axis=1)
    else:
        df_profit["Kliki final"] = df_profit["Moje Kliki"]

    return df_profit, inks
