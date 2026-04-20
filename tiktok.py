import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


st.set_page_config(page_title="TikTok Shop Growth Visualizer", layout="wide")
plt.rcParams["axes.unicode_minus"] = False


# Public benchmark estimates. Replace CATEGORY_PRESETS with internal data
# when a data-team subcategory table is available.


PLATFORM_COMMISSION = {
    "Home Living": 0.09,
    "Electronics": 0.07,
    "FMCG": 0.09,
    "Beauty": 0.09,
    "Fashion": 0.09,
}


# Field meanings:
# aov: estimated Germany TikTok Shop AOV in EUR
# videos_per_sample: average videos generated per sample shipped
# clicks_per_video: estimated product clicks per creator video
# click_to_order_rate: product click -> order conversion
# shop_tab_share: GMV share from ShopTab/mall/search etc.; no creator commission
CATEGORY_PRESETS = {
    "Home Living": {
        "Kitchenware": {"aov": 29.90, "videos_per_sample": 0.40, "clicks_per_video": 90, "click_to_order_rate": 0.032, "shop_tab_share": 0.35},
        "Home Supplies": {"aov": 24.90, "videos_per_sample": 0.40, "clicks_per_video": 80, "click_to_order_rate": 0.035, "shop_tab_share": 0.35},
        "Textiles & Soft Furnishings": {"aov": 34.90, "videos_per_sample": 0.35, "clicks_per_video": 70, "click_to_order_rate": 0.028, "shop_tab_share": 0.38},
        "Tools & Hardware": {"aov": 27.90, "videos_per_sample": 0.30, "clicks_per_video": 55, "click_to_order_rate": 0.024, "shop_tab_share": 0.40},
        "Furniture": {"aov": 129.00, "videos_per_sample": 0.20, "clicks_per_video": 35, "click_to_order_rate": 0.010, "shop_tab_share": 0.45},
        "Home Improvement": {"aov": 39.90, "videos_per_sample": 0.30, "clicks_per_video": 55, "click_to_order_rate": 0.022, "shop_tab_share": 0.40},
        "Toys & Hobbies": {"aov": 24.90, "videos_per_sample": 0.35, "clicks_per_video": 75, "click_to_order_rate": 0.032, "shop_tab_share": 0.35},
        "Books, Magazines & Audio": {"aov": 18.90, "videos_per_sample": 0.25, "clicks_per_video": 35, "click_to_order_rate": 0.022, "shop_tab_share": 0.40},
        "Collectibles": {"aov": 39.90, "videos_per_sample": 0.35, "clicks_per_video": 70, "click_to_order_rate": 0.030, "shop_tab_share": 0.35},
    },
    "Electronics": {
        "Phones & Electronics": {"aov": 69.00, "videos_per_sample": 0.25, "clicks_per_video": 50, "click_to_order_rate": 0.018, "shop_tab_share": 0.42},
        "Computers & Office Equipment": {"aov": 89.00, "videos_per_sample": 0.20, "clicks_per_video": 40, "click_to_order_rate": 0.013, "shop_tab_share": 0.45},
        "Household Appliances": {"aov": 59.00, "videos_per_sample": 0.25, "clicks_per_video": 55, "click_to_order_rate": 0.018, "shop_tab_share": 0.42},
        "Automotive & Motorcycle": {"aov": 39.90, "videos_per_sample": 0.20, "clicks_per_video": 40, "click_to_order_rate": 0.015, "shop_tab_share": 0.45},
        "Smart Home Systems": {"aov": 79.00, "videos_per_sample": 0.22, "clicks_per_video": 45, "click_to_order_rate": 0.015, "shop_tab_share": 0.44},
        "Audio & Headphones": {"aov": 49.90, "videos_per_sample": 0.28, "clicks_per_video": 60, "click_to_order_rate": 0.020, "shop_tab_share": 0.40},
        "Mobile Accessories": {"aov": 19.90, "videos_per_sample": 0.35, "clicks_per_video": 80, "click_to_order_rate": 0.035, "shop_tab_share": 0.35},
    },
    "FMCG": {
        "Food & Beverages": {"aov": 18.90, "videos_per_sample": 0.45, "clicks_per_video": 95, "click_to_order_rate": 0.045, "shop_tab_share": 0.32},
        "Health": {"aov": 29.90, "videos_per_sample": 0.35, "clicks_per_video": 75, "click_to_order_rate": 0.035, "shop_tab_share": 0.35},
        "Baby & Maternity": {"aov": 34.90, "videos_per_sample": 0.40, "clicks_per_video": 80, "click_to_order_rate": 0.040, "shop_tab_share": 0.35},
        "Pet Supplies": {"aov": 24.90, "videos_per_sample": 0.45, "clicks_per_video": 85, "click_to_order_rate": 0.038, "shop_tab_share": 0.32},
        "Household Consumables": {"aov": 19.90, "videos_per_sample": 0.40, "clicks_per_video": 75, "click_to_order_rate": 0.040, "shop_tab_share": 0.35},
        "Personal Care Consumables": {"aov": 19.90, "videos_per_sample": 0.45, "clicks_per_video": 95, "click_to_order_rate": 0.050, "shop_tab_share": 0.30},
    },
    "Beauty": {
        "Beauty & Personal Care": {"aov": 24.90, "videos_per_sample": 0.50, "clicks_per_video": 120, "click_to_order_rate": 0.055, "shop_tab_share": 0.30},
        "Skincare": {"aov": 29.90, "videos_per_sample": 0.50, "clicks_per_video": 130, "click_to_order_rate": 0.060, "shop_tab_share": 0.28},
        "Makeup": {"aov": 22.90, "videos_per_sample": 0.55, "clicks_per_video": 140, "click_to_order_rate": 0.065, "shop_tab_share": 0.28},
        "Hair Care & Styling": {"aov": 34.90, "videos_per_sample": 0.45, "clicks_per_video": 105, "click_to_order_rate": 0.045, "shop_tab_share": 0.32},
        "Fragrance": {"aov": 39.90, "videos_per_sample": 0.30, "clicks_per_video": 60, "click_to_order_rate": 0.025, "shop_tab_share": 0.40},
        "Beauty Devices": {"aov": 59.00, "videos_per_sample": 0.35, "clicks_per_video": 85, "click_to_order_rate": 0.030, "shop_tab_share": 0.38},
        "Men's Grooming": {"aov": 24.90, "videos_per_sample": 0.35, "clicks_per_video": 75, "click_to_order_rate": 0.035, "shop_tab_share": 0.35},
    },
    "Fashion": {
        "Womenswear & Underwear": {"aov": 29.90, "videos_per_sample": 0.40, "clicks_per_video": 85, "click_to_order_rate": 0.036, "shop_tab_share": 0.35},
        "Menswear & Underwear": {"aov": 34.90, "videos_per_sample": 0.35, "clicks_per_video": 75, "click_to_order_rate": 0.032, "shop_tab_share": 0.35},
        "Fashion Accessories": {"aov": 19.90, "videos_per_sample": 0.45, "clicks_per_video": 95, "click_to_order_rate": 0.045, "shop_tab_share": 0.32},
        "Shoes": {"aov": 49.90, "videos_per_sample": 0.30, "clicks_per_video": 65, "click_to_order_rate": 0.028, "shop_tab_share": 0.38},
        "Luggage & Bags": {"aov": 45.90, "videos_per_sample": 0.25, "clicks_per_video": 50, "click_to_order_rate": 0.020, "shop_tab_share": 0.42},
        "Jewelry Accessories & Derivatives": {"aov": 24.90, "videos_per_sample": 0.45, "clicks_per_video": 95, "click_to_order_rate": 0.040, "shop_tab_share": 0.35},
        "Kids' Fashion": {"aov": 24.90, "videos_per_sample": 0.35, "clicks_per_video": 70, "click_to_order_rate": 0.032, "shop_tab_share": 0.38},
        "Modest Fashion": {"aov": 29.90, "videos_per_sample": 0.35, "clicks_per_video": 70, "click_to_order_rate": 0.032, "shop_tab_share": 0.38},
        "Sports & Outdoor": {"aov": 49.90, "videos_per_sample": 0.30, "clicks_per_video": 60, "click_to_order_rate": 0.022, "shop_tab_share": 0.38},
    },
}


PHASES = [
    {"key": "phase1", "name": "Phase 1 - Cold Start", "samples_per_sku": 30, "take_rate": 0.00, "color": "#EAF4FF"},
    {"key": "phase2", "name": "Phase 2 - Growth", "samples_per_sku": 25, "take_rate": 0.05, "color": "#EEFBEF"},
    {"key": "phase3", "name": "Phase 3 - Scale", "samples_per_sku": 20, "take_rate": 0.10, "color": "#FFF4E8"},
]

CONTENT_DECAY_WEIGHTS = [1.00, 0.55, 0.30, 0.15]
PROMO_WEEKS = 9
LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


TEXT = {
    "en": {
        "language": "Language",
        "title": "TikTok Shop Growth Visualizer",
        "caption": "Germany public-benchmark simulator for SKU samples, creator videos, clicks, GMV, costs, and profit",
        "global_inputs": "Global Inputs",
        "sku_count": "Number of SKUs",
        "promo": "60-day platform fee promo",
        "promo_yes": "Yes, 5% platform fee for first ~60 days",
        "promo_no": "No, use default category commission",
        "fulfillment": "Fulfillment €/order",
        "sample_shipping": "Sample shipping €/unit",
        "creator_commission": "Creator affiliate commission",
        "ads_roas": "Ads ROAS assumption",
        "weeks_phase": "Weeks / phase",
        "phase_controls": "Phase Controls",
        "phase1": "Phase 1 - Cold Start",
        "phase2": "Phase 2 - Growth",
        "phase3": "Phase 3 - Scale",
        "take_rate": "Ads Take Rate (%)",
        "samples_sku_week": "Samples / SKU / week",
        "sku_setup": "SKU Setup",
        "sku_caption": "Category selection auto-loads AOV and funnel assumptions. Electronics uses 7% platform commission; all other categories use 9%.",
        "sku_name": "SKU name",
        "category": "Category",
        "subcategory": "Subcategory",
        "gross_margin": "Gross Margin (%)",
        "platform_commission": "Platform Commission",
        "benchmark_expander": "View / adjust category funnel assumptions",
        "videos_sample": "Videos / sample",
        "clicks_video": "Clicks / video",
        "click_order": "Click-to-order (%)",
        "shoptab_share": "ShopTab GMV share (%)",
        "generate": "Generate Simulator",
        "sku_mix": "SKU Mix & Funnel Assumptions",
        "total_gmv": "Total GMV",
        "total_profit": "Total Profit",
        "profit_margin": "Profit Margin",
        "growth_investment": "Growth Investment",
        "samples_sent": "Samples Sent",
        "videos_generated": "Videos Generated",
        "product_clicks": "Product Clicks",
        "orders": "Orders",
        "charts": "Charts",
        "overall_weekly": "Overall Weekly Trend",
        "phase_trend": "Phase-by-Phase Trend",
        "summary": "Summary",
        "phase_summary": "Phase Summary",
        "overall_summary": "Overall Summary",
        "break_even": "Break-even Signals",
        "weekly_profit": "First positive weekly profit",
        "cumulative_be": "Cumulative break-even",
        "not_reached": "Not reached",
        "weekly_details": "Weekly Details",
        "download_weekly": "Download weekly details CSV",
        "download_phase": "Download phase summary CSV",
        "input_error": "Input error",
    },
    "zh": {
        "language": "语言",
        "title": "TikTok Shop Growth Visualizer",
        "caption": "基于德国公开 benchmark 的 SKU 寄样、达人视频、点击、GMV、成本和利润模拟器",
        "global_inputs": "全局输入",
        "sku_count": "SKU 数量",
        "promo": "60天平台费优惠",
        "promo_yes": "是，前约60天平台费 5%",
        "promo_no": "否，使用默认类目佣金",
        "fulfillment": "履约成本 €/订单",
        "sample_shipping": "样品物流成本 €/件",
        "creator_commission": "达人佣金",
        "ads_roas": "广告 ROAS 假设",
        "weeks_phase": "每阶段周数",
        "phase_controls": "阶段控制",
        "phase1": "阶段 1 - 冷启动",
        "phase2": "阶段 2 - 增长",
        "phase3": "阶段 3 - 放量",
        "take_rate": "Ads Take Rate (%)",
        "samples_sku_week": "每个 SKU 每周寄样数",
        "sku_setup": "SKU 设置",
        "sku_caption": "选择 Category/Subcategory 后会自动加载 AOV 和漏斗假设。Electronics 平台佣金为 7%，其他类目为 9%。",
        "sku_name": "SKU 名称",
        "category": "Category",
        "subcategory": "Subcategory",
        "gross_margin": "毛利率 (%)",
        "platform_commission": "平台佣金",
        "benchmark_expander": "查看 / 调整类目漏斗假设",
        "videos_sample": "每个样品产出视频数",
        "clicks_video": "每条视频商品点击数",
        "click_order": "点击到下单转化率 (%)",
        "shoptab_share": "ShopTab GMV 占比 (%)",
        "generate": "生成模拟结果",
        "sku_mix": "SKU 组合与漏斗假设",
        "total_gmv": "总 GMV",
        "total_profit": "总利润",
        "profit_margin": "利润率",
        "growth_investment": "增长投入",
        "samples_sent": "寄样数",
        "videos_generated": "产出视频数",
        "product_clicks": "商品点击数",
        "orders": "订单数",
        "charts": "图表",
        "overall_weekly": "整体周趋势",
        "phase_trend": "分阶段趋势",
        "summary": "汇总",
        "phase_summary": "阶段汇总",
        "overall_summary": "整体汇总",
        "break_even": "Break-even 信号",
        "weekly_profit": "首次单周盈利",
        "cumulative_be": "累计 Break-even",
        "not_reached": "未达到",
        "weekly_details": "每周明细",
        "download_weekly": "下载每周明细 CSV",
        "download_phase": "下载阶段汇总 CSV",
        "input_error": "输入错误",
    },
    "de": {},
    "nl": {},
}
TEXT["de"] = {
    **TEXT["en"],
    "language": "Sprache",
    "caption": "Deutschland-Benchmark-Simulator für SKU-Samples, Creator-Videos, Klicks, GMV, Kosten und Gewinn",
    "global_inputs": "Globale Eingaben",
    "sku_count": "Anzahl SKUs",
    "promo": "60-Tage-Plattformgebühr-Promo",
    "promo_yes": "Ja, 5% Plattformgebühr für die ersten ~60 Tage",
    "promo_no": "Nein, Standard-Kategoriekommission verwenden",
    "fulfillment": "Fulfillment €/Bestellung",
    "sample_shipping": "Sample-Versand €/Stück",
    "creator_commission": "Creator-Affiliate-Provision",
    "ads_roas": "Ads-ROAS-Annahme",
    "weeks_phase": "Wochen / Phase",
    "phase_controls": "Phasensteuerung",
    "phase1": "Phase 1 - Kaltstart",
    "phase2": "Phase 2 - Wachstum",
    "phase3": "Phase 3 - Skalierung",
    "samples_sku_week": "Samples / SKU / Woche",
    "sku_setup": "SKU-Einstellung",
    "sku_caption": "Die Kategorieauswahl lädt AOV und Funnel-Annahmen automatisch. Electronics nutzt 7% Plattformkommission; alle anderen Kategorien 9%.",
    "sku_name": "SKU-Name",
    "category": "Kategorie",
    "platform_commission": "Plattformkommission",
    "benchmark_expander": "Kategorie-Funnel-Annahmen anzeigen / anpassen",
    "videos_sample": "Videos / Sample",
    "clicks_video": "Klicks / Video",
    "click_order": "Klick-zu-Bestellung (%)",
    "shoptab_share": "ShopTab GMV-Anteil (%)",
    "generate": "Simulator erzeugen",
    "sku_mix": "SKU-Mix & Funnel-Annahmen",
    "total_gmv": "Gesamt-GMV",
    "total_profit": "Gesamtgewinn",
    "profit_margin": "Gewinnmarge",
    "growth_investment": "Wachstumsinvestition",
    "samples_sent": "Samples",
    "videos_generated": "Videos",
    "product_clicks": "Produktklicks",
    "orders": "Bestellungen",
    "charts": "Charts",
    "phase_trend": "Trend je Phase",
    "summary": "Zusammenfassung",
    "phase_summary": "Phasenübersicht",
    "overall_summary": "Gesamtübersicht",
    "break_even": "Break-even-Signale",
    "weekly_profit": "Erste positive Wochenprofitabilität",
    "cumulative_be": "Kumulierter Break-even",
    "not_reached": "Nicht erreicht",
    "weekly_details": "Wöchentliche Details",
    "download_weekly": "Wöchentliche Details CSV herunterladen",
    "download_phase": "Phasenübersicht CSV herunterladen",
    "input_error": "Eingabefehler",
}
TEXT["nl"] = {
    **TEXT["en"],
    "language": "Taal",
    "caption": "Duitse benchmark-simulator voor SKU-samples, creator-video's, clicks, GMV, kosten en winst",
    "global_inputs": "Algemene invoer",
    "sku_count": "Aantal SKU's",
    "promo": "60-dagen platform fee promo",
    "promo_yes": "Ja, 5% platform fee voor de eerste ~60 dagen",
    "promo_no": "Nee, standaard categoriecommissie gebruiken",
    "fulfillment": "Fulfillment €/order",
    "sample_shipping": "Sample verzending €/stuk",
    "creator_commission": "Creator affiliate commissie",
    "ads_roas": "Ads ROAS-aanname",
    "weeks_phase": "Weken / fase",
    "phase_controls": "Fase-instellingen",
    "phase1": "Fase 1 - Koude start",
    "phase2": "Fase 2 - Groei",
    "phase3": "Fase 3 - Schaalvergroting",
    "samples_sku_week": "Samples / SKU / week",
    "sku_setup": "SKU-instellingen",
    "sku_caption": "Categoriekeuze laadt AOV en funnelaannames automatisch. Electronics gebruikt 7% platformcommissie; alle andere categorieen 9%.",
    "sku_name": "SKU-naam",
    "category": "Categorie",
    "platform_commission": "Platformcommissie",
    "benchmark_expander": "Categorie-funnelaannames bekijken / aanpassen",
    "videos_sample": "Video's / sample",
    "clicks_video": "Clicks / video",
    "click_order": "Click-to-order (%)",
    "shoptab_share": "ShopTab GMV-aandeel (%)",
    "generate": "Simulator genereren",
    "sku_mix": "SKU-mix & funnelaannames",
    "total_gmv": "Totale GMV",
    "total_profit": "Totale winst",
    "profit_margin": "Winstmarge",
    "growth_investment": "Groei-investering",
    "samples_sent": "Samples",
    "videos_generated": "Video's",
    "product_clicks": "Productclicks",
    "orders": "Orders",
    "charts": "Grafieken",
    "phase_trend": "Trend per fase",
    "summary": "Samenvatting",
    "phase_summary": "Faseoverzicht",
    "overall_summary": "Totaaloverzicht",
    "break_even": "Break-even signalen",
    "weekly_profit": "Eerste positieve weekwinst",
    "cumulative_be": "Cumulatieve break-even",
    "not_reached": "Niet bereikt",
    "weekly_details": "Wekelijkse details",
    "download_weekly": "Wekelijkse details CSV downloaden",
    "download_phase": "Faseoverzicht CSV downloaden",
    "input_error": "Invoerfout",
}


LANG_LABELS = {
    "en": "English",
    "zh": "简体中文",
    "de": "Deutsch",
    "nl": "Nederlands",
}


def money(value, digits=0):
    return f"€{float(value):,.{digits}f}"


def pct(value, digits=1):
    return f"{float(value):.{digits}%}"


with st.sidebar:
    lang = st.selectbox(
        "Language",
        options=["en", "zh", "de", "nl"],
        format_func=lambda code: LANG_LABELS[code],
        index=1,
    )

T = TEXT[lang]


def phase_label(phase):
    return T[phase["key"]]


def csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8-sig")


def format_eur_axis(ax):
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("€{x:,.0f}"))


def get_preset(category, subcategory):
    return CATEGORY_PRESETS[category][subcategory]


def apply_category_defaults(i):
    category = st.session_state[f"category_{i}"]
    subcategory = st.session_state[f"subcategory_{i}"]
    preset = get_preset(category, subcategory)
    st.session_state[f"aov_{i}"] = float(preset["aov"])
    st.session_state[f"platform_fee_{i}"] = PLATFORM_COMMISSION[category]
    st.session_state[f"videos_per_sample_{i}"] = float(preset["videos_per_sample"])
    st.session_state[f"clicks_per_video_{i}"] = float(preset["clicks_per_video"])
    st.session_state[f"click_to_order_pct_{i}"] = float(preset["click_to_order_rate"] * 100)
    st.session_state[f"shop_tab_share_pct_{i}"] = float(preset["shop_tab_share"] * 100)
    st.session_state[f"last_category_{i}"] = category
    st.session_state[f"last_subcategory_{i}"] = subcategory


def refresh_if_category_changed(i):
    if (
        st.session_state.get(f"last_category_{i}") != st.session_state[f"category_{i}"]
        or st.session_state.get(f"last_subcategory_{i}") != st.session_state[f"subcategory_{i}"]
    ):
        apply_category_defaults(i)


def initialize_sku(i):
    if f"sku_name_{i}" not in st.session_state:
        st.session_state[f"sku_name_{i}"] = LETTERS[i]
    if f"category_{i}" not in st.session_state:
        st.session_state[f"category_{i}"] = "Home Living"

    category = st.session_state[f"category_{i}"]
    subcategories = list(CATEGORY_PRESETS[category].keys())
    if f"subcategory_{i}" not in st.session_state or st.session_state[f"subcategory_{i}"] not in subcategories:
        st.session_state[f"subcategory_{i}"] = subcategories[0]

    if f"aov_{i}" not in st.session_state:
        apply_category_defaults(i)
    if f"gross_margin_pct_{i}" not in st.session_state:
        st.session_state[f"gross_margin_pct_{i}"] = 40.0


def build_product_df(n_skus):
    rows = []
    for i in range(int(n_skus)):
        rows.append({
            "SKU": st.session_state[f"sku_name_{i}"],
            "Category": st.session_state[f"category_{i}"],
            "Subcategory": st.session_state[f"subcategory_{i}"],
            "AOV": float(st.session_state[f"aov_{i}"]),
            "Gross Margin": float(st.session_state[f"gross_margin_pct_{i}"]) / 100,
            "Platform Fee Rate": PLATFORM_COMMISSION[st.session_state[f"category_{i}"]],
            "Videos / Sample": float(st.session_state[f"videos_per_sample_{i}"]),
            "Clicks / Video": float(st.session_state[f"clicks_per_video_{i}"]),
            "Click-to-order Rate": float(st.session_state[f"click_to_order_pct_{i}"]) / 100,
            "ShopTab GMV Share": float(st.session_state[f"shop_tab_share_pct_{i}"]) / 100,
        })

    df = pd.DataFrame(rows)
    if df["SKU"].astype(str).str.strip().eq("").any():
        raise ValueError("SKU name cannot be empty.")
    if df["AOV"].le(0).any():
        raise ValueError("AOV must be greater than 0.")
    if df["Gross Margin"].lt(0.05).any() or df["Gross Margin"].gt(0.90).any():
        raise ValueError("Gross margin must be between 5% and 90%.")
    if df["Videos / Sample"].lt(0).any() or df["Clicks / Video"].lt(0).any():
        raise ValueError("Funnel values cannot be negative.")
    if df["Click-to-order Rate"].lt(0).any() or df["Click-to-order Rate"].gt(1).any():
        raise ValueError("Click-to-order rate must be between 0% and 100%.")
    if df["ShopTab GMV Share"].lt(0).any() or df["ShopTab GMV Share"].gt(1).any():
        raise ValueError("ShopTab GMV share must be between 0% and 100%.")
    return df


def build_weekly_model(
    product_df,
    phase_inputs,
    weeks_per_phase,
    promo_60d,
    fulfillment_per_order,
    sample_shipping_cost,
    affiliate_commission_rate,
    ads_roas,
):
    aov = product_df["AOV"].to_numpy()
    gross_margin = product_df["Gross Margin"].to_numpy()
    platform_fee_rates = product_df["Platform Fee Rate"].to_numpy()
    product_cost_per_unit = aov * (1 - gross_margin)
    sample_all_in_cost_per_unit = product_cost_per_unit + float(sample_shipping_cost)

    videos_per_sample = product_df["Videos / Sample"].to_numpy()
    clicks_per_video = product_df["Clicks / Video"].to_numpy()
    click_to_order_rate = product_df["Click-to-order Rate"].to_numpy()
    shop_tab_share = product_df["ShopTab GMV Share"].to_numpy()

    rows = []
    video_history = []
    global_week = 0

    for phase in phase_inputs:
        for week_idx in range(int(weeks_per_phase)):
            global_week += 1

            samples_p = np.full(len(product_df), float(phase["samples_per_sku"]))
            new_videos_p = samples_p * videos_per_sample
            video_history.append(new_videos_p)

            active_videos_p = np.zeros(len(product_df))
            for age, weight in enumerate(CONTENT_DECAY_WEIGHTS):
                history_idx = len(video_history) - 1 - age
                if history_idx >= 0:
                    active_videos_p += video_history[history_idx] * weight

            organic_clicks_p = active_videos_p * clicks_per_video
            organic_orders_p = organic_clicks_p * click_to_order_rate
            organic_gmv_p = organic_orders_p * aov

            take_rate = float(phase["take_rate"])
            if take_rate * ads_roas >= 0.90:
                raise ValueError("Take Rate x Ads ROAS must be below 90%.")

            total_gmv_p = organic_gmv_p / (1 - take_rate * ads_roas)
            paid_gmv_p = total_gmv_p - organic_gmv_p
            orders_p = total_gmv_p / aov

            shop_tab_gmv_p = total_gmv_p * shop_tab_share
            affiliate_gmv_p = total_gmv_p - shop_tab_gmv_p

            if promo_60d and global_week <= PROMO_WEEKS:
                week_platform_fee_rates = np.full(len(product_df), 0.05)
            else:
                week_platform_fee_rates = platform_fee_rates

            cogs_p = total_gmv_p * (1 - gross_margin)
            platform_fee_p = total_gmv_p * week_platform_fee_rates
            samples_cost_p = samples_p * sample_all_in_cost_per_unit

            gmv = float(np.sum(total_gmv_p))
            orders = float(np.sum(orders_p))
            affiliate_gmv = float(np.sum(affiliate_gmv_p))
            cogs = float(np.sum(cogs_p))
            platform_fee = float(np.sum(platform_fee_p))
            samples_cost = float(np.sum(samples_cost_p))
            fulfillment_cost = orders * float(fulfillment_per_order)
            creator_commission = affiliate_gmv * float(affiliate_commission_rate)
            ads_cost = gmv * take_rate
            total_cost = cogs + platform_fee + creator_commission + ads_cost + samples_cost + fulfillment_cost

            rows.append({
                "Phase": phase_label(phase),
                "Phase Key": phase["key"],
                "Week in Phase": week_idx + 1,
                "Global Week": global_week,
                "Samples Sent": float(np.sum(samples_p)),
                "New Videos": float(np.sum(new_videos_p)),
                "Active Videos": float(np.sum(active_videos_p)),
                "Product Clicks": float(np.sum(organic_clicks_p)),
                "Orders": orders,
                "Organic Funnel GMV": float(np.sum(organic_gmv_p)),
                "Paid GMV Lift": float(np.sum(paid_gmv_p)),
                "GMV": gmv,
                "ShopTab GMV": float(np.sum(shop_tab_gmv_p)),
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
                "Profit": gmv - total_cost,
                "Ads Take Rate": take_rate,
            })

    return pd.DataFrame(rows)


def build_phase_summary(df):
    summary = df.groupby(["Phase Key", "Phase"], as_index=False).agg({
        "Samples Sent": "sum",
        "New Videos": "sum",
        "Product Clicks": "sum",
        "Orders": "sum",
        "Organic Funnel GMV": "sum",
        "Paid GMV Lift": "sum",
        "GMV": "sum",
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


def build_overall_summary(df):
    total_gmv = df["GMV"].sum()
    total_profit = df["Profit"].sum()
    total_samples = df["Samples Sent"].sum()
    return pd.DataFrame([{
        "Total Samples": total_samples,
        "Total Videos": df["New Videos"].sum(),
        "Total Clicks": df["Product Clicks"].sum(),
        "Total Orders": df["Orders"].sum(),
        "Total GMV": total_gmv,
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


def add_phase_backgrounds(ax, df):
    phase_ranges = df.groupby(["Phase Key", "Phase"], as_index=False).agg(
        start_week=("Global Week", "min"),
        end_week=("Global Week", "max"),
    )
    color_map = {p["key"]: p["color"] for p in PHASES}
    for _, row in phase_ranges.iterrows():
        ax.axvspan(row["start_week"] - 0.5, row["end_week"] + 0.5, color=color_map[row["Phase Key"]], alpha=0.8, zorder=0)


def make_weekly_chart(df, title, break_even_week=None):
    fig, ax = plt.subplots(figsize=(10, 5))
    add_phase_backgrounds(ax, df)
    ax.plot(df["Global Week"], df["GMV"], marker="o", linewidth=2, label="Forecast GMV", zorder=4)
    ax.plot(df["Global Week"], df["Total Cost"], marker="o", label="Total Cost", zorder=3)
    ax.plot(df["Global Week"], df["Profit"], marker="o", linewidth=2, label="Profit", zorder=4)
    ax.axhline(0, linewidth=1, color="#555555", zorder=2)
    if break_even_week is not None:
        point = df[df["Global Week"] == break_even_week]
        if not point.empty:
            y = float(point["Profit"].iloc[0])
            ax.scatter([break_even_week], [y], s=80, zorder=5)
            ax.axvline(break_even_week, linestyle="--", alpha=0.35, zorder=2)
            ax.annotate(f"Weekly BE: W{break_even_week}", xy=(break_even_week, y), xytext=(8, 8), textcoords="offset points")
    ax.set_title(title)
    ax.set_xlabel("Week")
    ax.set_ylabel("€")
    ax.grid(True, alpha=0.3, zorder=1)
    ax.legend()
    format_eur_axis(ax)
    fig.tight_layout()
    return fig


def make_cumulative_profit_chart(df, break_even_week=None):
    temp = df.copy()
    temp["Cumulative Profit"] = temp["Profit"].cumsum()
    fig, ax = plt.subplots(figsize=(10, 5))
    add_phase_backgrounds(ax, temp)
    ax.plot(temp["Global Week"], temp["Cumulative Profit"], marker="o", linewidth=2, label="Cumulative Profit", zorder=3)
    ax.axhline(0, linewidth=1, color="#555555", zorder=2)
    if break_even_week is not None:
        point = temp[temp["Global Week"] == break_even_week]
        if not point.empty:
            y = float(point["Cumulative Profit"].iloc[0])
            ax.scatter([break_even_week], [y], s=80, zorder=5)
            ax.axvline(break_even_week, linestyle="--", alpha=0.35, zorder=2)
            ax.annotate(f"Cumulative BE: W{break_even_week}", xy=(break_even_week, y), xytext=(8, 8), textcoords="offset points")
    ax.set_title("Cumulative Profit Trend")
    ax.set_xlabel("Week")
    ax.set_ylabel("€")
    ax.grid(True, alpha=0.3, zorder=1)
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


st.title(T["title"])
st.caption(T["caption"])

with st.sidebar:
    st.header(T["global_inputs"])
    n_skus = st.number_input(T["sku_count"], min_value=1, max_value=26, value=3, step=1)
    promo_60d = st.radio(
        T["promo"],
        options=[True, False],
        format_func=lambda x: T["promo_yes"] if x else T["promo_no"],
        index=0,
    )
    fulfillment_per_order = st.number_input(T["fulfillment"], min_value=0.0, value=6.0, step=0.5)
    sample_shipping_cost = st.number_input(T["sample_shipping"], min_value=0.0, value=5.0, step=1.0)
    affiliate_commission_rate = st.slider(T["creator_commission"], min_value=0.0, max_value=0.5, value=0.15, step=0.01)
    ads_roas = st.number_input(T["ads_roas"], min_value=0.1, max_value=8.0, value=3.0, step=0.1)
    weeks_per_phase = st.slider(T["weeks_phase"], min_value=2, max_value=8, value=4, step=1)

    st.header(T["phase_controls"])
    phase_inputs = []
    for idx, phase in enumerate(PHASES):
        st.subheader(phase_label(phase))
        take_rate = st.number_input(
            f"{T['take_rate']} - {phase_label(phase)}",
            min_value=0.0,
            max_value=30.0,
            value=float(phase["take_rate"] * 100),
            step=1.0,
            key=f"take_rate_{idx}",
        ) / 100
        samples_per_sku = st.number_input(
            f"{T['samples_sku_week']} - {phase_label(phase)}",
            min_value=0,
            value=int(phase["samples_per_sku"]),
            step=1,
            key=f"samples_per_sku_{idx}",
        )
        phase_inputs.append({**phase, "take_rate": take_rate, "samples_per_sku": samples_per_sku})

st.subheader(T["sku_setup"])
st.caption(T["sku_caption"])

for i in range(int(n_skus)):
    initialize_sku(i)
    with st.container(border=True):
        st.markdown(f"**SKU {i + 1}**")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.text_input(T["sku_name"], key=f"sku_name_{i}")
        with c2:
            st.selectbox(T["category"], options=list(CATEGORY_PRESETS.keys()), key=f"category_{i}")
        category = st.session_state[f"category_{i}"]
        subcategories = list(CATEGORY_PRESETS[category].keys())
        if st.session_state[f"subcategory_{i}"] not in subcategories:
            st.session_state[f"subcategory_{i}"] = subcategories[0]
        with c3:
            st.selectbox(T["subcategory"], options=subcategories, key=f"subcategory_{i}")

        refresh_if_category_changed(i)

        c4, c5, c6 = st.columns(3)
        with c4:
            st.number_input("AOV (€)", min_value=0.01, step=1.0, key=f"aov_{i}")
        with c5:
            st.number_input(T["gross_margin"], min_value=5.0, max_value=90.0, step=1.0, key=f"gross_margin_pct_{i}")
        with c6:
            st.metric(T["platform_commission"], pct(PLATFORM_COMMISSION[category], 0))

        with st.expander(T["benchmark_expander"], expanded=False):
            b1, b2, b3, b4 = st.columns(4)
            with b1:
                st.number_input(T["videos_sample"], min_value=0.0, max_value=5.0, step=0.05, key=f"videos_per_sample_{i}")
            with b2:
                st.number_input(T["clicks_video"], min_value=0.0, max_value=100000.0, step=10.0, key=f"clicks_per_video_{i}")
            with b3:
                st.number_input(T["click_order"], min_value=0.0, max_value=100.0, step=0.1, key=f"click_to_order_pct_{i}")
            with b4:
                st.number_input(T["shoptab_share"], min_value=0.0, max_value=100.0, step=1.0, key=f"shop_tab_share_pct_{i}")

generate = st.button(T["generate"], type="primary")

if generate:
    try:
        product_df = build_product_df(int(n_skus))
        df_all = build_weekly_model(
            product_df=product_df,
            phase_inputs=phase_inputs,
            weeks_per_phase=int(weeks_per_phase),
            promo_60d=bool(promo_60d),
            fulfillment_per_order=float(fulfillment_per_order),
            sample_shipping_cost=float(sample_shipping_cost),
            affiliate_commission_rate=float(affiliate_commission_rate),
            ads_roas=float(ads_roas),
        )
        phase_summary = build_phase_summary(df_all)
        overall_summary = build_overall_summary(df_all)
        weekly_be = first_positive_profit_week(df_all)
        cumulative_be = first_cumulative_break_even_week(df_all)

        st.subheader(T["sku_mix"])
        product_display = product_df.copy()
        product_display["AOV"] = product_display["AOV"].map(lambda x: money(x, 2))
        product_display["Gross Margin"] = product_display["Gross Margin"].map(lambda x: pct(x, 0))
        product_display["Platform Fee Rate"] = product_display["Platform Fee Rate"].map(lambda x: pct(x, 0))
        product_display["Click-to-order Rate"] = product_display["Click-to-order Rate"].map(lambda x: pct(x, 1))
        product_display["ShopTab GMV Share"] = product_display["ShopTab GMV Share"].map(lambda x: pct(x, 0))
        st.dataframe(product_display, use_container_width=True)

        overall = overall_summary.iloc[0]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(T["total_gmv"], money(overall["Total GMV"], 0))
        m2.metric(T["total_profit"], money(overall["Total Profit"], 0))
        m3.metric(T["profit_margin"], pct(overall["Profit Margin"], 1))
        m4.metric(T["growth_investment"], money(overall["Growth Investment"], 0))
        m5, m6, m7, m8 = st.columns(4)
        m5.metric(T["samples_sent"], f"{overall['Total Samples']:,.0f}")
        m6.metric(T["videos_generated"], f"{overall['Total Videos']:,.0f}")
        m7.metric(T["product_clicks"], f"{overall['Total Clicks']:,.0f}")
        m8.metric(T["orders"], f"{overall['Total Orders']:,.0f}")

        st.subheader(T["charts"])
        c1, c2 = st.columns(2)
        with c1:
            st.pyplot(make_weekly_chart(df_all, T["overall_weekly"], weekly_be))
        with c2:
            st.pyplot(make_cumulative_profit_chart(df_all, cumulative_be))
        st.pyplot(make_funnel_chart(df_all))

        st.subheader(T["phase_trend"])
        tabs = st.tabs([phase_label(p) for p in phase_inputs])
        for tab, phase in zip(tabs, phase_inputs):
            with tab:
                phase_df = df_all[df_all["Phase Key"] == phase["key"]].copy()
                st.pyplot(make_weekly_chart(phase_df, phase_label(phase), first_positive_profit_week(phase_df)))

        money_cols = [
            "Organic Funnel GMV", "Paid GMV Lift", "GMV", "ShopTab GMV",
            "Affiliate Video GMV", "COGS", "Gross Profit", "Platform Fee",
            "Creator Commission", "Ads Cost", "Samples Cost", "Fulfillment Cost",
            "Growth Investment", "Total Cost", "Profit", "GMV / Sample",
            "Total GMV", "Total Cost", "Total Profit",
        ]
        number_cols = [
            "Samples Sent", "New Videos", "Active Videos", "Product Clicks", "Orders",
            "Total Samples", "Total Videos", "Total Clicks", "Total Orders",
        ]

        st.subheader(T["summary"])
        s1, s2 = st.columns(2)
        with s1:
            st.markdown(f"**{T['phase_summary']}**")
            st.dataframe(
                format_table(phase_summary.drop(columns=["Phase Key"]), money_cols=money_cols, pct_cols=["Profit Margin"], number_cols=number_cols),
                use_container_width=True,
            )
        with s2:
            st.markdown(f"**{T['overall_summary']}**")
            st.dataframe(
                format_table(overall_summary, money_cols=money_cols, pct_cols=["Profit Margin"], number_cols=number_cols),
                use_container_width=True,
            )

        st.subheader(T["break_even"])
        b1, b2 = st.columns(2)
        b1.success(f"{T['weekly_profit']}: Week {weekly_be}") if weekly_be else b1.warning(f"{T['weekly_profit']}: {T['not_reached']}")
        b2.success(f"{T['cumulative_be']}: Week {cumulative_be}") if cumulative_be else b2.warning(f"{T['cumulative_be']}: {T['not_reached']}")

        st.subheader(T["weekly_details"])
        weekly_display = format_table(df_all.drop(columns=["Phase Key"]), money_cols=money_cols, pct_cols=["Ads Take Rate"], number_cols=number_cols)
        st.dataframe(weekly_display, use_container_width=True)

        d1, d2 = st.columns(2)
        d1.download_button(T["download_weekly"], data=csv_bytes(df_all), file_name="weekly_details.csv", mime="text/csv")
        d2.download_button(T["download_phase"], data=csv_bytes(phase_summary), file_name="phase_summary.csv", mime="text/csv")

    except Exception as e:
        st.error(f"{T['input_error']}: {e}")
