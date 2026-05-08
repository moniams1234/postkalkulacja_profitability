import pandas as pd
from .helpers import find_col

def add_time_costs(df_profit, df_czasy, rates):
    df = df_profit.copy()
    machine_cols = []
    if df_czasy is None:
        return df, None, machine_cols

    zp = find_col(df_czasy, ["Numer zlecenia produkcyjnego"])
    mach = find_col(df_czasy, ["Nazwa maszyny"])
    mins = find_col(df_czasy, ["Czas czynnosci [min]", "Czas czynności [min]"])
    if not (zp and mach and mins):
        return df, df_czasy, machine_cols

    cz = df_czasy.copy()
    cz["_zp"] = cz[zp].astype(str).str.strip()
    cz["_machine"] = cz[mach].astype(str).str.strip()
    cz["_minutes"] = pd.to_numeric(cz[mins], errors="coerce").fillna(0)

    def rate_for(m):
        ml = str(m).lower().strip()
        for k, v in rates.items():
            kl = str(k).lower().strip()
            if ml == kl or ml in kl or kl in ml:
                return float(v)
        return 0.0

    cz["_rate"] = cz["_machine"].apply(rate_for)
    cz["Koszt pracy"] = cz["_minutes"] / 60.0 * cz["_rate"]

    for machine in sorted(cz["_machine"].dropna().unique()):
        machine_cols.append(machine)
        g = cz[cz["_machine"] == machine].groupby("_zp")["Koszt pracy"].sum().reset_index()
        df = df.merge(g.rename(columns={"_zp": "_zp_key", "Koszt pracy": machine}),
                      left_on="Zlecenie produkcyjne", right_on="_zp_key", how="left")
        df.drop(columns=["_zp_key"], inplace=True, errors="ignore")
        df[machine] = pd.to_numeric(df[machine], errors="coerce").fillna(0)

    return df, cz, machine_cols

def add_totals(df, machine_cols, other_pct):
    df = df.copy()
    df["Other costs %"] = other_pct / 100.0
    df["Other Materials"] = pd.to_numeric(df.get("Sales Value", 0), errors="coerce").fillna(0) * df["Other costs %"]

    for c in machine_cols + ["Prepress costs"]:
        if c not in df.columns:
            df[c] = 0.0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["Total DL"] = df[machine_cols + ["Prepress costs"]].sum(axis=1)

    mat_names = ["Papier [16]", "Klej [17]", "Lakiery [20]", "Opakowania zbiorcze [24]",
                 "Other Materials", "Offset inks", "Płyta offsetowa", "Kliki final"]
    mat_cols = []
    for name in mat_names:
        col = find_col(df, [name])
        if col is None:
            df[name] = 0.0
            col = name
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        mat_cols.append(col)

    df["Total Materials"] = df[mat_cols].sum(axis=1)
    df["TPM"] = df["Sales Value"] - df["Total DL"]
    df["CM"] = df["Sales Value"] - df["Total DL"] - df["Total Materials"]
    return df
