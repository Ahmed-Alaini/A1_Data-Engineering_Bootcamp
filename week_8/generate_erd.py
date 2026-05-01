"""
Generate a precise ERD diagram for the Olist DWH schema.
Reads the actual schema definition and draws boxes + relationship lines.
Output: doc/ERD_DWH.png
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from pathlib import Path

# ── Colour palette ─────────────────────────────────────────────────────────────
C_FACT_HEADER  = "#C0392B"   # dark red   – fact table header
C_FACT_BG      = "#FADBD8"   # light red  – fact table rows
C_DIM_HEADER   = "#1A5276"   # dark blue  – dim table header
C_DIM_BG       = "#D6EAF8"   # light blue – dim table rows
C_BORDER       = "#2C3E50"
C_FK_LINE      = "#7F8C8D"
C_PK_TEXT      = "#922B21"   # red for PK labels
C_FK_TEXT      = "#1A5276"   # blue for FK labels
C_HEADER_TEXT  = "#FFFFFF"
C_ROW_TEXT     = "#2C3E50"

# ── Schema definition (exact columns from create_dwh_tables.sql) ───────────────
TABLES = {

    # ── DIMENSIONS ──────────────────────────────────────────────────────────────
    "dim_date": {
        "type": "dim",
        "cols": [
            ("PK", "date_sk",       "INTEGER"),
            ("",   "full_date",     "DATE"),
            ("",   "year",          "INTEGER"),
            ("",   "quarter",       "INTEGER"),
            ("",   "month",         "INTEGER"),
            ("",   "month_name",    "TEXT"),
            ("",   "day",           "INTEGER"),
            ("",   "day_of_week",   "INTEGER"),
            ("",   "day_name",      "TEXT"),
            ("",   "is_weekend",    "BOOLEAN"),
        ],
    },
    "dim_geolocation": {
        "type": "dim",
        "cols": [
            ("PK", "geolocation_sk", "SERIAL"),
            ("",   "zip_code",       "BIGINT"),
            ("",   "latitude",       "DOUBLE PRECISION"),
            ("",   "longitude",      "DOUBLE PRECISION"),
            ("",   "city",           "TEXT"),
            ("",   "state",          "TEXT"),
        ],
    },
    "dim_customers": {
        "type": "dim",
        "cols": [
            ("PK", "customer_sk",       "SERIAL"),
            ("",   "customer_id",       "TEXT"),
            ("",   "customer_unique_id","TEXT"),
            ("FK", "geolocation_sk",    "INTEGER"),
        ],
    },
    "dim_sellers": {
        "type": "dim",
        "cols": [
            ("PK", "seller_sk",      "SERIAL"),
            ("",   "seller_id",      "TEXT"),
            ("FK", "geolocation_sk", "INTEGER"),
        ],
    },
    "dim_products": {
        "type": "dim",
        "cols": [
            ("PK", "product_sk",                    "SERIAL"),
            ("",   "product_id",                    "TEXT"),
            ("",   "product_category_name",         "TEXT"),
            ("",   "product_category_name_english", "TEXT"),
            ("",   "product_name_length",           "INTEGER"),
            ("",   "product_description_length",    "INTEGER"),
            ("",   "product_photos_qty",            "INTEGER"),
            ("",   "product_weight_g",              "NUMERIC"),
            ("",   "product_length_cm",             "NUMERIC"),
            ("",   "product_height_cm",             "NUMERIC"),
            ("",   "product_width_cm",              "NUMERIC"),
        ],
    },
    "dim_order_status": {
        "type": "dim",
        "cols": [
            ("PK", "order_status_sk", "SERIAL"),
            ("",   "order_status",    "TEXT"),
        ],
    },
    "dim_payment_type": {
        "type": "dim",
        "cols": [
            ("PK", "payment_type_sk", "SERIAL"),
            ("",   "payment_type",    "TEXT"),
        ],
    },
    "dim_lead_origin": {
        "type": "dim",
        "cols": [
            ("PK", "lead_origin_sk", "SERIAL"),
            ("",   "origin",         "TEXT"),
            ("",   "landing_page_id","TEXT"),
        ],
    },
    "dim_lead_profile": {
        "type": "dim",
        "cols": [
            ("PK", "lead_profile_sk",       "SERIAL"),
            ("",   "lead_type",             "TEXT"),
            ("",   "lead_behaviour_profile","TEXT"),
            ("",   "business_type",         "TEXT"),
            ("",   "average_stock",         "TEXT"),
            ("",   "has_company",           "BOOLEAN"),
            ("",   "has_gtin",              "BOOLEAN"),
        ],
    },
    "dim_business_segment": {
        "type": "dim",
        "cols": [
            ("PK", "business_segment_sk", "SERIAL"),
            ("",   "business_segment",    "TEXT"),
        ],
    },

    # ── FACTS ───────────────────────────────────────────────────────────────────
    "fact_order_items": {
        "type": "fact",
        "cols": [
            ("PK", "order_item_sk",   "SERIAL"),
            ("",   "order_id",        "TEXT"),
            ("",   "order_item_id",   "INTEGER"),
            ("FK", "customer_sk",     "INTEGER"),
            ("FK", "product_sk",      "INTEGER"),
            ("FK", "seller_sk",       "INTEGER"),
            ("FK", "order_status_sk", "INTEGER"),
            ("FK", "purchase_date_sk","INTEGER"),
            ("",   "price",           "NUMERIC"),
            ("",   "freight_value",   "NUMERIC"),
            ("",   "total_item_value","NUMERIC"),
        ],
    },
    "fact_payments": {
        "type": "fact",
        "cols": [
            ("PK", "payment_sk",          "SERIAL"),
            ("",   "order_id",            "TEXT"),
            ("",   "payment_sequential",  "INTEGER"),
            ("FK", "customer_sk",         "INTEGER"),
            ("FK", "payment_type_sk",     "INTEGER"),
            ("FK", "purchase_date_sk",    "INTEGER"),
            ("",   "payment_installments","INTEGER"),
            ("",   "payment_value",       "NUMERIC"),
        ],
    },
    "fact_delivery_performance": {
        "type": "fact",
        "cols": [
            ("PK", "delivery_sk",               "SERIAL"),
            ("",   "order_id",                  "TEXT"),
            ("FK", "customer_sk",               "INTEGER"),
            ("FK", "order_status_sk",           "INTEGER"),
            ("FK", "purchase_date_sk",          "INTEGER"),
            ("FK", "approved_date_sk",          "INTEGER"),
            ("FK", "delivered_carrier_date_sk", "INTEGER"),
            ("FK", "delivered_customer_date_sk","INTEGER"),
            ("FK", "estimated_delivery_date_sk","INTEGER"),
            ("",   "approval_hours",            "NUMERIC"),
            ("",   "carrier_delivery_days",     "NUMERIC"),
            ("",   "customer_delivery_days",    "NUMERIC"),
            ("",   "estimated_vs_actual_days",  "NUMERIC"),
            ("",   "is_late",                   "BOOLEAN"),
        ],
    },
    "fact_reviews": {
        "type": "fact",
        "cols": [
            ("PK", "review_sk",              "SERIAL"),
            ("",   "review_id",              "TEXT"),
            ("",   "order_id",              "TEXT"),
            ("FK", "customer_sk",            "INTEGER"),
            ("FK", "review_creation_date_sk","INTEGER"),
            ("FK", "review_answer_date_sk",  "INTEGER"),
            ("",   "review_score",           "INTEGER"),
            ("",   "has_comment",            "BOOLEAN"),
            ("",   "response_hours",         "NUMERIC"),
        ],
    },
    "fact_seller_leads": {
        "type": "fact",
        "cols": [
            ("PK", "seller_lead_sk",              "SERIAL"),
            ("",   "mql_id",                      "TEXT"),
            ("FK", "seller_sk",                   "INTEGER"),
            ("FK", "lead_origin_sk",              "INTEGER"),
            ("FK", "lead_profile_sk",             "INTEGER"),
            ("FK", "business_segment_sk",         "INTEGER"),
            ("FK", "first_contact_date_sk",       "INTEGER"),
            ("FK", "won_date_sk",                 "INTEGER"),
            ("",   "sdr_id",                      "TEXT"),
            ("",   "sr_id",                       "TEXT"),
            ("",   "declared_product_catalog_size","NUMERIC"),
            ("",   "declared_monthly_revenue",    "NUMERIC"),
            ("",   "days_to_close",               "NUMERIC"),
            ("",   "is_closed",                   "BOOLEAN"),
        ],
    },
}

# ── Relationships (from_table, from_col, to_table, to_col) ────────────────────
RELATIONSHIPS = [
    # dim_geolocation ← dim_customers / dim_sellers
    ("dim_customers",           "geolocation_sk",              "dim_geolocation",      "geolocation_sk"),
    ("dim_sellers",             "geolocation_sk",              "dim_geolocation",      "geolocation_sk"),
    # fact_order_items → dims
    ("fact_order_items",        "customer_sk",                 "dim_customers",        "customer_sk"),
    ("fact_order_items",        "product_sk",                  "dim_products",         "product_sk"),
    ("fact_order_items",        "seller_sk",                   "dim_sellers",          "seller_sk"),
    ("fact_order_items",        "order_status_sk",             "dim_order_status",     "order_status_sk"),
    ("fact_order_items",        "purchase_date_sk",            "dim_date",             "date_sk"),
    # fact_payments → dims
    ("fact_payments",           "customer_sk",                 "dim_customers",        "customer_sk"),
    ("fact_payments",           "payment_type_sk",             "dim_payment_type",     "payment_type_sk"),
    ("fact_payments",           "purchase_date_sk",            "dim_date",             "date_sk"),
    # fact_delivery_performance → dims
    ("fact_delivery_performance","customer_sk",                "dim_customers",        "customer_sk"),
    ("fact_delivery_performance","order_status_sk",            "dim_order_status",     "order_status_sk"),
    ("fact_delivery_performance","purchase_date_sk",           "dim_date",             "date_sk"),
    ("fact_delivery_performance","approved_date_sk",           "dim_date",             "date_sk"),
    ("fact_delivery_performance","delivered_carrier_date_sk",  "dim_date",             "date_sk"),
    ("fact_delivery_performance","delivered_customer_date_sk", "dim_date",             "date_sk"),
    ("fact_delivery_performance","estimated_delivery_date_sk", "dim_date",             "date_sk"),
    # fact_reviews → dims
    ("fact_reviews",            "customer_sk",                 "dim_customers",        "customer_sk"),
    ("fact_reviews",            "review_creation_date_sk",     "dim_date",             "date_sk"),
    ("fact_reviews",            "review_answer_date_sk",       "dim_date",             "date_sk"),
    # fact_seller_leads → dims
    ("fact_seller_leads",       "seller_sk",                   "dim_sellers",          "seller_sk"),
    ("fact_seller_leads",       "lead_origin_sk",              "dim_lead_origin",      "lead_origin_sk"),
    ("fact_seller_leads",       "lead_profile_sk",             "dim_lead_profile",     "lead_profile_sk"),
    ("fact_seller_leads",       "business_segment_sk",         "dim_business_segment", "business_segment_sk"),
    ("fact_seller_leads",       "first_contact_date_sk",       "dim_date",             "date_sk"),
    ("fact_seller_leads",       "won_date_sk",                 "dim_date",             "date_sk"),
]

# ── Table layout positions (x, y) in data coordinates ─────────────────────────
# Canvas: 60 wide × 55 tall
POSITIONS = {
    # centre – facts (column)
    "fact_order_items":          (22, 44),
    "fact_payments":             (22, 27),
    "fact_delivery_performance": (22, 11),
    "fact_reviews":              (44, 44),
    "fact_seller_leads":         (44, 20),

    # left column – dims
    "dim_date":                  (1,  30),
    "dim_customers":             (1,  44),
    "dim_geolocation":           (1,  51),

    # top dims
    "dim_products":              (22, 54),
    "dim_sellers":               (10, 54),
    "dim_order_status":          (35, 54),

    # right dims
    "dim_payment_type":          (55, 30),

    # bottom-right dims (leads)
    "dim_lead_origin":           (55, 44),
    "dim_lead_profile":          (55, 15),
    "dim_business_segment":      (55, 6),
}

BOX_W = 18   # box width  (data units)
ROW_H = 1.1  # row height (data units)
HEADER_H = 1.4

def draw_table(ax, name, table, x, y):
    """Draw one table box; return dict of {col_name: (cx, cy)} anchor points."""
    cols  = table["cols"]
    ttype = table["type"]
    h_col = C_FACT_HEADER if ttype == "fact" else C_DIM_HEADER
    b_col = C_FACT_BG     if ttype == "fact" else C_DIM_BG

    anchors = {}
    total_h = HEADER_H + ROW_H * len(cols)

    # outer border
    rect = mpatches.FancyBboxPatch(
        (x, y - total_h), BOX_W, total_h,
        boxstyle="round,pad=0.05",
        linewidth=1.2, edgecolor=C_BORDER,
        facecolor=b_col, zorder=2,
    )
    ax.add_patch(rect)

    # header background
    header = mpatches.FancyBboxPatch(
        (x, y - HEADER_H), BOX_W, HEADER_H,
        boxstyle="round,pad=0.05",
        linewidth=0, edgecolor="none",
        facecolor=h_col, zorder=3,
    )
    ax.add_patch(header)

    # header text
    prefix = "[F] " if ttype == "fact" else "[D] "
    ax.text(
        x + BOX_W / 2, y - HEADER_H / 2,
        prefix + name,
        ha="center", va="center",
        fontsize=6.5, fontweight="bold",
        color=C_HEADER_TEXT, zorder=4,
        clip_on=False,
    )

    # separator line below header
    ax.plot([x, x + BOX_W], [y - HEADER_H, y - HEADER_H],
            color=C_BORDER, linewidth=0.8, zorder=4)

    # rows
    for i, (key, col, dtype) in enumerate(cols):
        ry = y - HEADER_H - ROW_H * i - ROW_H / 2

        # row bg stripe
        if i % 2 == 1:
            stripe_col = "#EBF5FB" if ttype == "dim" else "#FADBD8"
            ax.add_patch(plt.Rectangle(
                (x, y - HEADER_H - ROW_H * (i + 1)),
                BOX_W, ROW_H,
                color=stripe_col, zorder=2,
            ))

        # key badge
        if key == "PK":
            badge_col, badge_text = "#F39C12", "PK"
            text_col = C_PK_TEXT
        elif key == "FK":
            badge_col, badge_text = "#2980B9", "FK"
            text_col = C_FK_TEXT
        else:
            badge_col, badge_text = None, ""
            text_col = C_ROW_TEXT

        if badge_col:
            ax.text(x + 0.3, ry, badge_text,
                    ha="left", va="center",
                    fontsize=5, fontweight="bold",
                    color=badge_col, zorder=4)

        # column name
        ax.text(x + 2.0, ry, col,
                ha="left", va="center",
                fontsize=5.5, color=text_col,
                fontweight="bold" if key in ("PK", "FK") else "normal",
                zorder=4)

        # data type (right-aligned)
        ax.text(x + BOX_W - 0.3, ry, dtype,
                ha="right", va="center",
                fontsize=4.5, color="#626567",
                style="italic", zorder=4)

        # anchor = left-center of this row
        anchors[col] = (x, ry)

    return anchors


def get_edge_points(src_anchor, dst_anchor, src_x, dst_x, bw=BOX_W):
    """Return (x0,y0, x1,y1) exit/entry points for a relationship line."""
    sx, sy = src_anchor
    dx, dy = dst_anchor
    # decide which side of each box to exit/enter
    if sx < dx:
        return (sx + bw, sy), (dx, dy)
    else:
        return (sx, sy), (dx + bw, dy)


def draw_relationships(ax, all_anchors):
    seen_pairs = {}  # deduplicate same table-to-table connections
    for src_tbl, src_col, dst_tbl, dst_col in RELATIONSHIPS:
        if src_tbl not in all_anchors or dst_tbl not in all_anchors:
            continue
        if src_col not in all_anchors[src_tbl]:
            continue
        if dst_col not in all_anchors[dst_tbl]:
            continue

        src_a = all_anchors[src_tbl][src_col]
        dst_a = all_anchors[dst_tbl][dst_col]

        sx, sy = POSITIONS[src_tbl]
        dx, dy = POSITIONS[dst_tbl]

        (x0, y0), (x1, y1) = get_edge_points(src_a, dst_a, sx, dx)

        ax.annotate(
            "", xy=(x1, y1), xytext=(x0, y0),
            arrowprops=dict(
                arrowstyle="-|>",
                color=C_FK_LINE,
                lw=0.8,
                connectionstyle="arc3,rad=0.05",
            ),
            zorder=1,
        )


# ── Main drawing ───────────────────────────────────────────────────────────────
def main():
    fig_w, fig_h = 28, 22   # inches
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=150)
    ax.set_xlim(-1, 75)
    ax.set_ylim(-2, 60)
    ax.axis("off")
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#F8F9FA")

    # title
    ax.text(37, 58.5, "Olist DWH — Entity Relationship Diagram",
            ha="center", va="center",
            fontsize=18, fontweight="bold", color="#2C3E50")
    ax.text(37, 57.3,
            "Star Schema  |  PostgreSQL  |  dwh schema",
            ha="center", va="center",
            fontsize=10, color="#7F8C8D")

    # legend
    for lx, lc, lt in [(2, C_FACT_HEADER, "Fact Table"),
                        (12, C_DIM_HEADER,  "Dimension Table")]:
        ax.add_patch(plt.Rectangle((lx, 56.5), 1.5, 0.9,
                                   color=lc, zorder=3))
        ax.text(lx + 1.8, 56.95, lt, va="center",
                fontsize=9, color="#2C3E50", zorder=4)

    # draw tables
    all_anchors = {}
    for name, table in TABLES.items():
        x, y = POSITIONS[name]
        all_anchors[name] = draw_table(ax, name, table, x, y)

    # draw relationship arrows
    draw_relationships(ax, all_anchors)

    # save
    out_path = Path(__file__).parent / "doc" / "ERD_DWH.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(pad=0.5)
    plt.savefig(out_path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("ERD saved -> " + str(out_path))


if __name__ == "__main__":
    main()
