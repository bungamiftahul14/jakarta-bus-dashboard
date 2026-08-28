import streamlit as st
import pandas as pd
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="DKI Jakarta Public Bus Efficiency Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM ENTERPRISE CSS STYLING ---
st.markdown("""
    <style>
    /* Background Utama */
    .main {
        background-color: #F8FAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Container Eksekutif */
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

    /* Callout Card Insight */
    .insight-card {
        background-color: #EFF6FF;
        border-left: 4px solid #2563EB;
        padding: 16px 20px;
        border-radius: 4px;
        margin-bottom: 20px;
        color: #1E40AF;
        font-size: 13px;
        line-height: 1.6;
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
    
    /* Menyembunyikan Footer Bawaan Streamlit */
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

# --- INSIGHTS RINGKASAN EKSEKUTIF ---
st.markdown("""
    <div class="insight-card">
        <strong>📌 Key Operational Findings:</strong><br>
        • <strong>Konsentrasi Beban (Pareto 70/30):</strong> Sebanyak <strong>71.30%</strong> total penumpang se-DKI Jakarta terpusat hanya pada 3 terminal utama (Cililitan, Manggarai, dan Blok M).<br>
        • <strong>Pemborosan Kapasitas Operasional:</strong> 5 terminal <em>underutilized</em> (Klender, Grogol, Pasar Minggu, Pinang Ranti, Rawamangun) mencatatkan total <strong>548.090 trip bus</strong> dengan rerata &lt; 3 pnp/trip (membuang &gt;92% kapasitas armada).<br>
        • <strong>Volatilitas Musiman:</strong> Mobilitas Kuartal II melonjak hingga <strong>600% (6x lipat)</strong> dibanding awal Ramadan, memerlukan skema <em>Dynamic Dispatching</em>.
    </div>
""", unsafe_allow_html=True)

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
    
    # Memisahkan Transit Hub (+ Net) dan Gateway Hub (- Net)
    transit_df = hub_summary[hub_summary['net_flow'] > 0].sort_values(by='net_flow', ascending=False)
    gateway_df = hub_summary[hub_summary['net_flow'] < 0].sort_values(by='net_flow', ascending=True)
    gateway_df['net_flow_abs'] = gateway_df['net_flow'].abs()  # Buat positif untuk visualisasi
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown("##### 🟦 Transit Hubs (Dominan Keberangkatan / Komuter)")
        fig_transit = px.bar(
            transit_df,
            x='terminal',
            y='net_flow',
            text_auto='.2s',
            labels={'terminal': 'Terminal', 'net_flow': 'Surplus Keberangkatan'},
            title="Net Flow Positif (Penumpang Berangkat > Datang)"
        )
        fig_transit.update_traces(marker_color='#0284C7')
        fig_transit.update_layout(template="plotly_white")
        st.plotly_chart(fig_transit, use_container_width=True)
        
    with col_t2:
        st.markdown("##### 🟥 Gateway Hubs (Dominan Kedatangan / Luar Kota)")
        fig_gateway = px.bar(
            gateway_df,
            x='terminal',
            y='net_flow_abs',
            text_auto='.2s',
            labels={'terminal': 'Terminal', 'net_flow_abs': 'Surplus Kedatangan'},
            title="Net Flow Negatif (Penumpang Datang > Berangkat)"
        )
        fig_gateway.update_traces(marker_color='#E11D48')
        fig_gateway.update_layout(template="plotly_white")
        st.plotly_chart(fig_gateway, use_container_width=True)

    st.markdown("""
    **Kesimpulan Peran Terminal:**
    * **Transit Hubs (Manggarai, Cililitan, Blok M):** Berfungsi sebagai titik kumpul komuter harian menuju tempat kerja/aktivitas bisnis[cite: 3].
    * **Gateway Hubs (Kampung Rambutan, Rawamangun):** Berfungsi sebagai gerbang masuk utama yang menyerap arus kedatangan penumpang dari luar daerah DKI Jakarta[cite: 3].
    """)

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
    
    fig_bar_mismatch = px.bar(
        mismatch_summary_sorted,
        x='terminal',
        y='load_factor',
        color='load_factor',
        color_continuous_scale='Reds',
        text='load_factor',
        labels={'terminal': 'Nama Terminal', 'load_factor': 'Load Factor (Penumpang / Trip Bus)'},
        title="Peringkat Keterisian Bus per Terminal (Batas Standar Ideal = 40 Pnp/Trip)"
    )
    fig_bar_mismatch.add_hline(y=40, line_dash="dash", line_color="#16A34A", annotation_text="Target Ideal (40 pnp/trip)")
    fig_bar_mismatch.update_layout(template="plotly_white")
    st.plotly_chart(fig_bar_mismatch, use_container_width=True)
    
    st.markdown("""
    **Detail Anomali Operasional:**
    * **Critical Crisis (Manggarai):** Menampung beban ekstrem **276.7 pnp/trip** (7x lipat batas ideal) akibat keterbatasan alokasi bus (frekuensi bus di peringkat #16 padahal volume penumpang peringkat #2)[cite: 3].
    * **Underutilized / High Waste (Klender, Pasar Minggu, Grogol):** Melayani < 3 penumpang per perjalanan bus, menyebabkan pemborosan BBM dan sumber daya yang siap dialihkan[cite: 3].
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
            title=f"Konsentrasi Beban: Top 3 Menyumbang {top3:.2f}% Penumpang",
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
    ### 📌 Rekomendasi Kebijakan Strategis
    1. **Relokasi Operasional Lintas Terminal:** Mengalokasikan 138 trip surplus dari Blok M serta menyerap alokasi perjalanan dari terminal sepi (Klender & Pasar Minggu) ke Manggarai (+216 trip) dan Cililitan (+231 trip) tanpa perlu pengadaan armada baru[cite: 3].
    2. **Feeder Route Optimization:** Menata ulang rute bus feeder dari Gateway Hub (Kampung Rambutan) langsung ke Transit Hub (Manggarai & Cililitan)[cite: 3].
    3. **Surge Buffer Planning:** Menyiapkan protokol operasional cadangan khusus Kuartal II (April/Mei) untuk meredam lonjakan komuter[cite: 3].
    4. **Maintenance Scheduling:** Memanfaatkan penurunan volume harian di akhir pekan (~20.9%) untuk perawatan armada berkala[cite: 3].
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

csv_data = report_summary.to_csv(index=False).encode('utf-8')

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
