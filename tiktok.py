import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime
from html import escape


st.set_page_config(page_title="TikTok Shop Growth Visualizer", layout="wide")


# Planning benchmark estimates. Align inputs with AM guidance and
# similar TikTok Shop category or merchant data when available.


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
# shop_tab_share: reference share used to seed the Store/Search natural-sales assumption
CATEGORY_PRESETS = {
    "Home Living": {
        "Kitchenware": {"aov": 29.90, "videos_per_sample": 1.50, "clicks_per_video": 750, "click_to_order_rate": 0.032, "shop_tab_share": 0.35},
        "Home Supplies": {"aov": 24.90, "videos_per_sample": 1.45, "clicks_per_video": 680, "click_to_order_rate": 0.035, "shop_tab_share": 0.35},
        "Textiles & Soft Furnishings": {"aov": 34.90, "videos_per_sample": 1.35, "clicks_per_video": 620, "click_to_order_rate": 0.028, "shop_tab_share": 0.38},
        "Tools & Hardware": {"aov": 27.90, "videos_per_sample": 1.15, "clicks_per_video": 430, "click_to_order_rate": 0.024, "shop_tab_share": 0.40},
        "Furniture": {"aov": 129.00, "videos_per_sample": 1.00, "clicks_per_video": 300, "click_to_order_rate": 0.010, "shop_tab_share": 0.45},
        "Home Improvement": {"aov": 39.90, "videos_per_sample": 1.20, "clicks_per_video": 460, "click_to_order_rate": 0.022, "shop_tab_share": 0.40},
        "Toys & Hobbies": {"aov": 24.90, "videos_per_sample": 1.55, "clicks_per_video": 720, "click_to_order_rate": 0.032, "shop_tab_share": 0.35},
        "Books, Magazines & Audio": {"aov": 18.90, "videos_per_sample": 1.00, "clicks_per_video": 300, "click_to_order_rate": 0.022, "shop_tab_share": 0.40},
        "Collectibles": {"aov": 39.90, "videos_per_sample": 1.35, "clicks_per_video": 600, "click_to_order_rate": 0.030, "shop_tab_share": 0.35},
    },
    "Electronics": {
        "Phones & Electronics": {"aov": 69.00, "videos_per_sample": 1.10, "clicks_per_video": 520, "click_to_order_rate": 0.018, "shop_tab_share": 0.42},
        "Computers & Office Equipment": {"aov": 89.00, "videos_per_sample": 1.00, "clicks_per_video": 360, "click_to_order_rate": 0.013, "shop_tab_share": 0.45},
        "Household Appliances": {"aov": 59.00, "videos_per_sample": 1.15, "clicks_per_video": 460, "click_to_order_rate": 0.018, "shop_tab_share": 0.42},
        "Automotive & Motorcycle": {"aov": 39.90, "videos_per_sample": 1.00, "clicks_per_video": 360, "click_to_order_rate": 0.015, "shop_tab_share": 0.45},
        "Smart Home Systems": {"aov": 79.00, "videos_per_sample": 1.05, "clicks_per_video": 420, "click_to_order_rate": 0.015, "shop_tab_share": 0.44},
        "Audio & Headphones": {"aov": 49.90, "videos_per_sample": 1.20, "clicks_per_video": 650, "click_to_order_rate": 0.020, "shop_tab_share": 0.40},
        "Mobile Accessories": {"aov": 19.90, "videos_per_sample": 1.45, "clicks_per_video": 850, "click_to_order_rate": 0.035, "shop_tab_share": 0.35},
    },
    "FMCG": {
        "Food & Beverages": {"aov": 18.90, "videos_per_sample": 1.80, "clicks_per_video": 950, "click_to_order_rate": 0.045, "shop_tab_share": 0.32},
        "Health": {"aov": 29.90, "videos_per_sample": 1.45, "clicks_per_video": 720, "click_to_order_rate": 0.035, "shop_tab_share": 0.35},
        "Baby & Maternity": {"aov": 34.90, "videos_per_sample": 1.55, "clicks_per_video": 780, "click_to_order_rate": 0.040, "shop_tab_share": 0.35},
        "Pet Supplies": {"aov": 24.90, "videos_per_sample": 1.75, "clicks_per_video": 900, "click_to_order_rate": 0.038, "shop_tab_share": 0.32},
        "Household Consumables": {"aov": 19.90, "videos_per_sample": 1.55, "clicks_per_video": 720, "click_to_order_rate": 0.040, "shop_tab_share": 0.35},
        "Personal Care Consumables": {"aov": 19.90, "videos_per_sample": 1.90, "clicks_per_video": 1000, "click_to_order_rate": 0.050, "shop_tab_share": 0.30},
    },
    "Beauty": {
        "Beauty & Personal Care": {"aov": 24.90, "videos_per_sample": 2.00, "clicks_per_video": 1200, "click_to_order_rate": 0.055, "shop_tab_share": 0.30},
        "Skincare": {"aov": 29.90, "videos_per_sample": 2.10, "clicks_per_video": 1400, "click_to_order_rate": 0.060, "shop_tab_share": 0.28},
        "Makeup": {"aov": 22.90, "videos_per_sample": 2.25, "clicks_per_video": 1500, "click_to_order_rate": 0.065, "shop_tab_share": 0.28},
        "Hair Care & Styling": {"aov": 34.90, "videos_per_sample": 1.85, "clicks_per_video": 1100, "click_to_order_rate": 0.045, "shop_tab_share": 0.32},
        "Fragrance": {"aov": 39.90, "videos_per_sample": 1.30, "clicks_per_video": 650, "click_to_order_rate": 0.025, "shop_tab_share": 0.40},
        "Beauty Devices": {"aov": 59.00, "videos_per_sample": 1.35, "clicks_per_video": 750, "click_to_order_rate": 0.030, "shop_tab_share": 0.38},
        "Men's Grooming": {"aov": 24.90, "videos_per_sample": 1.50, "clicks_per_video": 720, "click_to_order_rate": 0.035, "shop_tab_share": 0.35},
    },
    "Fashion": {
        "Womenswear & Underwear": {"aov": 29.90, "videos_per_sample": 1.70, "clicks_per_video": 950, "click_to_order_rate": 0.036, "shop_tab_share": 0.35},
        "Menswear & Underwear": {"aov": 34.90, "videos_per_sample": 1.50, "clicks_per_video": 780, "click_to_order_rate": 0.032, "shop_tab_share": 0.35},
        "Fashion Accessories": {"aov": 19.90, "videos_per_sample": 1.85, "clicks_per_video": 1100, "click_to_order_rate": 0.045, "shop_tab_share": 0.32},
        "Shoes": {"aov": 49.90, "videos_per_sample": 1.25, "clicks_per_video": 650, "click_to_order_rate": 0.028, "shop_tab_share": 0.38},
        "Luggage & Bags": {"aov": 45.90, "videos_per_sample": 1.10, "clicks_per_video": 520, "click_to_order_rate": 0.020, "shop_tab_share": 0.42},
        "Jewelry Accessories & Derivatives": {"aov": 24.90, "videos_per_sample": 1.80, "clicks_per_video": 1050, "click_to_order_rate": 0.040, "shop_tab_share": 0.35},
        "Kids' Fashion": {"aov": 24.90, "videos_per_sample": 1.40, "clicks_per_video": 700, "click_to_order_rate": 0.032, "shop_tab_share": 0.38},
        "Modest Fashion": {"aov": 29.90, "videos_per_sample": 1.35, "clicks_per_video": 680, "click_to_order_rate": 0.032, "shop_tab_share": 0.38},
        "Sports & Outdoor": {"aov": 49.90, "videos_per_sample": 1.20, "clicks_per_video": 620, "click_to_order_rate": 0.022, "shop_tab_share": 0.38},
    },
}


PHASES = [
    {"key": "phase1", "name": "Phase 1 - Cold Start", "samples_per_sku": 30, "take_rate": 0.00, "color": "#EAF4FF"},
    {"key": "phase2", "name": "Phase 2 - Growth", "samples_per_sku": 25, "take_rate": 0.05, "color": "#EEFBEF"},
    {"key": "phase3", "name": "Phase 3 - Scale", "samples_per_sku": 20, "take_rate": 0.10, "color": "#FFF4E8"},
]

PROMO_WEEKS = 9
FBT_FREE_SHIPPING_AOV_THRESHOLD = 20.0
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
        "plan_setup": "Plan Setup",
        "cost_assumptions": "Cost Assumptions",
        "growth_levers": "Growth Levers",
        "reset_defaults": "Reset defaults",
        "reset_confirm": "Confirm reset",
        "reset_pending": "This will reset all inputs to the default planning setup. Click Confirm reset to continue.",
        "meeting_mode": "Meeting mode",
        "meeting_mode_help": "Hide detailed setup and data tables after generation, keeping the page focused on the client-facing summary and charts.",
        "meeting_mode_sidebar_note": "Meeting mode is on. Detailed controls are hidden after generation; turn it off to edit assumptions.",
        "sku_count": "Number of SKUs",
        "promo": "New seller: apply first-60-day 5% platform fee",
        "promo_yes": "Apply first-60-day 5% platform fee",
        "promo_no": "No, use default category commission",
        "fulfillment": "Logistics cost €/unit or order",
        "fbt": "Use FBT free shipping",
        "fbt_yes": "Yes, set logistics cost to €0",
        "fbt_no": "No, use manual logistics cost",
        "fbt_help": "Planning assumption: when selected, SKUs with AOV above €20 use €0 logistics cost; lower-AOV SKUs keep the manual logistics cost.",
        "creator_commission": "Organic creator commission",
        "paid_creator_commission": "Paid-traffic creator commission",
        "organic_click_window": "Content traffic tail period (weeks)",
        "ads_roas": "Ads ROAS assumption",
        "weeks_phase": "Weeks / phase",
        "phase_controls": "Phase Controls",
        "phase1": "Phase 1 - Cold Start",
        "phase2": "Phase 2 - Growth",
        "phase3": "Phase 3 - Scale",
        "phase1_objective": "Objective: validate creator content, seed first product videos, and build initial conversion signals.",
        "phase2_objective": "Objective: reduce sample intensity, start paid amplification, and convert validated content into scalable GMV.",
        "phase3_objective": "Objective: scale winning content with a higher paid acceleration budget while Store/Search and content-tail sales continue compounding.",
        "take_rate": "Paid acceleration budget (% of GMV)",
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
        "shoptab_share": "Store/Search GMV share (%)",
        "organic_commission_sku": "Organic creator commission (%)",
        "paid_commission_sku": "Paid-traffic creator commission (%)",
        "aov_help": "Average selling price per order for this subcategory. Current default is a planning benchmark; we recommend aligning with your AM and using TikTok Shop data from similar categories or merchants.",
        "gross_margin_help": "Merchant gross margin before platform fee, creator commission, ads, logistics, and sample investment. Product cost is calculated as AOV x (1 - gross margin).",
        "videos_sample_help": "Estimated creator videos generated per sample sent. Example: 1.50 means 100 samples generate about 150 videos. Current value is a planning benchmark; align with your AM using similar-category TikTok Shop data where available.",
        "clicks_video_help": "Estimated product-page clicks generated by each creator video during the content traffic tail period. Current value is a planning benchmark; align with your AM using similar-category TikTok Shop data where available.",
        "click_order_help": "Estimated conversion from product click to order. Current value is a public e-commerce/social-commerce benchmark placeholder.",
        "shoptab_share_help": "Share of organic GMV attributed to Store/Search/Mall/ShopTab after users are influenced by content. This GMV does not carry creator affiliate commission. Align this input with your AM using similar-category TikTok Shop data where available.",
        "organic_commission_help": "SKU-level standard affiliate commission for orders generated by creator organic traffic.",
        "paid_commission_help": "SKU-level commission for orders generated by paid traffic using creator affiliate content. TikTok Shop Ads can use a separate Shop Ads commission rate; current default is 5%.",
        "generate": "Generate Simulator",
        "sku_mix": "SKU Mix & Funnel Assumptions",
        "total_gmv": "Total GMV",
        "total_cost": "Total Cost",
        "sales_contribution": "Profit before samples & ads",
        "contribution_margin": "Contribution Margin",
        "total_profit": "Total Profit",
        "profit_margin": "Profit Margin",
        "growth_investment": "Growth Investment",
        "samples_sent": "Samples Sent",
        "videos_generated": "Videos Generated",
        "product_clicks": "Product Clicks",
        "orders": "Orders",
        "charts": "Charts",
        "overall_weekly": "Overall Weekly Trend",
        "cumulative_profit_trend": "Cumulative Profit Trend",
        "funnel_summary": "Funnel Summary",
        "forecast_gmv": "Forecast GMV",
        "total_cost_label": "Total Cost",
        "profit_label": "Profit",
        "net_profit": "Net Profit",
        "week": "Week",
        "samples_label": "Samples",
        "videos_label": "Videos",
        "clicks_label": "Clicks",
        "orders_label": "Orders",
        "affiliate_video_gmv": "Affiliate Video GMV",
        "shoptab_gmv": "Store/Search GMV",
        "phase_total_breakdown": "Profit Bridge",
        "supporting_charts": "Supporting Charts",
        "investment_split": "Investment Split",
        "product_profile": "Product Profile",
        "hero_title": "{weeks}-week incubation plan for {skus} SKUs",
        "hero_subtitle": "Projected {gmv} GMV with {growth_investment} growth investment. Break-even: {break_even}.",
        "hero_gmv": "Projected GMV",
        "hero_investment": "Growth Investment",
        "hero_break_even": "Break-even",
        "chart_insight": "Chart Insight",
        "overall_chart_insight": "GMV moves from {start_gmv} in Week 1 to {end_gmv} by Week {end_week}. The plan's cumulative profit ends at {cum_profit}.",
        "phase_chart_insight": "{phase} ends with {gmv} GMV, {profit} profit, and {investment} growth investment.",
        "client_narrative": "Plan Interpretation",
        "narrative_what": "What happens: The model estimates {gmv} GMV and {profit} total profit over {weeks} weeks.",
        "narrative_why": "Why it happens: The largest GMV source is {channel}, supported by {samples} samples and {videos} creator videos.",
        "narrative_next": "What to do next: Focus the next discussion on {driver}, the largest cost driver, and align funnel inputs with your AM using TikTok Shop data from similar categories or merchants.",
        "health_check": "Planning Notes",
        "health_ok": "No major assumption risk detected under the current setup.",
        "health_take_rate": "Paid acceleration budget x ROAS is high in at least one phase. Check whether the implied paid GMV lift is realistic.",
        "health_sample_roi": "Sample ROI is low. Review sample quantity, AOV, conversion rate, or sample cost.",
        "health_profit_negative": "Total profit is negative. The largest cost driver is {driver}.",
        "health_shoptab": "At least one SKU has a high Store/Search GMV share. Align this with your AM using similar-category TikTok Shop data before presenting as a firm forecast.",
        "health_conversion": "At least one SKU has a high click-to-order conversion rate. Consider using a conservative value unless similar-category TikTok Shop data supports it.",
        "health_low_margin": "At least one SKU has a low gross margin. Check whether the category can absorb platform fee, logistics, creator commission, and paid acceleration cost.",
        "health_high_commission": "At least one SKU has a high creator commission. Confirm whether the commission level is needed for creator recruitment or can be optimized.",
        "health_aggressive_roas": "The Ads ROAS assumption is aggressive. Consider showing the forecast range rather than a single target.",
        "health_promo_cliff": "Profit weakens after the first-60-day platform fee benefit. Review pricing, margin, or paid acceleration before the fee step-up.",
        "path_to_be": "Path to Break-even",
        "path_be_reached": "Cumulative break-even is reached in {week}. The final cumulative profit is {profit}.",
        "path_be_gap": "Cumulative break-even is not reached. The remaining gap is {gap}, with {driver} as the largest cost driver.",
        "download_meeting_html": "Download meeting summary HTML",
        "export_materials": "Export Meeting Materials",
        "generated_on": "Generated on",
        "plan_length": "Plan length",
        "sku_count_meta": "SKU count",
        "meeting_notes": "Meeting Notes",
        "brand_name": "Brand name",
        "meeting_date": "Meeting date",
        "am_name": "AM name",
        "key_recommendation": "Key recommendation",
        "key_recommendation_default": "Align funnel assumptions with the AM, then use this plan to agree sample volume, paid acceleration budget, and next milestone.",
        "assumption_status": "Assumption status",
        "benchmark_input": "Benchmark input",
        "am_aligned_input": "AM-aligned input",
        "merchant_confirmed_input": "Merchant-confirmed input",
        "commercial_takeaways": "Commercial Takeaways",
        "forecast_range": "Forecast Range",
        "forecast_range_prompt": "! Forecast range available",
        "conservative_case": "Conservative",
        "base_case": "Base",
        "upside_case": "Upside",
        "forecast_range_note": "Range is a planning sensitivity around the current funnel assumptions. Benchmark inputs use a wider range; AM-aligned or merchant-confirmed inputs use a narrower range.",
        "investment_required": "Investment required",
        "expected_gmv": "Expected GMV",
        "payback_timing": "Payback timing",
        "main_upside_lever": "Main upside lever",
        "main_risk": "Main risk",
        "main_risk_text": "{driver} is the largest cost driver; validate this assumption before treating the forecast as a target.",
        "cost_explanation": "Cost Explanation",
        "cost_explanation_text": "Profit is mainly shaped by {driver}, which accounts for {share} of total cost. Sample investment is {sample_share} and ads investment is {ads_share} of total cost, so the biggest margin lever is not always the visible growth budget.",
        "planning_disclaimer": "This simulator is for planning discussion only. Please calibrate inputs with your AM and similar TikTok Shop category or merchant data before using the output as a business target.",
        "phase_trend": "Phase-by-Phase Trend",
        "summary": "Summary",
        "phase_summary": "Phase Summary",
        "phase_chart_mode": "Phase chart view",
        "phase_chart_total": "Profit bridge",
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
        "executive_dashboard": "Core Dashboard",
        "executive_summary_text": "In this {weeks}-week plan, the brand needs about {growth_investment} in growth investment, including {sample_investment} for samples and {ads_investment} for ads. The model estimates {gmv} GMV and {profit} total profit. Each sample contributes around {gmv_per_sample} GMV and {profit_per_sample} profit. The largest GMV driver is {main_channel}. Weekly break-even: {weekly_be}. Cumulative break-even: {cumulative_be}.",
        "sample_roi_title": "Sample ROI",
        "gmv_per_sample": "GMV / Sample",
        "profit_per_sample": "Profit / Sample",
        "videos_per_sample_kpi": "Videos / Sample",
        "orders_per_sample": "Orders / Sample",
        "sample_gmv_roi": "GMV / Sample Cost",
        "sample_roi_text": "Commercial read: every sample is expected to generate {gmv_per_sample} GMV and {orders_per_sample} orders across the full simulation period.",
        "cost_breakdown": "Cost Breakdown",
        "cost_breakdown_text": "Largest cost driver in this view is {driver}: {amount}, equal to {share} of total cost.",
        "cost_cogs": "Product cost / COGS",
        "cost_platform_fee": "Platform fee",
        "cost_creator_commission": "Creator commission",
        "cost_fulfillment": "Logistics",
        "cost_samples": "Sample investment",
        "cost_ads": "Ads investment",
        "phase_objective": "Phase Objective",
        "benchmark_info": "Data Notes",
        "benchmark_info_text": "Current AOV, video, click, conversion, and Store/Search assumptions are planning benchmarks. We recommend aligning with your AM and using TikTok Shop data from similar categories or merchants in your industry as inputs.",
        "model_assumptions": "Model Logic",
        "model_assumptions_text": "The model uses SKU-level content funnel assumptions, paid acceleration budget x ROAS to estimate paid GMV lift, Store/Search GMV with no creator commission, and FBT free shipping only for SKUs above €20 AOV when selected.",
        "download_customer_summary": "Download meeting summary CSV",
        "download_meeting_pdf": "Download meeting summary PDF",
        "view_details": "View detailed tables",
        "channel_mix": "GMV Channel Mix",
    },
    "zh": {
        "language": "语言",
        "title": "TikTok Shop Growth Visualizer",
        "caption": "基于德国公开 benchmark 的 SKU 寄样、达人视频、点击、GMV、成本和利润模拟器",
        "global_inputs": "全局输入",
        "plan_setup": "计划设置",
        "cost_assumptions": "成本假设",
        "growth_levers": "增长杠杆",
        "reset_defaults": "恢复默认值",
        "reset_confirm": "确认恢复默认值",
        "reset_pending": "此操作会将所有输入恢复到默认沙盘设置。如需继续，请点击确认恢复默认值。",
        "meeting_mode": "会议展示模式",
        "meeting_mode_help": "生成结果后隐藏详细设置和数据表，让页面聚焦总结和图表。",
        "meeting_mode_sidebar_note": "会议展示模式已开启。生成结果后详细参数会收起；如需修改假设，请关闭该模式。",
        "sku_count": "SKU 数量",
        "promo": "是否为新商家：适用前约60天平台费 5%",
        "promo_yes": "适用前约60天平台费 5%",
        "promo_no": "否，使用默认类目佣金",
        "fulfillment": "物流成本 €/件/单",
        "fbt": "使用 FBT 包邮",
        "fbt_yes": "是，物流成本按 €0 计算",
        "fbt_no": "否，使用手动物流成本",
        "fbt_help": "沙盘假设：勾选后，AOV 高于 €20 的 SKU 物流成本按 €0 计算；AOV 不高于 €20 的 SKU 仍使用手动物流成本。",
        "creator_commission": "自然流达人佣金",
        "paid_creator_commission": "广告流达人佣金",
        "organic_click_window": "内容流量长尾周期（周）",
        "ads_roas": "广告 ROAS 假设",
        "weeks_phase": "每阶段周数",
        "phase_controls": "阶段控制",
        "phase1": "阶段 1 - 冷启动",
        "phase2": "阶段 2 - 增长",
        "phase3": "阶段 3 - 放量",
        "phase1_objective": "目标：验证达人内容，沉淀第一批商品视频，并建立早期转化信号。",
        "phase2_objective": "目标：降低寄样强度，开始广告加热，把已验证内容转化为可放大的 GMV。",
        "phase3_objective": "目标：用更高付费加热预算放大优质内容，同时让店铺/Search 和内容长尾成交继续累积。",
        "take_rate": "付费加热预算占 GMV (%)",
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
        "shoptab_share": "店铺/Search GMV 占比 (%)",
        "organic_commission_sku": "自然流达人佣金 (%)",
        "paid_commission_sku": "广告流达人佣金 (%)",
        "aov_help": "该 subcategory 的平均成交客单价。当前默认值是 planning benchmark，建议和您的 AM 对齐，参考 TikTok Shop 上类似行业或类似商家的数据进行输入。",
        "gross_margin_help": "商家毛利率，不包含平台佣金、达人佣金、广告、物流和寄样投入。商品成本会按 AOV x (1 - 毛利率) 自动计算。",
        "videos_sample_help": "每寄出 1 个样品预计产生的达人视频数。例如 1.50 表示 100 个样品约产生 150 条视频。当前为 planning benchmark，建议和您的 AM 对齐，参考 TikTok Shop 上类似行业或类似商家的数据进行输入。",
        "clicks_video_help": "每条达人视频在内容流量长尾周期内预计带来的商品页点击数。当前为 planning benchmark，建议和您的 AM 对齐，参考 TikTok Shop 上类似行业或类似商家的数据进行输入。",
        "click_order_help": "商品页点击到下单的转化率。当前为公开电商/social commerce benchmark 占位值。",
        "shoptab_share_help": "被内容种草后，最终通过店铺页/Search/Mall/ShopTab 成交的 organic GMV 占比。这部分 GMV 不产生达人佣金。建议和您的 AM 对齐，参考 TikTok Shop 上类似行业或类似商家的数据进行输入。",
        "organic_commission_help": "SKU level 的标准达人佣金，用于达人自然流成交订单。",
        "paid_commission_help": "SKU level 的广告流达人佣金，用于通过达人内容广告加热产生的订单。TikTok Shop Ads 可以单独设置 Shop Ads commission rate；当前默认 5%。",
        "generate": "生成模拟结果",
        "sku_mix": "SKU 组合与漏斗假设",
        "total_gmv": "总 GMV",
        "total_cost": "总成本",
        "sales_contribution": "样品广告前利润",
        "contribution_margin": "贡献利润率",
        "total_profit": "总利润",
        "profit_margin": "利润率",
        "growth_investment": "增长投入",
        "samples_sent": "寄样数",
        "videos_generated": "产出视频数",
        "product_clicks": "商品点击数",
        "orders": "订单数",
        "charts": "图表",
        "overall_weekly": "整体周趋势",
        "cumulative_profit_trend": "累计利润趋势",
        "funnel_summary": "漏斗汇总",
        "forecast_gmv": "预测 GMV",
        "total_cost_label": "总成本",
        "profit_label": "利润",
        "net_profit": "净利润",
        "week": "周",
        "samples_label": "样品",
        "videos_label": "视频",
        "clicks_label": "点击",
        "orders_label": "订单",
        "affiliate_video_gmv": "达人视频 GMV",
        "shoptab_gmv": "店铺/Search GMV",
        "phase_total_breakdown": "利润桥",
        "supporting_charts": "辅助图表",
        "investment_split": "投入拆分",
        "product_profile": "产品组合",
        "hero_title": "{weeks} 周、{skus} 个 SKU 的孵化计划",
        "hero_subtitle": "预计产生 {gmv} GMV，需要 {growth_investment} 增长投入。Break-even：{break_even}。",
        "hero_gmv": "预测 GMV",
        "hero_investment": "增长投入",
        "hero_break_even": "Break-even",
        "chart_insight": "图表解读",
        "overall_chart_insight": "GMV 从第 1 周的 {start_gmv} 增长到第 {end_week} 周的 {end_gmv}，累计利润最终为 {cum_profit}。",
        "phase_chart_insight": "{phase} 结束时预计产生 {gmv} GMV，利润 {profit}，增长投入 {investment}。",
        "client_narrative": "计划解读",
        "narrative_what": "结果：模型预计在 {weeks} 周内产生 {gmv} GMV，总利润为 {profit}。",
        "narrative_why": "原因：最大的 GMV 来源是 {channel}，同时由 {samples} 个样品和 {videos} 条达人视频支撑。",
        "narrative_next": "下一步：建议重点讨论 {driver} 这个最大成本项，并和您的 AM 对齐，参考 TikTok Shop 上类似行业或类似商家的数据进行输入。",
        "health_check": "计划提示",
        "health_ok": "当前设置下没有发现明显假设风险。",
        "health_take_rate": "至少一个阶段的付费加热预算占比 x ROAS 偏高，建议确认广告带来的 GMV 增量是否合理。",
        "health_sample_roi": "样品 ROI 偏低，建议检查寄样数量、AOV、转化率或样品成本。",
        "health_profit_negative": "总利润为负，当前最大的成本项是 {driver}。",
        "health_shoptab": "至少一个 SKU 的店铺/Search GMV 占比较高，建议和您的 AM 对齐，参考类似行业或类似商家的数据后再作为正式预测。",
        "health_conversion": "至少一个 SKU 的点击到下单转化率偏高，建议和您的 AM 对齐后再作为正式预测；如暂无可参考数据，可先使用更保守的假设。",
        "health_low_margin": "至少一个 SKU 毛利率偏低，建议确认该类目是否能覆盖平台费、物流、达人佣金和付费加热成本。",
        "health_high_commission": "至少一个 SKU 的达人佣金偏高，建议确认该佣金是否确实有助于达人招募，或是否可以优化。",
        "health_aggressive_roas": "当前广告 ROAS 假设偏积极，建议用可信区间而不是单点结果来和客户沟通。",
        "health_promo_cliff": "前约60天平台费优惠结束后利润走弱，建议提前复核定价、毛利或付费加热节奏。",
        "path_to_be": "Break-even 路径",
        "path_be_reached": "累计 Break-even 在 {week} 达成，最终累计利润为 {profit}。",
        "path_be_gap": "当前计划尚未达到累计 Break-even，距离回本还差 {gap}，最大成本项是 {driver}。",
        "download_meeting_html": "下载会议总结 HTML",
        "export_materials": "导出会议材料",
        "generated_on": "生成时间",
        "plan_length": "计划周期",
        "sku_count_meta": "SKU 数量",
        "meeting_notes": "会议信息",
        "brand_name": "品牌名称",
        "meeting_date": "会议日期",
        "am_name": "AM 名称",
        "key_recommendation": "关键建议",
        "key_recommendation_default": "建议先和 AM 对齐漏斗假设，再用该计划确认寄样数量、付费加热预算和下一阶段里程碑。",
        "assumption_status": "假设状态",
        "benchmark_input": "Benchmark 输入",
        "am_aligned_input": "已和 AM 对齐",
        "merchant_confirmed_input": "商家已确认",
        "commercial_takeaways": "商业结论",
        "forecast_range": "结果可信区间",
        "forecast_range_prompt": "! 可查看结果可信区间",
        "conservative_case": "保守",
        "base_case": "基准",
        "upside_case": "乐观",
        "forecast_range_note": "该区间是基于当前漏斗假设的敏感性测算。Benchmark 输入使用更宽区间；已和 AM 对齐或商家确认的输入使用更窄区间。",
        "investment_required": "所需投入",
        "expected_gmv": "预计 GMV",
        "payback_timing": "回本时间",
        "main_upside_lever": "主要增长杠杆",
        "main_risk": "主要风险",
        "main_risk_text": "{driver} 是当前最大的成本项；建议在把结果作为目标前，先确认该假设是否合理。",
        "cost_explanation": "成本解释",
        "cost_explanation_text": "当前利润主要受 {driver} 影响，该项占总成本 {share}。样品投入占总成本 {sample_share}，广告投入占总成本 {ads_share}，因此最大的利润杠杆不一定是最显眼的增长预算。",
        "planning_disclaimer": "本工具仅用于业务规划讨论。建议和您的 AM 对齐，并结合 TikTok Shop 类似行业或类似商家的数据校准输入后，再将输出作为业务目标参考。",
        "phase_trend": "分阶段趋势",
        "summary": "汇总",
        "phase_summary": "阶段汇总",
        "phase_chart_mode": "阶段图表视图",
        "phase_chart_total": "利润桥",
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
        "executive_summary": "核心总结",
        "executive_dashboard": "核心看板",
        "executive_summary_text": "按当前 {weeks} 周计划，品牌预计需要准备 {growth_investment} 增长投入，其中样品投入 {sample_investment}，广告投入 {ads_investment}。模型预计产生 {gmv} GMV，最终总利润为 {profit}。平均每个样品预计带来 {gmv_per_sample} GMV 和 {profit_per_sample} 利润。当前最大的 GMV 来源是 {main_channel}。首次单周盈利：{weekly_be}；累计 Break-even：{cumulative_be}。",
        "sample_roi_title": "样品 ROI",
        "gmv_per_sample": "GMV / 样品",
        "profit_per_sample": "利润 / 样品",
        "videos_per_sample_kpi": "视频 / 样品",
        "orders_per_sample": "订单 / 样品",
        "sample_gmv_roi": "GMV / 样品成本",
        "sample_roi_text": "商业解读：在完整模拟周期内，平均每个样品预计带来 {gmv_per_sample} GMV 和 {orders_per_sample} 个订单。",
        "cost_breakdown": "成本拆解",
        "cost_breakdown_text": "当前视图中最大的成本项是 {driver}：{amount}，占总成本 {share}。",
        "cost_cogs": "商品成本 / COGS",
        "cost_platform_fee": "平台费",
        "cost_creator_commission": "达人佣金",
        "cost_fulfillment": "物流成本",
        "cost_samples": "样品投入",
        "cost_ads": "广告投入",
        "phase_objective": "阶段目标",
        "benchmark_info": "数据说明",
        "benchmark_info_text": "当前 AOV、视频、点击、转化率和店铺/Search 占比是 planning benchmark。建议和您的 AM 对齐，参考 TikTok Shop 上类似行业或类似商家的数据进行输入。",
        "model_assumptions": "模型逻辑",
        "model_assumptions_text": "模型基于 SKU level 内容漏斗假设，用付费加热预算占比 x ROAS 估算广告带来的 GMV 增量；店铺/Search GMV 不计达人佣金；勾选 FBT 时，仅 AOV 高于 €20 的 SKU 物流成本按 €0 计算。",
        "download_customer_summary": "下载会议总结 CSV",
        "download_meeting_pdf": "下载会议总结 PDF",
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
    "promo": "Neuer Seller: 5% Plattformgebühr für die ersten ~60 Tage anwenden",
    "promo_yes": "5% Plattformgebühr für die ersten ~60 Tage anwenden",
    "promo_no": "Nein, Standard-Kategoriekommission verwenden",
    "fulfillment": "Logistikkosten €/Stück oder Bestellung",
    "fbt": "FBT-Gratisversand nutzen",
    "fbt_yes": "Ja, Logistikkosten auf €0 setzen",
    "fbt_no": "Nein, manuelle Logistikkosten nutzen",
    "fbt_help": "Planungsannahme: Bei Auswahl nutzen SKUs mit AOV über €20 Logistikkosten von €0; SKUs mit niedrigerem AOV behalten die manuellen Logistikkosten.",
    "creator_commission": "Organische Creator-Provision",
    "paid_creator_commission": "Paid-Traffic-Creator-Provision",
    "organic_click_window": "Content-Tail-Zeitraum (Wochen)",
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
    "shoptab_share": "Store/Search GMV-Anteil (%)",
    "organic_commission_sku": "Organische Creator-Provision (%)",
    "paid_commission_sku": "Paid-Traffic-Creator-Provision (%)",
    "aov_help": "Durchschnittlicher Verkaufspreis pro Bestellung. Der aktuelle Standardwert ist ein Planning Benchmark; bitte mit dem AM abstimmen und TikTok-Shop-Daten ähnlicher Kategorien oder Händler nutzen.",
    "gross_margin_help": "Händler-Bruttomarge vor Plattformgebühr, Creator-Provision, Ads, Logistik und Sample-Investment. Produktkosten = AOV x (1 - Bruttomarge).",
    "videos_sample_help": "Geschätzte Creator-Videos pro versendetem Sample. Beispiel: 0,40 bedeutet ca. 40 Videos aus 100 Samples. Aktuell ein öffentlicher Benchmark-Platzhalter.",
    "clicks_video_help": "Geschätzte Produktseiten-Klicks pro Creator-Video über den Content-Tail. Aktuell ein öffentlicher Benchmark-Platzhalter.",
    "click_order_help": "Geschätzte Conversion von Produktklick zu Bestellung. Aktuell ein öffentlicher Benchmark-Platzhalter.",
    "shoptab_share_help": "Anteil des organischen GMV, der nach Content-Einfluss über Store/Search/Mall/ShopTab kauft. Dieser GMV trägt keine Creator-Provision. Bitte mit dem AM anhand ähnlicher TikTok-Shop-Kategorien oder Händler abstimmen.",
    "organic_commission_help": "SKU-spezifische Standard-Affiliate-Provision für Bestellungen aus organischem Creator-Traffic.",
    "paid_commission_help": "SKU-spezifische Provision für Bestellungen aus bezahltem Traffic mit Creator-Content. TikTok Shop Ads kann eine separate Shop Ads Commission Rate nutzen; aktueller Standard ist 5%.",
    "generate": "Simulator erzeugen",
    "sku_mix": "SKU-Mix & Funnel-Annahmen",
    "total_gmv": "Gesamt-GMV",
    "total_cost": "Gesamtkosten",
    "sales_contribution": "Sales Contribution",
    "contribution_margin": "Deckungsbeitragsmarge",
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
    "promo": "Nieuwe seller: 5% platform fee voor de eerste ~60 dagen toepassen",
    "promo_yes": "5% platform fee voor de eerste ~60 dagen toepassen",
    "promo_no": "Nee, standaard categoriecommissie gebruiken",
    "fulfillment": "Logistieke kosten €/stuk of order",
    "fbt": "FBT gratis verzending gebruiken",
    "fbt_yes": "Ja, logistieke kosten op €0 zetten",
    "fbt_no": "Nee, handmatige logistieke kosten gebruiken",
    "fbt_help": "Planningsaanname: wanneer geselecteerd, gebruiken SKU's met AOV boven €20 logistieke kosten van €0; lagere-AOV SKU's gebruiken de handmatige logistieke kosten.",
    "creator_commission": "Organische creator commissie",
    "paid_creator_commission": "Paid-traffic creator commissie",
    "organic_click_window": "Content traffic tail periode (weken)",
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
    "shoptab_share": "Store/Search GMV-aandeel (%)",
    "organic_commission_sku": "Organische creator commissie (%)",
    "paid_commission_sku": "Paid-traffic creator commissie (%)",
    "aov_help": "Gemiddelde verkoopprijs per order. De huidige standaardwaarde is een planning benchmark; stem af met de AM en gebruik TikTok Shop-data van vergelijkbare categorieen of merchants.",
    "gross_margin_help": "Brutomarge van de merchant voor platform fee, creator commissie, ads, logistiek en sample-investering. Productkosten = AOV x (1 - brutomarge).",
    "videos_sample_help": "Geschat aantal creator-video's per verzonden sample. Voorbeeld: 0,40 betekent circa 40 video's uit 100 samples. Huidige waarde is een publieke benchmark-placeholder.",
    "clicks_video_help": "Geschat aantal productpagina-clicks per creator-video over de content-tail. Huidige waarde is een publieke benchmark-placeholder.",
    "click_order_help": "Geschatte conversie van productclick naar order. Huidige waarde is een publieke benchmark-placeholder.",
    "shoptab_share_help": "Aandeel organische GMV dat na content-invloed via Store/Search/Mall/ShopTab koopt. Deze GMV heeft geen creator commissie. Stem dit af met de AM op basis van vergelijkbare TikTok Shop-categorieen of merchants.",
    "organic_commission_help": "SKU-specifieke standaard affiliate commissie voor orders uit organisch creatorverkeer.",
    "paid_commission_help": "SKU-specifieke commissie voor orders uit paid traffic met creator-content. TikTok Shop Ads kan een aparte Shop Ads commission rate gebruiken; huidige default is 5%.",
    "generate": "Simulator genereren",
    "sku_mix": "SKU-mix & funnelaannames",
    "total_gmv": "Totale GMV",
    "total_cost": "Totale kosten",
    "sales_contribution": "Sales contribution",
    "contribution_margin": "Contributiemarge",
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


def short_number(value):
    value = float(value)
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs_value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"


def short_money(value):
    return f"€{short_number(value)}"


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

st.markdown(
    """
    <style>
    :root {
        --tts-red: #FE2C55;
        --tts-cyan: #25F4EE;
        --tts-ink: #111827;
        --tts-muted: #6B7280;
        --tts-line: #E5E7EB;
        --tts-panel: #FFFFFF;
        --tts-bg: #F6F7FB;
    }

    .stApp {
        background: var(--tts-bg);
    }

    [data-testid="stAppViewContainer"] > .main {
        background:
            linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(246,247,251,1) 340px),
            var(--tts-bg);
    }

    [data-testid="stSidebar"] {
        background: #F1F3F7;
        border-right: 1px solid #E1E5EC;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #1F2937;
        letter-spacing: 0;
    }

    .block-container {
        max-width: 1360px;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
    }

    h1 {
        color: var(--tts-ink);
        font-weight: 760;
        letter-spacing: 0;
        margin-bottom: 0.2rem;
    }

    h2, h3 {
        color: #1F2937;
        letter-spacing: 0;
    }

    div[data-testid="stCaptionContainer"] {
        color: var(--tts-muted);
        font-size: 1rem;
    }

    div[data-testid="stMetric"] {
        background: var(--tts-panel);
        border: 1px solid var(--tts-line);
        border-radius: 8px;
        padding: 12px 14px;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.045);
        min-height: 104px;
        height: auto !important;
        max-height: none !important;
        overflow: visible !important;
    }

    div[data-testid="stMetric"] * {
        max-height: none !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }

    div[data-testid="stMetricLabel"] {
        color: var(--tts-muted);
        font-weight: 650;
        white-space: normal;
        line-height: 1.25;
        overflow-wrap: anywhere;
        word-break: break-word;
    }

    div[data-testid="stMetricValue"] {
        color: var(--tts-ink);
        font-weight: 760;
        font-size: clamp(1.12rem, 1.85vw, 1.75rem);
        white-space: normal !important;
        overflow-wrap: anywhere;
        word-break: break-word;
        line-height: 1.18;
    }

    div[data-testid="stMetricValue"] > div {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }

    .readonly-rate {
        background: transparent;
        border: 0;
        border-radius: 0;
        padding: 0.35rem 0 0 0;
        min-height: 0;
    }

    .readonly-rate-label {
        color: #6B7280;
        font-size: 0.86rem;
        font-weight: 650;
        margin-bottom: 3px;
    }

    .readonly-rate-value {
        color: #111827;
        font-size: 1rem;
        font-weight: 500;
        line-height: 1.2;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #DDE3EA;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.92);
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.055);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 0;
        background: #EEF2F7;
        padding: 6px;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        padding: 0 18px;
        color: #4B5563;
        font-weight: 650;
        border-radius: 7px;
        background: transparent;
        border: 1px solid transparent;
    }

    .stTabs [aria-selected="true"] {
        color: #111827;
        background: #FFFFFF;
        border-color: #CBD5E1;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
    }

    .st-key-selected_phase_view div[role="radiogroup"],
    div[class*="st-key-phase_chart_mode_"] div[role="radiogroup"] {
        gap: 8px;
    }

    .st-key-selected_phase_view div[role="radiogroup"] label,
    div[class*="st-key-phase_chart_mode_"] div[role="radiogroup"] label {
        background: #EEF2F7;
        border: 1px solid #DDE3EA;
        border-radius: 8px;
        padding: 7px 14px;
        min-height: 38px;
    }

    .st-key-selected_phase_view div[role="radiogroup"] label:has(input:checked),
    div[class*="st-key-phase_chart_mode_"] div[role="radiogroup"] label:has(input:checked) {
        background: #FFFFFF;
        border-color: #CBD5E1;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
    }

    .stButton > button {
        border-radius: 8px;
        border: 0;
        background: var(--tts-red);
        color: white;
        font-weight: 720;
        min-height: 44px;
        box-shadow: 0 12px 24px rgba(254, 44, 85, 0.18);
    }

    .stButton > button:hover {
        background: #E9274E;
        color: white;
        border: 0;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--tts-line);
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.04);
    }

    div[data-testid="stExpander"] {
        border: 1px solid #DDE3EA;
        border-radius: 8px;
        background: #FFFFFF;
    }

    div[data-testid="stAlert"] {
        border-radius: 8px;
        border: 1px solid #DDE3EA;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.04);
    }

    div[data-testid="stPlotlyChart"] {
        background: #FFFFFF;
        border: 1px solid var(--tts-line);
        border-radius: 8px;
        padding: 24px 22px 20px 22px;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.04);
        min-height: 560px;
        display: flex;
        align-items: stretch;
        overflow: visible !important;
    }

    div[data-testid="stPlotlyChart"] > div {
        width: 100% !important;
        min-height: 520px;
        overflow: visible !important;
    }

    div[data-testid="stPlotlyChart"] svg {
        overflow: visible !important;
    }

    .dashboard-note {
        background: #FFFFFF;
        border: 1px solid #DDE3EA;
        border-left: 4px solid var(--tts-red);
        border-radius: 8px;
        padding: 14px 16px;
        color: #1F2937;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.04);
        line-height: 1.55;
    }

    .chart-lens {
        background: #FFFFFF;
        border: 1px solid #DDE3EA;
        border-radius: 8px;
        padding: 16px 18px;
        margin: 10px 0 14px 0;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.035);
    }

    .chart-lens-title {
        color: #111827;
        font-size: 0.92rem;
        font-weight: 760;
        margin-bottom: 6px;
    }

    .chart-lens-body {
        color: #4B5563;
        font-size: 0.94rem;
        line-height: 1.55;
    }

    .hero-band {
        background:
            linear-gradient(135deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98)),
            #FFFFFF;
        border: 1px solid #DDE3EA;
        border-radius: 8px;
        padding: 22px 24px;
        margin: 18px 0 18px 0;
        box-shadow: 0 16px 36px rgba(15, 23, 42, 0.07);
        display: grid;
        grid-template-columns: minmax(0, 1.45fr) repeat(3, minmax(120px, 0.55fr));
        gap: 18px;
        align-items: center;
    }

    .hero-title {
        color: #111827;
        font-size: 1.32rem;
        font-weight: 790;
        line-height: 1.18;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        color: #4B5563;
        font-size: 0.98rem;
        line-height: 1.45;
    }

    .hero-kpi {
        border-left: 1px solid #E5E7EB;
        padding-left: 16px;
    }

    .hero-kpi-label {
        color: #6B7280;
        font-size: 0.78rem;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .hero-kpi-value {
        color: #111827;
        font-size: 1.22rem;
        font-weight: 800;
        line-height: 1.15;
        overflow-wrap: anywhere;
    }

    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        margin: 10px 0 14px 0;
    }

    .premium-kpi {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-top: 3px solid var(--accent);
        border-radius: 8px;
        padding: 13px 14px;
        min-height: 94px;
        height: auto;
        overflow: visible;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.045);
    }

    .premium-kpi-label {
        color: #6B7280;
        font-size: 0.78rem;
        font-weight: 720;
        margin-bottom: 8px;
        line-height: 1.25;
        overflow-wrap: anywhere;
        word-break: break-word;
    }

    .premium-kpi-value {
        color: #111827;
        font-size: 1.34rem;
        font-weight: 800;
        line-height: 1.1;
        overflow-wrap: anywhere;
        word-break: break-word;
    }

    .insight-strip {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-left: 3px solid #25F4EE;
        border-radius: 8px;
        color: #374151;
        padding: 12px 14px;
        margin: 10px 0 18px 0;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.035);
        line-height: 1.45;
    }

    @media (max-width: 900px) {
        .hero-band,
        .kpi-grid {
            grid-template-columns: 1fr;
        }

        .hero-kpi {
            border-left: 0;
            border-top: 1px solid #E5E7EB;
            padding-left: 0;
            padding-top: 12px;
        }
    }

    .sku-title {
        font-size: 1rem;
        font-weight: 760;
        color: #111827;
        margin-bottom: 0.2rem;
    }

    .sku-subtitle {
        color: #6B7280;
        font-size: 0.88rem;
        margin-bottom: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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
    if f"organic_commission_pct_{i}" not in st.session_state:
        st.session_state[f"organic_commission_pct_{i}"] = 10.0
    if f"paid_commission_pct_{i}" not in st.session_state:
        st.session_state[f"paid_commission_pct_{i}"] = 5.0


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
            "Organic Creator Commission Rate": float(st.session_state[f"organic_commission_pct_{i}"]) / 100,
            "Paid Creator Commission Rate": float(st.session_state[f"paid_commission_pct_{i}"]) / 100,
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
        raise ValueError("Store/Search GMV share must be between 0% and 90%.")
    if df["Organic Creator Commission Rate"].lt(0).any() or df["Organic Creator Commission Rate"].gt(0.80).any():
        raise ValueError("Organic creator commission must be between 0% and 80%.")
    if df["Paid Creator Commission Rate"].lt(0).any() or df["Paid Creator Commission Rate"].gt(0.80).any():
        raise ValueError("Paid-traffic creator commission must be between 0% and 80%.")
    return df


def build_weekly_model(
    product_df,
    phase_inputs,
    weeks_per_phase,
    promo_60d,
    logistics_cost,
    use_fbt,
    organic_click_window_weeks,
    ads_roas,
):
    aov = product_df["AOV"].to_numpy()
    gross_margin = product_df["Gross Margin"].to_numpy()
    platform_fee_rates = product_df["Platform Fee Rate"].to_numpy()
    product_cost_per_unit = aov * (1 - gross_margin)
    base_logistics_cost = float(logistics_cost)
    logistics_cost_per_unit = np.full(len(product_df), base_logistics_cost)
    if use_fbt:
        logistics_cost_per_unit = np.where(aov > FBT_FREE_SHIPPING_AOV_THRESHOLD, 0.0, base_logistics_cost)
    sample_all_in_cost_per_unit = product_cost_per_unit + logistics_cost_per_unit

    videos_per_sample = product_df["Videos / Sample"].to_numpy()
    clicks_per_video = product_df["Clicks / Video"].to_numpy()
    click_to_order_rate = product_df["Click-to-order Rate"].to_numpy()
    shop_tab_share = product_df["ShopTab GMV Share"].to_numpy()
    organic_creator_commission_rate = product_df["Organic Creator Commission Rate"].to_numpy()
    paid_creator_commission_rate = product_df["Paid Creator Commission Rate"].to_numpy()

    rows = []
    video_history = []
    cumulative_videos_p = np.zeros(len(product_df))
    global_week = 0
    organic_click_window_weeks = max(1, int(organic_click_window_weeks))

    for phase in phase_inputs:
        for week_idx in range(int(weeks_per_phase)):
            global_week += 1

            samples_p = np.full(len(product_df), float(phase["samples_per_sku"]))
            new_videos_p = samples_p * videos_per_sample
            video_history.append(new_videos_p)
            cumulative_videos_p += new_videos_p

            active_videos_p = np.zeros(len(product_df))
            for age in range(organic_click_window_weeks):
                history_idx = len(video_history) - 1 - age
                if history_idx >= 0:
                    active_videos_p += video_history[history_idx] / organic_click_window_weeks

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
                raise ValueError("Paid acceleration budget x Ads ROAS must be below 90%.")

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
            fulfillment_cost = float(np.sum(orders_p * logistics_cost_per_unit))
            organic_creator_commission = float(np.sum(affiliate_organic_gmv_p * organic_creator_commission_rate))
            paid_creator_commission = float(np.sum(affiliate_paid_gmv_p * paid_creator_commission_rate))
            creator_commission = organic_creator_commission + paid_creator_commission
            ads_cost = gmv * take_rate
            sales_contribution = gmv - cogs - platform_fee - creator_commission - fulfillment_cost
            growth_investment = samples_cost + ads_cost
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
                "Affiliate Paid GMV": float(np.sum(affiliate_paid_gmv_p)),
                "ShopTab Paid GMV": float(np.sum(shop_tab_paid_gmv_p)),
                "GMV": gmv,
                "ShopTab GMV": float(np.sum(shop_tab_gmv_p)),
                "Affiliate Video GMV": affiliate_gmv,
                "COGS": cogs,
                "Gross Profit": gmv - cogs,
                "Platform Fee": platform_fee,
                "Organic Creator Commission": organic_creator_commission,
                "Paid Creator Commission": paid_creator_commission,
                "Creator Commission": creator_commission,
                "Ads Cost": ads_cost,
                "Samples Cost": samples_cost,
                "Fulfillment Cost": fulfillment_cost,
                "Sales Contribution": sales_contribution,
                "Contribution Margin": sales_contribution / gmv if gmv > 0 else 0,
                "Growth Investment": growth_investment,
                "Total Cost": total_cost,
                "Profit": sales_contribution - growth_investment,
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
        "Affiliate Paid GMV": "sum",
        "ShopTab Paid GMV": "sum",
        "GMV": "sum",
        "ShopTab GMV": "sum",
        "Affiliate Video GMV": "sum",
        "COGS": "sum",
        "Gross Profit": "sum",
        "Platform Fee": "sum",
        "Organic Creator Commission": "sum",
        "Paid Creator Commission": "sum",
        "Creator Commission": "sum",
        "Ads Cost": "sum",
        "Samples Cost": "sum",
        "Fulfillment Cost": "sum",
        "Sales Contribution": "sum",
        "Growth Investment": "sum",
        "Total Cost": "sum",
        "Profit": "sum",
    })
    summary["Profit Margin"] = np.where(summary["GMV"] > 0, summary["Profit"] / summary["GMV"], 0)
    summary["Contribution Margin"] = np.where(summary["GMV"] > 0, summary["Sales Contribution"] / summary["GMV"], 0)
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
        "Sales Contribution": df["Sales Contribution"].sum(),
        "Sample Investment": total_sample_cost,
        "Ads Investment": total_ads_cost,
        "Growth Investment": df["Growth Investment"].sum(),
        "Profit Margin": total_profit / total_gmv if total_gmv > 0 else 0,
        "Contribution Margin": df["Sales Contribution"].sum() / total_gmv if total_gmv > 0 else 0,
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
        return f"{T['shoptab_gmv']} ({pct(shop_tab_gmv / (shop_tab_gmv + affiliate_gmv), 0)})" if shop_tab_gmv + affiliate_gmv > 0 else T["shoptab_gmv"]
    return f"{T['affiliate_video_gmv']} ({pct(affiliate_gmv / (shop_tab_gmv + affiliate_gmv), 0)})"


def phase_objective(phase_key):
    return T.get(f"{phase_key}_objective", "")


def cost_driver(row):
    cost_map = {
        T["cost_cogs"]: float(row["COGS"]),
        T["cost_platform_fee"]: float(row["Platform Fee"]),
        T["cost_creator_commission"]: float(row["Creator Commission"]),
        T["cost_fulfillment"]: float(row["Fulfillment Cost"]),
        T["cost_samples"]: float(row["Samples Cost"]),
        T["cost_ads"]: float(row["Ads Cost"]),
    }
    driver, amount = max(cost_map.items(), key=lambda item: item[1])
    total_cost = float(row["Total Cost"])
    share = amount / total_cost if total_cost > 0 else 0
    return driver, amount, share


def build_customer_summary(overall, phase_summary, weekly_be_label, cumulative_be_label, meeting_notes, assumption_status, cost_explanation_text, forecast_range):
    rows = [
        (T["brand_name"], meeting_notes.get("brand_name") or "-"),
        (T["meeting_date"], str(meeting_notes.get("meeting_date") or "-")),
        (T["am_name"], meeting_notes.get("am_name") or "-"),
        (T["assumption_status"], assumption_status),
        (T["key_recommendation"], meeting_notes.get("key_recommendation") or "-"),
        (f"{T['forecast_range']} - {T['conservative_case']}", money(forecast_range["conservative_gmv"], 0)),
        (f"{T['forecast_range']} - {T['base_case']}", money(forecast_range["base_gmv"], 0)),
        (f"{T['forecast_range']} - {T['upside_case']}", money(forecast_range["upside_gmv"], 0)),
        (T["total_gmv"], money(overall["Total GMV"], 0)),
        (T["total_profit"], money(overall["Total Profit"], 0)),
        (T["growth_investment"], money(overall["Growth Investment"], 0)),
        (T["sample_investment"], money(overall["Sample Investment"], 0)),
        (T["ads_investment"], money(overall["Ads Investment"], 0)),
        (T["gmv_per_sample"], money(overall["GMV / Sample"], 0)),
        (T["profit_per_sample"], money(overall["Profit / Sample"], 0)),
        (T["orders_per_sample"], f"{overall['Orders / Sample']:.2f}"),
        (T["weekly_profit"], weekly_be_label),
        (T["cumulative_be"], cumulative_be_label),
        (T["cost_explanation"], cost_explanation_text),
        (T["planning_disclaimer"], T["planning_disclaimer"]),
    ]
    for _, phase_row in phase_summary.iterrows():
        rows.append((f"{phase_row['Phase']} {T['total_gmv']}", money(phase_row["GMV"], 0)))
        rows.append((f"{phase_row['Phase']} {T['total_profit']}", money(phase_row["Profit"], 0)))
    return pd.DataFrame(rows, columns=["Metric", "Value"])


def render_kpi_grid(items):
    for start in range(0, len(items), 4):
        row_items = items[start:start + 4]
        cols = st.columns(len(row_items))
        for col, (label, value, accent) in zip(cols, row_items):
            with col:
                st.markdown(
                    f"""
                    <div class="premium-kpi" style="border-top-color:{escape(str(accent))};">
                        <div class="premium-kpi-label">{escape(str(label))}</div>
                        <div class="premium-kpi-value">{escape(str(value))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_hero(overall, weeks, skus, break_even_label):
    st.markdown(
        f"""
        <div class="hero-band">
            <div>
                <div class="hero-title">{T["hero_title"].format(weeks=weeks, skus=skus)}</div>
                <div class="hero-subtitle">{T["hero_subtitle"].format(
                    gmv=money(overall["Total GMV"], 0),
                    growth_investment=money(overall["Growth Investment"], 0),
                    break_even=break_even_label,
                )}</div>
            </div>
            <div class="hero-kpi">
                <div class="hero-kpi-label">{T["hero_gmv"]}</div>
                <div class="hero-kpi-value">{money(overall["Total GMV"], 0)}</div>
            </div>
            <div class="hero-kpi">
                <div class="hero-kpi-label">{T["hero_investment"]}</div>
                <div class="hero-kpi-value">{money(overall["Growth Investment"], 0)}</div>
            </div>
            <div class="hero-kpi">
                <div class="hero-kpi-label">{T["hero_break_even"]}</div>
                <div class="hero-kpi-value">{break_even_label}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def commercial_takeaways(overall, df_all, cumulative_be_label, driver):
    return [
        (T["investment_required"], money(overall["Growth Investment"], 0)),
        (T["expected_gmv"], money(overall["Total GMV"], 0)),
        (T["payback_timing"], cumulative_be_label),
        (T["main_upside_lever"], main_gmv_channel(df_all)),
        (T["main_risk"], T["main_risk_text"].format(driver=driver)),
    ]


def forecast_range(overall, assumption_status):
    if assumption_status == T["merchant_confirmed_input"]:
        spread = 0.08
    elif assumption_status == T["am_aligned_input"]:
        spread = 0.12
    else:
        spread = 0.20

    base_gmv = float(overall["Total GMV"])
    base_profit = float(overall["Total Profit"])
    return {
        "spread": spread,
        "conservative_gmv": base_gmv * (1 - spread),
        "base_gmv": base_gmv,
        "upside_gmv": base_gmv * (1 + spread),
        "conservative_profit": base_profit * (1 - spread) if base_profit >= 0 else base_profit * (1 + spread),
        "base_profit": base_profit,
        "upside_profit": base_profit * (1 + spread) if base_profit >= 0 else base_profit * (1 - spread),
    }


def cost_explanation(row):
    driver, _amount, share = cost_driver(row)
    total_cost = float(row["Total Cost"])
    sample_share = float(row["Samples Cost"]) / total_cost if total_cost > 0 else 0
    ads_share = float(row["Ads Cost"]) / total_cost if total_cost > 0 else 0
    return T["cost_explanation_text"].format(
        driver=driver,
        share=pct(share, 0),
        sample_share=pct(sample_share, 0),
        ads_share=pct(ads_share, 0),
    )


def render_insight(text):
    st.markdown(
        f'<div class="insight-strip"><strong>{T["chart_insight"]}:</strong> {text}</div>',
        unsafe_allow_html=True,
    )


def render_chart_lens(title, body):
    st.markdown(
        f"""
        <div class="chart-lens">
            <div class="chart-lens-title">{escape(str(title))}</div>
            <div class="chart-lens-body">{escape(str(body))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def overall_chart_insight(df):
    ordered = df.sort_values("Global Week")
    if ordered.empty:
        return ""
    start = ordered.iloc[0]
    end = ordered.iloc[-1]
    cumulative_profit = ordered["Profit"].cumsum().iloc[-1]
    return T["overall_chart_insight"].format(
        start_gmv=money(start["GMV"], 0),
        end_week=int(end["Global Week"]),
        end_gmv=money(end["GMV"], 0),
        cum_profit=money(cumulative_profit, 0),
    )


def phase_chart_insight(row):
    return T["phase_chart_insight"].format(
        phase=row["Phase"],
        gmv=money(row["GMV"], 0),
        profit=money(row["Profit"], 0),
        investment=money(row["Growth Investment"], 0),
    )


def client_narrative(overall, df_all, phase_summary, weeks, driver):
    return [
        T["narrative_what"].format(
            gmv=money(overall["Total GMV"], 0),
            profit=money(overall["Total Profit"], 0),
            weeks=weeks,
        ),
        T["narrative_why"].format(
            channel=main_gmv_channel(df_all),
            samples=f"{overall['Total Samples']:,.0f}",
            videos=f"{overall['Total Videos']:,.0f}",
        ),
        T["narrative_next"].format(driver=driver),
    ]


def assumption_health_checks(product_df, phase_inputs, ads_roas, overall, driver, df_all):
    checks = []
    if any(float(phase["take_rate"]) * float(ads_roas) >= 0.70 for phase in phase_inputs):
        checks.append(("warning", T["health_take_rate"]))
    if float(overall["GMV / Sample Cost"]) < 3.0 and float(overall["Sample Investment"]) > 0:
        checks.append(("warning", T["health_sample_roi"]))
    if float(overall["Total Profit"]) < 0:
        checks.append(("warning", T["health_profit_negative"].format(driver=driver)))
    if product_df["Gross Margin"].min() <= 0.25:
        checks.append(("warning", T["health_low_margin"]))
    if max(product_df["Organic Creator Commission Rate"].max(), product_df["Paid Creator Commission Rate"].max()) >= 0.25:
        checks.append(("info", T["health_high_commission"]))
    if float(ads_roas) >= 7.0:
        checks.append(("info", T["health_aggressive_roas"]))
    if product_df["ShopTab GMV Share"].max() >= 0.55:
        checks.append(("info", T["health_shoptab"]))
    if product_df["Click-to-order Rate"].max() >= 0.08:
        checks.append(("info", T["health_conversion"]))
    if df_all["Global Week"].max() > PROMO_WEEKS:
        before = df_all[df_all["Global Week"] <= PROMO_WEEKS]["Profit"].tail(2).mean()
        after = df_all[df_all["Global Week"] > PROMO_WEEKS]["Profit"].head(2).mean()
        if pd.notna(before) and pd.notna(after) and before > 0 and after < before * 0.75:
            checks.append(("warning", T["health_promo_cliff"]))
    return checks or [("ok", T["health_ok"])]


def path_to_break_even(df_all, cumulative_be, driver):
    temp = df_all.copy()
    temp["Cumulative Profit"] = temp["Profit"].cumsum()
    final_profit = float(temp["Cumulative Profit"].iloc[-1]) if not temp.empty else 0.0
    if cumulative_be:
        return T["path_be_reached"].format(week=f"{T['week']} {cumulative_be}", profit=money(final_profit, 0))
    return T["path_be_gap"].format(gap=money(abs(final_profit), 0), driver=driver)


def make_investment_split_chart(df_all):
    values = pd.Series({
        T["cost_samples"]: df_all["Samples Cost"].sum(),
        T["cost_ads"]: df_all["Ads Cost"].sum(),
        T["cost_creator_commission"]: df_all["Creator Commission"].sum(),
        T["cost_platform_fee"]: df_all["Platform Fee"].sum(),
        T["cost_fulfillment"]: df_all["Fulfillment Cost"].sum(),
        T["cost_cogs"]: df_all["COGS"].sum(),
    })
    values = values[values > 0].sort_values(ascending=False)
    total = float(values.sum())
    shares = values / total if total > 0 else values
    colors_by_label = {
        T["cost_cogs"]: "#64748B",
        T["cost_fulfillment"]: "#14B8A6",
        T["cost_creator_commission"]: "#EC4899",
        T["cost_platform_fee"]: "#06B6D4",
        T["cost_ads"]: "#F97316",
        T["cost_samples"]: "#8B5CF6",
    }
    display = values.sort_values(ascending=True)
    share_display = shares.loc[display.index]
    colors = [colors_by_label.get(label, "#94A3B8") for label in display.index]
    fig = go.Figure(
        go.Bar(
            x=display.values,
            y=display.index,
            orientation="h",
            marker=dict(color=colors),
            text=[f"{short_money(v)} · {pct(share_display.loc[idx], 0)}" for idx, v in display.items()],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>Cost: €%{x:,.0f}<extra></extra>",
        )
    )
    apply_plotly_layout(fig, T["investment_split"], height=560)
    fig.update_layout(
        showlegend=False,
        margin=dict(l=170, r=170, t=112, b=60),
    )
    max_value = float(display.max()) if len(display) else 0
    fig.update_xaxes(showticklabels=False, title="", range=[0, max_value * 1.25 if max_value > 0 else 1])
    fig.update_yaxes(title="", automargin=True)
    return fig


def meeting_recap_html(overall, narrative, health_checks, path_text, weeks, skus, generated_at, meeting_notes, assumption_status, takeaways, cost_explanation_text, forecast_range_values):
    narrative_html = "".join(f"<li>{line}</li>" for line in narrative)
    health_html = "".join(f'<li class="{level}">{text}</li>' for level, text in health_checks)
    takeaways_html = "".join(f"<li><strong>{label}:</strong> {value}</li>" for label, value in takeaways)
    range_html = "".join(
        f"<li><strong>{label}:</strong> {value}</li>"
        for label, value in [
            (T["conservative_case"], money(forecast_range_values["conservative_gmv"], 0)),
            (T["base_case"], money(forecast_range_values["base_gmv"], 0)),
            (T["upside_case"], money(forecast_range_values["upside_gmv"], 0)),
        ]
    )
    notes_html = "".join(
        f"<li><strong>{label}:</strong> {value or '-'}</li>"
        for label, value in [
            (T["brand_name"], meeting_notes.get("brand_name")),
            (T["meeting_date"], meeting_notes.get("meeting_date")),
            (T["am_name"], meeting_notes.get("am_name")),
            (T["assumption_status"], assumption_status),
            (T["key_recommendation"], meeting_notes.get("key_recommendation")),
        ]
    )
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{T["title"]}</title>
  <style>
    body {{ font-family: Arial, sans-serif; color: #111827; margin: 0; line-height: 1.5; background: #f6f7fb; }}
    .page {{ max-width: 980px; margin: 28px auto; padding: 0 24px 32px; }}
    .topline {{ color: #6b7280; font-size: 13px; font-weight: 700; margin-bottom: 10px; }}
    .meta {{ color: #6b7280; font-size: 12px; margin: 10px 0 18px; display: flex; flex-wrap: wrap; gap: 8px 16px; }}
    .meta span {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 999px; padding: 5px 10px; }}
    .hero {{ background: #fff; border: 1px solid #e5e7eb; border-left: 5px solid #FE2C55; border-radius: 8px; padding: 22px 24px; box-shadow: 0 14px 30px rgba(15,23,42,.07); }}
    .hero h1 {{ margin: 0 0 8px; font-size: 28px; }}
    .hero p {{ margin: 0; color: #4b5563; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 18px 0; }}
    .card {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 14px; box-shadow: 0 8px 18px rgba(15,23,42,.04); }}
    .label {{ color: #6b7280; font-size: 12px; font-weight: 700; }}
    .value {{ font-size: 22px; font-weight: 800; margin-top: 6px; }}
    .section {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 18px 20px; margin-top: 14px; }}
    h2 {{ margin: 0 0 10px; font-size: 18px; }}
    li {{ margin-bottom: 8px; }}
    li.ok {{ color: #166534; }}
    li.info {{ color: #1d4ed8; }}
    li.warning {{ color: #92400e; }}
  </style>
</head>
<body>
  <div class="page">
    <div class="topline">TikTok Shop Growth Visualizer</div>
    <div class="meta">
      <span>{T["generated_on"]}: {generated_at}</span>
      <span>{T["plan_length"]}: {weeks} {T["week"]}</span>
      <span>{T["sku_count_meta"]}: {skus}</span>
    </div>
    <div class="hero">
      <h1>{T["hero_title"].format(weeks=weeks, skus=skus)}</h1>
      <p>{T["hero_subtitle"].format(gmv=money(overall["Total GMV"], 0), growth_investment=money(overall["Growth Investment"], 0), break_even=path_text)}</p>
    </div>
    <div class="grid">
      <div class="card"><div class="label">{T["total_gmv"]}</div><div class="value">{money(overall["Total GMV"], 0)}</div></div>
      <div class="card"><div class="label">{T["total_profit"]}</div><div class="value">{money(overall["Total Profit"], 0)}</div></div>
      <div class="card"><div class="label">{T["growth_investment"]}</div><div class="value">{money(overall["Growth Investment"], 0)}</div></div>
    </div>
    <div class="section">
      <h2>{T["meeting_notes"]}</h2>
      <ul>{notes_html}</ul>
    </div>
    <div class="section">
      <h2>{T["commercial_takeaways"]}</h2>
      <ul>{takeaways_html}</ul>
    </div>
    <div class="section">
      <h2>{T["forecast_range"]}</h2>
      <ul>{range_html}</ul>
      <p>{T["forecast_range_note"]}</p>
    </div>
    <div class="section">
      <h2>{T["client_narrative"]}</h2>
      <ol>{narrative_html}</ol>
    </div>
    <div class="section">
      <h2>{T["health_check"]}</h2>
      <ul>{health_html}</ul>
    </div>
    <div class="section">
      <h2>{T["path_to_be"]}</h2>
      <p>{path_text}</p>
    </div>
    <div class="section">
      <h2>{T["cost_explanation"]}</h2>
      <p>{cost_explanation_text}</p>
    </div>
    <div class="section">
      <p>{T["planning_disclaimer"]}</p>
    </div>
  </div>
</body>
</html>"""


def wrap_pdf_text(text, max_width, font_name, font_size):
    words = []
    current = ""
    for char in str(text):
        trial = current + char
        from reportlab.pdfbase import pdfmetrics
        if pdfmetrics.stringWidth(trial, font_name, font_size) <= max_width:
            current = trial
        else:
            if current:
                words.append(current)
            current = char
    if current:
        words.append(current)
    return words


def meeting_summary_pdf(overall, narrative, health_checks, path_text, weeks, skus, generated_at, meeting_notes, assumption_status, takeaways, cost_explanation_text, forecast_range_values):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 42
    font_name = "STSong-Light"
    pdfmetrics.registerFont(UnicodeCIDFont(font_name))

    def clean(value):
        return str(value).replace("€", "EUR ")

    def new_page_if_needed(y, needed=56):
        if y < margin + needed:
            pdf.showPage()
            pdf.setFont(font_name, 10)
            return height - margin
        return y

    def draw_wrapped(text, x, y, max_width, font_size=10, leading=14):
        pdf.setFont(font_name, font_size)
        for line in wrap_pdf_text(clean(text), max_width, font_name, font_size):
            y = new_page_if_needed(y, leading + 4)
            pdf.drawString(x, y, line)
            y -= leading
        return y

    y = height - margin
    pdf.setFillColor(colors.HexColor("#6B7280"))
    pdf.setFont(font_name, 9)
    pdf.drawString(margin, y, "TikTok Shop Growth Visualizer")
    y -= 20

    pdf.setFillColor(colors.HexColor("#111827"))
    pdf.setFont(font_name, 20)
    pdf.drawString(margin, y, clean(T["hero_title"].format(weeks=weeks, skus=skus)))
    y -= 24

    pdf.setFillColor(colors.HexColor("#6B7280"))
    pdf.setFont(font_name, 9)
    meta_line = (
        f"{T['generated_on']}: {generated_at}  |  "
        f"{T['plan_length']}: {weeks} {T['week']}  |  "
        f"{T['sku_count_meta']}: {skus}"
    )
    pdf.drawString(margin, y, clean(meta_line))
    y -= 18

    pdf.setFillColor(colors.HexColor("#111827"))
    y = draw_wrapped(
        T["hero_subtitle"].format(
            gmv=money(overall["Total GMV"], 0),
            growth_investment=money(overall["Growth Investment"], 0),
            break_even=path_text,
        ),
        margin,
        y,
        width - margin * 2,
        font_size=10,
        leading=14,
    )
    y -= 10

    card_w = (width - margin * 2 - 20) / 3
    cards = [
        (T["total_gmv"], money(overall["Total GMV"], 0)),
        (T["total_profit"], money(overall["Total Profit"], 0)),
        (T["growth_investment"], money(overall["Growth Investment"], 0)),
    ]
    for idx, (label, value) in enumerate(cards):
        x = margin + idx * (card_w + 10)
        pdf.setStrokeColor(colors.HexColor("#E5E7EB"))
        pdf.setFillColor(colors.white)
        pdf.roundRect(x, y - 58, card_w, 52, 6, stroke=1, fill=1)
        pdf.setFillColor(colors.HexColor("#6B7280"))
        pdf.setFont(font_name, 8)
        pdf.drawString(x + 10, y - 24, clean(label))
        pdf.setFillColor(colors.HexColor("#111827"))
        pdf.setFont(font_name, 14)
        pdf.drawString(x + 10, y - 43, clean(value))
    y -= 82

    sections = [
        (T["meeting_notes"], [
            f"{T['brand_name']}: {meeting_notes.get('brand_name') or '-'}",
            f"{T['meeting_date']}: {meeting_notes.get('meeting_date') or '-'}",
            f"{T['am_name']}: {meeting_notes.get('am_name') or '-'}",
            f"{T['assumption_status']}: {assumption_status}",
            f"{T['key_recommendation']}: {meeting_notes.get('key_recommendation') or '-'}",
        ]),
        (T["commercial_takeaways"], [f"{label}: {value}" for label, value in takeaways]),
        (T["forecast_range"], [
            f"{T['conservative_case']}: {money(forecast_range_values['conservative_gmv'], 0)}",
            f"{T['base_case']}: {money(forecast_range_values['base_gmv'], 0)}",
            f"{T['upside_case']}: {money(forecast_range_values['upside_gmv'], 0)}",
            T["forecast_range_note"],
        ]),
        (T["client_narrative"], [clean(item) for item in narrative]),
        (T["health_check"], [clean(text) for _level, text in health_checks]),
        (T["path_to_be"], [clean(path_text)]),
        (T["cost_explanation"], [clean(cost_explanation_text)]),
        (T["planning_disclaimer"], [clean(T["planning_disclaimer"])]),
    ]
    for title, lines in sections:
        y = new_page_if_needed(y, 90)
        pdf.setFillColor(colors.HexColor("#111827"))
        pdf.setFont(font_name, 14)
        pdf.drawString(margin, y, clean(title))
        y -= 18
        for idx, line in enumerate(lines, start=1):
            prefix = f"{idx}. " if title == T["client_narrative"] else "- "
            y = draw_wrapped(prefix + line, margin, y, width - margin * 2, font_size=10, leading=14)
        y -= 10

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def reset_defaults():
    prefixes = (
        "sku_name_", "category_", "subcategory_", "aov_", "gross_margin_pct_",
        "organic_commission_pct_", "paid_commission_pct_", "videos_per_sample_",
        "clicks_per_video_", "click_to_order_pct_", "shop_tab_share_pct_",
        "take_rate_", "samples_per_sku_", "phase_chart_mode_", "_model_",
    )
    exact_keys = {
        "has_generated", "selected_phase_view", "logistics_cost_manual",
        "meeting_mode_input", "n_skus_input", "promo_60d_input", "use_fbt_input",
        "weeks_per_phase_input", "ads_roas_input", "organic_window_input",
        "reset_confirm_pending", "brand_name_input", "meeting_date_input",
        "am_name_input", "key_recommendation_input", "assumption_status_input",
        "_model_brand_name", "_model_meeting_date", "_model_am_name",
        "_model_key_recommendation", "_model_assumption_status",
    }
    for key in list(st.session_state.keys()):
        if key in exact_keys or any(key.startswith(prefix) for prefix in prefixes):
            del st.session_state[key]
    st.rerun()


def apply_plotly_layout(fig, title, height=420):
    fig.update_layout(
        title={"text": title, "x": 0.02, "xanchor": "left", "y": 0.94, "yanchor": "top"},
        height=height,
        margin=dict(l=32, r=32, t=104, b=54),
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
        (T["forecast_gmv"], "GMV", CHART_COLORS["gmv"]),
        (T["total_cost_label"], "Total Cost", CHART_COLORS["cost"]),
        (T["profit_label"], "Profit", CHART_COLORS["profit"]),
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
    fig.update_xaxes(title=T["week"])
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
            name=T["cumulative_profit_trend"],
            line=dict(color=CHART_COLORS["cumulative"], width=3),
            marker=dict(size=7),
            hovertemplate=f"{T['cumulative_profit_trend']}: €%{{y:,.0f}}<extra></extra>",
        )
    )
    fig.add_hline(y=0, line_color="#6B7280", line_width=1)
    if break_even_week is not None:
        fig.add_vline(x=break_even_week, line_dash="dash", line_color="#6B7280")
    apply_plotly_layout(fig, T["cumulative_profit_trend"])
    fig.update_yaxes(tickprefix="€", tickformat=",.0f")
    fig.update_xaxes(title=T["week"])
    return fig


def make_funnel_chart(df):
    labels = [T["samples_label"], T["videos_label"], T["clicks_label"], T["orders_label"]]
    values = [
        float(df["Samples Sent"].sum()),
        float(df["New Videos"].sum()),
        float(df["Product Clicks"].sum()),
        float(df["Orders"].sum()),
    ]
    fig = go.Figure()
    positions = [
        (0.00, 0.48, 0.55, 1.00),
        (0.52, 1.00, 0.55, 1.00),
        (0.00, 0.48, 0.00, 0.45),
        (0.52, 1.00, 0.00, 0.45),
    ]
    colors = ["#8B5CF6", "#06B6D4", "#2563EB", "#10B981"]
    for idx, (label, value, color) in enumerate(zip(labels, values, colors)):
        x0, x1, y0, y1 = positions[idx]
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=value,
                number={"valueformat": ",.0f", "font": {"size": 34, "color": "#111827"}},
                title={"text": f"<span style='color:#64748B;font-size:15px'>{label}</span>", "font": {"size": 15}},
                domain={"x": [x0, x1], "y": [y0, y1]},
            )
        )
        fig.add_shape(
            type="rect",
            xref="paper",
            yref="paper",
            x0=x0,
            x1=x1,
            y0=y0,
            y1=y1,
            line=dict(color="#E5E7EB", width=1),
            fillcolor="#FFFFFF",
            layer="below",
        )
        fig.add_shape(
            type="rect",
            xref="paper",
            yref="paper",
            x0=x0,
            x1=x0 + 0.012,
            y0=y0,
            y1=y1,
            line=dict(width=0),
            fillcolor=color,
            layer="above",
        )
    apply_plotly_layout(fig, T["funnel_summary"], height=560)
    fig.update_layout(showlegend=False, margin=dict(l=42, r=42, t=112, b=44))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def make_channel_mix_chart(phase_summary):
    temp = phase_summary.copy()
    temp["Total Channel GMV"] = temp["ShopTab GMV"] + temp["Affiliate Video GMV"]
    temp["Store/Search Share"] = np.where(temp["Total Channel GMV"] > 0, temp["ShopTab GMV"] / temp["Total Channel GMV"], 0)
    temp["Affiliate Share"] = np.where(temp["Total Channel GMV"] > 0, temp["Affiliate Video GMV"] / temp["Total Channel GMV"], 0)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=temp["Phase"],
        y=temp["Store/Search Share"],
        name=T["shoptab_gmv"],
        marker_color="#2563EB",
        text=[pct(v, 0) for v in temp["Store/Search Share"]],
        textposition="inside",
        customdata=temp["ShopTab GMV"],
        hovertemplate=f"{T['shoptab_gmv']}: €%{{customdata:,.0f}}<br>Share: %{{y:.0%}}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=temp["Phase"],
        y=temp["Affiliate Share"],
        name=T["affiliate_video_gmv"],
        marker_color="#F97316",
        text=[pct(v, 0) for v in temp["Affiliate Share"]],
        textposition="inside",
        customdata=temp["Affiliate Video GMV"],
        hovertemplate=f"{T['affiliate_video_gmv']}: €%{{customdata:,.0f}}<br>Share: %{{y:.0%}}<extra></extra>",
    ))
    apply_plotly_layout(fig, T["channel_mix"], height=560)
    fig.update_layout(barmode="stack", margin=dict(l=70, r=48, t=112, b=86), bargap=0.42)
    fig.update_yaxes(tickformat=".0%", range=[0, 1], title="")
    fig.update_xaxes(title="", automargin=True)
    return fig


def make_phase_total_chart(phase_row):
    labels = [
        T["forecast_gmv"],
        T["cost_cogs"],
        T["cost_platform_fee"],
        T["cost_creator_commission"],
        T["cost_fulfillment"],
        T["cost_samples"],
        T["cost_ads"],
        T["net_profit"],
    ]
    values = [
        float(phase_row["GMV"]),
        -float(phase_row["COGS"]),
        -float(phase_row["Platform Fee"]),
        -float(phase_row["Creator Commission"]),
        -float(phase_row["Fulfillment Cost"]),
        -float(phase_row["Samples Cost"]),
        -float(phase_row["Ads Cost"]),
        float(phase_row["Profit"]),
    ]
    colors = [
        "#2563EB",
        "#64748B",
        "#06B6D4",
        "#EC4899",
        "#14B8A6",
        "#8B5CF6",
        "#F97316",
        "#16A34A" if float(phase_row["Profit"]) >= 0 else "#DC2626",
    ]
    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker=dict(color=colors, line=dict(color="rgba(255,255,255,0.9)", width=1)),
            text=[short_money(abs(v)) if v < 0 else short_money(v) for v in values],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{x}</b><br>€%{y:,.0f}<extra></extra>",
        )
    )

    max_pos = max([0] + [v for v in values if v >= 0])
    min_neg = min([0] + [v for v in values if v < 0])
    y_min = min_neg * 1.30 if min_neg < 0 else -max_pos * 0.08
    y_max = max_pos * 1.22 if max_pos > 0 else abs(min_neg) * 0.12
    apply_plotly_layout(fig, f"{phase_row['Phase']} - {T['phase_total_breakdown']}", height=560)
    fig.update_layout(
        showlegend=False,
        margin=dict(l=72, r=56, t=90, b=126),
        bargap=0.32,
    )
    fig.add_hline(y=0, line_color="#111827", line_width=1.2)
    fig.update_yaxes(tickprefix="€", tickformat=",.0f", range=[y_min, y_max])
    fig.update_xaxes(title="", tickangle=-16, automargin=True)
    return fig


def make_phase_cumulative_chart(phase_df, title):
    temp = phase_df.sort_values("Week in Phase").copy()
    temp["Cumulative GMV"] = temp["GMV"].cumsum()
    temp["Cumulative Total Cost"] = temp["Total Cost"].cumsum()
    temp["Cumulative Profit"] = temp["Profit"].cumsum()
    temp["Cumulative Sales Contribution"] = temp["Sales Contribution"].cumsum()
    temp["Cumulative Sample Investment"] = temp["Samples Cost"].cumsum()
    temp["Cumulative Ads Investment"] = temp["Ads Cost"].cumsum()
    temp["Cumulative Growth Investment"] = temp["Growth Investment"].cumsum()

    fig = go.Figure()
    series = [
        (T["total_gmv"], "Cumulative GMV", CHART_COLORS["gmv"], "solid", 4, 9),
        (T["total_cost_label"], "Cumulative Total Cost", CHART_COLORS["cost"], "solid", 4, 9),
        (T["sales_contribution"], "Cumulative Sales Contribution", "#10B981", "solid", 4, 9),
        (T["profit_label"], "Cumulative Profit", CHART_COLORS["profit"], "solid", 4, 9),
        (T["growth_investment"], "Cumulative Growth Investment", "#8B5CF6", "dash", 3, 8),
    ]
    if float(temp["Cumulative Ads Investment"].abs().sum()) > 0:
        series.append((T["ads_investment"], "Cumulative Ads Investment", "#06B6D4", "dot", 2, 7))
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
    apply_plotly_layout(fig, f"{title} - {T['phase_chart_cumulative']}", height=520)
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
    fig.update_xaxes(title=T["week"], dtick=1, tickmode="linear")
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
    st.header(T["plan_setup"])
    n_skus = st.number_input(T["sku_count"], min_value=1, max_value=26, value=5, step=1, key="n_skus_input")
    if st.button(T["reset_defaults"], key="reset_request_btn"):
        st.session_state["reset_confirm_pending"] = True
    if st.session_state.get("reset_confirm_pending", False):
        st.warning(T["reset_pending"])
        if st.button(T["reset_confirm"], key="reset_confirm_btn"):
            reset_defaults()

    meeting_mode = st.checkbox(
        T["meeting_mode"],
        value=False,
        help=T["meeting_mode_help"],
        key="meeting_mode_input",
    )

    sidebar_meeting_compact = meeting_mode and st.session_state.get("has_generated", False)
    if sidebar_meeting_compact:
        st.info(T["meeting_mode_sidebar_note"])
        promo_60d = bool(st.session_state.get("_model_promo_60d", st.session_state.get("promo_60d_input", True)))
        use_fbt = bool(st.session_state.get("_model_use_fbt", st.session_state.get("use_fbt_input", False)))
        weeks_per_phase = int(st.session_state.get("_model_weeks_per_phase", st.session_state.get("weeks_per_phase_input", 4)))
        logistics_cost = float(st.session_state.get("_model_logistics_cost", st.session_state.get("logistics_cost_manual", 5.0)))
        ads_roas = float(st.session_state.get("_model_ads_roas", st.session_state.get("ads_roas_input", 6.0)))
        organic_click_window_weeks = int(st.session_state.get("_model_organic_click_window_weeks", st.session_state.get("organic_window_input", 4)))
        phase_inputs = []
        for idx, phase in enumerate(PHASES):
            take_rate_pct = float(st.session_state.get(f"_model_take_rate_pct_{idx}", st.session_state.get(f"take_rate_{idx}", phase["take_rate"] * 100)))
            samples_per_sku = int(st.session_state.get(f"_model_samples_per_sku_{idx}", st.session_state.get(f"samples_per_sku_{idx}", phase["samples_per_sku"])))
            phase_inputs.append({**phase, "take_rate": take_rate_pct / 100, "samples_per_sku": samples_per_sku})
    else:
        promo_60d = st.checkbox(
            T["promo"],
            value=True,
            help=T["promo_yes"],
            key="promo_60d_input",
        )
        use_fbt = st.checkbox(
            T["fbt"],
            value=False,
            help=T["fbt_help"],
            key="use_fbt_input",
        )
        weeks_per_phase = st.slider(T["weeks_phase"], min_value=2, max_value=8, value=4, step=1, key="weeks_per_phase_input")

        st.header(T["cost_assumptions"])
        logistics_cost = st.number_input(
            T["fulfillment"],
            min_value=0.0,
            value=5.0,
            step=0.5,
            key="logistics_cost_manual",
        )

        st.header(T["growth_levers"])
        ads_roas = st.number_input(T["ads_roas"], min_value=0.1, max_value=8.0, value=6.0, step=0.1, key="ads_roas_input")
        organic_click_window_weeks = st.number_input(T["organic_click_window"], min_value=1, max_value=8, value=4, step=1, key="organic_window_input")
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

        st.session_state["_model_promo_60d"] = bool(promo_60d)
        st.session_state["_model_use_fbt"] = bool(use_fbt)
        st.session_state["_model_weeks_per_phase"] = int(weeks_per_phase)
        st.session_state["_model_logistics_cost"] = float(logistics_cost)
        st.session_state["_model_ads_roas"] = float(ads_roas)
        st.session_state["_model_organic_click_window_weeks"] = int(organic_click_window_weeks)
        for idx, phase in enumerate(phase_inputs):
            st.session_state[f"_model_take_rate_pct_{idx}"] = float(phase["take_rate"] * 100)
            st.session_state[f"_model_samples_per_sku_{idx}"] = int(phase["samples_per_sku"])

show_setup = (not meeting_mode) or (not st.session_state.get("has_generated", False))

if show_setup:
    st.subheader(T["sku_setup"])
    st.caption(T["sku_caption"])
    with st.expander(T["benchmark_info"], expanded=False):
        st.write(T["benchmark_info_text"])
    with st.expander(T["model_assumptions"], expanded=False):
        st.write(T["model_assumptions_text"])
        st.caption(T["planning_disclaimer"])

    with st.expander(T["meeting_notes"], expanded=False):
        n1, n2, n3 = st.columns(3)
        with n1:
            brand_name = st.text_input(T["brand_name"], key="brand_name_input")
        with n2:
            meeting_date = st.date_input(T["meeting_date"], value=datetime.now().date(), key="meeting_date_input")
        with n3:
            am_name = st.text_input(T["am_name"], key="am_name_input")
        assumption_status = st.selectbox(
            T["assumption_status"],
            options=[T["benchmark_input"], T["am_aligned_input"], T["merchant_confirmed_input"]],
            index=0,
            key="assumption_status_input",
        )
        key_recommendation = st.text_area(
            T["key_recommendation"],
            value=T["key_recommendation_default"],
            key="key_recommendation_input",
        )
    meeting_notes = {
        "brand_name": brand_name,
        "meeting_date": str(meeting_date),
        "am_name": am_name,
        "key_recommendation": key_recommendation,
    }
    st.session_state["_model_brand_name"] = brand_name
    st.session_state["_model_meeting_date"] = str(meeting_date)
    st.session_state["_model_am_name"] = am_name
    st.session_state["_model_key_recommendation"] = key_recommendation
    st.session_state["_model_assumption_status"] = assumption_status

    for i in range(int(n_skus)):
        initialize_sku(i)
        with st.container(border=True):
            category = st.session_state[f"category_{i}"]
            subcategory = st.session_state[f"subcategory_{i}"]
            st.markdown(
                f"""
                <div class="sku-title">SKU {i + 1} · {st.session_state[f"sku_name_{i}"]}</div>
                <div class="sku-subtitle">{category} / {subcategory} · {pct(PLATFORM_COMMISSION[category], 0)} {T["platform_commission"]}</div>
                """,
                unsafe_allow_html=True,
            )
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
                st.markdown(
                    f"""
                    <div class="readonly-rate">
                        <div class="readonly-rate-label">{T["platform_commission"]}</div>
                        <div class="readonly-rate-value">{pct(PLATFORM_COMMISSION[category], 0)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            c7, c8 = st.columns(2)
            with c7:
                st.number_input(
                    T["organic_commission_sku"],
                    min_value=0.0,
                    max_value=80.0,
                    step=0.5,
                    key=f"organic_commission_pct_{i}",
                    help=T["organic_commission_help"],
                )
            with c8:
                st.number_input(
                    T["paid_commission_sku"],
                    min_value=0.0,
                    max_value=80.0,
                    step=0.5,
                    key=f"paid_commission_pct_{i}",
                    help=T["paid_commission_help"],
                )

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
else:
    meeting_notes = {
        "brand_name": st.session_state.get("_model_brand_name", st.session_state.get("brand_name_input", "")),
        "meeting_date": st.session_state.get("_model_meeting_date", st.session_state.get("meeting_date_input", "")),
        "am_name": st.session_state.get("_model_am_name", st.session_state.get("am_name_input", "")),
        "key_recommendation": st.session_state.get("_model_key_recommendation", st.session_state.get("key_recommendation_input", T["key_recommendation_default"])),
    }
    assumption_status = st.session_state.get("_model_assumption_status", st.session_state.get("assumption_status_input", T["benchmark_input"]))
    for i in range(int(n_skus)):
        initialize_sku(i)

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
            use_fbt=bool(use_fbt),
            organic_click_window_weeks=int(organic_click_window_weeks),
            ads_roas=float(ads_roas),
        )
        phase_summary = build_phase_summary(df_all)
        overall_summary = build_overall_summary(df_all)
        weekly_be = first_positive_profit_week(df_all)
        cumulative_be = first_cumulative_break_even_week(df_all)

        overall = overall_summary.iloc[0]
        weekly_be_label = f"Week {weekly_be}" if weekly_be else T["not_reached"]
        cumulative_be_label = f"Week {cumulative_be}" if cumulative_be else T["not_reached"]
        total_cost_row = df_all.sum(numeric_only=True)
        total_cost_driver, _, _ = cost_driver(total_cost_row)
        narrative = client_narrative(
            overall=overall,
            df_all=df_all,
            phase_summary=phase_summary,
            weeks=int(weeks_per_phase) * len(PHASES),
            driver=total_cost_driver,
        )
        health_checks = assumption_health_checks(
            product_df=product_df,
            phase_inputs=phase_inputs,
            ads_roas=float(ads_roas),
            overall=overall,
            driver=total_cost_driver,
            df_all=df_all,
        )
        path_text = path_to_break_even(df_all, cumulative_be, total_cost_driver)
        total_cost_explanation = cost_explanation(total_cost_row)
        takeaways = commercial_takeaways(overall, df_all, cumulative_be_label, total_cost_driver)
        forecast_range_values = forecast_range(overall, assumption_status)

        render_hero(
            overall=overall,
            weeks=int(weeks_per_phase) * len(PHASES),
            skus=int(n_skus),
            break_even_label=cumulative_be_label,
        )

        st.subheader(T["executive_dashboard"])
        render_kpi_grid([
            (T["total_gmv"], money(overall["Total GMV"], 0), "#2563EB"),
            (T["total_profit"], money(overall["Total Profit"], 0), "#16A34A" if overall["Total Profit"] >= 0 else "#DC2626"),
            (T["growth_investment"], money(overall["Growth Investment"], 0), "#7C3AED"),
            (T["sample_gmv_roi"], f"{overall['GMV / Sample Cost']:.1f}x", "#0EA5E9"),
            (T["weekly_profit"], weekly_be_label, "#64748B"),
            (T["cumulative_be"], cumulative_be_label, "#64748B"),
            (T["orders"], f"{overall['Total Orders']:,.0f}", "#14B8A6"),
            (T["channel_mix"], main_gmv_channel(df_all), "#F97316"),
        ])
        st.markdown(
            f"""
            <div class="dashboard-note">
                {T["executive_summary_text"].format(
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
                )}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(T["planning_disclaimer"])
        st.info(f"**{T['assumption_status']}**: {assumption_status}")

        st.subheader(T["commercial_takeaways"])
        render_kpi_grid([
            (takeaways[0][0], takeaways[0][1], "#7C3AED"),
            (takeaways[1][0], takeaways[1][1], "#2563EB"),
            (takeaways[2][0], takeaways[2][1], "#14B8A6"),
            (takeaways[3][0], takeaways[3][1], "#F97316"),
        ])
        st.warning(f"**{takeaways[4][0]}**: {takeaways[4][1]}")

        with st.expander(T["forecast_range_prompt"], expanded=False):
            st.caption(T["forecast_range_note"])
            render_kpi_grid([
                (T["conservative_case"], money(forecast_range_values["conservative_gmv"], 0), "#64748B"),
                (T["base_case"], money(forecast_range_values["base_gmv"], 0), "#2563EB"),
                (T["upside_case"], money(forecast_range_values["upside_gmv"], 0), "#16A34A"),
            ])

        st.subheader(T["client_narrative"])
        for line in narrative:
            st.write(f"- {line}")

        st.subheader(T["health_check"])
        for level, check in health_checks:
            if level == "ok":
                st.success(check)
            elif level == "info":
                st.info(check)
            else:
                st.warning(check)

        st.subheader(T["path_to_be"])
        if cumulative_be:
            st.success(path_text)
        else:
            st.warning(path_text)

        st.subheader(T["sample_roi_title"])
        r1, r2, r3, r4 = st.columns(4)
        r1.metric(T["gmv_per_sample"], money(overall["GMV / Sample"], 0))
        r2.metric(T["profit_per_sample"], money(overall["Profit / Sample"], 0))
        r3.metric(T["videos_per_sample_kpi"], f"{overall['Videos / Sample']:.2f}")
        r4.metric(T["orders_per_sample"], f"{overall['Orders / Sample']:.2f}")
        r5, r6 = st.columns(2)
        r5.metric(T["sample_gmv_roi"], f"{overall['GMV / Sample Cost']:.1f}x")
        r6.metric(T["ads_investment"], money(overall["Ads Investment"], 0))
        st.info(
            T["sample_roi_text"].format(
                gmv_per_sample=money(overall["GMV / Sample"], 0),
                orders_per_sample=f"{overall['Orders / Sample']:.2f}",
            )
        )

        if not meeting_mode:
            with st.expander(T["product_profile"], expanded=False):
                product_display = product_df.copy()
                product_display["AOV"] = product_display["AOV"].map(lambda x: money(x, 2))
                product_display["Gross Margin"] = product_display["Gross Margin"].map(lambda x: pct(x, 0))
                product_display["Platform Fee Rate"] = product_display["Platform Fee Rate"].map(lambda x: pct(x, 0))
                product_display["Click-to-order Rate"] = product_display["Click-to-order Rate"].map(lambda x: pct(x, 1))
                product_display["ShopTab GMV Share"] = product_display["ShopTab GMV Share"].map(lambda x: pct(x, 0))
                product_display["Organic Creator Commission Rate"] = product_display["Organic Creator Commission Rate"].map(lambda x: pct(x, 1))
                product_display["Paid Creator Commission Rate"] = product_display["Paid Creator Commission Rate"].map(lambda x: pct(x, 1))
                product_display = product_display.rename(columns={
                    "ShopTab GMV Share": T["shoptab_share"],
                    "Organic Creator Commission Rate": T["organic_commission_sku"],
                    "Paid Creator Commission Rate": T["paid_commission_sku"],
                })
                st.dataframe(product_display, use_container_width=True)

        st.subheader(T["charts"])
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(make_weekly_chart(df_all, T["overall_weekly"], weekly_be), use_container_width=True)
        with c2:
            st.plotly_chart(make_cumulative_profit_chart(df_all, cumulative_be), use_container_width=True)
        render_insight(overall_chart_insight(df_all))
        st.subheader(T["supporting_charts"])
        support_tabs = st.tabs([T["funnel_summary"], T["channel_mix"], T["investment_split"]])
        with support_tabs[0]:
            if lang == "zh":
                render_chart_lens(
                    "商业视角",
                    f"这张图展示内容投入如何放大为生意结果：{overall['Total Samples']:,.0f} 个样品预计沉淀 "
                    f"{overall['Total Videos']:,.0f} 条达人视频，带来 {overall['Total Clicks']:,.0f} 次商品点击和 "
                    f"{overall['Total Orders']:,.0f} 个订单。",
                )
            else:
                render_chart_lens(
                    "Business lens",
                    f"This view shows how content seeding scales into commercial demand: {overall['Total Samples']:,.0f} samples "
                    f"are expected to create {overall['Total Videos']:,.0f} creator videos, {overall['Total Clicks']:,.0f} product clicks, "
                    f"and {overall['Total Orders']:,.0f} orders.",
                )
            st.plotly_chart(make_funnel_chart(df_all), use_container_width=True)
        with support_tabs[1]:
            if lang == "zh":
                render_chart_lens(
                    "商业视角",
                    "这张图看的是 GMV 归因结构：达人视频 GMV 用来验证内容和转化效率，店铺/Search GMV 则代表内容种草后的无达人佣金成交沉淀。",
                )
            else:
                render_chart_lens(
                    "Business lens",
                    "This view separates GMV ownership: Affiliate Video GMV validates content and conversion, while Store/Search GMV captures commission-light demand created after content exposure.",
                )
            st.plotly_chart(make_channel_mix_chart(phase_summary), use_container_width=True)
        with support_tabs[2]:
            if lang == "zh":
                render_chart_lens(
                    "商业视角",
                    f"这张图解释成本压力来自哪里。当前最大成本项是 {total_cost_driver}，因此优化利润时应优先判断这个成本是否合理，而不只看样品或广告预算。",
                )
            else:
                render_chart_lens(
                    "Business lens",
                    f"This view explains where margin pressure comes from. The largest cost driver is {total_cost_driver}, so profit optimization should start there, not only with samples or ads.",
                )
            st.plotly_chart(make_investment_split_chart(df_all), use_container_width=True)
        st.info(f"**{T['cost_explanation']}**: {total_cost_explanation}")

        st.subheader(T["phase_trend"])
        selected_phase_key = st.radio(
            "",
            options=[p["key"] for p in phase_inputs],
            format_func=lambda key: phase_label(next(p for p in phase_inputs if p["key"] == key)),
            horizontal=True,
            label_visibility="collapsed",
            key="selected_phase_view",
        )
        selected_phase = next(p for p in phase_inputs if p["key"] == selected_phase_key)
        phase_df = df_all[df_all["Phase Key"] == selected_phase["key"]].copy()
        phase_row = phase_summary[phase_summary["Phase Key"] == selected_phase["key"]].iloc[0]
        objective = phase_objective(selected_phase["key"])
        if objective:
            st.info(f"**{T['phase_objective']}**: {objective}")
        render_kpi_grid([
            (T["total_gmv"], money(phase_row["GMV"], 0), "#2563EB"),
            (T["total_cost"], money(phase_row["Total Cost"], 0), "#F97316"),
            (T["sales_contribution"], money(phase_row["Sales Contribution"], 0), "#10B981"),
            (T["total_profit"], money(phase_row["Profit"], 0), "#16A34A" if phase_row["Profit"] >= 0 else "#DC2626"),
            (T["sample_investment"], money(phase_row["Samples Cost"], 0), "#8B5CF6"),
            (T["ads_investment"], money(phase_row["Ads Cost"], 0), "#06B6D4"),
        ])

        chart_mode = st.radio(
            T["phase_chart_mode"],
            options=[T["phase_chart_cumulative"], T["phase_chart_total"]],
            horizontal=True,
            key=f"phase_chart_mode_{selected_phase['key']}",
        )
        if chart_mode == T["phase_chart_cumulative"]:
            st.plotly_chart(make_phase_cumulative_chart(phase_df, phase_label(selected_phase)), use_container_width=True)
        else:
            st.plotly_chart(make_phase_total_chart(phase_row), use_container_width=True)
        render_insight(phase_chart_insight(phase_row))

        driver, amount, share = cost_driver(phase_row)
        st.info(
            f"**{T['cost_breakdown']}**: "
            + T["cost_breakdown_text"].format(driver=driver, amount=money(amount, 0), share=pct(share, 0))
        )

        money_cols = [
            "Organic Funnel GMV", "Affiliate Organic GMV", "ShopTab Organic GMV",
            "Paid GMV Lift", "GMV", "ShopTab GMV",
            "Affiliate Video GMV", "Affiliate Paid GMV", "ShopTab Paid GMV",
            "COGS", "Gross Profit", "Platform Fee", "Organic Creator Commission",
            "Paid Creator Commission", "Creator Commission", "Ads Cost", "Samples Cost", "Fulfillment Cost",
            "Sales Contribution", "Growth Investment", "Total Cost", "Profit", "GMV / Sample",
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

        st.subheader(T["export_materials"])
        customer_summary = build_customer_summary(
            overall,
            phase_summary,
            weekly_be_label,
            cumulative_be_label,
            meeting_notes,
            assumption_status,
            total_cost_explanation,
            forecast_range_values,
        )
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        meeting_html = meeting_recap_html(
            overall=overall,
            narrative=narrative,
            health_checks=health_checks,
            path_text=path_text,
            weeks=int(weeks_per_phase) * len(PHASES),
            skus=int(n_skus),
            generated_at=generated_at,
            meeting_notes=meeting_notes,
            assumption_status=assumption_status,
            takeaways=takeaways,
            cost_explanation_text=total_cost_explanation,
            forecast_range_values=forecast_range_values,
        )
        meeting_pdf = meeting_summary_pdf(
            overall=overall,
            narrative=narrative,
            health_checks=health_checks,
            path_text=path_text,
            weeks=int(weeks_per_phase) * len(PHASES),
            skus=int(n_skus),
            generated_at=generated_at,
            meeting_notes=meeting_notes,
            assumption_status=assumption_status,
            takeaways=takeaways,
            cost_explanation_text=total_cost_explanation,
            forecast_range_values=forecast_range_values,
        )
        dl_summary, dl_html, dl_pdf = st.columns(3)
        with dl_summary:
            st.download_button(
                T["download_customer_summary"],
                data=csv_bytes(customer_summary),
                file_name="meeting_summary.csv",
                mime="text/csv",
            )
        with dl_html:
            st.download_button(
                T["download_meeting_html"],
                data=meeting_html.encode("utf-8"),
                file_name="meeting_summary.html",
                mime="text/html",
            )
        with dl_pdf:
            st.download_button(
                T["download_meeting_pdf"],
                data=meeting_pdf,
                file_name="meeting_summary.pdf",
                mime="application/pdf",
            )
        if not meeting_mode:
            st.subheader(T["summary"])
            with st.expander(T["phase_summary"], expanded=False):
                phase_summary_display = format_table(
                    phase_summary.drop(columns=["Phase Key"]),
                    money_cols=money_cols,
                    pct_cols=["Profit Margin", "Contribution Margin"],
                    number_cols=number_cols,
                    decimal_cols=decimal_cols,
                ).rename(columns={
                    "ShopTab Organic GMV": f"{T['shoptab_gmv']} Organic",
                    "ShopTab Paid GMV": f"{T['shoptab_gmv']} Paid",
                    "ShopTab GMV": T["shoptab_gmv"],
                })
                st.dataframe(
                    phase_summary_display,
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

        if not meeting_mode:
            with st.expander(T["view_details"], expanded=False):
                st.markdown(f"**{T['overall_summary']}**")
                st.dataframe(
                    format_table(overall_summary, money_cols=money_cols, pct_cols=["Profit Margin", "Contribution Margin"], number_cols=number_cols, decimal_cols=decimal_cols),
                    use_container_width=True,
                )
                st.markdown(f"**{T['weekly_details']}**")
                weekly_display = format_table(df_all.drop(columns=["Phase Key"]), money_cols=money_cols, pct_cols=["Ads Take Rate", "Contribution Margin"], number_cols=number_cols, decimal_cols=decimal_cols)
                weekly_display = weekly_display.rename(columns={
                    "Ads Take Rate": T["take_rate"],
                    "ShopTab Organic GMV": f"{T['shoptab_gmv']} Organic",
                    "ShopTab Paid GMV": f"{T['shoptab_gmv']} Paid",
                    "ShopTab GMV": T["shoptab_gmv"],
                })
                st.dataframe(weekly_display, use_container_width=True)

                d1, d2 = st.columns(2)
                d1.download_button(T["download_weekly"], data=csv_bytes(df_all), file_name="weekly_details.csv", mime="text/csv")
                d2.download_button(T["download_phase"], data=csv_bytes(phase_summary), file_name="phase_summary.csv", mime="text/csv")

    except Exception as e:
        st.error(f"{T['input_error']}: {e}")
