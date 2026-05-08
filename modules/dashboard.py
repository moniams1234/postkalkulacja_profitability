import plotly.express as px
from .summaries import customer_summary

BURG = "#6B0000"
ORANGE = "#FF5A1F"
RED = "#C91818"
GREEN = "#0FA958"

def kpi_values(df, month=None):
    data = df if not month or month == "Wszystkie" else df[df["Miesiąc faktury"] == month]
    sv = data["Sales Value"].sum()
    tpm = data["TPM"].sum()
    cm = data["CM"].sum()
    return {
        "Suma sprzedaży": sv,
        "Suma TPM": tpm,
        "TPM %": tpm / sv if sv else 0,
        "Suma CM": cm,
        "CM %": cm / sv if sv else 0,
        "Liczba zamówień": len(data),
        "Digital": (data["Digital/Offset"] == "Digital").sum(),
        "Offset": (data["Digital/Offset"] == "Offset").sum(),
        "no printing": (data["Digital/Offset"] == "no printing").sum(),
    }

def charts(summary_df):
    figs = {}
    if summary_df.empty:
        return figs
    figs["top_tpm"] = px.bar(summary_df.nlargest(5, "Suma TPM"), x="Klient", y="Suma TPM", title="Top 5 klientów wg TPM", color_discrete_sequence=[BURG])
    figs["top_cm"] = px.bar(summary_df.nlargest(5, "Suma CM"), x="Klient", y="Suma CM", title="Top 5 klientów wg CM", color_discrete_sequence=[ORANGE])
    figs["top_sales"] = px.bar(summary_df.nlargest(5, "Suma sprzedaży"), x="Klient", y="Suma sprzedaży", title="Top 5 klientów wg sprzedaży", color_discrete_sequence=[GREEN])
    figs["orders"] = px.bar(summary_df.sort_values("Liczba zamówień", ascending=False), x="Klient", y="Liczba zamówień", title="Liczba zamówień wg klientów", color_discrete_sequence=[BURG])
    figs["tpm_pct"] = px.bar(summary_df.sort_values("TPM %", ascending=False), x="Klient", y="TPM %", title="TPM % wg klientów", color_discrete_sequence=[ORANGE])
    figs["cm_pct"] = px.bar(summary_df.sort_values("CM %", ascending=False), x="Klient", y="CM %", title="CM % wg klientów", color_discrete_sequence=[GREEN])
    return figs
