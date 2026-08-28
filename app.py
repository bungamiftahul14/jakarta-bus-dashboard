import streamlit as st
import pandas as pd
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="DKI Jakarta Public Bus Efficiency Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INSTITUTIONAL ENTERPRISE CSS STYLING ---
st.markdown("""
    <style>
    /* Main Background & Font Styling */
    .main {
        background-color: #F8FAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Container */
    .header-container {
        background-color: #0F172A;
        padding: 24px 32px;
        border-radius: 8px;
        color: #FFFFFF;
        margin-bottom: 24px;
        border-left: 6px solid #2563EB;
    }
    .header-title {
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0;
        color: #F8FAFC;
    }
    .header-subtitle {
        font-size: 13px;
        color: #94A3B8;
        margin-top: 4px;
        margin-bottom: 0;
    }

    /* Metric Cards Styling */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 16px 20px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 12px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] {
        font-size: 22px;
        font-weight: 700;
        color: #0F172A;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre-wrap;
        background-color: #F1F5F9;
        border-radius: 6px 6px 0px 0px;
        color: #475569;
        font-size: 13px;
        font-weight: 600;
        padding: 0px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0F172A !important;
        color: #FFFFFF !important;
    }
    
    /* Hide Streamlit Default Footers & Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv("db_transportasi_dki.csv")
    df['jumlah_penumpang_datang'] = df['jumlah_penumpang_datang'].fillna(0)
    df['tanggal_lengkap'] = pd.to_datetime(
        df['periode_data'].astype(str) + df['tanggal'].astype(str).str.zfill(2),
        format='%Y%m%d'
    )
    return df

df = load_data()

# --- HEADER UTAMA ---
st.markdown("""
    <div class="header-container">
        <div class="header-title">DKI Jakarta Public Transportation Efficiency Dashboard</div>
        <div class="header-subtitle">Executive Load Factor Analysis & Operational Bus Redistribution Strategy</div>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR FILTER ---
st.sidebar.markdown("### Control Panel")
terminal_list = ["Seluruh Terminal"] + sorted(list(df['terminal'].dropna().unique()))
selected_terminal = st.sidebar.selectbox("Filter Scope Terminal:", terminal_list)

if selected_terminal != "Seluruh Terminal":
    filtered_df = df[df['terminal'] == selected_terminal]
else:
    filtered_df = df.copy()

# --- MACRO KPI CARDS ---
col1, col2, col3, col4, col5 = st.columns(5)

total_pnp_berangkat = filtered_df['jumlah_penumpang_berangkat'].sum()
total_pnp_datang = filtered_df['jumlah_penumpang_datang'].sum()
net_flow = total_pnp_berangkat - total_pnp_datang
total_bus_berangkat = filtered_df['jumlah_bus_berangkat'].sum()
avg_load_factor = total_pnp_berangkat / total_bus_berangkat if total_bus_berangkat > 0 else 0

col1.metric("Penumpang Berangkat", f"{total_pnp_berangkat:,.0f}")
col2.metric("Penumpang Datang", f"{total_pnp_datang:,.0f}")
col3.metric("Net Flow Volume", f"{net_flow:+,.0f}")
col4.metric("Total Trips Bus", f"{total_bus_berangkat:,.0f}")
col5.metric("Avg Load Factor", f"{avg_load_factor:.2f} pnp/trip")

st.markdown("<br>", unsafe_allow_html=True)

# --- STRUCTURED TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Executive Overview & Hub Roles", 
    "2. Supply-Demand Mismatch", 
    "3. Time Series & Pareto 70/30", 
    "4. Dynamic Bus Simulator & Action Plan"
])

# ==========================================
# TAB 1: EXECUTIVE OVERVIEW & HUB ROLES
# ==========================================
with tab1:
    st.subheader("Divergensikasi Arus & Klasifikasi Peran Terminal")
    st.caption("Perhitungan selisih neto memisahkan fungsi terminal antara Transit Hub (Komuter) dan Gateway Hub (Kedatangan Luar Kota).")
    
    hub_summary = df.groupby('terminal').agg({
        'jumlah_penumpang_datang': 'sum',
        'jumlah_penumpang_berangkat': 'sum'
    }).reset_index()
    
    hub_summary['net_flow'] = hub_summary['jumlah_penumpang_berangkat'] - hub_summary['jumlah_penumpang_datang']
    hub_summary['peran_terminal'] = hub_summary['net_flow'].apply(
        lambda x: 'Transit Hub (Net (+) Keberangkatan)' if x > 0 else 'Gateway Hub (Net (-) Kedatangan)'
    )
    hub_summary_sorted = hub_summary.sort_values(by='net_flow', ascending=False)
    
    fig_netflow = px.bar(
        hub_summary_sorted,
        x='terminal',
        y='net_flow',
        color='peran_terminal',
        color_discrete_map={
            'Transit Hub (Net (+) Keberangkatan)': '#0284C7',
            'Gateway Hub (Net (-) Kedatangan)': '#E11D48'
        },
        labels={'terminal': 'Terminal', 'net_flow': 'Selisih Neto Penumpang (Berangkat - Datang)'},
        title="Distribusi Peran Terminal Berdasarkan Net Flow Penumpang"
    )
    fig_netflow.update_layout(template="plotly_white")
    st.plotly_chart(fig_netflow, use_container_width=True)

# ==========================================
# TAB 2: SUPPLY-DEMAND MISMATCH
# ==========================================
with tab2:
    st.subheader("Krisis Alokasi Operasional: Overcrowded vs Underutilized")
    st.caption("Perbandingan keterisian muatan per perjalanan bus untuk mengisolasi terminal krisis.")
    
    mismatch_summary = df.groupby('terminal').agg({
        'jumlah_penumpang_berangkat': 'sum',
        'jumlah_bus_berangkat': 'sum'
    }).reset_index()
    
    mismatch_summary['load_factor'] = (mismatch_summary['jumlah_penumpang_berangkat'] / mismatch_summary['jumlah_bus_berangkat']).round(1)
    mismatch_summary_sorted = mismatch_summary.sort_values(by='load_factor', ascending=False)
    
    # Visualisasi Bar Chart Load Factor
    fig_bar_mismatch = px.bar(
        mismatch_summary_sorted,
        x='terminal',
        y='load_factor',
        color='load_factor',
        color_continuous_scale='Reds',
        text='load_factor',
        labels={'terminal': 'Nama Terminal', 'load_factor': 'Load Factor (Penumpang / Trip Bus)'},
        title="Peringkat Keterisian Bus per Terminal (Batas Standar Ideal = 40)"
    )
    fig_bar_mismatch.add_hline(y=40, line_dash="dash", line_color="#16A34A", annotation_text="Target Ideal (40 pnp/trip)")
    fig_bar_mismatch.update_layout(template="plotly_white")
    st.plotly_chart(fig_bar_mismatch, use_container_width=True)
    
    st.markdown("""
    **Temuan Anomali Operasional:**
    * **Overcrowded (Manggarai & Cililitan):** Manggarai mencatatkan keterisian ekstrem **276.7 pnp/trip** (7x lipat batas ideal) akibat minimnya frekuensi keberangkatan bus[cite: 2].
    * **Underutilized / Pemborosan (Klender, Pasar Minggu, Grogol):** Melayani < 5 penumpang/trip, membuktikan adanya pemborosan perjalanan bus yang bisa dialihkan[cite: 2].
    """)
    
# ==========================================
# TAB 3: TIME SERIES & PARETO
# ==========================================
with tab3:
    col_left, col_right = st.columns([6, 4])
    
    with col_left:
        st.subheader("Dinamika Volatilitas Waktu (2024 - 2026)")
        monthly_trend = filtered_df.groupby(filtered_df['tanggal_lengkap'].dt.to_period('M')).agg({
            'jumlah_penumpang_berangkat': 'sum'
        }).reset_index()
        monthly_trend['tanggal_lengkap'] = monthly_trend['tanggal_lengkap'].dt.to_timestamp()
        
        fig_line = px.line(
            monthly_trend, 
            x='tanggal_lengkap', 
            y='jumlah_penumpang_berangkat', 
            markers=True,
            title="Tren Musiman Penumpang Bulanan"
        )
        fig_line.update_layout(template="plotly_white")
        st.plotly_chart(fig_line, use_container_width=True)
        
    with col_right:
        st.subheader("Konsentrasi Beban (Prinsip Pareto 70/30)")
        pareto_df = df.groupby('terminal')['jumlah_penumpang_berangkat'].sum().reset_index()
        total_p = pareto_df['jumlah_penumpang_berangkat'].sum()
        pareto_df['kontribusi'] = (pareto_df['jumlah_penumpang_berangkat'] / total_p) * 100
        pareto_df = pareto_df.sort_values(by='kontribusi', ascending=False)
        
        top3 = pareto_df.head(3)['kontribusi'].sum()
        other = 100 - top3
        
        fig_pie = px.pie(
            values=[top3, other],
            names=['Top 3 Terminal (Cililitan, Manggarai, Blok M)', '14 Terminal Lainnya'],
            title=f"Konsentrasi Beban: Top 3 Menyumbang {top3:.2f}%",
            color_discrete_sequence=['#0F172A', '#94A3B8']
        )
        fig_pie.update_layout(template="plotly_white")
        st.plotly_chart(fig_pie, use_container_width=True)

# ==========================================
# TAB 4: DYNAMIC SIMULATOR & ACTION PLAN
# ==========================================
with tab4:
    st.subheader("Simulasi Relokasi Armada & Strategi Optimasi")
    
    target_capacity = st.slider("Target Kapasitas Ideal per Bus (Penumpang / Trip):", min_value=20, max_value=60, value=40)
    
    sim_df = df.groupby('terminal').agg({
        'jumlah_penumpang_berangkat': 'mean',
        'jumlah_bus_berangkat': 'mean'
    }).reset_index()
    
    sim_df.columns = ['Terminal', 'Rata_Pnp_Harian', 'Trips_Eksisting_Harian']
    sim_df['Rata_Pnp_Harian'] = sim_df['Rata_Pnp_Harian'].round(0)
    sim_df['Trips_Eksisting_Harian'] = sim_df['Trips_Eksisting_Harian'].round(0)
    sim_df['Trips_Ideal_Harian'] = (sim_df['Rata_Pnp_Harian'] / target_capacity).round(0)
    sim_df['Selisih_Trips_Harian'] = sim_df['Trips_Eksisting_Harian'] - sim_df['Trips_Ideal_Harian']
    sim_df['Status_Alokasi'] = sim_df['Selisih_Trips_Harian'].apply(lambda x: 'SURPLUS' if x >= 0 else 'DEFISIT')
    
    sim_df_sorted = sim_df.sort_values(by='Selisih_Trips_Harian')
    
    st.dataframe(
        sim_df_sorted,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rata_Pnp_Harian": st.column_config.NumberColumn("Rata-Rata Penumpang/Hari", format="%,.0f"),
            "Trips_Eksisting_Harian": st.column_config.NumberColumn("Trips Eksisting/Hari", format="%,.0f"),
            "Trips_Ideal_Harian": st.column_config.NumberColumn("Trips Ideal/Hari", format="%,.0f"),
            "Selisih_Trips_Harian": st.column_config.NumberColumn("Selisih Trips (Surplus/Defisit)", format="%+,.0f")
        }
    )
    
    st.markdown("""
    ---
    ### 📌 Rekomendasi Kebijakan Operasional
    1. **Relokasi Lintas Terminal:** Alihkan trip surplus dari Blok M serta penyerapan armada dari terminal sepi (Klender, Pasar Minggu) ke Manggarai & Cililitan tanpa perlu pengadaan unit baru[cite: 2].
    2. **Surge Buffer Planning:** Siapkan armada cadangan khusus Kuartal II (April/Mei) untuk menangani lonjakan puncak komuter/mudik[cite: 2].
    3. **Maintenance Schedule:** Manfaatkan penurunan volume harian di akhir pekan (~20.9%) untuk perawatan armada berkala[cite: 2].
    """)

# ==========================================
# EXPORT REPORT SECTION
# ==========================================
st.divider()
st.subheader("📄 Export Executive Report")
st.caption("Unduh ringkasan hasil analisis dan kalkulasi alokasi bus untuk kebutuhan dokumen formal.")

# Data Preparation for Export
report_summary = df.groupby('terminal').agg({
    'jumlah_penumpang_berangkat': 'sum',
    'jumlah_penumpang_datang': 'sum',
    'jumlah_bus_berangkat': 'sum',
    'jumlah_bus_datang': 'sum'
}).reset_index()

report_summary['net_flow'] = report_summary['jumlah_penumpang_berangkat'] - report_summary['jumlah_penumpang_datang']
report_summary['load_factor'] = (report_summary['jumlah_penumpang_berangkat'] / report_summary['jumlah_bus_berangkat']).round(2)

# Convert to CSV
csv_data = report_summary.to_csv(index=False).encode('utf-8')

# Generate Printable HTML Report
html_report = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; color: #0F172A; }}
        h1 {{ color: #0F172A; font-size: 20px; margin-bottom: 4px; }}
        p {{ color: #64748B; font-size: 12px; margin-top: 0; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 12px; }}
        th, td {{ border: 1px solid #CBD5E1; padding: 8px; text-align: left; }}
        th {{ background-color: #0F172A; color: white; }}
        tr:nth-child(even) {{ background-color: #F8FAFC; }}
    </style>
</head>
<body>
    <h1>DKI Jakarta Public Transportation - Summary Analysis Report</h1>
    <p>Generated automatically from Jakarta Bus Efficiency Dashboard</p>
    <hr>
    {report_summary.to_html(index=False, classes='table')}
</body>
</html>
"""

col_exp1, col_exp2 = st.columns([1, 4])
with col_exp1:
    st.download_button(
        label="📥 Download Summary CSV",
        data=csv_data,
        file_name="Jakarta_Bus_Efficiency_Summary.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_exp2:
    st.download_button(
        label="📄 Download Executive Report (HTML/PDF)",
        data=html_report,
        file_name="Jakarta_Bus_Efficiency_Report.html",
        mime="text/html",
        use_container_width=True
    )
