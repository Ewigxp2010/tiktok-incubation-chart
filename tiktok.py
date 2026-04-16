import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

plt.rcParams["axes.unicode_minus"] = False

# ======================
# Page config
# ======================
st.set_page_config(
    page_title="Meeting Growth Visualizer",
    layout="wide"
)

# ======================
# AOV preset library
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

LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# ======================
# Phase definition
# ======================
PHASES = [
    ("Phase 1 — Cold Start", 2_000, 10_000, 0.00, 30),
    ("Phase 2 — Growth", 10_000, 30_000, 0.05, 25),
    ("Phase 3 — Breakout", 30_000, 100_000, 0.10, 20),
]

# ======================
# Helpers
# ======================
def format_eur_axis(ax):
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("€{x:,.0f}"))

def normalize_shares(df):
    df = df.copy()
    df["Share"] = df["Share"].clip(lower=0)
    s = df["Share"].sum()
    if s <= 0:
        raise ValueError("At least one product share must be > 0.")
    df["ShareNorm"] = df["Share"] / s
    return df

def get_product_platform_fee_rate(phase_idx: int, promo_60d: bool, fee_type_series):
    """
    fee_type_series contains per-product default fee rates (0.07 or 0.09)

    If promo_60d is on:
      Phase 1 & Phase 2 => all products use 5%
      Phase 3 => use product-level default fee

    If promo_60d is off:
      all phases use product-level default fee
    """
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
    week_offset: int = 0
):
    gmv_series = np.linspace(gmv_start, gmv_end, weeks_in_phase)

    share = prod_df["ShareNorm"].to_numpy()
    aov = prod_df["AOV"].to_numpy()
    gross_margin = prod_df["Gross Margin"].to_numpy()
    fee_type = prod_df["Platform Fee Rate Default"]

    if np.any(aov <= 0):
        raise ValueError("AOV must be > 0 for all products.")

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

def build_phase_summary(df_all: pd.DataFrame):
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

def build_overall_summary(df_all: pd.DataFrame):
    total_gmv = df_all["GMV"].sum()
    total_cost = df_all["Total Cost"].sum()
    total_profit = df_all["Profit"].sum()
    total_orders = df_all["Orders (est.)"].sum()

    out = pd.DataFrame([{
        "Total GMV": total_gmv,
        "Total Cost": total_cost,
        "Total Profit": total_profit,
        "Total Orders (est.)": total_orders,
        "Overall Profit Margin": (total_profit / total_gmv) if total_gmv > 0 else 0
    }])
    return out

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

def plot_phase(df_phase: pd.DataFrame, title: str):
    fig, ax = plt.subplots(figsize=(10, 5))
    x = df_phase["Global Week"].to_numpy()

    ax.plot(x, df_phase["GMV"], marker="o", label="GMV")
    ax.plot(x, df_phase["Total Cost"], marker="o", label="Total Cost")
    ax.plot(x, df_phase["Profit"], marker="o", linewidth=2, label="Profit")
    ax.axhline(0, linewidth=1)
    ax.set_title(title)
    ax.set_xlabel("Week")
    ax.set_ylabel("€")
    ax.grid(True, alpha=0.3)
    ax.legend()
    format_eur_axis(ax)
    fig.tight_layout()
    return fig

def plot_overall(df_all: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 5.5))
    x = df_all["Global Week"].to_numpy()

    ax.plot(x, df_all["GMV"], marker="o", label="GMV")
    ax.plot(x, df_all["Total Cost"], marker="o", label="Total Cost")
    ax.plot(x, df_all["Profit"], marker="o", linewidth=2, label="Profit")
    ax.axhline(0, linewidth=1)
    ax.set_title("Overall weekly trend (all phases)")
    ax.set_xlabel("Global Week")
    ax.set_ylabel("€")
    ax.grid(True, alpha=0.3)
    ax.legend()
    format_eur_axis(ax)
    fig.tight_layout()
    return fig

def plot_cumulative_profit(df_all: pd.DataFrame):
    tmp = df_all.copy()
    tmp["Cumulative Profit"] = tmp["Profit"].cumsum()

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(tmp["Global Week"], tmp["Cumulative Profit"], marker="o", linewidth=2, label="Cumulative Profit")
    ax.axhline(0, linewidth=1)
    ax.set_title("Cumulative profit trend")
    ax.set_xlabel("Global Week")
    ax.set_ylabel("€")
    ax.grid(True, alpha=0.3)
    ax.legend()
    format_eur_axis(ax)
    fig.tight_layout()
    return fig

# ======================
# UI
# ======================
st.title("Meeting Growth Visualizer — Enhanced Version")

with st.sidebar:
    st.header("Global Inputs")

    n_products = st.number_input(
        "No. of products",
        min_value=1,
        max_value=26,
        value=3,
        step=1
    )

    promo_60d = st.radio(
        "60-day fee promo",
        options=[True, False],
        format_func=lambda x: "Yes (5% first ~60 days)" if x else "No promo",
        index=0
    )

    fulfillment_per_order = st.number_input(
        "Fulfillment €/order",
        min_value=0.0,
        value=6.0,
        step=0.5
    )

    sample_product_cost = st.number_input(
        "Sample product €/unit",
        min_value=0.0,
        value=30.0,
        step=1.0
    )

    sample_ship_cost = st.number_input(
        "Sample shipping €/unit",
        min_value=0.0,
        value=5.0,
        step=1.0
    )

    affiliate_share = st.slider(
        "Affiliate GMV share",
        min_value=0.0,
        max_value=1.0,
        value=0.40,
        step=0.01
    )

    affiliate_commission_rate = st.slider(
        "Affiliate commission",
        min_value=0.0,
        max_value=0.5,
        value=0.15,
        step=0.01
    )

    weeks_in_phase = st.slider(
        "Weeks / phase",
        min_value=2,
        max_value=8,
        value=4,
        step=1
    )

st.subheader("Product Setup")

product_rows = []

for i in range(int(n_products)):
    name = LETTERS[i]
    st.markdown(f"### Product {name}")

    col1, col2, col3, col4, col5, col6 = st.columns([1, 1.4, 1.6, 1, 1.4, 1.2])

    with col1:
        share = st.number_input(
            f"Share {name}",
            min_value=0.0,
            value=1.0,
            step=0.1,
            key=f"share_{i}"
        )

    with col2:
        family = st.selectbox(
            f"Family {name}",
            options=list(AOV_PRESETS.keys()),
            key=f"family_{i}"
        )

    preset_options = list(AOV_PRESETS[family].keys())

    with col3:
        category = st.selectbox(
            f"Preset {name}",
            options=preset_options,
            key=f"category_{i}"
        )

    default_aov = AOV_PRESETS[family][category]

    with col4:
        aov = st.number_input(
            f"AOV (€) {name}",
            min_value=0.01,
            value=float(default_aov),
            step=1.0,
            key=f"aov_{i}"
        )

    with col5:
        gross_margin = st.slider(
            f"Gross Margin {name}",
            min_value=0.05,
            max_value=0.90,
            value=0.40,
            step=0.01,
            key=f"gm_{i}"
        )

    with col6:
        fee_label = st.selectbox(
            f"Fee Type {name}",
            options=["Electronics (7%)", "Other (9%)"],
            index=1,
            key=f"fee_{i}"
        )
        fee_type = 0.07 if fee_label == "Electronics (7%)" else 0.09

    product_rows.append({
        "Product": name,
        "Family": family,
        "Preset Category": category,
        "Share": float(share),
        "AOV": float(aov),
        "Gross Margin": float(gross_margin),
        "Platform Fee Rate Default": float(fee_type),
    })

prod_df = pd.DataFrame(product_rows)

generate = st.button("Generate charts", type="primary")

# ======================
# Run
# ======================
if generate:
    try:
        prod_df = normalize_shares(prod_df)

        mix = prod_df[[
            "Product", "Family", "Preset Category", "Share", "ShareNorm",
            "AOV", "Gross Margin", "Platform Fee Rate Default"
        ]].copy()

        mix_display = mix.copy()
        mix_display["Share"] = mix_display["Share"].map(lambda v: f"{v:,.2f}")
        mix_display["ShareNorm"] = mix_display["ShareNorm"].map(lambda v: f"{v:.0%}")
        mix_display["AOV"] = mix_display["AOV"].map(lambda v: f"€{v:,.2f}")
        mix_display["Gross Margin"] = mix_display["Gross Margin"].map(lambda v: f"{v:.0%}")
        mix_display["Platform Fee Rate Default"] = mix_display["Platform Fee Rate Default"].map(lambda v: f"{v:.0%}")

        st.subheader("Product mix used (normalized)")
        st.dataframe(mix_display, use_container_width=True)

        fulfill_cost = float(fulfillment_per_order)
        samp_prod = float(sample_product_cost)
        samp_ship = float(sample_ship_cost)
        promo = bool(promo_60d)
        wks = int(weeks_in_phase)
        aff_share = float(affiliate_share)
        aff_comm_rate = float(affiliate_commission_rate)

        all_tables = []

        for idx, (name, g0, g1, ads_r, samp_w) in enumerate(PHASES):
            dfp = phase_weekly_series(
                idx, name, g0, g1, ads_r, samp_w,
                fulfill_cost, samp_prod, samp_ship,
                promo, wks, prod_df,
                aff_share, aff_comm_rate,
                week_offset=idx * wks
            )

            st.subheader(f"{name} — weekly trend")
            st.pyplot(plot_phase(dfp, f"{name} — weekly trend"), clear_figure=True)

            all_tables.append(dfp)

        df_all = pd.concat(all_tables, ignore_index=True)

        st.subheader("Overall weekly trend")
        st.pyplot(plot_overall(df_all), clear_figure=True)

        st.subheader("Cumulative profit trend")
        st.pyplot(plot_cumulative_profit(df_all), clear_figure=True)

        phase_summary = build_phase_summary(df_all)
        overall_summary = build_overall_summary(df_all)

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

        st.subheader("Phase summary")
        st.dataframe(phase_summary_fmt, use_container_width=True)

        st.subheader("Overall summary")
        st.dataframe(overall_summary_fmt, use_container_width=True)

        single_week_break_even = first_positive_profit_week(df_all)
        cumulative_break_even = first_cumulative_break_even_week(df_all)

        col_a, col_b = st.columns(2)
        with col_a:
            if single_week_break_even is not None:
                st.success(f"First positive weekly profit: Week {single_week_break_even}")
            else:
                st.warning("First positive weekly profit: Not reached")

        with col_b:
            if cumulative_break_even is not None:
                st.success(f"Cumulative break-even: Week {cumulative_break_even}")
            else:
                st.warning("Cumulative break-even: Not reached")

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

        st.subheader("Weekly details (all phases)")
        st.dataframe(df_all_display, use_container_width=True)

    except Exception as e:
        st.error(f"Input error: {e}")
