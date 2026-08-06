import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
from datetime import datetime
from html import escape
from ui_copy import ENHANCEMENT_TEXT


st.set_page_config(page_title="TikTok Shop Growth Visualizer", page_icon="📈", layout="wide")


# Planning defaults calibrated with the DE hit-product pool check
# (Apr 2026) where the source coverage was strong enough. For fields
# not directly available in the source file, defaults still preserve
# planning assumptions and should be aligned with AM guidance.


PLATFORM_COMMISSION = {
    "Automotive & Motorcycle": 0.07,
    "Baby & Maternity": 0.09,
    "Beauty & Personal Care": 0.09,
    "Books, Magazines & Audio": 0.09,
    "Collectibles": 0.09,
    "Computers & Office Equipment": 0.07,
    "Fashion Accessories": 0.09,
    "Food & Beverages": 0.09,
    "Furniture": 0.09,
    "Health": 0.09,
    "Home Improvement": 0.09,
    "Home Supplies": 0.09,
    "Household Appliances": 0.07,
    "Jewelry Accessories & Derivatives": 0.09,
    "Kids' Fashion": 0.09,
    "Kitchenware": 0.09,
    "Luggage & Bags": 0.09,
    "Menswear & Underwear": 0.09,
    "Modest Fashion": 0.09,
    "Pet Supplies": 0.09,
    "Phones & Electronics": 0.07,
    "Shoes": 0.09,
    "Sports & Outdoor": 0.09,
    "Textiles & Soft Furnishings": 0.09,
    "Tools & Hardware": 0.09,
    "Toys & Hobbies": 0.09,
    "Womenswear & Underwear": 0.09
}


# Field meanings:
# aov: estimated Germany TikTok Shop AOV in EUR
# videos_per_sample: average videos generated per sample shipped
# clicks_per_video: estimated product clicks per creator video. The DE hit-product
#                   source does not include click data, so this is calibrated from
#                   observed orders/video while preserving a bounded planning CVR.
# click_to_order_rate: product click -> order conversion
# shop_tab_share: reference share used to seed the Store/Search natural-sales assumption
CATEGORY_PRESETS = {
    "Automotive & Motorcycle": {
        "Car Electronics": {
            "aov": 39.56,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 180,
            "gross_margin_pct": 38.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.221,
            "videos_per_sample": 1.0
        },
        "Car Exterior Accessories": {
            "aov": 27.83,
            "click_to_order_rate": 0.026,
            "clicks_per_video": 240,
            "gross_margin_pct": 38.0,
            "organic_commission_pct": 12.5,
            "paid_commission_pct": 6.2,
            "shop_tab_share": 0.271,
            "videos_per_sample": 1.25
        },
        "Car Interior Accessories": {
            "aov": 20.16,
            "click_to_order_rate": 0.026,
            "clicks_per_video": 228,
            "gross_margin_pct": 38.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.201,
            "videos_per_sample": 1.0
        },
        "Car Repair Tools": {
            "aov": 34.23,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 272,
            "gross_margin_pct": 38.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.17,
            "videos_per_sample": 1.68
        },
        "Car Washing & Maintenance": {
            "aov": 25.56,
            "click_to_order_rate": 0.026,
            "clicks_per_video": 180,
            "gross_margin_pct": 38.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.252,
            "videos_per_sample": 1.0
        }
    },
    "Baby & Maternity": {
        "Baby Care & Health": {
            "aov": 39.35,
            "click_to_order_rate": 0.05,
            "clicks_per_video": 240,
            "gross_margin_pct": 46.0,
            "organic_commission_pct": 7.6,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.284,
            "videos_per_sample": 1.0
        },
        "Baby Clothing & Shoes": {
            "aov": 34.9,
            "click_to_order_rate": 0.05,
            "clicks_per_video": 240,
            "gross_margin_pct": 46.0,
            "organic_commission_pct": 5.6,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.229,
            "videos_per_sample": 1.0
        },
        "Baby Fashion Accessories": {
            "aov": 39.4,
            "click_to_order_rate": 0.05,
            "clicks_per_video": 240,
            "gross_margin_pct": 46.0,
            "organic_commission_pct": 8.4,
            "paid_commission_pct": 4.2,
            "shop_tab_share": 0.298,
            "videos_per_sample": 1.0
        },
        "Baby Furniture": {
            "aov": 51.39,
            "click_to_order_rate": 0.046,
            "clicks_per_video": 240,
            "gross_margin_pct": 46.0,
            "organic_commission_pct": 5.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.439,
            "videos_per_sample": 1.0
        },
        "Baby Safety": {
            "aov": 38.5,
            "click_to_order_rate": 0.05,
            "clicks_per_video": 240,
            "gross_margin_pct": 46.0,
            "organic_commission_pct": 5.6,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.193,
            "videos_per_sample": 1.0
        },
        "Baby Toys": {
            "aov": 38.48,
            "click_to_order_rate": 0.05,
            "clicks_per_video": 240,
            "gross_margin_pct": 46.0,
            "organic_commission_pct": 5.6,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.339,
            "videos_per_sample": 1.13
        },
        "Baby Travel Gear": {
            "aov": 60.94,
            "click_to_order_rate": 0.046,
            "clicks_per_video": 240,
            "gross_margin_pct": 46.0,
            "organic_commission_pct": 6.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.383,
            "videos_per_sample": 1.0
        },
        "Maternity Supplies": {
            "aov": 37.28,
            "click_to_order_rate": 0.05,
            "clicks_per_video": 240,
            "gross_margin_pct": 46.0,
            "organic_commission_pct": 7.6,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.427,
            "videos_per_sample": 1.0
        },
        "Nursing & Feeding": {
            "aov": 32.93,
            "click_to_order_rate": 0.05,
            "clicks_per_video": 240,
            "gross_margin_pct": 46.0,
            "organic_commission_pct": 7.6,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.245,
            "videos_per_sample": 1.0
        }
    },
    "Beauty & Personal Care": {
        "Bath & Body Care": {
            "aov": 21.3,
            "click_to_order_rate": 0.049,
            "clicks_per_video": 260,
            "gross_margin_pct": 55.0,
            "organic_commission_pct": 12.5,
            "paid_commission_pct": 6.2,
            "shop_tab_share": 0.297,
            "videos_per_sample": 1.29
        },
        "Eye & Ear Care": {
            "aov": 24.18,
            "click_to_order_rate": 0.049,
            "clicks_per_video": 260,
            "gross_margin_pct": 55.0,
            "organic_commission_pct": 12.0,
            "paid_commission_pct": 6.0,
            "shop_tab_share": 0.233,
            "videos_per_sample": 1.76
        },
        "Fragrance": {
            "aov": 28.28,
            "click_to_order_rate": 0.045,
            "clicks_per_video": 260,
            "gross_margin_pct": 55.0,
            "organic_commission_pct": 12.0,
            "paid_commission_pct": 6.0,
            "shop_tab_share": 0.336,
            "videos_per_sample": 1.4
        },
        "Haircare & Styling": {
            "aov": 25.28,
            "click_to_order_rate": 0.049,
            "clicks_per_video": 260,
            "gross_margin_pct": 55.0,
            "organic_commission_pct": 12.0,
            "paid_commission_pct": 6.0,
            "shop_tab_share": 0.291,
            "videos_per_sample": 1.2
        },
        "Hand & Foot Care": {
            "aov": 23.82,
            "click_to_order_rate": 0.049,
            "clicks_per_video": 260,
            "gross_margin_pct": 55.0,
            "organic_commission_pct": 13.2,
            "paid_commission_pct": 6.6,
            "shop_tab_share": 0.257,
            "videos_per_sample": 1.8
        },
        "Makeup": {
            "aov": 24.33,
            "click_to_order_rate": 0.049,
            "clicks_per_video": 260,
            "gross_margin_pct": 55.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.37,
            "videos_per_sample": 2.0
        },
        "Men's Care": {
            "aov": 23.93,
            "click_to_order_rate": 0.049,
            "clicks_per_video": 260,
            "gross_margin_pct": 55.0,
            "organic_commission_pct": 10.2,
            "paid_commission_pct": 5.1,
            "shop_tab_share": 0.286,
            "videos_per_sample": 1.67
        },
        "Nail Care": {
            "aov": 24.26,
            "click_to_order_rate": 0.049,
            "clicks_per_video": 260,
            "gross_margin_pct": 55.0,
            "organic_commission_pct": 12.5,
            "paid_commission_pct": 6.2,
            "shop_tab_share": 0.127,
            "videos_per_sample": 1.19
        },
        "Nasal & Oral Care": {
            "aov": 18.66,
            "click_to_order_rate": 0.049,
            "clicks_per_video": 260,
            "gross_margin_pct": 55.0,
            "organic_commission_pct": 12.5,
            "paid_commission_pct": 6.2,
            "shop_tab_share": 0.236,
            "videos_per_sample": 1.69
        },
        "Personal Care Appliances": {
            "aov": 32.89,
            "click_to_order_rate": 0.045,
            "clicks_per_video": 260,
            "gross_margin_pct": 55.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.272,
            "videos_per_sample": 1.98
        },
        "Skincare": {
            "aov": 23.54,
            "click_to_order_rate": 0.049,
            "clicks_per_video": 260,
            "gross_margin_pct": 55.0,
            "organic_commission_pct": 12.0,
            "paid_commission_pct": 6.0,
            "shop_tab_share": 0.351,
            "videos_per_sample": 1.5
        },
        "Special Personal Care": {
            "aov": 24.91,
            "click_to_order_rate": 0.049,
            "clicks_per_video": 260,
            "gross_margin_pct": 55.0,
            "organic_commission_pct": 12.2,
            "paid_commission_pct": 6.1,
            "shop_tab_share": 0.282,
            "videos_per_sample": 1.67
        }
    },
    "Books, Magazines & Audio": {
        "Children's & Infants' Books": {
            "aov": 36.47,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 38.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.227,
            "videos_per_sample": 1.0
        },
        "Education & Schooling": {
            "aov": 17.94,
            "click_to_order_rate": 0.038,
            "clicks_per_video": 200,
            "gross_margin_pct": 38.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.25,
            "videos_per_sample": 1.0
        },
        "Humanities & Social Sciences": {
            "aov": 20.73,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 200,
            "gross_margin_pct": 38.0,
            "organic_commission_pct": 5.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.227,
            "videos_per_sample": 1.0
        }
    },
    "Collectibles": {
        "Entertainment": {
            "aov": 43.78,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 2.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.256,
            "videos_per_sample": 1.0
        },
        "Sports Collectibles": {
            "aov": 39.54,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 3.2,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.311,
            "videos_per_sample": 1.0
        },
        "Trading Cards & Accessories": {
            "aov": 51.78,
            "click_to_order_rate": 0.024,
            "clicks_per_video": 200,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 2.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.65,
            "videos_per_sample": 1.0
        }
    },
    "Computers & Office Equipment": {
        "Computer Accessories": {
            "aov": 17.71,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 262,
            "gross_margin_pct": 34.0,
            "organic_commission_pct": 11.5,
            "paid_commission_pct": 5.8,
            "shop_tab_share": 0.191,
            "videos_per_sample": 1.09
        },
        "Data Storage & Software": {
            "aov": 29.28,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 702,
            "gross_margin_pct": 34.0,
            "organic_commission_pct": 6.5,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.1,
            "videos_per_sample": 1.09
        },
        "Network Components": {
            "aov": 20.43,
            "click_to_order_rate": 0.026,
            "clicks_per_video": 314,
            "gross_margin_pct": 34.0,
            "organic_commission_pct": 12.5,
            "paid_commission_pct": 6.2,
            "shop_tab_share": 0.14,
            "videos_per_sample": 1.09
        },
        "Office Equipment": {
            "aov": 19.21,
            "click_to_order_rate": 0.026,
            "clicks_per_video": 193,
            "gross_margin_pct": 34.0,
            "organic_commission_pct": 5.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.197,
            "videos_per_sample": 1.45
        },
        "Office Stationery & Supplies": {
            "aov": 13.34,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 180,
            "gross_margin_pct": 34.0,
            "organic_commission_pct": 12.5,
            "paid_commission_pct": 6.2,
            "shop_tab_share": 0.272,
            "videos_per_sample": 1.0
        }
    },
    "Fashion Accessories": {
        "Clothes Accessories": {
            "aov": 19.18,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 309,
            "gross_margin_pct": 54.0,
            "organic_commission_pct": 12.5,
            "paid_commission_pct": 6.2,
            "shop_tab_share": 0.65,
            "videos_per_sample": 1.16
        },
        "Costume Jewelry & Accessories": {
            "aov": 22.06,
            "click_to_order_rate": 0.036,
            "clicks_per_video": 220,
            "gross_margin_pct": 54.0,
            "organic_commission_pct": 12.5,
            "paid_commission_pct": 6.2,
            "shop_tab_share": 0.356,
            "videos_per_sample": 1.43
        },
        "Eyewear": {
            "aov": 21.93,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 220,
            "gross_margin_pct": 54.0,
            "organic_commission_pct": 7.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.65,
            "videos_per_sample": 1.38
        },
        "Fashion Watches & Accessories": {
            "aov": 27.86,
            "click_to_order_rate": 0.036,
            "clicks_per_video": 220,
            "gross_margin_pct": 54.0,
            "organic_commission_pct": 7.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.387,
            "videos_per_sample": 1.02
        },
        "Hair Accessories": {
            "aov": 27.72,
            "click_to_order_rate": 0.036,
            "clicks_per_video": 864,
            "gross_margin_pct": 54.0,
            "organic_commission_pct": 2.5,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.286,
            "videos_per_sample": 1.38
        },
        "Hair Extensions & Wigs": {
            "aov": 88.73,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 281,
            "gross_margin_pct": 54.0,
            "organic_commission_pct": 5.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.478,
            "videos_per_sample": 1.46
        }
    },
    "Food & Beverages": {
        "Baking": {
            "aov": 15.79,
            "click_to_order_rate": 0.058,
            "clicks_per_video": 240,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.394,
            "videos_per_sample": 3.0
        },
        "Drinks": {
            "aov": 27.66,
            "click_to_order_rate": 0.054,
            "clicks_per_video": 240,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.448,
            "videos_per_sample": 1.83
        },
        "Pantry Food": {
            "aov": 18.77,
            "click_to_order_rate": 0.054,
            "clicks_per_video": 240,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 6.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.441,
            "videos_per_sample": 1.29
        },
        "Snacks": {
            "aov": 19.61,
            "click_to_order_rate": 0.054,
            "clicks_per_video": 240,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 9.0,
            "paid_commission_pct": 4.5,
            "shop_tab_share": 0.411,
            "videos_per_sample": 1.97
        },
        "Staples & Cooking Essentials": {
            "aov": 24.64,
            "click_to_order_rate": 0.054,
            "clicks_per_video": 240,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.391,
            "videos_per_sample": 1.0
        }
    },
    "Furniture": {
        "Children's Furniture": {
            "aov": 102.6,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 200,
            "gross_margin_pct": 40.0,
            "organic_commission_pct": 6.8,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.3,
            "videos_per_sample": 1.0
        },
        "Commercial Furniture": {
            "aov": 132.31,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 200,
            "gross_margin_pct": 40.0,
            "organic_commission_pct": 8.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.349,
            "videos_per_sample": 1.0
        },
        "Indoor Furniture": {
            "aov": 143.7,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 200,
            "gross_margin_pct": 40.0,
            "organic_commission_pct": 8.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.374,
            "videos_per_sample": 1.0
        },
        "Outdoor Furniture": {
            "aov": 75.61,
            "click_to_order_rate": 0.026,
            "clicks_per_video": 200,
            "gross_margin_pct": 40.0,
            "organic_commission_pct": 7.5,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.19,
            "videos_per_sample": 1.56
        }
    },
    "Health": {
        "Medical Supplies": {
            "aov": 26.13,
            "click_to_order_rate": 0.054,
            "clicks_per_video": 240,
            "gross_margin_pct": 48.0,
            "organic_commission_pct": 12.2,
            "paid_commission_pct": 6.1,
            "shop_tab_share": 0.298,
            "videos_per_sample": 1.72
        },
        "Nutrition & Wellness": {
            "aov": 29.67,
            "click_to_order_rate": 0.05,
            "clicks_per_video": 240,
            "gross_margin_pct": 48.0,
            "organic_commission_pct": 15.0,
            "paid_commission_pct": 7.5,
            "shop_tab_share": 0.308,
            "videos_per_sample": 1.58
        }
    },
    "Home Improvement": {
        "Bathroom Fixtures": {
            "aov": 32.55,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 208,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 12.5,
            "paid_commission_pct": 6.2,
            "shop_tab_share": 0.248,
            "videos_per_sample": 1.0
        },
        "Building Supplies": {
            "aov": 33.06,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.208,
            "videos_per_sample": 1.0
        },
        "Electrical Equipment & Supplies": {
            "aov": 438.01,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 228,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 9.5,
            "paid_commission_pct": 4.8,
            "shop_tab_share": 0.282,
            "videos_per_sample": 1.0
        },
        "Garden Supplies": {
            "aov": 21.18,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 6.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.219,
            "videos_per_sample": 1.0
        },
        "Kitchen Fixtures": {
            "aov": 61.18,
            "click_to_order_rate": 0.026,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 11.0,
            "paid_commission_pct": 5.5,
            "shop_tab_share": 0.24,
            "videos_per_sample": 1.0
        },
        "Lights & Lighting": {
            "aov": 29.9,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 11.8,
            "paid_commission_pct": 5.9,
            "shop_tab_share": 0.128,
            "videos_per_sample": 1.0
        },
        "Security & Safety": {
            "aov": 37.7,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 11.0,
            "paid_commission_pct": 5.5,
            "shop_tab_share": 0.182,
            "videos_per_sample": 1.0
        },
        "Smart Home Systems": {
            "aov": 28.25,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 8.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.164,
            "videos_per_sample": 1.0
        }
    },
    "Home Supplies": {
        "Bathroom Supplies": {
            "aov": 21.97,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 10.1,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.259,
            "videos_per_sample": 1.15
        },
        "Festive & Party Supplies": {
            "aov": 36.39,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 359,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 11.2,
            "paid_commission_pct": 5.6,
            "shop_tab_share": 0.208,
            "videos_per_sample": 1.18
        },
        "Home Care Supplies": {
            "aov": 23.81,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 9.0,
            "paid_commission_pct": 4.5,
            "shop_tab_share": 0.316,
            "videos_per_sample": 1.09
        },
        "Home Decor": {
            "aov": 24.52,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 333,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 12.5,
            "paid_commission_pct": 6.2,
            "shop_tab_share": 0.248,
            "videos_per_sample": 1.0
        },
        "Home Organizers": {
            "aov": 28.58,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.265,
            "videos_per_sample": 2.14
        },
        "Laundry Tools & Accessories": {
            "aov": 19.18,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 6.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.387,
            "videos_per_sample": 1.23
        },
        "Miscellaneous Home": {
            "aov": 29.41,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 10.4,
            "paid_commission_pct": 5.2,
            "shop_tab_share": 0.346,
            "videos_per_sample": 1.1
        }
    },
    "Household Appliances": {
        "Commercial Appliances": {
            "aov": 48.66,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 180,
            "gross_margin_pct": 35.0,
            "organic_commission_pct": 12.5,
            "paid_commission_pct": 6.2,
            "shop_tab_share": 0.192,
            "videos_per_sample": 2.1
        },
        "Home Appliances": {
            "aov": 46.64,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 180,
            "gross_margin_pct": 35.0,
            "organic_commission_pct": 8.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.269,
            "videos_per_sample": 1.8
        },
        "Kitchen Appliances": {
            "aov": 44.48,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 180,
            "gross_margin_pct": 35.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.332,
            "videos_per_sample": 1.0
        },
        "Large Home Appliances": {
            "aov": 29.88,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 443,
            "gross_margin_pct": 35.0,
            "organic_commission_pct": 9.1,
            "paid_commission_pct": 4.5,
            "shop_tab_share": 0.276,
            "videos_per_sample": 1.33
        }
    },
    "Jewelry Accessories & Derivatives": {
        "Pearl": {
            "aov": 22.47,
            "click_to_order_rate": 0.036,
            "clicks_per_video": 220,
            "gross_margin_pct": 58.0,
            "organic_commission_pct": 4.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.316,
            "videos_per_sample": 1.0
        },
        "Platinum, Carat Gold": {
            "aov": 27.46,
            "click_to_order_rate": 0.036,
            "clicks_per_video": 220,
            "gross_margin_pct": 58.0,
            "organic_commission_pct": 9.4,
            "paid_commission_pct": 4.7,
            "shop_tab_share": 0.361,
            "videos_per_sample": 1.0
        }
    },
    "Kids' Fashion": {
        "Boys' Footwear": {
            "aov": 46.74,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 220,
            "gross_margin_pct": 50.0,
            "organic_commission_pct": 12.9,
            "paid_commission_pct": 6.5,
            "shop_tab_share": 0.49,
            "videos_per_sample": 1.94
        },
        "Kids' Fashion Accessories": {
            "aov": 33.77,
            "click_to_order_rate": 0.032,
            "clicks_per_video": 220,
            "gross_margin_pct": 50.0,
            "organic_commission_pct": 14.1,
            "paid_commission_pct": 7.0,
            "shop_tab_share": 0.428,
            "videos_per_sample": 1.79
        }
    },
    "Kitchenware": {
        "Barbecue": {
            "aov": 30.57,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.241,
            "videos_per_sample": 1.0
        },
        "Cookware": {
            "aov": 72.61,
            "click_to_order_rate": 0.026,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 8.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.417,
            "videos_per_sample": 1.53
        },
        "Cutlery & Tableware": {
            "aov": 41.02,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.428,
            "videos_per_sample": 1.0
        },
        "Drinkware": {
            "aov": 20.83,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.23,
            "videos_per_sample": 1.0
        },
        "Kitchen Utensils & Gadgets": {
            "aov": 26.01,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 9.0,
            "paid_commission_pct": 4.5,
            "shop_tab_share": 0.246,
            "videos_per_sample": 1.2
        },
        "Tea & Coffeeware": {
            "aov": 24.67,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 200,
            "gross_margin_pct": 42.0,
            "organic_commission_pct": 9.0,
            "paid_commission_pct": 4.5,
            "shop_tab_share": 0.432,
            "videos_per_sample": 1.0
        }
    },
    "Luggage & Bags": {
        "Functional Bags": {
            "aov": 40.03,
            "click_to_order_rate": 0.032,
            "clicks_per_video": 220,
            "gross_margin_pct": 50.0,
            "organic_commission_pct": 11.0,
            "paid_commission_pct": 5.5,
            "shop_tab_share": 0.391,
            "videos_per_sample": 1.0
        },
        "Luggage & Travel Bags": {
            "aov": 89.84,
            "click_to_order_rate": 0.024,
            "clicks_per_video": 220,
            "gross_margin_pct": 50.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.395,
            "videos_per_sample": 1.0
        },
        "Men's Bags": {
            "aov": 37.89,
            "click_to_order_rate": 0.032,
            "clicks_per_video": 220,
            "gross_margin_pct": 50.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.318,
            "videos_per_sample": 1.4
        },
        "Women's Bags": {
            "aov": 38.6,
            "click_to_order_rate": 0.032,
            "clicks_per_video": 220,
            "gross_margin_pct": 50.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.232,
            "videos_per_sample": 1.2
        }
    },
    "Menswear & Underwear": {
        "Men's Bottoms": {
            "aov": 40.67,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 220,
            "gross_margin_pct": 52.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.594,
            "videos_per_sample": 1.24
        },
        "Men's Tops": {
            "aov": 30.8,
            "click_to_order_rate": 0.032,
            "clicks_per_video": 220,
            "gross_margin_pct": 52.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.188,
            "videos_per_sample": 1.0
        },
        "Men's Underwear & Socks": {
            "aov": 35.85,
            "click_to_order_rate": 0.032,
            "clicks_per_video": 220,
            "gross_margin_pct": 52.0,
            "organic_commission_pct": 9.0,
            "paid_commission_pct": 4.5,
            "shop_tab_share": 0.367,
            "videos_per_sample": 1.0
        }
    },
    "Modest Fashion": {
        "Hijabs": {
            "aov": 29.45,
            "click_to_order_rate": 0.032,
            "clicks_per_video": 220,
            "gross_margin_pct": 52.0,
            "organic_commission_pct": 12.8,
            "paid_commission_pct": 6.4,
            "shop_tab_share": 0.382,
            "videos_per_sample": 1.0
        },
        "Prayer Attire & Equipment": {
            "aov": 25.96,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 220,
            "gross_margin_pct": 52.0,
            "organic_commission_pct": 12.7,
            "paid_commission_pct": 6.3,
            "shop_tab_share": 0.493,
            "videos_per_sample": 1.0
        }
    },
    "Pet Supplies": {
        "Bird Supplies": {
            "aov": 29.39,
            "click_to_order_rate": 0.05,
            "clicks_per_video": 240,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 8.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.225,
            "videos_per_sample": 1.23
        },
        "Dog & Cat Accessories": {
            "aov": 26.87,
            "click_to_order_rate": 0.054,
            "clicks_per_video": 240,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 13.5,
            "paid_commission_pct": 6.8,
            "shop_tab_share": 0.14,
            "videos_per_sample": 1.92
        },
        "Dog & Cat Food": {
            "aov": 33.43,
            "click_to_order_rate": 0.05,
            "clicks_per_video": 240,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 11.0,
            "paid_commission_pct": 5.5,
            "shop_tab_share": 0.286,
            "videos_per_sample": 1.93
        },
        "Dog & Cat Furniture": {
            "aov": 52.89,
            "click_to_order_rate": 0.046,
            "clicks_per_video": 240,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 8.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.383,
            "videos_per_sample": 1.93
        },
        "Dog & Cat Grooming": {
            "aov": 22.26,
            "click_to_order_rate": 0.054,
            "clicks_per_video": 240,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 8.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.1,
            "videos_per_sample": 1.83
        },
        "Dog & Cat Litter": {
            "aov": 127.41,
            "click_to_order_rate": 0.042,
            "clicks_per_video": 240,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 12.0,
            "paid_commission_pct": 6.0,
            "shop_tab_share": 0.316,
            "videos_per_sample": 1.87
        },
        "Farm Animal & Poultry Supplies": {
            "aov": 91.94,
            "click_to_order_rate": 0.042,
            "clicks_per_video": 240,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.144,
            "videos_per_sample": 1.93
        }
    },
    "Phones & Electronics": {
        "Audio & Video": {
            "aov": 27.21,
            "click_to_order_rate": 0.026,
            "clicks_per_video": 180,
            "gross_margin_pct": 35.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.258,
            "videos_per_sample": 1.0
        },
        "Cameras & Photography": {
            "aov": 47.82,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 180,
            "gross_margin_pct": 35.0,
            "organic_commission_pct": 5.5,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.277,
            "videos_per_sample": 1.0
        },
        "Gaming & Consoles": {
            "aov": 37.77,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 180,
            "gross_margin_pct": 35.0,
            "organic_commission_pct": 12.5,
            "paid_commission_pct": 6.2,
            "shop_tab_share": 0.22,
            "videos_per_sample": 1.44
        },
        "Mobile Phone Accessories": {
            "aov": 23.78,
            "click_to_order_rate": 0.026,
            "clicks_per_video": 180,
            "gross_margin_pct": 35.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.225,
            "videos_per_sample": 1.1
        },
        "Phones & Tablets": {
            "aov": 117.29,
            "click_to_order_rate": 0.014,
            "clicks_per_video": 180,
            "gross_margin_pct": 35.0,
            "organic_commission_pct": 6.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.283,
            "videos_per_sample": 2.25
        },
        "Smart & Wearable Devices": {
            "aov": 33.64,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 180,
            "gross_margin_pct": 35.0,
            "organic_commission_pct": 8.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.275,
            "videos_per_sample": 1.0
        },
        "Tablet & Computer Accessories": {
            "aov": 26.63,
            "click_to_order_rate": 0.026,
            "clicks_per_video": 637,
            "gross_margin_pct": 35.0,
            "organic_commission_pct": 10.5,
            "paid_commission_pct": 5.2,
            "shop_tab_share": 0.199,
            "videos_per_sample": 1.25
        },
        "Universal Accessories": {
            "aov": 28.49,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 279,
            "gross_margin_pct": 35.0,
            "organic_commission_pct": 10.8,
            "paid_commission_pct": 5.4,
            "shop_tab_share": 0.247,
            "videos_per_sample": 1.45
        }
    },
    "Shoes": {
        "Men's Shoes": {
            "aov": 28.06,
            "click_to_order_rate": 0.032,
            "clicks_per_video": 220,
            "gross_margin_pct": 50.0,
            "organic_commission_pct": 8.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.346,
            "videos_per_sample": 1.25
        },
        "Shoe Accessories": {
            "aov": 29.35,
            "click_to_order_rate": 0.032,
            "clicks_per_video": 220,
            "gross_margin_pct": 50.0,
            "organic_commission_pct": 12.7,
            "paid_commission_pct": 6.3,
            "shop_tab_share": 0.294,
            "videos_per_sample": 1.21
        },
        "Women's Shoes": {
            "aov": 36.16,
            "click_to_order_rate": 0.032,
            "clicks_per_video": 220,
            "gross_margin_pct": 50.0,
            "organic_commission_pct": 12.0,
            "paid_commission_pct": 6.0,
            "shop_tab_share": 0.352,
            "videos_per_sample": 1.67
        }
    },
    "Sports & Outdoor": {
        "Ball Sports": {
            "aov": 32.84,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.209,
            "videos_per_sample": 1.53
        },
        "Camping & Hiking": {
            "aov": 35.21,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.216,
            "videos_per_sample": 1.38
        },
        "Fitness": {
            "aov": 57.28,
            "click_to_order_rate": 0.026,
            "clicks_per_video": 200,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.417,
            "videos_per_sample": 2.0
        },
        "Leisure & Outdoor Recreation Equipment": {
            "aov": 20.25,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 250,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 12.0,
            "paid_commission_pct": 6.0,
            "shop_tab_share": 0.256,
            "videos_per_sample": 1.77
        },
        "Sport & Outdoor Clothing": {
            "aov": 36.62,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 10.5,
            "paid_commission_pct": 5.2,
            "shop_tab_share": 0.287,
            "videos_per_sample": 1.18
        },
        "Sports & Outdoor Accessories": {
            "aov": 30.39,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 12.0,
            "paid_commission_pct": 6.0,
            "shop_tab_share": 0.247,
            "videos_per_sample": 1.19
        },
        "Sports Footwear": {
            "aov": 59.47,
            "click_to_order_rate": 0.026,
            "clicks_per_video": 200,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 11.0,
            "paid_commission_pct": 5.5,
            "shop_tab_share": 0.259,
            "videos_per_sample": 1.78
        },
        "Swimwear, Surfwear & Wetsuits": {
            "aov": 28.74,
            "click_to_order_rate": 0.028,
            "clicks_per_video": 200,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.565,
            "videos_per_sample": 1.78
        }
    },
    "Textiles & Soft Furnishings": {
        "Bedding and Linens": {
            "aov": 33.43,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 44.0,
            "organic_commission_pct": 12.0,
            "paid_commission_pct": 6.0,
            "shop_tab_share": 0.253,
            "videos_per_sample": 1.15
        },
        "Household Textiles": {
            "aov": 41.81,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 44.0,
            "organic_commission_pct": 9.0,
            "paid_commission_pct": 4.5,
            "shop_tab_share": 0.374,
            "videos_per_sample": 1.26
        }
    },
    "Tools & Hardware": {
        "Garden Tools": {
            "aov": 42.33,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 40.0,
            "organic_commission_pct": 6.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.201,
            "videos_per_sample": 1.0
        },
        "Hand Tools": {
            "aov": 39.68,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 40.0,
            "organic_commission_pct": 12.2,
            "paid_commission_pct": 6.1,
            "shop_tab_share": 0.194,
            "videos_per_sample": 1.0
        },
        "Hardware": {
            "aov": 47.3,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 412,
            "gross_margin_pct": 40.0,
            "organic_commission_pct": 12.5,
            "paid_commission_pct": 6.2,
            "shop_tab_share": 0.1,
            "videos_per_sample": 1.0
        },
        "Measuring Tools": {
            "aov": 30.86,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 40.0,
            "organic_commission_pct": 8.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.145,
            "videos_per_sample": 1.0
        },
        "Power Tools": {
            "aov": 39.36,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 40.0,
            "organic_commission_pct": 8.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.224,
            "videos_per_sample": 1.5
        },
        "Pumps & Plumbing": {
            "aov": 34.58,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 301,
            "gross_margin_pct": 40.0,
            "organic_commission_pct": 10.8,
            "paid_commission_pct": 5.4,
            "shop_tab_share": 0.182,
            "videos_per_sample": 1.0
        },
        "Soldering Equipment": {
            "aov": 43.91,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 40.0,
            "organic_commission_pct": 8.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.313,
            "videos_per_sample": 1.0
        }
    },
    "Toys & Hobbies": {
        "Classic & Novelty Toys": {
            "aov": 23.38,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 200,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.291,
            "videos_per_sample": 1.0
        },
        "Dolls & Stuffed Toys": {
            "aov": 29.59,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 200,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 9.8,
            "paid_commission_pct": 4.9,
            "shop_tab_share": 0.326,
            "videos_per_sample": 1.0
        },
        "Educational Toys": {
            "aov": 22.41,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 200,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 6.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.351,
            "videos_per_sample": 1.6
        },
        "Electric & Remote Control Toys": {
            "aov": 24.64,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 200,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 8.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.172,
            "videos_per_sample": 1.11
        },
        "Games & Puzzles": {
            "aov": 20.9,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 200,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.356,
            "videos_per_sample": 1.0
        },
        "Sports & Outdoor Play": {
            "aov": 95.16,
            "click_to_order_rate": 0.022,
            "clicks_per_video": 200,
            "gross_margin_pct": 45.0,
            "organic_commission_pct": 5.0,
            "paid_commission_pct": 4.0,
            "shop_tab_share": 0.389,
            "videos_per_sample": 1.0
        }
    },
    "Womenswear & Underwear": {
        "Women's Bottoms": {
            "aov": 46.31,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 220,
            "gross_margin_pct": 52.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.568,
            "videos_per_sample": 1.08
        },
        "Women's Dresses": {
            "aov": 29.37,
            "click_to_order_rate": 0.03,
            "clicks_per_video": 220,
            "gross_margin_pct": 52.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.504,
            "videos_per_sample": 1.0
        },
        "Women's Sleepwear & Loungewear": {
            "aov": 23.08,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 220,
            "gross_margin_pct": 52.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.65,
            "videos_per_sample": 1.0
        },
        "Women's Suits & Sets": {
            "aov": 33.35,
            "click_to_order_rate": 0.032,
            "clicks_per_video": 220,
            "gross_margin_pct": 52.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.1,
            "videos_per_sample": 1.23
        },
        "Women's Tops": {
            "aov": 27.77,
            "click_to_order_rate": 0.036,
            "clicks_per_video": 220,
            "gross_margin_pct": 52.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.22,
            "videos_per_sample": 1.12
        },
        "Women's Underwear": {
            "aov": 27.61,
            "click_to_order_rate": 0.034,
            "clicks_per_video": 220,
            "gross_margin_pct": 52.0,
            "organic_commission_pct": 10.0,
            "paid_commission_pct": 5.0,
            "shop_tab_share": 0.553,
            "videos_per_sample": 1.0
        }
    }
}


CATEGORY_GROSS_MARGIN_DEFAULTS = {
    "Automotive & Motorcycle": 38.0,
    "Baby & Maternity": 46.0,
    "Beauty & Personal Care": 55.0,
    "Books, Magazines & Audio": 38.0,
    "Collectibles": 45.0,
    "Computers & Office Equipment": 34.0,
    "Fashion Accessories": 54.0,
    "Food & Beverages": 45.0,
    "Furniture": 40.0,
    "Health": 48.0,
    "Home Improvement": 42.0,
    "Home Supplies": 42.0,
    "Household Appliances": 35.0,
    "Jewelry Accessories & Derivatives": 58.0,
    "Kids' Fashion": 50.0,
    "Kitchenware": 42.0,
    "Luggage & Bags": 50.0,
    "Menswear & Underwear": 52.0,
    "Modest Fashion": 52.0,
    "Pet Supplies": 45.0,
    "Phones & Electronics": 35.0,
    "Shoes": 50.0,
    "Sports & Outdoor": 45.0,
    "Textiles & Soft Furnishings": 44.0,
    "Tools & Hardware": 40.0,
    "Toys & Hobbies": 45.0,
    "Womenswear & Underwear": 52.0
}


DEFAULT_SKU_PROFILES = [
    {"category": "Beauty & Personal Care", "subcategory": "Skincare", "gross_margin_pct": 55.0, "organic_commission_pct": 12.0, "paid_commission_pct": 6.0},
    {"category": "Food & Beverages", "subcategory": "Snacks", "gross_margin_pct": 45.0, "organic_commission_pct": 9.0, "paid_commission_pct": 4.5},
    {"category": "Health", "subcategory": "Nutrition & Wellness", "gross_margin_pct": 48.0, "organic_commission_pct": 15.0, "paid_commission_pct": 7.5},
    {"category": "Phones & Electronics", "subcategory": "Mobile Phone Accessories", "gross_margin_pct": 35.0, "organic_commission_pct": 10.0, "paid_commission_pct": 5.0},
    {"category": "Household Appliances", "subcategory": "Kitchen Appliances", "gross_margin_pct": 35.0, "organic_commission_pct": 10.0, "paid_commission_pct": 5.0},
]

CATEGORY_LABELS = {
    "zh": {
        "Automotive & Motorcycle": "汽车与摩托车",
        "Baby & Maternity": "母婴用品",
        "Beauty & Personal Care": "美妆个护",
        "Books, Magazines & Audio": "图书、杂志与音频",
        "Collectibles": "收藏品",
        "Computers & Office Equipment": "电脑与办公设备",
        "Fashion Accessories": "时尚配饰",
        "Food & Beverages": "食品饮料",
        "Furniture": "家具",
        "Health": "健康",
        "Home Improvement": "家装建材",
        "Home Supplies": "家居用品",
        "Household Appliances": "家用电器",
        "Jewelry Accessories & Derivatives": "珠宝配饰及衍生品",
        "Kids' Fashion": "童装童鞋",
        "Kitchenware": "厨具",
        "Luggage & Bags": "箱包",
        "Menswear & Underwear": "男装与内衣",
        "Modest Fashion": "端庄服饰",
        "Pet Supplies": "宠物用品",
        "Phones & Electronics": "手机与电子产品",
        "Shoes": "鞋靴",
        "Sports & Outdoor": "运动户外",
        "Textiles & Soft Furnishings": "家纺软装",
        "Tools & Hardware": "工具与五金",
        "Toys & Hobbies": "玩具与兴趣爱好",
        "Womenswear & Underwear": "女装与内衣",
    },
    "de": {
        "Automotive & Motorcycle": "Auto & Motorrad",
        "Baby & Maternity": "Baby & Schwangerschaft",
        "Beauty & Personal Care": "Beauty & Körperpflege",
        "Books, Magazines & Audio": "Bücher, Magazine & Audio",
        "Collectibles": "Sammlerstücke",
        "Computers & Office Equipment": "Computer & Büroausstattung",
        "Fashion Accessories": "Modeaccessoires",
        "Food & Beverages": "Lebensmittel & Getränke",
        "Furniture": "Möbel",
        "Health": "Gesundheit",
        "Home Improvement": "Heimwerken",
        "Home Supplies": "Haushaltswaren",
        "Household Appliances": "Haushaltsgeräte",
        "Jewelry Accessories & Derivatives": "Schmuckzubehör & Derivate",
        "Kids' Fashion": "Kindermode",
        "Kitchenware": "Küchenwaren",
        "Luggage & Bags": "Gepäck & Taschen",
        "Menswear & Underwear": "Herrenmode & Unterwäsche",
        "Modest Fashion": "Modest Fashion",
        "Pet Supplies": "Tierbedarf",
        "Phones & Electronics": "Telefone & Elektronik",
        "Shoes": "Schuhe",
        "Sports & Outdoor": "Sport & Outdoor",
        "Textiles & Soft Furnishings": "Textilien & Heimtextilien",
        "Tools & Hardware": "Werkzeuge & Hardware",
        "Toys & Hobbies": "Spielzeug & Hobbys",
        "Womenswear & Underwear": "Damenmode & Unterwäsche",
    },
    "nl": {
        "Automotive & Motorcycle": "Auto & motor",
        "Baby & Maternity": "Baby & zwangerschap",
        "Beauty & Personal Care": "Beauty & persoonlijke verzorging",
        "Books, Magazines & Audio": "Boeken, magazines & audio",
        "Collectibles": "Verzamelobjecten",
        "Computers & Office Equipment": "Computers & kantoorapparatuur",
        "Fashion Accessories": "Modeaccessoires",
        "Food & Beverages": "Eten & drinken",
        "Furniture": "Meubels",
        "Health": "Gezondheid",
        "Home Improvement": "Woningverbetering",
        "Home Supplies": "Huishoudelijke artikelen",
        "Household Appliances": "Huishoudelijke apparaten",
        "Jewelry Accessories & Derivatives": "Sieradenaccessoires & derivaten",
        "Kids' Fashion": "Kindermode",
        "Kitchenware": "Keukengerei",
        "Luggage & Bags": "Bagage & tassen",
        "Menswear & Underwear": "Herenmode & ondergoed",
        "Modest Fashion": "Modest fashion",
        "Pet Supplies": "Dierbenodigdheden",
        "Phones & Electronics": "Telefoons & elektronica",
        "Shoes": "Schoenen",
        "Sports & Outdoor": "Sport & outdoor",
        "Textiles & Soft Furnishings": "Textiel & zachte inrichting",
        "Tools & Hardware": "Gereedschap & hardware",
        "Toys & Hobbies": "Speelgoed & hobby's",
        "Womenswear & Underwear": "Damesmode & ondergoed",
    },
}

SUBCATEGORY_LABELS = {
    "zh": {
        "Car Electronics": "汽车电子", "Car Exterior Accessories": "汽车外饰配件", "Car Interior Accessories": "汽车内饰配件", "Car Repair Tools": "汽车维修工具", "Car Washing & Maintenance": "洗车与保养",
        "Baby Care & Health": "婴儿护理与健康", "Baby Clothing & Shoes": "婴儿服装与鞋", "Baby Fashion Accessories": "婴儿时尚配饰", "Baby Furniture": "婴儿家具", "Baby Safety": "婴儿安全用品", "Baby Toys": "婴儿玩具", "Baby Travel Gear": "婴儿出行用品", "Maternity Supplies": "孕产用品", "Nursing & Feeding": "哺乳与喂养",
        "Bath & Body Care": "沐浴身体护理", "Eye & Ear Care": "眼耳护理", "Fragrance": "香水香氛", "Haircare & Styling": "头发护理与造型", "Hand & Foot Care": "手足护理", "Makeup": "彩妆", "Men's Care": "男士护理", "Nail Care": "美甲护理", "Nasal & Oral Care": "鼻腔与口腔护理", "Personal Care Appliances": "个护电器", "Skincare": "护肤", "Special Personal Care": "特殊个护",
        "Children's & Infants' Books": "儿童与婴幼儿图书", "Education & Schooling": "教育与学习", "Humanities & Social Sciences": "人文社科",
        "Entertainment": "娱乐收藏", "Sports Collectibles": "体育收藏", "Trading Cards & Accessories": "集换式卡牌与配件",
        "Computer Accessories": "电脑配件", "Data Storage & Software": "数据存储与软件", "Network Components": "网络组件", "Office Equipment": "办公设备", "Office Stationery & Supplies": "办公文具与用品",
        "Clothes Accessories": "服饰配件", "Costume Jewelry & Accessories": "饰品与配件", "Eyewear": "眼镜", "Fashion Watches & Accessories": "时尚手表与配件", "Hair Accessories": "发饰", "Hair Extensions & Wigs": "接发与假发",
        "Baking": "烘焙", "Drinks": "饮品", "Pantry Food": "食品储备", "Snacks": "零食", "Staples & Cooking Essentials": "主食与烹饪基础食材",
        "Children's Furniture": "儿童家具", "Commercial Furniture": "商用家具", "Indoor Furniture": "室内家具", "Outdoor Furniture": "户外家具",
        "Medical Supplies": "医疗用品", "Nutrition & Wellness": "营养与健康",
        "Bathroom Fixtures": "卫浴五金", "Building Supplies": "建筑材料", "Electrical Equipment & Supplies": "电气设备与用品", "Garden Supplies": "园艺用品", "Kitchen Fixtures": "厨房装置", "Lights & Lighting": "灯具照明", "Security & Safety": "安防安全", "Smart Home Systems": "智能家居系统",
        "Bathroom Supplies": "浴室用品", "Festive & Party Supplies": "节庆派对用品", "Home Care Supplies": "家庭清洁护理", "Home Decor": "家居装饰", "Home Organizers": "收纳用品", "Laundry Tools & Accessories": "洗衣工具与配件", "Miscellaneous Home": "其他家居",
        "Commercial Appliances": "商用电器", "Home Appliances": "家庭电器", "Kitchen Appliances": "厨房电器", "Large Home Appliances": "大家电",
        "Pearl": "珍珠", "Platinum, Carat Gold": "铂金与K金",
        "Boys' Footwear": "男童鞋", "Kids' Fashion Accessories": "儿童时尚配饰",
        "Barbecue": "烧烤", "Cookware": "锅具", "Cutlery & Tableware": "餐具", "Drinkware": "饮具", "Kitchen Utensils & Gadgets": "厨房工具与小物", "Tea & Coffeeware": "茶具与咖啡器具",
        "Functional Bags": "功能包", "Luggage & Travel Bags": "行李箱与旅行包", "Men's Bags": "男包", "Women's Bags": "女包",
        "Men's Bottoms": "男士下装", "Men's Tops": "男士上装", "Men's Underwear & Socks": "男士内衣袜子",
        "Hijabs": "头巾", "Prayer Attire & Equipment": "祈祷服饰与用品",
        "Bird Supplies": "鸟类用品", "Dog & Cat Accessories": "猫狗配件", "Dog & Cat Food": "猫狗食品", "Dog & Cat Furniture": "猫狗家具", "Dog & Cat Grooming": "猫狗美容护理", "Dog & Cat Litter": "猫狗清洁用品", "Farm Animal & Poultry Supplies": "农场动物与家禽用品",
        "Audio & Video": "音频与视频", "Cameras & Photography": "相机与摄影", "Gaming & Consoles": "游戏与主机", "Mobile Phone Accessories": "手机配件", "Phones & Tablets": "手机与平板", "Smart & Wearable Devices": "智能与穿戴设备", "Tablet & Computer Accessories": "平板与电脑配件", "Universal Accessories": "通用配件",
        "Men's Shoes": "男鞋", "Shoe Accessories": "鞋配件", "Women's Shoes": "女鞋",
        "Ball Sports": "球类运动", "Camping & Hiking": "露营徒步", "Fitness": "健身", "Leisure & Outdoor Recreation Equipment": "休闲户外装备", "Sport & Outdoor Clothing": "运动户外服装", "Sports & Outdoor Accessories": "运动户外配件", "Sports Footwear": "运动鞋", "Swimwear, Surfwear & Wetsuits": "泳装冲浪服与潜水服",
        "Bedding and Linens": "床品与布草", "Household Textiles": "家用纺织品",
        "Garden Tools": "园艺工具", "Hand Tools": "手动工具", "Hardware": "五金", "Measuring Tools": "测量工具", "Power Tools": "电动工具", "Pumps & Plumbing": "泵与管道", "Soldering Equipment": "焊接设备",
        "Classic & Novelty Toys": "经典与新奇玩具", "Dolls & Stuffed Toys": "娃娃与毛绒玩具", "Educational Toys": "益智教育玩具", "Electric & Remote Control Toys": "电动与遥控玩具", "Games & Puzzles": "游戏与拼图", "Sports & Outdoor Play": "运动与户外玩具",
        "Women's Bottoms": "女士下装", "Women's Dresses": "女士连衣裙", "Women's Sleepwear & Loungewear": "女士睡衣家居服", "Women's Suits & Sets": "女士套装", "Women's Tops": "女士上装", "Women's Underwear": "女士内衣",
    },
    "de": {
        "Car Electronics": "Autoelektronik", "Car Exterior Accessories": "Auto-Außenzubehör", "Car Interior Accessories": "Auto-Innenzubehör", "Car Repair Tools": "Autoreparaturwerkzeuge", "Car Washing & Maintenance": "Autowäsche & Pflege",
        "Baby Care & Health": "Babypflege & Gesundheit", "Baby Clothing & Shoes": "Babykleidung & Schuhe", "Baby Fashion Accessories": "Baby-Modeaccessoires", "Baby Furniture": "Babymöbel", "Baby Safety": "Babysicherheit", "Baby Toys": "Babyspielzeug", "Baby Travel Gear": "Baby-Reiseausstattung", "Maternity Supplies": "Schwangerschaftsbedarf", "Nursing & Feeding": "Stillen & Füttern",
        "Bath & Body Care": "Bad- & Körperpflege", "Eye & Ear Care": "Augen- & Ohrenpflege", "Fragrance": "Duft", "Haircare & Styling": "Haarpflege & Styling", "Hand & Foot Care": "Hand- & Fußpflege", "Makeup": "Make-up", "Men's Care": "Männerpflege", "Nail Care": "Nagelpflege", "Nasal & Oral Care": "Nasen- & Mundpflege", "Personal Care Appliances": "Körperpflegegeräte", "Skincare": "Hautpflege", "Special Personal Care": "Spezielle Körperpflege",
        "Children's & Infants' Books": "Kinder- & Babybücher", "Education & Schooling": "Bildung & Schule", "Humanities & Social Sciences": "Geistes- & Sozialwissenschaften",
        "Entertainment": "Entertainment", "Sports Collectibles": "Sport-Sammlerstücke", "Trading Cards & Accessories": "Sammelkarten & Zubehör",
        "Computer Accessories": "Computerzubehör", "Data Storage & Software": "Datenspeicher & Software", "Network Components": "Netzwerkkomponenten", "Office Equipment": "Bürogeräte", "Office Stationery & Supplies": "Bürobedarf & Schreibwaren",
        "Clothes Accessories": "Kleidungsaccessoires", "Costume Jewelry & Accessories": "Modeschmuck & Accessoires", "Eyewear": "Brillen", "Fashion Watches & Accessories": "Modeuhren & Zubehör", "Hair Accessories": "Haarschmuck", "Hair Extensions & Wigs": "Extensions & Perücken",
        "Baking": "Backen", "Drinks": "Getränke", "Pantry Food": "Vorratslebensmittel", "Snacks": "Snacks", "Staples & Cooking Essentials": "Grundnahrungsmittel & Kochzutaten",
        "Children's Furniture": "Kindermöbel", "Commercial Furniture": "Gewerbemöbel", "Indoor Furniture": "Innenmöbel", "Outdoor Furniture": "Outdoor-Möbel",
        "Medical Supplies": "Medizinbedarf", "Nutrition & Wellness": "Ernährung & Wellness",
        "Bathroom Fixtures": "Badarmaturen", "Building Supplies": "Baumaterialien", "Electrical Equipment & Supplies": "Elektrogeräte & Zubehör", "Garden Supplies": "Gartenbedarf", "Kitchen Fixtures": "Küchenausstattung", "Lights & Lighting": "Lampen & Beleuchtung", "Security & Safety": "Sicherheit", "Smart Home Systems": "Smart-Home-Systeme",
        "Bathroom Supplies": "Badbedarf", "Festive & Party Supplies": "Fest- & Partybedarf", "Home Care Supplies": "Haushaltspflege", "Home Decor": "Wohnaccessoires", "Home Organizers": "Aufbewahrung", "Laundry Tools & Accessories": "Wäschetools & Zubehör", "Miscellaneous Home": "Sonstiges Wohnen",
        "Commercial Appliances": "Gewerbegeräte", "Home Appliances": "Haushaltsgeräte", "Kitchen Appliances": "Küchengeräte", "Large Home Appliances": "Großgeräte",
        "Pearl": "Perlen", "Platinum, Carat Gold": "Platin & Karatgold",
        "Boys' Footwear": "Jungenschuhe", "Kids' Fashion Accessories": "Kinder-Modeaccessoires",
        "Barbecue": "Grillen", "Cookware": "Kochgeschirr", "Cutlery & Tableware": "Besteck & Geschirr", "Drinkware": "Trinkgefäße", "Kitchen Utensils & Gadgets": "Küchenutensilien & Gadgets", "Tea & Coffeeware": "Tee- & Kaffeezubehör",
        "Functional Bags": "Funktionstaschen", "Luggage & Travel Bags": "Gepäck & Reisetaschen", "Men's Bags": "Herrentaschen", "Women's Bags": "Damentaschen",
        "Men's Bottoms": "Herrenhosen", "Men's Tops": "Herrenoberteile", "Men's Underwear & Socks": "Herrenunterwäsche & Socken",
        "Hijabs": "Hijabs", "Prayer Attire & Equipment": "Gebetskleidung & Zubehör",
        "Bird Supplies": "Vogelbedarf", "Dog & Cat Accessories": "Hunde- & Katzenzubehör", "Dog & Cat Food": "Hunde- & Katzenfutter", "Dog & Cat Furniture": "Hunde- & Katzenmöbel", "Dog & Cat Grooming": "Hunde- & Katzenpflege", "Dog & Cat Litter": "Hunde- & Katzenstreu", "Farm Animal & Poultry Supplies": "Nutztiere & Geflügelbedarf",
        "Audio & Video": "Audio & Video", "Cameras & Photography": "Kameras & Fotografie", "Gaming & Consoles": "Gaming & Konsolen", "Mobile Phone Accessories": "Handyzubehör", "Phones & Tablets": "Telefone & Tablets", "Smart & Wearable Devices": "Smart- & Wearable-Geräte", "Tablet & Computer Accessories": "Tablet- & Computerzubehör", "Universal Accessories": "Universalzubehör",
        "Men's Shoes": "Herrenschuhe", "Shoe Accessories": "Schuhzubehör", "Women's Shoes": "Damenschuhe",
        "Ball Sports": "Ballsport", "Camping & Hiking": "Camping & Wandern", "Fitness": "Fitness", "Leisure & Outdoor Recreation Equipment": "Freizeit- & Outdoor-Ausrüstung", "Sport & Outdoor Clothing": "Sport- & Outdoorbekleidung", "Sports & Outdoor Accessories": "Sport- & Outdoorzubehör", "Sports Footwear": "Sportschuhe", "Swimwear, Surfwear & Wetsuits": "Bademode, Surfwear & Neoprenanzüge",
        "Bedding and Linens": "Bettwaren & Wäsche", "Household Textiles": "Haushaltstextilien",
        "Garden Tools": "Gartenwerkzeuge", "Hand Tools": "Handwerkzeuge", "Hardware": "Hardware", "Measuring Tools": "Messwerkzeuge", "Power Tools": "Elektrowerkzeuge", "Pumps & Plumbing": "Pumpen & Sanitär", "Soldering Equipment": "Lötgeräte",
        "Classic & Novelty Toys": "Klassisches & Neuheitenspielzeug", "Dolls & Stuffed Toys": "Puppen & Plüschtiere", "Educational Toys": "Lernspielzeug", "Electric & Remote Control Toys": "Elektrisches & ferngesteuertes Spielzeug", "Games & Puzzles": "Spiele & Puzzles", "Sports & Outdoor Play": "Sport- & Outdoor-Spielzeug",
        "Women's Bottoms": "Damenunterteile", "Women's Dresses": "Damenkleider", "Women's Sleepwear & Loungewear": "Damen-Nachtwäsche & Loungewear", "Women's Suits & Sets": "Damenanzüge & Sets", "Women's Tops": "Damenoberteile", "Women's Underwear": "Damenunterwäsche",
    },
    "nl": {
        "Car Electronics": "Auto-elektronica", "Car Exterior Accessories": "Auto-exterieuraccessoires", "Car Interior Accessories": "Auto-interieuraccessoires", "Car Repair Tools": "Autoreparatiegereedschap", "Car Washing & Maintenance": "Autowas & onderhoud",
        "Baby Care & Health": "Babyverzorging & gezondheid", "Baby Clothing & Shoes": "Babykleding & schoenen", "Baby Fashion Accessories": "Baby-modeaccessoires", "Baby Furniture": "Babymeubels", "Baby Safety": "Babyveiligheid", "Baby Toys": "Babyspeelgoed", "Baby Travel Gear": "Babyreisartikelen", "Maternity Supplies": "Zwangerschapsbenodigdheden", "Nursing & Feeding": "Borstvoeding & voeding",
        "Bath & Body Care": "Bad- & lichaamsverzorging", "Eye & Ear Care": "Oog- & oorverzorging", "Fragrance": "Geuren", "Haircare & Styling": "Haarverzorging & styling", "Hand & Foot Care": "Hand- & voetverzorging", "Makeup": "Make-up", "Men's Care": "Mannenverzorging", "Nail Care": "Nagelverzorging", "Nasal & Oral Care": "Neus- & mondverzorging", "Personal Care Appliances": "Persoonlijke verzorgingsapparaten", "Skincare": "Huidverzorging", "Special Personal Care": "Speciale persoonlijke verzorging",
        "Children's & Infants' Books": "Kinder- & babyboeken", "Education & Schooling": "Onderwijs & scholing", "Humanities & Social Sciences": "Geestes- & sociale wetenschappen",
        "Entertainment": "Entertainment", "Sports Collectibles": "Sportverzamelobjecten", "Trading Cards & Accessories": "Ruilkaarten & accessoires",
        "Computer Accessories": "Computeraccessoires", "Data Storage & Software": "Dataopslag & software", "Network Components": "Netwerkcomponenten", "Office Equipment": "Kantoorapparatuur", "Office Stationery & Supplies": "Kantoorartikelen",
        "Clothes Accessories": "Kledingaccessoires", "Costume Jewelry & Accessories": "Modesieraden & accessoires", "Eyewear": "Brillen", "Fashion Watches & Accessories": "Modehorloges & accessoires", "Hair Accessories": "Haaraccessoires", "Hair Extensions & Wigs": "Hairextensions & pruiken",
        "Baking": "Bakken", "Drinks": "Dranken", "Pantry Food": "Voorraadkast-eten", "Snacks": "Snacks", "Staples & Cooking Essentials": "Basisproducten & kookbenodigdheden",
        "Children's Furniture": "Kindermeubels", "Commercial Furniture": "Commerciële meubels", "Indoor Furniture": "Binnenmeubels", "Outdoor Furniture": "Buitenmeubels",
        "Medical Supplies": "Medische benodigdheden", "Nutrition & Wellness": "Voeding & wellness",
        "Bathroom Fixtures": "Badkamerarmaturen", "Building Supplies": "Bouwmaterialen", "Electrical Equipment & Supplies": "Elektrische apparatuur & benodigdheden", "Garden Supplies": "Tuinbenodigdheden", "Kitchen Fixtures": "Keukenarmaturen", "Lights & Lighting": "Lampen & verlichting", "Security & Safety": "Beveiliging & veiligheid", "Smart Home Systems": "Smart-home-systemen",
        "Bathroom Supplies": "Badkamerbenodigdheden", "Festive & Party Supplies": "Feest- & partybenodigdheden", "Home Care Supplies": "Huishoudverzorging", "Home Decor": "Woondecoratie", "Home Organizers": "Opbergers", "Laundry Tools & Accessories": "Wasaccessoires", "Miscellaneous Home": "Overig wonen",
        "Commercial Appliances": "Commerciële apparaten", "Home Appliances": "Huishoudelijke apparaten", "Kitchen Appliances": "Keukenapparaten", "Large Home Appliances": "Grote huishoudelijke apparaten",
        "Pearl": "Parels", "Platinum, Carat Gold": "Platina & karaatgoud",
        "Boys' Footwear": "Jongensschoenen", "Kids' Fashion Accessories": "Kinder-modeaccessoires",
        "Barbecue": "Barbecue", "Cookware": "Kookgerei", "Cutlery & Tableware": "Bestek & servies", "Drinkware": "Drinkgerei", "Kitchen Utensils & Gadgets": "Keukengerei & gadgets", "Tea & Coffeeware": "Thee- & koffieware",
        "Functional Bags": "Functionele tassen", "Luggage & Travel Bags": "Bagage & reistassen", "Men's Bags": "Herentassen", "Women's Bags": "Damestassen",
        "Men's Bottoms": "Herenbroeken", "Men's Tops": "Herentops", "Men's Underwear & Socks": "Herenondergoed & sokken",
        "Hijabs": "Hijabs", "Prayer Attire & Equipment": "Gebedskleding & uitrusting",
        "Bird Supplies": "Vogelbenodigdheden", "Dog & Cat Accessories": "Honden- & kattenaccessoires", "Dog & Cat Food": "Honden- & kattenvoer", "Dog & Cat Furniture": "Honden- & kattenmeubels", "Dog & Cat Grooming": "Honden- & kattenverzorging", "Dog & Cat Litter": "Honden- & kattenbakvulling", "Farm Animal & Poultry Supplies": "Boerderijdieren- & pluimveebenodigdheden",
        "Audio & Video": "Audio & video", "Cameras & Photography": "Camera's & fotografie", "Gaming & Consoles": "Gaming & consoles", "Mobile Phone Accessories": "Mobiele telefoonaccessoires", "Phones & Tablets": "Telefoons & tablets", "Smart & Wearable Devices": "Smart & wearable apparaten", "Tablet & Computer Accessories": "Tablet- & computeraccessoires", "Universal Accessories": "Universele accessoires",
        "Men's Shoes": "Herenschoenen", "Shoe Accessories": "Schoenaccessoires", "Women's Shoes": "Damesschoenen",
        "Ball Sports": "Balsporten", "Camping & Hiking": "Kamperen & wandelen", "Fitness": "Fitness", "Leisure & Outdoor Recreation Equipment": "Vrijetijds- & outdooruitrusting", "Sport & Outdoor Clothing": "Sport- & outdoorkleding", "Sports & Outdoor Accessories": "Sport- & outdooraccessoires", "Sports Footwear": "Sportschoenen", "Swimwear, Surfwear & Wetsuits": "Badmode, surfwear & wetsuits",
        "Bedding and Linens": "Beddengoed & linnengoed", "Household Textiles": "Huishoudtextiel",
        "Garden Tools": "Tuingereedschap", "Hand Tools": "Handgereedschap", "Hardware": "Hardware", "Measuring Tools": "Meetgereedschap", "Power Tools": "Elektrisch gereedschap", "Pumps & Plumbing": "Pompen & sanitair", "Soldering Equipment": "Soldeerapparatuur",
        "Classic & Novelty Toys": "Klassiek & nieuwigheidsspeelgoed", "Dolls & Stuffed Toys": "Poppen & knuffels", "Educational Toys": "Educatief speelgoed", "Electric & Remote Control Toys": "Elektrisch & afstandsbediend speelgoed", "Games & Puzzles": "Spellen & puzzels", "Sports & Outdoor Play": "Sport- & buitenspeelgoed",
        "Women's Bottoms": "Damesbroeken", "Women's Dresses": "Damesjurken", "Women's Sleepwear & Loungewear": "Damesnachtkleding & loungewear", "Women's Suits & Sets": "Damespakken & sets", "Women's Tops": "Damestops", "Women's Underwear": "Damesondergoed",
    },
}


PHASES = [
    {"key": "phase1", "name": "Phase 1 - Cold Start", "samples_per_sku": 30, "take_rate": 0.00, "color": "#F6F8FB"},
    {"key": "phase2", "name": "Phase 2 - Growth", "samples_per_sku": 25, "take_rate": 0.05, "color": "#F5FAF8"},
    {"key": "phase3", "name": "Phase 3 - Scale", "samples_per_sku": 20, "take_rate": 0.10, "color": "#FAF8F4"},
]

PROMO_WEEKS = 9
FBT_FREE_SHIPPING_AOV_THRESHOLD = 20.0
MODEL_VERSION = "DE planning model v1.2 | Hit-product calibrated Apr 2026"
MODEL_LAST_REVIEWED = "DE hit-product pool check | Apr 29 2026"
LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
SCENARIO_ADJUSTMENTS = {
    "conservative": {"clicks": 0.85, "conversion": 0.85, "roas": 0.90},
    "base": {"clicks": 1.00, "conversion": 1.00, "roas": 1.00},
    "upside": {"clicks": 1.15, "conversion": 1.15, "roas": 1.10},
}
CHART_COLORS = {
    "gmv": "#315EEC",
    "cost": "#7C8797",
    "profit": "#12A08C",
    "cumulative": "#7C3AED",
    "grid": "#EAF0F7",
    "text": "#111827",
}


TEXT = {
    "en": {
        "language": "Language",
        "title": "TikTok Shop Growth Visualizer",
        "caption": "Client-ready planning simulator for SKU samples, creator videos, clicks, GMV, costs, and profit",
        "global_inputs": "Global Inputs",
        "plan_setup": "Plan Setup",
        "step1_title": "Step 1 · Confirm listing scope",
        "step1_body": "Start with the expected number of SKUs to be listed. The simulator will then prepare the phase plan, SKU setup, and forecast workspace around that portfolio size.",
        "expected_listing_skus": "Expected listing SKUs",
        "continue_setup": "Continue to plan setup",
        "setup_ready": "Listing scope confirmed. You can adjust assumptions in the sidebar and SKU details below.",
        "plan_preview": "Plan preview",
        "plan_preview_text": "This simulation will model {skus} SKUs across {weeks} weeks. Samples per SKU/week: {samples}; paid growth budget: {take_rates}; content sales window: {organic_window} weeks; Ads ROAS: {ads_roas}.",
        "assumption_quality": "Assumption quality",
        "assumption_quality_text": "Current status: {status}. Planning inputs are useful for scenario discussion; AM-aligned or merchant-confirmed inputs should be used before treating the result as a business target.",
        "cost_assumptions": "Cost Assumptions",
        "growth_levers": "Growth Levers",
        "target_setup": "Target Setup",
        "target_gmv": "Target GMV (€)",
        "target_profit": "Target Profit (€)",
        "target_gmv_help": "Optional. Leave as 0 if there is no GMV target for this scenario.",
        "target_profit_help": "Optional. Leave as 0 if there is no profit target for this scenario.",
        "scenario_case": "Scenario sensitivity",
        "scenario_conservative": "Conservative",
        "scenario_base": "Base",
        "scenario_upside": "Upside",
        "scenario_case_help": "Optional lens for fast meeting discussion. It adjusts clicks, click-to-order rate, and ROAS for the simulation only; it does not overwrite SKU inputs.",
        "scenario_case_detail": "Conservative applies -15% clicks, -15% click-to-order rate, and -10% ROAS. Base keeps current inputs. Upside applies +15% clicks, +15% click-to-order rate, and +10% ROAS.",
        "lock_plan": "Lock current plan",
        "unlock_plan": "Unlock plan",
        "plan_locked": "Current plan is locked. Unlock to refresh results from changed inputs.",
        "debug_details": "Debug Details",
        "debug_metric": "Metric",
        "debug_value": "Value",
        "debug_lock_status": "Plan locked",
        "debug_effective_roas": "Effective ROAS",
        "debug_multiplier_clicks": "Clicks multiplier",
        "debug_multiplier_cvr": "Conversion multiplier",
        "debug_multiplier_roas": "ROAS multiplier",
        "debug_target_gmv_gap": "Target GMV gap",
        "debug_target_profit_gap": "Target profit gap",
        "scenario_snapshot": "Plan Snapshot",
        "model_last_reviewed": "Model last reviewed",
        "calibration_note": "Default SKU assumptions use recent DE hit-product calibration.",
        "internal_logic_checklist": "Internal Logic Checklist",
        "internal_logic_intro": "Use this default-collapsed view for AM or data-team alignment. It explains how the model builds GMV, allocates channels, applies costs, and arrives at profit.",
        "internal_logic_context": "Current plan signals",
        "internal_logic_fbt_title": "FBT rule",
        "internal_logic_fbt_on": "FBT is on. {eligible} of {total} current SKUs use €0 logistics cost; {fallback} SKU(s) at or below €20 still use the fallback logistics cost.",
        "internal_logic_fbt_off": "FBT is off. All current SKUs use the manual logistics cost assumption.",
        "internal_logic_paid_title": "Paid growth rule",
        "internal_logic_paid_text": "Paid growth budget is active in {paid_phases} of {total_phases} phases at {take_rates}, using an Ads ROAS assumption of {ads_roas}. This creates incremental GMV that is allocated back into the two existing channels.",
        "internal_logic_channel_title": "Channel split rule",
        "internal_logic_channel_text": "The current SKU mix averages {avg_share} Store/Search share after content exposure, with the highest SKU at {max_share}. Affiliate Video GMV and Store/Search GMV remain the only two channels in the model.",
        "internal_logic_fee_title": "Platform fee rule",
        "internal_logic_fee_on": "The new-seller fee benefit is on, so weeks 1-{promo_weeks} use the 5% platform fee before reverting to the category default rate.",
        "internal_logic_fee_off": "The new-seller fee benefit is off, so the model uses the default category platform commission throughout the full plan.",
        "chart_read": "How to read",
        "read_weekly_chart": "Track whether GMV stays ahead of cost and profit remains positive.",
        "read_cumulative_chart": "Track whether cumulative profit recovers upfront investment.",
        "assumption_appendix": "Assumption Appendix",
        "reset_defaults": "Reset defaults",
        "reset_sku_assumptions": "Reset SKU assumptions",
        "reset_sku_assumptions_help": "Restore AOV, funnel assumptions, gross margin, and commission defaults for selected SKU categories without changing phase controls.",
        "reset_confirm": "Confirm reset",
        "reset_pending": "This will reset all inputs to the default planning setup. Click Confirm reset to continue.",
        "meeting_mode": "Focus view",
        "meeting_mode_help": "After generation, keep the page focused on the concise meeting storyline, headline metrics, and key charts.",
        "meeting_mode_sidebar_note": "Focus view is on. Detailed inputs are tucked away; turn it off to adjust assumptions.",
        "back_to_client_view": "Back to client view",
        "sku_count": "Number of SKUs",
        "promo": "New seller: apply first-60-day 5% platform fee",
        "promo_yes": "Apply first-60-day 5% platform fee",
        "promo_no": "No, use default category commission",
        "fulfillment": "Non-FBT customer order logistics cost €/order",
        "fulfillment_fbt_fallback": "Fallback customer order logistics cost €/order for SKUs at or below €20",
        "logistics_carrier_cost": "Carrier / last-mile cost €/order",
        "logistics_pick_pack_cost": "Pick & pack cost €/order",
        "logistics_return_allowance": "Return / failed delivery allowance €/order",
        "logistics_total": "Order logistics total",
        "logistics_detail_note": "{total} per order = {carrier} carrier + {pick_pack} pick & pack + {returns} return allowance.",
        "sample_shipping_cost": "Sample shipping cost €/sample",
        "sample_handling_cost": "Sample pack & handling €/sample",
        "sample_shipping_total": "Sample logistics total",
        "sample_shipping_detail_note": "{total} per sample = {shipping} shipping + {handling} pack & handling.",
        "fbt": "Use FBT free shipping",
        "fbt_yes": "Yes, set logistics cost to €0",
        "fbt_no": "No, use manual logistics cost",
        "fbt_help": "Planning assumption: when selected, customer orders for SKUs with AOV above €20 use €0 logistics cost; lower-AOV SKUs keep the manual order logistics cost. Sample shipping is controlled separately.",
        "fbt_active_all": "€0.00 effective under FBT",
        "fbt_active_mixed": "Mixed under FBT ({logistics} fallback for AOV ≤ €20)",
        "fbt_active_none": "{logistics} fallback still applies (no current SKU above €20)",
        "fbt_status": "FBT status",
        "effective_logistics": "Effective logistics cost",
        "fbt_status_eligible": "FBT active",
        "fbt_status_fallback": "Fallback logistics applies",
        "creator_commission": "Organic creator commission",
        "paid_creator_commission": "Paid-traffic creator commission",
        "organic_click_window": "Content sales window (weeks)",
        "ads_roas": "Ads ROAS assumption",
        "weeks_phase": "Weeks / phase",
        "phase_controls": "Phase Controls",
        "phase1": "Phase 1 - Cold Start",
        "phase2": "Phase 2 - Growth",
        "phase3": "Phase 3 - Scale",
        "phase1_objective": "Talking point: validate creator content, seed the first product videos, and build early conversion signals before scaling budget.",
        "phase2_objective": "Talking point: reduce sample intensity and start paid amplification, turning validated content into more scalable GMV.",
        "phase3_objective": "Talking point: scale winning content with higher paid acceleration while Store/Search and content-tail sales continue compounding.",
        "take_rate": "Paid growth budget (% of GMV)",
        "take_rate_help": "Internal take-rate planning view: the share of GMV reinvested as paid growth budget in this phase.",
        "samples_sku_week": "Samples / SKU / week",
        "sku_setup": "SKU Setup",
        "sku_caption": "Category and subcategory selection auto-load AOV, funnel assumptions, and creator-commission defaults. Electronics-linked first-level categories use 7% platform commission; all others use 9%.",
        "sku_name": "SKU name",
        "category": "Category",
        "subcategory": "Subcategory",
        "gross_margin": "Gross Margin (%)",
        "platform_commission": "Platform Commission",
        "avg_sample_cost": "Avg sample cost / unit",
        "sample_investment": "Sample Investment",
        "ads_investment": "Ads Investment",
        "benchmark_expander": "View / adjust category funnel assumptions",
        "benchmark_note": "Defaults come from recent DE category calibration. Adjust only when you want to override the planning baseline.",
        "videos_sample": "Videos / sample",
        "clicks_video": "Clicks / video",
        "click_order": "Click-to-order (%)",
        "shoptab_share": "Store/Search order share after content exposure (%)",
        "organic_commission_sku": "Organic creator commission (%)",
        "paid_commission_sku": "Paid-traffic creator commission (%)",
        "aov_help": "Average selling price per order for this subcategory. Current default is a planning input; we recommend aligning with your AM and using TikTok Shop data from similar categories or merchants.",
        "gross_margin_help": "Merchant gross margin before platform fee, creator commission, ads, logistics, and sample investment. Product cost is calculated as AOV x (1 - gross margin).",
        "videos_sample_help": "Estimated creator videos generated per sample sent. Example: 1.50 means 100 samples generate about 150 videos. Current value is a planning input; align with your AM using similar-category TikTok Shop data where available.",
        "clicks_video_help": "Estimated product-page clicks generated by each creator video during the content traffic tail period. Current value is a planning input; align with your AM using similar-category TikTok Shop data where available.",
        "click_order_help": "Estimated conversion from product click to order. Use AM-aligned TikTok Shop data from similar categories or merchants where available.",
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
        "charts": "Growth & Profit Path",
        "overall_weekly": "GMV, Cost & Profit Path",
        "cumulative_profit_trend": "Cumulative Payback Curve",
        "funnel_summary": "Content-to-order journey",
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
        "paid_gmv_increment": "Incremental GMV from paid growth",
        "shoptab_gmv": "Store/Search GMV",
        "phase_total_breakdown": "Phase Profit Bridge",
        "supporting_charts": "Business Drivers",
        "section_primary": "Core view",
        "section_secondary": "Supporting view",
        "growth_profit_path": "Growth & Profit Path",
        "executive_insight": "Executive Insight",
        "executive_insight_text": "{payback}. Growth is primarily driven by {channel}; {driver} is the current optimization priority. The plan delivers a {margin} profit margin.",
        "insight_payback_reached": "Cumulative payback is reached in {week}",
        "insight_payback_not_reached": "Cumulative payback is not reached within the plan",
        "model_updated": "Model updated",
        "live_model": "Live model",
        "product_console": "Growth Planning Console",
        "model_calculating": "Refreshing growth model...",
        "peak_gmv": "Peak GMV",
        "break_even_marker": "Positive weekly profit",
        "growth_engine": "Growth Engine",
        "growth_engine_subtitle": "How samples compound into creator content, demand, orders, and GMV.",
        "growth_engine_rate": "Step efficiency",
        "growth_engine_video_rate": "videos / sample",
        "growth_engine_click_rate": "clicks / video",
        "growth_engine_order_rate": "orders / click",
        "growth_engine_aov": "GMV / order",
        "growth_diagnostics": "Growth Diagnostics",
        "growth_diagnostics_subtitle": "Priority levers based on the current funnel and cost structure.",
        "diagnostic_priority": "Priority",
        "diagnostic_current": "Current signal",
        "diagnostic_action": "Recommended move",
        "diagnostic_good": "Healthy",
        "diagnostic_attention": "Watch",
        "diagnostic_high": "High priority",
        "diagnostic_profit_title": "Profitability pressure",
        "diagnostic_profit_action": "Improve margin, reduce logistics or paid acceleration before scaling.",
        "diagnostic_sample_title": "Sample efficiency",
        "diagnostic_sample_action": "Tighten sample quantity, sample cost, or SKU selection before expanding seeding.",
        "diagnostic_video_title": "Creator video yield",
        "diagnostic_video_action": "Improve creator matching, brief quality, and sample follow-up to lift videos per sample.",
        "diagnostic_click_title": "Content click power",
        "diagnostic_click_action": "Use stronger hooks, proof points, pricing cues, and creative testing to lift clicks per video.",
        "diagnostic_conversion_title": "Click-to-order conversion",
        "diagnostic_conversion_action": "Review PDP, price, voucher, reviews, shipping promise, and creator offer clarity.",
        "diagnostic_order_value_title": "Order value",
        "diagnostic_order_value_action": "Test bundles, multipacks, or hero SKU mix to increase GMV per order.",
        "diagnostic_logistics_title": "Order logistics drag",
        "diagnostic_logistics_action": "Review FBT eligibility, carrier cost, pick-pack cost, and return allowance.",
        "diagnostic_paid_title": "Paid-growth dependence",
        "diagnostic_paid_action": "Validate ROAS confidence and phase 2/3 budget readiness before treating upside as target.",
        "diagnostic_healthy_title": "Growth engine is balanced",
        "diagnostic_healthy_action": "Use the base plan as the discussion anchor and validate SKU-level assumptions with AM data.",
        "decision_focus": "Decision Focus",
        "decision_focus_subtitle": "Current-plan signals to guide the next growth discussion.",
        "focus_payback": "Payback quality",
        "focus_driver": "Primary driver",
        "focus_efficiency": "Efficiency signal",
        "focus_cost": "Cost pressure",
        "investment_split": "Investment Mix",
        "product_profile": "Product Profile",
        "hero_title": "{weeks}-week incubation plan for {skus} SKUs",
        "hero_subtitle": "Projected {gmv} GMV with {growth_investment} growth investment. Break-even: {break_even}.",
        "hero_gmv": "Projected GMV",
        "hero_investment": "Growth Investment",
        "hero_break_even": "Break-even",
        "chart_insight": "Chart Insight",
        "overall_chart_insight": "Week 1 GMV: {start_gmv}. Week {end_week} GMV: {end_gmv}. Final cumulative profit: {cum_profit}.",
        "phase_chart_insight": "{phase}: {gmv} GMV, {profit} profit, {investment} investment.",
        "client_narrative": "Plan Interpretation",
        "narrative_what": "What happens: The model estimates {gmv} GMV and {profit} total profit over {weeks} weeks.",
        "narrative_why": "Why it happens: The largest GMV source is {channel}, supported by {samples} samples and {videos} creator videos.",
        "narrative_next": "What to do next: Focus the next discussion on {driver}, the largest cost driver, and align funnel inputs with your AM using TikTok Shop data from similar categories or merchants.",
        "health_check": "Planning Notes",
        "risk_review": "Planning Notes & Risk Checks",
        "risk_review_intro": "These checks are hidden by default for a cleaner customer view. Use them to pressure-test assumptions before treating the result as a target.",
        "health_ok": "No major assumption risk detected under the current setup.",
        "health_take_rate": "Paid growth budget x ROAS is high in at least one phase. Check whether the implied incremental GMV from paid growth is realistic.",
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
        "export_materials_note": "Use these files for meeting follow-up, internal alignment, or sharing a concise customer-ready plan.",
        "export_summary_desc": "Raw meeting summary for internal tracking.",
        "export_html_desc": "Readable recap for follow-up emails.",
        "export_one_pager_desc": "Concise customer-facing one-pager.",
        "export_detail_desc": "Full PDF with assumptions appendix.",
        "generated_on": "Generated on",
        "plan_length": "Plan length",
        "sku_count_meta": "SKU count",
        "meeting_notes": "Meeting Notes",
        "brand_name_help": "Recommended: add the brand name so exported PDF/CSV files look customized for the client.",
        "model_version": "Model version",
        "meeting_header": "Brand Growth Simulation",
        "brand_name": "Brand name",
        "scenario_name": "Scenario name",
        "scenario_name_help": "Optional. Useful when comparing several versions, such as Standard Launch or Scale Plan.",
        "meeting_date": "Meeting date",
        "am_name": "AM name",
        "key_recommendation": "Key recommendation",
        "key_recommendation_default": "Align funnel assumptions with the AM, then use this plan to agree sample volume, paid growth budget, and next milestone.",
        "assumption_status": "Assumption status",
        "benchmark_input": "Planning input",
        "am_aligned_input": "AM-aligned input",
        "merchant_confirmed_input": "Merchant-confirmed input",
        "commercial_takeaways": "Commercial Takeaways",
        "business_readout": "Business Readout",
        "business_readout_profit": "Profit story",
        "business_readout_growth": "Growth engine",
        "business_readout_payback": "Payback path",
        "business_readout_profit_positive": "The plan is profitable under the current assumptions; the largest margin lever is {driver}.",
        "business_readout_profit_negative": "The plan is not yet profitable under the current assumptions; focus first on {driver}, AOV, margin, and commission structure.",
        "business_readout_growth_text": "{channel} is the main GMV engine, supported by {samples} samples and {videos} creator videos.",
        "business_readout_payback_text": "Cumulative break-even: {break_even}. Sample efficiency: {sample_roi}x GMV per sample cost.",
        "diagnosis_summary": "Diagnosis Summary",
        "diagnosis_profitable": "This plan is commercially positive under the current assumptions. The main watch-out is {driver}, while sample efficiency is {sample_roi}x GMV per sample cost.",
        "diagnosis_negative": "This plan is not yet profitable under the current assumptions. The main unlock is improving {driver}, increasing AOV/margin, or tightening paid growth before scaling.",
        "diagnosis_sample_strong": "The plan is sample-efficient, but margin still depends on {driver}. Keep sample quality high and validate SKU-level conversion before increasing paid growth.",
        "diagnosis_ads_heavy": "Paid growth contributes meaningfully to GMV. Review ROAS confidence and phase 2/3 budget readiness before using this as a target.",
        "target_comparison": "Target Comparison",
        "target_met": "Target reached",
        "target_gap": "Gap to target",
        "target_not_set": "No target set",
        "target_gmv_gap_text": "Target GMV gap: {gap}.",
        "target_profit_gap_text": "Target profit gap: {gap}.",
        "key_assumptions": "Key Assumptions",
        "assumption_phase_plan": "Phase plan",
        "assumption_phase_plan_value": "{weeks} weeks per phase; samples per SKU/week: {samples}; paid growth budget: {take_rates}.",
        "assumption_operating": "Operating setup",
        "assumption_operating_value": "{skus} SKUs; order logistics {logistics}; sample shipping {sample_shipping}; content sales window {organic_window} weeks.",
        "assumption_growth": "Growth setup",
        "assumption_growth_value": "Ads ROAS {ads_roas}; new seller platform-fee benefit: {promo}; FBT free shipping: {fbt}.",
        "yes": "Yes",
        "no": "No",
        "next_actions": "Recommended Next Steps",
        "action_group_validate": "Validate",
        "action_group_optimize": "Optimize",
        "action_group_scale": "Scale",
        "action_expand_samples": "Sample ROI is strong. Consider expanding the creator sample pool while keeping SKU-level conversion assumptions aligned with AM data.",
        "action_fix_profit": "Profit is negative under the current setup. Revisit the largest cost driver, SKU gross margin, and commission structure before scaling budget.",
        "action_scale_ads": "Paid growth is contributing meaningful GMV. Consider preparing Phase 2/3 ad budget scenarios around the current ROAS assumption.",
        "action_strengthen_store": "Store/Search contribution is material. Strengthen listing quality, product detail pages, and search readiness so content traffic can convert without extra creator commission.",
        "action_align_inputs": "Before using this as a target, align AOV, videos per sample, clicks per video, and click-to-order rate with your AM using similar TikTok Shop category or merchant data.",
        "action_default": "Use this simulation to agree the sample plan, paid growth budget, and next milestone before moving into execution.",
        "action_no_immediate": "No priority action in this lane under the current setup.",
        "forecast_range": "Forecast Range",
        "forecast_range_prompt": "! Forecast range available",
        "conservative_case": "Conservative",
        "base_case": "Base",
        "upside_case": "Upside",
        "forecast_range_note": "Range is a planning sensitivity around the current funnel assumptions. Planning inputs use a wider range; AM-aligned or merchant-confirmed inputs use a narrower range.",
        "investment_required": "Investment required",
        "expected_gmv": "Expected GMV",
        "payback_timing": "Payback timing",
        "main_upside_lever": "Main upside lever",
        "main_risk": "Main risk",
        "main_risk_text": "{driver} is the largest cost driver; validate this assumption before treating the forecast as a target.",
        "cost_explanation": "Cost Explanation",
        "cost_explanation_text": "Profit is mainly shaped by {driver}, which accounts for {share} of total cost. Sample investment is {sample_share} and ads investment is {ads_share} of total cost, so the biggest margin lever is not always the visible growth budget.",
        "planning_disclaimer": "For planning use only. Align key inputs with your AM before using this as a target.",
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
        "cost_cogs": "Product Cost",
        "cost_platform_fee": "Platform fee",
        "cost_creator_commission": "Creator Sales Commission",
        "cost_fulfillment": "Logistics",
        "cost_samples": "Sample investment",
        "cost_ads": "Ads investment",
        "phase_objective": "Phase talking point",
        "phase_strategy": "Phase Strategy",
        "phase_strategy_text": "The plan starts with creator content validation, then shifts into paid amplification, and finally scales winning content while Store/Search demand continues to compound.",
        "pdf_proposal_title": "Growth Plan Proposal",
        "benchmark_info": "Data Notes",
        "benchmark_info_text": "Current AOV, video, click, conversion, Store/Search share, and creator-commission defaults are planning inputs calibrated from recent DE hit-product data where available. We still recommend aligning critical assumptions with your AM and similar TikTok Shop category benchmarks before using the plan as a target.",
        "model_assumptions": "Model Logic",
        "model_logic_intro": "The model follows a SKU-level content commerce funnel, then layers paid acceleration, channel mix, and cost structure on top.",
        "model_logic_1_title": "1. Samples create creator content",
        "model_logic_1_body": "Each phase defines samples per SKU per week. For every SKU, samples are converted into new creator videos using the selected subcategory's videos-per-sample assumption.",
        "model_logic_1_formula": "Samples x Videos per sample = New creator videos",
        "model_logic_2_title": "2. Videos keep contributing after the posting week",
        "model_logic_2_body": "Creator videos are not treated as one-week assets. They remain active across the content traffic tail period, so earlier videos can keep generating clicks and orders in later weeks.",
        "model_logic_2_formula": "Active videos = current-week videos + videos still inside the traffic-tail window",
        "model_logic_3_title": "3. Content traffic becomes organic GMV",
        "model_logic_3_body": "Active videos generate product clicks. Clicks convert into orders through the click-to-order rate, and orders convert into GMV through AOV.",
        "model_logic_3_formula": "Active videos x Clicks per video x Click-to-order rate x AOV = Organic GMV",
        "model_logic_4_title": "4. Organic GMV is split by channel",
        "model_logic_4_body": "Affiliate Video GMV carries the organic creator commission. Store/Search GMV represents content-influenced demand that converts through store, search, mall, or ShopTab and does not carry creator commission.",
        "model_logic_4_formula": "Organic GMV = Affiliate Video GMV + Store/Search GMV",
        "model_logic_5_title": "5. Paid growth scales validated demand",
        "model_logic_5_body": "Phase 2 and Phase 3 can apply paid acceleration as a percentage of GMV. The model uses Ads ROAS to estimate the incremental GMV added by that budget, then allocates that increment back into Affiliate Video GMV and Store/Search GMV rather than treating it as a standalone channel.",
        "model_logic_5_formula": "Incremental paid GMV is estimated from paid budget share x Ads ROAS",
        "model_logic_6_title": "6. Cost and profit are calculated from the full operating model",
        "model_logic_6_body": "Product cost is derived from AOV and gross margin. Sample investment uses product cost plus sample shipping. Profit subtracts product cost, platform fee, creator commission, customer order logistics, samples, and ads from GMV.",
        "model_logic_6_formula": "Profit = GMV - Product Cost - Platform Fee - Creator Commission - Logistics - Samples - Ads",
        "model_assumptions_text": "SKU-level model: samples create creator videos, videos generate long-tail clicks and orders, organic GMV splits into Affiliate Video and Store/Search, paid acceleration adds incremental GMV, and profit is calculated after product cost, platform fee, creator commission, customer order logistics, sample investment, and ads.",
        "download_customer_summary": "Summary CSV",
        "download_meeting_html": "Meeting HTML",
        "download_one_pager_pdf": "One-page PDF",
        "download_meeting_pdf": "Detail PDF",
        "view_details": "View detailed tables",
        "channel_mix": "GMV Channel Mix",
    },
    "zh": {
        "language": "语言",
        "title": "TikTok Shop Growth Visualizer",
        "caption": "面向客户会议的 SKU 寄样、达人视频、点击、GMV、成本和利润规划模拟器",
        "global_inputs": "全局输入",
        "plan_setup": "计划设置",
        "step1_title": "第一步 · 确认上架 SKU 范围",
        "step1_body": "请先填写预计上架的 SKU 数量。确认后，系统会围绕这个产品组合展开阶段计划、SKU 设置和预测看板。",
        "expected_listing_skus": "预计上架 SKU 数量",
        "continue_setup": "继续设置计划",
        "setup_ready": "SKU 范围已确认。您可以在左侧调整假设，并在下方设置 SKU 明细。",
        "plan_preview": "计划预览",
        "plan_preview_text": "本次模拟将覆盖 {skus} 个 SKU、共 {weeks} 周。每 SKU 每周寄样：{samples}；付费增长预算占比：{take_rates}；内容出单窗口：{organic_window} 周；广告 ROAS：{ads_roas}。",
        "assumption_quality": "假设质量",
        "assumption_quality_text": "当前状态：{status}。Planning 输入适合做沙盘讨论；如需将结果作为业务目标，建议优先使用已和 AM 对齐或商家确认的输入。",
        "cost_assumptions": "成本假设",
        "growth_levers": "增长杠杆",
        "target_setup": "目标设置",
        "target_gmv": "目标 GMV (€)",
        "target_profit": "目标利润 (€)",
        "target_gmv_help": "可选项。如果当前方案没有 GMV 目标，保持 0 即可。",
        "target_profit_help": "可选项。如果当前方案没有利润目标，保持 0 即可。",
        "scenario_case": "场景敏感度",
        "scenario_conservative": "保守",
        "scenario_base": "基准",
        "scenario_upside": "乐观",
        "scenario_case_help": "会议中快速讨论不同结果区间用。仅在模拟中调整点击、点击到下单转化率和 ROAS，不覆盖 SKU 输入。",
        "scenario_case_detail": "保守：点击 -15%、点击到下单转化率 -15%、ROAS -10%。基准：保持当前输入。乐观：点击 +15%、点击到下单转化率 +15%、ROAS +10%。",
        "lock_plan": "锁定当前方案",
        "unlock_plan": "解锁方案",
        "plan_locked": "当前方案已锁定。如需根据新输入刷新结果，请先解锁。",
        "debug_details": "Debug Details",
        "debug_metric": "指标",
        "debug_value": "当前值",
        "debug_lock_status": "方案是否锁定",
        "debug_effective_roas": "有效 ROAS",
        "debug_multiplier_clicks": "点击 multiplier",
        "debug_multiplier_cvr": "转化 multiplier",
        "debug_multiplier_roas": "ROAS multiplier",
        "debug_target_gmv_gap": "目标 GMV 差距",
        "debug_target_profit_gap": "目标利润差距",
        "scenario_snapshot": "计划快照",
        "model_last_reviewed": "模型最近校准",
        "calibration_note": "当前 SKU 默认值优先使用最新 DE hit-product 校准口径。",
        "chart_read": "怎么看",
        "read_weekly_chart": "看 GMV 是否持续跑赢成本、利润是否保持为正。",
        "read_cumulative_chart": "看累计利润是否覆盖前期投入。",
        "assumption_appendix": "假设附录",
        "reset_defaults": "恢复默认值",
        "reset_sku_assumptions": "仅恢复 SKU 假设",
        "reset_sku_assumptions_help": "只恢复当前 SKU 类目下的 AOV、漏斗假设、毛利和佣金默认值，不改变阶段计划。",
        "reset_confirm": "确认恢复默认值",
        "reset_pending": "此操作会将所有输入恢复到默认沙盘设置。如需继续，请点击确认恢复默认值。",
        "meeting_mode": "精简展示",
        "meeting_mode_help": "生成结果后，页面会聚焦会议讲述路径、核心指标和关键图表。",
        "meeting_mode_sidebar_note": "精简展示已开启。详细输入已收起；如需调整假设，请关闭该模式。",
        "back_to_client_view": "回到客户展示视角",
        "sku_count": "SKU 数量",
        "promo": "是否为新商家：适用前约60天平台费 5%",
        "promo_yes": "适用前约60天平台费 5%",
        "promo_no": "否，使用默认类目佣金",
        "fulfillment": "非 FBT 客户订单物流成本 €/单",
        "fulfillment_fbt_fallback": "AOV 不高于 €20 的 SKU 兜底客户订单物流成本 €/单",
        "logistics_carrier_cost": "承运商/尾程成本 €/单",
        "logistics_pick_pack_cost": "拣货打包成本 €/单",
        "logistics_return_allowance": "退货/派送失败预留 €/单",
        "logistics_total": "订单物流合计",
        "logistics_detail_note": "每单 {total} = 承运商 {carrier} + 拣货打包 {pick_pack} + 退货预留 {returns}。",
        "sample_shipping_cost": "样品寄送成本 €/个样品",
        "sample_handling_cost": "样品包装处理 €/个样品",
        "sample_shipping_total": "样品物流合计",
        "sample_shipping_detail_note": "每个样品 {total} = 寄送 {shipping} + 包装处理 {handling}。",
        "fbt": "使用 FBT 包邮",
        "fbt_yes": "是，物流成本按 €0 计算",
        "fbt_no": "否，使用手动物流成本",
        "fbt_help": "沙盘假设：勾选后，AOV 高于 €20 的 SKU 客户订单物流成本按 €0 计算；AOV 不高于 €20 的 SKU 仍使用手动订单物流成本。样品寄送成本单独控制。",
        "fbt_active_all": "当前有效物流成本为 €0.00（FBT 生效）",
        "fbt_active_mixed": "FBT 部分生效（AOV 不高于 €20 的 SKU 仍使用 {logistics} 兜底）",
        "fbt_active_none": "当前仍使用 {logistics} 兜底物流成本（没有 SKU 高于 €20）",
        "fbt_status": "FBT 状态",
        "effective_logistics": "有效物流成本",
        "fbt_status_eligible": "FBT 生效",
        "fbt_status_fallback": "仍使用兜底物流",
        "creator_commission": "自然流达人佣金",
        "paid_creator_commission": "广告流达人佣金",
        "organic_click_window": "内容出单窗口（周）",
        "ads_roas": "广告 ROAS 假设",
        "weeks_phase": "每阶段周数",
        "phase_controls": "阶段控制",
        "phase1": "阶段 1 - 冷启动",
        "phase2": "阶段 2 - 增长",
        "phase3": "阶段 3 - 放量",
        "phase1_objective": "讲解词：这一阶段重点不是立刻放大预算，而是验证达人内容、沉淀第一批商品视频，并建立早期转化信号。",
        "phase2_objective": "讲解词：这一阶段降低寄样强度，开始用付费加热放大已验证内容，把内容能力转化为可规模化的 GMV。",
        "phase3_objective": "讲解词：这一阶段放大优质内容和付费加热，同时让店铺/Search 与内容长尾出单继续累积。",
        "take_rate": "付费增长预算占 GMV (%)",
        "take_rate_help": "内部 take rate 规划视角：该阶段将 GMV 的多少比例作为付费增长预算重新投入。",
        "samples_sku_week": "每个 SKU 每周寄样数",
        "sku_setup": "SKU 设置",
        "sku_caption": "选择类目/子类目后会自动加载 AOV、漏斗假设和达人佣金默认值。一级类目里与电子产品相关的类目平台佣金为 7%，其余类目为 9%。",
        "sku_name": "SKU 名称",
        "category": "类目",
        "subcategory": "子类目",
        "gross_margin": "毛利率 (%)",
        "platform_commission": "平台佣金",
        "avg_sample_cost": "平均样品成本 / 件",
        "sample_investment": "样品投入",
        "ads_investment": "广告投入",
        "benchmark_expander": "查看 / 调整类目漏斗假设",
        "benchmark_note": "默认值优先来自最新 DE 类目校准；仅在需要覆盖当前 planning 基线时再调整。",
        "videos_sample": "每个样品产出视频数",
        "clicks_video": "每条视频商品点击数",
        "click_order": "点击到下单转化率 (%)",
        "shoptab_share": "内容种草后的店铺/Search 出单占比 (%)",
        "organic_commission_sku": "自然流达人佣金 (%)",
        "paid_commission_sku": "广告流达人佣金 (%)",
        "aov_help": "该 subcategory 的平均成交客单价。当前默认值是 planning 输入，建议和您的 AM 对齐，参考 TikTok Shop 上类似行业或类似商家的数据进行输入。",
        "gross_margin_help": "商家毛利率，不包含平台佣金、达人佣金、广告、物流和寄样投入。商品成本会按 AOV x (1 - 毛利率) 自动计算。",
        "videos_sample_help": "每寄出 1 个样品预计产生的达人视频数。例如 1.50 表示 100 个样品约产生 150 条视频。当前为 planning 输入，建议和您的 AM 对齐，参考 TikTok Shop 上类似行业或类似商家的数据进行输入。",
        "clicks_video_help": "每条达人视频在内容流量长尾周期内预计带来的商品页点击数。当前为 planning 输入，建议和您的 AM 对齐，参考 TikTok Shop 上类似行业或类似商家的数据进行输入。",
        "click_order_help": "商品页点击到下单的转化率。建议和您的 AM 对齐，优先参考 TikTok Shop 上类似行业或类似商家的数据。",
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
        "charts": "增长与利润路径",
        "overall_weekly": "GMV、成本与利润路径",
        "cumulative_profit_trend": "累计回本曲线",
        "funnel_summary": "内容到订单路径",
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
        "paid_gmv_increment": "付费加热带来的增量 GMV",
        "shoptab_gmv": "店铺/Search GMV",
        "phase_total_breakdown": "阶段利润桥",
        "supporting_charts": "业务驱动因素",
        "section_primary": "核心视图",
        "section_secondary": "辅助视图",
        "growth_profit_path": "增长与利润路径",
        "executive_insight": "核心商业结论",
        "executive_insight_text": "{payback}。当前增长主要由 {channel} 驱动；{driver} 是优先优化项。方案预计实现 {margin} 的利润率。",
        "insight_payback_reached": "方案在 {week} 实现累计回本",
        "insight_payback_not_reached": "方案周期内尚未实现累计回本",
        "model_updated": "模型已更新",
        "live_model": "实时模型",
        "product_console": "增长规划控制台",
        "model_calculating": "正在刷新增长模型...",
        "peak_gmv": "GMV 峰值",
        "break_even_marker": "单周利润转正",
        "growth_engine": "增长引擎",
        "growth_engine_subtitle": "样品如何逐步转化为达人内容、需求、订单和 GMV。",
        "growth_engine_rate": "阶段效率",
        "growth_engine_video_rate": "视频 / 样品",
        "growth_engine_click_rate": "点击 / 视频",
        "growth_engine_order_rate": "订单 / 点击",
        "growth_engine_aov": "GMV / 订单",
        "growth_diagnostics": "增长诊断",
        "growth_diagnostics_subtitle": "基于当前漏斗和成本结构，自动识别优先优化杠杆。",
        "diagnostic_priority": "优先级",
        "diagnostic_current": "当前信号",
        "diagnostic_action": "建议动作",
        "diagnostic_good": "健康",
        "diagnostic_attention": "关注",
        "diagnostic_high": "高优先级",
        "diagnostic_profit_title": "利润压力",
        "diagnostic_profit_action": "放大前优先优化毛利、物流成本或付费加热强度。",
        "diagnostic_sample_title": "样品效率",
        "diagnostic_sample_action": "扩大寄样前，先收紧样品数量、样品成本或 SKU 选择。",
        "diagnostic_video_title": "达人视频产出",
        "diagnostic_video_action": "优化达人匹配、brief 质量和样品跟进，提升每个样品带来的视频数。",
        "diagnostic_click_title": "内容点击能力",
        "diagnostic_click_action": "通过更强 hook、卖点、价格信息和素材测试提升每条视频点击。",
        "diagnostic_conversion_title": "点击到下单转化",
        "diagnostic_conversion_action": "检查 PDP、价格、券、评价、物流承诺和达人权益表达。",
        "diagnostic_order_value_title": "客单价",
        "diagnostic_order_value_action": "测试组合装、多件装或 hero SKU 组合，提高每单 GMV。",
        "diagnostic_logistics_title": "订单物流拖累",
        "diagnostic_logistics_action": "复核 FBT 资格、承运成本、拣配成本和退货/失败配送预留。",
        "diagnostic_paid_title": "付费增长依赖",
        "diagnostic_paid_action": "在把乐观结果作为目标前，先验证 ROAS 可信度和 Phase 2/3 预算准备。",
        "diagnostic_healthy_title": "增长引擎较均衡",
        "diagnostic_healthy_action": "可以用基准方案作为讨论锚点，并用 AM 数据继续验证 SKU level 假设。",
        "decision_focus": "决策焦点",
        "decision_focus_subtitle": "围绕当前方案，提炼下一轮增长讨论的关键判断。",
        "focus_payback": "回本质量",
        "focus_driver": "主要驱动",
        "focus_efficiency": "效率信号",
        "focus_cost": "成本压力",
        "investment_split": "投入结构",
        "product_profile": "产品组合",
        "hero_title": "{weeks} 周、{skus} 个 SKU 的孵化计划",
        "hero_subtitle": "预计产生 {gmv} GMV，需要 {growth_investment} 增长投入。Break-even：{break_even}。",
        "hero_gmv": "预测 GMV",
        "hero_investment": "增长投入",
        "hero_break_even": "Break-even",
        "chart_insight": "图表解读",
        "overall_chart_insight": "第 1 周 GMV：{start_gmv}；第 {end_week} 周 GMV：{end_gmv}；累计利润：{cum_profit}。",
        "phase_chart_insight": "{phase}：{gmv} GMV，利润 {profit}，投入 {investment}。",
        "client_narrative": "计划解读",
        "narrative_what": "结果：模型预计在 {weeks} 周内产生 {gmv} GMV，总利润为 {profit}。",
        "narrative_why": "原因：最大的 GMV 来源是 {channel}，同时由 {samples} 个样品和 {videos} 条达人视频支撑。",
        "narrative_next": "下一步：建议重点讨论 {driver} 这个最大成本项，并和您的 AM 对齐，参考 TikTok Shop 上类似行业或类似商家的数据进行输入。",
        "health_check": "计划提示",
        "risk_review": "计划提示与风险检查",
        "risk_review_intro": "这些检查默认收起，以保持客户展示页面简洁。建议在把结果作为目标前，用它们复核关键假设。",
        "health_ok": "当前设置下没有发现明显假设风险。",
        "health_take_rate": "至少一个阶段的付费增长预算占比 x ROAS 偏高，建议确认广告带来的 GMV 增量是否合理。",
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
        "export_materials_note": "这些文件可用于会后跟进、内部对齐，或分享简洁的客户版计划。",
        "export_summary_desc": "用于内部跟进的会议总结原始表。",
        "export_html_desc": "适合会后邮件分享的总结页面。",
        "export_one_pager_desc": "简洁的客户展示一页版。",
        "export_detail_desc": "包含假设附录的完整 PDF。",
        "generated_on": "生成时间",
        "plan_length": "计划周期",
        "sku_count_meta": "SKU 数量",
        "meeting_notes": "会议信息",
        "brand_name_help": "建议填写品牌名称，这样导出的 PDF/CSV 文件会更像为客户定制的材料。",
        "model_version": "模型版本",
        "meeting_header": "品牌增长模拟",
        "brand_name": "品牌名称",
        "scenario_name": "方案名称",
        "scenario_name_help": "可选项。适合区分多个版本，例如标准启动方案、放量方案或保守方案。",
        "meeting_date": "会议日期",
        "am_name": "AM 名称",
        "key_recommendation": "关键建议",
        "key_recommendation_default": "建议先和 AM 对齐漏斗假设，再用该计划确认寄样数量、付费增长预算和下一阶段里程碑。",
        "assumption_status": "假设状态",
        "benchmark_input": "Planning 输入",
        "am_aligned_input": "已和 AM 对齐",
        "merchant_confirmed_input": "商家已确认",
        "commercial_takeaways": "商业结论",
        "business_readout": "商业解读",
        "business_readout_profit": "利润逻辑",
        "business_readout_growth": "增长来源",
        "business_readout_payback": "回本路径",
        "business_readout_profit_positive": "按当前假设，该方案可以盈利；最大的利润杠杆是 {driver}。",
        "business_readout_profit_negative": "按当前假设，该方案尚未盈利；建议优先复核 {driver}、AOV、毛利和佣金结构。",
        "business_readout_growth_text": "{channel} 是主要 GMV 来源，由 {samples} 个样品和 {videos} 条达人视频支撑。",
        "business_readout_payback_text": "累计 Break-even：{break_even}。样品效率：样品成本的 {sample_roi}x GMV。",
        "diagnosis_summary": "自动诊断摘要",
        "diagnosis_profitable": "按当前假设，该方案具备正向商业回报。主要关注点是 {driver}，当前样品效率为样品成本的 {sample_roi}x GMV。",
        "diagnosis_negative": "按当前假设，该方案尚未盈利。主要优化方向是改善 {driver}，提升 AOV/毛利，或在放大前收紧付费增长预算。",
        "diagnosis_sample_strong": "该方案样品效率较高，但利润仍受 {driver} 影响。建议保持样品质量，并在放大付费增长前验证 SKU level 转化。",
        "diagnosis_ads_heavy": "付费增长对 GMV 贡献明显。建议在把结果作为目标前，确认 ROAS 可信度和 Phase 2/3 的预算准备。",
        "internal_logic_checklist": "内部逻辑清单",
        "internal_logic_intro": "该模块默认收起，适合和 AM 或数据团队对齐口径时使用。它会说明模型如何生成 GMV、拆分渠道、计入成本，并最终得出利润。",
        "internal_logic_context": "当前方案信号",
        "internal_logic_fbt_title": "FBT 规则",
        "internal_logic_fbt_on": "当前已开启 FBT。{total} 个 SKU 中有 {eligible} 个享受 €0 物流成本；仍有 {fallback} 个 AOV 不高于 €20 的 SKU 继续使用兜底物流成本。",
        "internal_logic_fbt_off": "当前未开启 FBT，因此所有 SKU 都使用手动填写的物流成本假设。",
        "internal_logic_paid_title": "付费增长规则",
        "internal_logic_paid_text": "当前 {total_phases} 个阶段中有 {paid_phases} 个启用了付费增长预算，占比分别为 {take_rates}；广告 ROAS 假设为 {ads_roas}。这部分带来的是增量 GMV，并会分配回现有两条渠道，而不是形成第三渠道。",
        "internal_logic_channel_title": "渠道拆分规则",
        "internal_logic_channel_text": "当前 SKU 组合的平均店铺/Search 占比为 {avg_share}，其中最高 SKU 为 {max_share}。模型里仍然只有达人视频 GMV 和店铺/Search GMV 两条渠道。",
        "internal_logic_fee_title": "平台费规则",
        "internal_logic_fee_on": "当前已开启新商家平台费优惠，因此第 1-{promo_weeks} 周使用 5% 平台费，之后恢复到类目默认平台费率。",
        "internal_logic_fee_off": "当前未开启新商家平台费优惠，因此整个周期都使用默认类目平台费率。",
        "target_comparison": "目标对比",
        "target_met": "已达到目标",
        "target_gap": "距离目标",
        "target_not_set": "未设置目标",
        "target_gmv_gap_text": "距离目标 GMV：{gap}。",
        "target_profit_gap_text": "距离目标利润：{gap}。",
        "key_assumptions": "关键假设摘要",
        "assumption_phase_plan": "阶段计划",
        "assumption_phase_plan_value": "每阶段 {weeks} 周；每 SKU 每周寄样：{samples}；付费增长预算占比：{take_rates}。",
        "assumption_operating": "运营设置",
        "assumption_operating_value": "{skus} 个 SKU；订单物流 {logistics}；样品寄送 {sample_shipping}；内容出单窗口 {organic_window} 周。",
        "assumption_growth": "增长设置",
        "assumption_growth_value": "广告 ROAS {ads_roas}；新商家平台费优惠：{promo}；FBT 包邮：{fbt}。",
        "yes": "是",
        "no": "否",
        "next_actions": "建议下一步行动",
        "action_group_validate": "验证",
        "action_group_optimize": "优化",
        "action_group_scale": "放大",
        "action_expand_samples": "样品 ROI 表现较强。可以考虑扩大达人寄样池，同时继续用 AM/类似行业数据校准 SKU level 的转化假设。",
        "action_fix_profit": "当前设置下利润为负。建议在扩大预算前，优先复核最大成本项、SKU 毛利率和达人佣金结构。",
        "action_scale_ads": "付费增长对 GMV 有明显贡献。建议围绕当前 ROAS 假设，提前准备 Phase 2/3 的广告预算场景。",
        "action_strengthen_store": "店铺/Search 贡献较明显。建议强化 listing、商品详情页和搜索承接，让内容种草后的流量尽量以无达人佣金方式成交。",
        "action_align_inputs": "在把结果作为业务目标前，建议和您的 AM 对齐 AOV、每样品视频数、每视频点击数和点击到下单转化率，并参考 TikTok Shop 类似行业或类似商家数据。",
        "action_default": "建议用该模拟结果确认寄样计划、付费增长预算和下一阶段里程碑，再进入执行。",
        "action_no_immediate": "当前设置下，该方向暂无优先动作。",
        "forecast_range": "结果可信区间",
        "forecast_range_prompt": "! 可查看结果可信区间",
        "conservative_case": "保守",
        "base_case": "基准",
        "upside_case": "乐观",
        "forecast_range_note": "该区间是基于当前漏斗假设的敏感性测算。Planning 输入使用更宽区间；已和 AM 对齐或商家确认的输入使用更窄区间。",
        "investment_required": "所需投入",
        "expected_gmv": "预计 GMV",
        "payback_timing": "回本时间",
        "main_upside_lever": "主要增长杠杆",
        "main_risk": "主要风险",
        "main_risk_text": "{driver} 是当前最大的成本项；建议在把结果作为目标前，先确认该假设是否合理。",
        "cost_explanation": "成本解释",
        "cost_explanation_text": "当前利润主要受 {driver} 影响，该项占总成本 {share}。样品投入占总成本 {sample_share}，广告投入占总成本 {ads_share}，因此最大的利润杠杆不一定是最显眼的增长预算。",
        "planning_disclaimer": "本工具仅用于规划讨论。建议先和您的 AM 对齐关键输入，再作为业务目标参考。",
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
        "cost_cogs": "商品成本",
        "cost_platform_fee": "平台费",
        "cost_creator_commission": "达人销售佣金",
        "cost_fulfillment": "物流成本",
        "cost_samples": "样品投入",
        "cost_ads": "广告投入",
        "phase_objective": "阶段讲解词",
        "phase_strategy": "阶段策略",
        "phase_strategy_text": "计划先验证达人内容，再进入付费加热，最后放大已验证内容；同时店铺/Search 的承接会随着内容沉淀持续复利。",
        "pdf_proposal_title": "增长方案提案",
        "benchmark_info": "数据说明",
        "benchmark_info_text": "当前 AOV、视频、点击、转化率、店铺/Search 占比和达人佣金默认值，已优先参考最新 DE hit-product 数据做 planning 校准；若缺少足够样本，则会回退到一级类目口径。正式作为业务目标前，仍建议和您的 AM 对齐关键输入。",
        "model_assumptions": "模型逻辑",
        "model_logic_intro": "模型以 SKU level 的内容电商漏斗为基础，再叠加付费加热、渠道拆分和完整成本结构。",
        "model_logic_1_title": "1. 样品产生达人内容",
        "model_logic_1_body": "每个阶段会定义每个 SKU 每周寄出多少样品。每个 SKU 会根据所选 subcategory 的每样品视频数假设，计算新增达人视频。",
        "model_logic_1_formula": "样品数 x 每样品视频数 = 新增达人视频",
        "model_logic_2_title": "2. 视频不是只在当周出单",
        "model_logic_2_body": "达人视频不会被视为一次性流量。视频会在内容流量长尾周期内持续贡献点击和订单，因此前几周的视频会继续影响后续周的成交。",
        "model_logic_2_formula": "活跃视频 = 当周新增视频 + 仍在长尾周期内的视频",
        "model_logic_3_title": "3. 内容流量转化为自然 GMV",
        "model_logic_3_body": "活跃视频带来商品点击，点击通过点击到下单转化率形成订单，订单再通过 AOV 转化为 GMV。",
        "model_logic_3_formula": "活跃视频 x 每视频点击数 x 点击到下单转化率 x AOV = 自然 GMV",
        "model_logic_4_title": "4. 自然 GMV 拆成达人视频和店铺/Search",
        "model_logic_4_body": "达人视频 GMV 需要支付自然流达人佣金。店铺/Search GMV 代表被内容种草后，通过店铺、搜索、商城或 ShopTab 成交的需求，这部分不计算达人佣金。",
        "model_logic_4_formula": "自然 GMV = 达人视频 GMV + 店铺/Search GMV",
        "model_logic_5_title": "5. 付费加热放大已验证需求",
        "model_logic_5_body": "第二、第三阶段可以设置付费增长预算占 GMV 的比例。模型会结合广告 ROAS，估算该预算带来的增量 GMV，再把这部分增量拆回达人视频 GMV 和店铺/Search GMV，而不是把它视为独立渠道。",
        "model_logic_5_formula": "付费增量 GMV 由付费预算占比 x 广告 ROAS 推算",
        "model_logic_6_title": "6. 成本和利润来自完整经营模型",
        "model_logic_6_body": "商品成本由 AOV 和毛利率反推；样品投入由商品成本加样品寄送成本构成；利润会扣除商品成本、平台费、达人佣金、客户订单物流、样品投入和广告投入。",
        "model_logic_6_formula": "利润 = GMV - 商品成本 - 平台费 - 达人佣金 - 物流 - 样品投入 - 广告投入",
        "model_assumptions_text": "SKU level 模型：样品产生达人视频，视频在长尾周期内持续带来点击和订单，自然 GMV 拆分为达人视频与店铺/Search，付费加热带来增量 GMV，最终利润扣除商品成本、平台费、达人佣金、客户订单物流、样品投入和广告投入。",
        "download_customer_summary": "总结 CSV",
        "download_meeting_html": "会议 HTML",
        "download_one_pager_pdf": "一页 PDF",
        "download_meeting_pdf": "详细 PDF",
        "view_details": "查看详细表格",
        "channel_mix": "GMV 渠道拆分",
    },
    "de": {},
    "nl": {},
}
TEXT["de"] = {
    **TEXT["en"],
    "language": "Sprache",
    "caption": "Kundenfertiger Planungssimulator für SKU-Samples, Creator-Videos, Klicks, GMV, Kosten und Gewinn",
    "global_inputs": "Globale Eingaben",
    "sku_count": "Anzahl SKUs",
    "promo": "Neuer Seller: 5% Plattformgebühr für die ersten ~60 Tage anwenden",
    "promo_yes": "5% Plattformgebühr für die ersten ~60 Tage anwenden",
    "promo_no": "Nein, Standard-Kategoriekommission verwenden",
    "fulfillment": "Non-FBT Logistikkosten pro Kundenbestellung €/Bestellung",
    "fulfillment_fbt_fallback": "Fallback-Logistikkosten pro Kundenbestellung €/Bestellung für SKUs mit AOV ≤ €20",
    "logistics_carrier_cost": "Carrier-/Last-Mile-Kosten €/Bestellung",
    "logistics_pick_pack_cost": "Pick-&-Pack-Kosten €/Bestellung",
    "logistics_return_allowance": "Retouren-/Fehlzustellungs-Puffer €/Bestellung",
    "logistics_total": "Bestelllogistik gesamt",
    "logistics_detail_note": "{total} pro Bestellung = {carrier} Carrier + {pick_pack} Pick & Pack + {returns} Retourenpuffer.",
    "sample_shipping_cost": "Sample-Versandkosten €/Sample",
    "sample_handling_cost": "Sample-Verpackung & Handling €/Sample",
    "sample_shipping_total": "Sample-Logistik gesamt",
    "sample_shipping_detail_note": "{total} pro Sample = {shipping} Versand + {handling} Verpackung & Handling.",
    "fbt": "FBT-Gratisversand nutzen",
    "fbt_yes": "Ja, Logistikkosten auf €0 setzen",
    "fbt_no": "Nein, manuelle Logistikkosten nutzen",
    "fbt_help": "Planungsannahme: Bei Auswahl nutzen Kundenbestellungen für SKUs mit AOV über €20 Logistikkosten von €0; niedrigere-AOV SKUs behalten die manuellen Bestell-Logistikkosten. Sample-Versand wird separat gesteuert.",
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
    "subcategory": "Unterkategorie",
    "platform_commission": "Plattformkommission",
    "avg_sample_cost": "Ø Sample-Kosten / Stück",
    "sample_investment": "Sample-Investition",
    "ads_investment": "Ads-Investition",
    "benchmark_expander": "Kategorie-Funnel-Annahmen anzeigen / anpassen",
    "benchmark_note": "Standardwerte stammen aus der aktuellen DE-Kalibrierung. Nur anpassen, wenn Sie die Planungsbasis bewusst uberschreiben wollen.",
    "videos_sample": "Videos / Sample",
    "clicks_video": "Klicks / Video",
    "click_order": "Klick-zu-Bestellung (%)",
    "shoptab_share": "Store/Search GMV-Anteil (%)",
    "organic_commission_sku": "Organische Creator-Provision (%)",
    "paid_commission_sku": "Paid-Traffic-Creator-Provision (%)",
    "aov_help": "Durchschnittlicher Verkaufspreis pro Bestellung. Der aktuelle Standardwert ist eine Planning-Eingabe; bitte mit dem AM abstimmen und TikTok-Shop-Daten ähnlicher Kategorien oder Händler nutzen.",
    "gross_margin_help": "Händler-Bruttomarge vor Plattformgebühr, Creator-Provision, Ads, Logistik und Sample-Investment. Produktkosten = AOV x (1 - Bruttomarge).",
    "videos_sample_help": "Geschätzte Creator-Videos pro versendetem Sample. Beispiel: 1,50 bedeutet ca. 150 Videos aus 100 Samples. Bitte mit dem AM anhand ähnlicher TikTok-Shop-Kategorien oder Händler abstimmen.",
    "clicks_video_help": "Geschätzte Produktseiten-Klicks pro Creator-Video über den Content-Tail. Bitte mit dem AM anhand ähnlicher TikTok-Shop-Kategorien oder Händler abstimmen.",
    "click_order_help": "Geschätzte Conversion von Produktklick zu Bestellung. Bitte ähnliche TikTok-Shop-Kategorien oder Händler als Referenz nutzen.",
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
    "caption": "Client-ready planningssimulator voor SKU-samples, creator-video's, clicks, GMV, kosten en winst",
    "global_inputs": "Algemene invoer",
    "sku_count": "Aantal SKU's",
    "promo": "Nieuwe seller: 5% platform fee voor de eerste ~60 dagen toepassen",
    "promo_yes": "5% platform fee voor de eerste ~60 dagen toepassen",
    "promo_no": "Nee, standaard categoriecommissie gebruiken",
    "fulfillment": "Non-FBT logistieke kosten per klantorder €/order",
    "fulfillment_fbt_fallback": "Fallback logistieke kosten per klantorder €/order voor SKU's met AOV ≤ €20",
    "logistics_carrier_cost": "Carrier / last-mile kosten €/order",
    "logistics_pick_pack_cost": "Pick & pack kosten €/order",
    "logistics_return_allowance": "Retour / mislukte levering buffer €/order",
    "logistics_total": "Orderlogistiek totaal",
    "logistics_detail_note": "{total} per order = {carrier} carrier + {pick_pack} pick & pack + {returns} retourbuffer.",
    "sample_shipping_cost": "Sampleverzendkosten €/sample",
    "sample_handling_cost": "Sample verpakken & handling €/sample",
    "sample_shipping_total": "Samplelogistiek totaal",
    "sample_shipping_detail_note": "{total} per sample = {shipping} verzending + {handling} verpakken & handling.",
    "fbt": "FBT gratis verzending gebruiken",
    "fbt_yes": "Ja, logistieke kosten op €0 zetten",
    "fbt_no": "Nee, handmatige logistieke kosten gebruiken",
    "fbt_help": "Planningsaanname: wanneer geselecteerd, gebruiken klantorders voor SKU's met AOV boven €20 logistieke kosten van €0; lagere-AOV SKU's gebruiken de handmatige orderlogistiek. Sampleverzending wordt apart ingesteld.",
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
    "subcategory": "Subcategorie",
    "platform_commission": "Platformcommissie",
    "avg_sample_cost": "Gem. samplekosten / stuk",
    "sample_investment": "Sample-investering",
    "ads_investment": "Ads-investering",
    "benchmark_expander": "Categorie-funnelaannames bekijken / aanpassen",
    "benchmark_note": "Standaardwaarden komen uit de recente DE-kalibratie. Pas ze alleen aan als je de planningsbasis bewust wilt overschrijven.",
    "videos_sample": "Video's / sample",
    "clicks_video": "Clicks / video",
    "click_order": "Click-to-order (%)",
    "shoptab_share": "Store/Search GMV-aandeel (%)",
    "organic_commission_sku": "Organische creator commissie (%)",
    "paid_commission_sku": "Paid-traffic creator commissie (%)",
    "aov_help": "Gemiddelde verkoopprijs per order. De huidige standaardwaarde is een planning input; stem af met de AM en gebruik TikTok Shop-data van vergelijkbare categorieen of merchants.",
    "gross_margin_help": "Brutomarge van de merchant voor platform fee, creator commissie, ads, logistiek en sample-investering. Productkosten = AOV x (1 - brutomarge).",
    "videos_sample_help": "Geschat aantal creator-video's per verzonden sample. Voorbeeld: 1,50 betekent circa 150 video's uit 100 samples. Stem af met de AM op basis van vergelijkbare TikTok Shop-categorieen of merchants.",
    "clicks_video_help": "Geschat aantal productpagina-clicks per creator-video over de content-tail. Stem af met de AM op basis van vergelijkbare TikTok Shop-categorieen of merchants.",
    "click_order_help": "Geschatte conversie van productclick naar order. Gebruik vergelijkbare TikTok Shop-categorieen of merchants als referentie.",
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


for language_code, enhancement_copy in ENHANCEMENT_TEXT.items():
    TEXT[language_code].update(enhancement_copy)


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


def signed_money(value):
    value = float(value)
    if abs(value) < 0.5:
        return "€0"
    sign = "+" if value > 0 else "-"
    return f"{sign}{money(abs(value), 0)}"


def pct(value, digits=1):
    return f"{float(value):.{digits}%}"


def safe_filename_part(value, fallback="Brand"):
    text = str(value or "").strip() or fallback
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in text)
    cleaned = "_".join(part for part in cleaned.split("_") if part)
    return cleaned[:60] or fallback


with st.sidebar:
    if "language_input" not in st.session_state:
        st.session_state["language_input"] = "en"
    lang = st.selectbox(
        "Language",
        options=["en", "zh", "de", "nl"],
        format_func=lambda code: LANG_LABELS[code],
        key="language_input",
    )

T = TEXT[lang]

ASSUMPTION_STATUS_KEYS = ["planning", "am_aligned", "merchant_confirmed"]
PHASE_CHART_MODE_KEYS = ["cumulative", "total"]


def assumption_status_label(status_key):
    return {
        "planning": T["benchmark_input"],
        "am_aligned": T["am_aligned_input"],
        "merchant_confirmed": T["merchant_confirmed_input"],
    }.get(status_key, T["benchmark_input"])


def normalize_assumption_status(value):
    if value in ASSUMPTION_STATUS_KEYS:
        return value
    legacy_labels = {}
    for text_map in TEXT.values():
        legacy_labels[text_map["benchmark_input"]] = "planning"
        legacy_labels[text_map["am_aligned_input"]] = "am_aligned"
        legacy_labels[text_map["merchant_confirmed_input"]] = "merchant_confirmed"
    return legacy_labels.get(value, "planning")


def normalize_phase_chart_mode(value):
    if value in PHASE_CHART_MODE_KEYS:
        return value
    legacy_labels = {}
    for text_map in TEXT.values():
        legacy_labels[text_map["phase_chart_cumulative"]] = "cumulative"
        legacy_labels[text_map["phase_chart_total"]] = "total"
    return legacy_labels.get(value, "cumulative")


def phase_chart_mode_label(mode_key):
    return {
        "cumulative": T["phase_chart_cumulative"],
        "total": T["phase_chart_total"],
    }.get(mode_key, T["phase_chart_cumulative"])


def migrate_session_state():
    phase_keys = [phase["key"] for phase in PHASES]
    if st.session_state.get("selected_phase_view") not in (None, *phase_keys):
        st.session_state["selected_phase_view"] = phase_keys[0]

    for phase_key in phase_keys:
        mode_key = f"phase_chart_mode_{phase_key}"
        if mode_key in st.session_state:
            st.session_state[mode_key] = normalize_phase_chart_mode(st.session_state[mode_key])

    for status_key in ("assumption_status_input", "_model_assumption_status"):
        if status_key in st.session_state:
            st.session_state[status_key] = normalize_assumption_status(st.session_state[status_key])


migrate_session_state()

st.markdown(
    """
    <style>
    :root {
        --tts-accent: #111827;
        --tts-blue: #315EEC;
        --tts-cyan: #25D7D2;
        --tts-red: #FE2C55;
        --tts-violet: #7C3AED;
        --tts-accent-soft: #F4F7FB;
        --tts-green: #12A08C;
        --tts-ink: #0F172A;
        --tts-muted: #667085;
        --tts-line: #D9E1EC;
        --tts-panel: #FFFFFF;
        --tts-bg: #F3F6FA;
    }

    .stApp {
        background: var(--tts-bg);
    }

    [data-testid="stAppViewContainer"] > .main {
        background:
            radial-gradient(circle at 18% 0%, rgba(37, 215, 210, 0.12), transparent 28%),
            radial-gradient(circle at 86% 4%, rgba(254, 44, 85, 0.08), transparent 24%),
            linear-gradient(180deg, #F8FAFD 0%, #F3F6FA 42%, #EEF3F8 100%);
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
        gap: 0.55rem;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #1F2937;
        letter-spacing: 0;
    }

    .block-container {
        max-width: 1240px;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
    }

    [data-testid="stAppViewContainer"] > .main .block-container {
        padding-left: 2.2rem;
        padding-right: 2.2rem;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(247,249,252,0.96) 100%);
        border-right: 1px solid #DDE5EF;
        box-shadow: 18px 0 38px rgba(15, 23, 42, 0.045);
    }

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #1F2937;
        font-size: 0.94rem;
        font-weight: 780;
        margin-top: 0.55rem;
    }

    section[data-testid="stSidebar"] div[data-testid="stExpander"] {
        border: 1px solid #DCE4EE;
        border-radius: 13px;
        background: rgba(255,255,255,0.86);
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.035);
        margin-bottom: 0.18rem;
    }

    section[data-testid="stSidebar"] div[data-testid="stExpander"] details[open] {
        background: linear-gradient(180deg, #FFFFFF 0%, #FAFCFF 100%);
    }

    section[data-testid="stSidebar"] div[data-testid="stExpander"] details summary p {
        color: #273449;
        font-size: 0.82rem;
        font-weight: 780;
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

    .cover-shell {
        max-width: 1160px;
        margin: 0 auto;
        padding: 12vh 0 0 0;
        position: relative;
    }

    .cover-logo-row {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        text-align: center;
    }

    .cover-logo-meta {
        min-width: 0;
        text-align: center;
    }

    .cover-logo-kicker {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #315EEC;
        background: rgba(49, 94, 236, 0.09);
        border: 1px solid rgba(49, 94, 236, 0.16);
        padding: 0.48rem 0.9rem;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 780;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        margin-bottom: 0.95rem;
    }

    .cover-logo-title {
        color: #0F172A;
        font-size: 5.2rem;
        font-weight: 860;
        line-height: 0.94;
        letter-spacing: 0;
        max-width: 1100px;
        white-space: nowrap;
    }

    .cover-logo-subtitle {
        color: #617089;
        font-size: 1.08rem;
        line-height: 1.58;
        margin: 1.15rem auto 0 auto;
        max-width: 620px;
        text-align: center;
    }

    .cover-bottom-row {
        max-width: 980px;
        margin: 3.1rem auto 0 auto;
    }

    .cover-row-label {
        color: #7A8699;
        font-size: 0.69rem;
        font-weight: 780;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        margin: 0 0 0.75rem 0.3rem;
        text-align: left;
    }

    .cover-field {
        background: transparent;
        border: 0;
        padding: 0;
        min-height: 0;
    }

    .cover-field-kicker {
        color: #667085;
        font-size: 0.7rem;
        font-weight: 760;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        margin: 0 0 0.45rem 0.2rem;
    }

    .cover-button-wrap {
        display: flex;
        align-items: stretch;
    }

    .cover-note {
        color: #738196;
        font-size: 0.78rem;
        line-height: 1.7;
        max-width: 620px;
        margin: 1.3rem auto 0 auto;
        text-align: center;
    }

    .cover-note strong {
        color: #111827;
        font-weight: 700;
    }

    .cover-bottom-row .stButton > button {
        min-height: 74px;
        border-radius: 20px;
        font-size: 1.08rem;
        font-weight: 780;
        background: linear-gradient(180deg, #315EEC 0%, #244DDC 100%);
        border: 0;
        box-shadow: 0 18px 38px rgba(49, 94, 236, 0.2);
    }

    .cover-bottom-row [data-testid="stNumberInputContainer"] input {
        min-height: 74px;
        border-radius: 20px;
        font-size: 1.12rem;
        font-weight: 700;
        background: #FFFFFF;
        border: 1.5px solid #D6DFEA;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.045);
    }

    .cover-bottom-row [data-testid="stNumberInputContainer"] button {
        min-height: 74px;
        border-radius: 18px;
    }

    .cover-bottom-row + div[data-testid="stHorizontalBlock"] {
        max-width: 980px;
        margin: 0 auto;
        align-items: end;
        gap: 1rem;
    }

    .cover-bottom-row + div[data-testid="stHorizontalBlock"] [data-testid="column"] {
        align-self: stretch;
    }

    .cover-bottom-row + div[data-testid="stHorizontalBlock"] [data-testid="stNumberInputContainer"] {
        margin-top: 0;
    }

    @media (max-width: 1100px) {
        .cover-logo-title {
            white-space: normal;
        }
    }

    div[data-testid="stMetric"] {
        background: var(--tts-panel);
        border: 1px solid var(--tts-line);
        border-radius: 8px;
        padding: 14px 15px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
        min-height: 116px;
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
        font-size: 1.45rem;
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
        background: #FFFFFF;
        border: 1.5px solid #D8E0EA;
        border-radius: 14px;
        padding: 0.88rem 1rem;
        min-height: 78px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .readonly-rate-label {
        color: #6B7280;
        font-size: 0.8rem;
        font-weight: 680;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    .readonly-rate-value {
        color: #111827;
        font-size: 1.12rem;
        font-weight: 760;
        line-height: 1.2;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #D0D7E2;
        border-radius: 10px;
        background: #FFFFFF;
        box-shadow: none;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.chart-card-title) {
        border: 1px solid rgba(214, 224, 236, 0.95);
        border-radius: 18px;
        background: linear-gradient(180deg, #FFFFFF 0%, #FBFCFE 100%);
        box-shadow: 0 18px 46px rgba(15, 23, 42, 0.06);
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.chart-card-title) > div {
        padding: 6px 8px 4px 8px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.sku-title) {
        border: 1.5px solid #D8E0EA;
        border-radius: 16px;
        background: #FFFFFF;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.035);
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.sku-title) > div {
        padding-top: 4px;
        padding-bottom: 4px;
    }

    div[data-testid="stNumberInput"] [data-baseweb="input"],
    div[data-testid="stTextInput"] [data-baseweb="input"],
    div[data-testid="stSelectbox"] [data-baseweb="select"] {
        border: 1.5px solid #D5DDE7 !important;
        border-radius: 12px !important;
        background: #FFFFFF !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.02) !important;
    }

    div[data-testid="stNumberInput"] [data-baseweb="input"]:hover,
    div[data-testid="stTextInput"] [data-baseweb="input"]:hover,
    div[data-testid="stSelectbox"] [data-baseweb="select"]:hover {
        border-color: #C2CCDA !important;
    }

    div[data-testid="stNumberInput"] [data-baseweb="input"]:focus-within,
    div[data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
    div[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within {
        border-color: #7D93B3 !important;
        box-shadow: 0 0 0 1px #7D93B3 inset, 0 0 0 5px rgba(49, 94, 236, 0.07) !important;
    }

    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextInput"] input,
    div[data-testid="stSelectbox"] input {
        color: #111827 !important;
        font-weight: 520;
    }

    div[data-testid="stNumberInput"] button {
        color: #6B7280 !important;
    }

    div[data-testid="stNumberInput"] label p,
    div[data-testid="stTextInput"] label p,
    div[data-testid="stSelectbox"] label p {
        color: #4B5563 !important;
        font-weight: 620 !important;
        font-size: 0.84rem !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stNumberInput"] [data-baseweb="input"],
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] [data-baseweb="input"],
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] {
        border-color: #D2DAE5 !important;
        background: #FFFFFF !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        display: grid;
        grid-auto-flow: column;
        grid-auto-columns: minmax(0, 1fr);
        gap: 8px;
        border-bottom: 0;
        background: transparent;
        padding: 0;
        border-radius: 0;
        width: 100%;
    }

    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    .stTabs [data-baseweb="tab"] {
        min-height: 42px;
        padding: 8px 14px;
        color: #334155;
        font-weight: 680;
        border-radius: 12px;
        background: #F8FAFC;
        border: 1px solid #E7ECF2;
        justify-content: center;
        width: 100%;
    }

    .stTabs [aria-selected="true"] {
        color: #111827;
        background: #FFFFFF;
        border-color: #CCD7E4;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }

    .stTabs [data-baseweb="tab"]:hover {
        border-color: #D8E0EA;
        background: #FFFFFF;
    }

    .tabs-shell {
        background: transparent;
        border: 0;
        border-radius: 0;
        padding: 4px 0 0 0;
        box-shadow: none;
        margin-top: 6px;
    }

    .stButton > button {
        border-radius: 10px;
        border: 1px solid #E4E7EC;
        background: #FFFFFF;
        color: #111827;
        font-weight: 720;
        min-height: 44px;
        box-shadow: none;
    }

    .stButton > button:hover {
        background: #F8FAFC;
        color: #111827;
        border: 1px solid #D9DEE5;
    }

    .stButton > button:focus-visible,
    .stDownloadButton > button:focus-visible,
    [data-baseweb="select"]:focus-visible {
        outline: 3px solid rgba(49, 94, 236, 0.30) !important;
        outline-offset: 2px !important;
    }

    .st-key-selected_phase_view_control [data-testid="stButton"],
    div[class*="st-key-phase_chart_mode_"][class*="_control"] [data-testid="stButton"] {
        flex: 1 1 0;
        min-width: 0;
    }

    .st-key-selected_phase_view_control [data-testid="stButton"] button,
    div[class*="st-key-phase_chart_mode_"][class*="_control"] [data-testid="stButton"] button {
        width: 100%;
    }

    .stButton > button[kind="primary"] {
        border-color: #111827;
        background: #111827;
        color: #FFFFFF;
        box-shadow: none;
    }

    .stButton > button[kind="primary"]:hover {
        background: #0F172A;
        color: #FFFFFF;
        border-color: #0F172A;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--tts-line);
        border-radius: 8px;
        overflow: hidden;
        box-shadow: none;
    }

    div[data-testid="stExpander"] {
        border: 1px solid #D8E0EA;
        border-radius: 14px;
        background: #FFFFFF;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.025);
        overflow: hidden;
    }

    div[data-testid="stExpander"] details summary {
        padding-top: 2px;
        padding-bottom: 2px;
    }

    div[data-testid="stExpander"] details summary p {
        color: #111827;
        font-weight: 700;
    }

    div[data-testid="stExpander"] div[data-testid="stExpander"] {
        margin-top: 0.8rem;
        border: 1px solid #E3E9F2;
        border-radius: 12px;
        background: linear-gradient(180deg, #FBFCFE 0%, #F7F9FC 100%);
        box-shadow: none;
    }

    div[data-testid="stExpander"] div[data-testid="stExpander"] details summary {
        padding-top: 0.15rem;
        padding-bottom: 0.15rem;
    }

    div[data-testid="stExpander"] div[data-testid="stExpander"] details summary p {
        color: #2B3648;
        font-size: 0.92rem;
        font-weight: 680;
    }

    .benchmark-note {
        color: #6B7280;
        font-size: 0.81rem;
        line-height: 1.55;
        margin: 0.1rem 0 0.9rem 0;
        max-width: 760px;
    }

    div[data-testid="stAlert"] {
        border-radius: 12px;
        border: 1px solid #E7ECF2;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.018);
        background: #FFFFFF;
    }

    div[data-testid="stPlotlyChart"] {
        background: transparent;
        border: 0;
        border-radius: 0;
        padding: 0;
        margin: 8px 0 0 0;
        box-shadow: none;
        overflow: visible;
    }

    div[data-testid="stPlotlyChart"] > div {
        width: 100% !important;
        min-height: 0 !important;
        overflow: visible;
    }

    .dashboard-note {
        background: #FFFFFF;
        border: 1px solid #D0D7E2;
        border-radius: 10px;
        padding: 12px 14px;
        color: #334155;
        box-shadow: none;
        line-height: 1.48;
    }

    .dashboard-intro {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
        margin: 10px 0 14px 0;
        align-items: stretch;
    }

    .dashboard-intro-card {
        background: #FFFFFF;
        border: 1px solid #D0D7E2;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: none;
        min-height: 96px;
    }

    .dashboard-intro-kicker {
        color: #64748B;
        font-size: 0.76rem;
        font-weight: 780;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }

    .dashboard-intro-text {
        color: #334155;
        font-size: 0.92rem;
        line-height: 1.46;
    }

    .executive-brief-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin: 10px 0 16px 0;
    }

    .executive-brief-card {
        background: #FFFFFF;
        border: 1px solid #D0D7E2;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: none;
        min-height: 118px;
    }

    .executive-brief-kicker {
        color: #64748B;
        font-size: 0.74rem;
        font-weight: 780;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 8px;
    }

    .executive-brief-body {
        color: #334155;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .setup-gate {
        background: #FFFFFF;
        border: 1px solid #D0D7E2;
        border-radius: 12px;
        padding: 22px 24px;
        margin: 22px 0 14px 0;
        box-shadow: none;
    }

    .setup-gate-kicker {
        color: #667085;
        font-size: 0.82rem;
        font-weight: 780;
        margin-bottom: 8px;
    }

    .setup-gate-title {
        color: #111827;
        font-size: 1.42rem;
        font-weight: 800;
        line-height: 1.18;
        margin-bottom: 8px;
    }

    .setup-gate-body {
        color: #4B5563;
        font-size: 1rem;
        line-height: 1.58;
        max-width: 760px;
    }

    .setup-ready {
        background: linear-gradient(180deg, #FFFFFF 0%, #FAFBFD 100%);
        border: 1px solid #D9E1EB;
        border-radius: 12px;
        padding: 12px 14px;
        margin: 12px 0 18px 0;
        color: #374151;
        box-shadow: none;
        line-height: 1.55;
    }

    .sidebar-meta {
        color: #98A2B3;
        font-size: 0.74rem;
        line-height: 1.5;
        margin: 5px 0 9px 0;
    }

    .inline-note {
        margin: 0.3rem 0 0.45rem 0;
    }

    .inline-note details {
        border: 0;
        background: transparent;
        padding: 0;
        margin: 0;
    }

    .inline-note summary {
        list-style: none;
        cursor: pointer;
        color: #667085;
        font-size: 0.78rem;
        font-weight: 620;
        line-height: 1.4;
        user-select: none;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
    }

    .inline-note summary::-webkit-details-marker {
        display: none;
    }

    .inline-note summary::before {
        content: "+";
        color: #98A2B3;
        font-size: 0.82rem;
        font-weight: 700;
        line-height: 1;
    }

    .inline-note details[open] summary::before {
        content: "−";
    }

    .inline-note-body {
        color: #667085;
        font-size: 0.8rem;
        line-height: 1.55;
        margin-top: 0.35rem;
        max-width: 920px;
    }

    .sidebar-divider {
        height: 1px;
        background: #E5EAF1;
        margin: 2px 0 10px 0;
        border-radius: 999px;
    }

    .meeting-header {
        background: #FFFFFF;
        border: 1px solid #D0D7E2;
        border-radius: 16px;
        padding: 22px 24px;
        margin-bottom: 22px;
        box-shadow: none;
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 16px;
        flex-wrap: wrap;
    }

    .meeting-header-kicker {
        color: #64748B;
        font-size: 0.86rem;
        font-weight: 760;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 5px;
    }

    .meeting-header-title {
        color: #111827;
        font-size: 2.45rem;
        font-weight: 810;
        line-height: 0.98;
        letter-spacing: 0;
    }

    .meeting-header-meta {
        color: #475569;
        font-size: 0.92rem;
        font-weight: 650;
        text-align: right;
        line-height: 1.45;
    }

    .meeting-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-top: 7px;
        padding: 4px 10px;
        border-radius: 999px;
        background: #F8FAFC;
        border: 1px solid #E7ECF2;
        color: #334155;
        font-size: 0.78rem;
        font-weight: 760;
    }

    .section-shell {
        margin: 40px 0 14px 0;
        padding-bottom: 10px;
        border-bottom: 1px solid #E2E8F0;
    }

    .section-eyebrow {
        color: #64748B;
        font-size: 0.74rem;
        font-weight: 780;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 7px;
    }

    .section-title {
        color: #111827;
        font-size: 1.4rem;
        font-weight: 780;
        line-height: 1.12;
        margin: 0 0 2px 0;
    }

    .action-list {
        background: #FFFFFF;
        border: 1px solid #D0D7E2;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: none;
    }

    .action-group-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin: 10px 0 18px 0;
        align-items: stretch;
    }

    .action-group {
        background: #FFFFFF;
        border: 1px solid #D0D7E2;
        border-radius: 12px;
        padding: 14px 15px;
        min-height: 144px;
        box-shadow: none;
        display: flex;
        flex-direction: column;
    }

    .action-group-title {
        color: #111827;
        font-size: 0.86rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .action-group-item {
        color: #374151;
        font-size: 0.9rem;
        line-height: 1.45;
        padding: 8px 0;
        border-top: 1px solid #EEF2F7;
    }

    .action-group-item:first-of-type {
        border-top: 0;
    }

    .action-item {
        display: flex;
        gap: 10px;
        padding: 10px 0;
        border-bottom: 1px solid #EEF2F7;
        color: #1F2937;
        line-height: 1.5;
    }

    .action-item:last-child {
        border-bottom: 0;
    }

    .action-index {
        flex: 0 0 26px;
        width: 26px;
        height: 26px;
        border-radius: 999px;
        background: #EEF2F7;
        color: #334155;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 760;
        font-size: 0.82rem;
    }

    .readout-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin: 10px 0 14px 0;
        align-items: stretch;
    }

    .readout-card {
        background: #FFFFFF;
        border: 1px solid #D0D7E2;
        border-radius: 12px;
        padding: 17px 18px;
        min-height: 138px;
        box-shadow: none;
        display: flex;
        flex-direction: column;
    }

    .readout-title {
        color: #111827;
        font-size: 0.88rem;
        font-weight: 780;
        margin-bottom: 8px;
    }

    .readout-body {
        color: #374151;
        font-size: 0.94rem;
        line-height: 1.52;
        overflow-wrap: anywhere;
    }

    .chart-lens {
        background: #FFFFFF;
        border: 1px solid #D0D7E2;
        border-radius: 10px;
        padding: 12px 14px;
        margin: 10px 0 14px 0;
        box-shadow: none;
    }

    .chart-lens.compact {
        padding: 10px 12px;
        margin: 6px 0 10px 0;
        box-shadow: none;
    }

    .chart-lens-title {
        color: #111827;
        font-size: 0.92rem;
        font-weight: 760;
        margin-bottom: 6px;
    }

    .chart-lens.compact .chart-lens-title {
        font-size: 0.8rem;
        margin-bottom: 4px;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    .chart-lens-body {
        color: #4B5563;
        font-size: 0.94rem;
        line-height: 1.55;
    }

    .chart-lens.compact .chart-lens-body {
        color: #334155;
        font-size: 0.9rem;
        line-height: 1.45;
    }

    .subtle-note {
        color: #667085;
        font-size: 0.8rem;
        line-height: 1.55;
        padding: 0 0 8px 0;
        margin: 0 0 8px 0;
    }

    .subtle-note strong {
        color: #475569;
        font-weight: 760;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        font-size: 0.74rem;
    }

    .funnel-card-wrap {
        background: transparent;
        border: 0;
        border-radius: 0;
        padding: 0 0 2px 0;
        box-shadow: none;
        margin-bottom: 0;
    }

    .support-panel {
        background: transparent;
        border: 0;
        border-radius: 0;
        padding: 0;
        box-shadow: none;
        margin-bottom: 14px;
    }

    .chart-card-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 18px;
        margin: 10px 0 14px 0;
        align-items: start;
    }

    .chart-card {
        background: linear-gradient(180deg, #FFFFFF 0%, #FBFCFE 100%);
        border: 1px solid rgba(216, 225, 236, 0.95);
        border-radius: 18px;
        padding: 16px 18px 12px 18px;
        box-shadow: 0 18px 46px rgba(15, 23, 42, 0.055);
        margin: 8px 0 12px 0;
    }

    .chart-card-header {
        display: block;
        margin-bottom: 8px;
    }

    .chart-card-kicker {
        display: inline-block;
        color: var(--tts-blue);
        font-size: 0.68rem;
        font-weight: 760;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        white-space: nowrap;
        margin-bottom: 6px;
    }

    .chart-card-title {
        color: #111827;
        font-size: 1.02rem;
        font-weight: 760;
        line-height: 1.18;
        margin: 0;
    }

    .chart-card-subtitle {
        color: #667085;
        font-size: 0.8rem;
        line-height: 1.45;
        margin-top: 4px;
        max-width: 52ch;
    }

    .chart-card-body {
        margin-top: 2px;
    }

    .chart-card-footer {
        margin-top: 10px;
        padding-top: 0;
        border-top: 0;
        color: #667085;
        font-size: 0.75rem;
        line-height: 1.46;
    }

    .chart-card-footer strong {
        color: #475467;
        font-weight: 700;
    }

    .report-appendix {
        background: #FFFFFF;
        border: 1px solid #D0D7E2;
        border-radius: 12px;
        padding: 0.95rem 1rem;
        margin-top: 1rem;
    }

    .funnel-card-title {
        color: #6B7280;
        font-size: 0.73rem;
        font-weight: 780;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .funnel-card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 12px;
    }

    .funnel-card {
        border: 1px solid #E9EDF2;
        border-radius: 4px;
        padding: 14px 14px;
        min-height: 98px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 8px;
        background: #FFFFFF;
    }

    .funnel-card-label {
        color: #64748B;
        font-size: 0.82rem;
        font-weight: 760;
        line-height: 1.25;
    }

    .funnel-card-value {
        color: #111827;
        font-size: 1.65rem;
        font-weight: 820;
        line-height: 1.12;
        overflow-wrap: anywhere;
    }

    .hero-band {
        position: relative;
        overflow: hidden;
        background:
            linear-gradient(135deg, rgba(17, 24, 39, 0.96) 0%, rgba(31, 41, 55, 0.96) 55%, rgba(49, 94, 236, 0.94) 100%);
        border: 1px solid rgba(255,255,255,0.16);
        border-radius: 22px;
        padding: 28px 30px;
        margin: 10px 0 22px 0;
        box-shadow: 0 22px 60px rgba(15, 23, 42, 0.18);
        display: grid;
        grid-template-columns: minmax(320px, 1.6fr) repeat(3, minmax(150px, 0.52fr));
        gap: 18px;
        align-items: center;
    }

    .hero-band::before {
        content: "";
        position: absolute;
        inset: 0;
        background:
            linear-gradient(90deg, rgba(37, 244, 238, 0.18), transparent 28%),
            linear-gradient(270deg, rgba(254, 44, 85, 0.16), transparent 24%);
        pointer-events: none;
    }

    .hero-band > * {
        position: relative;
        z-index: 1;
    }

    .hero-copy {
        display: grid;
        grid-template-columns: 52px minmax(0, 1fr);
        gap: 16px;
        align-items: start;
    }

    .hero-mark {
        position: relative;
        overflow: hidden;
        width: 52px;
        height: 52px;
        border-radius: 16px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        background:
            radial-gradient(circle at 28% 18%, rgba(255,255,255,0.34), transparent 32%),
            linear-gradient(135deg, rgba(37,244,238,0.26), rgba(49,94,236,0.28) 48%, rgba(254,44,85,0.24));
        border: 1px solid rgba(255,255,255,0.26);
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.20),
            0 14px 32px rgba(37,244,238,0.10),
            0 16px 34px rgba(254,44,85,0.08);
    }

    .hero-mark svg,
    .hero-kpi-icon svg,
    .premium-kpi-icon svg,
    .growth-path-icon svg {
        position: relative;
        z-index: 1;
        width: 1.22em;
        height: 1.22em;
        stroke-width: 1.9;
        display: block;
    }

    .hero-mark::after,
    .hero-kpi-icon::after,
    .premium-kpi-icon::after,
    .growth-path-icon::after,
    .growth-engine-mark::after,
    .growth-engine-step-icon::after {
        content: "";
        position: absolute;
        width: 34%;
        height: 34%;
        right: 8%;
        top: 8%;
        border-radius: 999px;
        background: rgba(255,255,255,0.34);
        filter: blur(2px);
        opacity: 0.52;
        pointer-events: none;
    }

    .hero-title {
        color: #FFFFFF;
        font-size: 2.4rem;
        font-weight: 810;
        line-height: 0.94;
        letter-spacing: 0;
        margin-bottom: 12px;
    }

    .hero-subtitle {
        color: rgba(255,255,255,0.76);
        font-size: 1.02rem;
        line-height: 1.56;
    }

    .hero-kpi {
        border-left: 1px solid rgba(255,255,255,0.18);
        padding-left: 16px;
        min-width: 0;
    }

    .hero-kpi-icon {
        position: relative;
        overflow: hidden;
        width: 34px;
        height: 34px;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        background:
            radial-gradient(circle at 30% 20%, rgba(255,255,255,0.26), transparent 34%),
            rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.18);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.14);
        margin-bottom: 10px;
    }

    .hero-kpi-label {
        color: rgba(255,255,255,0.62);
        font-size: 0.74rem;
        font-weight: 760;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .hero-kpi-value {
        color: #FFFFFF;
        font-size: 1.35rem;
        font-weight: 800;
        line-height: 1.2;
        overflow-wrap: anywhere;
        word-break: normal;
    }

    .executive-insight-shell {
        position: relative;
        overflow: hidden;
        display: grid;
        grid-template-columns: 46px minmax(0, 1fr) auto;
        align-items: center;
        gap: 14px;
        background:
            radial-gradient(circle at 96% 0%, rgba(37, 215, 210, 0.13), transparent 32%),
            linear-gradient(135deg, #FFFFFF 0%, #F8FBFF 100%);
        border: 1px solid #D5E0EC;
        border-radius: 18px;
        padding: 15px 17px;
        margin: -8px 0 18px 0;
        box-shadow: 0 16px 38px rgba(15, 23, 42, 0.055);
    }

    .executive-insight-icon {
        width: 46px;
        height: 46px;
        border-radius: 15px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        background:
            radial-gradient(circle at 28% 18%, rgba(255,255,255,0.30), transparent 34%),
            linear-gradient(135deg, #315EEC, #7C3AED 62%, #FE2C55);
        box-shadow: 0 12px 24px rgba(49, 94, 236, 0.20);
    }

    .executive-insight-icon svg {
        width: 1.3em;
        height: 1.3em;
        stroke-width: 1.9;
    }

    .executive-insight-kicker {
        color: #315EEC;
        font-size: 0.66rem;
        font-weight: 840;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
    }

    .executive-insight-text {
        color: #1E293B;
        font-size: 0.91rem;
        font-weight: 680;
        line-height: 1.5;
    }

    .model-live-chip {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        color: #178A62;
        background: rgba(23, 138, 98, 0.08);
        border: 1px solid rgba(23, 138, 98, 0.15);
        border-radius: 999px;
        padding: 7px 10px;
        font-size: 0.68rem;
        font-weight: 800;
        white-space: nowrap;
    }

    .model-live-chip::before {
        content: "";
        width: 7px;
        height: 7px;
        border-radius: 999px;
        background: #12A08C;
        box-shadow: 0 0 0 4px rgba(18, 160, 140, 0.10);
    }

    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
        gap: 12px;
        margin: 10px 0 18px 0;
        align-items: stretch;
    }

    .kpi-grid.kpi-grid-four {
        grid-template-columns: repeat(4, minmax(0, 1fr));
    }

    .kpi-grid.kpi-grid-three {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .kpi-grid.kpi-grid-compact {
        grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
    }

    .outcome-context-strip {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin: 12px 0 20px 0;
    }

    .outcome-context-card {
        display: flex;
        align-items: center;
        gap: 11px;
        min-width: 0;
        padding: 12px 14px;
        background: #FFFFFF;
        border: 1px solid #DCE4EE;
        border-radius: 12px;
    }

    .outcome-context-icon {
        flex: 0 0 30px;
        width: 30px;
        height: 30px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #315EEC;
        background: #F4F7FB;
        border: 1px solid #E2E8F0;
        border-radius: 9px;
    }

    .outcome-context-icon svg {
        width: 1.05em;
        height: 1.05em;
        stroke-width: 1.9;
    }

    .outcome-context-label {
        color: #667085;
        font-size: 0.7rem;
        font-weight: 760;
        line-height: 1.2;
        text-transform: uppercase;
    }

    .outcome-context-value {
        color: #111827;
        font-size: 0.9rem;
        font-weight: 800;
        line-height: 1.25;
        margin-top: 4px;
        overflow-wrap: anywhere;
    }

    .premium-kpi {
        position: relative;
        background: linear-gradient(180deg, #FFFFFF 0%, #FBFCFE 100%);
        border: 1px solid #D5DFEA;
        border-radius: 16px;
        padding: 16px 16px;
        min-height: 94px;
        height: auto;
        overflow: visible;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.055);
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        gap: 6px;
    }

    .premium-kpi::before {
        content: "";
        position: absolute;
        left: 14px;
        right: 14px;
        top: 0;
        height: 3px;
        border-radius: 0 0 999px 999px;
        background: var(--kpi-accent, var(--tts-blue));
        opacity: 0.9;
    }

    .premium-kpi-top {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        min-height: 2.8em;
    }

    .premium-kpi-icon {
        position: relative;
        overflow: hidden;
        flex: 0 0 34px;
        width: 34px;
        height: 34px;
        border-radius: 13px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: var(--kpi-accent, var(--tts-blue));
        background:
            radial-gradient(circle at 28% 18%, rgba(255,255,255,0.92), transparent 34%),
            linear-gradient(145deg,
                color-mix(in srgb, var(--kpi-accent, var(--tts-blue)) 16%, #FFFFFF),
                color-mix(in srgb, var(--kpi-accent, var(--tts-blue)) 6%, #FFFFFF)
            );
        border: 1px solid color-mix(in srgb, var(--kpi-accent, var(--tts-blue)) 22%, #FFFFFF);
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.82),
            0 8px 18px color-mix(in srgb, var(--kpi-accent, var(--tts-blue)) 16%, transparent);
    }

    .kpi-grid.kpi-grid-compact .premium-kpi {
        min-height: 100px;
        padding: 14px 14px 14px 14px;
    }

    .kpi-grid.kpi-grid-compact .premium-kpi-value {
        font-size: 1.05rem;
    }

    .kpi-grid.kpi-grid-compact .premium-kpi-label {
        font-size: 0.7rem;
    }

    .premium-kpi-label {
        color: #6B7280;
        font-size: 0.72rem;
        font-weight: 720;
        line-height: 1.3;
        overflow-wrap: anywhere;
        word-break: break-word;
        min-height: 2.7em;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    .premium-kpi-value {
        color: #111827;
        font-size: 1.28rem;
        font-weight: 800;
        line-height: 1.18;
        overflow-wrap: anywhere;
        word-break: break-word;
        min-height: 2.4em;
        display: flex;
        align-items: flex-end;
    }

    .insight-strip {
        background: transparent;
        border: 0;
        color: #667085;
        padding: 0;
        margin: 0;
        box-shadow: none;
        line-height: 1.5;
        font-size: 0.82rem;
    }

    .insight-strip.compact {
        padding: 0;
        margin: 0;
        font-size: 0.82rem;
        color: #667085;
        box-shadow: none;
    }

    .status-panel {
        background: #FFFFFF;
        border: 1.5px solid #D8E0EA;
        border-radius: 12px;
        padding: 11px 13px;
        margin: 8px 0 12px 0;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.025);
    }

    .status-panel.compact {
        padding: 10px 12px;
        margin: 6px 0 10px 0;
    }

    .status-panel-kicker {
        color: #64748B;
        font-size: 0.76rem;
        font-weight: 780;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }

    .status-panel-title {
        color: #111827;
        font-size: 0.92rem;
        font-weight: 760;
        margin-bottom: 5px;
    }

    .status-panel.compact .status-panel-title {
        font-size: 0.84rem;
        margin-bottom: 3px;
    }

    .status-panel-body {
        color: #334155;
        font-size: 0.92rem;
        line-height: 1.5;
    }

    .status-panel-row {
        display: flex;
        gap: 10px;
        align-items: baseline;
        flex-wrap: wrap;
    }

    .status-panel-row-title {
        color: #111827;
        font-size: 0.84rem;
        font-weight: 760;
        white-space: nowrap;
    }

    .status-panel-row-body {
        color: #334155;
        font-size: 0.88rem;
        line-height: 1.45;
        flex: 1 1 280px;
    }

    .status-panel.compact .status-panel-body {
        font-size: 0.88rem;
        line-height: 1.42;
    }

    .status-panel.info {
        border-left-color: #E7EBF1;
        background: #FFFFFF;
    }

    .status-panel.success {
        border-left-color: #E7EBF1;
        background: #FFFFFF;
    }

    .status-panel.warning {
        border-left-color: #E7EBF1;
        background: #FFFFFF;
    }

    .growth-path-strip {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr)) minmax(210px, 0.8fr);
        gap: 12px;
        margin: 0 0 22px 0;
        align-items: stretch;
    }

    .growth-path-node {
        position: relative;
        background: rgba(255,255,255,0.9);
        border: 1px solid #D6E0EC;
        border-radius: 16px;
        padding: 14px 15px;
        box-shadow: 0 10px 26px rgba(15, 23, 42, 0.045);
        overflow: hidden;
    }

    .growth-path-node::after {
        content: "";
        position: absolute;
        top: 16px;
        right: -18px;
        width: 36px;
        height: 2px;
        background: linear-gradient(90deg, var(--tts-cyan), var(--tts-blue));
        opacity: 0.55;
    }

    .growth-path-node:last-child::after,
    .growth-path-summary::after {
        display: none;
    }

    .growth-path-kicker {
        color: #64748B;
        font-size: 0.68rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }

    .growth-path-heading {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }

    .growth-path-icon {
        position: relative;
        overflow: hidden;
        flex: 0 0 30px;
        width: 30px;
        height: 30px;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: var(--tts-blue);
        background:
            radial-gradient(circle at 28% 20%, rgba(255,255,255,0.92), transparent 34%),
            linear-gradient(145deg, rgba(49, 94, 236, 0.13), rgba(37, 244, 238, 0.07));
        border: 1px solid rgba(49, 94, 236, 0.16);
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.72),
            0 8px 16px rgba(49, 94, 236, 0.08);
    }

    .growth-path-summary .growth-path-icon {
        color: #FFFFFF;
        background:
            radial-gradient(circle at 30% 20%, rgba(255,255,255,0.26), transparent 34%),
            rgba(255,255,255,0.10);
        border-color: rgba(255,255,255,0.18);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.14);
    }

    .growth-path-title {
        color: #111827;
        font-size: 0.96rem;
        font-weight: 800;
        line-height: 1.2;
        margin: 0;
    }

    .growth-path-metrics {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 8px;
    }

    .growth-path-label {
        color: #667085;
        font-size: 0.68rem;
        font-weight: 720;
        line-height: 1.2;
    }

    .growth-path-value {
        color: #0F172A;
        font-size: 0.92rem;
        font-weight: 800;
        line-height: 1.2;
        margin-top: 2px;
        overflow-wrap: anywhere;
    }

    .growth-path-summary {
        background: linear-gradient(180deg, #111827 0%, #1F2937 100%);
        border-color: rgba(255,255,255,0.1);
    }

    .growth-path-summary .growth-path-kicker,
    .growth-path-summary .growth-path-label {
        color: rgba(255,255,255,0.62);
    }

    .growth-path-summary .growth-path-title,
    .growth-path-summary .growth-path-value {
        color: #FFFFFF;
    }

    .growth-engine-panel {
        background: linear-gradient(180deg, rgba(255,255,255,0.94) 0%, rgba(248,251,255,0.94) 100%);
        border: 1px solid #D6E0EC;
        border-radius: 20px;
        padding: 18px;
        margin: 0 0 24px 0;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.055);
    }

    .growth-engine-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 16px;
    }

    .growth-engine-title-wrap {
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 0;
    }

    .growth-engine-mark {
        position: relative;
        overflow: hidden;
        width: 40px;
        height: 40px;
        border-radius: 14px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        background:
            radial-gradient(circle at 28% 18%, rgba(255,255,255,0.30), transparent 34%),
            linear-gradient(135deg, var(--tts-blue), var(--tts-violet) 56%, var(--tts-red));
        border: 1px solid rgba(255,255,255,0.18);
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.20),
            0 12px 22px rgba(49, 94, 236, 0.20);
        flex: 0 0 40px;
    }

    .growth-engine-mark svg,
    .growth-engine-step-icon svg {
        position: relative;
        z-index: 1;
        width: 1.22em;
        height: 1.22em;
        stroke-width: 1.9;
        display: block;
    }

    .growth-engine-title {
        color: #0F172A;
        font-size: 1.05rem;
        font-weight: 850;
        line-height: 1.15;
    }

    .growth-engine-subtitle {
        color: #64748B;
        font-size: 0.82rem;
        line-height: 1.42;
        margin-top: 3px;
    }

    .growth-engine-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 10px;
    }

    .growth-engine-step {
        position: relative;
        background: #FFFFFF;
        border: 1px solid #DCE5EF;
        border-radius: 16px;
        padding: 14px;
        min-height: 132px;
        overflow: hidden;
    }

    .growth-engine-step::after {
        content: "";
        position: absolute;
        top: 28px;
        right: -18px;
        width: 36px;
        height: 2px;
        background: linear-gradient(90deg, var(--tts-cyan), var(--tts-blue));
        opacity: 0.45;
    }

    .growth-engine-step:last-child::after {
        display: none;
    }

    .growth-engine-step-top {
        display: flex;
        align-items: center;
        gap: 9px;
        margin-bottom: 12px;
    }

    .growth-engine-step-icon {
        position: relative;
        overflow: hidden;
        width: 32px;
        height: 32px;
        border-radius: 13px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: var(--step-accent, var(--tts-blue));
        background:
            radial-gradient(circle at 28% 18%, rgba(255,255,255,0.92), transparent 34%),
            linear-gradient(145deg,
                color-mix(in srgb, var(--step-accent, var(--tts-blue)) 18%, #FFFFFF),
                color-mix(in srgb, var(--step-accent, var(--tts-blue)) 7%, #FFFFFF)
            );
        border: 1px solid color-mix(in srgb, var(--step-accent, var(--tts-blue)) 23%, #FFFFFF);
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.82),
            0 8px 18px color-mix(in srgb, var(--step-accent, var(--tts-blue)) 15%, transparent);
        flex: 0 0 32px;
    }

    .growth-engine-step-label {
        color: #64748B;
        font-size: 0.68rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        line-height: 1.2;
    }

    .growth-engine-step-value {
        color: #0F172A;
        font-size: 1.18rem;
        font-weight: 860;
        line-height: 1.12;
        overflow-wrap: anywhere;
        margin-bottom: 8px;
    }

    .growth-engine-step-rate {
        color: #667085;
        font-size: 0.75rem;
        line-height: 1.35;
        padding-top: 8px;
        border-top: 1px solid #EEF3F8;
    }

    .decision-grid {
        display: grid;
        grid-template-columns: minmax(0, 1.08fr) minmax(0, 1fr);
        gap: 14px;
        margin: 0 0 24px 0;
        align-items: stretch;
    }

    .decision-panel {
        background: linear-gradient(180deg, #FFFFFF 0%, #FBFCFE 100%);
        border: 1px solid #D6E0EC;
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 14px 34px rgba(15, 23, 42, 0.05);
        min-width: 0;
    }

    .decision-panel-title {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #0F172A;
        font-size: 0.98rem;
        font-weight: 850;
        line-height: 1.2;
        margin-bottom: 4px;
    }

    .decision-panel-title .premium-kpi-icon {
        width: 32px;
        height: 32px;
        flex-basis: 32px;
    }

    .decision-panel-subtitle {
        color: #64748B;
        font-size: 0.78rem;
        line-height: 1.4;
        margin: 0 0 14px 42px;
    }

    .diagnostic-card {
        border: 1px solid #E2E8F0;
        border-radius: 15px;
        padding: 14px;
        background:
            radial-gradient(circle at 100% 0%, color-mix(in srgb, var(--diagnostic-accent, var(--tts-blue)) 10%, transparent), transparent 34%),
            #FFFFFF;
    }

    .diagnostic-top {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 12px;
    }

    .diagnostic-name {
        color: #0F172A;
        font-size: 1rem;
        font-weight: 850;
        line-height: 1.2;
    }

    .diagnostic-pill {
        color: var(--diagnostic-accent, var(--tts-blue));
        background: color-mix(in srgb, var(--diagnostic-accent, var(--tts-blue)) 10%, #FFFFFF);
        border: 1px solid color-mix(in srgb, var(--diagnostic-accent, var(--tts-blue)) 20%, #FFFFFF);
        border-radius: 999px;
        padding: 5px 8px;
        font-size: 0.66rem;
        font-weight: 820;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        white-space: nowrap;
    }

    .diagnostic-signal {
        color: #334155;
        font-size: 0.86rem;
        font-weight: 760;
        line-height: 1.35;
        margin-bottom: 9px;
    }

    .diagnostic-action {
        color: #667085;
        font-size: 0.8rem;
        line-height: 1.45;
    }

    .debug-details-grid {
        overflow: hidden;
        border: 1px solid #DCE4EE;
        border-radius: 14px;
        background: #FFFFFF;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.82);
    }

    .debug-details-header,
    .debug-details-row {
        display: grid;
        grid-template-columns: minmax(0, 1.35fr) minmax(120px, 0.65fr);
        align-items: center;
        column-gap: 18px;
        padding: 10px 14px;
    }

    .debug-details-header {
        color: #64748B;
        background: #F7F9FC;
        border-bottom: 1px solid #E7EDF4;
        font-size: 0.68rem;
        font-weight: 820;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .debug-details-header span:last-child,
    .debug-details-value {
        text-align: right;
    }

    .debug-details-row {
        min-height: 42px;
        color: #334155;
        font-size: 0.79rem;
        line-height: 1.35;
    }

    .debug-details-row + .debug-details-row {
        border-top: 1px solid #EDF1F6;
    }

    .debug-details-label {
        font-weight: 680;
    }

    .debug-details-value {
        color: #0F172A;
        font-weight: 820;
        font-variant-numeric: tabular-nums;
        overflow-wrap: anywhere;
    }

    .detail-table-shell {
        overflow: hidden;
        border: 1px solid #DCE4EE;
        border-radius: 14px;
        background: #FFFFFF;
    }

    .detail-table-scroll {
        max-height: min(56vh, 480px);
        overflow: auto;
        scrollbar-gutter: stable;
    }

    .detail-table {
        width: max-content;
        min-width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        color: #334155;
        font-size: 0.74rem;
        line-height: 1.35;
        font-variant-numeric: tabular-nums;
    }

    .detail-table th,
    .detail-table td {
        max-width: 240px;
        padding: 9px 11px;
        text-align: left;
        vertical-align: top;
        white-space: nowrap;
        border-bottom: 1px solid #EDF1F6;
    }

    .detail-table th {
        position: sticky;
        top: 0;
        z-index: 1;
        color: #526174;
        background: #F7F9FC;
        font-size: 0.65rem;
        font-weight: 820;
        text-transform: uppercase;
        letter-spacing: 0.045em;
    }

    .detail-table tbody tr:last-child td {
        border-bottom: 0;
    }

    .detail-table tbody tr:hover td {
        background: #F8FAFD;
    }

    .focus-card-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 8px;
    }

    .focus-card {
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 12px;
        background:
            radial-gradient(circle at 100% 0%, color-mix(in srgb, var(--focus-accent, var(--tts-blue)) 9%, transparent), transparent 34%),
            #FFFFFF;
        min-width: 0;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.76);
    }

    .focus-name {
        color: #0F172A;
        font-size: 0.78rem;
        font-weight: 850;
        line-height: 1.2;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 6px;
    }

    .focus-icon {
        width: 26px;
        height: 26px;
        border-radius: 10px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: var(--focus-accent, var(--tts-blue));
        background: color-mix(in srgb, var(--focus-accent, var(--tts-blue)) 10%, #FFFFFF);
        border: 1px solid color-mix(in srgb, var(--focus-accent, var(--tts-blue)) 20%, #FFFFFF);
        flex: 0 0 26px;
    }

    .focus-icon svg {
        width: 1.05em;
        height: 1.05em;
        stroke-width: 1.9;
        display: block;
    }

    .focus-value {
        color: #0F172A;
        font-size: 1.02rem;
        font-weight: 880;
        line-height: 1.15;
        overflow-wrap: anywhere;
        margin-bottom: 8px;
    }

    .focus-meta {
        color: #667085;
        font-size: 0.72rem;
        line-height: 1.4;
    }

    .export-shell {
        background: #FFFFFF;
        border: 1px solid #D0D7E2;
        border-radius: 12px;
        padding: 14px 16px 16px 16px;
        box-shadow: none;
    }

    .export-shell-caption {
        color: #64748B;
        font-size: 0.79rem;
        line-height: 1.45;
        margin-bottom: 8px;
    }

    div[data-testid="stDownloadButton"] button {
        width: 100%;
        min-height: 46px;
        border-radius: 8px;
        white-space: normal;
        line-height: 1.25;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        color: #111827;
        box-shadow: none;
    }

    div[data-testid="stDownloadButton"] button:hover {
        background: #F9FAFB;
        border-color: #D1D5DB;
        color: #111827;
    }

    .export-card-title {
        color: #111827;
        font-size: 0.88rem;
        font-weight: 780;
        margin-bottom: 4px;
        line-height: 1.25;
    }

    .export-card-desc {
        color: #64748B;
        font-size: 0.78rem;
        line-height: 1.35;
        min-height: 42px;
        margin-bottom: 8px;
    }

    .export-card-shell [data-testid="stVerticalBlockBorderWrapper"] {
        min-height: 164px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        background: #FFFFFF;
    }

    .export-card-shell [data-testid="stVerticalBlock"] {
        height: 100%;
    }

    .export-card-shell [data-testid="stDownloadButton"] {
        margin-top: auto;
    }

    /* Refined growth-console design system. */
    .stApp,
    .stApp * {
        letter-spacing: 0 !important;
    }

    h1.hero-title,
    h1.cover-logo-title {
        margin: 0;
    }

    h1.hero-title {
        color: #FFFFFF !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        background: linear-gradient(180deg, #F8F9FB 0%, #F2F4F7 100%);
    }

    .block-container {
        max-width: 1280px;
        padding-top: 2.2rem;
    }

    section[data-testid="stSidebar"] {
        background: #FAFBFC;
        border-right-color: #E3E7EC;
        box-shadow: 10px 0 28px rgba(16, 24, 40, 0.035);
    }

    section[data-testid="stSidebar"] div[data-testid="stExpander"] {
        border-color: #E1E6EC;
        border-radius: 8px;
        background: #FFFFFF;
        box-shadow: 0 2px 8px rgba(16, 24, 40, 0.025);
    }

    section[data-testid="stSidebar"] div[data-testid="stExpander"] details[open] {
        background: #FFFFFF;
    }

    .product-masthead {
        min-height: 52px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 0 1px 13px 1px;
        margin-bottom: 15px;
        border-bottom: 1px solid #E1E5EA;
    }

    #results-start {
        scroll-margin-top: 76px;
    }

    .product-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        min-width: 0;
    }

    .product-symbol {
        position: relative;
        width: 34px;
        height: 34px;
        flex: 0 0 34px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        background: #151922;
        border: 1px solid #282E38;
        border-radius: 8px;
        box-shadow: 0 6px 14px rgba(16, 24, 40, 0.13);
    }

    .product-symbol::before {
        content: "";
        position: absolute;
        inset: -1px 6px auto 6px;
        height: 2px;
        border-radius: 0 0 2px 2px;
        background: linear-gradient(90deg, var(--tts-cyan) 0 47%, var(--tts-red) 53% 100%);
    }

    .product-symbol svg {
        width: 18px;
        height: 18px;
        stroke-width: 1.9;
    }

    .product-brand-name {
        color: #131820;
        font-size: 0.94rem;
        font-weight: 820;
        line-height: 1.15;
    }

    .product-brand-subtitle {
        color: #7A8493;
        font-size: 0.68rem;
        font-weight: 680;
        line-height: 1.3;
        margin-top: 2px;
    }

    .product-masthead-meta {
        display: flex;
        align-items: center;
        gap: 9px;
        color: #697386;
        font-size: 0.68rem;
        font-weight: 700;
        white-space: nowrap;
    }

    .product-status {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        color: #13795B;
        padding: 6px 9px;
        border: 1px solid #D7E8E2;
        background: #F4FAF7;
        border-radius: 8px;
    }

    .product-status::before {
        content: "";
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #16A37E;
        box-shadow: 0 0 0 3px rgba(22, 163, 126, 0.10);
    }

    .cover-shell {
        padding-top: 8vh;
    }

    .cover-logo-title {
        font-size: 4.2rem;
        line-height: 1.02;
    }

    .cover-logo-kicker {
        color: #485364;
        background: #F0F2F5;
        border-color: #E1E5EA;
        border-radius: 8px;
    }

    .cover-bottom-row .stButton > button {
        border-radius: 8px;
        background: #151922;
        border: 1px solid #151922;
        box-shadow: 0 10px 24px rgba(16, 24, 40, 0.14);
    }

    .cover-bottom-row [data-testid="stNumberInputContainer"] input,
    .cover-bottom-row [data-testid="stNumberInputContainer"] button {
        border-radius: 8px;
    }

    .hero-band {
        background: linear-gradient(115deg, #12161E 0%, #1B202A 100%);
        border-color: #272E38;
        border-radius: 8px;
        padding: 26px 28px;
        margin: 0 0 20px 0;
        box-shadow: 0 16px 38px rgba(16, 24, 40, 0.15);
    }

    .hero-band::before {
        inset: 0 22px auto 22px;
        height: 3px;
        background: linear-gradient(90deg, var(--tts-cyan) 0 44%, rgba(255,255,255,0.22) 44% 56%, var(--tts-red) 56% 100%);
        border-radius: 0 0 3px 3px;
        opacity: 0.95;
    }

    .hero-title {
        font-size: 2.15rem;
        line-height: 1.04;
    }

    .hero-mark,
    .hero-kpi-icon {
        border-radius: 8px;
        background: rgba(255,255,255,0.07);
        border-color: rgba(255,255,255,0.14);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.10);
    }

    .hero-mark::after,
    .hero-kpi-icon::after,
    .premium-kpi-icon::after,
    .growth-path-icon::after,
    .growth-engine-mark::after,
    .growth-engine-step-icon::after {
        display: none;
    }

    .executive-insight-shell,
    .growth-engine-panel,
    .decision-panel,
    .premium-kpi,
    .growth-path-node,
    .diagnostic-card {
        background: #FFFFFF;
        border-color: #E0E5EB;
        border-radius: 8px;
        box-shadow: 0 7px 20px rgba(16, 24, 40, 0.04);
    }

    .executive-insight-icon,
    .growth-engine-mark {
        border-radius: 8px;
        background: #171B23;
        border-color: #2B313C;
        box-shadow: 0 7px 16px rgba(16, 24, 40, 0.13);
    }

    .executive-insight-kicker {
        color: #5E6979;
    }

    .model-live-chip {
        border-radius: 8px;
    }

    .premium-kpi::before {
        left: 0;
        right: auto;
        top: 15px;
        bottom: 15px;
        width: 2px;
        height: auto;
        border-radius: 0 2px 2px 0;
    }

    .premium-kpi-icon,
    .growth-path-icon,
    .growth-engine-step-icon {
        border-radius: 8px;
        background: #F4F6F8;
        border-color: #E1E6EC;
        box-shadow: none;
    }

    .growth-path-summary {
        background: #171B23;
        border-color: #272D37;
    }

    .growth-path-node::after,
    .growth-engine-step::after {
        background: #C8D0DA;
        opacity: 0.8;
    }

    .growth-engine-step {
        background: #FCFDFE;
        border-color: #E5E9EE;
        border-radius: 8px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.chart-card-title),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.sku-title) {
        background: #FFFFFF;
        border-color: #E0E5EB;
        border-radius: 8px;
        box-shadow: 0 8px 24px rgba(16, 24, 40, 0.045);
    }

    div[data-testid="stExpander"],
    div[data-testid="stExpander"] div[data-testid="stExpander"] {
        border-radius: 8px;
        background: #FFFFFF;
        box-shadow: 0 3px 10px rgba(16, 24, 40, 0.025);
    }

    div[data-testid="stNumberInput"] [data-baseweb="input"],
    div[data-testid="stTextInput"] [data-baseweb="input"],
    div[data-testid="stSelectbox"] [data-baseweb="select"],
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
    }

    div[data-testid="stNumberInput"] [data-baseweb="input"]:focus-within,
    div[data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
    div[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within {
        border-color: #475467 !important;
        box-shadow: 0 0 0 1px #475467 inset, 0 0 0 4px rgba(17, 24, 39, 0.06) !important;
    }

    .stButton > button {
        border-radius: 8px;
        transition: transform 120ms ease, border-color 120ms ease, background 120ms ease, box-shadow 120ms ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 14px rgba(16, 24, 40, 0.07);
    }

    /* Executive workspace refinement. */
    [data-testid="stAppViewContainer"] > .main {
        background: #F4F6F8;
    }

    [data-testid="stMain"] {
        scroll-behavior: smooth;
    }

    .block-container {
        padding-top: 1.55rem;
    }

    .product-masthead {
        min-height: 46px;
        padding-bottom: 10px;
        margin-bottom: 10px;
    }

    .workspace-nav {
        position: relative;
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 3px;
        padding: 4px;
        margin: 0;
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid #DCE2E9;
        border-radius: 8px;
        box-shadow: 0 8px 24px rgba(16, 24, 40, 0.075);
        backdrop-filter: blur(14px);
    }

    div[data-testid="stElementContainer"]:has(.workspace-nav) {
        position: sticky;
        top: 66px;
        z-index: 50;
        height: auto;
        margin-bottom: 10px;
    }

    .workspace-nav-link {
        --nav-accent: #315EEC;
        position: relative;
        overflow: hidden;
        min-width: 0;
        min-height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 7px;
        padding: 7px 9px;
        color: #596475 !important;
        border-radius: 6px;
        text-decoration: none !important;
        font-size: 0.72rem;
        font-weight: 750;
        line-height: 1;
        transition: color 120ms ease, background 120ms ease;
    }

    .workspace-nav-link:nth-child(2) {
        --nav-accent: #7257D9;
    }

    .workspace-nav-link:nth-child(3) {
        --nav-accent: #16836A;
    }

    .workspace-nav-link:nth-child(4) {
        --nav-accent: #D83B5F;
    }

    .workspace-nav-link::after {
        content: "";
        position: absolute;
        inset: auto 14px 0 14px;
        height: 2px;
        background: var(--nav-accent);
        opacity: 0;
        transition: opacity 120ms ease;
    }

    .workspace-nav-link:hover,
    .workspace-nav-link:focus-visible {
        color: #151A22 !important;
        background: #F1F3F6;
        outline: none;
    }

    [data-testid="stAppViewContainer"]:not(:has(.section-anchor:target)) .workspace-nav-link[href="#results-start"],
    [data-testid="stAppViewContainer"]:has(#results-start:target) .workspace-nav-link[href="#results-start"],
    [data-testid="stAppViewContainer"]:has(#phase-workspace:target) .workspace-nav-link[href="#phase-workspace"],
    [data-testid="stAppViewContainer"]:has(#action-workspace:target) .workspace-nav-link[href="#action-workspace"],
    [data-testid="stAppViewContainer"]:has(#export-workspace:target) .workspace-nav-link[href="#export-workspace"] {
        color: #151A22 !important;
        background: #F1F3F6;
    }

    [data-testid="stAppViewContainer"]:not(:has(.section-anchor:target)) .workspace-nav-link[href="#results-start"]::after,
    [data-testid="stAppViewContainer"]:has(#results-start:target) .workspace-nav-link[href="#results-start"]::after,
    [data-testid="stAppViewContainer"]:has(#phase-workspace:target) .workspace-nav-link[href="#phase-workspace"]::after,
    [data-testid="stAppViewContainer"]:has(#action-workspace:target) .workspace-nav-link[href="#action-workspace"]::after,
    [data-testid="stAppViewContainer"]:has(#export-workspace:target) .workspace-nav-link[href="#export-workspace"]::after {
        opacity: 1;
    }

    .workspace-nav-icon {
        width: 18px;
        height: 18px;
        flex: 0 0 18px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: var(--nav-accent);
    }

    .workspace-nav-icon svg {
        width: 17px;
        height: 17px;
        stroke-width: 1.85;
    }

    .section-anchor {
        height: 0;
        scroll-margin-top: 126px;
    }

    .sidebar-workspace-header {
        display: grid;
        grid-template-columns: 36px minmax(0, 1fr);
        gap: 10px;
        align-items: center;
        padding: 4px 0 14px 0;
        margin: 0 0 14px 0;
        border-bottom: 1px solid #E1E6EC;
    }

    .sidebar-workspace-icon {
        position: relative;
        width: 36px;
        height: 36px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        background: #151A22;
        border: 1px solid #29313C;
        border-radius: 8px;
        box-shadow: 0 6px 14px rgba(16, 24, 40, 0.12);
    }

    .sidebar-workspace-icon::before {
        content: "";
        position: absolute;
        inset: -1px 7px auto 7px;
        height: 2px;
        background: linear-gradient(90deg, var(--tts-cyan) 0 48%, var(--tts-red) 52% 100%);
    }

    .sidebar-workspace-icon svg {
        width: 18px;
        height: 18px;
        stroke-width: 1.9;
    }

    section[data-testid="stSidebar"] h2.sidebar-workspace-title {
        margin: 0;
        padding: 0;
        color: #151A22;
        font-size: 0.94rem;
        font-weight: 810;
        line-height: 1.2;
    }

    .sidebar-workspace-subtitle {
        margin-top: 3px;
        color: #7A8493;
        font-size: 0.67rem;
        font-weight: 620;
        line-height: 1.35;
    }

    .hero-band {
        grid-template-columns: minmax(280px, 0.9fr) minmax(0, 1.1fr);
        gap: 20px;
        padding: 22px 24px;
        margin-bottom: 12px;
        background: #131820;
        border-color: #29313C;
        box-shadow: 0 12px 30px rgba(16, 24, 40, 0.14);
    }

    .hero-copy {
        grid-template-columns: 42px minmax(0, 1fr);
        gap: 13px;
        align-items: center;
    }

    .hero-mark {
        width: 42px;
        height: 42px;
    }

    h1.hero-title {
        font-size: 2rem;
        line-height: 1.08;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        max-width: 38rem;
        font-size: 0.86rem;
        line-height: 1.48;
    }

    .hero-metrics {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        align-items: stretch;
        min-width: 0;
        border-left: 1px solid rgba(255,255,255,0.14);
    }

    .hero-kpi {
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-width: 0;
        padding: 2px 8px;
        border-left-color: rgba(255,255,255,0.14);
    }

    .hero-kpi:first-child {
        border-left: 0;
    }

    .hero-kpi-icon {
        width: 30px;
        height: 30px;
        margin-bottom: 8px;
    }

    .hero-kpi-label {
        margin-bottom: 5px;
        font-size: 0.64rem;
    }

    .hero-kpi-value {
        font-size: 0.98rem;
        white-space: nowrap;
    }

    .hero-kpi-value,
    .outcome-context-value,
    .growth-path-value,
    .growth-engine-step-value,
    .premium-kpi-value,
    .focus-value,
    input {
        font-variant-numeric: tabular-nums;
        font-feature-settings: "tnum" 1;
    }

    .executive-insight-shell {
        padding: 13px 15px;
        margin: 0 0 14px 0;
        box-shadow: 0 4px 14px rgba(16, 24, 40, 0.035);
    }

    .outcome-context-strip {
        margin: 10px 0 16px 0;
    }

    .outcome-context-card {
        border-color: #DCE2E9;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.025);
    }

    .outcome-context-card:nth-child(1) .outcome-context-icon {
        color: #315EEC;
    }

    .outcome-context-card:nth-child(2) .outcome-context-icon {
        color: #7257D9;
    }

    .outcome-context-card:nth-child(3) .outcome-context-icon {
        color: #16836A;
    }

    .section-shell {
        margin-top: 28px;
        padding-bottom: 8px;
    }

    .section-title {
        font-size: 1.34rem;
    }

    .chart-card-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 10px;
    }

    .chart-card-heading {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        min-width: 0;
    }

    .chart-card-icon {
        width: 34px;
        height: 34px;
        flex: 0 0 34px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #315EEC;
        background: #F3F6FF;
        border: 1px solid #DCE4F8;
        border-radius: 8px;
    }

    .chart-card-icon svg {
        width: 18px;
        height: 18px;
        stroke-width: 1.9;
    }

    .chart-card-copy {
        min-width: 0;
    }

    .chart-card-kicker {
        margin-bottom: 4px;
    }

    .chart-card-legends {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-end;
        gap: 7px 12px;
        max-width: 58%;
        padding-top: 3px;
    }

    .chart-legend-item {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: #697386;
        font-size: 0.66rem;
        font-weight: 680;
        line-height: 1.2;
        white-space: nowrap;
    }

    .chart-legend-swatch {
        width: 16px;
        flex: 0 0 16px;
        color: var(--legend-color);
    }

    .chart-legend-swatch.line {
        height: 2px;
        background: currentColor;
        border-radius: 2px;
    }

    .chart-legend-swatch.band {
        height: 8px;
        background: currentColor;
        border: 1px solid color-mix(in srgb, currentColor 42%, white);
        border-radius: 2px;
        opacity: 0.72;
    }

    .chart-legend-swatch.dash {
        height: 0;
        border-top: 2px dashed currentColor;
    }

    .action-group {
        position: relative;
        overflow: hidden;
        border-color: #DCE2E9;
        box-shadow: 0 5px 18px rgba(16, 24, 40, 0.035);
    }

    .action-group::before {
        content: "";
        position: absolute;
        inset: 0 auto 0 0;
        width: 2px;
        background: var(--action-accent);
    }

    .action-group-head {
        display: flex;
        align-items: center;
        gap: 9px;
        padding-bottom: 12px;
        border-bottom: 1px solid #E8ECF1;
    }

    .action-group-icon {
        width: 32px;
        height: 32px;
        flex: 0 0 32px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: var(--action-accent);
        background: #F4F6F8;
        border: 1px solid #E1E6EC;
        border-radius: 8px;
    }

    .action-group-icon svg {
        width: 17px;
        height: 17px;
        stroke-width: 1.9;
    }

    .action-group-title {
        margin: 0;
        padding: 0;
        border: 0;
    }

    .action-group-item {
        position: relative;
        padding-left: 17px;
    }

    .action-group-item::before {
        content: "";
        position: absolute;
        left: 1px;
        top: 0.72em;
        width: 6px;
        height: 6px;
        border: 2px solid var(--action-accent);
        border-radius: 50%;
        transform: translateY(-50%);
    }

    .st-key-selected_phase_view_control,
    div[class*="st-key-phase_chart_mode_"][class*="_control"] {
        gap: 4px !important;
        padding: 4px;
        background: #E9EDF2;
        border: 1px solid #DDE3EA;
        border-radius: 8px;
    }

    .st-key-selected_phase_view_control [data-testid="stButton"],
    div[class*="st-key-phase_chart_mode_"][class*="_control"] [data-testid="stButton"] {
        flex: 1 1 0;
        min-width: 0;
    }

    .st-key-selected_phase_view_control [data-testid="stButton"] button,
    div[class*="st-key-phase_chart_mode_"][class*="_control"] [data-testid="stButton"] button {
        position: relative;
        overflow: hidden;
        min-height: 42px;
        border: 0 !important;
        background: transparent !important;
        color: #596475 !important;
        box-shadow: none !important;
        transform: none !important;
    }

    .st-key-selected_phase_view_control [data-testid="stButton"] button[kind="primary"],
    div[class*="st-key-phase_chart_mode_"][class*="_control"] [data-testid="stButton"] button[kind="primary"] {
        background: #151A22 !important;
        color: #FFFFFF !important;
        box-shadow: 0 3px 8px rgba(16, 24, 40, 0.16) !important;
    }

    .st-key-selected_phase_view_control [data-testid="stButton"] button[kind="primary"]::after {
        content: "";
        position: absolute;
        inset: 0 18px auto 18px;
        height: 2px;
        background: linear-gradient(90deg, var(--tts-cyan) 0 48%, var(--tts-red) 52% 100%);
    }

    .st-key-selected_phase_view_control [data-testid="stIconMaterial"],
    div[class*="st-key-phase_chart_mode_"][class*="_control"] [data-testid="stIconMaterial"] {
        font-size: 1.05rem;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.chart-card-title) {
        border-color: #DCE2E9;
        box-shadow: 0 6px 22px rgba(16, 24, 40, 0.04);
    }

    /* Premium analytics workspace. */
    :root {
        --workspace-border: #D8DEE7;
        --workspace-divider: #E7EBF0;
        --workspace-surface: #FFFFFF;
        --workspace-shadow: 0 10px 28px rgba(16, 24, 40, 0.065);
    }

    section[data-testid="stSidebar"] {
        background: #F8F9FB;
        border-right-color: #DEE3EA;
        box-shadow: 8px 0 26px rgba(16, 24, 40, 0.035);
    }

    .product-masthead {
        border-bottom-color: var(--workspace-border);
    }

    .workspace-nav {
        gap: 4px;
        padding: 4px;
        background: #EDEFF3;
        border-color: #D9DFE7;
        box-shadow: var(--workspace-shadow);
    }

    .workspace-nav-link {
        min-height: 38px;
        border: 1px solid transparent;
        transition: color 140ms ease, background 140ms ease, border-color 140ms ease, box-shadow 140ms ease;
    }

    .workspace-nav-icon {
        width: 22px;
        height: 22px;
        flex-basis: 22px;
        color: var(--nav-accent);
        background: color-mix(in srgb, var(--nav-accent) 8%, #FFFFFF);
        border: 1px solid color-mix(in srgb, var(--nav-accent) 16%, #FFFFFF);
        border-radius: 6px;
    }

    .workspace-nav-icon svg {
        width: 14px;
        height: 14px;
    }

    [data-testid="stAppViewContainer"]:not(:has(.section-anchor:target)) .workspace-nav-link[href="#results-start"],
    [data-testid="stAppViewContainer"]:has(#results-start:target) .workspace-nav-link[href="#results-start"],
    [data-testid="stAppViewContainer"]:has(#phase-workspace:target) .workspace-nav-link[href="#phase-workspace"],
    [data-testid="stAppViewContainer"]:has(#action-workspace:target) .workspace-nav-link[href="#action-workspace"],
    [data-testid="stAppViewContainer"]:has(#export-workspace:target) .workspace-nav-link[href="#export-workspace"] {
        color: #111820 !important;
        background: #FFFFFF;
        border-color: #DDE2E9;
        box-shadow: 0 2px 7px rgba(16, 24, 40, 0.08);
    }

    .hero-band {
        background: #10151D;
        border-color: #252D38;
        box-shadow: 0 16px 36px rgba(16, 24, 40, 0.18);
    }

    .hero-mark {
        color: #8BE7E1;
        background: #19212B;
        border-color: #34404E;
    }

    .hero-kpi:nth-child(1) { --hero-accent: #6F9BFF; }
    .hero-kpi:nth-child(2) { --hero-accent: #63D2B3; }
    .hero-kpi:nth-child(3) { --hero-accent: #D3A0FF; }
    .hero-kpi:nth-child(4) { --hero-accent: #FF7892; }

    .hero-kpi-icon {
        color: var(--hero-accent, #FFFFFF);
        background: color-mix(in srgb, var(--hero-accent, #FFFFFF) 11%, #171D26);
        border-color: color-mix(in srgb, var(--hero-accent, #FFFFFF) 24%, #222A35);
    }

    .executive-insight-shell {
        border-left: 3px solid #171D26;
        box-shadow: 0 6px 18px rgba(16, 24, 40, 0.04);
    }

    .outcome-context-strip {
        gap: 0;
        overflow: hidden;
        background: var(--workspace-surface);
        border: 1px solid var(--workspace-border);
        border-radius: 8px;
        box-shadow: 0 3px 12px rgba(16, 24, 40, 0.035);
    }

    .outcome-context-card {
        padding: 13px 15px;
        background: transparent;
        border: 0;
        border-radius: 0;
        box-shadow: none;
    }

    .outcome-context-card + .outcome-context-card {
        border-left: 1px solid var(--workspace-divider);
    }

    .outcome-context-icon {
        border-radius: 6px;
    }

    .section-shell {
        position: relative;
        border-bottom-color: var(--workspace-border);
    }

    .section-shell::after {
        content: "";
        position: absolute;
        left: 0;
        bottom: -1px;
        width: 68px;
        height: 2px;
        background: linear-gradient(90deg, #315EEC 0 58%, #12A08C 58% 78%, #FE2C55 78% 100%);
    }

    h2.section-title {
        font-size: 1.5rem !important;
        font-weight: 780 !important;
        line-height: 1.2 !important;
    }

    .growth-path-node {
        border-color: var(--workspace-border);
        box-shadow: 0 6px 18px rgba(16, 24, 40, 0.04);
    }

    .growth-path-node::after {
        display: none;
    }

    .growth-path-node::before {
        content: "";
        position: absolute;
        inset: 0 0 auto 0;
        height: 3px;
        background: linear-gradient(
            90deg,
            var(--phase-accent, #315EEC) 0 var(--phase-share, 0%),
            #E7EBF0 var(--phase-share, 0%) 100%
        );
    }

    .growth-path-icon {
        color: var(--phase-accent, #315EEC);
        background: color-mix(in srgb, var(--phase-accent, #315EEC) 8%, #FFFFFF);
        border-color: color-mix(in srgb, var(--phase-accent, #315EEC) 18%, #FFFFFF);
    }

    .growth-path-summary::before {
        background: linear-gradient(90deg, var(--tts-cyan) 0 48%, rgba(255,255,255,0.26) 48% 54%, var(--tts-red) 54% 100%);
    }

    .growth-engine-panel {
        overflow: hidden;
        padding: 16px 0 0 0;
        border-color: var(--workspace-border);
        box-shadow: 0 8px 24px rgba(16, 24, 40, 0.045);
    }

    .growth-engine-header {
        padding: 0 16px;
        margin-bottom: 14px;
    }

    .growth-engine-grid {
        gap: 0;
        border-top: 1px solid var(--workspace-divider);
    }

    .growth-engine-step {
        min-height: 126px;
        padding: 15px;
        background: transparent;
        border: 0;
        border-radius: 0;
        box-shadow: none;
        overflow: visible;
    }

    .growth-engine-step + .growth-engine-step {
        border-left: 1px solid var(--workspace-divider);
    }

    .growth-engine-step::before {
        content: "";
        position: absolute;
        inset: 0 15px auto 15px;
        height: 2px;
        background: var(--step-accent, #315EEC);
        opacity: 0.72;
    }

    .growth-engine-step::after {
        display: none;
    }

    .growth-engine-step-icon {
        border-radius: 6px;
        color: var(--step-accent, #315EEC);
        background: color-mix(in srgb, var(--step-accent, #315EEC) 8%, #FFFFFF);
        border-color: color-mix(in srgb, var(--step-accent, #315EEC) 18%, #FFFFFF);
    }

    .decision-panel {
        padding: 0;
        background: transparent;
        border: 0;
        box-shadow: none;
    }

    .diagnostic-card,
    .focus-card {
        border-color: var(--workspace-border);
        box-shadow: 0 5px 16px rgba(16, 24, 40, 0.035);
    }

    .chart-card-icon {
        --chart-accent: #315EEC;
        color: var(--chart-accent);
        background: color-mix(in srgb, var(--chart-accent) 8%, #FFFFFF);
        border-color: color-mix(in srgb, var(--chart-accent) 18%, #FFFFFF);
        border-radius: 6px;
    }

    h3.chart-card-title {
        font-size: 1.1rem !important;
        font-weight: 780 !important;
        line-height: 1.2 !important;
    }

    .chart-card-icon-phase { --chart-accent: #7257D9; }
    .chart-card-icon-profit { --chart-accent: #16836A; }
    .chart-card-icon-target { --chart-accent: #D83B5F; }
    .chart-card-icon-channel { --chart-accent: #138D93; }
    .chart-card-icon-investment,
    .chart-card-icon-cost,
    .chart-card-icon-ads { --chart-accent: #C94C67; }
    .chart-card-icon-sample,
    .chart-card-icon-video { --chart-accent: #4B72D5; }

    .st-key-selected_phase_view_control,
    div[class*="st-key-phase_chart_mode_"][class*="_control"] {
        background: #EDEFF3;
        border-color: #D9DFE7;
    }

    .st-key-selected_phase_view_control [data-testid="stButton"] button[kind="primary"],
    div[class*="st-key-phase_chart_mode_"][class*="_control"] [data-testid="stButton"] button[kind="primary"] {
        background: #121820 !important;
        box-shadow: 0 4px 10px rgba(16, 24, 40, 0.18) !important;
    }

    @media (prefers-reduced-motion: reduce) {
        [data-testid="stMain"] {
            scroll-behavior: auto;
        }

        .stButton > button,
        .growth-path-node,
        .growth-engine-step {
            transition: none !important;
            transform: none !important;
        }
    }

    @media (max-width: 900px) {
        .cover-logo-title {
            font-size: 3.8rem;
        }

        .meeting-header-title {
            font-size: 2.1rem;
        }

        .chart-card-grid,
        .cover-cta-row,
        .cover-summary-grid,
        .hero-band,
        .decision-grid,
        .dashboard-intro,
        .executive-brief-grid,
        .readout-grid,
        .action-group-grid {
            grid-template-columns: 1fr;
        }

        .growth-path-strip,
        .growth-engine-grid,
        .focus-card-grid,
        .kpi-grid,
        .kpi-grid.kpi-grid-three,
        .kpi-grid.kpi-grid-four,
        .outcome-context-strip {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .growth-path-summary,
        .growth-engine-step:last-child,
        .outcome-context-card:last-child {
            grid-column: 1 / -1;
        }

        .growth-path-node::after,
        .growth-engine-step::after {
            display: none;
        }

        .growth-path-node,
        .growth-engine-step,
        .focus-card {
            padding: 11px;
        }

        .growth-path-title {
            font-size: 0.84rem;
        }

        .outcome-context-card {
            align-items: flex-start;
            padding: 11px;
        }

        .outcome-context-card:nth-child(3) {
            border-top: 1px solid var(--workspace-divider);
            border-left: 0;
        }

        .growth-engine-step + .growth-engine-step {
            border-left: 0;
        }

        .growth-engine-step:nth-child(even) {
            border-left: 1px solid var(--workspace-divider);
        }

        .growth-engine-step:nth-child(n + 3) {
            border-top: 1px solid var(--workspace-divider);
        }

        .growth-engine-step:last-child {
            border-left: 0;
        }

        .st-key-selected_phase_view_control,
        div[class*="st-key-phase_chart_mode_"][class*="_control"] {
            flex-wrap: nowrap !important;
        }

        .st-key-selected_phase_view_control [data-testid="stButton"] button,
        div[class*="st-key-phase_chart_mode_"][class*="_control"] [data-testid="stButton"] button {
            min-height: 42px;
            padding-left: 8px;
            padding-right: 8px;
        }

        .st-key-selected_phase_view_control [data-testid="stButton"] button p,
        div[class*="st-key-phase_chart_mode_"][class*="_control"] [data-testid="stButton"] button p {
            font-size: 0.78rem !important;
            white-space: nowrap !important;
        }

        .executive-insight-shell {
            grid-template-columns: 42px minmax(0, 1fr);
        }

        .model-live-chip {
            grid-column: 1 / -1;
            justify-self: start;
        }

        .section-shell {
            margin-top: 18px;
        }

        .workspace-nav {
            position: relative;
        }

        div[data-testid="stElementContainer"]:has(.workspace-nav) {
            position: sticky;
            top: 60px;
            margin-bottom: 10px;
        }

        .chart-card-header {
            flex-direction: column;
            gap: 9px;
        }

        .chart-card-legends {
            justify-content: flex-start;
            max-width: none;
            padding-left: 44px;
        }

        .hero-metrics {
            grid-template-columns: repeat(4, minmax(0, 1fr));
            padding-top: 14px;
            border-top: 1px solid rgba(255,255,255,0.15);
            border-left: 0;
        }

        .hero-kpi {
            border-top: 0;
            border-left: 1px solid rgba(255,255,255,0.14);
            padding: 0 12px;
        }

        .hero-kpi:first-child {
            border-left: 0;
        }

        .hero-copy {
            grid-template-columns: 42px minmax(0, 1fr);
        }

        .product-masthead {
            align-items: flex-start;
        }

        .product-masthead-meta > span:last-child {
            display: none;
        }

        [data-testid="stAppViewContainer"] > .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }

    @media (max-width: 600px) {
        .cover-logo-title {
            font-size: 3rem;
        }

        .meeting-header-title {
            font-size: 1.85rem;
        }

        h2.section-title {
            font-size: 1.28rem !important;
        }

        h3.chart-card-title {
            font-size: 1.05rem !important;
        }

        .funnel-card-value {
            font-size: 1.45rem;
        }

        .growth-engine-grid,
        .outcome-context-strip {
            grid-template-columns: 1fr;
        }

        .growth-engine-step:last-child,
        .outcome-context-card:last-child {
            grid-column: auto;
        }

        .outcome-context-card + .outcome-context-card,
        .outcome-context-card:nth-child(3) {
            border-top: 1px solid var(--workspace-divider);
            border-left: 0;
        }

        .growth-engine-step:nth-child(even),
        .growth-engine-step + .growth-engine-step {
            border-top: 1px solid var(--workspace-divider);
            border-left: 0;
        }

        .workspace-nav-link {
            min-height: 46px;
            flex-direction: column;
            gap: 3px;
            padding: 6px 3px;
            font-size: 0.61rem;
            line-height: 1.15;
            text-align: center;
        }

        .workspace-nav-icon {
            width: 20px;
            height: 20px;
            flex-basis: 20px;
        }

        .workspace-nav-icon svg {
            width: 13px;
            height: 13px;
        }

        .chart-card-legends {
            gap: 6px 10px;
            padding-left: 0;
        }

        .chart-legend-item {
            font-size: 0.61rem;
        }

        .hero-band {
            gap: 0;
            padding: 18px;
            margin-bottom: 14px;
        }

        .growth-path-node:nth-child(3) {
            grid-column: 1 / -1;
        }

        .hero-copy {
            grid-template-columns: 40px minmax(0, 1fr);
            gap: 12px;
            padding-bottom: 14px;
        }

        .hero-mark {
            width: 40px;
            height: 40px;
        }

        h1.hero-title {
            font-size: 1.95rem;
            line-height: 1.08;
            margin-bottom: 8px;
        }

        .hero-subtitle {
            font-size: 0.84rem;
            line-height: 1.45;
        }

        .hero-metrics {
            grid-template-columns: 1fr;
            padding-top: 0;
            border-top: 0;
        }

        .hero-kpi,
        .hero-kpi:first-child {
            display: grid;
            grid-template-columns: 30px minmax(0, 1fr) auto;
            grid-template-rows: auto auto;
            gap: 1px 10px;
            align-items: center;
            min-height: 52px;
            padding: 10px 0;
            border-left: 0;
            border-top-color: rgba(255,255,255,0.16);
        }

        .hero-kpi-icon {
            grid-row: 1 / 3;
            width: 30px;
            height: 30px;
            margin: 0;
        }

        .hero-kpi-label {
            grid-column: 2;
            margin: 0;
            font-size: 0.6rem;
            line-height: 1.2;
        }

        .hero-kpi-value {
            grid-column: 3;
            grid-row: 1 / 3;
            font-size: 0.98rem;
            text-align: right;
            white-space: nowrap;
        }

        .executive-insight-shell {
            gap: 10px;
            padding: 13px;
        }

        .debug-details-header {
            display: none;
        }

        .debug-details-row {
            grid-template-columns: 1fr;
            gap: 3px;
            padding: 10px 12px;
        }

        .debug-details-value {
            text-align: left;
        }
    }

    .sku-title {
        font-size: 1.02rem;
        font-weight: 790;
        color: #111827;
        margin-bottom: 0.32rem;
    }

    .sku-subtitle {
        color: #6B7280;
        font-size: 0.84rem;
        margin-bottom: 1rem;
        padding-bottom: 0.82rem;
        border-bottom: 1px solid #E8EDF4;
    }

    .premium-kpi,
    .meeting-header,
    .setup-gate,
    .export-shell,
    .chart-lens,
    .insight-strip,
    .readout-card,
    .executive-brief-card,
    .dashboard-intro-card,
    .support-panel,
    .report-appendix,
    .action-group,
    .readonly-rate {
        border-color: #D0D7E2;
    }

    div[data-testid="stPlotlyChart"] {
        background: transparent;
        border: 0;
        border-radius: 0;
        padding: 0;
        box-shadow: none !important;
    }

    div[data-testid="stPlotlyChart"] > div {
        min-height: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def phase_label(phase):
    return T[phase["key"]]


def category_label(category):
    return CATEGORY_LABELS.get(lang, {}).get(category, category)


def subcategory_label(subcategory):
    return SUBCATEGORY_LABELS.get(lang, {}).get(subcategory, subcategory)


def category_path_label(category, subcategory):
    return f"{category_label(category)} / {subcategory_label(subcategory)}"


def csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8-sig")


def dataframe_html(df):
    def cell_text(value):
        if value is None:
            return ""
        try:
            if pd.isna(value):
                return ""
        except (TypeError, ValueError):
            pass
        return str(value)

    header_html = "".join(f"<th scope=\"col\">{escape(str(column))}</th>" for column in df.columns)
    body_html = "".join(
        "<tr>"
        + "".join(f"<td>{escape(cell_text(value))}</td>" for value in row)
        + "</tr>"
        for row in df.itertuples(index=False, name=None)
    )
    return (
        '<div class="detail-table-shell">'
        '<div class="detail-table-scroll">'
        '<table class="detail-table">'
        f'<thead><tr>{header_html}</tr></thead>'
        f'<tbody>{body_html}</tbody>'
        '</table>'
        '</div>'
        '</div>'
    )


def get_preset(category, subcategory):
    return CATEGORY_PRESETS[category][subcategory]


def get_default_margin_pct(category):
    return CATEGORY_GROSS_MARGIN_DEFAULTS.get(category, 45.0)


def get_default_commissions(preset):
    organic = float(preset.get("organic_commission_pct", 10.0))
    paid = float(preset.get("paid_commission_pct", round(max(4.0, min(8.0, organic * 0.5)), 1)))
    return organic, paid


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
    st.session_state[f"gross_margin_pct_{i}"] = float(preset.get("gross_margin_pct", get_default_margin_pct(category)))
    organic_pct, paid_pct = get_default_commissions(preset)
    st.session_state[f"organic_commission_pct_{i}"] = float(organic_pct)
    st.session_state[f"paid_commission_pct_{i}"] = float(paid_pct)
    st.session_state[f"last_category_{i}"] = category
    st.session_state[f"last_subcategory_{i}"] = subcategory


def refresh_if_category_changed(i):
    if (
        st.session_state.get(f"last_category_{i}") != st.session_state[f"category_{i}"]
        or st.session_state.get(f"last_subcategory_{i}") != st.session_state[f"subcategory_{i}"]
    ):
        apply_category_defaults(i)


def handle_category_change(i):
    category = st.session_state[f"category_{i}"]
    subcategories = list(CATEGORY_PRESETS[category].keys())
    current_subcategory = st.session_state.get(f"subcategory_{i}")
    if current_subcategory not in subcategories:
        st.session_state[f"subcategory_{i}"] = subcategories[0]
    apply_category_defaults(i)


def handle_subcategory_change(i):
    apply_category_defaults(i)


def initialize_sku(i):
    default_profile = DEFAULT_SKU_PROFILES[i % len(DEFAULT_SKU_PROFILES)]
    if f"sku_name_{i}" not in st.session_state:
        st.session_state[f"sku_name_{i}"] = LETTERS[i]
    if f"category_{i}" not in st.session_state:
        st.session_state[f"category_{i}"] = default_profile["category"]

    category = st.session_state[f"category_{i}"]
    subcategories = list(CATEGORY_PRESETS[category].keys())
    if f"subcategory_{i}" not in st.session_state or st.session_state[f"subcategory_{i}"] not in subcategories:
        profile_subcategory = default_profile["subcategory"]
        st.session_state[f"subcategory_{i}"] = profile_subcategory if profile_subcategory in subcategories else subcategories[0]

    if f"aov_{i}" not in st.session_state:
        apply_category_defaults(i)
    if f"gross_margin_pct_{i}" not in st.session_state:
        st.session_state[f"gross_margin_pct_{i}"] = get_default_margin_pct(category)
    preset = get_preset(category, st.session_state[f"subcategory_{i}"])
    organic_pct, paid_pct = get_default_commissions(preset)
    if f"organic_commission_pct_{i}" not in st.session_state:
        st.session_state[f"organic_commission_pct_{i}"] = organic_pct
    if f"paid_commission_pct_{i}" not in st.session_state:
        st.session_state[f"paid_commission_pct_{i}"] = paid_pct


def preserve_setup_widget_state():
    """Keep hidden setup widgets intact while focus view is active."""
    prefixes = (
        "sku_name_", "category_", "subcategory_", "aov_", "gross_margin_pct_",
        "organic_commission_pct_", "paid_commission_pct_", "videos_per_sample_",
        "clicks_per_video_", "click_to_order_pct_", "shop_tab_share_pct_",
        "take_rate_", "samples_per_sku_",
    )
    exact_keys = {
        "promo_60d_input", "use_fbt_input", "weeks_per_phase_input",
        "logistics_carrier_cost_manual", "logistics_pick_pack_cost_manual",
        "logistics_return_allowance_manual", "sample_shipping_cost_manual",
        "sample_handling_cost_manual", "ads_roas_input", "organic_window_input",
        "target_gmv_input", "target_profit_input", "scenario_case_input",
        "brand_name_input", "scenario_name_input", "meeting_date_input",
        "am_name_input", "key_recommendation_input", "assumption_status_input",
    }
    for key in list(st.session_state.keys()):
        if key in exact_keys or any(key.startswith(prefix) for prefix in prefixes):
            st.session_state[key] = st.session_state[key]


def switch_to_client_view():
    st.session_state["meeting_mode_input"] = False
    st.session_state["selected_phase_view"] = PHASES[0]["key"]
    for phase in PHASES:
        st.session_state[f"phase_chart_mode_{phase['key']}"] = "cumulative"


def build_product_df(n_skus):
    rows = []
    for i in range(int(n_skus)):
        sku_name = str(st.session_state.get(f"sku_name_{i}", "")).strip() or LETTERS[i]
        rows.append({
            "SKU": sku_name,
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


def model_input_signature(
    product_df,
    phase_inputs,
    weeks_per_phase,
    promo_60d,
    use_fbt,
    logistics_carrier_cost,
    logistics_pick_pack_cost,
    logistics_return_allowance,
    logistics_cost,
    sample_delivery_cost,
    sample_handling_cost,
    sample_shipping_cost,
    ads_roas,
    organic_click_window_weeks,
    target_gmv,
    target_profit,
    scenario_case,
    assumption_status_key,
):
    return repr((
        int(weeks_per_phase),
        bool(promo_60d),
        bool(use_fbt),
        round(float(logistics_carrier_cost), 4),
        round(float(logistics_pick_pack_cost), 4),
        round(float(logistics_return_allowance), 4),
        round(float(logistics_cost), 4),
        round(float(sample_delivery_cost), 4),
        round(float(sample_handling_cost), 4),
        round(float(sample_shipping_cost), 4),
        round(float(ads_roas), 4),
        int(organic_click_window_weeks),
        round(float(target_gmv or 0), 2),
        round(float(target_profit or 0), 2),
        str(scenario_case),
        normalize_assumption_status(assumption_status_key),
        tuple(
            (phase["key"], round(float(phase["take_rate"]), 4), int(phase["samples_per_sku"]))
            for phase in phase_inputs
        ),
        product_df.round(6).to_json(orient="split"),
    ))


def apply_model_draft(
    product_df,
    phase_inputs,
    weeks_per_phase,
    promo_60d,
    use_fbt,
    logistics_carrier_cost,
    logistics_pick_pack_cost,
    logistics_return_allowance,
    logistics_cost,
    sample_delivery_cost,
    sample_handling_cost,
    sample_shipping_cost,
    ads_roas,
    organic_click_window_weeks,
    target_gmv,
    target_profit,
    scenario_case,
    assumption_status_key,
):
    st.session_state["_applied_product_df"] = product_df.copy()
    st.session_state["_applied_phase_inputs"] = [dict(phase) for phase in phase_inputs]
    st.session_state["_applied_weeks_per_phase"] = int(weeks_per_phase)
    st.session_state["_applied_promo_60d"] = bool(promo_60d)
    st.session_state["_applied_use_fbt"] = bool(use_fbt)
    st.session_state["_applied_logistics_carrier_cost"] = float(logistics_carrier_cost)
    st.session_state["_applied_logistics_pick_pack_cost"] = float(logistics_pick_pack_cost)
    st.session_state["_applied_logistics_return_allowance"] = float(logistics_return_allowance)
    st.session_state["_applied_logistics_cost"] = float(logistics_cost)
    st.session_state["_applied_sample_delivery_cost"] = float(sample_delivery_cost)
    st.session_state["_applied_sample_handling_cost"] = float(sample_handling_cost)
    st.session_state["_applied_sample_shipping_cost"] = float(sample_shipping_cost)
    st.session_state["_applied_ads_roas"] = float(ads_roas)
    st.session_state["_applied_organic_click_window_weeks"] = int(organic_click_window_weeks)
    st.session_state["_applied_target_gmv"] = float(target_gmv or 0)
    st.session_state["_applied_target_profit"] = float(target_profit or 0)
    st.session_state["_applied_scenario_case"] = scenario_case
    st.session_state["_applied_assumption_status"] = normalize_assumption_status(assumption_status_key)
    st.session_state["_applied_signature"] = model_input_signature(
        product_df=product_df,
        phase_inputs=phase_inputs,
        weeks_per_phase=weeks_per_phase,
        promo_60d=promo_60d,
        use_fbt=use_fbt,
        logistics_carrier_cost=logistics_carrier_cost,
        logistics_pick_pack_cost=logistics_pick_pack_cost,
        logistics_return_allowance=logistics_return_allowance,
        logistics_cost=logistics_cost,
        sample_delivery_cost=sample_delivery_cost,
        sample_handling_cost=sample_handling_cost,
        sample_shipping_cost=sample_shipping_cost,
        ads_roas=ads_roas,
        organic_click_window_weeks=organic_click_window_weeks,
        target_gmv=target_gmv,
        target_profit=target_profit,
        scenario_case=scenario_case,
        assumption_status_key=assumption_status_key,
    )


def effective_logistics_cost_per_unit(aov_values, logistics_cost, use_fbt):
    base_logistics_cost = float(logistics_cost)
    logistics_cost_per_unit = np.full(len(aov_values), base_logistics_cost)
    if use_fbt:
        logistics_cost_per_unit = np.where(np.asarray(aov_values) > FBT_FREE_SHIPPING_AOV_THRESHOLD, 0.0, base_logistics_cost)
    return logistics_cost_per_unit


def logistics_display_text(product_df, logistics_cost, use_fbt):
    if product_df is None or product_df.empty:
        return money(float(logistics_cost), 2)
    logistics_cost_per_unit = effective_logistics_cost_per_unit(product_df["AOV"].to_numpy(), logistics_cost, use_fbt)
    if not use_fbt:
        return money(float(logistics_cost), 2)
    if np.allclose(logistics_cost_per_unit, 0.0):
        return T["fbt_active_all"]
    if np.allclose(logistics_cost_per_unit, float(logistics_cost)):
        return T["fbt_active_none"].format(logistics=money(float(logistics_cost), 2))
    return T["fbt_active_mixed"].format(logistics=money(float(logistics_cost), 2))


def sku_fbt_status(aov, logistics_cost, use_fbt):
    effective_cost = float(effective_logistics_cost_per_unit(np.asarray([aov]), logistics_cost, use_fbt)[0])
    status = T["fbt_status_eligible"] if use_fbt and effective_cost == 0 else T["fbt_status_fallback"]
    return status, effective_cost


def logistics_detail_display(carrier_cost, pick_pack_cost, return_allowance):
    total = float(carrier_cost) + float(pick_pack_cost) + float(return_allowance)
    return T["logistics_detail_note"].format(
        total=money(total, 2),
        carrier=money(float(carrier_cost), 2),
        pick_pack=money(float(pick_pack_cost), 2),
        returns=money(float(return_allowance), 2),
    )


def sample_shipping_detail_display(shipping_cost, handling_cost):
    total = float(shipping_cost) + float(handling_cost)
    return T["sample_shipping_detail_note"].format(
        total=money(total, 2),
        shipping=money(float(shipping_cost), 2),
        handling=money(float(handling_cost), 2),
    )


@st.cache_data(show_spinner=False, max_entries=64)
def build_weekly_model(
    product_df,
    phase_inputs,
    weeks_per_phase,
    promo_60d,
    logistics_cost,
    sample_shipping_cost,
    use_fbt,
    organic_click_window_weeks,
    ads_roas,
    language_code,
):
    aov = product_df["AOV"].to_numpy()
    gross_margin = product_df["Gross Margin"].to_numpy()
    platform_fee_rates = product_df["Platform Fee Rate"].to_numpy()
    product_cost_per_unit = aov * (1 - gross_margin)
    logistics_cost_per_unit = effective_logistics_cost_per_unit(aov, logistics_cost, use_fbt)
    sample_all_in_cost_per_unit = product_cost_per_unit + float(sample_shipping_cost)

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
                raise ValueError("Paid growth budget x Ads ROAS must be below 90%.")

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
                "Phase": TEXT[language_code][phase["key"]],
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


def build_customer_summary(overall, phase_summary, weekly_be_label, cumulative_be_label, meeting_notes, assumption_status, cost_explanation_text, forecast_range, assumption_summary=None, next_actions=None):
    rows = [
        (T["brand_name"], meeting_notes.get("brand_name") or "-"),
        (T["scenario_name"], meeting_notes.get("scenario_name") or "-"),
        (T["meeting_date"], str(meeting_notes.get("meeting_date") or "-")),
        (T["am_name"], meeting_notes.get("am_name") or "-"),
        (T["model_version"], MODEL_VERSION),
        (T["assumption_status"], assumption_status),
        (T["key_recommendation"], meeting_notes.get("key_recommendation") or "-"),
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
    for label, value, _accent in assumption_summary or []:
        rows.append((f"{T['key_assumptions']} - {label}", value))
    for idx, action in enumerate(next_actions or [], start=1):
        rows.append((f"{T['next_actions']} {idx}", action))
    for _, phase_row in phase_summary.iterrows():
        rows.append((f"{phase_row['Phase']} {T['total_gmv']}", money(phase_row["GMV"], 0)))
        rows.append((f"{phase_row['Phase']} {T['total_profit']}", money(phase_row["Profit"], 0)))
    return pd.DataFrame(rows, columns=["Metric", "Value"])


ICON_SVG = {
    "trend": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 18.2h15" opacity=".28"/><path d="M5.2 15.9 9.6 11l3.6 3.2 5.8-7.1"/><path d="M15.2 7.1H19v3.8"/><circle cx="9.6" cy="11" r="1.15" fill="currentColor" stroke="none" opacity=".32"/><circle cx="13.2" cy="14.2" r="1.15" fill="currentColor" stroke="none" opacity=".32"/></svg>',
    "profit": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="7.6" opacity=".24"/><path d="M12 6.2v11.6"/><path d="M15.8 8.7c-.7-.9-1.9-1.5-3.6-1.5-2.1 0-3.5.9-3.5 2.4 0 3.5 7.2 1.6 7.2 5.1 0 1.5-1.5 2.5-3.8 2.5-1.7 0-3.2-.6-4-1.6"/><path d="M6.7 18.3 4.9 20"/><path d="M17.3 5.7 19.1 4"/></svg>',
    "investment": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 8.3h15v9.6h-15z" opacity=".28"/><path d="M5.2 9h13.6v8.2H5.2z"/><path d="M8.3 9V6.9h7.4V9"/><path d="M8.2 13.2h5.4"/><path d="M16.4 13.2h1.2"/><path d="M6.7 18.8 4.9 20.2"/><path d="M17.3 5.2l1.8-1.4"/></svg>',
    "target": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="7.5" opacity=".24"/><circle cx="12" cy="12" r="5.2"/><circle cx="12" cy="12" r="1.9" fill="currentColor" stroke="none" opacity=".42"/><path d="M12 3.2v2.3"/><path d="M20.8 12h-2.3"/><path d="M12 20.8v-2.3"/><path d="M3.2 12h2.3"/></svg>',
    "sample": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M5.5 8.5 12 4.8l6.5 3.7v7.4L12 19.6l-6.5-3.7z" opacity=".26"/><path d="M6.2 8.8 12 5.5l5.8 3.3v6.5L12 18.6l-5.8-3.3z"/><path d="m6.2 8.8 5.8 3.3 5.8-3.3"/><path d="M12 12.1v6.5"/><path d="m9 7.1 5.8 3.3"/></svg>',
    "ads": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M5.3 15.8V8.7l10.2-3v13.1z" opacity=".26"/><path d="M6 15.2V9.3l8.7-2.6v11.1z"/><path d="M14.7 9.5h2.3a2.7 2.7 0 0 1 0 5.4h-2.3"/><path d="m8.1 15.6 1.1 3.9"/><path d="M18.8 6.1 20.4 5"/><path d="M19.2 18.5l1.5 1.1"/></svg>',
    "channel": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 7h5.3v5.3H4.5z" opacity=".28"/><path d="M14.2 4.8h5.3v5.3h-5.3z" opacity=".28"/><path d="M14.2 14.4h5.3v4.8h-5.3z" opacity=".28"/><path d="M5.2 7.7h3.9v3.9H5.2z"/><path d="M14.9 5.5h3.9v3.9h-3.9z"/><path d="M14.9 15.1h3.9v3.4h-3.9z"/><path d="M9.1 9.7h2.4c1 0 1.7-.7 1.7-1.7v-.5"/><path d="M9.1 9.7h2.4c1 0 1.7.7 1.7 1.7v5.4"/></svg>',
    "cost": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M5.2 5.7h12.7v11.8H5.2z" opacity=".24"/><path d="M6 6.5h11.1v10.2H6z"/><path d="M8.2 9.3h6.8"/><path d="M8.2 12h5.2"/><path d="M8.2 14.7h3.5"/><path d="M16 16.3l3 3"/><path d="M19 16.3l-3 3"/></svg>',
    "phase": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M4 18h4v-4h4v-4h4V6h4" opacity=".3"/><path d="M4 18h4v-4h4v-4h4V6h4"/><path d="m17.5 3.5 2.5 2.5-2.5 2.5"/></svg>',
    "video": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="5" width="17" height="14" rx="2" opacity=".28"/><rect x="4.5" y="6" width="15" height="12" rx="1.5"/><path d="m10 9 5 3-5 3z" fill="currentColor" stroke="none" opacity=".48"/></svg>',
    "click": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="m6 3 11.2 8.4-5.1 1.3-2.5 5.1z" opacity=".3"/><path d="m6.8 4.5 9 6.7-4.3 1.1-2.1 4.2z"/><path d="m13.2 13.3 4.3 4.3"/><path d="M4 10H2.5M5.3 6.5 4.2 5.4M9.2 3.5V2"/></svg>',
    "order": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M5 8h14l-1 11H6z" opacity=".26"/><path d="M6 8h12l-.9 10H6.9z"/><path d="M9 9V7a3 3 0 0 1 6 0v2"/><path d="m10 13 1.4 1.4 3-3"/></svg>',
    "truck": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 6h11v10h-11z" opacity=".26"/><path d="M4.5 7h9v8h-9z"/><path d="M13.5 10h4l2.5 3v2h-6.5z"/><circle cx="8" cy="17" r="1.8"/><circle cx="17.5" cy="17" r="1.8"/></svg>',
    "spark": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3.8 13.7 9l5.2 1.8-5.2 1.8L12 18l-1.7-5.4-5.2-1.8L10.3 9z" opacity=".28"/><path d="M12 5.2 13.3 9l3.8 1.3-3.8 1.3L12 15.6l-1.3-4-3.8-1.3L10.7 9z"/><path d="M18 3.5v3"/><path d="M19.5 5h-3"/><path d="M5.8 17.3v2.2"/><path d="M6.9 18.4H4.7"/></svg>',
}


def icon_svg(name):
    return ICON_SVG.get(name, ICON_SVG["spark"])


def icon_for_label(label):
    label_text = str(label)
    if label_text in {T.get("total_gmv"), T.get("forecast_gmv"), T.get("hero_gmv"), T.get("gmv_per_sample"), T.get("sample_gmv_roi")}:
        return "trend"
    if label_text in {T.get("total_profit"), T.get("net_profit"), T.get("profit_per_sample"), T.get("weekly_profit")}:
        return "profit"
    if label_text in {T.get("growth_investment"), T.get("sample_investment"), T.get("hero_investment")}:
        return "investment"
    if label_text in {T.get("cumulative_be"), T.get("hero_break_even"), T.get("target_gmv"), T.get("target_profit")}:
        return "target"
    if label_text in {T.get("total_samples"), T.get("samples_label"), T.get("videos_per_sample_kpi"), T.get("orders_per_sample")}:
        return "sample"
    if label_text in {T.get("ads_investment"), T.get("take_rate"), T.get("ads_roas")}:
        return "ads"
    if label_text in {T.get("channel_mix"), T.get("affiliate_video_gmv"), T.get("shoptab_gmv")}:
        return "channel"
    if label_text in {T.get("cost_explanation"), T.get("cost_fulfillment"), T.get("total_cost_label")}:
        return "cost"
    return "spark"


def render_workspace_nav():
    items = [
        ("results-start", T.get("workspace_nav_overview", "Overview"), "trend"),
        ("phase-workspace", T.get("workspace_nav_phases", "Phases"), "phase"),
        ("action-workspace", T.get("workspace_nav_actions", "Actions"), "target"),
        ("export-workspace", T.get("workspace_nav_exports", "Export"), "investment"),
    ]
    links = "".join(
        f'<a class="workspace-nav-link" href="#{anchor}">'
        f'<span class="workspace-nav-icon">{icon_svg(icon)}</span>'
        f'<span>{escape(str(label))}</span></a>'
        for anchor, label, icon in items
    )
    st.markdown(
        f'<nav class="workspace-nav" aria-label="Growth workspace">{links}</nav>',
        unsafe_allow_html=True,
    )


def render_section_anchor(anchor):
    st.markdown(
        f'<div class="section-anchor" id="{escape(str(anchor))}"></div>',
        unsafe_allow_html=True,
    )


def render_sidebar_workspace_header():
    title = T.get("sidebar_console", T.get("plan_setup", "Plan Setup"))
    subtitle = T.get("sidebar_console_subtitle", T.get("setup_ready", "Configure the active growth plan"))
    st.markdown(
        '<div class="sidebar-workspace-header">'
        f'<div class="sidebar-workspace-icon">{icon_svg("phase")}</div>'
        '<div>'
        f'<h2 class="sidebar-workspace-title">{escape(title)}</h2>'
        f'<div class="sidebar-workspace-subtitle">{escape(subtitle)}</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )


def render_kpi_grid(items, compact=False, fixed_cols=None):
    cards = []
    for label, value, accent in items:
        accent_style = f' style="--kpi-accent:{escape(str(accent))};"' if accent else ""
        icon = icon_svg(icon_for_label(label))
        cards.append(
            f'<div class="premium-kpi"{accent_style}>'
            f'<div class="premium-kpi-top"><div class="premium-kpi-icon">{icon}</div>'
            f'<div class="premium-kpi-label">{escape(str(label))}</div></div>'
            f'<div class="premium-kpi-value">{escape(str(value))}</div>'
            "</div>"
        )
    class_names = ["kpi-grid"]
    if compact:
        class_names.append("kpi-grid-compact")
    if fixed_cols == 3:
        class_names.append("kpi-grid-three")
    if fixed_cols == 4:
        class_names.append("kpi-grid-four")
    class_name = " ".join(class_names)
    st.markdown(f'<div class="{class_name}">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_section_header(title, eyebrow=None):
    eyebrow_html = f'<div class="section-eyebrow">{escape(str(eyebrow))}</div>' if eyebrow else ""
    st.markdown(
        f'<div class="section-shell">{eyebrow_html}<h2 class="section-title">{escape(str(title))}</h2></div>',
        unsafe_allow_html=True,
    )


def set_segmented_button_value(state_key, option):
    st.session_state[state_key] = option


def render_segmented_buttons(options, state_key, format_func=str, help_func=None, icon_func=None):
    if not options:
        return None
    if state_key not in st.session_state:
        st.session_state[state_key] = options[0]
    selected = st.session_state.get(state_key, options[0])
    if selected not in options:
        selected = options[0]
        st.session_state[state_key] = selected
    with st.container(key=f"{state_key}_control", horizontal=True, gap="small"):
        for idx, option in enumerate(options):
            st.button(
                format_func(option),
                key=f"{state_key}__btn__{idx}",
                type="primary" if option == selected else "secondary",
                icon=icon_func(option) if icon_func else None,
                width="stretch",
                help=help_func(option) if help_func else None,
                on_click=set_segmented_button_value,
                args=(state_key, option),
            )
    return st.session_state[state_key]


def render_dashboard_intro(snapshot_text, diagnosis_text):
    html = (
        '<div class="dashboard-intro">'
        f'<div class="dashboard-intro-card"><div class="dashboard-intro-kicker">{escape(T["scenario_snapshot"])}</div>'
        f'<div class="dashboard-intro-text">{escape(str(snapshot_text))}</div></div>'
        f'<div class="dashboard-intro-card"><div class="dashboard-intro-kicker">{escape(T["diagnosis_summary"])}</div>'
        f'<div class="dashboard-intro-text">{escape(str(diagnosis_text))}</div></div>'
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_outcome_context(forecast_values, overall, previous_outcomes, target_gmv, target_profit):
    forecast_value = (
        f"{money(forecast_values['conservative_gmv'], 0)} – "
        f"{money(forecast_values['upside_gmv'], 0)}"
    )
    if previous_outcomes:
        change_value = T["model_change_value"].format(
            gmv=signed_money(float(overall["Total GMV"]) - float(previous_outcomes["gmv"])),
            profit=signed_money(float(overall["Total Profit"]) - float(previous_outcomes["profit"])),
        )
    else:
        change_value = T["baseline_model"]

    has_gmv_target = float(target_gmv or 0) > 0
    has_profit_target = float(target_profit or 0) > 0
    if has_gmv_target or has_profit_target:
        target_value = T["target_gap_value"].format(
            gmv=signed_money(float(overall["Total GMV"]) - float(target_gmv)) if has_gmv_target else "–",
            profit=signed_money(float(overall["Total Profit"]) - float(target_profit)) if has_profit_target else "–",
        )
    else:
        target_value = T["target_not_set_short"]

    items = [
        (T["forecast_band"], forecast_value, "trend"),
        (T["model_change"], change_value, "spark"),
        (T["target_gap"], target_value, "target"),
    ]
    cards = "".join(
        f'<div class="outcome-context-card">'
        f'<div class="outcome-context-icon">{icon_svg(icon)}</div>'
        f'<div><div class="outcome-context-label">{escape(label)}</div>'
        f'<div class="outcome-context-value">{escape(value)}</div></div></div>'
        for label, value, icon in items
    )
    st.markdown(f'<div class="outcome-context-strip">{cards}</div>', unsafe_allow_html=True)


def render_sidebar_meta(text):
    st.markdown(f'<div class="sidebar-meta">{escape(str(text))}</div>', unsafe_allow_html=True)


def render_sidebar_divider():
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)


def render_meeting_header(meeting_notes, generated_at, assumption_status):
    brand = str(meeting_notes.get("brand_name") or "").strip()
    scenario = str(meeting_notes.get("scenario_name") or "").strip()
    title = brand if brand else T["meeting_header"]
    subtitle = scenario if scenario else T["meeting_header"]
    date_text = str(meeting_notes.get("meeting_date") or generated_at.split(" ")[0])
    am_text = str(meeting_notes.get("am_name") or "-")
    html = (
        '<div class="meeting-header"><div>'
        f'<div class="meeting-header-kicker">{escape(subtitle)}</div>'
        f'<div class="meeting-header-title">{escape(title)}</div>'
        '</div><div class="meeting-header-meta">'
        f'{escape(T["meeting_date"])}: {escape(date_text)}<br>'
        f'{escape(T["am_name"])}: {escape(am_text)}<br>'
        f'<span class="meeting-badge">{escape(str(assumption_status))}</span>'
        '</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_product_masthead(updated_at):
    version_label = MODEL_VERSION.split("|")[0].strip()
    html = (
        '<div class="product-masthead">'
        '<div class="product-brand">'
        f'<div class="product-symbol">{icon_svg("trend")}</div>'
        '<div>'
        '<div class="product-brand-name">TikTok Shop</div>'
        f'<div class="product-brand-subtitle">{escape(T["product_console"])}</div>'
        '</div></div>'
        '<div class="product-masthead-meta">'
        f'<span class="product-status">{escape(T["live_model"])} · {escape(updated_at)}</span>'
        f'<span>{escape(version_label)}</span>'
        '</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_hero(overall, weeks, skus, break_even_label):
    subtitle = T["hero_subtitle"].format(
        gmv=money(overall["Total GMV"], 0),
        growth_investment=money(overall["Growth Investment"], 0),
        break_even=break_even_label,
    )
    html = (
        '<div class="hero-band"><div class="hero-copy">'
        f'<div class="hero-mark">{icon_svg("trend")}</div>'
        '<div>'
        f'<h1 class="hero-title">{escape(T["hero_title"].format(weeks=weeks, skus=skus))}</h1>'
        f'<div class="hero-subtitle">{escape(subtitle)}</div></div>'
        f'</div><div class="hero-metrics"><div class="hero-kpi"><div class="hero-kpi-icon">{icon_svg("trend")}</div><div class="hero-kpi-label">{escape(T["hero_gmv"])}</div><div class="hero-kpi-value">{money(overall["Total GMV"], 0)}</div></div>'
        f'<div class="hero-kpi"><div class="hero-kpi-icon">{icon_svg("profit")}</div><div class="hero-kpi-label">{escape(T["total_profit"])}</div><div class="hero-kpi-value">{money(overall["Total Profit"], 0)}</div></div>'
        f'<div class="hero-kpi"><div class="hero-kpi-icon">{icon_svg("investment")}</div><div class="hero-kpi-label">{escape(T["hero_investment"])}</div><div class="hero-kpi-value">{money(overall["Growth Investment"], 0)}</div></div>'
        f'<div class="hero-kpi"><div class="hero-kpi-icon">{icon_svg("target")}</div><div class="hero-kpi-label">{escape(T["hero_break_even"])}</div><div class="hero-kpi-value">{escape(break_even_label)}</div></div>'
        '</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_executive_insight(overall, df_all, cumulative_be_label, driver, updated_at):
    payback = (
        T["insight_payback_not_reached"]
        if cumulative_be_label == T["not_reached"]
        else T["insight_payback_reached"].format(week=cumulative_be_label)
    )
    insight = T["executive_insight_text"].format(
        payback=payback,
        channel=main_gmv_channel(df_all),
        driver=driver,
        margin=pct(float(overall["Profit Margin"]), 1),
    )
    html = (
        '<div class="executive-insight-shell">'
        f'<div class="executive-insight-icon">{icon_svg("spark")}</div>'
        '<div>'
        f'<div class="executive-insight-kicker">{escape(T["executive_insight"])}</div>'
        f'<div class="executive-insight-text">{escape(insight)}</div>'
        '</div>'
        f'<div class="model-live-chip">{escape(T["model_updated"])} · {escape(updated_at)}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_growth_path_strip(phase_summary, payback_label, driver):
    cards = []
    phase_accents = ("#315EEC", "#7257D9", "#16836A")
    max_phase_gmv = max((float(value) for value in phase_summary["GMV"]), default=0.0)
    for idx, (_, row) in enumerate(phase_summary.iterrows(), start=1):
        phase_accent = phase_accents[(idx - 1) % len(phase_accents)]
        phase_share = min(100.0, max(0.0, float(row["GMV"]) / max_phase_gmv * 100.0)) if max_phase_gmv else 0.0
        metrics = [
            (T["total_gmv"], money(row["GMV"], 0)),
            (T["total_profit"], money(row["Profit"], 0)),
        ]
        metric_html = "".join(
            f'<div><div class="growth-path-label">{escape(label)}</div><div class="growth-path-value">{escape(value)}</div></div>'
            for label, value in metrics
        )
        cards.append(
            f'<div class="growth-path-node" style="--phase-accent:{phase_accent};--phase-share:{phase_share:.1f}%;">'
            f'<div class="growth-path-kicker">Phase {idx}</div>'
            f'<div class="growth-path-heading"><div class="growth-path-icon">{icon_svg("phase")}</div>'
            f'<div class="growth-path-title">{escape(str(row["Phase"]))}</div></div>'
            f'<div class="growth-path-metrics">{metric_html}</div>'
            "</div>"
        )
    summary_metrics = [
        (T["cumulative_be"], payback_label),
        (T["cost_explanation"], driver),
    ]
    summary_html = "".join(
        f'<div><div class="growth-path-label">{escape(label)}</div><div class="growth-path-value">{escape(value)}</div></div>'
        for label, value in summary_metrics
    )
    cards.append(
        f'<div class="growth-path-node growth-path-summary" style="--phase-accent:#FE2C55;--phase-share:100%;">'
        f'<div class="growth-path-kicker">{escape(T["section_primary"])}</div>'
        f'<div class="growth-path-heading"><div class="growth-path-icon">{icon_svg("target")}</div>'
        f'<div class="growth-path-title">{escape(T["growth_profit_path"])}</div></div>'
        f'<div class="growth-path-metrics">{summary_html}</div>'
        "</div>"
    )
    st.markdown(f'<div class="growth-path-strip">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_growth_engine(overall):
    samples = float(overall.get("Total Samples", 0) or 0)
    videos = float(overall.get("Total Videos", 0) or 0)
    clicks = float(overall.get("Total Clicks", 0) or 0)
    orders = float(overall.get("Total Orders", 0) or 0)
    gmv = float(overall.get("Total GMV", 0) or 0)

    steps = [
        {
            "label": T["samples_label"],
            "value": f"{samples:,.0f}",
            "rate": T["growth_engine_rate"],
            "icon": "sample",
            "accent": "#315EEC",
        },
        {
            "label": T["videos_label"],
            "value": f"{videos:,.0f}",
            "rate": f"{videos / samples:.2f} {T['growth_engine_video_rate']}" if samples else "-",
            "icon": "video",
            "accent": "#25D7D2",
        },
        {
            "label": T["clicks_label"],
            "value": f"{clicks:,.0f}",
            "rate": f"{clicks / videos:,.0f} {T['growth_engine_click_rate']}" if videos else "-",
            "icon": "click",
            "accent": "#7C3AED",
        },
        {
            "label": T["orders_label"],
            "value": f"{orders:,.0f}",
            "rate": f"{pct(orders / clicks, 1)} {T['growth_engine_order_rate']}" if clicks else "-",
            "icon": "order",
            "accent": "#12A08C",
        },
        {
            "label": T["forecast_gmv"],
            "value": money(gmv, 0),
            "rate": f"{money(gmv / orders, 2)} {T['growth_engine_aov']}" if orders else "-",
            "icon": "trend",
            "accent": "#FE2C55",
        },
    ]
    step_html = []
    for step in steps:
        step_html.append(
            f'<div class="growth-engine-step" style="--step-accent:{escape(step["accent"])};">'
            '<div class="growth-engine-step-top">'
            f'<div class="growth-engine-step-icon">{icon_svg(step["icon"])}</div>'
            f'<div class="growth-engine-step-label">{escape(step["label"])}</div>'
            '</div>'
            f'<div class="growth-engine-step-value">{escape(step["value"])}</div>'
            f'<div class="growth-engine-step-rate">{escape(step["rate"])}</div>'
            '</div>'
        )
    html = (
        '<div class="growth-engine-panel">'
        '<div class="growth-engine-header">'
        '<div class="growth-engine-title-wrap">'
        f'<div class="growth-engine-mark">{icon_svg("spark")}</div>'
        '<div>'
        f'<div class="growth-engine-title">{escape(T["growth_engine"])}</div>'
        f'<div class="growth-engine-subtitle">{escape(T["growth_engine_subtitle"])}</div>'
        '</div></div></div>'
        f'<div class="growth-engine-grid">{"".join(step_html)}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def growth_bottleneck(overall, df_all):
    samples = float(overall.get("Total Samples", 0) or 0)
    videos = float(overall.get("Total Videos", 0) or 0)
    clicks = float(overall.get("Total Clicks", 0) or 0)
    orders = float(overall.get("Total Orders", 0) or 0)
    gmv = float(overall.get("Total GMV", 0) or 0)
    profit_margin = float(overall.get("Profit Margin", 0) or 0)
    sample_roi = float(overall.get("GMV / Sample Cost", 0) or 0)
    paid_share = float(df_all["Paid GMV Lift"].sum()) / gmv if gmv > 0 and "Paid GMV Lift" in df_all.columns else 0.0
    logistics_per_order = float(df_all["Fulfillment Cost"].sum()) / orders if orders > 0 and "Fulfillment Cost" in df_all.columns else 0.0
    videos_per_sample = videos / samples if samples > 0 else 0.0
    clicks_per_video = clicks / videos if videos > 0 else 0.0
    order_rate = orders / clicks if clicks > 0 else 0.0
    gmv_per_order = gmv / orders if orders > 0 else 0.0

    candidates = [
        (max(0.0, 0.08 - profit_margin) / 0.08, T["diagnostic_profit_title"], f"{T['profit_margin']}: {pct(profit_margin, 1)}", T["diagnostic_profit_action"], "profit"),
        (max(0.0, 5.0 - sample_roi) / 5.0, T["diagnostic_sample_title"], f"{T['sample_gmv_roi']}: {sample_roi:.1f}x", T["diagnostic_sample_action"], "sample"),
        (max(0.0, 1.20 - videos_per_sample) / 1.20, T["diagnostic_video_title"], f"{T['videos_per_sample_kpi']}: {videos_per_sample:.2f}", T["diagnostic_video_action"], "phase"),
        (max(0.0, 180.0 - clicks_per_video) / 180.0, T["diagnostic_click_title"], f"{T['growth_engine_click_rate']}: {clicks_per_video:,.0f}", T["diagnostic_click_action"], "channel"),
        (max(0.0, 0.08 - order_rate) / 0.08, T["diagnostic_conversion_title"], f"{T['click_order']}: {pct(order_rate, 1)}", T["diagnostic_conversion_action"], "target"),
        (max(0.0, 22.0 - gmv_per_order) / 22.0, T["diagnostic_order_value_title"], f"{T['growth_engine_aov']}: {money(gmv_per_order, 2)}", T["diagnostic_order_value_action"], "trend"),
        (max(0.0, logistics_per_order - 2.50) / 2.50, T["diagnostic_logistics_title"], f"{T['fulfillment']}: {money(logistics_per_order, 2)}", T["diagnostic_logistics_action"], "truck"),
        (max(0.0, paid_share - 0.35) / 0.35, T["diagnostic_paid_title"], f"{T['paid_gmv_increment']}: {pct(paid_share, 1)}", T["diagnostic_paid_action"], "ads"),
    ]
    score, title, signal, action, icon = max(candidates, key=lambda item: item[0])
    if score <= 0.04:
        return {
            "title": T["diagnostic_healthy_title"],
            "signal": f"{T['profit_margin']}: {pct(profit_margin, 1)} · {T['sample_gmv_roi']}: {sample_roi:.1f}x",
            "action": T["diagnostic_healthy_action"],
            "icon": "spark",
            "severity": T["diagnostic_good"],
            "accent": "#12A08C",
        }
    if score >= 0.45:
        severity = T["diagnostic_high"]
        accent = "#FE2C55"
    else:
        severity = T["diagnostic_attention"]
        accent = "#F59E0B"
    return {
        "title": title,
        "signal": signal,
        "action": action,
        "icon": icon,
        "severity": severity,
        "accent": accent,
    }


def render_decision_panel(overall, df_all, cumulative_be_label, driver):
    bottleneck = growth_bottleneck(overall, df_all)
    diagnostic_html = (
        f'<div class="diagnostic-card" style="--diagnostic-accent:{escape(bottleneck["accent"])};">'
        '<div class="diagnostic-top">'
        f'<div><div class="diagnostic-name">{escape(bottleneck["title"])}</div></div>'
        f'<div class="diagnostic-pill">{escape(bottleneck["severity"])}</div>'
        '</div>'
        f'<div class="diagnostic-signal">{escape(T["diagnostic_current"])}: {escape(bottleneck["signal"])}</div>'
        f'<div class="diagnostic-action">{escape(T["diagnostic_action"])}: {escape(bottleneck["action"])}</div>'
        '</div>'
    )
    focus_items = [
        (T["focus_payback"], cumulative_be_label, f"{T['total_profit']}: {money(overall['Total Profit'], 0)}", "target", "#315EEC"),
        (T["focus_driver"], main_gmv_channel(df_all), f"{T['forecast_gmv']}: {money(overall['Total GMV'], 0)}", "trend", "#12A08C"),
        (T["focus_efficiency"], f"{float(overall['GMV / Sample Cost']):.1f}x", f"{T['profit_margin']}: {pct(float(overall['Profit Margin']), 1)}", "spark", "#7C3AED"),
        (T["focus_cost"], driver, f"{T['total_cost_label']}: {money(overall['Total Cost'], 0)}", "cost", "#FE2C55"),
    ]
    focus_cards = []
    for label, value, meta, icon, accent in focus_items:
        focus_cards.append(
            f'<div class="focus-card" style="--focus-accent:{escape(accent)};">'
            f'<div class="focus-name"><span>{escape(label)}</span><span class="focus-icon">{icon_svg(icon)}</span></div>'
            f'<div class="focus-value">{escape(str(value))}</div>'
            f'<div class="focus-meta">{escape(str(meta))}</div>'
            '</div>'
        )
    html = (
        '<div class="decision-grid">'
        '<div class="decision-panel">'
        f'<div class="decision-panel-title"><div class="premium-kpi-icon" style="--kpi-accent:{escape(bottleneck["accent"])};">{icon_svg(bottleneck["icon"])}</div><span>{escape(T["growth_diagnostics"])}</span></div>'
        f'<div class="decision-panel-subtitle">{escape(T["growth_diagnostics_subtitle"])}</div>'
        f'{diagnostic_html}</div>'
        '<div class="decision-panel">'
        f'<div class="decision-panel-title"><div class="premium-kpi-icon" style="--kpi-accent:#315EEC;">{icon_svg("target")}</div><span>{escape(T["decision_focus"])}</span></div>'
        f'<div class="decision-panel-subtitle">{escape(T["decision_focus_subtitle"])}</div>'
        f'<div class="focus-card-grid">{"".join(focus_cards)}</div>'
        '</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_cover_page(default_skus):
    lang_tag = {
        "en": "DE planning model",
        "zh": "DE planning model",
        "de": "DE Planungsmodell",
        "nl": "DE planningsmodel",
    }.get(lang, "DE planning model")
    st.markdown(
        f"""
        <div class="cover-shell">
            <div class="cover-logo-row">
                <div class="cover-logo-meta">
                    <div class="cover-logo-kicker">{escape(lang_tag)}</div>
                    <h1 class="cover-logo-title">{escape(T["meeting_header"])}</h1>
                    <div class="cover-logo-subtitle">{escape(T["caption"])}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_assumption_summary(phase_inputs, weeks_per_phase, n_skus, logistics_display, sample_shipping_cost, ads_roas, organic_click_window_weeks, promo_60d, use_fbt):
    samples = " / ".join(str(int(phase["samples_per_sku"])) for phase in phase_inputs)
    take_rates = " / ".join(pct(float(phase["take_rate"]), 0) for phase in phase_inputs)
    yes = T["yes"]
    no = T["no"]
    return [
        (
            T["assumption_phase_plan"],
            T["assumption_phase_plan_value"].format(
                weeks=int(weeks_per_phase),
                samples=samples,
                take_rates=take_rates,
            ),
            "#315EEC",
        ),
        (
            T["assumption_operating"],
            T["assumption_operating_value"].format(
                skus=int(n_skus),
                logistics=logistics_display,
                sample_shipping=money(float(sample_shipping_cost), 2),
                organic_window=int(organic_click_window_weeks),
            ),
            "#178A62",
        ),
        (
            T["assumption_growth"],
            T["assumption_growth_value"].format(
                ads_roas=f"{float(ads_roas):.1f}",
                promo=yes if promo_60d else no,
                fbt=yes if use_fbt else no,
            ),
            "#4F46E5",
        ),
    ]


def commercial_takeaways(overall, df_all, cumulative_be_label, driver):
    return [
        (T["investment_required"], money(overall["Growth Investment"], 0)),
        (T["expected_gmv"], money(overall["Total GMV"], 0)),
        (T["payback_timing"], cumulative_be_label),
        (T["main_upside_lever"], main_gmv_channel(df_all)),
        (T["main_risk"], T["main_risk_text"].format(driver=driver)),
    ]


def business_readout_items(overall, df_all, cumulative_be_label, driver):
    profit_key = "business_readout_profit_positive" if float(overall["Total Profit"]) >= 0 else "business_readout_profit_negative"
    return [
        (
            T["business_readout_profit"],
            T[profit_key].format(driver=driver),
            "#178A62" if float(overall["Total Profit"]) >= 0 else "#B42318",
        ),
        (
            T["business_readout_growth"],
            T["business_readout_growth_text"].format(
                channel=main_gmv_channel(df_all),
                samples=f"{overall['Total Samples']:,.0f}",
                videos=f"{overall['Total Videos']:,.0f}",
            ),
            "#315EEC",
        ),
        (
            T["business_readout_payback"],
            T["business_readout_payback_text"].format(
                break_even=cumulative_be_label,
                sample_roi=f"{overall['GMV / Sample Cost']:.1f}",
            ),
            "#4F46E5",
        ),
    ]


def executive_brief_items(overall, df_all, weekly_be_label, cumulative_be_label, driver):
    main_channel = main_gmv_channel(df_all)
    return [
        (
            T["growth_investment"],
            T["executive_brief_investment"].format(
                total=money(overall["Growth Investment"], 0),
                samples=money(overall["Sample Investment"], 0),
                ads=money(overall["Ads Investment"], 0),
            ),
        ),
        (
            T["sample_roi_title"],
            T["executive_brief_sample"].format(
                gmv=money(overall["GMV / Sample"], 0),
                profit=money(overall["Profit / Sample"], 0),
            ),
        ),
        (
            T["diagnosis_summary"],
            T["executive_brief_diagnosis"].format(
                channel=main_channel,
                weekly_be=weekly_be_label,
                cumulative_be=cumulative_be_label,
                driver=driver,
            ),
        ),
    ]


def diagnosis_summary(overall, df_all, driver):
    sample_roi = float(overall["GMV / Sample Cost"])
    total_profit = float(overall["Total Profit"])
    total_gmv = float(overall["Total GMV"])
    paid_gmv = float(df_all["Paid GMV Lift"].sum()) if "Paid GMV Lift" in df_all.columns else 0.0
    if total_profit < 0:
        return T["diagnosis_negative"].format(driver=driver)
    if total_gmv > 0 and paid_gmv / total_gmv >= 0.30:
        return T["diagnosis_ads_heavy"]
    if sample_roi >= 8.0:
        return T["diagnosis_sample_strong"].format(driver=driver)
    return T["diagnosis_profitable"].format(driver=driver, sample_roi=f"{sample_roi:.1f}")


def target_comparison_items(overall, target_gmv, target_profit):
    items = []
    target_gmv = float(target_gmv or 0)
    target_profit = float(target_profit or 0)
    if target_gmv > 0:
        gap = float(overall["Total GMV"]) - target_gmv
        label = T["target_met"] if gap >= 0 else T["target_gap"]
        items.append((T["target_gmv"], label if gap >= 0 else money(abs(gap), 0), "#315EEC" if gap >= 0 else "#6B7280"))
    if target_profit > 0:
        gap = float(overall["Total Profit"]) - target_profit
        label = T["target_met"] if gap >= 0 else T["target_gap"]
        items.append((T["target_profit"], label if gap >= 0 else money(abs(gap), 0), "#178A62" if gap >= 0 else "#B42318"))
    return items


def debug_details_html(overall, scenario_key, effective_ads_roas, target_gmv, target_profit, n_skus, locked):
    factors = SCENARIO_ADJUSTMENTS.get(scenario_key, SCENARIO_ADJUSTMENTS["base"])
    target_gmv = float(target_gmv or 0)
    target_profit = float(target_profit or 0)
    gmv_gap = float(overall["Total GMV"]) - target_gmv if target_gmv > 0 else None
    profit_gap = float(overall["Total Profit"]) - target_profit if target_profit > 0 else None
    rows = [
        (T["scenario_case"], {
            "conservative": T["scenario_conservative"],
            "base": T["scenario_base"],
            "upside": T["scenario_upside"],
        }.get(scenario_key, T["scenario_base"])),
        (T["debug_multiplier_clicks"], f"{factors['clicks']:.2f}x"),
        (T["debug_multiplier_cvr"], f"{factors['conversion']:.2f}x"),
        (T["debug_multiplier_roas"], f"{factors['roas']:.2f}x"),
        (T["debug_effective_roas"], f"{float(effective_ads_roas):.2f}"),
        (T["debug_lock_status"], T["yes"] if locked else T["no"]),
        (T["debug_target_gmv_gap"], money(gmv_gap, 0) if gmv_gap is not None else T["target_not_set"]),
        (T["debug_target_profit_gap"], money(profit_gap, 0) if profit_gap is not None else T["target_not_set"]),
        (T["sku_count"], f"{int(n_skus)}"),
        (T["model_version"], MODEL_VERSION),
        (T["model_last_reviewed"], MODEL_LAST_REVIEWED),
    ]
    row_html = "".join(
        '<div class="debug-details-row" role="row">'
        f'<span class="debug-details-label" role="cell">{escape(str(label))}</span>'
        f'<span class="debug-details-value" role="cell">{escape(str(value))}</span>'
        '</div>'
        for label, value in rows
    )
    return (
        '<div class="debug-details-grid" role="table">'
        '<div class="debug-details-header" role="row">'
        f'<span role="columnheader">{escape(T["debug_metric"])}</span>'
        f'<span role="columnheader">{escape(T["debug_value"])}</span>'
        '</div>'
        f'{row_html}'
        '</div>'
    )


def apply_scenario_adjustment(product_df, ads_roas, scenario_key):
    adjusted = product_df.copy()
    factors = SCENARIO_ADJUSTMENTS.get(scenario_key, SCENARIO_ADJUSTMENTS["base"])
    adjusted["Clicks / Video"] = adjusted["Clicks / Video"] * factors["clicks"]
    adjusted["Click-to-order Rate"] = (adjusted["Click-to-order Rate"] * factors["conversion"]).clip(upper=1.0)
    return adjusted, float(ads_roas) * factors["roas"]


def scenario_snapshot_text(n_skus, weeks_per_phase, phase_inputs, ads_roas, scenario_label):
    samples = " / ".join(str(int(phase["samples_per_sku"])) for phase in phase_inputs)
    take_rates = " / ".join(pct(float(phase["take_rate"]), 0) for phase in phase_inputs)
    return f"{int(n_skus)} SKUs · {int(weeks_per_phase) * len(PHASES)} weeks · {samples} samples/SKU/week · {take_rates} paid growth · ROAS {float(ads_roas):.1f}"


def forecast_range(overall, assumption_status):
    assumption_status_key = normalize_assumption_status(assumption_status)
    if assumption_status_key == "merchant_confirmed":
        spread = 0.08
    elif assumption_status_key == "am_aligned":
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


def recommended_next_actions(overall, df_all, phase_summary, product_df, cumulative_be, driver):
    actions = []
    if float(overall["GMV / Sample Cost"]) >= 5.0:
        actions.append(T["action_expand_samples"])
    if float(overall["Total Profit"]) < 0:
        actions.append(T["action_fix_profit"])
    paid_gmv = float(df_all["Paid GMV Lift"].sum()) if "Paid GMV Lift" in df_all.columns else 0.0
    if paid_gmv > float(overall["Total GMV"]) * 0.20 and float(overall["Ads Investment"]) > 0:
        actions.append(T["action_scale_ads"])
    shop_gmv = float(df_all["ShopTab GMV"].sum()) if "ShopTab GMV" in df_all.columns else 0.0
    if float(overall["Total GMV"]) > 0 and shop_gmv / float(overall["Total GMV"]) >= 0.30:
        actions.append(T["action_strengthen_store"])
    if product_df["Click-to-order Rate"].max() >= 0.06 or product_df["ShopTab GMV Share"].max() >= 0.45:
        actions.append(T["action_align_inputs"])
    if cumulative_be is None and T["action_fix_profit"] not in actions:
        actions.append(T["action_fix_profit"])
    actions.append(T["action_align_inputs"])

    unique_actions = []
    for action in actions:
        if action not in unique_actions:
            unique_actions.append(action)
    return unique_actions[:4] or [T["action_default"]]


def render_action_list(actions):
    items = [
        f'<div class="action-item"><span class="action-index">{idx}</span><span>{escape(str(action))}</span></div>'
        for idx, action in enumerate(actions, start=1)
    ]
    st.markdown(f'<div class="action-list">{"".join(items)}</div>', unsafe_allow_html=True)


def group_next_actions(actions):
    grouped = {
        T["action_group_validate"]: [],
        T["action_group_optimize"]: [],
        T["action_group_scale"]: [],
    }
    for action in actions:
        if action == T["action_align_inputs"]:
            grouped[T["action_group_validate"]].append(action)
        elif action in (T["action_fix_profit"], T["action_strengthen_store"]):
            grouped[T["action_group_optimize"]].append(action)
        elif action in (T["action_expand_samples"], T["action_scale_ads"]):
            grouped[T["action_group_scale"]].append(action)
        else:
            grouped[T["action_group_validate"]].append(action)
    return grouped


def render_grouped_actions(actions):
    cards = []
    group_styles = {
        T["action_group_validate"]: ("target", "#315EEC"),
        T["action_group_optimize"]: ("cost", "#D97706"),
        T["action_group_scale"]: ("trend", "#16836A"),
    }
    for title, items in group_next_actions(actions).items():
        icon, accent = group_styles.get(title, ("spark", "#315EEC"))
        body = "".join(
            f'<div class="action-group-item">{escape(str(item))}</div>'
            for item in (items or [T["action_no_immediate"]])
        )
        cards.append(
            f'<div class="action-group" style="--action-accent:{escape(accent)};">'
            '<div class="action-group-head">'
            f'<div class="action-group-icon">{icon_svg(icon)}</div>'
            f'<div class="action-group-title">{escape(str(title))}</div></div>{body}</div>'
        )
    st.markdown(f'<div class="action-group-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_business_readout(items):
    cards = []
    for title, body, _accent in items:
        cards.append(
            f'<div class="readout-card">'
            f'<div class="readout-title">{escape(str(title))}</div>'
            f'<div class="readout-body">{escape(str(body))}</div>'
            "</div>"
        )
    st.markdown(f'<div class="readout-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_executive_brief(items):
    cards = []
    for kicker, body in items:
        cards.append(
            f'<div class="executive-brief-card">'
            f'<div class="executive-brief-kicker">{escape(str(kicker))}</div>'
            f'<div class="executive-brief-body">{escape(str(body))}</div>'
            "</div>"
        )
    st.markdown(f'<div class="executive-brief-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


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


def render_insight(text, compact=False):
    class_name = "insight-strip compact" if compact else "insight-strip"
    st.markdown(
        f'<div class="{class_name}"><strong style="color:#111827;font-weight:720;">{T["chart_insight"]}</strong> {text}</div>',
        unsafe_allow_html=True,
    )


def render_chart_lens(title, body, compact=False):
    class_name = "chart-lens compact" if compact else "chart-lens"
    st.markdown(
        f'<div class="{class_name}">'
        f'<div class="chart-lens-title">{escape(str(title))}</div>'
        f'<div class="chart-lens-body">{escape(str(body))}</div>'
        "</div>",
        unsafe_allow_html=True,
    )


def render_chart_panel_header(title, subtitle=None, kicker=None, icon=None, legends=None):
    kicker_html = f'<div class="chart-card-kicker">{escape(str(kicker))}</div>' if kicker else ""
    subtitle_html = f'<div class="chart-card-subtitle">{escape(str(subtitle))}</div>' if subtitle else ""
    icon_name = icon if icon in ICON_SVG else "spark"
    icon_html = f'<div class="chart-card-icon chart-card-icon-{icon_name}">{icon_svg(icon_name)}</div>' if icon else ""
    legend_html = ""
    if legends:
        legend_items = []
        for label, color, swatch_type in legends:
            swatch_class = swatch_type if swatch_type in {"line", "band", "dash"} else "line"
            legend_items.append(
                f'<span class="chart-legend-item">'
                f'<span class="chart-legend-swatch {swatch_class}" style="--legend-color:{escape(str(color))};"></span>'
                f'<span>{escape(str(label))}</span></span>'
            )
        legend_html = f'<div class="chart-card-legends">{"".join(legend_items)}</div>'
    st.markdown(
        '<div class="chart-card-header">'
        f'<div class="chart-card-heading">{icon_html}<div class="chart-card-copy">'
        f'{kicker_html}<h3 class="chart-card-title">{escape(str(title))}</h3>{subtitle_html}'
        f'</div></div>{legend_html}</div>',
        unsafe_allow_html=True,
    )


def render_chart_panel_caption(caption):
    if st.session_state.get("meeting_mode_input", False) and st.session_state.get("has_generated", False):
        return
    st.markdown(
        f'<div class="inline-note"><details><summary>{escape(T["chart_read"])}</summary>'
        f'<div class="inline-note-body">{caption}</div></details></div>',
        unsafe_allow_html=True,
    )


def render_subtle_note(body, label=None):
    if st.session_state.get("meeting_mode_input", False) and st.session_state.get("has_generated", False):
        return
    summary = escape(str(label)) if label else escape(T["chart_read"])
    body_html = escape(str(body)).replace("\n", "<br>")
    st.markdown(
        f'<div class="inline-note"><details><summary>{summary}</summary>'
        f'<div class="inline-note-body">{body_html}</div></details></div>',
        unsafe_allow_html=True,
    )


def render_status_panel(title, body, tone="info", compact=False, kicker=None):
    class_name = f"status-panel {tone}" + (" compact" if compact else "")
    kicker_html = f'<div class="status-panel-kicker">{escape(str(kicker))}</div>' if kicker else ""
    title_text = escape(str(title))
    body_text = escape(str(body))
    if compact and not kicker:
        panel_html = (
            f'<div class="{class_name}">'
            f'<div class="status-panel-row"><div class="status-panel-row-title">{title_text}</div>'
            f'<div class="status-panel-row-body">{body_text}</div></div></div>'
        )
    else:
        panel_html = (
            f'<div class="{class_name}">{kicker_html}'
            f'<div class="status-panel-title">{title_text}</div>'
            f'<div class="status-panel-body">{body_text}</div></div>'
        )
    st.markdown(panel_html, unsafe_allow_html=True)


def render_model_logic():
    st.write(T["model_logic_intro"])
    for idx in range(1, 7):
        st.markdown(
            f'<div class="chart-lens">'
            f'<div class="chart-lens-title">{escape(T[f"model_logic_{idx}_title"])}</div>'
            f'<div class="chart-lens-body">{escape(T[f"model_logic_{idx}_body"])}</div>'
            f'<div style="margin-top:8px;color:#1D4ED8;font-weight:720;">{escape(T[f"model_logic_{idx}_formula"])}</div>'
            "</div>",
            unsafe_allow_html=True,
        )


def internal_logic_signals(product_df, phase_inputs, promo_60d, use_fbt, ads_roas):
    aov_values = product_df["AOV"].astype(float)
    total_skus = len(product_df)
    eligible_fbt = int((aov_values > 20).sum()) if use_fbt else 0
    fallback_skus = total_skus - eligible_fbt if use_fbt else total_skus
    take_rates = " / ".join(pct(float(phase["take_rate"]), 0) for phase in phase_inputs)
    paid_phases = sum(float(phase["take_rate"]) > 0 for phase in phase_inputs)
    avg_shop_share = float(product_df["ShopTab GMV Share"].mean()) if total_skus else 0.0
    max_shop_share = float(product_df["ShopTab GMV Share"].max()) if total_skus else 0.0

    items = [
        (
            T["internal_logic_fbt_title"],
            T["internal_logic_fbt_on"].format(
                eligible=eligible_fbt,
                total=total_skus,
                fallback=fallback_skus,
            ) if use_fbt else T["internal_logic_fbt_off"],
        ),
        (
            T["internal_logic_paid_title"],
            T["internal_logic_paid_text"].format(
                paid_phases=paid_phases,
                total_phases=len(phase_inputs),
                take_rates=take_rates,
                ads_roas=f"{float(ads_roas):.1f}",
            ),
        ),
        (
            T["internal_logic_channel_title"],
            T["internal_logic_channel_text"].format(
                avg_share=pct(avg_shop_share, 0),
                max_share=pct(max_shop_share, 0),
            ),
        ),
        (
            T["internal_logic_fee_title"],
            T["internal_logic_fee_on"].format(promo_weeks=PROMO_WEEKS) if promo_60d else T["internal_logic_fee_off"],
        ),
    ]
    return items


def plan_preview_text(n_skus, phase_inputs, weeks_per_phase, organic_click_window_weeks, ads_roas):
    samples = " / ".join(str(int(phase["samples_per_sku"])) for phase in phase_inputs)
    take_rates = " / ".join(pct(float(phase["take_rate"]), 0) for phase in phase_inputs)
    return T["plan_preview_text"].format(
        skus=int(n_skus),
        weeks=int(weeks_per_phase) * len(PHASES),
        samples=samples,
        take_rates=take_rates,
        organic_window=int(organic_click_window_weeks),
        ads_roas=f"{float(ads_roas):.1f}",
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
        T["cost_fulfillment"]: "#7C8EA3",
        T["cost_creator_commission"]: "#A78BFA",
        T["cost_platform_fee"]: "#94A3B8",
        T["cost_ads"]: "#315EEC",
        T["cost_samples"]: "#4F46E5",
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


def meeting_recap_html(overall, narrative, health_checks, path_text, weeks, skus, generated_at, meeting_notes, assumption_status, takeaways, cost_explanation_text, diagnosis_text, forecast_range_values, assumption_summary, next_actions):
    narrative_html = "".join(f"<li>{line}</li>" for line in narrative)
    health_html = "".join(f'<li class="{level}">{text}</li>' for level, text in health_checks)
    takeaways_html = "".join(f"<li><strong>{label}:</strong> {value}</li>" for label, value in takeaways)
    assumptions_html = "".join(f"<li><strong>{label}:</strong> {value}</li>" for label, value, _accent in assumption_summary)
    actions_html = "".join(f"<li>{action}</li>" for action in next_actions)
    notes_html = "".join(
        f"<li><strong>{label}:</strong> {value or '-'}</li>"
        for label, value in [
            (T["brand_name"], meeting_notes.get("brand_name")),
            (T["scenario_name"], meeting_notes.get("scenario_name")),
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
      <span>{T["model_version"]}: {MODEL_VERSION}</span>
    </div>
    <div class="hero">
      <h1>{(meeting_notes.get("brand_name") or T["hero_title"].format(weeks=weeks, skus=skus))}{(" · " + meeting_notes.get("scenario_name")) if meeting_notes.get("scenario_name") else ""}</h1>
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
      <h2>{T["diagnosis_summary"]}</h2>
      <p>{diagnosis_text}</p>
    </div>
    <div class="section">
      <h2>{T["key_assumptions"]}</h2>
      <ul>{assumptions_html}</ul>
    </div>
    <div class="section">
      <h2>{T["next_actions"]}</h2>
      <ol>{actions_html}</ol>
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


@st.cache_data(show_spinner=False, max_entries=24)
def meeting_summary_pdf(overall, narrative, health_checks, path_text, weeks, skus, generated_at, meeting_notes, assumption_status, takeaways, cost_explanation_text, diagnosis_text, forecast_range_values, assumption_summary, next_actions, df_all, product_df=None, detail_pack=True, language_code="en"):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 38
    font_name = "STSong-Light"
    pdfmetrics.registerFont(UnicodeCIDFont(font_name))

    def clean(value):
        return str(value).replace("€", "EUR ")

    brand_title = meeting_notes.get("brand_name") or T["hero_title"].format(weeks=weeks, skus=skus)
    if meeting_notes.get("scenario_name"):
        brand_title = f"{brand_title} - {meeting_notes.get('scenario_name')}"
    page_no = 1

    def draw_logo(x, y):
        pdf.setFillColor(colors.HexColor("#111827"))
        pdf.setFont(font_name, 15)
        pdf.drawString(x + 30, y - 3, "TikTok Shop")

        bag_x = x
        bag_y = y - 15
        pdf.setFillColor(colors.white)
        pdf.setStrokeColor(colors.HexColor("#111827"))
        pdf.setLineWidth(1.1)
        pdf.roundRect(bag_x, bag_y, 22, 20, 4, stroke=1, fill=1)
        pdf.setStrokeColor(colors.HexColor("#111827"))
        pdf.arc(bag_x + 6, bag_y + 12, bag_x + 16, bag_y + 24, 200, 140)
        pdf.setFillColor(colors.HexColor("#25F4EE"))
        pdf.circle(bag_x + 9, bag_y + 9, 3.2, stroke=0, fill=1)
        pdf.setFillColor(colors.HexColor("#FE2C55"))
        pdf.circle(bag_x + 13, bag_y + 8, 3.2, stroke=0, fill=1)
        pdf.setFillColor(colors.HexColor("#111827"))
        pdf.circle(bag_x + 11, bag_y + 10, 3.0, stroke=0, fill=1)

    def draw_footer():
        pdf.setStrokeColor(colors.HexColor("#E5E7EB"))
        pdf.setLineWidth(0.8)
        pdf.line(margin, 34, width - margin, 34)
        pdf.setFillColor(colors.HexColor("#94A3B8"))
        pdf.setFont(font_name, 7.5)
        pdf.drawString(margin, 22, clean(f"{T['model_version']}: {MODEL_VERSION}"))
        pdf.drawCentredString(width / 2, 22, clean(T["planning_disclaimer"])[:90])
        pdf.drawRightString(width - margin, 22, f"{page_no}")

    def draw_page_header():
        draw_logo(margin, height - 34)
        pdf.setFillColor(colors.HexColor("#64748B"))
        pdf.setFont(font_name, 8)
        pdf.drawRightString(width - margin, height - 39, clean(f"{T['generated_on']}: {generated_at}"))

    def new_page():
        nonlocal page_no
        draw_footer()
        pdf.showPage()
        page_no += 1
        draw_page_header()
        return height - 74

    def new_page_if_needed(y, needed=72):
        if y < margin + needed:
            return new_page()
        return y

    def draw_wrapped(text, x, y, max_width, font_size=10, leading=14):
        pdf.setFont(font_name, font_size)
        for line in wrap_pdf_text(clean(text), max_width, font_name, font_size):
            y = new_page_if_needed(y, leading + 4)
            pdf.drawString(x, y, line)
            y -= leading
        return y

    def draw_chip(text, x, y):
        chip_text = clean(text)
        chip_w = min(pdfmetrics.stringWidth(chip_text, font_name, 8) + 18, width - margin * 2)
        pdf.setFillColor(colors.HexColor("#F1F5F9"))
        pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
        pdf.roundRect(x, y - 15, chip_w, 19, 9, stroke=1, fill=1)
        pdf.setFillColor(colors.HexColor("#475569"))
        pdf.setFont(font_name, 8)
        pdf.drawString(x + 9, y - 10, chip_text)
        return x + chip_w + 7

    def draw_metric_cards(cards, y):
        card_gap = 10
        card_w = (width - margin * 2 - card_gap * (len(cards) - 1)) / len(cards)
        card_h = 58
        for idx, (label, value, accent) in enumerate(cards):
            x = margin + idx * (card_w + card_gap)
            pdf.setFillColor(colors.white)
            pdf.setStrokeColor(colors.HexColor("#E5E7EB"))
            pdf.roundRect(x, y - card_h, card_w, card_h, 7, stroke=1, fill=1)
            pdf.setFillColor(colors.HexColor(accent))
            pdf.roundRect(x, y - 4, card_w, 4, 2, stroke=0, fill=1)
            pdf.setFillColor(colors.HexColor("#64748B"))
            pdf.setFont(font_name, 8)
            pdf.drawString(x + 12, y - 20, clean(label))
            pdf.setFillColor(colors.HexColor("#111827"))
            pdf.setFont(font_name, 15)
            pdf.drawString(x + 12, y - 42, clean(value))
        return y - card_h - 16

    def draw_dual_summary(left_title, left_body, right_title, right_body, y, left_accent="#2563EB", right_accent="#14B8A6"):
        y = new_page_if_needed(y, 126)
        gap = 10
        box_w = (width - margin * 2 - gap) / 2
        box_h = 96
        cards = [
            (margin, left_title, left_body, left_accent),
            (margin + box_w + gap, right_title, right_body, right_accent),
        ]
        for x, title, body, accent in cards:
            pdf.setFillColor(colors.white)
            pdf.setStrokeColor(colors.HexColor("#E5E7EB"))
            pdf.roundRect(x, y - box_h, box_w, box_h, 8, stroke=1, fill=1)
            pdf.setFillColor(colors.HexColor(accent))
            pdf.roundRect(x, y - 4, box_w, 4, 2, stroke=0, fill=1)
            pdf.setFillColor(colors.HexColor("#64748B"))
            pdf.setFont(font_name, 8)
            pdf.drawString(x + 12, y - 18, clean(title))
            pdf.setFillColor(colors.HexColor("#111827"))
            cursor = y - 34
            cursor = draw_wrapped(body, x + 12, cursor, box_w - 24, font_size=9.1, leading=12)
        return y - box_h - 14

    def draw_highlight_strip(title, body, y, accent="#7C3AED"):
        y = new_page_if_needed(y, 70)
        box_h = 54
        pdf.setFillColor(colors.HexColor("#FBFCFE"))
        pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
        pdf.roundRect(margin, y - box_h, width - margin * 2, box_h, 8, stroke=1, fill=1)
        pdf.setFillColor(colors.HexColor(accent))
        pdf.roundRect(margin, y - box_h, 5, box_h, 3, stroke=0, fill=1)
        pdf.setFillColor(colors.HexColor("#64748B"))
        pdf.setFont(font_name, 8)
        pdf.drawString(margin + 16, y - 18, clean(title))
        pdf.setFillColor(colors.HexColor("#111827"))
        draw_wrapped(body, margin + 16, y - 34, width - margin * 2 - 30, font_size=9.1, leading=12)
        return y - box_h - 14

    def draw_page_title(title, subtitle, y, accent="#111827"):
        y = new_page_if_needed(y, 72)
        pdf.setFillColor(colors.HexColor("#111827"))
        pdf.setFont(font_name, 18)
        pdf.drawString(margin, y, clean(title))
        pdf.setFillColor(colors.HexColor("#64748B"))
        y = draw_wrapped(subtitle, margin, y - 18, width - margin * 2, font_size=8.8, leading=12)
        pdf.setStrokeColor(colors.HexColor("#E5E7EB"))
        pdf.setLineWidth(0.8)
        pdf.line(margin, y - 2, width - margin, y - 2)
        return y - 14

    def draw_section(title, lines, y, accent="#2563EB", ordered=False, compact=False):
        line_height = 12 if compact else 14
        estimated = 36 + max(1, len(lines)) * line_height * 2
        y = new_page_if_needed(y, estimated)
        box_top = y
        pdf.setFillColor(colors.white)
        pdf.setStrokeColor(colors.HexColor("#E5E7EB"))
        box_h = min(estimated, max(88, y - margin - 12))
        pdf.roundRect(margin, box_top - box_h, width - margin * 2, box_h, 8, stroke=1, fill=1)
        pdf.setFillColor(colors.HexColor(accent))
        pdf.roundRect(margin, box_top - 4, width - margin * 2, 4, 2, stroke=0, fill=1)
        pdf.setFillColor(colors.HexColor("#111827"))
        pdf.setFont(font_name, 13)
        pdf.drawString(margin + 14, box_top - 24, clean(title))
        cursor = box_top - 43
        for idx, line in enumerate(lines, start=1):
            prefix = f"{idx}. " if ordered else "- "
            pdf.setFillColor(colors.HexColor("#334155"))
            cursor = draw_wrapped(prefix + line, margin + 18, cursor, width - margin * 2 - 36, font_size=8.8 if compact else 9.4, leading=line_height)
            cursor -= 2
            if cursor < box_top - box_h + 14:
                break
        return box_top - box_h - 12

    def draw_two_column_section(title, pairs, y, accent="#7C3AED"):
        rows = [pairs[i:i + 2] for i in range(0, len(pairs), 2)]
        y = new_page_if_needed(y, 120)
        box_h = 42 + len(rows) * 44
        pdf.setFillColor(colors.white)
        pdf.setStrokeColor(colors.HexColor("#E5E7EB"))
        pdf.roundRect(margin, y - box_h, width - margin * 2, box_h, 8, stroke=1, fill=1)
        pdf.setFillColor(colors.HexColor(accent))
        pdf.roundRect(margin, y - 4, width - margin * 2, 4, 2, stroke=0, fill=1)
        pdf.setFillColor(colors.HexColor("#111827"))
        pdf.setFont(font_name, 13)
        pdf.drawString(margin + 14, y - 24, clean(title))
        col_w = (width - margin * 2 - 42) / 2
        cursor_y = y - 50
        for row in rows:
            for col_idx, (label, value, _accent) in enumerate(row):
                x = margin + 18 + col_idx * (col_w + 16)
                pdf.setFillColor(colors.HexColor("#64748B"))
                pdf.setFont(font_name, 8)
                pdf.drawString(x, cursor_y + 12, clean(label))
                pdf.setFillColor(colors.HexColor("#111827"))
                draw_wrapped(value, x, cursor_y, col_w, font_size=8.8, leading=11)
            cursor_y -= 44
        return y - box_h - 12

    def draw_trend_chart(df, y):
        y = new_page_if_needed(y, 170)
        box_h = 158
        x0 = margin
        y0 = y - box_h
        box_w = width - margin * 2
        pdf.setFillColor(colors.white)
        pdf.setStrokeColor(colors.HexColor("#E5E7EB"))
        pdf.roundRect(x0, y0, box_w, box_h, 8, stroke=1, fill=1)
        pdf.setFillColor(colors.HexColor("#2563EB"))
        pdf.roundRect(x0, y - 4, box_w, 4, 2, stroke=0, fill=1)
        pdf.setFillColor(colors.HexColor("#111827"))
        pdf.setFont(font_name, 13)
        pdf.drawString(x0 + 14, y - 24, clean(T["overall_weekly"]))

        plot_x = x0 + 38
        plot_y = y0 + 28
        plot_w = box_w - 68
        plot_h = box_h - 70
        temp = df.sort_values("Global Week").copy()
        series = [
            (T["forecast_gmv"], "GMV", "#2563EB"),
            (T["total_cost_label"], "Total Cost", "#F97316"),
            (T["profit_label"], "Profit", "#16A34A"),
        ]
        values = []
        for _label, col, _color in series:
            if col in temp:
                values.extend(temp[col].astype(float).tolist())
        if not values:
            return y0 - 12
        min_v = min(0, min(values))
        max_v = max(values)
        if max_v == min_v:
            max_v = min_v + 1

        pdf.setStrokeColor(colors.HexColor("#E5E7EB"))
        pdf.setLineWidth(0.7)
        for tick in range(4):
            yy = plot_y + tick * plot_h / 3
            pdf.line(plot_x, yy, plot_x + plot_w, yy)
        if min_v < 0 < max_v:
            zero_y = plot_y + (0 - min_v) / (max_v - min_v) * plot_h
            pdf.setStrokeColor(colors.HexColor("#94A3B8"))
            pdf.line(plot_x, zero_y, plot_x + plot_w, zero_y)

        weeks_list = temp["Global Week"].astype(float).tolist()
        min_week = min(weeks_list)
        max_week = max(weeks_list)
        week_span = max(max_week - min_week, 1)
        for label, col, color in series:
            if col not in temp:
                continue
            points = []
            for _, row in temp.iterrows():
                px = plot_x + (float(row["Global Week"]) - min_week) / week_span * plot_w
                py = plot_y + (float(row[col]) - min_v) / (max_v - min_v) * plot_h
                points.append((px, py))
            pdf.setStrokeColor(colors.HexColor(color))
            pdf.setLineWidth(1.7)
            for idx in range(len(points) - 1):
                pdf.line(points[idx][0], points[idx][1], points[idx + 1][0], points[idx + 1][1])
            pdf.setFillColor(colors.HexColor(color))
            for px, py in points:
                pdf.circle(px, py, 1.8, stroke=0, fill=1)

        legend_x = plot_x
        legend_y = y0 + 13
        for label, _col, color in series:
            pdf.setFillColor(colors.HexColor(color))
            pdf.circle(legend_x, legend_y + 3, 3, stroke=0, fill=1)
            pdf.setFillColor(colors.HexColor("#475569"))
            pdf.setFont(font_name, 8)
            pdf.drawString(legend_x + 8, legend_y, clean(label))
            legend_x += 112
        return y0 - 12

    draw_page_header()
    y = height - 78

    pdf.setFillColor(colors.HexColor("#F8FAFC"))
    pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
    pdf.roundRect(margin, y - 86, width - margin * 2, 86, 10, stroke=1, fill=1)
    pdf.setFillColor(colors.HexColor("#25F4EE"))
    pdf.roundRect(margin, y - 86, 5, 86, 3, stroke=0, fill=1)
    pdf.setFillColor(colors.HexColor("#FE2C55"))
    pdf.roundRect(margin + 6, y - 86, 5, 86, 3, stroke=0, fill=1)
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont(font_name, 8.5)
    pdf.drawString(margin + 18, y - 18, clean(T["pdf_proposal_title"]))
    pdf.setFillColor(colors.HexColor("#111827"))
    pdf.setFont(font_name, 21)
    pdf.drawString(margin + 18, y - 42, clean(brand_title))
    y -= 62

    pdf.setFillColor(colors.HexColor("#475569"))
    y = draw_wrapped(
        T["hero_subtitle"].format(
            gmv=money(overall["Total GMV"], 0),
            growth_investment=money(overall["Growth Investment"], 0),
            break_even=path_text,
        ),
        margin + 18,
        y,
        width - margin * 2 - 36,
        font_size=9.5,
        leading=13,
    )
    y -= 16

    chip_x = margin
    chip_y = y
    for chip in [
        f"{T['plan_length']}: {weeks} {T['week']}",
        f"{T['sku_count_meta']}: {skus}",
        f"{T['scenario_name']}: {meeting_notes.get('scenario_name') or '-'}",
        f"{T['meeting_date']}: {meeting_notes.get('meeting_date') or '-'}",
        f"{T['am_name']}: {meeting_notes.get('am_name') or '-'}",
        f"{T['assumption_status']}: {assumption_status}",
    ]:
        next_x = draw_chip(chip, chip_x, chip_y)
        if next_x > width - margin - 120:
            chip_x = margin
            chip_y -= 25
        else:
            chip_x = next_x
    y = chip_y - 28

    y = draw_metric_cards(
        [
            (T["total_gmv"], money(overall["Total GMV"], 0), "#2563EB"),
            (T["total_profit"], money(overall["Total Profit"], 0), "#16A34A" if float(overall["Total Profit"]) >= 0 else "#DC2626"),
            (T["growth_investment"], money(overall["Growth Investment"], 0), "#7C3AED"),
        ],
        y,
    )

    y = draw_dual_summary(
        T["scenario_snapshot"],
        clean(
            T["hero_subtitle"].format(
                gmv=money(overall["Total GMV"], 0),
                growth_investment=money(overall["Growth Investment"], 0),
                break_even=path_text,
            )
        ),
        T["diagnosis_summary"],
        clean(diagnosis_text),
        y,
    )

    y = draw_highlight_strip(
        T["key_recommendation"],
        clean(meeting_notes.get("key_recommendation") or next_actions[0] if next_actions else T["phase_strategy_text"]),
        y,
        accent="#7C3AED",
    )

    y = draw_section(T["phase_strategy"], [T["phase_strategy_text"]], y, accent="#7C3AED", compact=True)

    y = draw_trend_chart(df_all, y)

    y = draw_section(
        T["commercial_takeaways"],
        [f"{label}: {value}" for label, value in takeaways],
        y,
        accent="#2563EB",
        compact=True,
    )

    if not detail_pack:
        if y > margin + 122:
            y = draw_section(
                T["next_actions"],
                [clean(action) for action in next_actions[:3]],
                y,
                accent="#14B8A6",
                ordered=True,
                compact=True,
            )
        draw_footer()
        pdf.save()
        buffer.seek(0)
        return buffer.getvalue()

    y = draw_two_column_section(T["key_assumptions"], assumption_summary, y, accent="#7C3AED")

    y = new_page()
    y = draw_page_title(
        T["meeting_header"],
        clean(T["export_materials_note"]),
        y,
    )
    sections = [
        (T["client_narrative"], [clean(item) for item in narrative]),
        (T["meeting_notes"], [
            f"{T['key_recommendation']}: {meeting_notes.get('key_recommendation') or '-'}",
        ], "#8B5CF6"),
        (T["health_check"], [clean(text) for _level, text in health_checks], "#F97316"),
        (T["path_to_be"], [clean(path_text)], "#14B8A6"),
        (T["cost_explanation"], [clean(cost_explanation_text)], "#2563EB"),
        (T["diagnosis_summary"], [clean(diagnosis_text)], "#14B8A6"),
        (T["next_actions"], [clean(action) for action in next_actions], "#14B8A6"),
    ]
    for item in sections:
        if len(item) == 2:
            title, lines = item
            accent = "#2563EB"
        else:
            title, lines, accent = item
        y = draw_section(title, lines, y, accent=accent, ordered=(title in (T["client_narrative"], T["next_actions"])), compact=True)

    if product_df is not None:
        y = new_page()
        y = draw_page_title(
            T["assumption_appendix"],
            clean(T["planning_disclaimer"]),
            y,
        )
        appendix_lines = []
        for _, sku in product_df.iterrows():
            category_display = category_label(sku["Category"])
            subcategory_display = subcategory_label(sku["Subcategory"])
            appendix_lines.append(
                f"{sku['SKU']} | {category_display} / {subcategory_display} | "
                f"AOV {money(sku['AOV'], 2)} | Margin {pct(sku['Gross Margin'], 0)} | "
                f"Videos/sample {float(sku['Videos / Sample']):.2f} | "
                f"Clicks/video {float(sku['Clicks / Video']):,.0f} | "
                f"CVR {pct(sku['Click-to-order Rate'], 1)} | "
                f"Store/Search {pct(sku['ShopTab GMV Share'], 0)}"
            )
        y = draw_section(T["assumption_appendix"], appendix_lines, y, accent="#64748B", compact=True)

    draw_footer()
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def reset_defaults():
    prefixes = (
        "sku_name_", "category_", "subcategory_", "aov_", "gross_margin_pct_",
        "organic_commission_pct_", "paid_commission_pct_", "videos_per_sample_",
        "clicks_per_video_", "click_to_order_pct_", "shop_tab_share_pct_",
        "take_rate_", "samples_per_sku_", "phase_chart_mode_", "_model_",
        "_applied_",
    )
    exact_keys = {
        "has_generated", "selected_phase_view", "logistics_cost_manual",
        "logistics_carrier_cost_manual", "logistics_pick_pack_cost_manual",
        "logistics_return_allowance_manual", "sample_shipping_cost_manual",
        "sample_handling_cost_manual", "meeting_mode_input", "n_skus_input", "promo_60d_input", "use_fbt_input",
        "weeks_per_phase_input", "ads_roas_input", "organic_window_input",
        "reset_confirm_pending", "brand_name_input", "meeting_date_input",
        "am_name_input", "key_recommendation_input", "assumption_status_input",
        "sku_count_confirmed", "scenario_name_input", "target_gmv_input", "target_profit_input",
        "scenario_case_input", "plan_locked",
        "_draft_signature", "_scroll_to_results",
        "_model_brand_name", "_model_meeting_date", "_model_am_name",
        "_model_key_recommendation", "_model_assumption_status", "_model_scenario_name",
        "_model_target_gmv", "_model_target_profit", "_model_scenario_case",
        "_model_logistics_carrier_cost", "_model_logistics_pick_pack_cost",
        "_model_logistics_return_allowance", "_model_sample_shipping_cost",
        "_model_sample_delivery_cost", "_model_sample_handling_cost",
        "_locked_df_all", "_locked_product_df", "_locked_phase_inputs",
        "_locked_weeks_per_phase", "_locked_ads_roas", "_locked_scenario_label",
        "_locked_base_ads_roas", "_locked_assumption_status",
        "_locked_scenario_case", "_locked_promo_60d", "_locked_use_fbt",
        "_locked_logistics_cost", "_locked_sample_shipping_cost",
        "_locked_logistics_carrier_cost", "_locked_logistics_pick_pack_cost",
        "_locked_logistics_return_allowance", "_locked_sample_delivery_cost",
        "_locked_sample_handling_cost",
        "_locked_organic_click_window_weeks", "_locked_target_gmv", "_locked_target_profit",
    }
    for key in list(st.session_state.keys()):
        if key in exact_keys or any(key.startswith(prefix) for prefix in prefixes):
            del st.session_state[key]
    st.rerun()


def reset_sku_assumptions(n_skus):
    for i in range(int(n_skus)):
        initialize_sku(i)
        apply_category_defaults(i)
    st.rerun()


def apply_plotly_layout(fig, title, height=460):
    fig.update_layout(
        title={
            "text": title,
            "x": 0.0,
            "xanchor": "left",
            "y": 0.985,
            "yanchor": "top",
            "font": {"size": 11, "color": "#111827", "family": "Arial, sans-serif"},
        },
        height=height,
        margin=dict(l=44, r=32, t=18, b=34),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FBFCFE",
        font=dict(color="#111827", family="Arial, sans-serif"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.06,
            xanchor="left",
            x=0.06,
            bgcolor="rgba(255,255,255,0.72)",
            font=dict(size=9, color="#667085"),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#D9E2EE",
            font=dict(color="#111827", size=11),
        ),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=CHART_COLORS["grid"],
        zeroline=False,
        linecolor="#EDF2F7",
        tickfont=dict(color="#667085", size=9),
        ticklen=0,
        automargin=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=CHART_COLORS["grid"],
        zeroline=False,
        linecolor="#EDF2F7",
        tickfont=dict(color="#667085", size=9),
        ticklen=0,
        automargin=True,
    )
    return fig


def add_terminal_value_labels(fig, series):
    for trace_name, x_value, y_value, color, prefix in series:
        fig.add_annotation(
            x=x_value,
            y=y_value,
            xshift=14,
            showarrow=False,
            text=f"{prefix}{y_value:,.0f}",
            font=dict(size=9, color="#475467", family="Arial, sans-serif"),
            bgcolor="rgba(255,255,255,0)",
            borderwidth=0,
            borderpad=0,
            xanchor="left",
            yanchor="middle",
            align="left",
        )


def week_tick_step(max_week):
    if max_week <= 6:
        return 1
    if max_week <= 12:
        return 2
    return 4


def add_phase_bands(fig, df, target_row=None, target_col=None):
    phase_ranges = df.groupby(["Phase Key"], as_index=False).agg(
        start_week=("Global Week", "min"),
        end_week=("Global Week", "max"),
    )
    color_map = {p["key"]: p["color"] for p in PHASES}
    for _, phase_row in phase_ranges.iterrows():
        fig.add_vrect(
            x0=phase_row["start_week"] - 0.5,
            x1=phase_row["end_week"] + 0.5,
            fillcolor=color_map.get(phase_row["Phase Key"], "#F3F4F6"),
            opacity=0.22,
            line_width=0,
            layer="below",
            row=target_row if target_row is not None else None,
            col=target_col if target_col is not None else None,
        )


def add_phase_labels(fig, df):
    phase_ranges = df.groupby("Phase Key", as_index=False).agg(
        start_week=("Global Week", "min"),
        end_week=("Global Week", "max"),
    )
    phase_lookup = {phase["key"]: phase for phase in PHASES}
    for _, phase_row in phase_ranges.iterrows():
        phase = phase_lookup.get(phase_row["Phase Key"])
        if phase is None:
            continue
        midpoint = (float(phase_row["start_week"]) + float(phase_row["end_week"])) / 2
        fig.add_annotation(
            x=midpoint,
            y=1.035,
            xref="x",
            yref="paper",
            text=phase_label(phase),
            showarrow=False,
            font=dict(size=9, color="#64748B", family="Arial, sans-serif"),
            bgcolor="rgba(255,255,255,0.84)",
            bordercolor="rgba(203,213,225,0.76)",
            borderwidth=1,
            borderpad=4,
        )


def add_end_label(fig, x, y, text, color, row=None, col=None, xshift=10, yshift=0):
    kwargs = {}
    if row is not None:
        kwargs["row"] = row
    if col is not None:
        kwargs["col"] = col
    fig.add_annotation(
        x=x,
        y=y,
        xshift=xshift,
        yshift=yshift,
        showarrow=False,
        text=text,
        font=dict(size=9, color=color, family="Arial, sans-serif"),
        bgcolor="rgba(255,255,255,0.88)",
        bordercolor="rgba(255,255,255,0)",
        borderpad=1,
        xanchor="left",
        yanchor="middle",
        align="left",
        **kwargs,
    )


def make_weekly_chart(df, title, break_even_week=None):
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        row_heights=[0.68, 0.32],
    )
    add_phase_bands(fig, df, target_row="all", target_col=1)
    top_series = [
        (T["forecast_gmv"], "GMV", CHART_COLORS["gmv"], 2.8),
        (T["total_cost_label"], "Total Cost", CHART_COLORS["cost"], 2.2),
    ]
    for label, col, color, width in top_series:
        fig.add_trace(
            go.Scatter(
                x=df["Global Week"],
                y=df[col],
                mode="lines",
                name=label,
                line=dict(color=color, width=width, shape="spline", smoothing=0.52),
                fill="tozeroy" if col == "GMV" else None,
                fillcolor="rgba(49, 94, 236, 0.06)" if col == "GMV" else None,
                hovertemplate=f"{label}: €%{{y:,.0f}}<extra></extra>",
            ),
            row=1,
            col=1,
        )
    fig.add_trace(
        go.Bar(
            x=df["Global Week"],
            y=df["Growth Investment"],
            name=T["growth_investment"],
            marker=dict(color="rgba(91, 91, 214, 0.20)", line=dict(color="#5B5BD6", width=1)),
            hovertemplate=f"{T['growth_investment']}: €%{{y:,.0f}}<extra></extra>",
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=df["Global Week"],
            y=df["Profit"],
            name=T["profit_label"],
            marker=dict(color="rgba(23, 138, 98, 0.78)", line=dict(color="#178A62", width=0.8)),
            hovertemplate=f"{T['profit_label']}: €%{{y:,.0f}}<extra></extra>",
        ),
        row=2,
        col=1,
    )
    fig.add_hline(y=0, line_color="#98A2B3", line_width=1, row=2, col=1)
    if break_even_week is not None:
        fig.add_vline(x=break_even_week, line_dash="dash", line_color="#98A2B3", row="all", col=1)
    apply_plotly_layout(fig, "", height=540)
    fig.update_layout(showlegend=False, margin=dict(l=52, r=76, t=24, b=46), barmode="group", bargap=0.42)
    fig.update_yaxes(tickprefix="€", tickformat=",.0f", row=1, col=1)
    fig.update_yaxes(tickprefix="€", tickformat=",.0f", row=2, col=1)
    fig.update_xaxes(title=T["week"], row=2, col=1, dtick=1, tickmode="linear")
    fig.update_xaxes(title="", row=1, col=1)
    last_x = df["Global Week"].iloc[-1]
    add_end_label(fig, last_x, float(df["GMV"].iloc[-1]), money(float(df["GMV"].iloc[-1]), 0), CHART_COLORS["gmv"], row=1, col=1)
    add_end_label(fig, last_x, float(df["Total Cost"].iloc[-1]), money(float(df["Total Cost"].iloc[-1]), 0), CHART_COLORS["cost"], row=1, col=1)
    add_end_label(fig, last_x, float(df["Profit"].iloc[-1]), money(float(df["Profit"].iloc[-1]), 0), CHART_COLORS["profit"], row=2, col=1, xshift=14)
    add_end_label(fig, last_x, float(df["Growth Investment"].iloc[-1]), money(float(df["Growth Investment"].iloc[-1]), 0), "#5B5BD6", row=2, col=1, xshift=14)
    return fig


def make_scale_chart(df, title, break_even_week=None, height=330, forecast_spread=0.0, target_gmv=0.0):
    fig = go.Figure()
    add_phase_bands(fig, df)
    add_phase_labels(fig, df)
    max_week = int(df["Global Week"].max())
    forecast_spread = max(0.0, float(forecast_spread or 0.0))
    if forecast_spread > 0:
        lower_band = df["GMV"] * (1 - forecast_spread)
        upper_band = df["GMV"] * (1 + forecast_spread)
        fig.add_trace(
            go.Scatter(
                x=df["Global Week"],
                y=lower_band,
                mode="lines",
                line=dict(width=0),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["Global Week"],
                y=upper_band,
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(49, 94, 236, 0.075)",
                name=T["forecast_band"],
                customdata=np.column_stack((lower_band, upper_band)),
                hovertemplate=(
                    f"{T['forecast_band']}: "
                    "€%{customdata[0]:,.0f} – €%{customdata[1]:,.0f}<extra></extra>"
                ),
                showlegend=False,
            )
        )
    fig.add_trace(
        go.Scatter(
            x=df["Global Week"],
            y=df["Total Cost"],
            mode="lines+markers",
            name=T["total_cost_label"],
            line=dict(color=CHART_COLORS["cost"], width=2.1, shape="spline", smoothing=0.52),
            marker=dict(size=3.6, color=CHART_COLORS["cost"], line=dict(color="#FFFFFF", width=0.9)),
            hovertemplate=f"{T['total_cost_label']}: €%{{y:,.0f}}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Global Week"],
            y=df["GMV"],
            mode="lines+markers",
            name=T["forecast_gmv"],
            line=dict(color=CHART_COLORS["gmv"], width=3.0, shape="spline", smoothing=0.52),
            marker=dict(size=4.2, color=CHART_COLORS["gmv"], line=dict(color="#FFFFFF", width=1.0)),
            fill="tonexty",
            fillcolor="rgba(49, 94, 236, 0.10)",
            hovertemplate=f"{T['forecast_gmv']}: €%{{y:,.0f}}<extra></extra>",
        )
    )
    target_gmv = float(target_gmv or 0.0)
    if target_gmv > 0 and len(df) > 0:
        target_weekly = target_gmv / len(df)
        fig.add_trace(
            go.Scatter(
                x=[1, max_week],
                y=[target_weekly, target_weekly],
                mode="lines",
                name=T["target_weekly_run_rate"],
                line=dict(color="#FE2C55", width=1.5, dash="dot"),
                hovertemplate=f"{T['target_weekly_run_rate']}: €%{{y:,.0f}}<extra></extra>",
                showlegend=False,
            )
        )
        fig.add_annotation(
            x=max_week,
            y=target_weekly,
            text=T["target_weekly_run_rate"],
            showarrow=False,
            xanchor="right",
            yshift=12,
            font=dict(size=9, color="#C81E45"),
            bgcolor="rgba(255,255,255,0.92)",
        )
    if break_even_week is not None:
        fig.add_vline(x=break_even_week, line_dash="dash", line_color="#98A2B3")
        profit_value = float(df.loc[df["Global Week"] == break_even_week, "GMV"].iloc[0])
        fig.add_annotation(
            x=break_even_week,
            y=profit_value,
            text=f"{T['break_even_marker']} · {T['week']} {break_even_week}",
            showarrow=True,
            arrowhead=0,
            arrowwidth=1,
            arrowcolor="#64748B",
            ax=34,
            ay=-46,
            font=dict(size=9, color="#475569"),
            bgcolor="rgba(255,255,255,0.94)",
            bordercolor="#D8E1EC",
            borderwidth=1,
            borderpad=5,
        )
    peak_idx = df["GMV"].idxmax()
    peak_week = int(df.loc[peak_idx, "Global Week"])
    peak_gmv = float(df.loc[peak_idx, "GMV"])
    fig.add_annotation(
        x=peak_week,
        y=peak_gmv,
        text=f"{T['peak_gmv']}<br>{money(peak_gmv, 0)}",
        showarrow=True,
        arrowhead=0,
        arrowwidth=1.2,
        arrowcolor=CHART_COLORS["gmv"],
        ax=0,
        ay=-56,
        font=dict(size=9, color=CHART_COLORS["gmv"]),
        bgcolor="rgba(255,255,255,0.96)",
        bordercolor="rgba(49,94,236,0.20)",
        borderwidth=1,
        borderpad=5,
    )
    apply_plotly_layout(fig, "", height=height)
    fig.update_layout(showlegend=False, margin=dict(l=42, r=68, t=42, b=34))
    fig.update_yaxes(tickprefix="€", tickformat=",.0f")
    fig.update_xaxes(title=T["week"], dtick=week_tick_step(max_week), tickmode="linear")
    last_x = df["Global Week"].iloc[-1]
    add_end_label(fig, last_x, float(df["GMV"].iloc[-1]), money(float(df["GMV"].iloc[-1]), 0), CHART_COLORS["gmv"], xshift=16, yshift=-10)
    add_end_label(fig, last_x, float(df["Total Cost"].iloc[-1]), money(float(df["Total Cost"].iloc[-1]), 0), CHART_COLORS["cost"], xshift=16, yshift=10)
    return fig


def make_profit_investment_chart(df, title, height=310):
    fig = go.Figure()
    max_week = int(df["Global Week"].max())
    fig.add_trace(
        go.Bar(
            x=df["Global Week"],
            y=df["Growth Investment"],
            name=T["growth_investment"],
            marker=dict(color="rgba(91, 91, 214, 0.12)", line=dict(color="#7C74E8", width=0.8)),
            hovertemplate=f"{T['growth_investment']}: €%{{y:,.0f}}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df["Global Week"],
            y=df["Profit"],
            name=T["profit_label"],
            marker=dict(color="rgba(25, 140, 110, 0.58)", line=dict(color="#198C6E", width=0.75)),
            hovertemplate=f"{T['profit_label']}: €%{{y:,.0f}}<extra></extra>",
        )
    )
    fig.add_hline(y=0, line_color="#98A2B3", line_width=1)
    apply_plotly_layout(fig, "", height=height)
    fig.update_layout(showlegend=False, margin=dict(l=42, r=54, t=10, b=28), barmode="group", bargap=0.64)
    fig.update_yaxes(tickprefix="€", tickformat=",.0f")
    fig.update_xaxes(title=T["week"], dtick=week_tick_step(max_week), tickmode="linear")
    last_x = df["Global Week"].iloc[-1]
    add_end_label(fig, last_x, float(df["Profit"].iloc[-1]), money(float(df["Profit"].iloc[-1]), 0), CHART_COLORS["profit"], xshift=14)
    add_end_label(fig, last_x, float(df["Growth Investment"].iloc[-1]), money(float(df["Growth Investment"].iloc[-1]), 0), "#5B5BD6", xshift=14)
    return fig


def make_cumulative_profit_chart(df, break_even_week=None, height=520, target_profit=0.0):
    temp = df.copy()
    temp["Cumulative Profit"] = temp["Profit"].cumsum()
    max_week = int(temp["Global Week"].max())
    fig = go.Figure()
    add_phase_bands(fig, temp)
    fig.add_trace(
        go.Scatter(
            x=temp["Global Week"],
            y=temp["Cumulative Profit"],
            mode="lines+markers",
            fill="tozeroy",
            name=T["cumulative_profit_trend"],
            line=dict(color=CHART_COLORS["cumulative"], width=2.45, shape="spline", smoothing=0.36),
            marker=dict(size=4.0, color=CHART_COLORS["cumulative"], line=dict(color="#FFFFFF", width=0.8)),
            fillcolor="rgba(79, 70, 229, 0.055)",
            hovertemplate=f"{T['cumulative_profit_trend']}: €%{{y:,.0f}}<extra></extra>",
        )
    )
    fig.add_hline(y=0, line_color="#6B7280", line_width=1)
    target_profit = float(target_profit or 0.0)
    if target_profit > 0:
        fig.add_trace(
            go.Scatter(
                x=[1, max_week],
                y=[target_profit, target_profit],
                mode="lines",
                name=T["target_profit"],
                line=dict(color="#FE2C55", width=1.5, dash="dot"),
                hovertemplate=f"{T['target_profit']}: €%{{y:,.0f}}<extra></extra>",
                showlegend=False,
            )
        )
        fig.add_annotation(
            x=max_week,
            y=target_profit,
            text=T["target_profit"],
            showarrow=False,
            xanchor="right",
            yshift=12,
            font=dict(size=9, color="#C81E45"),
            bgcolor="rgba(255,255,255,0.92)",
        )
    if break_even_week is not None:
        fig.add_vline(x=break_even_week, line_dash="dash", line_color="#6B7280")
    apply_plotly_layout(fig, "", height=height)
    fig.update_layout(showlegend=False, margin=dict(l=44, r=48, t=10, b=28))
    fig.update_yaxes(tickprefix="€", tickformat=",.0f")
    fig.update_xaxes(title=T["week"], dtick=week_tick_step(max_week), tickmode="linear")
    add_end_label(
        fig,
        temp["Global Week"].iloc[-1],
        float(temp["Cumulative Profit"].iloc[-1]),
        money(float(temp["Cumulative Profit"].iloc[-1]), 0),
        CHART_COLORS["cumulative"],
    )
    return fig


def render_funnel_summary(df):
    items = [
        (T["samples_label"], f"{df['Samples Sent'].sum():,.0f}", "#4F46E5"),
        (T["videos_label"], f"{df['New Videos'].sum():,.0f}", "#3B82F6"),
        (T["clicks_label"], f"{df['Product Clicks'].sum():,.0f}", "#315EEC"),
        (T["orders_label"], f"{df['Orders'].sum():,.0f}", "#178A62"),
    ]
    cards = [
        (
            f'<div class="funnel-card">'
            f'<div class="funnel-card-label">{escape(label)}</div>'
            f'<div class="funnel-card-value">{escape(value)}</div>'
            "</div>"
        )
        for label, value, _color in items
    ]
    st.markdown(
        f"""
        <div class="funnel-card-wrap">
            <div class="funnel-card-title">{escape(T["funnel_summary"])}</div>
            <div class="funnel-card-grid">{"".join(cards)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
        marker_color="#315EEC",
        text=[pct(v, 0) for v in temp["Store/Search Share"]],
        textposition="inside",
        marker_line=dict(color="rgba(255,255,255,0.9)", width=1),
        customdata=temp["ShopTab GMV"],
        hovertemplate=f"{T['shoptab_gmv']}: €%{{customdata:,.0f}}<br>Share: %{{y:.0%}}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=temp["Phase"],
        y=temp["Affiliate Share"],
        name=T["affiliate_video_gmv"],
        marker_color="#94A3B8",
        text=[pct(v, 0) for v in temp["Affiliate Share"]],
        textposition="inside",
        marker_line=dict(color="rgba(255,255,255,0.9)", width=1),
        customdata=temp["Affiliate Video GMV"],
        hovertemplate=f"{T['affiliate_video_gmv']}: €%{{customdata:,.0f}}<br>Share: %{{y:.0%}}<extra></extra>",
    ))
    apply_plotly_layout(fig, T["channel_mix"], height=560)
    fig.update_layout(barmode="stack", margin=dict(l=70, r=48, t=112, b=86), bargap=0.32)
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
    measure = ["absolute", "relative", "relative", "relative", "relative", "relative", "relative", "total"]
    fig = go.Figure(
        go.Waterfall(
            x=labels,
            y=values,
            measure=measure,
            connector={"line": {"color": "#CBD5E1", "width": 1.1}},
            increasing={"marker": {"color": "#315EEC"}},
            decreasing={"marker": {"color": "#94A3B8"}},
            totals={"marker": {"color": "#178A62" if float(phase_row["Profit"]) >= 0 else "#B42318"}},
            text=[short_money(abs(v)) if v < 0 else short_money(v) for v in values],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{x}</b><br>€%{y:,.0f}<extra></extra>",
        )
    )
    apply_plotly_layout(fig, "", height=520)
    fig.update_layout(
        showlegend=False,
        margin=dict(l=72, r=38, t=24, b=106),
        waterfallgap=0.26,
    )
    fig.update_yaxes(tickprefix="€", tickformat=",.0f")
    fig.update_xaxes(title="", tickangle=-14, automargin=True)
    return fig


def make_phase_cumulative_chart(phase_df, title):
    temp = phase_df.sort_values("Week in Phase").copy()
    temp["Cumulative GMV"] = temp["GMV"].cumsum()
    temp["Cumulative Total Cost"] = temp["Total Cost"].cumsum()
    temp["Cumulative Profit"] = temp["Profit"].cumsum()
    temp["Cumulative Growth Investment"] = temp["Growth Investment"].cumsum()
    max_week = int(temp["Week in Phase"].max())

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        row_heights=[0.68, 0.32],
    )
    fig.add_trace(
        go.Scatter(
            x=temp["Week in Phase"],
            y=temp["Cumulative Total Cost"],
            mode="lines+markers",
            name=T["total_cost_label"],
            line=dict(color=CHART_COLORS["cost"], width=2.0, shape="spline", smoothing=0.52),
            marker=dict(size=3.3, color=CHART_COLORS["cost"], line=dict(color="#FFFFFF", width=0.8)),
            hovertemplate=f"{T['total_cost_label']}: €%{{y:,.0f}}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=temp["Week in Phase"],
            y=temp["Cumulative GMV"],
            mode="lines+markers",
            name=T["total_gmv"],
            line=dict(color=CHART_COLORS["gmv"], width=2.8, shape="spline", smoothing=0.52),
            marker=dict(size=4.0, color=CHART_COLORS["gmv"], line=dict(color="#FFFFFF", width=0.8)),
            fill="tonexty",
            fillcolor="rgba(49, 94, 236, 0.10)",
            hovertemplate=f"{T['total_gmv']}: €%{{y:,.0f}}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=temp["Week in Phase"],
            y=temp["Cumulative Growth Investment"],
            name=T["growth_investment"],
            marker=dict(color="rgba(91, 91, 214, 0.16)", line=dict(color="#6B63E8", width=0.9)),
            hovertemplate=f"{T['growth_investment']}: €%{{y:,.0f}}<extra></extra>",
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=temp["Week in Phase"],
            y=temp["Cumulative Profit"],
            name=T["profit_label"],
            marker=dict(color="rgba(25, 140, 110, 0.72)", line=dict(color="#198C6E", width=0.8)),
            hovertemplate=f"{T['profit_label']}: €%{{y:,.0f}}<extra></extra>",
        ),
        row=2,
        col=1,
    )

    last = temp.iloc[-1]
    add_end_label(fig, last["Week in Phase"], float(last["Cumulative GMV"]), money(float(last["Cumulative GMV"]), 0), CHART_COLORS["gmv"], row=1, col=1, yshift=-10)
    add_end_label(fig, last["Week in Phase"], float(last["Cumulative Total Cost"]), money(float(last["Cumulative Total Cost"]), 0), CHART_COLORS["cost"], row=1, col=1, yshift=10)
    add_end_label(fig, last["Week in Phase"], float(last["Cumulative Profit"]), money(float(last["Cumulative Profit"]), 0), CHART_COLORS["profit"], row=2, col=1)
    add_end_label(fig, last["Week in Phase"], float(last["Cumulative Growth Investment"]), money(float(last["Cumulative Growth Investment"]), 0), "#5B5BD6", row=2, col=1)

    fig.add_hline(y=0, line_color="#98A2B3", line_width=1, opacity=0.85, row=2, col=1)
    apply_plotly_layout(fig, "", height=540)
    fig.update_layout(
        showlegend=False,
        margin=dict(l=44, r=54, t=16, b=34),
        barmode="group",
        bargap=0.56,
    )
    fig.update_yaxes(tickprefix="€", tickformat=",.0f", row=1, col=1)
    fig.update_yaxes(tickprefix="€", tickformat=",.0f", row=2, col=1)
    fig.update_xaxes(title=T["week"], dtick=week_tick_step(max_week), tickmode="linear", row=2, col=1)
    fig.update_xaxes(title="", row=1, col=1)
    return fig


def compact_phase_label(phase_key):
    phase_number = next(
        (idx for idx, phase in enumerate(PHASES, start=1) if phase["key"] == phase_key),
        1,
    )
    return T.get("phase_short", "Phase {number}").format(number=phase_number)


def phase_button_icon(phase_key):
    return {
        "phase1": ":material/filter_1:",
        "phase2": ":material/filter_2:",
        "phase3": ":material/filter_3:",
    }.get(phase_key, ":material/flag:")


def phase_chart_mode_icon(mode_key):
    return {
        "cumulative": ":material/show_chart:",
        "total": ":material/waterfall_chart:",
    }.get(mode_key, ":material/monitoring:")


@st.fragment
def render_phase_explorer(phase_inputs, df_all, phase_summary):
    render_section_header(T["phase_trend"])
    selected_phase_key = render_segmented_buttons(
        [phase["key"] for phase in phase_inputs],
        "selected_phase_view",
        format_func=compact_phase_label,
        help_func=lambda key: phase_label(next(phase for phase in phase_inputs if phase["key"] == key)),
        icon_func=phase_button_icon,
    )
    selected_phase = next(phase for phase in phase_inputs if phase["key"] == selected_phase_key)
    phase_df = df_all[df_all["Phase Key"] == selected_phase["key"]].copy()
    phase_row = phase_summary[phase_summary["Phase Key"] == selected_phase["key"]].iloc[0]
    chart_mode = render_segmented_buttons(
        PHASE_CHART_MODE_KEYS,
        f"phase_chart_mode_{selected_phase['key']}",
        format_func=phase_chart_mode_label,
        icon_func=phase_chart_mode_icon,
    )
    with st.container(border=True):
        render_chart_panel_header(phase_label(selected_phase), icon="phase")
        if chart_mode == "cumulative":
            st.plotly_chart(
                make_phase_cumulative_chart(phase_df, phase_label(selected_phase)),
                use_container_width=True,
                config={"displayModeBar": False, "responsive": True},
            )
        else:
            st.plotly_chart(
                make_phase_total_chart(phase_row),
                use_container_width=True,
                config={"displayModeBar": False, "responsive": True},
            )
        render_chart_panel_caption(escape(phase_chart_insight(phase_row)))


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


if not st.session_state.get("sku_count_confirmed", False) and not st.session_state.get("has_generated", False):
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        [data-testid="stAppViewContainer"] > .main .block-container {
            max-width: 1080px;
            padding-left: 2.75rem;
            padding-right: 2.75rem;
            padding-top: 2.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    render_cover_page(5)
    st.markdown(f'<div class="cover-bottom-row"><div class="cover-row-label">{escape(T["expected_listing_skus"])}</div></div>', unsafe_allow_html=True)
    cover_col1, cover_col2 = st.columns([1.25, 1.05], vertical_alignment="bottom")
    with cover_col1:
        st.number_input(
            T["expected_listing_skus"],
            min_value=1,
            max_value=26,
            value=5,
            step=1,
            key="n_skus_input",
            label_visibility="collapsed",
        )
    with cover_col2:
        if st.button(T["continue_setup"], type="primary", icon=":material/arrow_forward:", width="stretch"):
            st.session_state["sku_count_confirmed"] = True
            st.rerun()
    st.markdown(
        f'<div class="cover-note"><strong>{escape(T["model_version"])}:</strong> {escape(MODEL_VERSION)}. {escape(T["calibration_note"])}</div>',
        unsafe_allow_html=True,
    )
    st.stop()

if st.session_state.get("has_generated", False):
    preserve_setup_widget_state()

with st.sidebar:
    render_sidebar_workspace_header()
    n_skus = st.number_input(T["expected_listing_skus"], min_value=1, max_value=26, value=5, step=1, key="n_skus_input")

    if "meeting_mode_input" not in st.session_state:
        st.session_state["meeting_mode_input"] = True
    meeting_mode = st.toggle(
        T["meeting_mode"],
        help=T["meeting_mode_help"],
        key="meeting_mode_input",
    )

    sidebar_meeting_compact = meeting_mode and st.session_state.get("has_generated", False)
    if sidebar_meeting_compact:
        st.button(
            T["back_to_client_view"],
            key="back_to_client_view_btn",
            icon=":material/tune:",
            on_click=switch_to_client_view,
        )
        promo_60d = bool(st.session_state.get("_applied_promo_60d", st.session_state.get("_model_promo_60d", st.session_state.get("promo_60d_input", True))))
        use_fbt = bool(st.session_state.get("_applied_use_fbt", st.session_state.get("_model_use_fbt", st.session_state.get("use_fbt_input", False))))
        weeks_per_phase = int(st.session_state.get("_applied_weeks_per_phase", st.session_state.get("_model_weeks_per_phase", st.session_state.get("weeks_per_phase_input", 4))))
        logistics_carrier_cost = float(st.session_state.get("_applied_logistics_carrier_cost", st.session_state.get("_model_logistics_carrier_cost", st.session_state.get("logistics_carrier_cost_manual", st.session_state.get("logistics_cost_manual", 5.0)))))
        logistics_pick_pack_cost = float(st.session_state.get("_applied_logistics_pick_pack_cost", st.session_state.get("_model_logistics_pick_pack_cost", st.session_state.get("logistics_pick_pack_cost_manual", 0.0))))
        logistics_return_allowance = float(st.session_state.get("_applied_logistics_return_allowance", st.session_state.get("_model_logistics_return_allowance", st.session_state.get("logistics_return_allowance_manual", 0.0))))
        logistics_cost = float(st.session_state.get("_applied_logistics_cost", st.session_state.get("_model_logistics_cost", logistics_carrier_cost + logistics_pick_pack_cost + logistics_return_allowance)))
        sample_delivery_cost = float(st.session_state.get("_applied_sample_delivery_cost", st.session_state.get("_model_sample_delivery_cost", st.session_state.get("sample_shipping_cost_manual", logistics_cost))))
        sample_handling_cost = float(st.session_state.get("_applied_sample_handling_cost", st.session_state.get("_model_sample_handling_cost", st.session_state.get("sample_handling_cost_manual", 0.0))))
        sample_shipping_cost = float(st.session_state.get("_applied_sample_shipping_cost", st.session_state.get("_model_sample_shipping_cost", sample_delivery_cost + sample_handling_cost)))
        ads_roas = float(st.session_state.get("_applied_ads_roas", st.session_state.get("_model_ads_roas", st.session_state.get("ads_roas_input", 6.0))))
        organic_click_window_weeks = int(st.session_state.get("_applied_organic_click_window_weeks", st.session_state.get("_model_organic_click_window_weeks", st.session_state.get("organic_window_input", 4))))
        target_gmv = float(st.session_state.get("_applied_target_gmv", st.session_state.get("_model_target_gmv", st.session_state.get("target_gmv_input", 0.0))))
        target_profit = float(st.session_state.get("_applied_target_profit", st.session_state.get("_model_target_profit", st.session_state.get("target_profit_input", 0.0))))
        scenario_case = st.session_state.get("_applied_scenario_case", "base")
        st.session_state["_model_scenario_case"] = scenario_case
        st.session_state["scenario_case_input"] = scenario_case
        phase_inputs = []
        for idx, phase in enumerate(PHASES):
            applied_phases = st.session_state.get("_applied_phase_inputs", [])
            if idx < len(applied_phases):
                phase_inputs.append(dict(applied_phases[idx]))
                continue
            take_rate_pct = float(st.session_state.get(f"_model_take_rate_pct_{idx}", st.session_state.get(f"take_rate_{idx}", phase["take_rate"] * 100)))
            samples_per_sku = int(st.session_state.get(f"_model_samples_per_sku_{idx}", st.session_state.get(f"samples_per_sku_{idx}", phase["samples_per_sku"])))
            phase_inputs.append({**phase, "take_rate": take_rate_pct / 100, "samples_per_sku": samples_per_sku})
    else:
        st.markdown(f'<div class="setup-ready">{escape(T["setup_ready"])}</div>', unsafe_allow_html=True)
        render_sidebar_meta(f"{T['model_version']}: {MODEL_VERSION}")
        render_sidebar_divider()
        if st.button(T["reset_defaults"], key="reset_request_btn", icon=":material/restart_alt:"):
            st.session_state["reset_confirm_pending"] = True
        if st.session_state.get("reset_confirm_pending", False):
            render_status_panel(T["reset_defaults"], T["reset_pending"], tone="warning", compact=True)
            if st.button(T["reset_confirm"], key="reset_confirm_btn", icon=":material/check:"):
                reset_defaults()
        if st.button(T["reset_sku_assumptions"], key="reset_sku_assumptions_btn", help=T["reset_sku_assumptions_help"], icon=":material/replay:"):
            reset_sku_assumptions(n_skus)
        with st.expander(T["plan_setup"], expanded=True):
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

        legacy_order_cost = float(st.session_state.get("logistics_cost_manual", 5.0))
        if "logistics_carrier_cost_manual" not in st.session_state:
            st.session_state["logistics_carrier_cost_manual"] = legacy_order_cost
        if "logistics_pick_pack_cost_manual" not in st.session_state:
            st.session_state["logistics_pick_pack_cost_manual"] = 0.0
        if "logistics_return_allowance_manual" not in st.session_state:
            st.session_state["logistics_return_allowance_manual"] = 0.0
        if "sample_handling_cost_manual" not in st.session_state:
            st.session_state["sample_handling_cost_manual"] = 0.0
        with st.expander(T["cost_assumptions"], expanded=False):
            fulfillment_label = T["fulfillment_fbt_fallback"] if use_fbt else T["fulfillment"]
            st.caption(fulfillment_label)
            logistics_carrier_cost = st.number_input(T["logistics_carrier_cost"], min_value=0.0, step=0.25, key="logistics_carrier_cost_manual")
            logistics_pick_pack_cost = st.number_input(T["logistics_pick_pack_cost"], min_value=0.0, step=0.25, key="logistics_pick_pack_cost_manual")
            logistics_return_allowance = st.number_input(T["logistics_return_allowance"], min_value=0.0, step=0.25, key="logistics_return_allowance_manual")
            logistics_cost = float(logistics_carrier_cost) + float(logistics_pick_pack_cost) + float(logistics_return_allowance)
            render_subtle_note(logistics_detail_display(logistics_carrier_cost, logistics_pick_pack_cost, logistics_return_allowance), T["logistics_total"])
            sample_delivery_cost = st.number_input(T["sample_shipping_cost"], min_value=0.0, value=5.0, step=0.5, key="sample_shipping_cost_manual")
            sample_handling_cost = st.number_input(T["sample_handling_cost"], min_value=0.0, step=0.25, key="sample_handling_cost_manual")
            sample_shipping_cost = float(sample_delivery_cost) + float(sample_handling_cost)
            render_subtle_note(sample_shipping_detail_display(sample_delivery_cost, sample_handling_cost), T["sample_shipping_total"])
            if use_fbt:
                render_subtle_note(T["fbt_help"], T["fbt"])

        with st.expander(T["growth_levers"], expanded=False):
            ads_roas = st.number_input(T["ads_roas"], min_value=0.1, max_value=8.0, value=6.0, step=0.1, key="ads_roas_input")
            organic_click_window_weeks = st.number_input(T["organic_click_window"], min_value=1, max_value=8, value=4, step=1, key="organic_window_input")
        scenario_case = "base"
        st.session_state["scenario_case_input"] = scenario_case

        with st.expander(T["target_setup"], expanded=False):
            target_gmv = st.number_input(T["target_gmv"], min_value=0.0, value=0.0, step=1000.0, key="target_gmv_input", help=T["target_gmv_help"])
            target_profit = st.number_input(T["target_profit"], min_value=0.0, value=0.0, step=1000.0, key="target_profit_input", help=T["target_profit_help"])

        phase_inputs = []
        with st.expander(T["phase_controls"], expanded=False):
            for idx, phase in enumerate(PHASES):
                st.subheader(phase_label(phase))
                take_rate = st.number_input(
                    f"{T['take_rate']} - {phase_label(phase)}",
                    min_value=0.0,
                    max_value=30.0,
                    value=float(phase["take_rate"] * 100),
                    step=1.0,
                    key=f"take_rate_{idx}",
                    help=T.get("take_rate_help"),
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
        st.session_state["_model_logistics_carrier_cost"] = float(logistics_carrier_cost)
        st.session_state["_model_logistics_pick_pack_cost"] = float(logistics_pick_pack_cost)
        st.session_state["_model_logistics_return_allowance"] = float(logistics_return_allowance)
        st.session_state["_model_logistics_cost"] = float(logistics_cost)
        st.session_state["_model_sample_delivery_cost"] = float(sample_delivery_cost)
        st.session_state["_model_sample_handling_cost"] = float(sample_handling_cost)
        st.session_state["_model_sample_shipping_cost"] = float(sample_shipping_cost)
        st.session_state["_model_ads_roas"] = float(ads_roas)
        st.session_state["_model_organic_click_window_weeks"] = int(organic_click_window_weeks)
        st.session_state["_model_target_gmv"] = float(target_gmv)
        st.session_state["_model_target_profit"] = float(target_profit)
        st.session_state["_model_scenario_case"] = scenario_case
        for idx, phase in enumerate(phase_inputs):
            st.session_state[f"_model_take_rate_pct_{idx}"] = float(phase["take_rate"] * 100)
            st.session_state[f"_model_samples_per_sku_{idx}"] = int(phase["samples_per_sku"])

show_setup = (not meeting_mode) or (not st.session_state.get("has_generated", False))

if show_setup:
    st.subheader(T["sku_setup"])
    with st.expander(T["benchmark_info"], expanded=False):
        st.write(T["benchmark_info_text"])
    with st.expander(T["model_assumptions"], expanded=False):
        render_model_logic()
        render_subtle_note(T["planning_disclaimer"], T["model_assumptions"])

    with st.expander(T["meeting_notes"], expanded=False):
        n1, n2, n3, n4 = st.columns(4)
        with n1:
            brand_name = st.text_input(T["brand_name"], key="brand_name_input", help=T["brand_name_help"])
        with n2:
            scenario_name = st.text_input(T["scenario_name"], key="scenario_name_input", help=T["scenario_name_help"])
        with n3:
            meeting_date = st.date_input(T["meeting_date"], value=datetime.now().date(), key="meeting_date_input")
        with n4:
            am_name = st.text_input(T["am_name"], key="am_name_input")
        st.session_state["assumption_status_input"] = normalize_assumption_status(
            st.session_state.get("assumption_status_input", "planning")
        )
        assumption_status_key = st.selectbox(
            T["assumption_status"],
            options=ASSUMPTION_STATUS_KEYS,
            format_func=assumption_status_label,
            key="assumption_status_input",
        )
        key_recommendation = st.text_area(
            T["key_recommendation"],
            value=T["key_recommendation_default"],
            key="key_recommendation_input",
        )
    meeting_notes = {
        "brand_name": brand_name,
        "scenario_name": scenario_name,
        "meeting_date": str(meeting_date),
        "am_name": am_name,
        "key_recommendation": key_recommendation,
    }
    st.session_state["_model_brand_name"] = brand_name
    st.session_state["_model_scenario_name"] = scenario_name
    st.session_state["_model_meeting_date"] = str(meeting_date)
    st.session_state["_model_am_name"] = am_name
    st.session_state["_model_key_recommendation"] = key_recommendation
    st.session_state["_model_assumption_status"] = assumption_status_key
    assumption_status = assumption_status_label(assumption_status_key)

    for i in range(int(n_skus)):
        initialize_sku(i)
        category = st.session_state[f"category_{i}"]
        subcategory = st.session_state[f"subcategory_{i}"]
        sku_name_preview = st.session_state[f"sku_name_{i}"] or chr(65 + i)
        expander_label = f"SKU {i + 1} · {sku_name_preview} · {category_path_label(category, subcategory)}"
        with st.expander(expander_label, expanded=(not st.session_state.get("has_generated", False))):
            category = st.session_state[f"category_{i}"]
            subcategory = st.session_state[f"subcategory_{i}"]
            st.markdown(
                f"""
                <div class="sku-title">SKU {i + 1}</div>
                <div class="sku-subtitle">{category_path_label(category, subcategory)} · {pct(PLATFORM_COMMISSION[category], 0)} {T["platform_commission"]}</div>
                """,
                unsafe_allow_html=True,
            )
            c1, c2, c3 = st.columns(3)
            with c1:
                st.text_input(T["sku_name"], key=f"sku_name_{i}")
            with c2:
                category_options = list(CATEGORY_PRESETS.keys())
                st.selectbox(
                    T["category"],
                    options=category_options,
                    key=f"category_{i}",
                    format_func=category_label,
                    on_change=handle_category_change,
                    args=(i,),
                )
            category = st.session_state[f"category_{i}"]
            subcategories = list(CATEGORY_PRESETS[category].keys())
            if st.session_state[f"subcategory_{i}"] not in subcategories:
                st.session_state[f"subcategory_{i}"] = subcategories[0]
            with c3:
                st.selectbox(
                    T["subcategory"],
                    options=subcategories,
                    key=f"subcategory_{i}",
                    format_func=subcategory_label,
                    on_change=handle_subcategory_change,
                    args=(i,),
                )

            refresh_if_category_changed(i)
            fbt_status, effective_logistics = sku_fbt_status(
                aov=float(st.session_state[f"aov_{i}"]),
                logistics_cost=float(logistics_cost),
                use_fbt=bool(use_fbt),
            )

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

            if use_fbt:
                render_subtle_note(
                    f"{T['fbt_status']}: {fbt_status} · {T['effective_logistics']}: {money(effective_logistics, 2)}",
                    T["fbt"],
                )

            with st.expander(T["benchmark_expander"], expanded=False):
                st.markdown(f'<div class="benchmark-note">{escape(T["benchmark_note"])}</div>', unsafe_allow_html=True)
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
        "scenario_name": st.session_state.get("_model_scenario_name", st.session_state.get("scenario_name_input", "")),
        "meeting_date": st.session_state.get("_model_meeting_date", st.session_state.get("meeting_date_input", "")),
        "am_name": st.session_state.get("_model_am_name", st.session_state.get("am_name_input", "")),
        "key_recommendation": st.session_state.get("_model_key_recommendation", st.session_state.get("key_recommendation_input", T["key_recommendation_default"])),
    }
    assumption_status_key = normalize_assumption_status(
        st.session_state.get(
            "_applied_assumption_status",
            st.session_state.get("_model_assumption_status", st.session_state.get("assumption_status_input", "planning")),
        )
    )
    st.session_state["_model_assumption_status"] = assumption_status_key
    assumption_status = assumption_status_label(assumption_status_key)
    for i in range(int(n_skus)):
        initialize_sku(i)

scenario_label = {
    "conservative": T["scenario_conservative"],
    "base": T["scenario_base"],
    "upside": T["scenario_upside"],
}.get(scenario_case, T["scenario_base"])
for i in range(int(n_skus)):
    initialize_sku(i)

draft_product_df = None
draft_signature = None
input_validation_error = None
try:
    draft_product_df = build_product_df(int(n_skus))
    draft_signature = model_input_signature(
        product_df=draft_product_df,
        phase_inputs=phase_inputs,
        weeks_per_phase=weeks_per_phase,
        promo_60d=promo_60d,
        use_fbt=use_fbt,
        logistics_carrier_cost=logistics_carrier_cost,
        logistics_pick_pack_cost=logistics_pick_pack_cost,
        logistics_return_allowance=logistics_return_allowance,
        logistics_cost=logistics_cost,
        sample_delivery_cost=sample_delivery_cost,
        sample_handling_cost=sample_handling_cost,
        sample_shipping_cost=sample_shipping_cost,
        ads_roas=ads_roas,
        organic_click_window_weeks=organic_click_window_weeks,
        target_gmv=target_gmv,
        target_profit=target_profit,
        scenario_case=scenario_case,
        assumption_status_key=assumption_status_key,
    )
except (KeyError, TypeError, ValueError) as exc:
    input_validation_error = str(exc)

st.session_state["_draft_signature"] = draft_signature
if st.session_state.get("plan_locked", False):
    st.warning(T["plan_locked"])
    if st.button(T["unlock_plan"], key="unlock_plan_btn", icon=":material/lock_open:"):
        st.session_state["plan_locked"] = False
        st.rerun()

if not st.session_state.get("has_generated", False):
    if input_validation_error:
        st.error(f"{T['input_error']}: {input_validation_error}")

    if st.button(T["generate"], type="primary", icon=":material/monitoring:", disabled=bool(input_validation_error)):
        apply_model_draft(
            product_df=draft_product_df,
            phase_inputs=phase_inputs,
            weeks_per_phase=weeks_per_phase,
            promo_60d=promo_60d,
            use_fbt=use_fbt,
            logistics_carrier_cost=logistics_carrier_cost,
            logistics_pick_pack_cost=logistics_pick_pack_cost,
            logistics_return_allowance=logistics_return_allowance,
            logistics_cost=logistics_cost,
            sample_delivery_cost=sample_delivery_cost,
            sample_handling_cost=sample_handling_cost,
            sample_shipping_cost=sample_shipping_cost,
            ads_roas=ads_roas,
            organic_click_window_weeks=organic_click_window_weeks,
            target_gmv=target_gmv,
            target_profit=target_profit,
            scenario_case=scenario_case,
            assumption_status_key=assumption_status_key,
        )
        st.session_state["has_generated"] = True
        st.session_state["plan_locked"] = False
        st.session_state["_scroll_to_results"] = True
        st.rerun()

if (
    st.session_state.get("has_generated", False)
    and "_applied_product_df" not in st.session_state
    and draft_product_df is not None
):
    apply_model_draft(
        product_df=draft_product_df,
        phase_inputs=phase_inputs,
        weeks_per_phase=weeks_per_phase,
        promo_60d=promo_60d,
        use_fbt=use_fbt,
        logistics_carrier_cost=logistics_carrier_cost,
        logistics_pick_pack_cost=logistics_pick_pack_cost,
        logistics_return_allowance=logistics_return_allowance,
        logistics_cost=logistics_cost,
        sample_delivery_cost=sample_delivery_cost,
        sample_handling_cost=sample_handling_cost,
        sample_shipping_cost=sample_shipping_cost,
        ads_roas=ads_roas,
        organic_click_window_weeks=organic_click_window_weeks,
        target_gmv=target_gmv,
        target_profit=target_profit,
        scenario_case=scenario_case,
        assumption_status_key=assumption_status_key,
    )

has_pending_model_changes = (
    st.session_state.get("has_generated", False)
    and show_setup
    and not st.session_state.get("plan_locked", False)
    and draft_signature is not None
    and draft_signature != st.session_state.get("_applied_signature")
)
if show_setup and st.session_state.get("has_generated", False):
    with st.sidebar:
        if input_validation_error:
            render_status_panel(T["input_error"], input_validation_error, tone="warning", compact=True)
        elif has_pending_model_changes:
            render_status_panel(T["update_model"], T["pending_model_changes"], tone="warning", compact=True)
            if st.button(T["update_model"], type="primary", key="apply_model_changes_btn", icon=":material/sync:", width="stretch"):
                apply_model_draft(
                    product_df=draft_product_df,
                    phase_inputs=phase_inputs,
                    weeks_per_phase=weeks_per_phase,
                    promo_60d=promo_60d,
                    use_fbt=use_fbt,
                    logistics_carrier_cost=logistics_carrier_cost,
                    logistics_pick_pack_cost=logistics_pick_pack_cost,
                    logistics_return_allowance=logistics_return_allowance,
                    logistics_cost=logistics_cost,
                    sample_delivery_cost=sample_delivery_cost,
                    sample_handling_cost=sample_handling_cost,
                    sample_shipping_cost=sample_shipping_cost,
                    ads_roas=ads_roas,
                    organic_click_window_weeks=organic_click_window_weeks,
                    target_gmv=target_gmv,
                    target_profit=target_profit,
                    scenario_case=scenario_case,
                    assumption_status_key=assumption_status_key,
                )
                st.session_state["_scroll_to_results"] = True
                st.rerun()

if st.session_state.get("has_generated", False):
    try:
        if st.session_state.get("plan_locked", False) and "_locked_df_all" in st.session_state:
            product_df = st.session_state["_locked_product_df"].copy()
            df_all = st.session_state["_locked_df_all"].copy()
            phase_inputs = st.session_state["_locked_phase_inputs"]
            weeks_per_phase = st.session_state["_locked_weeks_per_phase"]
            effective_ads_roas = st.session_state["_locked_ads_roas"]
            scenario_label = st.session_state.get("_locked_scenario_label", scenario_label)
            scenario_case = st.session_state.get("_locked_scenario_case", scenario_case)
            promo_60d = st.session_state.get("_locked_promo_60d", promo_60d)
            use_fbt = st.session_state.get("_locked_use_fbt", use_fbt)
            logistics_carrier_cost = st.session_state.get("_locked_logistics_carrier_cost", st.session_state.get("_model_logistics_carrier_cost", st.session_state.get("logistics_carrier_cost_manual", logistics_cost)))
            logistics_pick_pack_cost = st.session_state.get("_locked_logistics_pick_pack_cost", st.session_state.get("_model_logistics_pick_pack_cost", st.session_state.get("logistics_pick_pack_cost_manual", 0.0)))
            logistics_return_allowance = st.session_state.get("_locked_logistics_return_allowance", st.session_state.get("_model_logistics_return_allowance", st.session_state.get("logistics_return_allowance_manual", 0.0)))
            logistics_cost = st.session_state.get("_locked_logistics_cost", logistics_cost)
            sample_delivery_cost = st.session_state.get("_locked_sample_delivery_cost", st.session_state.get("_model_sample_delivery_cost", st.session_state.get("sample_shipping_cost_manual", sample_shipping_cost)))
            sample_handling_cost = st.session_state.get("_locked_sample_handling_cost", st.session_state.get("_model_sample_handling_cost", st.session_state.get("sample_handling_cost_manual", 0.0)))
            sample_shipping_cost = st.session_state.get("_locked_sample_shipping_cost", sample_shipping_cost)
            organic_click_window_weeks = st.session_state.get("_locked_organic_click_window_weeks", organic_click_window_weeks)
            target_gmv = st.session_state.get("_locked_target_gmv", target_gmv)
            target_profit = st.session_state.get("_locked_target_profit", target_profit)
            model_ads_roas = st.session_state.get("_locked_base_ads_roas", st.session_state.get("_applied_ads_roas", effective_ads_roas))
            assumption_status_key = normalize_assumption_status(
                st.session_state.get("_locked_assumption_status", st.session_state.get("_applied_assumption_status", assumption_status_key))
            )
        else:
            product_df = st.session_state["_applied_product_df"].copy()
            phase_inputs = [dict(phase) for phase in st.session_state["_applied_phase_inputs"]]
            weeks_per_phase = int(st.session_state["_applied_weeks_per_phase"])
            promo_60d = bool(st.session_state["_applied_promo_60d"])
            use_fbt = bool(st.session_state["_applied_use_fbt"])
            logistics_carrier_cost = float(st.session_state["_applied_logistics_carrier_cost"])
            logistics_pick_pack_cost = float(st.session_state["_applied_logistics_pick_pack_cost"])
            logistics_return_allowance = float(st.session_state["_applied_logistics_return_allowance"])
            logistics_cost = float(st.session_state["_applied_logistics_cost"])
            sample_delivery_cost = float(st.session_state["_applied_sample_delivery_cost"])
            sample_handling_cost = float(st.session_state["_applied_sample_handling_cost"])
            sample_shipping_cost = float(st.session_state["_applied_sample_shipping_cost"])
            model_ads_roas = float(st.session_state["_applied_ads_roas"])
            organic_click_window_weeks = int(st.session_state["_applied_organic_click_window_weeks"])
            target_gmv = float(st.session_state["_applied_target_gmv"])
            target_profit = float(st.session_state["_applied_target_profit"])
            scenario_case = st.session_state["_applied_scenario_case"]
            assumption_status_key = normalize_assumption_status(st.session_state["_applied_assumption_status"])
            adjusted_product_df, effective_ads_roas = apply_scenario_adjustment(product_df, model_ads_roas, scenario_case)
            with st.spinner(T["model_calculating"]):
                df_all = build_weekly_model(
                    product_df=adjusted_product_df,
                    phase_inputs=phase_inputs,
                    weeks_per_phase=int(weeks_per_phase),
                    promo_60d=bool(promo_60d),
                    logistics_cost=float(logistics_cost),
                    sample_shipping_cost=float(sample_shipping_cost),
                    use_fbt=bool(use_fbt),
                    organic_click_window_weeks=int(organic_click_window_weeks),
                    ads_roas=float(effective_ads_roas),
                    language_code=lang,
                )
        assumption_status = assumption_status_label(assumption_status_key)
        model_n_skus = len(product_df)
        scenario_label = {
            "conservative": T["scenario_conservative"],
            "base": T["scenario_base"],
            "upside": T["scenario_upside"],
        }.get(scenario_case, T["scenario_base"])
        phase_summary = build_phase_summary(df_all)
        overall_summary = build_overall_summary(df_all)
        weekly_be = first_positive_profit_week(df_all)
        cumulative_be = first_cumulative_break_even_week(df_all)

        overall = overall_summary.iloc[0]
        weekly_be_label = f"Week {weekly_be}" if weekly_be else T["not_reached"]
        cumulative_be_label = f"Week {cumulative_be}" if cumulative_be else T["not_reached"]
        model_signature = model_input_signature(
            product_df=product_df,
            phase_inputs=phase_inputs,
            weeks_per_phase=weeks_per_phase,
            promo_60d=promo_60d,
            use_fbt=use_fbt,
            logistics_carrier_cost=logistics_carrier_cost,
            logistics_pick_pack_cost=logistics_pick_pack_cost,
            logistics_return_allowance=logistics_return_allowance,
            logistics_cost=logistics_cost,
            sample_delivery_cost=sample_delivery_cost,
            sample_handling_cost=sample_handling_cost,
            sample_shipping_cost=sample_shipping_cost,
            ads_roas=model_ads_roas,
            organic_click_window_weeks=organic_click_window_weeks,
            target_gmv=target_gmv,
            target_profit=target_profit,
            scenario_case=scenario_case,
            assumption_status_key=assumption_status_key,
        )
        current_outcomes = {
            "gmv": float(overall["Total GMV"]),
            "profit": float(overall["Total Profit"]),
            "break_even": cumulative_be,
        }
        if st.session_state.get("_model_signature") != model_signature:
            previous_outcomes = st.session_state.get("_model_current_outcomes")
            if previous_outcomes:
                st.session_state["_model_previous_outcomes"] = previous_outcomes
            st.session_state["_model_current_outcomes"] = current_outcomes
            st.session_state["_model_signature"] = model_signature
            st.session_state["_model_updated_at"] = datetime.now().strftime("%H:%M:%S")
            st.session_state["_model_generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        elif "_model_current_outcomes" not in st.session_state:
            st.session_state["_model_current_outcomes"] = current_outcomes
        if "_model_generated_at" not in st.session_state:
            st.session_state["_model_generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        previous_outcomes = st.session_state.get("_model_previous_outcomes")
        model_updated_at = st.session_state.get("_model_updated_at", datetime.now().strftime("%H:%M:%S"))
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
            ads_roas=float(effective_ads_roas),
            overall=overall,
            driver=total_cost_driver,
            df_all=df_all,
        )
        path_text = path_to_break_even(df_all, cumulative_be, total_cost_driver)
        total_cost_explanation = cost_explanation(total_cost_row)
        diagnosis_text = diagnosis_summary(overall, df_all, total_cost_driver)
        takeaways = commercial_takeaways(overall, df_all, cumulative_be_label, total_cost_driver)
        business_readout = business_readout_items(overall, df_all, cumulative_be_label, total_cost_driver)
        forecast_range_values = forecast_range(overall, assumption_status)
        generated_at = st.session_state["_model_generated_at"]
        logistics_display = logistics_display_text(product_df, float(logistics_cost), bool(use_fbt))
        if not use_fbt:
            logistics_display = logistics_detail_display(logistics_carrier_cost, logistics_pick_pack_cost, logistics_return_allowance)
        assumption_summary = build_assumption_summary(
            phase_inputs=phase_inputs,
            weeks_per_phase=int(weeks_per_phase),
            n_skus=model_n_skus,
            logistics_display=logistics_display,
            sample_shipping_cost=float(sample_shipping_cost),
            ads_roas=float(effective_ads_roas),
            organic_click_window_weeks=int(organic_click_window_weeks),
            promo_60d=bool(promo_60d),
            use_fbt=bool(use_fbt),
        )
        next_actions = recommended_next_actions(
            overall=overall,
            df_all=df_all,
            phase_summary=phase_summary,
            product_df=product_df,
            cumulative_be=cumulative_be,
            driver=total_cost_driver,
        )

        st.markdown('<div class="section-anchor" id="results-start"></div>', unsafe_allow_html=True)
        if st.session_state.get("_scroll_to_results", False):
            components.html(
                """
                <script>
                const anchor = window.parent.document.getElementById("results-start");
                if (anchor) {
                    anchor.scrollIntoView({behavior: "smooth", block: "start"});
                }
                </script>
                """,
                height=0,
            )
            st.session_state["_scroll_to_results"] = False

        render_product_masthead(model_updated_at)
        render_workspace_nav()
        render_hero(
            overall=overall,
            weeks=int(weeks_per_phase) * len(PHASES),
            skus=model_n_skus,
            break_even_label=cumulative_be_label,
        )
        render_executive_insight(overall, df_all, cumulative_be_label, total_cost_driver, model_updated_at)
        render_outcome_context(
            forecast_range_values,
            overall,
            previous_outcomes,
            target_gmv,
            target_profit,
        )
        render_growth_engine(overall)
        with st.container(border=True):
            render_chart_panel_header(
                T["forecast_gmv"],
                kicker=T["section_primary"],
                icon="trend",
                legends=[
                    (T["forecast_gmv"], CHART_COLORS["gmv"], "line"),
                    (T["total_cost_label"], CHART_COLORS["cost"], "line"),
                    (T["forecast_band"], "#CBD8FF", "band"),
                ],
            )
            st.plotly_chart(
                make_scale_chart(
                    df_all,
                    T["forecast_gmv"],
                    weekly_be,
                    height=450,
                    forecast_spread=forecast_range_values["spread"],
                    target_gmv=target_gmv,
                ),
                use_container_width=True,
                config={"displayModeBar": False, "responsive": True},
            )
            render_chart_panel_caption(T["forecast_chart_caption"])
        render_decision_panel(overall, df_all, cumulative_be_label, total_cost_driver)
        if not meeting_mode:
            render_dashboard_intro(
                scenario_snapshot_text(model_n_skus, weeks_per_phase, phase_inputs, effective_ads_roas, scenario_label),
                diagnosis_text,
            )

        if (not meeting_mode) and (not st.session_state.get("plan_locked", False)):
            if st.button(T["lock_plan"], key="lock_plan_btn", icon=":material/lock:"):
                st.session_state["plan_locked"] = True
                st.session_state["_locked_product_df"] = product_df.copy()
                st.session_state["_locked_df_all"] = df_all.copy()
                st.session_state["_locked_phase_inputs"] = phase_inputs
                st.session_state["_locked_weeks_per_phase"] = int(weeks_per_phase)
                st.session_state["_locked_ads_roas"] = float(effective_ads_roas)
                st.session_state["_locked_base_ads_roas"] = float(model_ads_roas)
                st.session_state["_locked_scenario_label"] = scenario_label
                st.session_state["_locked_scenario_case"] = scenario_case
                st.session_state["_locked_promo_60d"] = bool(promo_60d)
                st.session_state["_locked_use_fbt"] = bool(use_fbt)
                st.session_state["_locked_logistics_carrier_cost"] = float(logistics_carrier_cost)
                st.session_state["_locked_logistics_pick_pack_cost"] = float(logistics_pick_pack_cost)
                st.session_state["_locked_logistics_return_allowance"] = float(logistics_return_allowance)
                st.session_state["_locked_logistics_cost"] = float(logistics_cost)
                st.session_state["_locked_sample_delivery_cost"] = float(sample_delivery_cost)
                st.session_state["_locked_sample_handling_cost"] = float(sample_handling_cost)
                st.session_state["_locked_sample_shipping_cost"] = float(sample_shipping_cost)
                st.session_state["_locked_organic_click_window_weeks"] = int(organic_click_window_weeks)
                st.session_state["_locked_target_gmv"] = float(target_gmv)
                st.session_state["_locked_target_profit"] = float(target_profit)
                st.session_state["_locked_assumption_status"] = assumption_status_key
                st.rerun()
        target_items = target_comparison_items(overall, target_gmv, target_profit)

        render_section_anchor("phase-workspace")
        render_growth_path_strip(phase_summary, cumulative_be_label, total_cost_driver)
        render_phase_explorer(phase_inputs, df_all, phase_summary)

        render_section_header(T["charts"], T["section_primary"])
        chart_left, chart_right = st.columns(2, gap="large")
        with chart_left:
            with st.container(border=True):
                render_chart_panel_header(
                    T["sales_contribution"],
                    icon="profit",
                    legends=[
                        (T["profit_label"], CHART_COLORS["profit"], "line"),
                        (T["growth_investment"], "#7C74E8", "band"),
                    ],
                )
                st.plotly_chart(make_profit_investment_chart(df_all, T["sales_contribution"], height=320), use_container_width=True, config={"displayModeBar": False, "responsive": True})
                render_chart_panel_caption(T["weekly_profit_caption"])
        with chart_right:
            with st.container(border=True):
                render_chart_panel_header(
                    T["cumulative_profit_trend"],
                    icon="target",
                    legends=[
                        (T["cumulative_profit_trend"], CHART_COLORS["cumulative"], "line"),
                        (T["cumulative_be"], "#6B7280", "dash"),
                    ],
                )
                st.plotly_chart(
                    make_cumulative_profit_chart(
                        df_all,
                        cumulative_be,
                        height=320,
                        target_profit=target_profit,
                    ),
                    use_container_width=True,
                    config={"displayModeBar": False, "responsive": True},
                )
                render_chart_panel_caption(T["cumulative_profit_caption"])
        if meeting_mode:
            support_container = st.expander(T["supporting_charts"], expanded=False)
        else:
            render_section_header(T["supporting_charts"], T["section_secondary"])
            support_container = st.container()
        with support_container:
            support_col1, support_col2, support_col3 = st.columns(3, gap="large")
            with support_col1:
                with st.container(border=True):
                    render_chart_panel_header(
                        T["funnel_summary"],
                        kicker=T["section_secondary"],
                        icon="sample",
                    )
                    render_funnel_summary(df_all)
                    render_chart_panel_caption(T["funnel_business_lens"].format(
                        samples=f"{overall['Total Samples']:,.0f}",
                        videos=f"{overall['Total Videos']:,.0f}",
                        clicks=f"{overall['Total Clicks']:,.0f}",
                        orders=f"{overall['Total Orders']:,.0f}",
                    ))
            with support_col2:
                with st.container(border=True):
                    render_chart_panel_header(
                        T["channel_mix"],
                        kicker=T["section_secondary"],
                        icon="channel",
                    )
                    st.plotly_chart(make_channel_mix_chart(phase_summary), use_container_width=True, config={"displayModeBar": False, "responsive": True})
                    render_chart_panel_caption(T["channel_business_lens"])
            with support_col3:
                with st.container(border=True):
                    render_chart_panel_header(
                        T["investment_split"],
                        kicker=T["section_secondary"],
                        icon="investment",
                    )
                    st.plotly_chart(make_investment_split_chart(df_all), use_container_width=True, config={"displayModeBar": False, "responsive": True})
                    render_chart_panel_caption(T["cost_business_lens"].format(driver=total_cost_driver))

        render_section_anchor("action-workspace")
        render_section_header(T["next_actions"])
        render_grouped_actions(next_actions)

        detailed_analysis_label = {
            "en": "Detailed Analysis",
            "zh": "详细分析",
            "de": "Detailanalyse",
            "nl": "Detailanalyse",
        }[lang]

        with st.expander(detailed_analysis_label, expanded=False):
            st.markdown('<div class="report-appendix">', unsafe_allow_html=True)

            if target_items:
                st.subheader(T["target_comparison"])
                render_kpi_grid(target_items)

            render_subtle_note(
                scenario_snapshot_text(model_n_skus, weeks_per_phase, phase_inputs, effective_ads_roas, scenario_label),
                T["scenario_snapshot"],
            )
            render_executive_brief(
                executive_brief_items(
                    overall=overall,
                    df_all=df_all,
                    weekly_be_label=weekly_be_label,
                    cumulative_be_label=cumulative_be_label,
                    driver=total_cost_driver,
                )
            )
            st.caption(T["planning_disclaimer"])

            st.subheader(T["commercial_takeaways"])
            render_business_readout(business_readout)
            render_kpi_grid([
                (T["weekly_profit"], f"Week {weekly_be}" if weekly_be else T["not_reached"], "#178A62" if weekly_be else "#98A2B3"),
                (T["cumulative_be"], f"Week {cumulative_be}" if cumulative_be else T["not_reached"], "#178A62" if cumulative_be else "#98A2B3"),
            ], compact=True)
            render_kpi_grid([
                (takeaways[0][0], takeaways[0][1], "#4F46E5"),
                (takeaways[1][0], takeaways[1][1], "#315EEC"),
                (takeaways[2][0], takeaways[2][1], "#178A62"),
                (takeaways[3][0], takeaways[3][1], "#94A3B8"),
            ])
            render_subtle_note(takeaways[4][1], takeaways[4][0])

            st.subheader(T["key_assumptions"])
            render_kpi_grid(assumption_summary)

            st.subheader(T["sample_roi_title"])
            render_kpi_grid([
                (T["gmv_per_sample"], money(overall["GMV / Sample"], 0), "#315EEC"),
                (T["profit_per_sample"], money(overall["Profit / Sample"], 0), "#178A62" if overall["Profit / Sample"] >= 0 else "#B42318"),
                (T["videos_per_sample_kpi"], f"{overall['Videos / Sample']:.2f}", "#94A3B8"),
                (T["orders_per_sample"], f"{overall['Orders / Sample']:.2f}", "#178A62"),
                (T["sample_gmv_roi"], f"{overall['GMV / Sample Cost']:.1f}x", "#4F46E5"),
                (T["ads_investment"], money(overall["Ads Investment"], 0), "#6B7280"),
            ], compact=True)
            render_status_panel(
                T["sample_roi_title"],
                T["sample_roi_text"].format(
                    gmv_per_sample=money(overall["GMV / Sample"], 0),
                    orders_per_sample=f"{overall['Orders / Sample']:.2f}",
                ),
                tone="info",
                compact=True,
            )

            st.subheader(T["health_check"])
            for line in narrative:
                st.write(f"- {line}")
            for level, check in health_checks:
                if level == "ok":
                    render_status_panel(T["health_check"], check, tone="success", compact=True)
                elif level == "info":
                    render_status_panel(T["health_check"], check, tone="info", compact=True)
                else:
                    render_status_panel(T["health_check"], check, tone="warning", compact=True)
            with st.expander(T["path_to_be"], expanded=False):
                if cumulative_be:
                    render_status_panel(T["path_to_be"], path_text, tone="success", compact=True)
                else:
                    render_status_panel(T["path_to_be"], path_text, tone="warning", compact=True)

            with st.expander(T["internal_logic_checklist"], expanded=False):
                st.caption(T["internal_logic_intro"])
                for title, body in internal_logic_signals(
                    product_df=product_df,
                    phase_inputs=phase_inputs,
                    promo_60d=bool(promo_60d),
                    use_fbt=bool(use_fbt),
                    ads_roas=float(effective_ads_roas),
                ):
                    render_status_panel(T["internal_logic_context"], body, tone="info", compact=True, kicker=title)
                render_model_logic()
                st.caption(T["planning_disclaimer"])

            with st.expander(T["debug_details"], expanded=False):
                st.markdown(
                    debug_details_html(
                        overall=overall,
                        scenario_key=scenario_case,
                        effective_ads_roas=effective_ads_roas,
                        target_gmv=target_gmv,
                        target_profit=target_profit,
                        n_skus=model_n_skus,
                        locked=st.session_state.get("plan_locked", False),
                    ),
                    unsafe_allow_html=True,
                )

            if not meeting_mode:
                with st.expander(T["product_profile"], expanded=False):
                    product_display = product_df.copy()
                    product_display["Category"] = product_display["Category"].map(category_label)
                    product_display["Subcategory"] = product_display["Subcategory"].map(subcategory_label)
                    product_display[T["fbt_status"]] = product_df["AOV"].map(
                        lambda x: sku_fbt_status(float(x), float(logistics_cost), bool(use_fbt))[0]
                    )
                    product_display[T["effective_logistics"]] = product_df["AOV"].map(
                        lambda x: money(sku_fbt_status(float(x), float(logistics_cost), bool(use_fbt))[1], 2)
                    )
                    product_display["AOV"] = product_display["AOV"].map(lambda x: money(x, 2))
                    product_display["Gross Margin"] = product_display["Gross Margin"].map(lambda x: pct(x, 0))
                    product_display["Platform Fee Rate"] = product_display["Platform Fee Rate"].map(lambda x: pct(x, 0))
                    product_display["Click-to-order Rate"] = product_display["Click-to-order Rate"].map(lambda x: pct(x, 1))
                    product_display["ShopTab GMV Share"] = product_display["ShopTab GMV Share"].map(lambda x: pct(x, 0))
                    product_display["Organic Creator Commission Rate"] = product_display["Organic Creator Commission Rate"].map(lambda x: pct(x, 1))
                    product_display["Paid Creator Commission Rate"] = product_display["Paid Creator Commission Rate"].map(lambda x: pct(x, 1))
                    product_display = product_display.rename(columns={
                        "Category": T["category"],
                        "Subcategory": T["subcategory"],
                        "ShopTab GMV Share": T["shoptab_share"],
                        "Organic Creator Commission Rate": T["organic_commission_sku"],
                        "Paid Creator Commission Rate": T["paid_commission_sku"],
                    })
                    st.markdown(dataframe_html(product_display), unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

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

        customer_summary = build_customer_summary(
            overall,
            phase_summary,
            weekly_be_label,
            cumulative_be_label,
            meeting_notes,
            assumption_status,
            total_cost_explanation,
            forecast_range_values,
            assumption_summary=assumption_summary,
            next_actions=next_actions,
        )
        meeting_html = meeting_recap_html(
            overall=overall,
            narrative=narrative,
            health_checks=health_checks,
            path_text=path_text,
            weeks=int(weeks_per_phase) * len(PHASES),
            skus=model_n_skus,
            generated_at=generated_at,
            meeting_notes=meeting_notes,
            assumption_status=assumption_status,
            takeaways=takeaways,
            cost_explanation_text=total_cost_explanation,
            diagnosis_text=diagnosis_text,
            forecast_range_values=forecast_range_values,
            assumption_summary=assumption_summary,
            next_actions=next_actions,
        )
        one_pager_pdf = meeting_summary_pdf(
            overall=overall,
            narrative=narrative,
            health_checks=health_checks,
            path_text=path_text,
            weeks=int(weeks_per_phase) * len(PHASES),
            skus=model_n_skus,
            generated_at=generated_at,
            meeting_notes=meeting_notes,
            assumption_status=assumption_status,
            takeaways=takeaways,
            cost_explanation_text=total_cost_explanation,
            diagnosis_text=diagnosis_text,
            forecast_range_values=forecast_range_values,
            assumption_summary=assumption_summary,
            next_actions=next_actions,
            df_all=df_all,
            product_df=product_df,
            detail_pack=False,
            language_code=lang,
        )
        meeting_pdf = meeting_summary_pdf(
            overall=overall,
            narrative=narrative,
            health_checks=health_checks,
            path_text=path_text,
            weeks=int(weeks_per_phase) * len(PHASES),
            skus=model_n_skus,
            generated_at=generated_at,
            meeting_notes=meeting_notes,
            assumption_status=assumption_status,
            takeaways=takeaways,
            cost_explanation_text=total_cost_explanation,
            diagnosis_text=diagnosis_text,
            forecast_range_values=forecast_range_values,
            assumption_summary=assumption_summary,
            next_actions=next_actions,
            df_all=df_all,
            product_df=product_df,
            detail_pack=True,
            language_code=lang,
        )
        export_date = datetime.now().strftime("%Y-%m-%d")
        export_prefix = (
            f"{safe_filename_part(meeting_notes.get('brand_name'), 'Brand')}_"
            f"{safe_filename_part(meeting_notes.get('scenario_name'), 'Scenario')}_"
            f"TikTokShop_GrowthPlan_{export_date}"
        )
        render_section_anchor("export-workspace")
        render_section_header(T["export_materials"])
        if not meeting_mode:
            st.markdown(f'<div class="export-shell-caption">{escape(T["export_materials_note"])}</div>', unsafe_allow_html=True)
        dl_summary, dl_html, dl_one_pager, dl_pdf = st.columns(4)
        with dl_summary:
            st.markdown('<div class="export-card-shell">', unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(
                    f'<div class="export-card-title">{T["download_customer_summary"]}</div>'
                    f'<div class="export-card-desc">{T["export_summary_desc"]}</div>',
                    unsafe_allow_html=True,
                )
                st.download_button(
                    T["download_customer_summary"],
                    data=csv_bytes(customer_summary),
                    file_name=f"{export_prefix}_summary.csv",
                    mime="text/csv",
                    icon=":material/download:",
                    width="stretch",
                )
            st.markdown('</div>', unsafe_allow_html=True)
        with dl_html:
            st.markdown('<div class="export-card-shell">', unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(
                    f'<div class="export-card-title">{T["download_meeting_html"]}</div>'
                    f'<div class="export-card-desc">{T["export_html_desc"]}</div>',
                    unsafe_allow_html=True,
                )
                st.download_button(
                    T["download_meeting_html"],
                    data=meeting_html.encode("utf-8"),
                    file_name=f"{export_prefix}_summary.html",
                    mime="text/html",
                    icon=":material/download:",
                    width="stretch",
                )
            st.markdown('</div>', unsafe_allow_html=True)
        with dl_one_pager:
            st.markdown('<div class="export-card-shell">', unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(
                    f'<div class="export-card-title">{T["download_one_pager_pdf"]}</div>'
                    f'<div class="export-card-desc">{T["export_one_pager_desc"]}</div>',
                    unsafe_allow_html=True,
                )
                st.download_button(
                    T["download_one_pager_pdf"],
                    data=one_pager_pdf,
                    file_name=f"{export_prefix}_one_pager.pdf",
                    mime="application/pdf",
                    icon=":material/download:",
                    width="stretch",
                )
            st.markdown('</div>', unsafe_allow_html=True)
        with dl_pdf:
            st.markdown('<div class="export-card-shell">', unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(
                    f'<div class="export-card-title">{T["download_meeting_pdf"]}</div>'
                    f'<div class="export-card-desc">{T["export_detail_desc"]}</div>',
                    unsafe_allow_html=True,
                )
                st.download_button(
                    T["download_meeting_pdf"],
                    data=meeting_pdf,
                    file_name=f"{export_prefix}_detail.pdf",
                    mime="application/pdf",
                    icon=":material/download:",
                    width="stretch",
                )
            st.markdown('</div>', unsafe_allow_html=True)
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
                    "Paid GMV Lift": T["paid_gmv_increment"],
                    "ShopTab Organic GMV": f"{T['shoptab_gmv']} Organic",
                    "ShopTab Paid GMV": f"{T['shoptab_gmv']} Paid",
                    "ShopTab GMV": T["shoptab_gmv"],
                })
                st.markdown(dataframe_html(phase_summary_display), unsafe_allow_html=True)

        if not meeting_mode:
            with st.expander(T["view_details"], expanded=False):
                st.markdown(f"**{T['overall_summary']}**")
                st.markdown(
                    dataframe_html(
                        format_table(
                            overall_summary,
                            money_cols=money_cols,
                            pct_cols=["Profit Margin", "Contribution Margin"],
                            number_cols=number_cols,
                            decimal_cols=decimal_cols,
                        )
                    ),
                    unsafe_allow_html=True,
                )
                st.markdown(f"**{T['weekly_details']}**")
                weekly_display = format_table(df_all.drop(columns=["Phase Key"]), money_cols=money_cols, pct_cols=["Ads Take Rate", "Contribution Margin"], number_cols=number_cols, decimal_cols=decimal_cols)
                weekly_display = weekly_display.rename(columns={
                    "Ads Take Rate": T["take_rate"],
                    "Paid GMV Lift": T["paid_gmv_increment"],
                    "ShopTab Organic GMV": f"{T['shoptab_gmv']} Organic",
                    "ShopTab Paid GMV": f"{T['shoptab_gmv']} Paid",
                    "ShopTab GMV": T["shoptab_gmv"],
                })
                st.markdown(dataframe_html(weekly_display), unsafe_allow_html=True)

                d1, d2 = st.columns(2)
                d1.download_button(T["download_weekly"], data=csv_bytes(df_all), file_name=f"{export_prefix}_weekly_details.csv", mime="text/csv")
                d2.download_button(T["download_phase"], data=csv_bytes(phase_summary), file_name=f"{export_prefix}_phase_summary.csv", mime="text/csv")

    except Exception as e:
        st.error(f"{T['input_error']}: {e}")
