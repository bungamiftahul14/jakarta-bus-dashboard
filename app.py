import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman Dashboard
st.set_page_config(
    page_title="Jakarta Bus Efficiency Dashboard",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Jakarta Public Transport: Bus Allocation & Load Factor Dashboard")
st.markdown("Analisis Pergerakan Penumpang & Efisiensi Operasional Bus Terminal DKI Jakarta")

# Membaca data CSV dari repository
@st.cache_data
def load_data():
    df = pd.read_csv("db_transportasi_dki.csv")
    
    # 1. Menangani missing value pada penumpang datang
    df['jumlah_penumpang_datang'] = df['jumlah_penumpang_datang'].fillna(0)
    
    # 2. Membuat kolom tanggal lengkap (YYYY-MM-DD) dari periode_data + tanggal
    df['tanggal_lengkap'] = pd.to_datetime(
        df['periode_data'].astype(str) + df['tanggal'].astype(str).str.zfill(2),
        format='%Y%m%d'
    )
    return df

df = load_data()

# --- SIDEBAR FILTER ---
st.sidebar.header("Filter Analisis")
terminal_list = ["Semua Terminal"] + sorted(list(df['terminal'].dropna().unique()))
selected_terminal = st.sidebar.selectbox("Pilih Terminal", terminal_list)

if selected_terminal != "Semua Terminal":
    filtered_df = df[df['terminal'] == selected_terminal]
else:
    filtered_df = df.copy()

# --- KPI METRICS (AKUMULASI MAKRO) ---
col1, col2, col3, col4 = st.columns(4)
total_pnp_berangkat = filtered_df['jumlah_penumpang_berangkat'].sum()
total_pnp_datang = filtered_df['jumlah_penumpang_datang'].sum()
total_bus_berangkat = filtered_df['jumlah_bus_berangkat'].sum()
avg_load_factor = total_pnp_berangkat / total_bus_berangkat if total_bus_berangkat > 0 else 0

col1.metric("Total Penumpang Berangkat", f"{total_pnp_berangkat:,.0f}")
col2.metric("Total Penumpang Datang", f"{total_pnp_datang:,.0f}")
col3.metric("Total Trip Bus Berangkat", f"{total_bus_berangkat:,.0f}")
col4.metric("Rata-Rata Load Factor", f"{avg_load_factor:.2f} pnp/bus")

st.divider()

# --- TABS DASHBOARD ---
tab1, tab2, tab3 = st.tabs(["⚠️ Supply-Demand Mismatch", "📈 Tren & Pareto 70/30", "🧮 Dynamic Bus Simulator"])

with tab1:
    st.subheader("Anomali Load Factor per Terminal")
    
    terminal_summary = df.groupby('terminal').agg({
        'jumlah_penumpang_berangkat': 'sum',
        'jumlah_bus_berangkat': 'sum'
    }).reset_index()
    
    terminal_summary['load_factor'] = terminal_summary['jumlah_penumpang_berangkat'] / terminal_summary['jumlah_bus_berangkat']
    terminal_summary = terminal_summary.sort_values(by='load_factor', ascending=False)
    
    fig_bar = px.bar(
        terminal_summary, 
        x='terminal', 
        y='load_factor',
        color='load_factor',
        color_continuous_scale='Reds',
        labels={'terminal': 'Terminal', 'load_factor': 'Penumpang / Trip Bus'},
        title="Load Factor Keterisian Bus per Terminal (Batas Ideal = 40)"
    )
    fig_bar.add_hline(y=40, line_dash="dash", line_color="green", annotation_text="Kapasitas Ideal (40 pnp/bus)")
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.subheader("Tren Fluktuasi Penumpang Bulanan")
    monthly_trend = filtered_df.groupby(filtered_df['tanggal_lengkap'].dt.to_period('M')).agg({
        'jumlah_penumpang_berangkat': 'sum'
    }).reset_index()
    monthly_trend['tanggal_lengkap'] = monthly_trend['tanggal_lengkap'].dt.to_timestamp()
    
    fig_line = px.line(
        monthly_trend, 
        x='tanggal_lengkap', 
        y='jumlah_penumpang_berangkat', 
        markers=True,
        title="Dinamika Arus Penumpang (2024 - 2026)"
    )
    st.plotly_chart(fig_line, use_container_width=True)

with tab3:
    st.subheader("Simulasi Alokasi Trip Ideal")
    target_capacity = st.slider("Tentukan Kapasitas Target per Bus (Penumpang/Trip):", min_value=20, max_value=60, value=40)
    
    sim_df = df.groupby('terminal').agg({
        'jumlah_penumpang_berangkat': 'mean',
        'jumlah_bus_berangkat': 'mean'
    }).reset_index()
    
    sim_df.columns = ['Terminal', 'Rata_Pnp_Harian', 'Trips_Eksisting']
    sim_df['Trips_Ideal'] = (sim_df['Rata_Pnp_Harian'] / target_capacity).round(0)
    sim_df['Selisih_Trips'] = sim_df['Trips_Eksisting'] - sim_df['Trips_Ideal']
    sim_df['Status'] = sim_df['Selisih_Trips'].apply(lambda x: 'SURPLUS' if x > 0 else 'DEFISIT')
    
    st.dataframe(sim_df.sort_values(by='Selisih_Trips'), use_container_width=True)
