import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go


st.set_page_config(page_title="TikTok Shop Growth Visualizer", layout="wide")


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
# shop_tab_share: reference share used to seed the ShopTab natural-sales assumption
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

# Videos generated in week 1 keep contributing in later weeks, with a content tail.
CONTENT_DECAY_WEIGHTS = [1.00, 0.75, 0.60, 0.48, 0.38, 0.30, 0.24, 0.19, 0.15, 0.12, 0.10, 0.08]
PROMO_WEEKS = 9
LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
CHART_COLORS = {
    "gmv": "#2563EB",
    "cost": "#F97316",
    "profit": "#16A34A",
    "cumulative": "#7C3AED",
    "grid": "#E5E7EB",
    "text": "#111827",
}


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
        "fulfillment": "Logistics cost €/unit or order",
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
        "avg_sample_cost": "Avg sample cost / unit",
        "sample_investment": "Sample Investment",
        "ads_investment": "Ads Investment",
        "benchmark_expander": "View / adjust category funnel assumptions",
        "videos_sample": "Videos / sample",
        "clicks_video": "Clicks / video",
        "click_order": "Click-to-order (%)",
        "shoptab_share": "ShopTab GMV share (%)",
        "aov_help": "Average selling price per order for this subcategory. Current default is a public-market benchmark for Germany and should be replaced with internal TikTok Shop subcategory AOV when available.",
        "gross_margin_help": "Merchant gross margin before platform fee, creator commission, ads, logistics, and sample investment. Product cost is calculated as AOV x (1 - gross margin).",
        "videos_sample_help": "Estimated creator videos generated per sample sent. Example: 0.40 means 100 samples generate about 40 videos. Current value is a public benchmark placeholder.",
        "clicks_video_help": "Estimated product-page clicks generated by each creator video over its active content tail. Current value is a public social-commerce benchmark placeholder.",
        "click_order_help": "Estimated conversion from product click to order. Current value is a public e-commerce/social-commerce benchmark placeholder.",
        "shoptab_share_help": "Share of organic GMV attributed to ShopTab/Search/Mall/Storefront after users are influenced by content. This GMV does not carry creator affiliate commission. Current value is a public benchmark placeholder and should be replaced with internal data.",
        "generate": "Generate Simulator",
        "sku_mix": "SKU Mix & Funnel Assumptions",
        "total_gmv": "Total GMV",
        "total_cost": "Total Cost",
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
        "phase_chart_mode": "Phase chart view",
        "phase_chart_total": "Total view",
        "phase_chart_cumulative": "Cumulative trend",
        "overall_summary": "Overall Summary",
        "break_even": "Break-even Signals",
        "weekly_profit": "First positive weekly profit",
        "cumulative_be": "Cumulative break-even",
        "not_reached": "Not reached",
        "weekly_details": "Weekly Details",
        "download_weekly": "Download weekly details CSV",
        "download_phase": "Download phase summary CSV",
        "input_error": "Input error",
        "insight": "Plan Insight",
        "insight_text": "Over {weeks} weeks, this plan sends {samples} samples, generates estimated GMV of {gmv}, and ends with {profit} total profit. Weekly break-even: {weekly_be}. Cumulative break-even: {cumulative_be}.",
        "executive_summary": "Executive Summary",
        "executive_summary_text": "In this {weeks}-week plan, the brand needs about {growth_investment} in growth investment, including {sample_investment} for samples and {ads_investment} for ads. The model estimates {gmv} GMV and {profit} total profit. Each sample contributes around {gmv_per_sample} GMV and {profit_per_sample} profit. The largest GMV driver is {main_channel}. Weekly break-even: {weekly_be}. Cumulative break-even: {cumulative_be}.",
        "sample_roi_title": "Sample ROI",
        "gmv_per_sample": "GMV / Sample",
        "profit_per_sample": "Profit / Sample",
        "videos_per_sample_kpi": "Videos / Sample",
        "orders_per_sample": "Orders / Sample",
        "sample_gmv_roi": "GMV / Sample Cost",
        "view_details": "View detailed tables",
        "channel_mix": "GMV Channel Mix",
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
        "fulfillment": "物流成本 €/件/单",
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
        "avg_sample_cost": "平均样品成本 / 件",
        "sample_investment": "样品投入",
        "ads_investment": "广告投入",
        "benchmark_expander": "查看 / 调整类目漏斗假设",
        "videos_sample": "每个样品产出视频数",
        "clicks_video": "每条视频商品点击数",
        "click_order": "点击到下单转化率 (%)",
        "shoptab_share": "ShopTab GMV 占比 (%)",
        "aov_help": "该 subcategory 的平均成交客单价。当前默认值是基于公开市场信息的德国 benchmark，拿到 TikTok Shop 内部 subcategory AOV 后建议替换。",
        "gross_margin_help": "商家毛利率，不包含平台佣金、达人佣金、广告、物流和寄样投入。商品成本会按 AOV x (1 - 毛利率) 自动计算。",
        "videos_sample_help": "每寄出 1 个样品预计产生的达人视频数。例如 0.40 表示 100 个样品约产生 40 条视频。当前为公开 benchmark 占位值。",
        "clicks_video_help": "每条达人视频在内容长尾周期内预计带来的商品页点击数。当前为公开 social commerce benchmark 占位值。",
        "click_order_help": "商品页点击到下单的转化率。当前为公开电商/social commerce benchmark 占位值。",
        "shoptab_share_help": "被内容种草后，最终通过 ShopTab/Search/Mall/店铺页成交的 organic GMV 占比。这部分 GMV 不产生达人佣金。当前为公开 benchmark 占位值，拿到内部数据后建议替换。",
        "generate": "生成模拟结果",
        "sku_mix": "SKU 组合与漏斗假设",
        "total_gmv": "总 GMV",
        "total_cost": "总成本",
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
        "phase_chart_mode": "阶段图表视图",
        "phase_chart_total": "阶段总和",
        "phase_chart_cumulative": "累计走势",
        "overall_summary": "整体汇总",
        "break_even": "Break-even 信号",
        "weekly_profit": "首次单周盈利",
        "cumulative_be": "累计 Break-even",
        "not_reached": "未达到",
        "weekly_details": "每周明细",
        "download_weekly": "下载每周明细 CSV",
        "download_phase": "下载阶段汇总 CSV",
        "input_error": "输入错误",
        "insight": "计划解读",
        "insight_text": "按当前计划，品牌将在 {weeks} 周内寄出 {samples} 个样品，预计产生 {gmv} GMV，最终总利润为 {profit}。首次单周盈利：{weekly_be}。累计 Break-even：{cumulative_be}。",
        "executive_summary": "客户版总结",
        "executive_summary_text": "按当前 {weeks} 周计划，品牌预计需要准备 {growth_investment} 增长投入，其中样品投入 {sample_investment}，广告投入 {ads_investment}。模型预计产生 {gmv} GMV，最终总利润为 {profit}。平均每个样品预计带来 {gmv_per_sample} GMV 和 {profit_per_sample} 利润。当前最大的 GMV 来源是 {main_channel}。首次单周盈利：{weekly_be}；累计 Break-even：{cumulative_be}。",
        "sample_roi_title": "样品 ROI",
        "gmv_per_sample": "GMV / 样品",
        "profit_per_sample": "利润 / 样品",
        "videos_per_sample_kpi": "视频 / 样品",
        "orders_per_sample": "订单 / 样品",
        "sample_gmv_roi": "GMV / 样品成本",
        "view_details": "查看详细表格",
        "channel_mix": "GMV 渠道拆分",
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
    "fulfillment": "Logistikkosten €/Stück oder Bestellung",
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
    "avg_sample_cost": "Ø Sample-Kosten / Stück",
    "sample_investment": "Sample-Investition",
    "ads_investment": "Ads-Investition",
    "benchmark_expander": "Kategorie-Funnel-Annahmen anzeigen / anpassen",
    "videos_sample": "Videos / Sample",
    "clicks_video": "Klicks / Video",
    "click_order": "Klick-zu-Bestellung (%)",
    "shoptab_share": "ShopTab GMV-Anteil (%)",
    "aov_help": "Durchschnittlicher Verkaufspreis pro Bestellung. Der aktuelle Standardwert ist ein öffentlicher Deutschland-Benchmark und sollte durch interne TikTok-Shop-Daten ersetzt werden.",
    "gross_margin_help": "Händler-Bruttomarge vor Plattformgebühr, Creator-Provision, Ads, Logistik und Sample-Investment. Produktkosten = AOV x (1 - Bruttomarge).",
    "videos_sample_help": "Geschätzte Creator-Videos pro versendetem Sample. Beispiel: 0,40 bedeutet ca. 40 Videos aus 100 Samples. Aktuell ein öffentlicher Benchmark-Platzhalter.",
    "clicks_video_help": "Geschätzte Produktseiten-Klicks pro Creator-Video über den Content-Tail. Aktuell ein öffentlicher Benchmark-Platzhalter.",
    "click_order_help": "Geschätzte Conversion von Produktklick zu Bestellung. Aktuell ein öffentlicher Benchmark-Platzhalter.",
    "shoptab_share_help": "Anteil des organischen GMV, der nach Content-Einfluss über ShopTab/Search/Mall/Storefront kauft. Dieser GMV trägt keine Creator-Provision. Aktuell ein öffentlicher Benchmark-Platzhalter.",
    "generate": "Simulator erzeugen",
    "sku_mix": "SKU-Mix & Funnel-Annahmen",
    "total_gmv": "Gesamt-GMV",
    "total_cost": "Gesamtkosten",
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
    "phase_chart_mode": "Phasen-Chartansicht",
    "phase_chart_total": "Gesamtansicht",
    "phase_chart_cumulative": "Kumulativer Trend",
    "overall_summary": "Gesamtübersicht",
    "break_even": "Break-even-Signale",
    "weekly_profit": "Erste positive Wochenprofitabilität",
    "cumulative_be": "Kumulierter Break-even",
    "not_reached": "Nicht erreicht",
    "weekly_details": "Wöchentliche Details",
    "download_weekly": "Wöchentliche Details CSV herunterladen",
    "download_phase": "Phasenübersicht CSV herunterladen",
    "input_error": "Eingabefehler",
    "insight": "Plan-Insight",
    "insight_text": "Über {weeks} Wochen versendet dieser Plan {samples} Samples, erzeugt geschätzten GMV von {gmv} und endet mit {profit} Gesamtgewinn. Erste positive Woche: {weekly_be}. Kumulierter Break-even: {cumulative_be}.",
    "executive_summary": "Executive Summary",
    "sample_roi_title": "Sample ROI",
    "gmv_per_sample": "GMV / Sample",
    "profit_per_sample": "Gewinn / Sample",
    "videos_per_sample_kpi": "Videos / Sample",
    "orders_per_sample": "Bestellungen / Sample",
    "sample_gmv_roi": "GMV / Sample-Kosten",
    "view_details": "Detaillierte Tabellen anzeigen",
    "channel_mix": "GMV-Kanalmix",
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
    "fulfillment": "Logistieke kosten €/stuk of order",
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
    "avg_sample_cost": "Gem. samplekosten / stuk",
    "sample_investment": "Sample-investering",
    "ads_investment": "Ads-investering",
    "benchmark_expander": "Categorie-funnelaannames bekijken / aanpassen",
    "videos_sample": "Video's / sample",
    "clicks_video": "Clicks / video",
    "click_order": "Click-to-order (%)",
    "shoptab_share": "ShopTab GMV-aandeel (%)",
    "aov_help": "Gemiddelde verkoopprijs per order. De huidige standaardwaarde is een publieke Duitsland-benchmark en moet worden vervangen door interne TikTok Shop-data zodra beschikbaar.",
    "gross_margin_help": "Brutomarge van de merchant voor platform fee, creator commissie, ads, logistiek en sample-investering. Productkosten = AOV x (1 - brutomarge).",
    "videos_sample_help": "Geschat aantal creator-video's per verzonden sample. Voorbeeld: 0,40 betekent circa 40 video's uit 100 samples. Huidige waarde is een publieke benchmark-placeholder.",
    "clicks_video_help": "Geschat aantal productpagina-clicks per creator-video over de content-tail. Huidige waarde is een publieke benchmark-placeholder.",
    "click_order_help": "Geschatte conversie van productclick naar order. Huidige waarde is een publieke benchmark-placeholder.",
    "shoptab_share_help": "Aandeel organische GMV dat na content-invloed via ShopTab/Search/Mall/Storefront koopt. Deze GMV heeft geen creator commissie. Huidige waarde is een publieke benchmark-placeholder.",
    "generate": "Simulator genereren",
    "sku_mix": "SKU-mix & funnelaannames",
    "total_gmv": "Totale GMV",
    "total_cost": "Totale kosten",
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
    "phase_chart_mode": "Fasegrafiek",
    "phase_chart_total": "Totaaloverzicht",
    "phase_chart_cumulative": "Cumulatieve trend",
    "overall_summary": "Totaaloverzicht",
    "break_even": "Break-even signalen",
    "weekly_profit": "Eerste positieve weekwinst",
    "cumulative_be": "Cumulatieve break-even",
    "not_reached": "Niet bereikt",
    "weekly_details": "Wekelijkse details",
    "download_weekly": "Wekelijkse details CSV downloaden",
    "download_phase": "Faseoverzicht CSV downloaden",
    "input_error": "Invoerfout",
    "insight": "Plan-inzicht",
    "insight_text": "Over {weeks} weken verstuurt dit plan {samples} samples, genereert naar schatting {gmv} GMV en eindigt met {profit} totale winst. Eerste positieve week: {weekly_be}. Cumulatieve break-even: {cumulative_be}.",
    "executive_summary": "Executive Summary",
    "sample_roi_title": "Sample ROI",
    "gmv_per_sample": "GMV / sample",
    "profit_per_sample": "Winst / sample",
    "videos_per_sample_kpi": "Video's / sample",
    "orders_per_sample": "Orders / sample",
    "sample_gmv_roi": "GMV / samplekosten",
    "view_details": "Gedetailleerde tabellen bekijken",
    "channel_mix": "GMV-kanaalmix",
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
        index=0,
    )

T = TEXT[lang]


def phase_label(phase):
    return T[phase["key"]]


def csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8-sig")


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
    if df["ShopTab GMV Share"].lt(0).any() or df["ShopTab GMV Share"].gt(0.90).any():
        raise ValueError("ShopTab GMV share must be between 0% and 90%.")
    return df


def build_weekly_model(
    product_df,
    phase_inputs,
    weeks_per_phase,
    promo_60d,
    logistics_cost,
    affiliate_commission_rate,
    ads_roas,
):
    aov = product_df["AOV"].to_numpy()
    gross_margin = product_df["Gross Margin"].to_numpy()
    platform_fee_rates = product_df["Platform Fee Rate"].to_numpy()
    product_cost_per_unit = aov * (1 - gross_margin)
    sample_all_in_cost_per_unit = product_cost_per_unit + float(logistics_cost)

    videos_per_sample = product_df["Videos / Sample"].to_numpy()
    clicks_per_video = product_df["Clicks / Video"].to_numpy()
    click_to_order_rate = product_df["Click-to-order Rate"].to_numpy()
    shop_tab_share = product_df["ShopTab GMV Share"].to_numpy()

    rows = []
    video_history = []
    cumulative_videos_p = np.zeros(len(product_df))
    global_week = 0

    for phase in phase_inputs:
        for week_idx in range(int(weeks_per_phase)):
            global_week += 1

            samples_p = np.full(len(product_df), float(phase["samples_per_sku"]))
            new_videos_p = samples_p * videos_per_sample
            video_history.append(new_videos_p)
            cumulative_videos_p += new_videos_p

            active_videos_p = np.zeros(len(product_df))
            for age, weight in enumerate(CONTENT_DECAY_WEIGHTS):
                history_idx = len(video_history) - 1 - age
                if history_idx >= 0:
                    active_videos_p += video_history[history_idx] * weight

            organic_clicks_p = active_videos_p * clicks_per_video
            organic_orders_p = organic_clicks_p * click_to_order_rate
            affiliate_organic_gmv_p = organic_orders_p * aov
            organic_gmv_p = np.divide(
                affiliate_organic_gmv_p,
                1 - shop_tab_share,
                out=np.zeros_like(affiliate_organic_gmv_p),
                where=(1 - shop_tab_share) > 0,
            )
            shop_tab_organic_gmv_p = organic_gmv_p * shop_tab_share

            take_rate = float(phase["take_rate"])
            if take_rate * ads_roas >= 0.90:
                raise ValueError("Take Rate x Ads ROAS must be below 90%.")

            total_gmv_p = organic_gmv_p / (1 - take_rate * ads_roas)
            paid_gmv_p = total_gmv_p - organic_gmv_p
            orders_p = total_gmv_p / aov

            affiliate_mix_p = np.divide(
                affiliate_organic_gmv_p,
                organic_gmv_p,
                out=np.zeros_like(affiliate_organic_gmv_p),
                where=organic_gmv_p > 0,
            )
            shop_tab_paid_gmv_p = paid_gmv_p * (1 - affiliate_mix_p)
            affiliate_paid_gmv_p = paid_gmv_p * affiliate_mix_p
            shop_tab_gmv_p = shop_tab_organic_gmv_p + shop_tab_paid_gmv_p
            affiliate_gmv_p = affiliate_organic_gmv_p + affiliate_paid_gmv_p

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
            fulfillment_cost = orders * float(logistics_cost)
            creator_commission = affiliate_gmv * float(affiliate_commission_rate)
            ads_cost = gmv * take_rate
            total_cost = cogs + platform_fee + creator_commission + ads_cost + samples_cost + fulfillment_cost

            rows.append({
                "Phase": phase_label(phase),
                "Phase Key": phase["key"],
                "Week in Phase": week_idx + 1,
                "Global Week": global_week,
                "Samples Sent": float(np.sum(samples_p)),
                "Avg Sample Cost / Unit": float(np.average(sample_all_in_cost_per_unit)) if len(sample_all_in_cost_per_unit) else 0.0,
                "New Videos": float(np.sum(new_videos_p)),
                "Active Videos": float(np.sum(active_videos_p)),
                "Cumulative Videos": float(np.sum(cumulative_videos_p)),
                "Product Clicks": float(np.sum(organic_clicks_p)),
                "Orders": orders,
                "Organic Funnel GMV": float(np.sum(organic_gmv_p)),
                "Affiliate Organic GMV": float(np.sum(affiliate_organic_gmv_p)),
                "ShopTab Organic GMV": float(np.sum(shop_tab_organic_gmv_p)),
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
        "Avg Sample Cost / Unit": "mean",
        "New Videos": "sum",
        "Cumulative Videos": "max",
        "Product Clicks": "sum",
        "Orders": "sum",
        "Organic Funnel GMV": "sum",
        "Affiliate Organic GMV": "sum",
        "ShopTab Organic GMV": "sum",
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
    total_sample_cost = df["Samples Cost"].sum()
    total_ads_cost = df["Ads Cost"].sum()
    return pd.DataFrame([{
        "Total Samples": total_samples,
        "Avg Sample Cost / Unit": df["Avg Sample Cost / Unit"].mean(),
        "Total Videos": df["New Videos"].sum(),
        "Total Clicks": df["Product Clicks"].sum(),
        "Total Orders": df["Orders"].sum(),
        "Total GMV": total_gmv,
        "Total Cost": df["Total Cost"].sum(),
        "Total Profit": total_profit,
        "Sample Investment": total_sample_cost,
        "Ads Investment": total_ads_cost,
        "Growth Investment": df["Growth Investment"].sum(),
        "Profit Margin": total_profit / total_gmv if total_gmv > 0 else 0,
        "GMV / Sample": total_gmv / total_samples if total_samples > 0 else 0,
        "Profit / Sample": total_profit / total_samples if total_samples > 0 else 0,
        "Videos / Sample": df["New Videos"].sum() / total_samples if total_samples > 0 else 0,
        "Orders / Sample": df["Orders"].sum() / total_samples if total_samples > 0 else 0,
        "GMV / Sample Cost": total_gmv / total_sample_cost if total_sample_cost > 0 else 0,
    }])


def first_positive_profit_week(df):
    hit = df[df["Profit"] > 0]
    return None if hit.empty else int(hit["Global Week"].iloc[0])


def first_cumulative_break_even_week(df):
    temp = df.copy()
    temp["Cumulative Profit"] = temp["Profit"].cumsum()
    hit = temp[temp["Cumulative Profit"] >= 0]
    return None if hit.empty else int(hit["Global Week"].iloc[0])


def main_gmv_channel(df):
    shop_tab_gmv = float(df["ShopTab GMV"].sum())
    affiliate_gmv = float(df["Affiliate Video GMV"].sum())
    if shop_tab_gmv >= affiliate_gmv:
        return f"ShopTab ({pct(shop_tab_gmv / (shop_tab_gmv + affiliate_gmv), 0)})" if shop_tab_gmv + affiliate_gmv > 0 else "ShopTab"
    return f"Affiliate video ({pct(affiliate_gmv / (shop_tab_gmv + affiliate_gmv), 0)})"


def apply_plotly_layout(fig, title, height=420):
    fig.update_layout(
        title={"text": title, "x": 0.02, "xanchor": "left"},
        height=height,
        margin=dict(l=24, r=24, t=64, b=36),
        paper_bgcolor="white",
        plot_bgcolor="#FAFBFC",
        font=dict(color="#111827", family="Arial, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#E5E7EB", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB", zeroline=False)
    return fig


def add_phase_bands(fig, df):
    phase_ranges = df.groupby(["Phase Key"], as_index=False).agg(
        start_week=("Global Week", "min"),
        end_week=("Global Week", "max"),
    )
    color_map = {p["key"]: p["color"] for p in PHASES}
    for _, row in phase_ranges.iterrows():
        fig.add_vrect(
            x0=row["start_week"] - 0.5,
            x1=row["end_week"] + 0.5,
            fillcolor=color_map.get(row["Phase Key"], "#F3F4F6"),
            opacity=0.28,
            line_width=0,
            layer="below",
        )


def make_weekly_chart(df, title, break_even_week=None):
    fig = go.Figure()
    add_phase_bands(fig, df)
    series = [
        ("Forecast GMV", "GMV", CHART_COLORS["gmv"]),
        ("Total Cost", "Total Cost", CHART_COLORS["cost"]),
        ("Profit", "Profit", CHART_COLORS["profit"]),
    ]
    for label, col, color in series:
        fig.add_trace(
            go.Scatter(
                x=df["Global Week"],
                y=df[col],
                mode="lines+markers",
                name=label,
                line=dict(color=color, width=3),
                marker=dict(size=7),
                hovertemplate=f"{label}: €%{{y:,.0f}}<extra></extra>",
            )
        )
    fig.add_hline(y=0, line_color="#6B7280", line_width=1)
    if break_even_week is not None:
        fig.add_vline(x=break_even_week, line_dash="dash", line_color="#6B7280")
    apply_plotly_layout(fig, title)
    fig.update_yaxes(tickprefix="€", tickformat=",.0f")
    fig.update_xaxes(title="Week")
    return fig


def make_cumulative_profit_chart(df, break_even_week=None):
    temp = df.copy()
    temp["Cumulative Profit"] = temp["Profit"].cumsum()
    fig = go.Figure()
    add_phase_bands(fig, temp)
    fig.add_trace(
        go.Scatter(
            x=temp["Global Week"],
            y=temp["Cumulative Profit"],
            mode="lines+markers",
            fill="tozeroy",
            name="Cumulative Profit",
            line=dict(color=CHART_COLORS["cumulative"], width=3),
            marker=dict(size=7),
            hovertemplate="Cumulative Profit: €%{y:,.0f}<extra></extra>",
        )
    )
    fig.add_hline(y=0, line_color="#6B7280", line_width=1)
    if break_even_week is not None:
        fig.add_vline(x=break_even_week, line_dash="dash", line_color="#6B7280")
    apply_plotly_layout(fig, "Cumulative Profit Trend")
    fig.update_yaxes(tickprefix="€", tickformat=",.0f")
    fig.update_xaxes(title="Week")
    return fig


def make_funnel_chart(df):
    values = pd.Series({
        "Samples": df["Samples Sent"].sum(),
        "Videos": df["New Videos"].sum(),
        "Clicks": df["Product Clicks"].sum(),
        "Orders": df["Orders"].sum(),
    })
    display = values.sort_values(ascending=True)
    fig = go.Figure(
        go.Bar(
            x=display.values,
            y=display.index,
            orientation="h",
            marker=dict(color=["#93C5FD", "#60A5FA", "#2563EB", "#1D4ED8"]),
            text=[f"{v:,.0f}" for v in display.values],
            textposition="outside",
            hovertemplate="%{y}: %{x:,.0f}<extra></extra>",
        )
    )
    apply_plotly_layout(fig, "Funnel Summary", height=360)
    fig.update_xaxes(showticklabels=False, title="")
    fig.update_yaxes(title="")
    return fig


def make_channel_mix_chart(phase_summary):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=phase_summary["Phase"],
        y=phase_summary["ShopTab GMV"],
        name="ShopTab GMV",
        marker_color="#2563EB",
        hovertemplate="ShopTab GMV: €%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=phase_summary["Phase"],
        y=phase_summary["Affiliate Video GMV"],
        name="Affiliate Video GMV",
        marker_color="#F97316",
        hovertemplate="Affiliate Video GMV: €%{y:,.0f}<extra></extra>",
    ))
    apply_plotly_layout(fig, T["channel_mix"], height=390)
    fig.update_layout(barmode="stack")
    fig.update_yaxes(tickprefix="€", tickformat=",.0f")
    return fig


def make_phase_total_chart(phase_row):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=["Forecast GMV"],
            y=[float(phase_row["GMV"])],
            name="Forecast GMV",
            marker_color="#2563EB",
            text=[money(phase_row["GMV"], 0)],
            textposition="outside",
            hovertemplate="Forecast GMV: €%{y:,.0f}<extra></extra>",
        )
    )

    cost_parts = [
        ("COGS", "COGS", "#64748B"),
        ("Platform Fee", "Platform Fee", "#F97316"),
        ("Creator Commission", "Creator Commission", "#EC4899"),
        ("Fulfillment Cost", "Fulfillment Cost", "#14B8A6"),
        ("Sample Investment", "Samples Cost", "#8B5CF6"),
        ("Ads Investment", "Ads Cost", "#06B6D4"),
    ]
    for label, col, color in cost_parts:
        value = float(phase_row[col])
        if abs(value) <= 0:
            continue
        fig.add_trace(
            go.Bar(
                x=["Total Cost"],
                y=[value],
                name=label,
                marker_color=color,
                text=[money(value, 0)],
                textposition="inside",
                insidetextanchor="middle",
                hovertemplate=f"<b>{label}</b><br>Cost: €%{{y:,.0f}}<extra></extra>",
            )
        )

    profit_color = "#16A34A" if float(phase_row["Profit"]) >= 0 else "#DC2626"
    fig.add_trace(
        go.Bar(
            x=["Profit"],
            y=[float(phase_row["Profit"])],
            name="Profit",
            marker_color=profit_color,
            text=[money(phase_row["Profit"], 0)],
            textposition="outside",
            hovertemplate="Profit: €%{y:,.0f}<extra></extra>",
        )
    )

    apply_plotly_layout(fig, f"{phase_row['Phase']} - P&L Breakdown", height=540)
    fig.update_layout(
        barmode="stack",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,0.85)",
        ),
        margin=dict(l=28, r=32, t=78, b=118),
    )
    fig.add_hline(y=0, line_color="#6B7280", line_width=1)
    fig.update_yaxes(tickprefix="€", tickformat=",.0f")
    fig.update_xaxes(title="")
    return fig


def make_phase_cumulative_chart(phase_df, title):
    temp = phase_df.sort_values("Week in Phase").copy()
    temp["Cumulative GMV"] = temp["GMV"].cumsum()
    temp["Cumulative Total Cost"] = temp["Total Cost"].cumsum()
    temp["Cumulative Profit"] = temp["Profit"].cumsum()
    temp["Cumulative Sample Investment"] = temp["Samples Cost"].cumsum()
    temp["Cumulative Ads Investment"] = temp["Ads Cost"].cumsum()
    temp["Cumulative Growth Investment"] = temp["Growth Investment"].cumsum()

    fig = go.Figure()
    series = [
        ("GMV", "Cumulative GMV", CHART_COLORS["gmv"], "solid", 4, 9),
        ("Total Cost", "Cumulative Total Cost", CHART_COLORS["cost"], "solid", 4, 9),
        ("Profit", "Cumulative Profit", CHART_COLORS["profit"], "solid", 4, 9),
        ("Growth Investment", "Cumulative Growth Investment", "#8B5CF6", "dash", 3, 8),
    ]
    if float(temp["Cumulative Ads Investment"].abs().sum()) > 0:
        series.append(("Ads Investment", "Cumulative Ads Investment", "#06B6D4", "dot", 2, 7))
    for label, col, color, dash, width, marker_size in series:
        fig.add_trace(
            go.Scatter(
                x=temp["Week in Phase"],
                y=temp[col],
                mode="lines+markers",
                name=label,
                line=dict(color=color, width=width, dash=dash),
                marker=dict(size=marker_size, color=color, line=dict(color="white", width=1.5)),
                hovertemplate=f"{label}: €%{{y:,.0f}}<extra></extra>",
            )
        )

    for label, col, color, _, _, _ in series[:4]:
        last = temp.iloc[-1]
        fig.add_annotation(
            x=last["Week in Phase"],
            y=last[col],
            text=money(last[col], 0),
            showarrow=False,
            xshift=34,
            font=dict(size=12, color=color),
            bgcolor="rgba(255,255,255,0.82)",
            bordercolor=color,
            borderwidth=1,
            borderpad=3,
        )

    fig.add_hline(y=0, line_color="#6B7280", line_width=1, opacity=0.75)
    apply_plotly_layout(fig, f"{title} - Cumulative Trend", height=520)
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,0.85)",
        ),
        margin=dict(l=28, r=98, t=78, b=104),
    )
    fig.update_yaxes(tickprefix="€", tickformat=",.0f")
    fig.update_xaxes(title="Week in Phase", dtick=1, tickmode="linear")
    return fig


def format_table(df, money_cols=None, pct_cols=None, number_cols=None, decimal_cols=None):
    out = df.copy()
    for col in dict.fromkeys(money_cols or []):
        if col in out.columns:
            out[col] = out[col].map(lambda x: money(x, 0))
    for col in dict.fromkeys(pct_cols or []):
        if col in out.columns:
            out[col] = out[col].map(lambda x: pct(x, 1))
    for col in dict.fromkeys(number_cols or []):
        if col in out.columns:
            out[col] = out[col].map(lambda x: f"{float(x):,.0f}")
    for col in dict.fromkeys(decimal_cols or []):
        if col in out.columns:
            out[col] = out[col].map(lambda x: f"{float(x):,.2f}")
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
    logistics_cost = st.number_input(T["fulfillment"], min_value=0.0, value=5.0, step=0.5)
    affiliate_commission_rate = st.slider(T["creator_commission"], min_value=0.0, max_value=0.5, value=0.10, step=0.01)
    ads_roas = st.number_input(T["ads_roas"], min_value=0.1, max_value=8.0, value=5.0, step=0.1)
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
            st.number_input("AOV (€)", min_value=0.01, step=1.0, key=f"aov_{i}", help=T["aov_help"])
        with c5:
            st.number_input(T["gross_margin"], min_value=5.0, max_value=90.0, step=1.0, key=f"gross_margin_pct_{i}", help=T["gross_margin_help"])
        with c6:
            st.metric(T["platform_commission"], pct(PLATFORM_COMMISSION[category], 0))

        with st.expander(T["benchmark_expander"], expanded=False):
            b1, b2, b3, b4 = st.columns(4)
            with b1:
                st.number_input(T["videos_sample"], min_value=0.0, max_value=5.0, step=0.05, key=f"videos_per_sample_{i}", help=T["videos_sample_help"])
            with b2:
                st.number_input(T["clicks_video"], min_value=0.0, max_value=100000.0, step=10.0, key=f"clicks_per_video_{i}", help=T["clicks_video_help"])
            with b3:
                st.number_input(T["click_order"], min_value=0.0, max_value=100.0, step=0.1, key=f"click_to_order_pct_{i}", help=T["click_order_help"])
            with b4:
                st.number_input(T["shoptab_share"], min_value=0.0, max_value=90.0, step=1.0, key=f"shop_tab_share_pct_{i}", help=T["shoptab_share_help"])

if st.button(T["generate"], type="primary"):
    st.session_state["has_generated"] = True

if st.session_state.get("has_generated", False):
    try:
        product_df = build_product_df(int(n_skus))
        df_all = build_weekly_model(
            product_df=product_df,
            phase_inputs=phase_inputs,
            weeks_per_phase=int(weeks_per_phase),
            promo_60d=bool(promo_60d),
            logistics_cost=float(logistics_cost),
            affiliate_commission_rate=float(affiliate_commission_rate),
            ads_roas=float(ads_roas),
        )
        phase_summary = build_phase_summary(df_all)
        overall_summary = build_overall_summary(df_all)
        weekly_be = first_positive_profit_week(df_all)
        cumulative_be = first_cumulative_break_even_week(df_all)

        overall = overall_summary.iloc[0]
        weekly_be_label = f"Week {weekly_be}" if weekly_be else T["not_reached"]
        cumulative_be_label = f"Week {cumulative_be}" if cumulative_be else T["not_reached"]

        st.subheader(T["executive_summary"])
        st.success(
            T["executive_summary_text"].format(
                weeks=int(weeks_per_phase) * len(PHASES),
                samples=f"{overall['Total Samples']:,.0f}",
                gmv=money(overall["Total GMV"], 0),
                profit=money(overall["Total Profit"], 0),
                growth_investment=money(overall["Growth Investment"], 0),
                sample_investment=money(overall["Sample Investment"], 0),
                ads_investment=money(overall["Ads Investment"], 0),
                gmv_per_sample=money(overall["GMV / Sample"], 0),
                profit_per_sample=money(overall["Profit / Sample"], 0),
                main_channel=main_gmv_channel(df_all),
                weekly_be=weekly_be_label,
                cumulative_be=cumulative_be_label,
            )
        )

        st.subheader(T["sku_mix"])
        product_display = product_df.copy()
        product_display["AOV"] = product_display["AOV"].map(lambda x: money(x, 2))
        product_display["Gross Margin"] = product_display["Gross Margin"].map(lambda x: pct(x, 0))
        product_display["Platform Fee Rate"] = product_display["Platform Fee Rate"].map(lambda x: pct(x, 0))
        product_display["Click-to-order Rate"] = product_display["Click-to-order Rate"].map(lambda x: pct(x, 1))
        product_display["ShopTab GMV Share"] = product_display["ShopTab GMV Share"].map(lambda x: pct(x, 0))
        st.dataframe(product_display, use_container_width=True)

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
        m9, m10 = st.columns(2)
        m9.metric(T["sample_investment"], money(df_all["Samples Cost"].sum(), 0))
        m10.metric(T["avg_sample_cost"], money(overall["Avg Sample Cost / Unit"], 2))

        st.subheader(T["sample_roi_title"])
        r1, r2, r3, r4 = st.columns(4)
        r1.metric(T["gmv_per_sample"], money(overall["GMV / Sample"], 0))
        r2.metric(T["profit_per_sample"], money(overall["Profit / Sample"], 0))
        r3.metric(T["videos_per_sample_kpi"], f"{overall['Videos / Sample']:.2f}")
        r4.metric(T["orders_per_sample"], f"{overall['Orders / Sample']:.2f}")
        r5, r6 = st.columns(2)
        r5.metric(T["sample_gmv_roi"], f"{overall['GMV / Sample Cost']:.1f}x")
        r6.metric(T["ads_investment"], money(overall["Ads Investment"], 0))

        st.subheader(T["charts"])
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(make_weekly_chart(df_all, "Overall Weekly Trend", weekly_be), use_container_width=True)
        with c2:
            st.plotly_chart(make_cumulative_profit_chart(df_all, cumulative_be), use_container_width=True)
        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(make_funnel_chart(df_all), use_container_width=True)
        with c4:
            st.plotly_chart(make_channel_mix_chart(phase_summary), use_container_width=True)

        st.subheader(T["phase_trend"])
        tabs = st.tabs([phase_label(p) for p in phase_inputs])
        for tab, phase in zip(tabs, phase_inputs):
            with tab:
                phase_df = df_all[df_all["Phase Key"] == phase["key"]].copy()
                phase_row = phase_summary[phase_summary["Phase Key"] == phase["key"]].iloc[0]
                p1, p2, p3, p4, p5 = st.columns(5)
                p1.metric(T["total_gmv"], money(phase_row["GMV"], 0))
                p2.metric(T["total_cost"], money(phase_row["Total Cost"], 0))
                p3.metric(T["total_profit"], money(phase_row["Profit"], 0))
                p4.metric(T["sample_investment"], money(phase_row["Samples Cost"], 0))
                p5.metric(T["ads_investment"], money(phase_row["Ads Cost"], 0))

                chart_mode = st.radio(
                    T["phase_chart_mode"],
                    options=[T["phase_chart_cumulative"], T["phase_chart_total"]],
                    horizontal=True,
                    key=f"phase_chart_mode_{phase['key']}",
                )
                if chart_mode == T["phase_chart_cumulative"]:
                    st.plotly_chart(make_phase_cumulative_chart(phase_df, phase_label(phase)), use_container_width=True)
                else:
                    st.plotly_chart(make_phase_total_chart(phase_row), use_container_width=True)

        money_cols = [
            "Organic Funnel GMV", "Affiliate Organic GMV", "ShopTab Organic GMV",
            "Paid GMV Lift", "GMV", "ShopTab GMV",
            "Affiliate Video GMV", "COGS", "Gross Profit", "Platform Fee",
            "Creator Commission", "Ads Cost", "Samples Cost", "Fulfillment Cost",
            "Growth Investment", "Total Cost", "Profit", "GMV / Sample",
            "Profit / Sample", "Total GMV", "Total Profit", "Avg Sample Cost / Unit",
            "Sample Investment", "Ads Investment",
        ]
        number_cols = [
            "Samples Sent", "New Videos", "Active Videos", "Cumulative Videos", "Product Clicks", "Orders",
            "Total Samples", "Total Videos", "Total Clicks", "Total Orders",
        ]
        decimal_cols = [
            "Videos / Sample", "Orders / Sample", "GMV / Sample Cost",
        ]

        st.subheader(T["summary"])
        st.markdown(f"**{T['phase_summary']}**")
        st.dataframe(
            format_table(phase_summary.drop(columns=["Phase Key"]), money_cols=money_cols, pct_cols=["Profit Margin"], number_cols=number_cols, decimal_cols=decimal_cols),
            use_container_width=True,
        )

        st.subheader(T["break_even"])
        b1, b2 = st.columns(2)
        with b1:
            if weekly_be:
                st.success(f"{T['weekly_profit']}: Week {weekly_be}")
            else:
                st.warning(f"{T['weekly_profit']}: {T['not_reached']}")
        with b2:
            if cumulative_be:
                st.success(f"{T['cumulative_be']}: Week {cumulative_be}")
            else:
                st.warning(f"{T['cumulative_be']}: {T['not_reached']}")

        with st.expander(T["view_details"], expanded=False):
            st.markdown(f"**{T['overall_summary']}**")
            st.dataframe(
                format_table(overall_summary, money_cols=money_cols, pct_cols=["Profit Margin"], number_cols=number_cols, decimal_cols=decimal_cols),
                use_container_width=True,
            )
            st.markdown(f"**{T['weekly_details']}**")
            weekly_display = format_table(df_all.drop(columns=["Phase Key"]), money_cols=money_cols, pct_cols=["Ads Take Rate"], number_cols=number_cols, decimal_cols=decimal_cols)
            st.dataframe(weekly_display, use_container_width=True)

            d1, d2 = st.columns(2)
            d1.download_button(T["download_weekly"], data=csv_bytes(df_all), file_name="weekly_details.csv", mime="text/csv")
            d2.download_button(T["download_phase"], data=csv_bytes(phase_summary), file_name="phase_summary.csv", mime="text/csv")

    except Exception as e:
        st.error(f"{T['input_error']}: {e}")
