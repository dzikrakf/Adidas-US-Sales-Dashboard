
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =========================
# KONFIGURASI DASHBOARD
# =========================
st.set_page_config(
    page_title="Adidas US Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================
# TEMA DASHBOARD
# =========================
st.markdown("""
<style>
    /* Background halaman utama */
    .stApp {
        background-color: #F5F5F5;
        color: #171717;
    }

    /* Sidebar abu-abu terang */
    [data-testid="stSidebar"] {
        background-color: #E5E5E5 !important;
    }

    /* Semua teks sidebar hitam */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] span {
        color: #171717 !important;
    }

/* Memperbesar tulisan di sidebar dan filter */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    font-size: 15px !important;
}

/* Judul dan subjudul sidebar */
[data-testid="stSidebar"] h1 {
    font-size: 26px !important;
}

[data-testid="stSidebar"] h2 {
    font-size: 21px !important;
}

[data-testid="stSidebar"] h3 {
    font-size: 18px !important;
}


    /* Kotak pilihan tahun dan wilayah */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #BDBDBD !important;
    }

    /* Ikon dropdown dan clear filter */
    [data-testid="stSidebar"] div[data-baseweb="select"] svg {
        color: #171717 !important;
        fill: #171717 !important;
    }

    /* KPI */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #D9D9D9;
        border-top: 3px solid #171717;
        padding: 16px;
        border-radius: 6px;
    }

    /* Kotak insight */
    .insight-card {
        background-color: #FFFFFF;
        padding: 22px;
        border: 1px solid #D9D9D9;
        border-left: 5px solid #171717;
        border-radius: 6px;
        min-height: 145px;
    }

    .insight-label {
        color: #555555;
        font-size: 14px;
        font-weight: 600;
    }

    .insight-name {
        color: #171717;
        font-size: 23px;
        font-weight: 700;
        margin-top: 12px;
    }

    .insight-value {
        color: #171717;
        font-size: 19px;
        margin-top: 8px;
    }

    /* Tombol */
    .stButton > button,
    .stDownloadButton > button {
        background-color: #171717;
        color: #FFFFFF;
        border: 1px solid #171717;
        border-radius: 5px;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background-color: #444444;
        color: #FFFFFF;
        border-color: #444444;
    }

    /* Judul halaman */
    h1, h2, h3 {
        color: #171717;
    }

    hr {
        border-color: #D0D0D0;
    }
</style>
""", unsafe_allow_html=True)


# =========================
# MEMBACA DATASET
# =========================
folder = Path(__file__).parent
file_path = folder / "Dataset_adidas.xlsx"

if not file_path.exists():
    st.error(
        "File Dataset_adidas.xlsx tidak ditemukan. "
        "Pastikan file berada di folder yang sama dengan app.py."
    )
    st.stop()

df = pd.read_excel(file_path)
df.columns = df.columns.str.strip()


# =========================
# DATA CLEANING
# =========================

# Membersihkan spasi pada data teks
for col in df.select_dtypes(include=["object", "string"]).columns:
    df[col] = df[col].apply(
        lambda x: x.strip() if isinstance(x, str) else x
    )
    df[col] = df[col].replace("", pd.NA)

# Mengubah format tanggal
df["invoice_date"] = pd.to_datetime(
    df["invoice_date"], errors="coerce"
)

# Mengubah kolom numerik
numeric_cols = [
    "price_per_unit",
    "units_sold",
    "total_sales",
    "operating_profit",
    "operating_margin"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Menghapus data duplikat
df = df.drop_duplicates().copy()

# Menghapus data penting yang kosong
required_cols = [
    "invoice_date",
    "region",
    "product",
    "sales_method",
    "total_sales",
    "operating_profit",
    "units_sold"
]

df = df.dropna(subset=required_cols).copy()

# Menghapus nilai negatif pada penjualan dan unit
df = df[
    (df["total_sales"] >= 0) &
    (df["units_sold"] >= 0)
].copy()

# Membuat kolom tahun dan bulan
df["Year"] = df["invoice_date"].dt.year
df["Month"] = df["invoice_date"].dt.month
df["Month_Name"] = df["invoice_date"].dt.strftime("%b")



# =========================
# FILTER SIDEBAR
# =========================
st.sidebar.title("ADIDAS")
st.sidebar.subheader("SALES FILTER")
st.sidebar.caption("Pilih tahun dan wilayah.")

years = sorted(df["Year"].dropna().unique().tolist())
regions = sorted(df["region"].dropna().unique().tolist())

# Dropdown tahun
selected_year = st.sidebar.selectbox(
    "Tahun",
    options=["Semua Tahun"] + years,
    index=0,
    format_func=lambda x: str(x)
)

# Dropdown wilayah
selected_region = st.sidebar.selectbox(
    "Wilayah",
    options=["Semua Wilayah"] + regions,
    index=0
)

# Terapkan filter
filtered_df = df.copy()

if selected_year != "Semua Tahun":
    filtered_df = filtered_df[
        filtered_df["Year"] == selected_year
    ]

if selected_region != "Semua Wilayah":
    filtered_df = filtered_df[
        filtered_df["region"] == selected_region
    ]

if filtered_df.empty:
    st.title("ADIDAS US SALES DASHBOARD")
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()


# =========================
# JUDUL DASHBOARD
# =========================
st.title("ADIDAS US SALES DASHBOARD")
st.markdown("---")


# =========================
# INSIGHT PENJUALAN
# =========================
st.subheader("Insight Penjualan")

total_produk = (
    filtered_df.groupby("product")["total_sales"]
    .sum()
    .sort_values(ascending=False)
)

total_wilayah = (
    filtered_df.groupby("region")["total_sales"]
    .sum()
    .sort_values(ascending=False)
)

col_insight1, col_insight2 = st.columns(2)

with col_insight1:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-label">
                PRODUK DENGAN OMZET TERTINGGI
            </div>
            <div class="insight-name">
                {total_produk.index[0]}
            </div>
            <div class="insight-value">
                ${total_produk.iloc[0]:,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_insight2:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-label">
                WILAYAH DENGAN OMZET TERTINGGI
            </div>
            <div class="insight-name">
                {total_wilayah.index[0]}
            </div>
            <div class="insight-value">
                ${total_wilayah.iloc[0]:,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")


# =========================
# GAMBARAN UMUM PENJUALAN
# =========================
st.header("Gambaran Umum Penjualan")

total_sales = filtered_df["total_sales"].sum()
total_profit = filtered_df["operating_profit"].sum()
total_units = filtered_df["units_sold"].sum()

kpi1, kpi2, kpi3 = st.columns(3)

kpi1.metric("TOTAL SALES", f"${total_sales:,.0f}")
kpi2.metric("OPERATING PROFIT", f"${total_profit:,.0f}")
kpi3.metric("UNITS SOLD", f"{total_units:,.0f}")

st.caption(f"Jumlah transaksi dalam data: {len(filtered_df):,} baris")
st.markdown("---")


# =========================
# ANALISIS PENJUALAN
# =========================
st.header("Analisis Penjualan")


# 1. Tren penjualan bulanan
st.subheader("01 | Tren Penjualan Bulanan")

monthly_sales = (
    filtered_df.groupby(
        ["Year", "Month", "Month_Name"], as_index=False
    )["total_sales"]
    .sum()
    .sort_values(["Year", "Month"])
)

monthly_sales["Periode"] = (
    monthly_sales["Month_Name"] + " " +
    monthly_sales["Year"].astype(str)
)

fig1 = px.line(
    monthly_sales,
    x="Periode",
    y="total_sales",
    markers=True,
    labels={
        "Periode": "Bulan",
        "total_sales": "Total Sales ($)"
    }
)

fig1.update_traces(
    line=dict(color="#171717", width=3),
    marker=dict(color="#171717", size=7)
)

fig1.update_layout(
    template="plotly_white",
    height=380,
    margin=dict(l=20, r=20, t=25, b=20),
    xaxis_tickangle=-45
)

st.plotly_chart(fig1, use_container_width=True)


# 2. Penjualan per produk
st.subheader("02 | Penjualan per Produk")

product_sales = (
    filtered_df.groupby("product", as_index=False)["total_sales"]
    .sum()
    .sort_values("total_sales", ascending=True)
)

fig2 = px.bar(
    product_sales,
    x="total_sales",
    y="product",
    orientation="h",
    labels={
        "product": "Produk",
        "total_sales": "Total Sales ($)"
    }
)

fig2.update_traces(marker_color="#171717")

fig2.update_layout(
    template="plotly_white",
    height=400,
    margin=dict(l=20, r=20, t=25, b=20)
)

st.plotly_chart(fig2, use_container_width=True)


# 3. Kontribusi metode penjualan
st.subheader("03 | Kontribusi Metode Penjualan")

method_sales = (
    filtered_df.groupby("sales_method", as_index=False)["total_sales"]
    .sum()
)

fig3 = px.pie(
    method_sales,
    names="sales_method",
    values="total_sales",
    hole=0.4,
    color_discrete_sequence=[
        "#171717", "#777777", "#C9C9C9"
    ]
)

fig3.update_layout(
    template="plotly_white",
    height=380,
    margin=dict(l=20, r=20, t=25, b=20)
)

st.plotly_chart(fig3, use_container_width=True)


# 4. Hubungan unit terjual dan laba
st.subheader("04 | Hubungan Unit Terjual dan Laba")

scatter_df = filtered_df[
    ["units_sold", "operating_profit", "sales_method"]
].dropna().copy()

# Membatasi titik agar grafik tetap responsif
if len(scatter_df) > 2000:
    scatter_df = scatter_df.sample(
        n=2000,
        random_state=42
    )

fig4 = px.scatter(
    scatter_df,
    x="units_sold",
    y="operating_profit",
    color="sales_method",
    labels={
        "units_sold": "Units Sold",
        "operating_profit": "Operating Profit ($)",
        "sales_method": "Sales Method"
    },
    color_discrete_sequence=[
        "#171717", "#777777", "#BDBDBD"
    ],
    render_mode="webgl"
)

fig4.update_layout(
    template="plotly_white",
    height=420,
    margin=dict(l=20, r=20, t=25, b=20)
)

st.plotly_chart(
    fig4,
    use_container_width=True,
    config={"responsive": True}
)

st.markdown("---")


# =========================
# PREVIEW DATASET
# =========================
st.header("Preview Dataset")

st.caption(
    f"Menampilkan maksimal 100 baris pertama "
    f"dari {len(filtered_df):,} baris sesuai filter."
)

st.dataframe(
    filtered_df.head(100),
    use_container_width=True,
    hide_index=True
)

# Unduh dataset hasil cleaning sesuai filter
csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="Unduh Dataset",
    data=csv_data,
    file_name="Dataset_adidas.csv",
    mime="text/csv"
)
