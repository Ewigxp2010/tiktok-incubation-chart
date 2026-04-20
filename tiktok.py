import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.font_manager as fm


plt.rcParams["axes.unicode_minus"] = False

for font_name in [
    "Noto Sans CJK SC",
    "Noto Sans CJK",
    "Microsoft YaHei",
    "SimHei",
    "PingFang SC",
    "Arial Unicode MS",
]:
    if any(font_name in f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [font_name, "DejaVu Sans"]
        break


st.set_page_config(
    page_title="TikTok Shop Growth Visualizer",
    layout="wide",
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
    },
}


# Public benchmark placeholders.
# Replace these with your internal subcategory data once your data team shares it.
FUNNEL_PRESETS = {
    "Home & Living": {
        "Kitchenware": {
            "videos_per_sample": 0.40,
            "clicks_per_video": 120,
            "click_to_order_rate": 0.038,
            "shop_tab_share": 0.30,
        },
        "Pet Supplies": {
            "videos_per_sample": 0.45,
            "clicks_per_video": 110,
            "click_to_order_rate": 0.040,
            "shop_tab_share": 0.28,
        },
        "Sports & Outdoor": {
            "videos_per_sample": 0.35,
            "clicks_per_video": 80,
            "click_to_order_rate": 0.025,
            "shop_tab_share": 0.32,
        },
        "Textiles & Soft Furnishings": {
            "videos_per_sample": 0.35,
            "clicks_per_video": 90,
            "click_to_order_rate": 0.030,
            "shop_tab_share": 0.35,
        },
        "Tools & Hardware": {
            "videos_per_sample": 0.35,
            "clicks_per_video": 90,
            "click_to_order_rate": 0.030,
            "shop_tab_share": 0.30,
        },
        "Luggage & Bags": {
            "videos_per_sample": 0.30,
            "clicks_per_video": 70,
            "click_to_order_rate": 0.025,
            "shop_tab_share": 0.35,
        },
        "Shoes": {
            "videos_per_sample": 0.35,
            "clicks_per_video": 85,
            "click_to_order_rate": 0.035,
            "shop_tab_share": 0.35,
        },
        "Menswear & Underwear": {
            "videos_per_sample": 0.35,
            "clicks_per_video": 95,
            "click_to_order_rate": 0.038,
            "shop_tab_share": 0.35,
        },
        "Modest Fashion": {
            "videos_per_sample": 0.35,
            "clicks_per_video": 90,
            "click_to_order_rate": 0.035,
            "shop_tab_share": 0.35,
        },
        "Womenswear & Underwear": {
            "videos_per_sample": 0.40,
            "clicks_per_video": 110,
            "click_to_order_rate": 0.042,
            "shop_tab_share": 0.35,
        },
        "Furniture": {
            "videos_per_sample": 0.25,
            "clicks_per_video": 45,
            "click_to_order_rate": 0.015,
            "shop_tab_share": 0.40,
        },
        "Home Improvement": {
            "videos_per_sample": 0.30,
            "clicks_per_video": 70,
            "click_to_order_rate": 0.025,
            "shop_tab_share": 0.35,
        },
        "Home Supplies": {
            "videos_per_sample": 0.40,
            "clicks_per_video": 100,
            "click_to_order_rate": 0.038,
            "shop_tab_share": 0.32,
        },
    },
    "Electronics": {
        "Phones & Electronics": {
            "videos_per_sample": 0.30,
            "clicks_per_video": 70,
            "click_to_order_rate": 0.025,
            "shop_tab_share": 0.35,
        },
        "Computers & Office Equipment": {
            "videos_per_sample": 0.25,
            "clicks_per_video": 55,
            "click_to_order_rate": 0.018,
            "shop_tab_share": 0.40,
        },
        "Household Appliances": {
            "videos_per_sample": 0.30,
            "clicks_per_video": 75,
            "click_to_order_rate": 0.025,
            "shop_tab_share": 0.35,
        },
        "Automotive & Motorcycle": {
            "videos_per_sample": 0.25,
            "clicks_per_video": 50,
            "click_to_order_rate": 0.020,
            "shop_tab_share": 0.35,
        },
        "Collectibles": {
            "videos_per_sample": 0.35,
            "clicks_per_video": 80,
            "click_to_order_rate": 0.035,
            "shop_tab_share": 0.30,
        },
        "Beauty & Personal Care": {
            "videos_per_sample": 0.50,
            "clicks_per_video": 150,
            "click_to_order_rate": 0.065,
            "shop_tab_share": 0.25,
        },
        "Baby & Maternity": {
            "videos_per_sample": 0.45,
            "clicks_per_video": 110,
            "click_to_order_rate": 0.050,
            "shop_tab_share": 0.30,
        },
        "Books, Magazines & Audio": {
            "videos_per_sample": 0.30,
            "clicks_per_video": 50,
            "click_to_order_rate": 0.025,
            "shop_tab_share": 0.35,
        },
    },
}


SCENARIO_MULTIPLIERS = {
    "conservative": {
        "videos_per_sample": 0.75,
        "clicks_per_video": 0.70,
        "click_to_order_rate": 0.75,
    },
    "base": {
        "videos_per_sample": 1.00,
        "clicks_per_video": 1.00,
        "click_to_order_rate": 1.00,
    },
    "aggressive": {
        "videos_per_sample": 1.25,
        "clicks_per_video": 1.30,
        "click_to_order_rate": 1.20,
    },
}


LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
PHASE_KEYS = ["phase1", "phase2", "phase3"]
CONTENT_DECAY_WEIGHTS = [1.00, 0.55, 0.30, 0.15]
PROMO_WEEKS = 9


PHASE_DEFAULTS = {
    "phase1": {
        "gmv_start": 2_000,
        "gmv_end": 10_000,
        "ads_take_rate": 0.00,
        "default_sku_samples": 30,
    },
    "phase2": {
        "gmv_start": 10_000,
        "gmv_end": 30_000,
        "ads_take_rate": 0.05,
        "default_sku_samples": 25,
    },
    "phase3": {
        "gmv_start": 30_000,
        "gmv_end": 100_000,
        "ads_take_rate": 0.10,
        "default_sku_samples": 20,
    },
}


PHASE_COLOR_KEYS = {
    "phase1": {"bg": "#EAF4FF", "badge_bg": "#DCEEFF", "badge_text": "#1D4E89"},
    "phase2": {"bg": "#EEFBEF", "badge_bg": "#DFF5E3", "badge_text": "#1E6B35"},
    "phase3": {"bg": "#FFF4E8", "badge_bg": "#FFE8D6", "badge_text": "#A14B00"},
}


ELECTRONICS_FEE_CATEGORIES = {
    "Phones & Electronics",
    "Computers & Office Equipment",
    "Household Appliances",
    "Automotive & Motorcycle",
}


# ======================
# i18n
# ======================
TEXT = {
    "en": {
        "app_title": "TikTok Shop Growth Visualizer",
        "app_caption": "Funnel-based Streamlit simulator for samples, videos, clicks, GMV, cost, and profit",
        "language": "Language",
        "global_inputs": "Global Inputs",
        "num_products": "No. of products",
        "scenario": "Scenario",
        "scenario_conservative": "Conservative",
        "scenario_base": "Base",
        "scenario_aggressive": "Aggressive",
        "promo_60d": "60-day fee promo",
        "promo_yes": "Yes (5% for first ~60 days)",
        "promo_no": "No promo",
        "fulfillment": "Fulfillment €/order",
        "sample_shipping": "Sample shipping €/unit",
        "affiliate_commission": "Affiliate commission",
        "ads_roas": "Ads ROAS assumption",
        "ads_roas_help": "Used to estimate paid GMV lift from ads take rate. Example: 3.0 means €1 ad spend drives €3 GMV.",
        "weeks_per_phase": "Weeks / phase",
        "phase_controls": "Phase Controls",
        "phase1": "Phase 1 - Cold Start",
        "phase2": "Phase 2 - Growth",
        "phase3": "Phase 3 - Breakout",
        "ads_rate": "Ads Take Rate",
        "ads_rate_help": "Internal KPI: ad spend as % of total GMV.",
        "samples_per_week": "Samples / week",
        "product_setup": "Product Setup",
        "product_setup_caption": "Choose a subcategory to load benchmark AOV and funnel assumptions. All assumptions can be manually overridden.",
        "apply_benchmark": "Apply category benchmark",
        "generate": "Generate simulator",
        "assumption_note": "Current funnel values are public benchmark placeholders. Replace them with your internal subcategory data when available.",
        "product_mix": "Product Mix & Funnel Assumptions",
        "charts": "Charts",
        "overall_weekly_trend": "Overall Weekly Trend",
        "cumulative_profit_trend": "Cumulative Profit Trend",
        "phase_by_phase": "Phase-by-Phase Weekly Trend",
        "summary": "Summary",
        "phase_summary": "Phase summary",
        "overall_summary": "Overall summary",
        "break_even_signals": "Break-even Signals",
        "weekly_details": "Weekly Details",
        "download_weekly": "Download weekly details CSV",
        "download_phase": "Download phase summary CSV",
        "total_gmv": "Total GMV",
        "total_profit": "Total Profit",
        "profit_margin": "Profit Margin",
        "total_samples": "Samples Sent",
        "total_videos": "Videos Generated",
        "total_clicks": "Product Clicks",
        "total_orders": "Orders",
        "growth_investment": "Growth Investment",
        "first_positive_profit": "First positive weekly profit",
        "cumulative_break_even": "Cumulative break-even",
        "not_reached": "Not reached",
        "weekly_be_label": "Weekly BE",
        "cumulative_be_label": "Cumulative BE",
        "week": "Week",
        "product": "Product",
        "preset": "Preset",
        "sku_samples": "SKU samples / week",
        "sku_samples_help": "Samples sent per week for this SKU in each phase.",
        "aov": "AOV (€)",
        "gross_margin": "Gross Margin (%)",
        "fee_type": "Fee Type",
        "electronics_fee": "Electronics (7%)",
        "other_fee": "Other (9%)",
        "family": "Family",
        "preset_category": "Preset Category",
        "platform_fee_default": "Platform Fee Rate Default",
        "input_error": "Input error",
        "ads_take_rate_col": "Ads Take Rate",
        "product_block": "Product",
        "gross_margin_help": "Enter gross margin as a percentage, e.g. 40 = 40%",
        "gmv_start": "Target GMV start",
        "gmv_end": "Target GMV end",
        "target_gmv_help": "Reference target line only. Forecast GMV is generated by the funnel.",
        "videos_per_sample": "Videos / sample",
        "clicks_per_video": "Clicks / video",
        "click_to_order": "Click-to-order (%)",
        "shop_tab_share": "ShopTab GMV share (%)",
        "shop_tab_share_help": "ShopTab / mall GMV does not pay affiliate creator commission.",
        "benchmark": "Benchmark",
        "funnel_summary": "Funnel summary",
        "cost_summary": "Cost summary",
    },
    "zh": {
        "app_title": "TikTok Shop Growth Visualizer",
        "app_caption": "基于寄样、视频、点击、GMV、成本和利润的 Streamlit 增长漏斗模拟器",
        "language": "语言",
        "global_inputs": "全局输入",
        "num_products": "产品数量",
        "scenario": "情景",
        "scenario_conservative": "保守",
        "scenario_base": "基准",
        "scenario_aggressive": "激进",
        "promo_60d": "60天费率优惠",
        "promo_yes": "是（前约60天 5%）",
        "promo_no": "否",
        "fulfillment": "履约成本 €/订单",
        "sample_shipping": "样品物流成本 €/件",
        "affiliate_commission": "达人佣金",
        "ads_roas": "广告 ROAS 假设",
        "ads_roas_help": "用于估算广告 take rate 带来的付费 GMV 放大。例如 3.0 表示 €1 广告费带来 €3 GMV。",
        "weeks_per_phase": "每阶段周数",
        "phase_controls": "阶段控制",
        "phase1": "阶段 1 - 冷启动",
        "phase2": "阶段 2 - 增长",
        "phase3": "阶段 3 - 爆发",
        "ads_rate": "Ads Take Rate",
        "ads_rate_help": "内部 KPI 口径：广告花费 / 总 GMV。",
        "samples_per_week": "每周寄样数",
        "product_setup": "产品设置",
        "product_setup_caption": "选择 subcategory 后会带出 AOV 和漏斗 benchmark；所有假设都可以手动修改。",
        "apply_benchmark": "应用类目 benchmark",
        "generate": "生成模拟结果",
        "assumption_note": "当前漏斗参数是基于公开信息的临时 benchmark。拿到数据组的真实 subcategory 数据后，建议替换这些值。",
        "product_mix": "产品组合与漏斗假设",
        "charts": "图表",
        "overall_weekly_trend": "整体周趋势",
        "cumulative_profit_trend": "累计利润趋势",
        "phase_by_phase": "分阶段周趋势",
        "summary": "汇总",
        "phase_summary": "阶段汇总",
        "overall_summary": "整体汇总",
        "break_even_signals": "Break-even 信号",
        "weekly_details": "每周明细",
        "download_weekly": "下载每周明细 CSV",
        "download_phase": "下载阶段汇总 CSV",
        "total_gmv": "总 GMV",
        "total_profit": "总利润",
        "profit_margin": "利润率",
        "total_samples": "寄样数",
        "total_videos": "产出视频数",
        "total_clicks": "商品点击数",
        "total_orders": "订单数",
        "growth_investment": "增长投入",
        "first_positive_profit": "首次单周盈利",
        "cumulative_break_even": "累计 Break-even",
        "not_reached": "未达到",
        "weekly_be_label": "单周 BE",
        "cumulative_be_label": "累计 BE",
        "week": "周",
        "product": "产品",
        "preset": "Preset",
        "sku_samples": "SKU 每周寄样数",
        "sku_samples_help": "这个 SKU 在每个阶段每周寄出的样品数量。",
        "aov": "AOV (€)",
        "gross_margin": "毛利率 (%)",
        "fee_type": "费率类型",
        "electronics_fee": "电子类 (7%)",
        "other_fee": "其他 (9%)",
        "family": "大类",
        "preset_category": "Preset 类目",
        "platform_fee_default": "默认平台费率",
        "input_error": "输入错误",
        "ads_take_rate_col": "Ads Take Rate",
        "product_block": "产品",
        "gross_margin_help": "请输入百分比，例如 40 = 40%",
        "gmv_start": "目标 GMV 起点",
        "gmv_end": "目标 GMV 终点",
        "target_gmv_help": "只作为参考目标线。预测 GMV 由寄样漏斗计算得出。",
        "videos_per_sample": "每个样品产出视频数",
        "clicks_per_video": "每条视频商品点击数",
        "click_to_order": "点击到下单转化率 (%)",
        "shop_tab_share": "ShopTab GMV 占比 (%)",
        "shop_tab_share_help": "ShopTab / 商城成交不计达人销售佣金。",
        "benchmark": "Benchmark",
        "funnel_summary": "漏斗汇总",
        "cost_summary": "成本汇总",
    },
    "de": {
        "app_title": "TikTok Shop Growth Visualizer",
        "app_caption": "Streamlit-Funnel-Simulator für Samples, Videos, Klicks, GMV, Kosten und Gewinn",
        "language": "Sprache",
        "global_inputs": "Globale Eingaben",
        "num_products": "Anzahl Produkte",
        "scenario": "Szenario",
        "scenario_conservative": "Konservativ",
        "scenario_base": "Basis",
        "scenario_aggressive": "Ambitioniert",
        "promo_60d": "60-Tage-Gebührenpromo",
        "promo_yes": "Ja (5% für die ersten ~60 Tage)",
        "promo_no": "Keine Promo",
        "fulfillment": "Fulfillment €/Bestellung",
        "sample_shipping": "Sample-Versand €/Stück",
        "affiliate_commission": "Affiliate-Provision",
        "ads_roas": "Ads-ROAS-Annahme",
        "ads_roas_help": "Schätzt den bezahlten GMV-Uplift aus Ads Take Rate. Beispiel: 3,0 bedeutet €1 Ads Spend erzeugt €3 GMV.",
        "weeks_per_phase": "Wochen / Phase",
        "phase_controls": "Phasensteuerung",
        "phase1": "Phase 1 - Kaltstart",
        "phase2": "Phase 2 - Wachstum",
        "phase3": "Phase 3 - Skalierung",
        "ads_rate": "Ads Take Rate",
        "ads_rate_help": "Interne KPI: Ads Spend als Anteil am Gesamt-GMV.",
        "samples_per_week": "Samples / Woche",
        "product_setup": "Produkteinstellung",
        "product_setup_caption": "Wähle eine Subcategory, um AOV und Funnel-Benchmarks zu laden. Alle Annahmen können überschrieben werden.",
        "apply_benchmark": "Kategorie-Benchmark anwenden",
        "generate": "Simulator erzeugen",
        "assumption_note": "Die Funnel-Werte sind öffentliche Benchmark-Platzhalter. Ersetze sie durch interne Subcategory-Daten, sobald verfügbar.",
        "product_mix": "Produktmix & Funnel-Annahmen",
        "charts": "Charts",
        "overall_weekly_trend": "Gesamter Wochenverlauf",
        "cumulative_profit_trend": "Kumulierter Gewinnverlauf",
        "phase_by_phase": "Wochenverlauf je Phase",
        "summary": "Zusammenfassung",
        "phase_summary": "Phasenübersicht",
        "overall_summary": "Gesamtübersicht",
        "break_even_signals": "Break-even-Signale",
        "weekly_details": "Wöchentliche Details",
        "download_weekly": "Wöchentliche Details als CSV herunterladen",
        "download_phase": "Phasenübersicht als CSV herunterladen",
        "total_gmv": "Gesamt-GMV",
        "total_profit": "Gesamtgewinn",
        "profit_margin": "Gewinnmarge",
        "total_samples": "Samples",
        "total_videos": "Videos",
        "total_clicks": "Produktklicks",
        "total_orders": "Bestellungen",
        "growth_investment": "Wachstumsinvestition",
        "first_positive_profit": "Erste positive Wochenprofitabilität",
        "cumulative_break_even": "Kumulierter Break-even",
        "not_reached": "Nicht erreicht",
        "weekly_be_label": "Wochen-BE",
        "cumulative_be_label": "Kumulierter BE",
        "week": "Woche",
        "product": "Produkt",
        "preset": "Preset",
        "sku_samples": "SKU Samples / Woche",
        "sku_samples_help": "Samples pro Woche für dieses SKU in jeder Phase.",
        "aov": "AOV (€)",
        "gross_margin": "Bruttomarge (%)",
        "fee_type": "Gebührentyp",
        "electronics_fee": "Elektronik (7%)",
        "other_fee": "Sonstige (9%)",
        "family": "Familie",
        "preset_category": "Preset-Kategorie",
        "platform_fee_default": "Standard-Plattformgebühr",
        "input_error": "Eingabefehler",
        "ads_take_rate_col": "Ads Take Rate",
        "product_block": "Produkt",
        "gross_margin_help": "Bruttomarge in Prozent eingeben, z. B. 40 = 40%",
        "gmv_start": "Ziel-GMV Start",
        "gmv_end": "Ziel-GMV Ende",
        "target_gmv_help": "Nur Referenzlinie. Forecast-GMV wird aus dem Funnel berechnet.",
        "videos_per_sample": "Videos / Sample",
        "clicks_per_video": "Klicks / Video",
        "click_to_order": "Klick-zu-Bestellung (%)",
        "shop_tab_share": "ShopTab GMV-Anteil (%)",
        "shop_tab_share_help": "ShopTab/Mall-GMV zahlt keine Creator-Provision.",
        "benchmark": "Benchmark",
        "funnel_summary": "Funnel-Übersicht",
        "cost_summary": "Kostenübersicht",
    },
    "nl": {
        "app_title": "TikTok Shop Growth Visualizer",
        "app_caption": "Streamlit-funnelsimulator voor samples, video's, clicks, GMV, kosten en winst",
        "language": "Taal",
        "global_inputs": "Algemene invoer",
        "num_products": "Aantal producten",
        "scenario": "Scenario",
        "scenario_conservative": "Conservatief",
        "scenario_base": "Basis",
        "scenario_aggressive": "Ambitieus",
        "promo_60d": "60-dagen fee promo",
        "promo_yes": "Ja (5% gedurende de eerste ~60 dagen)",
        "promo_no": "Geen promo",
        "fulfillment": "Fulfillment €/bestelling",
        "sample_shipping": "Sample verzending €/stuk",
        "affiliate_commission": "Affiliate commissie",
        "ads_roas": "Ads ROAS-aanname",
        "ads_roas_help": "Schat betaalde GMV-uplift op basis van ads take rate. Voorbeeld: 3,0 betekent €1 advertentie-uitgave levert €3 GMV op.",
        "weeks_per_phase": "Weken / fase",
        "phase_controls": "Fase-instellingen",
        "phase1": "Fase 1 - Koude start",
        "phase2": "Fase 2 - Groei",
        "phase3": "Fase 3 - Doorbraak",
        "ads_rate": "Ads Take Rate",
        "ads_rate_help": "Interne KPI: advertentie-uitgaven als % van totale GMV.",
        "samples_per_week": "Samples / week",
        "product_setup": "Productinstellingen",
        "product_setup_caption": "Kies een subcategory om AOV en funnelbenchmarks te laden. Alle aannames kunnen handmatig worden aangepast.",
        "apply_benchmark": "Categoriebenchmark toepassen",
        "generate": "Simulator genereren",
        "assumption_note": "De huidige funnelwaarden zijn publieke benchmark placeholders. Vervang ze door interne subcategory-data zodra beschikbaar.",
        "product_mix": "Productmix & funnelaannames",
        "charts": "Grafieken",
        "overall_weekly_trend": "Totale wekelijkse trend",
        "cumulative_profit_trend": "Cumulatieve winsttrend",
        "phase_by_phase": "Wekelijkse trend per fase",
        "summary": "Samenvatting",
        "phase_summary": "Faseoverzicht",
        "overall_summary": "Totaaloverzicht",
        "break_even_signals": "Break-even signalen",
        "weekly_details": "Wekelijkse details",
        "download_weekly": "Download wekelijkse details CSV",
        "download_phase": "Download faseoverzicht CSV",
        "total_gmv": "Totale GMV",
        "total_profit": "Totale winst",
        "profit_margin": "Winstmarge",
        "total_samples": "Samples",
        "total_videos": "Video's",
        "total_clicks": "Productclicks",
        "total_orders": "Orders",
        "growth_investment": "Groei-investering",
        "first_positive_profit": "Eerste positieve weekwinst",
        "cumulative_break_even": "Cumulatieve break-even",
        "not_reached": "Niet bereikt",
        "weekly_be_label": "Wekelijkse BE",
        "cumulative_be_label": "Cumulatieve BE",
        "week": "Week",
        "product": "Product",
        "preset": "Preset",
        "sku_samples": "SKU samples / week",
        "sku_samples_help": "Samples per week voor deze SKU in elke fase.",
        "aov": "AOV (€)",
        "gross_margin": "Brutomarge (%)",
        "fee_type": "Fee type",
        "electronics_fee": "Elektronica (7%)",
        "other_fee": "Overig (9%)",
        "family": "Familie",
        "preset_category": "Preset-categorie",
        "platform_fee_default": "Standaard platform fee",
        "input_error": "Invoerfout",
        "ads_take_rate_col": "Ads Take Rate",
        "product_block": "Product",
        "gross_margin_help": "Voer brutomarge in als percentage, bijv. 40 = 40%",
        "gmv_start": "Doel-GMV start",
        "gmv_end": "Doel-GMV einde",
        "target_gmv_help": "Alleen referentielijn. Forecast-GMV wordt door de funnel berekend.",
        "videos_per_sample": "Video's / sample",
        "clicks_per_video": "Clicks / video",
        "click_to_order": "Click-to-order (%)",
        "shop_tab_share": "ShopTab GMV-aandeel (%)",
        "shop_tab_share_help": "ShopTab/mall-GMV betaalt geen creatorcommissie.",
        "benchmark": "Benchmark",
        "funnel_summary": "Funneloverzicht",
        "cost_summary": "Kostenoverzicht",
    },
}


LANG_LABELS = {
    "en": "English",
    "zh": "简体中文",
    "de": "Deutsch",
    "nl": "Nederlands",
}


# ======================
# Language
# ======================
with st.sidebar:
    lang = st.selectbox(
        "Language",
        options=["en", "zh", "de", "nl"],
        format_func=lambda x: LANG_LABELS[x],
        index=0,
    )

T = TEXT[lang]


# ======================
# Helpers
# ======================
def phase_label(phase_key: str) -> str:
    return T[phase_key]


def parse_percent_text(value) -> float:
    if value is None:
        return 0.0
    text = str(value).strip().replace("%", "").replace(",", ".")
    if text == "":
        return 0.0
    return float(text)


def money(v: float, digits: int = 0) -> str:
    return f"€{v:,.{digits}f}"


def pct(v: float, digits: int = 1) -> str:
    return f"{v:.{digits}%}"


def get_benchmark(family: str, preset: str) -> dict:
    benchmark = FUNNEL_PRESETS[family][preset].copy()
    benchmark["aov"] = AOV_PRESETS[family][preset]
    return benchmark


def guess_fee_type(preset: str) -> str:
    return "electronics" if preset in ELECTRONICS_FEE_CATEGORIES else "other"


def fee_label(fee_type: str) -> str:
    return T["electronics_fee"] if fee_type == "electronics" else T["other_fee"]


def format_eur_axis(ax):
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("€{x:,.0f}"))


def platform_fee_rates_for_week(
    global_week: int,
    promo_60d: bool,
    fee_type_series: pd.Series,
) -> np.ndarray:
    if promo_60d and global_week <= PROMO_WEEKS:
        return np.full(len(fee_type_series), 0.05)
    return fee_type_series.to_numpy()


def build_phase_inputs():
    phase_inputs = []
    for phase_key in PHASE_KEYS:
        defaults = PHASE_DEFAULTS[phase_key]
        phase_inputs.append({
            "key": phase_key,
            "name": phase_label(phase_key),
            "gmv_start": defaults["gmv_start"],
            "gmv_end": defaults["gmv_end"],
            "ads_take_rate": defaults["ads_take_rate"],
            "default_sku_samples": defaults["default_sku_samples"],
        })
    return phase_inputs


def add_phase_backgrounds(ax, df: pd.DataFrame):
    phase_ranges = (
        df.groupby(["Phase Key", "Phase"], as_index=False)
        .agg(
            start_week=("Global Week", "min"),
            end_week=("Global Week", "max"),
        )
    )

    for _, row in phase_ranges.iterrows():
        phase_key = row["Phase Key"]
        color = PHASE_COLOR_KEYS.get(phase_key, {}).get("bg", "#F5F5F5")
        ax.axvspan(
            row["start_week"] - 0.5,
            row["end_week"] + 0.5,
            color=color,
            alpha=0.8,
            zorder=0,
        )


def render_phase_badges(phase_keys):
    html_parts = []
    for pkey in phase_keys:
        style = PHASE_COLOR_KEYS.get(
            pkey,
            {"badge_bg": "#EEEEEE", "badge_text": "#333333"},
        )
        html_parts.append(
            f"""
            <span style="
                display:inline-block;
                padding:8px 14px;
                margin-right:10px;
                margin-bottom:8px;
                border-radius:999px;
                background:{style['badge_bg']};
                color:{style['badge_text']};
                font-weight:600;
                font-size:14px;
            ">
                {phase_label(pkey)}
            </span>
            """
        )
    st.markdown("".join(html_parts), unsafe_allow_html=True)


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def build_product_df_from_ui(n_products: int) -> pd.DataFrame:
    rows = []

    for i in range(int(n_products)):
        family = st.session_state[f"family_{i}"]
        preset = st.session_state[f"preset_{i}"]
        fee_type = st.session_state[f"fee_type_{i}"]
        fee_rate = 0.07 if fee_type == "electronics" else 0.09

        gross_margin_pct = float(st.session_state[f"gross_margin_pct_{i}"])
        gross_margin_decimal = gross_margin_pct / 100.0

        rows.append({
            "Product": st.session_state[f"product_name_{i}"],
            "Family": family,
            "Preset Category": preset,
            "AOV": float(st.session_state[f"aov_{i}"]),
            "Gross Margin": gross_margin_decimal,
            "Platform Fee Rate Default": float(fee_rate),
            "Videos / Sample": float(st.session_state[f"videos_per_sample_{i}"]),
            "Clicks / Video": float(st.session_state[f"clicks_per_video_{i}"]),
            "Click-to-order Rate": float(st.session_state[f"click_to_order_pct_{i}"]) / 100.0,
            "ShopTab GMV Share": float(st.session_state[f"shop_tab_share_pct_{i}"]) / 100.0,
            "phase1_samples_per_week": float(st.session_state[f"phase1_samples_{i}"]),
            "phase2_samples_per_week": float(st.session_state[f"phase2_samples_{i}"]),
            "phase3_samples_per_week": float(st.session_state[f"phase3_samples_{i}"]),
        })

    df = pd.DataFrame(rows)

    if df["Product"].isna().any() or (df["Product"].astype(str).str.strip() == "").any():
        raise ValueError("Product name cannot be empty.")

    if (df["AOV"] <= 0).any() or df["AOV"].isna().any():
        raise ValueError("AOV must be > 0 for all products.")

    if ((df["Gross Margin"] < 0.05) | (df["Gross Margin"] > 0.90) | df["Gross Margin"].isna()).any():
        raise ValueError("Gross Margin must be between 5% and 90% for all products.")

    if (df["Videos / Sample"] < 0).any() or (df["Clicks / Video"] < 0).any():
        raise ValueError("Videos / sample and clicks / video must be >= 0.")

    if ((df["Click-to-order Rate"] < 0) | (df["Click-to-order Rate"] > 1)).any():
        raise ValueError("Click-to-order rate must be between 0% and 100%.")

    if ((df["ShopTab GMV Share"] < 0) | (df["ShopTab GMV Share"] > 1)).any():
        raise ValueError("ShopTab GMV share must be between 0% and 100%.")

    sample_cols = [f"{phase_key}_samples_per_week" for phase_key in PHASE_KEYS]
    if (df[sample_cols] < 0).any().any() or df[sample_cols].isna().any().any():
        raise ValueError("SKU samples / week must be >= 0 for all phases.")

    if df[sample_cols].sum().sum() <= 0:
        raise ValueError("At least one SKU must have samples / week > 0 in one phase.")

    return df


def build_weekly_plan(
    phase_inputs,
    prod_df: pd.DataFrame,
    scenario_key: str,
    promo_60d: bool,
    weeks_in_phase: int,
    fulfillment_per_order: float,
    sample_shipping_cost: float,
    affiliate_commission_rate: float,
    ads_roas: float,
) -> pd.DataFrame:
    scenario = SCENARIO_MULTIPLIERS[scenario_key]

    aov = prod_df["AOV"].to_numpy()
    gross_margin = prod_df["Gross Margin"].to_numpy()
    fee_type = prod_df["Platform Fee Rate Default"]
    product_sample_cost = aov * (1.0 - gross_margin)

    videos_per_sample = prod_df["Videos / Sample"].to_numpy() * scenario["videos_per_sample"]
    clicks_per_video = prod_df["Clicks / Video"].to_numpy() * scenario["clicks_per_video"]
    click_to_order_rate = np.minimum(
        prod_df["Click-to-order Rate"].to_numpy() * scenario["click_to_order_rate"],
        1.0,
    )
    shop_tab_share = prod_df["ShopTab GMV Share"].to_numpy()

    rows = []
    video_history = []
    global_week = 0

    for phase in phase_inputs:
        target_series = np.linspace(
            float(phase["gmv_start"]),
            float(phase["gmv_end"]),
            int(weeks_in_phase),
        )

        for week_idx in range(int(weeks_in_phase)):
            global_week += 1
            sample_col = f"{phase['key']}_samples_per_week"
            samples_p = prod_df[sample_col].to_numpy(dtype=float)
            samples_total = float(np.sum(samples_p))
            new_videos_p = samples_p * videos_per_sample
            video_history.append(new_videos_p)

            active_videos_p = np.zeros(len(prod_df))
            for age, weight in enumerate(CONTENT_DECAY_WEIGHTS):
                history_idx = len(video_history) - 1 - age
                if history_idx >= 0:
                    active_videos_p += video_history[history_idx] * weight

            organic_clicks_p = active_videos_p * clicks_per_video
            organic_orders_p = organic_clicks_p * click_to_order_rate
            organic_gmv_p = organic_orders_p * aov

            ads_take_rate = float(phase["ads_take_rate"])
            if ads_take_rate * ads_roas >= 0.90:
                raise ValueError(
                    "Ads Take Rate x Ads ROAS must be below 90%, otherwise paid GMV lift becomes unstable."
                )

            # total_gmv = organic_gmv + ads_spend * ads_roas
            # ads_spend = total_gmv * ads_take_rate
            # => total_gmv = organic_gmv / (1 - ads_take_rate * ads_roas)
            paid_lift_denominator = 1.0 - ads_take_rate * ads_roas
            total_gmv_p = organic_gmv_p / paid_lift_denominator
            paid_gmv_p = total_gmv_p - organic_gmv_p
            orders_p = total_gmv_p / aov

            shop_tab_gmv_p = total_gmv_p * shop_tab_share
            affiliate_video_gmv_p = total_gmv_p - shop_tab_gmv_p

            product_fee_rates = platform_fee_rates_for_week(global_week, promo_60d, fee_type)
            platform_fee_p = total_gmv_p * product_fee_rates
            cogs_p = total_gmv_p * (1.0 - gross_margin)
            sample_cost_p = samples_p * (product_sample_cost + float(sample_shipping_cost))

            gmv = float(np.sum(total_gmv_p))
            organic_gmv = float(np.sum(organic_gmv_p))
            paid_gmv = float(np.sum(paid_gmv_p))
            target_gmv = float(target_series[week_idx])
            orders_total = float(np.sum(orders_p))
            new_videos_total = float(np.sum(new_videos_p))
            active_videos_total = float(np.sum(active_videos_p))
            clicks_total = float(np.sum(organic_clicks_p))
            shop_tab_gmv = float(np.sum(shop_tab_gmv_p))
            affiliate_video_gmv = float(np.sum(affiliate_video_gmv_p))

            cogs_total = float(np.sum(cogs_p))
            platform_fee_total = float(np.sum(platform_fee_p))
            samples_cost = float(np.sum(sample_cost_p))
            fulfillment = orders_total * float(fulfillment_per_order)
            creator_commission = affiliate_video_gmv * float(affiliate_commission_rate)
            ads_cost = gmv * ads_take_rate

            gross_profit = gmv - cogs_total
            growth_investment = samples_cost + ads_cost
            total_cost = (
                cogs_total
                + platform_fee_total
                + creator_commission
                + ads_cost
                + samples_cost
                + fulfillment
            )
            profit = gmv - total_cost

            rows.append({
                "Phase Key": phase["key"],
                "Phase": phase["name"],
                "Week in Phase": week_idx + 1,
                "Global Week": global_week,
                "Samples Sent": samples_total,
                "New Videos": new_videos_total,
                "Active Videos": active_videos_total,
                "Product Clicks": clicks_total,
                "Orders (est.)": orders_total,
                "Organic Funnel GMV": organic_gmv,
                "Paid GMV Lift": paid_gmv,
                "GMV": gmv,
                "Target GMV": target_gmv,
                "Target Gap": gmv - target_gmv,
                "ShopTab GMV": shop_tab_gmv,
                "Affiliate Video GMV": affiliate_video_gmv,
                "Creator Commission": creator_commission,
                "Platform Fee": platform_fee_total,
                "Ads Cost": ads_cost,
                "Samples Cost": samples_cost,
                "Fulfillment Cost": fulfillment,
                "COGS": cogs_total,
                "Gross Profit": gross_profit,
                "Growth Investment": growth_investment,
                "Total Cost": total_cost,
                "Profit": profit,
                "Ads Take Rate": ads_take_rate,
                "Ads ROAS": ads_roas,
            })

    return pd.DataFrame(rows)


def build_phase_summary(df_all: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df_all.groupby(["Phase Key", "Phase"], as_index=False)
        .agg({
            "Samples Sent": "sum",
            "New Videos": "sum",
            "Product Clicks": "sum",
            "Orders (est.)": "sum",
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
            "Ads Cost": "sum",
            "Samples Cost": "sum",
            "Fulfillment Cost": "sum",
            "Creator Commission": "sum",
            "Growth Investment": "sum",
            "Total Cost": "sum",
            "Profit": "sum",
        })
    )
    summary["Profit Margin"] = np.where(summary["GMV"] > 0, summary["Profit"] / summary["GMV"], 0)
    summary["GMV / Sample"] = np.where(summary["Samples Sent"] > 0, summary["GMV"] / summary["Samples Sent"], 0)
    return summary


def build_overall_summary(df_all: pd.DataFrame) -> pd.DataFrame:
    total_gmv = df_all["GMV"].sum()
    total_cost = df_all["Total Cost"].sum()
    total_profit = df_all["Profit"].sum()
    total_samples = df_all["Samples Sent"].sum()

    return pd.DataFrame([{
        "Total Samples": total_samples,
        "Total Videos": df_all["New Videos"].sum(),
        "Total Clicks": df_all["Product Clicks"].sum(),
        "Total Orders (est.)": df_all["Orders (est.)"].sum(),
        "Total GMV": total_gmv,
        "Total Target GMV": df_all["Target GMV"].sum(),
        "Total Cost": total_cost,
        "Total Profit": total_profit,
        "Growth Investment": df_all["Growth Investment"].sum(),
        "Overall Profit Margin": (total_profit / total_gmv) if total_gmv > 0 else 0,
        "GMV / Sample": (total_gmv / total_samples) if total_samples > 0 else 0,
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


def get_point_by_week(df: pd.DataFrame, week: int, y_col: str):
    match = df[df["Global Week"] == week]
    if match.empty:
        return None
    return float(match.iloc[0][y_col])


def make_chart(
    df: pd.DataFrame,
    title: str,
    weekly_be_week=None,
    annotate_break_even: bool = False,
):
    fig, ax = plt.subplots(figsize=(10, 5))
    add_phase_backgrounds(ax, df)

    ax.plot(df["Global Week"], df["GMV"], marker="o", linewidth=2, label="Forecast GMV", zorder=4)
    ax.plot(df["Global Week"], df["Target GMV"], linestyle="--", label="Target GMV", zorder=3)
    ax.plot(df["Global Week"], df["Total Cost"], marker="o", label="Total Cost", zorder=3)
    ax.plot(df["Global Week"], df["Profit"], marker="o", linewidth=2, label="Profit", zorder=4)
    ax.axhline(0, linewidth=1, zorder=2)

    if annotate_break_even and weekly_be_week is not None:
        y_weekly = get_point_by_week(df, weekly_be_week, "Profit")
        if y_weekly is not None:
            ax.scatter([weekly_be_week], [y_weekly], s=80, zorder=5)
            ax.annotate(
                f"{T['weekly_be_label']}: W{weekly_be_week}",
                xy=(weekly_be_week, y_weekly),
                xytext=(8, 8),
                textcoords="offset points",
            )
            ax.axvline(weekly_be_week, linestyle="--", alpha=0.35, zorder=2)

    ax.set_title(title)
    ax.set_xlabel(T["week"])
    ax.set_ylabel("€")
    ax.grid(True, alpha=0.3, zorder=1)
    ax.legend()
    format_eur_axis(ax)
    fig.tight_layout()
    return fig


def make_cumulative_profit_chart(df_all: pd.DataFrame, cumulative_be_week=None):
    tmp = df_all.copy()
    tmp["Cumulative Profit"] = tmp["Profit"].cumsum()

    fig, ax = plt.subplots(figsize=(10, 5))
    add_phase_backgrounds(ax, tmp)

    ax.plot(
        tmp["Global Week"],
        tmp["Cumulative Profit"],
        marker="o",
        linewidth=2,
        label="Cumulative Profit",
        zorder=3,
    )
    ax.axhline(0, linewidth=1, zorder=2)

    if cumulative_be_week is not None:
        y_cum = get_point_by_week(tmp, cumulative_be_week, "Cumulative Profit")
        if y_cum is not None:
            ax.scatter([cumulative_be_week], [y_cum], s=80, zorder=5)
            ax.annotate(
                f"{T['cumulative_be_label']}: W{cumulative_be_week}",
                xy=(cumulative_be_week, y_cum),
                xytext=(8, 8),
                textcoords="offset points",
            )
            ax.axvline(cumulative_be_week, linestyle="--", alpha=0.35, zorder=2)

    ax.set_title(T["cumulative_profit_trend"])
    ax.set_xlabel(T["week"])
    ax.set_ylabel("€")
    ax.grid(True, alpha=0.3, zorder=1)
    ax.legend()
    format_eur_axis(ax)
    fig.tight_layout()
    return fig


def make_funnel_chart(df_all: pd.DataFrame):
    totals = pd.Series({
        T["total_samples"]: df_all["Samples Sent"].sum(),
        T["total_videos"]: df_all["New Videos"].sum(),
        T["total_clicks"]: df_all["Product Clicks"].sum(),
        T["total_orders"]: df_all["Orders (est.)"].sum(),
    })

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(totals.index, totals.values)
    ax.set_title(T["funnel_summary"])
    ax.grid(True, axis="y", alpha=0.3)
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
    fig.autofmt_xdate(rotation=15)
    fig.tight_layout()
    return fig


def format_display_table(df: pd.DataFrame, money_cols=None, pct_cols=None, number_cols=None) -> pd.DataFrame:
    out = df.copy()
    for col in money_cols or []:
        if col in out.columns:
            out[col] = out[col].map(lambda v: money(float(v), 0))
    for col in pct_cols or []:
        if col in out.columns:
            out[col] = out[col].map(lambda v: pct(float(v), 1))
    for col in number_cols or []:
        if col in out.columns:
            out[col] = out[col].map(lambda v: f"{float(v):,.0f}")
    return out


def initialize_product_state(i: int, n_products: int):
    if f"product_name_{i}" not in st.session_state:
        st.session_state[f"product_name_{i}"] = LETTERS[i]

    if f"family_{i}" not in st.session_state:
        st.session_state[f"family_{i}"] = "Home & Living"

    current_family = st.session_state[f"family_{i}"]
    available_presets = list(AOV_PRESETS[current_family].keys())

    if f"preset_{i}" not in st.session_state or st.session_state[f"preset_{i}"] not in available_presets:
        st.session_state[f"preset_{i}"] = available_presets[0]

    preset = st.session_state[f"preset_{i}"]
    benchmark = get_benchmark(current_family, preset)

    defaults = {
        f"aov_{i}": float(benchmark["aov"]),
        f"gross_margin_pct_{i}": 40.0,
        f"fee_type_{i}": guess_fee_type(preset),
        f"videos_per_sample_{i}": float(benchmark["videos_per_sample"]),
        f"clicks_per_video_{i}": float(benchmark["clicks_per_video"]),
        f"click_to_order_pct_{i}": float(benchmark["click_to_order_rate"] * 100.0),
        f"shop_tab_share_pct_{i}": float(benchmark["shop_tab_share"] * 100.0),
        f"phase1_samples_{i}": float(PHASE_DEFAULTS["phase1"]["default_sku_samples"]),
        f"phase2_samples_{i}": float(PHASE_DEFAULTS["phase2"]["default_sku_samples"]),
        f"phase3_samples_{i}": float(PHASE_DEFAULTS["phase3"]["default_sku_samples"]),
        f"last_family_{i}": current_family,
        f"last_preset_{i}": preset,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def apply_category_benchmark(i: int):
    family = st.session_state[f"family_{i}"]
    preset = st.session_state[f"preset_{i}"]
    benchmark = get_benchmark(family, preset)
    st.session_state[f"aov_{i}"] = float(benchmark["aov"])
    st.session_state[f"fee_type_{i}"] = guess_fee_type(preset)
    st.session_state[f"videos_per_sample_{i}"] = float(benchmark["videos_per_sample"])
    st.session_state[f"clicks_per_video_{i}"] = float(benchmark["clicks_per_video"])
    st.session_state[f"click_to_order_pct_{i}"] = float(benchmark["click_to_order_rate"] * 100.0)
    st.session_state[f"shop_tab_share_pct_{i}"] = float(benchmark["shop_tab_share"] * 100.0)
    st.session_state[f"last_family_{i}"] = family
    st.session_state[f"last_preset_{i}"] = preset


def refresh_benchmark_if_category_changed(i: int):
    family = st.session_state[f"family_{i}"]
    preset = st.session_state[f"preset_{i}"]
    if (
        st.session_state.get(f"last_family_{i}") != family
        or st.session_state.get(f"last_preset_{i}") != preset
    ):
        apply_category_benchmark(i)


# ======================
# UI
# ======================
st.title(T["app_title"])
st.caption(T["app_caption"])
st.info(T["assumption_note"])


with st.sidebar:
    st.header(T["global_inputs"])

    n_products = st.number_input(
        T["num_products"],
        min_value=1,
        max_value=26,
        value=3,
        step=1,
    )

    scenario_key = st.selectbox(
        T["scenario"],
        options=["conservative", "base", "aggressive"],
        format_func=lambda x: T[f"scenario_{x}"],
        index=1,
    )

    promo_60d = st.radio(
        T["promo_60d"],
        options=[True, False],
        format_func=lambda x: T["promo_yes"] if x else T["promo_no"],
        index=0,
    )

    fulfillment_per_order = st.number_input(
        T["fulfillment"],
        min_value=0.0,
        value=6.0,
        step=0.5,
    )

    sample_ship_cost = st.number_input(
        T["sample_shipping"],
        min_value=0.0,
        value=5.0,
        step=1.0,
    )

    affiliate_commission_rate = st.slider(
        T["affiliate_commission"],
        min_value=0.0,
        max_value=0.5,
        value=0.15,
        step=0.01,
    )

    ads_roas = st.number_input(
        T["ads_roas"],
        min_value=0.1,
        max_value=8.0,
        value=3.0,
        step=0.1,
        help=T["ads_roas_help"],
    )

    weeks_in_phase = st.slider(
        T["weeks_per_phase"],
        min_value=2,
        max_value=8,
        value=4,
        step=1,
    )

    st.header(T["phase_controls"])
    phase_inputs = build_phase_inputs()

    for i, phase in enumerate(phase_inputs):
        st.subheader(phase["name"])

        phase["gmv_start"] = st.number_input(
            f"{T['gmv_start']} - {phase['name']}",
            min_value=0.0,
            value=float(phase["gmv_start"]),
            step=1_000.0,
            key=f"gmv_start_{i}",
            help=T["target_gmv_help"],
        )

        phase["gmv_end"] = st.number_input(
            f"{T['gmv_end']} - {phase['name']}",
            min_value=0.0,
            value=float(phase["gmv_end"]),
            step=1_000.0,
            key=f"gmv_end_{i}",
            help=T["target_gmv_help"],
        )

        phase["ads_take_rate"] = st.slider(
            f"{T['ads_rate']} - {phase['name']}",
            min_value=0.0,
            max_value=0.30,
            value=float(phase["ads_take_rate"]),
            step=0.01,
            key=f"ads_{i}",
            help=T["ads_rate_help"],
        )


# ======================
# Product Setup
# ======================
st.subheader(T["product_setup"])
st.caption(T["product_setup_caption"])

for i in range(int(n_products)):
    initialize_product_state(i, int(n_products))

    with st.container(border=True):
        st.markdown(f"**{T['product_block']} {i + 1}**")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.text_input(T["product"], key=f"product_name_{i}")

        with col2:
            st.selectbox(T["family"], options=list(AOV_PRESETS.keys()), key=f"family_{i}")

        selected_family = st.session_state[f"family_{i}"]
        updated_presets = list(AOV_PRESETS[selected_family].keys())
        if st.session_state[f"preset_{i}"] not in updated_presets:
            st.session_state[f"preset_{i}"] = updated_presets[0]

        with col3:
            st.selectbox(T["preset"], options=updated_presets, key=f"preset_{i}")

        refresh_benchmark_if_category_changed(i)

        if st.button(f"{T['apply_benchmark']} - {T['product_block']} {i + 1}", key=f"apply_benchmark_{i}"):
            apply_category_benchmark(i)
            st.rerun()

        sample_cols = st.columns(3)
        for sample_col, phase_key in zip(sample_cols, PHASE_KEYS):
            with sample_col:
                st.number_input(
                    f"{phase_label(phase_key)} - {T['sku_samples']}",
                    min_value=0.0,
                    step=1.0,
                    key=f"{phase_key}_samples_{i}",
                    help=T["sku_samples_help"],
                )

        col4, col5, col6 = st.columns(3)

        with col4:
            st.number_input(
                T["aov"],
                min_value=0.01,
                step=1.0,
                key=f"aov_{i}",
            )

        with col5:
            st.selectbox(
                T["fee_type"],
                options=["electronics", "other"],
                format_func=fee_label,
                key=f"fee_type_{i}",
            )

        col7, col8, col9, col10 = st.columns(4)

        with col7:
            st.number_input(
                T["gross_margin"],
                min_value=5.0,
                max_value=90.0,
                step=1.0,
                key=f"gross_margin_pct_{i}",
                help=T["gross_margin_help"],
            )

        with col8:
            st.number_input(
                T["videos_per_sample"],
                min_value=0.0,
                max_value=5.0,
                step=0.05,
                key=f"videos_per_sample_{i}",
            )

        with col9:
            st.number_input(
                T["clicks_per_video"],
                min_value=0.0,
                max_value=100_000.0,
                step=10.0,
                key=f"clicks_per_video_{i}",
            )

        with col10:
            st.number_input(
                T["click_to_order"],
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key=f"click_to_order_pct_{i}",
            )

        st.slider(
            T["shop_tab_share"],
            min_value=0.0,
            max_value=100.0,
            step=1.0,
            key=f"shop_tab_share_pct_{i}",
            help=T["shop_tab_share_help"],
        )


generate = st.button(T["generate"], type="primary")


# ======================
# Run
# ======================
if generate:
    try:
        prod_df = build_product_df_from_ui(int(n_products))

        df_all = build_weekly_plan(
            phase_inputs=phase_inputs,
            prod_df=prod_df,
            scenario_key=scenario_key,
            promo_60d=bool(promo_60d),
            weeks_in_phase=int(weeks_in_phase),
            fulfillment_per_order=float(fulfillment_per_order),
            sample_shipping_cost=float(sample_ship_cost),
            affiliate_commission_rate=float(affiliate_commission_rate),
            ads_roas=float(ads_roas),
        )

        phase_summary = build_phase_summary(df_all)
        overall_summary = build_overall_summary(df_all)

        single_week_break_even = first_positive_profit_week(df_all)
        cumulative_break_even = first_cumulative_break_even_week(df_all)

        mix_display = prod_df[[
            "Product",
            "Family",
            "Preset Category",
            "phase1_samples_per_week",
            "phase2_samples_per_week",
            "phase3_samples_per_week",
            "AOV",
            "Gross Margin",
            "Platform Fee Rate Default",
            "Videos / Sample",
            "Clicks / Video",
            "Click-to-order Rate",
            "ShopTab GMV Share",
        ]].copy()

        mix_display.columns = [
            T["product"],
            T["family"],
            T["preset_category"],
            f"{phase_label('phase1')} - {T['sku_samples']}",
            f"{phase_label('phase2')} - {T['sku_samples']}",
            f"{phase_label('phase3')} - {T['sku_samples']}",
            T["aov"],
            T["gross_margin"],
            T["platform_fee_default"],
            T["videos_per_sample"],
            T["clicks_per_video"],
            T["click_to_order"],
            T["shop_tab_share"],
        ]

        for phase_key in PHASE_KEYS:
            col_name = f"{phase_label(phase_key)} - {T['sku_samples']}"
            mix_display[col_name] = mix_display[col_name].map(lambda v: f"{v:,.0f}")
        mix_display[T["aov"]] = mix_display[T["aov"]].map(lambda v: money(float(v), 2))
        mix_display[T["gross_margin"]] = mix_display[T["gross_margin"]].map(lambda v: pct(float(v), 0))
        mix_display[T["platform_fee_default"]] = mix_display[T["platform_fee_default"]].map(lambda v: pct(float(v), 0))
        mix_display[T["click_to_order"]] = mix_display[T["click_to_order"]].map(lambda v: pct(float(v), 1))
        mix_display[T["shop_tab_share"]] = mix_display[T["shop_tab_share"]].map(lambda v: pct(float(v), 0))

        st.subheader(T["product_mix"])
        st.dataframe(mix_display, use_container_width=True)

        metric1, metric2, metric3, metric4 = st.columns(4)
        row = overall_summary.iloc[0]
        with metric1:
            st.metric(T["total_gmv"], money(row["Total GMV"], 0))
        with metric2:
            st.metric(T["total_profit"], money(row["Total Profit"], 0))
        with metric3:
            st.metric(T["profit_margin"], pct(row["Overall Profit Margin"], 1))
        with metric4:
            st.metric(T["growth_investment"], money(row["Growth Investment"], 0))

        metric5, metric6, metric7, metric8 = st.columns(4)
        with metric5:
            st.metric(T["total_samples"], f"{row['Total Samples']:,.0f}")
        with metric6:
            st.metric(T["total_videos"], f"{row['Total Videos']:,.0f}")
        with metric7:
            st.metric(T["total_clicks"], f"{row['Total Clicks']:,.0f}")
        with metric8:
            st.metric(T["total_orders"], f"{row['Total Orders (est.)']:,.0f}")

        st.subheader(T["charts"])
        render_phase_badges([p["key"] for p in phase_inputs])

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.pyplot(
                make_chart(
                    df_all,
                    T["overall_weekly_trend"],
                    weekly_be_week=single_week_break_even,
                    annotate_break_even=True,
                )
            )

        with chart_col2:
            st.pyplot(
                make_cumulative_profit_chart(
                    df_all,
                    cumulative_be_week=cumulative_break_even,
                )
            )

        st.pyplot(make_funnel_chart(df_all))

        st.subheader(T["phase_by_phase"])
        phase_tabs = st.tabs([p["name"] for p in phase_inputs])

        for tab, phase in zip(phase_tabs, phase_inputs):
            with tab:
                phase_df = df_all[df_all["Phase Key"] == phase["key"]].copy()
                phase_weekly_be = None
                tmp_phase_be = phase_df[phase_df["Profit"] > 0]
                if not tmp_phase_be.empty:
                    phase_weekly_be = int(tmp_phase_be["Global Week"].iloc[0])

                render_phase_badges([phase["key"]])
                st.pyplot(
                    make_chart(
                        phase_df,
                        phase["name"],
                        weekly_be_week=phase_weekly_be,
                        annotate_break_even=True,
                    )
                )

        st.subheader(T["summary"])
        sum_col1, sum_col2 = st.columns(2)

        phase_summary_fmt = format_display_table(
            phase_summary.drop(columns=["Phase Key"]),
            money_cols=[
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
                "Ads Cost",
                "Samples Cost",
                "Fulfillment Cost",
                "Creator Commission",
                "Growth Investment",
                "Total Cost",
                "Profit",
                "GMV / Sample",
            ],
            pct_cols=["Profit Margin"],
            number_cols=["Samples Sent", "New Videos", "Product Clicks", "Orders (est.)"],
        )

        overall_summary_fmt = format_display_table(
            overall_summary,
            money_cols=[
                "Total GMV",
                "Total Target GMV",
                "Total Cost",
                "Total Profit",
                "Growth Investment",
                "GMV / Sample",
            ],
            pct_cols=["Overall Profit Margin"],
            number_cols=["Total Samples", "Total Videos", "Total Clicks", "Total Orders (est.)"],
        )

        with sum_col1:
            st.markdown(f"**{T['phase_summary']}**")
            st.dataframe(phase_summary_fmt, use_container_width=True)
        with sum_col2:
            st.markdown(f"**{T['overall_summary']}**")
            st.dataframe(overall_summary_fmt, use_container_width=True)

        st.subheader(T["break_even_signals"])
        be_col1, be_col2 = st.columns(2)
        with be_col1:
            if single_week_break_even is not None:
                st.success(f"{T['first_positive_profit']}: {T['week']} {single_week_break_even}")
            else:
                st.warning(f"{T['first_positive_profit']}: {T['not_reached']}")

        with be_col2:
            if cumulative_break_even is not None:
                st.success(f"{T['cumulative_break_even']}: {T['week']} {cumulative_break_even}")
            else:
                st.warning(f"{T['cumulative_break_even']}: {T['not_reached']}")

        st.subheader(T["weekly_details"])

        df_all_display = format_display_table(
            df_all.drop(columns=["Phase Key"]),
            money_cols=[
                "Organic Funnel GMV",
                "Paid GMV Lift",
                "GMV",
                "Target GMV",
                "Target Gap",
                "ShopTab GMV",
                "Affiliate Video GMV",
                "Creator Commission",
                "Platform Fee",
                "Ads Cost",
                "Samples Cost",
                "Fulfillment Cost",
                "COGS",
                "Gross Profit",
                "Growth Investment",
                "Total Cost",
                "Profit",
            ],
            pct_cols=["Ads Take Rate"],
            number_cols=[
                "Samples Sent",
                "New Videos",
                "Active Videos",
                "Product Clicks",
                "Orders (est.)",
            ],
        )

        st.dataframe(df_all_display, use_container_width=True)

        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                T["download_weekly"],
                data=to_csv_bytes(df_all),
                file_name="weekly_details.csv",
                mime="text/csv",
            )
        with dl2:
            st.download_button(
                T["download_phase"],
                data=to_csv_bytes(phase_summary),
                file_name="phase_summary.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"{T['input_error']}: {e}")
