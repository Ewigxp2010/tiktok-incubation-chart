import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


st.set_page_config(page_title="TikTok Shop Growth Visualizer", layout="wide")
plt.rcParams["axes.unicode_minus"] = False


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
    },
}


# 临时公开 benchmark。拿到数据组真实数据后，主要替换这里。
FUNNEL_PRESETS = {
    "Home & Living": {
        "Kitchenware": {"videos_per_sample": 0.40, "clicks_per_video": 120, "click_to_order_rate": 0.038, "shop_tab_share": 0.30},
        "Pet Supplies": {"videos_per_sample": 0.45, "clicks_per_video": 110, "click_to_order_rate": 0.040, "shop_tab_share": 0.28},
        "Sports & Outdoor": {"videos_per_sample": 0.35, "clicks_per_video": 80, "click_to_order_rate": 0.025, "shop_tab_share": 0.32},
        "Textiles & Soft Furnishings": {"videos_per_sample": 0.35, "clicks_per_video": 90, "click_to_order_rate": 0.030, "shop_tab_share": 0.35},
        "Tools & Hardware": {"videos_per_sample": 0.35, "clicks_per_video": 90, "click_to_order_rate": 0.030, "shop_tab_share": 0.30},
        "Luggage & Bags": {"videos_per_sample": 0.30, "clicks_per_video": 70, "click_to_order_rate": 0.025, "shop_tab_share": 0.35},
        "Shoes": {"videos_per_sample": 0.35, "clicks_per_video": 85, "click_to_order_rate": 0.035, "shop_tab_share": 0.35},
        "Menswear & Underwear": {"videos_per_sample": 0.35, "clicks_per_video": 95, "click_to_order_rate": 0.038, "shop_tab_share": 0.35},
        "Modest Fashion": {"videos_per_sample": 0.35, "clicks_per_video": 90, "click_to_order_rate": 0.035, "shop_tab_share": 0.35},
        "Womenswear & Underwear": {"videos_per_sample": 0.40, "clicks_per_video": 110, "click_to_order_rate": 0.042, "shop_tab_share": 0.35},
        "Furniture": {"videos_per_sample": 0.25, "clicks_per_video": 45, "click_to_order_rate": 0.015, "shop_tab_share": 0.40},
        "Home Improvement": {"videos_per_sample": 0.30, "clicks_per_video": 70, "click_to_order_rate": 0.025, "shop_tab_share": 0.35},
        "Home Supplies": {"videos_per_sample": 0.40, "clicks_per_video": 100, "click_to_order_rate": 0.038, "shop_tab_share": 0.32},
    },
    "Electronics": {
        "Phones & Electronics": {"videos_per_sample": 0.30, "clicks_per_video": 70, "click_to_order_rate": 0.025, "shop_tab_share": 0.35},
        "Computers & Office Equipment": {"videos_per_sample": 0.25, "clicks_per_video": 55, "click_to_order_rate": 0.018, "shop_tab_share": 0.40},
        "Household Appliances": {"videos_per_sample": 0.30, "clicks_per_video": 75, "click_to_order_rate": 0.025, "shop_tab_share": 0.35},
        "Automotive & Motorcycle": {"videos_per_sample": 0.25, "clicks_per_video": 50, "click_to_order_rate": 0.020, "shop_tab_share": 0.35},
        "Collectibles": {"videos_per_sample": 0.35, "clicks_per_video": 80, "click_to_order_rate": 0.035, "shop_tab_share": 0.30},
        "Beauty & Personal Care": {"videos_per_sample": 0.50, "clicks_per_video": 150, "click_to_order_rate": 0.065, "shop_tab_share": 0.25},
        "Baby & Maternity": {"videos_per_sample": 0.45, "clicks_per_video": 110, "click_to_order_rate": 0.050, "shop_tab_share": 0.30},
        "Books, Magazines & Audio": {"videos_per_sample": 0.30, "clicks_per_video": 50, "click_to_order_rate": 0.025, "shop_tab_share": 0.35},
    },
}


SCENARIOS = {
    "保守": {"videos_per_sample": 0.75, "clicks_per_video": 0.70, "click_to_order_rate": 0.75},
    "基准": {"videos_per_sample": 1.00, "clicks_per_video": 1.00, "click_to_order_rate": 1.00},
    "激进": {"videos_per_sample": 1.25, "clicks_per_video": 1.30, "click_to_order_rate": 1.20},
}


PHASE_DEFAULTS = [
    {"name": "阶段 1 - 冷启动", "gmv_start": 2000, "gmv_end": 10000, "ads_take_rate": 0.00, "samples": 30},
    {"name": "阶段 2 - 增长", "gmv_start": 10000, "gmv_end": 30000, "ads_take_rate": 0.05, "samples": 25},
    {"name": "阶段 3 - 爆发", "gmv_start": 30000, "gmv_end": 100000, "ads_take_rate": 0.10, "samples": 20},
]


PHASE_COLORS = {
    "阶段 1 - 冷启动": "#EAF4FF",
    "阶段 2 - 增长": "#EEFBEF",
    "阶段 3 - 爆发": "#FFF4E8",
}


ELECTRONICS_FEE_CATEGORIES = {
    "Phones & Electronics",
    "Computers & Office Equipment",
    "Household Appliances",
    "Automotive & Motorcycle",
}


CONTENT_DECAY_WEIGHTS = [1.00, 0.55, 0.30, 0.15]
PROMO_WEEKS = 9
LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def money(x, digits=0):
    return f"€{float(x):,.{digits}f}"


def pct(x, digits=1):
    return f"{float(x):.{digits}%}"


def parse_percent(x):
    if x is None:
        return 0.0
    text = str(x).strip().replace("%", "").replace(",", ".")
    return 0.0 if text == "" else float(text)


def get_benchmark(family, preset):
    data = FUNNEL_PRESETS[family][preset].copy()
    data["aov"] = AOV_PRESETS[family][preset]
    return data


def guess_fee_type(preset):
    return "electronics" if preset in ELECTRONICS_FEE_CATEGORIES else "other"


def fee_label(x):
    return "电子类 / Electronics (7%)" if x == "electronics" else "其他 / Other (9%)"


def platform_fee_rate(global_week, promo_60d, base_rates):
    if promo_60d and global_week <= PROMO_WEEKS:
        return np.full(len(base_rates), 0.05)
    return base_rates


def format_eur_axis(ax):
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("€{x:,.0f}"))


def add_phase_backgrounds(ax, df):
    ranges = df.groupby("Phase", as_index=False).agg(
        start=("Global Week", "min"),
        end=("Global Week", "max"),
    )
    for _, row in ranges.iterrows():
        ax.axvspan(
            row["start"] - 0.5,
            row["end"] + 0.5,
            color=PHASE_COLORS.get(row["Phase"], "#F5F5F5"),
            alpha=0.8,
            zorder=0,
        )


def init_product_state(i, n_products):
    if f"product_name_{i}" not in st.session_state:
        st.session_state[f"product_name_{i}"] = LETTERS[i]
    if f"family_{i}" not in st.session_state:
        st.session_state[f"family_{i}"] = "Home & Living"

    family = st.session_state[f"family_{i}"]
    presets = list(AOV_PRESETS[family].keys())

    if f"preset_{i}" not in st.session_state or st.session_state[f"preset_{i}"] not in presets:
        st.session_state[f"preset_{i}"] = presets[0]

    preset = st.session_state[f"preset_{i}"]
    b = get_benchmark(family, preset)

    defaults = {
        f"sample_share_{i}": f"{round(100 / n_products, 1)}",
        f"aov_{i}": b["aov"],
        f"gross_margin_pct_{i}": 40.0,
        f"fee_type_{i}": guess_fee_type(preset),
        f"videos_per_sample_{i}": b["videos_per_sample"],
        f"clicks_per_video_{i}": b["clicks_per_video"],
        f"click_to_order_pct_{i}": b["click_to_order_rate"] * 100,
        f"shop_tab_share_pct_{i}": b["shop_tab_share"] * 100,
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def apply_benchmark(i):
    family = st.session_state[f"family_{i}"]
    preset = st.session_state[f"preset_{i}"]
    b = get_benchmark(family, preset)

    st.session_state[f"aov_{i}"] = b["aov"]
    st.session_state[f"fee_type_{i}"] = guess_fee_type(preset)
    st.session_state[f"videos_per_sample_{i}"] = b["videos_per_sample"]
    st.session_state[f"clicks_per_video_{i}"] = b["clicks_per_video"]
    st.session_state[f"click_to_order_pct_{i}"] = b["click_to_order_rate"] * 100
    st.session_state[f"shop_tab_share_pct_{i}"] = b["shop_tab_share"] * 100


def build_product_df(n_products):
    rows = []

    for i in range(n_products):
        fee_type = st.session_state[f"fee_type_{i}"]
        rows.append({
            "Product": st.session_state[f"product_name_{i}"],
            "Family": st.session_state[f"family_{i}"],
            "Subcategory": st.session_state[f"preset_{i}"],
            "Sample Allocation (%)": parse_percent(st.session_state[f"sample_share_{i}"]),
            "AOV": float(st.session_state[f"aov_{i}"]),
            "Gross Margin": float(st.session_state[f"gross_margin_pct_{i}"]) / 100,
            "Platform Fee Rate": 0.07 if fee_type == "electronics" else 0.09,
            "Videos / Sample": float(st.session_state[f"videos_per_sample_{i}"]),
            "Clicks / Video": float(st.session_state[f"clicks_per_video_{i}"]),
            "Click-to-order Rate": float(st.session_state[f"click_to_order_pct_{i}"]) / 100,
            "ShopTab GMV Share": float(st.session_state[f"shop_tab_share_pct_{i}"]) / 100,
        })

    df = pd.DataFrame(rows)

    if df["Product"].astype(str).str.strip().eq("").any():
        raise ValueError("产品名称不能为空")
    if df["AOV"].le(0).any():
        raise ValueError("AOV 必须大于 0")
    if df["Gross Margin"].lt(0.05).any() or df["Gross Margin"].gt(0.90).any():
        raise ValueError("毛利率必须在 5% 到 90% 之间")
    if df["Sample Allocation (%)"].sum() <= 0:
        raise ValueError("至少一个产品的寄样分配占比必须大于 0")
    if df["Click-to-order Rate"].lt(0).any() or df["Click-to-order Rate"].gt(1).any():
        raise ValueError("点击到下单转化率必须在 0% 到 100% 之间")
    if df["ShopTab GMV Share"].lt(0).any() or df["ShopTab GMV Share"].gt(1).any():
        raise ValueError("ShopTab GMV 占比必须在 0% 到 100% 之间")

    df["SampleShareNorm"] = df["Sample Allocation (%)"] / df["Sample Allocation (%)"].sum()
    return df


def build_weekly_model(
    product_df,
    phases,
    weeks_per_phase,
    scenario_name,
    promo_60d,
    fulfillment_per_order,
    sample_shipping_cost,
    affiliate_commission_rate,
    ads_roas,
):
    scenario = SCENARIOS[scenario_name]

    share = product_df["SampleShareNorm"].to_numpy()
    aov = product_df["AOV"].to_numpy()
    gross_margin = product_df["Gross Margin"].to_numpy()
    base_fee_rates = product_df["Platform Fee Rate"].to_numpy()

    sample_product_cost = aov * (1 - gross_margin)
    videos_per_sample = product_df["Videos / Sample"].to_numpy() * scenario["videos_per_sample"]
    clicks_per_video = product_df["Clicks / Video"].to_numpy() * scenario["clicks_per_video"]
    click_to_order = np.minimum(
        product_df["Click-to-order Rate"].to_numpy() * scenario["click_to_order_rate"],
        1.0,
    )
    shop_tab_share = product_df["ShopTab GMV Share"].to_numpy()

    rows = []
    video_history = []
    global_week = 0

    for phase in phases:
        target_series = np.linspace(phase["gmv_start"], phase["gmv_end"], weeks_per_phase)

        for week_idx in range(weeks_per_phase):
            global_week += 1

            samples_total = float(phase["samples"])
            samples_p = samples_total * share

            new_videos_p = samples_p * videos_per_sample
            video_history.append(new_videos_p)

            active_videos_p = np.zeros(len(product_df))
            for age, weight in enumerate(CONTENT_DECAY_WEIGHTS):
                idx = len(video_history) - 1 - age
                if idx >= 0:
                    active_videos_p += video_history[idx] * weight

            organic_clicks_p = active_videos_p * clicks_per_video
            organic_orders_p = organic_clicks_p * click_to_order
            organic_gmv_p = organic_orders_p * aov

            ads_take_rate = float(phase["ads_take_rate"])
            if ads_take_rate * ads_roas >= 0.90:
                raise ValueError("Ads Take Rate x Ads ROAS 必须低于 90%，否则模型会不稳定")

            denominator = 1 - ads_take_rate * ads_roas
            total_gmv_p = organic_gmv_p / denominator
            paid_gmv_p = total_gmv_p - organic_gmv_p

            orders_p = total_gmv_p / aov
            shop_tab_gmv_p = total_gmv_p * shop_tab_share
            affiliate_gmv_p = total_gmv_p - shop_tab_gmv_p

            week_fee_rates = platform_fee_rate(global_week, promo_60d, base_fee_rates)
            cogs_p = total_gmv_p * (1 - gross_margin)
            platform_fee_p = total_gmv_p * week_fee_rates
            sample_cost_p = samples_p * (sample_product_cost + sample_shipping_cost)

            gmv = float(np.sum(total_gmv_p))
            orders = float(np.sum(orders_p))
            shop_tab_gmv = float(np.sum(shop_tab_gmv_p))
            affiliate_gmv = float(np.sum(affiliate_gmv_p))

            cogs = float(np.sum(cogs_p))
            platform_fee = float(np.sum(platform_fee_p))
            samples_cost = float(np.sum(sample_cost_p))
            fulfillment_cost = orders * fulfillment_per_order
            creator_commission = affiliate_gmv * affiliate_commission_rate
            ads_cost = gmv * ads_take_rate

            total_cost = cogs + platform_fee + samples_cost + fulfillment_cost + creator_commission + ads_cost
            profit = gmv - total_cost

            rows.append({
                "Phase": phase["name"],
                "Week in Phase": week_idx + 1,
                "Global Week": global_week,
                "Samples Sent": samples_total,
                "New Videos": float(np.sum(new_videos_p)),
                "Active Videos": float(np.sum(active_videos_p)),
                "Product Clicks": float(np.sum(organic_clicks_p)),
                "Orders": orders,
                "Organic Funnel GMV": float(np.sum(organic_gmv_p)),
                "Paid GMV Lift": float(np.sum(paid_gmv_p)),
                "GMV": gmv,
                "Target GMV": float(target_series[week_idx]),
                "Target Gap": gmv - float(target_series[week_idx]),
                "ShopTab GMV": shop_tab_gmv,
                "Affiliate Video GMV": affiliate_gmv,
                "COGS": cogs,
                "Gross Profit": gmv - cogs,
                "Platform Fee": platform_fee,
                "Creator Commission": creator_commission,
                "Ads Cost": ads_cost,
                "Samples Cost": samples_cost,
                "Fulfillment Cost": fulfillment_cost,
                "Growth Investment": samples_cost + ads_cost,
                "Total Cost": total_cost,
                "Profit": profit,
                "Ads Take Rate": ads_take_rate,
            })

    return pd.DataFrame(rows)


def summarize_phase(df):
    summary = df.groupby("Phase", as_index=False).agg({
        "Samples Sent": "sum",
        "New Videos": "sum",
        "Product Clicks": "sum",
        "Orders": "sum",
        "Organic Funnel GMV": "sum",
        "Paid GMV Lift": "sum",
        "GMV": "sum",
        "Target GMV": "sum",
        "Target Gap": "sum",
        "ShopTab GMV": "sum",
        "Affiliate Video GMV": "sum",
        "COGS": "sum",
        "Gross Profit": "sum",
        "Platform Fee": "sum",
        "Creator Commission": "sum",
        "Ads Cost": "sum",
        "Samples Cost": "sum",
        "Fulfillment Cost": "sum",
        "Growth Investment": "sum",
        "Total Cost": "sum",
        "Profit": "sum",
    })
    summary["Profit Margin"] = np.where(summary["GMV"] > 0, summary["Profit"] / summary["GMV"], 0)
    summary["GMV / Sample"] = np.where(summary["Samples Sent"] > 0, summary["GMV"] / summary["Samples Sent"], 0)
    return summary


def summarize_overall(df):
    total_gmv = df["GMV"].sum()
    total_profit = df["Profit"].sum()
    total_samples = df["Samples Sent"].sum()
    return pd.DataFrame([{
        "Total Samples": total_samples,
        "Total Videos": df["New Videos"].sum(),
        "Total Clicks": df["Product Clicks"].sum(),
        "Total Orders": df["Orders"].sum(),
        "Total GMV": total_gmv,
        "Total Target GMV": df["Target GMV"].sum(),
        "Total Cost": df["Total Cost"].sum(),
        "Total Profit": total_profit,
        "Growth Investment": df["Growth Investment"].sum(),
        "Profit Margin": total_profit / total_gmv if total_gmv > 0 else 0,
        "GMV / Sample": total_gmv / total_samples if total_samples > 0 else 0,
    }])


def first_positive_profit_week(df):
    hit = df[df["Profit"] > 0]
    return None if hit.empty else int(hit["Global Week"].iloc[0])


def first_cumulative_break_even_week(df):
    temp = df.copy()
    temp["Cumulative Profit"] = temp["Profit"].cumsum()
    hit = temp[temp["Cumulative Profit"] >= 0]
    return None if hit.empty else int(hit["Global Week"].iloc[0])


def make_weekly_chart(df, title, be_week=None):
    fig, ax = plt.subplots(figsize=(10, 5))
    add_phase_backgrounds(ax, df)

    ax.plot(df["Global Week"], df["GMV"], marker="o", linewidth=2, label="Forecast GMV", zorder=4)
    ax.plot(df["Global Week"], df["Target GMV"], linestyle="--", label="Target GMV", zorder=3)
    ax.plot(df["Global Week"], df["Total Cost"], marker="o", label="Total Cost", zorder=3)
    ax.plot(df["Global Week"], df["Profit"], marker="o", linewidth=2, label="Profit", zorder=4)
    ax.axhline(0, linewidth=1, color="#555555", zorder=2)

    if be_week is not None:
        point = df[df["Global Week"] == be_week]
        if not point.empty:
            y = float(point["Profit"].iloc[0])
            ax.scatter([be_week], [y], s=80, zorder=5)
            ax.axvline(be_week, linestyle="--", alpha=0.35, zorder=2)
            ax.annotate(f"Weekly BE: W{be_week}", xy=(be_week, y), xytext=(8, 8), textcoords="offset points")

    ax.set_title(title)
    ax.set_xlabel("Week")
    ax.set_ylabel("€")
    ax.grid(True, alpha=0.3, zorder=1)
    ax.legend()
    format_eur_axis(ax)
    fig.tight_layout()
    return fig


def make_cumulative_chart(df, be_week=None):
    temp = df.copy()
    temp["Cumulative Profit"] = temp["Profit"].cumsum()

    fig, ax = plt.subplots(figsize=(10, 5))
    add_phase_backgrounds(ax, temp)
    ax.plot(temp["Global Week"], temp["Cumulative Profit"], marker="o", linewidth=2, label="Cumulative Profit")
    ax.axhline(0, linewidth=1, color="#555555")

    if be_week is not None:
        point = temp[temp["Global Week"] == be_week]
        if not point.empty:
            y = float(point["Cumulative Profit"].iloc[0])
            ax.scatter([be_week], [y], s=80)
            ax.axvline(be_week, linestyle="--", alpha=0.35)
            ax.annotate(f"Cumulative BE: W{be_week}", xy=(be_week, y), xytext=(8, 8), textcoords="offset points")

    ax.set_title("Cumulative Profit Trend")
    ax.set_xlabel("Week")
    ax.set_ylabel("€")
    ax.grid(True, alpha=0.3)
    ax.legend()
    format_eur_axis(ax)
    fig.tight_layout()
    return fig


def make_funnel_chart(df):
    values = pd.Series({
        "Samples": df["Samples Sent"].sum(),
        "Videos": df["New Videos"].sum(),
        "Clicks": df["Product Clicks"].sum(),
        "Orders": df["Orders"].sum(),
    })

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(values.index, values.values)
    ax.set_title("Funnel Summary")
    ax.grid(True, axis="y", alpha=0.3)
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
    fig.tight_layout()
    return fig


def format_table(df, money_cols=None, pct_cols=None, number_cols=None):
    out = df.copy()
    for col in money_cols or []:
        if col in out.columns:
            out[col] = out[col].map(lambda x: money(x, 0))
    for col in pct_cols or []:
        if col in out.columns:
            out[col] = out[col].map(lambda x: pct(x, 1))
    for col in number_cols or []:
        if col in out.columns:
            out[col] = out[col].map(lambda x: f"{float(x):,.0f}")
    return out


def csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8-sig")


st.title("TikTok Shop Growth Visualizer")
st.caption("基于寄样、视频、点击、转化、GMV、成本和利润的 Streamlit 增长漏斗模拟器")
st.info("当前 subcategory 漏斗参数是临时 benchmark。拿到数据组真实数据后，请替换代码顶部的 FUNNEL_PRESETS。")


with st.sidebar:
    st.header("全局输入")

    n_products = st.number_input("产品数量", min_value=1, max_value=26, value=3, step=1)
    scenario_name = st.selectbox("情景假设", options=list(SCENARIOS.keys()), index=1)

    promo_60d = st.radio(
        "60天费率优惠",
        options=[True, False],
        format_func=lambda x: "是，前约60天平台费 5%" if x else "否，使用默认平台费",
        index=0,
    )

    fulfillment_per_order = st.number_input("履约成本 €/订单", min_value=0.0, value=6.0, step=0.5)
    sample_shipping_cost = st.number_input("样品物流成本 €/件", min_value=0.0, value=5.0, step=1.0)

    affiliate_commission_rate = st.slider("达人佣金", min_value=0.0, max_value=0.5, value=0.15, step=0.01)

    ads_roas = st.number_input(
        "广告 ROAS 假设",
        min_value=0.1,
        max_value=8.0,
        value=3.0,
        step=0.1,
        help="例如 3.0 表示 €1 广告费带来 €3 GMV。",
    )

    weeks_per_phase = st.slider("每阶段周数", min_value=2, max_value=8, value=4, step=1)

    st.header("阶段控制")
    phase_inputs = []

    for idx, default in enumerate(PHASE_DEFAULTS):
        st.subheader(default["name"])

        gmv_start = st.number_input(
            f"目标 GMV 起点 - {default['name']}",
            min_value=0.0,
            value=float(default["gmv_start"]),
            step=1000.0,
            key=f"phase_gmv_start_{idx}",
        )

        gmv_end = st.number_input(
            f"目标 GMV 终点 - {default['name']}",
            min_value=0.0,
            value=float(default["gmv_end"]),
            step=1000.0,
            key=f"phase_gmv_end_{idx}",
        )

        ads_take_rate = st.slider(
            f"Ads Take Rate - {default['name']}",
            min_value=0.0,
            max_value=0.30,
            value=float(default["ads_take_rate"]),
            step=0.01,
            key=f"phase_ads_{idx}",
            help="内部 KPI 口径：广告花费 / 总 GMV。",
        )

        samples = st.number_input(
            f"每周总寄样数 - {default['name']}",
            min_value=0,
            value=int(default["samples"]),
            step=1,
            key=f"phase_samples_{idx}",
        )

        phase_inputs.append({
            "name": default["name"],
            "gmv_start": gmv_start,
            "gmv_end": gmv_end,
            "ads_take_rate": ads_take_rate,
            "samples": samples,
        })


st.subheader("产品设置")
st.caption("选择 subcategory 后会带出 AOV 和漏斗 benchmark。所有假设都可以手动修改。")


for i in range(int(n_products)):
    init_product_state(i, int(n_products))

    with st.container(border=True):
        st.markdown(f"**产品 {i + 1}**")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.text_input("产品名称", key=f"product_name_{i}")

        with c2:
            st.selectbox("大类", options=list(AOV_PRESETS.keys()), key=f"family_{i}")

        family = st.session_state[f"family_{i}"]
        presets = list(AOV_PRESETS[family].keys())

        if st.session_state[f"preset_{i}"] not in presets:
            st.session_state[f"preset_{i}"] = presets[0]

        with c3:
            st.selectbox("Subcategory", options=presets, key=f"preset_{i}")

        if st.button(f"应用类目 benchmark - 产品 {i + 1}", key=f"apply_benchmark_{i}"):
            apply_benchmark(i)
            st.rerun()

        c4, c5, c6 = st.columns(3)

        with c4:
            st.text_input(
                "寄样分配占比 (%)",
                key=f"sample_share_{i}",
                help="例如 50 或 20。不需要加起来等于 100，系统会自动标准化。",
            )

        with c5:
            st.number_input("AOV (€)", min_value=0.01, step=1.0, key=f"aov_{i}")

        with c6:
            st.selectbox("费率类型", options=["electronics", "other"], format_func=fee_label, key=f"fee_type_{i}")

        c7, c8, c9, c10 = st.columns(4)

        with c7:
            st.number_input("毛利率 (%)", min_value=5.0, max_value=90.0, step=1.0, key=f"gross_margin_pct_{i}")

        with c8:
            st.number_input("每个样品产出视频数", min_value=0.0, max_value=5.0, step=0.05, key=f"videos_per_sample_{i}")

        with c9:
            st.number_input("每条视频商品点击数", min_value=0.0, max_value=100000.0, step=10.0, key=f"clicks_per_video_{i}")

        with c10:
            st.number_input("点击到下单转化率 (%)", min_value=0.0, max_value=100.0, step=0.1, key=f"click_to_order_pct_{i}")

        st.slider(
            "ShopTab GMV 占比 (%)",
            min_value=0.0,
            max_value=100.0,
            step=1.0,
            key=f"shop_tab_share_pct_{i}",
            help="ShopTab / 商城成交不计达人销售佣金。",
        )


generate = st.button("生成模拟结果", type="primary")


if generate:
    try:
        product_df = build_product_df(int(n_products))

        df_all = build_weekly_model(
            product_df=product_df,
            phases=phase_inputs,
            weeks_per_phase=int(weeks_per_phase),
            scenario_name=scenario_name,
            promo_60d=bool(promo_60d),
            fulfillment_per_order=float(fulfillment_per_order),
            sample_shipping_cost=float(sample_shipping_cost),
            affiliate_commission_rate=float(affiliate_commission_rate),
            ads_roas=float(ads_roas),
        )

        phase_summary = summarize_phase(df_all)
        overall_summary = summarize_overall(df_all)

        weekly_be = first_positive_profit_week(df_all)
        cumulative_be = first_cumulative_break_even_week(df_all)

        st.subheader("产品组合与漏斗假设")

        product_display = product_df.copy()
        product_display["SampleShareNorm"] = product_display["SampleShareNorm"].map(lambda x: pct(x, 0))
        product_display["AOV"] = product_display["AOV"].map(lambda x: money(x, 2))
        product_display["Gross Margin"] = product_display["Gross Margin"].map(lambda x: pct(x, 0))
        product_display["Platform Fee Rate"] = product_display["Platform Fee Rate"].map(lambda x: pct(x, 0))
        product_display["Click-to-order Rate"] = product_display["Click-to-order Rate"].map(lambda x: pct(x, 1))
        product_display["ShopTab GMV Share"] = product_display["ShopTab GMV Share"].map(lambda x: pct(x, 0))

        st.dataframe(product_display, use_container_width=True)

        overall = overall_summary.iloc[0]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("总 GMV", money(overall["Total GMV"], 0))
        m2.metric("总利润", money(overall["Total Profit"], 0))
        m3.metric("利润率", pct(overall["Profit Margin"], 1))
        m4.metric("增长投入", money(overall["Growth Investment"], 0))

        m5, m6, m7, m8 = st.columns(4)
        m5.metric("寄样数", f"{overall['Total Samples']:,.0f}")
        m6.metric("产出视频数", f"{overall['Total Videos']:,.0f}")
        m7.metric("商品点击数", f"{overall['Total Clicks']:,.0f}")
        m8.metric("订单数", f"{overall['Total Orders']:,.0f}")

        st.subheader("图表")

        c1, c2 = st.columns(2)
        with c1:
            st.pyplot(make_weekly_chart(df_all, "Overall Weekly Trend", weekly_be))
        with c2:
            st.pyplot(make_cumulative_chart(df_all, cumulative_be))

        st.pyplot(make_funnel_chart(df_all))

        st.subheader("分阶段趋势")
        tabs = st.tabs([p["name"] for p in phase_inputs])

        for tab, phase in zip(tabs, phase_inputs):
            with tab:
                phase_df = df_all[df_all["Phase"] == phase["name"]].copy()
                phase_be = first_positive_profit_week(phase_df)
                st.pyplot(make_weekly_chart(phase_df, phase["name"], phase_be))

        money_cols = [
            "Organic Funnel GMV",
            "Paid GMV Lift",
            "GMV",
            "Target GMV",
            "Target Gap",
            "ShopTab GMV",
            "Affiliate Video GMV",
            "COGS",
            "Gross Profit",
            "Platform Fee",
            "Creator Commission",
            "Ads Cost",
            "Samples Cost",
            "Fulfillment Cost",
            "Growth Investment",
            "Total Cost",
            "Profit",
            "GMV / Sample",
        ]

        number_cols = ["Samples Sent", "New Videos", "Product Clicks", "Orders"]

        st.subheader("汇总")

        s1, s2 = st.columns(2)

        with s1:
            st.markdown("**阶段汇总**")
            st.dataframe(
                format_table(
                    phase_summary,
                    money_cols=money_cols,
                    pct_cols=["Profit Margin"],
                    number_cols=number_cols,
                ),
                use_container_width=True,
            )

        with s2:
            st.markdown("**整体汇总**")
            st.dataframe(
                format_table(
                    overall_summary,
                    money_cols=["Total GMV", "Total Target GMV", "Total Cost", "Total Profit", "Growth Investment", "GMV / Sample"],
                    pct_cols=["Profit Margin"],
                    number_cols=["Total Samples", "Total Videos", "Total Clicks", "Total Orders"],
                ),
                use_container_width=True,
            )

        st.subheader("Break-even 信号")

        b1, b2 = st.columns(2)

        with b1:
            if weekly_be is None:
                st.warning("首次单周盈利：未达到")
            else:
                st.success(f"首次单周盈利：第 {weekly_be} 周")

        with b2:
            if cumulative_be is None:
                st.warning("累计 Break-even：未达到")
            else:
                st.success(f"累计 Break-even：第 {cumulative_be} 周")

        st.subheader("每周明细")

        weekly_display = format_table(
            df_all,
            money_cols=money_cols,
            pct_cols=["Ads Take Rate"],
            number_cols=["Samples Sent", "New Videos", "Active Videos", "Product Clicks", "Orders"],
        )

        st.dataframe(weekly_display, use_container_width=True)

        d1, d2 = st.columns(2)

        with d1:
            st.download_button(
                "下载每周明细 CSV",
                data=csv_bytes(df_all),
                file_name="weekly_details.csv",
                mime="text/csv",
            )

        with d2:
            st.download_button(
                "下载阶段汇总 CSV",
                data=csv_bytes(phase_summary),
                file_name="phase_summary.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"输入错误：{e}")
