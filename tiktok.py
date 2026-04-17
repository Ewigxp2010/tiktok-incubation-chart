import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

plt.rcParams["axes.unicode_minus"] = False

st.set_page_config(
    page_title="Meeting Growth Visualizer",
    layout="wide"
)

# ======================
# Presets
# ======================
AOV_PRESETS = {
    "Home & Living": {
        "Kitchenware": 39.68,
        "Pet Supplies": 29.10,
        "Sports & Outdoor": 127.82,
        "Textiles & Soft Furnishings": 41.68,
        "Tools & Hardware": 34.52,
        "Luggage & Bags": 90.05,
        "Shoes": 70.03,
        "Menswear & Underwear": 53.44,
        "Modest Fashion": 19.42,
        "Womenswear & Underwear": 22.34,
        "Furniture": 145.52,
        "Home Improvement": 53.59,
        "Home Supplies": 27.34,
    },
    "Electronics": {
        "Phones & Electronics": 55.14,
        "Computers & Office Equipment": 59.85,
        "Household Appliances": 59.79,
        "Automotive & Motorcycle": 41.19,
        "Collectibles": 77.02,
        "Beauty & Personal Care": 34.14,
        "Baby & Maternity": 51.12,
        "Books, Magazines & Audio": 21.11,
    }
}

ALL_PRESET_OPTIONS = []
for family_name, preset_map in AOV_PRESETS.items():
    for preset_name in preset_map.keys():
        ALL_PRESET_OPTIONS.append(f"{family_name} | {preset_name}")

LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

PHASES = [
    ("Phase 1 — Cold Start", 2_000, 10_000, 0.00, 30),
    ("Phase 2 — Growth", 10_000, 30_000, 0.05, 25),
    ("Phase 3 — Breakout", 30_000, 100_000, 0.10, 20),
]

# ======================
# Helpers
# ======================
def default_product_df(n_products: int) -> pd.DataFrame:
    rows = []
    default_family = "Home & Living"
    default_preset = list(AOV_PRESETS[default_family].keys())[0]
    default_aov = AOV_PRESETS[default_family][default_preset]

    for i in range(n_products):
        rows.append({
            "Product": LETTERS[i],
            "Preset": f"{default_family} | {default_preset}",
            "Share": 1.0,
            "AOV": float(default_aov),
            "Gross Margin": 0.40,
            "Fee Type": "Other (9%)",
        })
    return pd.DataFrame(rows)

def normalize_shares(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Share"] = pd.to_numeric(df["Share"], errors="coerce").fillna(0).clip(lower=0)
    s = df["Share"].sum()
    if s <= 0:
        raise ValueError("At least one product share must be > 0.")
    df["ShareNorm"] = df["Share"] / s
    return df

def split_preset(preset_value: str):
    if " | " not in str(preset_value):
        raise ValueError(f"Invalid preset value: {preset_value}")
    family, preset = preset_value.split(" | ", 1)
    return family, preset

def prepare_product_df(df_input: pd.DataFrame) -> pd.DataFrame:
    df = df_input.copy()

    required_cols = ["Product", "Preset", "Share", "AOV", "Gross Margin", "Fee Type"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    families = []
    presets = []
    fee_rates = []

    for _, row in df.iterrows():
        family, preset = split_preset(row["Preset"])
        families.append(family)
        presets.append(preset)

        fee_label = str(row["Fee Type"]).strip()
        if fee_label == "Electronics (7%)":
            fee_rates.append(0.07)
        else:
            fee_rates.append(0.09)

    df["Family"] = families
    df["Preset Category"] = presets
    df["Platform Fee Rate Default"] = fee_rates
    df["AOV"] = pd.to_numeric(df["AOV"], errors="coerce")
    df["Gross Margin"] = pd.to_numeric(df["Gross Margin"], errors="coerce")
    df["Share"] = pd.to_numeric(df["Share"], errors="coerce")

    if df["Product"].isna().any():
        raise ValueError("Product name cannot be empty.")

    if (df["AOV"] <= 0).any() or df["AOV"].isna().any():
        raise ValueError("AOV must be > 0 for all products.")

    if ((df["Gross Margin"] < 0.05) | (df["Gross Margin"] > 0.90) | df["Gross Margin"].isna()).any():
        raise ValueError("Gross Margin must be between 0.05 and 0.90 for all products.")

    df = normalize_shares(df)
    return df

def format_eur_axis(ax):
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("€{x:,.0f}"))

def get_product_platform_fee_rate(phase_idx: int, promo_60d: bool, fee_type_series: pd.Series) -> np.ndarray:
    if promo_60d and phase_idx in (0, 1):
        return np.full(len(fee_type_series), 0.05)
    return fee_type_series.to_numpy()

def phase_weekly_series(
    phase_idx: int,
    phase_name: str,
    gmv_start: float,
    gmv_end: float,
    ads_rate: float,
    samples_per_week: int,
    fulfill_cost: float,
    sample_product_cost: float,
    sample_ship_cost: float,
    promo_60d: bool,
    weeks_in_phase: int,
    prod_df: pd.DataFrame,
    affiliate_share: float,
    affiliate_commission_rate: float,
    week_offset: int = 0,
) -> pd.DataFrame:
    gmv_series = np.linspace(gmv_start, gmv_end, weeks_in_phase)

    share = prod_df["ShareNorm"].to_numpy()
    aov = prod_df["AOV"].to_numpy()
    gross_margin = prod_df["Gross Margin"].to_numpy()
    fee_type = prod_df["Platform Fee Rate Default"]

    sample_allin_unit = float(sample_product_cost) + float(sample_ship_cost)
    product_fee_rates = get_product_platform_fee_rate(phase_idx, promo_60d, fee_type)

    rows = []
    for i in range(weeks_in_phase):
        gmv = float(gmv_series[i])

        affiliate_gmv = gmv * affiliate_share
        non_affiliate_gmv = gmv * (1 - affiliate_share)

        rev = gmv * share
        orders_p = rev / aov
        orders_total = float(np.sum(orders_p))

        cogs_p = rev * (1.0 - gross_margin)
        cogs_total = float(np.sum(cogs_p))

        platform_fee_p = rev * product_fee_rates
        platform_fee_total = float(np.sum(platform_fee_p))

        ads = gmv * ads_rate
        samples_cost = float(samples_per_week) * sample_allin_unit
        fulfillment = orders_total * float(fulfill_cost)
        creator_commission = affiliate_gmv * affiliate_commission_rate

        total_cost = (
            cogs_total
            + ads
            + samples_cost
            + fulfillment
            + platform_fee_total
            + creator_commission
        )
        profit = gmv - total_cost

        rows.append({
            "Phase": phase_name,
            "Week in Phase": i + 1,
            "Global Week": week_offset + i + 1,
            "GMV": gmv,
            "Affiliate GMV": affiliate_gmv,
            "Non-affiliate GMV": non_affiliate_gmv,
            "Creator Commission": creator_commission,
            "Platform Fee": platform_fee_total,
            "Ads Cost": ads,
            "Samples Cost": samples_cost,
            "Fulfillment Cost": fulfillment,
            "COGS": cogs_total,
            "Total Cost": total_cost,
            "Profit": profit,
            "Orders (est.)": orders_total,
            "Ads Rate": ads_rate,
            "Samples / Week": samples_per_week
        })

    return pd.DataFrame(rows)

def build_phase_summary(df_all: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df_all.groupby("Phase", as_index=False)
        .agg({
            "GMV": "sum",
            "Total Cost": "sum",
            "Profit": "sum",
            "Orders (est.)": "sum",
            "Platform Fee": "sum",
            "Ads Cost": "sum",
            "Samples Cost": "sum",
            "Fulfillment Cost": "sum",
            "Creator Commission": "sum",
            "COGS": "sum"
        })
    )
    summary["Profit Margin"] = np.where(summary["GMV"] > 0, summary["Profit"] / summary["GMV"], 0)
    return summary

def build_overall_summary(df_all: pd.DataFrame) -> pd.DataFrame:
    total_gmv = df_all["GMV"].sum()
    total_cost = df_all["Total Cost"].sum()
    total_profit = df_all["Profit"].sum()
    total_orders = df_all["Orders (est.)"].sum()

    return pd.DataFrame([{
        "Total GMV": total_gmv,
        "Total Cost": total_cost,
        "Total Profit": total_profit,
        "Total Orders (est.)": total_orders,
        "Overall Profit Margin": (total_profit / total_gmv) if total_gmv > 0 else 0
    }])

def first_positive_profit_week(df_all: pd.DataFrame):
    tmp = df_all[df_all["Profit"] > 0]
    if len(tmp) == 0:
        return None
    return int(tmp["Global Week"].iloc[0])

def first_cumulative_break_even_week(df_all: pd.DataFrame):
    tmp = df_all.copy()
    tmp["Cumulative Profit"] = tmp["Profit"].cumsum()
    pos = tmp[tmp["Cumulative Profit"] >= 0]
    if len(pos) == 0:
        return None
    return int(pos["Global Week"].iloc[0])

def make_chart(df: pd.DataFrame, title: str):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Global Week"], df["GMV"], marker="o", label="GMV")
    ax.plot(df["Global Week"], df["Total Cost"], marker="o", label="Total Cost")
    ax.plot(df["Global Week"], df["Profit"], marker="o", linewidth=2, label="Profit")
    ax.axhline(0, linewidth=1)
    ax.set_title(title)
    ax.set_xlabel("Week")
    ax.set_ylabel("€")
    ax.grid(True, alpha=0.3)
    ax.legend()
    format_eur_axis(ax)
    fig.tight_layout()
    return fig

def make_cumulative_profit_chart(df_all: pd.DataFrame):
    tmp = df_all.copy()
    tmp["Cumulative Profit"] = tmp["Profit"].cumsum()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(tmp["Global Week"], tmp["Cumulative Profit"], marker="o", linewidth=2, label="Cumulative Profit")
    ax.axhline(0, linewidth=1)
    ax.set_title("Cumulative Profit Trend")
    ax.set_xlabel("Global Week")
    ax.set_ylabel("€")
    ax.grid(True, alpha=0.3)
    ax.legend()
    format_eur_axis(ax)
    fig.tight_layout()
    return fig

def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

# ======================
# UI
# ======================
st.title("Meeting Growth Visualizer")
st.caption("Enhanced Streamlit version for GMV / Cost / Profit modeling")

with st.sidebar:
    st.header("Global Inputs")

    n_products = st.number_input(
        "No. of products",
        min_value=1,
        max_value=26,
        value=3,
        step=1,
    )

    promo_60d = st.radio(
        "60-day fee promo",
        options=[True, False],
        format_func=lambda x: "Yes (5% first ~60 days)" if x else "No promo",
        index=0,
    )

    fulfillment_per_order = st.number_input(
        "Fulfillment €/order",
        min_value=0.0,
        value=6.0,
        step=0.5,
    )

    sample_product_cost = st.number_input(
        "Sample product €/unit",
        min_value=0.0,
        value=30.0,
        step=1.0,
    )

    sample_ship_cost = st.number_input(
        "Sample shipping €/unit",
        min_value=0.0,
        value=5.0,
        step=1.0,
    )

    affiliate_share = st.slider(
        "Affiliate GMV share",
        min_value=0.0,
        max_value=1.0,
        value=0.40,
        step=0.01,
    )

    affiliate_commission_rate = st.slider(
        "Affiliate commission",
        min_value=0.0,
        max_value=0.5,
        value=0.15,
        step=0.01,
    )

    weeks_in_phase = st.slider(
        "Weeks / phase",
        min_value=2,
        max_value=8,
        value=4,
        step=1,
    )

# keep editor stable
if "editor_df" not in st.session_state or len(st.session_state.editor_df) != int(n_products):
    st.session_state.editor_df = default_product_df(int(n_products))

st.subheader("Product Setup")
st.caption("You can edit the table directly. Preset is used as a category reference; AOV can still be manually overridden.")

edited_df = st.data_editor(
    st.session_state.editor_df,
    num_rows="fixed",
    use_container_width=True,
    column_config={
        "Product": st.column_config.TextColumn("Product"),
        "Preset": st.column_config.SelectboxColumn("Preset", options=ALL_PRESET_OPTIONS),
        "Share": st.column_config.NumberColumn("Share", min_value=0.0, step=0.1, format="%.2f"),
        "AOV": st.column_config.NumberColumn("AOV (€)", min_value=0.01, step=1.0, format="%.2f"),
        "Gross Margin": st.column_config.NumberColumn("Gross Margin", min_value=0.05, max_value=0.90, step=0.01, format="%.2f"),
        "Fee Type": st.column_config.SelectboxColumn("Fee Type", options=["Electronics (7%)", "Other (9%)"]),
    },
    hide_index=True,
    key="product_editor",
)

st.session_state.editor_df = edited_df.copy()

generate = st.button("Generate charts", type="primary")

if generate:
    try:
        prod_df = prepare_product_df(edited_df)

        mix_display = prod_df[[
            "Product", "Family", "Preset Category", "Share", "ShareNorm",
            "AOV", "Gross Margin", "Platform Fee Rate Default"
        ]].copy()

        mix_display["Share"] = mix_display["Share"].map(lambda v: f"{v:,.2f}")
        mix_display["ShareNorm"] = mix_display["ShareNorm"].map(lambda v: f"{v:.0%}")
        mix_display["AOV"] = mix_display["AOV"].map(lambda v: f"€{v:,.2f}")
        mix_display["Gross Margin"] = mix_display["Gross Margin"].map(lambda v: f"{v:.0%}")
        mix_display["Platform Fee Rate Default"] = mix_display["Platform Fee Rate Default"].map(lambda v: f"{v:.0%}")

        st.subheader("Product Mix Used")
        st.dataframe(mix_display, use_container_width=True)

        all_tables = []
        for idx, (phase_name, g0, g1, ads_r, samp_w) in enumerate(PHASES):
            dfp = phase_weekly_series(
                idx,
                phase_name,
                g0,
                g1,
                ads_r,
                samp_w,
                float(fulfillment_per_order),
                float(sample_product_cost),
                float(sample_ship_cost),
                bool(promo_60d),
                int(weeks_in_phase),
                prod_df,
                float(affiliate_share),
                float(affiliate_commission_rate),
                week_offset=idx * int(weeks_in_phase),
            )
            all_tables.append(dfp)

        df_all = pd.concat(all_tables, ignore_index=True)

        phase_summary = build_phase_summary(df_all)
        overall_summary = build_overall_summary(df_all)

        metric1, metric2, metric3 = st.columns(3)
        with metric1:
            st.metric("Total GMV", f"€{overall_summary.iloc[0]['Total GMV']:,.0f}")
        with metric2:
            st.metric("Total Profit", f"€{overall_summary.iloc[0]['Total Profit']:,.0f}")
        with metric3:
            st.metric("Profit Margin", f"{overall_summary.iloc[0]['Overall Profit Margin']:.1%}")

        st.subheader("Charts")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.pyplot(make_chart(df_all, "Overall Weekly Trend"))

        with chart_col2:
            st.pyplot(make_cumulative_profit_chart(df_all))

        st.subheader("Phase-by-Phase Weekly Trend")
        phase_tabs = st.tabs([p[0] for p in PHASES])
        for tab, (phase_name, _, _, _, _) in zip(phase_tabs, PHASES):
            with tab:
                phase_df = df_all[df_all["Phase"] == phase_name].copy()
                st.pyplot(make_chart(phase_df, phase_name))

        phase_summary_fmt = phase_summary.copy()
        for col in [
            "GMV", "Total Cost", "Profit", "Orders (est.)", "Platform Fee",
            "Ads Cost", "Samples Cost", "Fulfillment Cost", "Creator Commission", "COGS"
        ]:
            phase_summary_fmt[col] = phase_summary_fmt[col].map(lambda v: f"{v:,.0f}")
        phase_summary_fmt["Profit Margin"] = phase_summary["Profit Margin"].map(lambda v: f"{v:.1%}")

        overall_summary_fmt = overall_summary.copy()
        overall_summary_fmt["Total GMV"] = overall_summary_fmt["Total GMV"].map(lambda v: f"{v:,.0f}")
        overall_summary_fmt["Total Cost"] = overall_summary_fmt["Total Cost"].map(lambda v: f"{v:,.0f}")
        overall_summary_fmt["Total Profit"] = overall_summary_fmt["Total Profit"].map(lambda v: f"{v:,.0f}")
        overall_summary_fmt["Total Orders (est.)"] = overall_summary_fmt["Total Orders (est.)"].map(lambda v: f"{v:,.0f}")
        overall_summary_fmt["Overall Profit Margin"] = overall_summary["Overall Profit Margin"].map(lambda v: f"{v:.1%}")

        st.subheader("Summary")
        sum_col1, sum_col2 = st.columns(2)
        with sum_col1:
            st.dataframe(phase_summary_fmt, use_container_width=True)
        with sum_col2:
            st.dataframe(overall_summary_fmt, use_container_width=True)

        single_week_break_even = first_positive_profit_week(df_all)
        cumulative_break_even = first_cumulative_break_even_week(df_all)

        st.subheader("Break-even Signals")
        be_col1, be_col2 = st.columns(2)
        with be_col1:
            if single_week_break_even is not None:
                st.success(f"First positive weekly profit: Week {single_week_break_even}")
            else:
                st.warning("First positive weekly profit: Not reached")

        with be_col2:
            if cumulative_break_even is not None:
                st.success(f"Cumulative break-even: Week {cumulative_break_even}")
            else:
                st.warning("Cumulative break-even: Not reached")

        st.subheader("Weekly Details")
        df_all_display = df_all.copy()
        money_cols = [
            "GMV", "Affiliate GMV", "Non-affiliate GMV", "Creator Commission",
            "Platform Fee", "Ads Cost", "Samples Cost", "Fulfillment Cost",
            "COGS", "Total Cost", "Profit"
        ]
        for col in money_cols:
            df_all_display[col] = df_all_display[col].map(lambda v: f"{v:,.2f}")
        df_all_display["Orders (est.)"] = df_all_display["Orders (est.)"].map(lambda v: f"{v:,.2f}")
        df_all_display["Ads Rate"] = df_all["Ads Rate"].map(lambda v: f"{v:.0%}")

        st.dataframe(df_all_display, use_container_width=True)

        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                "Download weekly details CSV",
                data=to_csv_bytes(df_all),
                file_name="weekly_details.csv",
                mime="text/csv"
            )
        with dl2:
            st.download_button(
                "Download phase summary CSV",
                data=to_csv_bytes(phase_summary),
                file_name="phase_summary.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Input error: {e}")
