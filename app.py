import streamlit as st
import pandas as pd
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Analisis Transportasi Terminal DKI Jakarta",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM ENTERPRISE CSS STYLING ---
st.markdown("""
    <style>
    .main {
        background-color: #F8FAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
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
        <div class="header-title">Analisis Pergerakan Penumpang & Efisiensi Operasional Bus</div>
        <div class="header-subtitle">Optimasi Efisiensi Operasional Bus Perkotaan DKI Jakarta</div>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR FILTER ---
st.sidebar.markdown("### Panel Kontrol")
terminal_list = ["Seluruh Terminal"] + sorted(list(df['terminal'].dropna().unique()))
selected_terminal = st.sidebar.selectbox("Pilih Terminal:", terminal_list)

if selected_terminal != "Seluruh Terminal":
    filtered_df = df[df['terminal'] == selected_terminal]
    is_filtered = True
else:
    filtered_df = df.copy()
    is_filtered = False

# --- INDIKATOR UTAMA VOLUME TRANSPORTASI ---
col1, col2, col3, col4, col5 = st.columns(5)

total_pnp_berangkat = filtered_df['jumlah_penumpang_berangkat'].sum()
total_pnp_datang = filtered_df['jumlah_penumpang_datang'].sum()
net_flow = total_pnp_berangkat - total_pnp_datang
total_bus_berangkat = filtered_df['jumlah_bus_berangkat'].sum()
avg_load_factor = total_pnp_berangkat / total_bus_berangkat if total_bus_berangkat > 0 else 0

col1.metric("Total Penumpang Berangkat", f"{total_pnp_berangkat:,.0f}")
col2.metric("Total Penumpang Datang", f"{total_pnp_datang:,.0f}")
col3.metric("Selisih Neto Arus", f"{net_flow:+,.0f}")
col4.metric("Total Pergerakan Bus", f"{total_bus_berangkat:,.0f}")
col5.metric("Rata-Rata Beban/Bus", f"{avg_load_factor:.2f} pnp/bus")

st.markdown("<br>", unsafe_allow_html=True)

# --- STRUCTURED TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Peran & Arus Terminal", 
    "2. Kepadatan & Ketimpangan Bus", 
    "3. Tren Bulanan & Pareto 70/30", 
    "4. Simulasi Relokasi Bus"
])

# ==========================================
# TAB 1: PERAN & ARUS TERMINAL
# ==========================================
with tab1:
    st.subheader("Analisis Selisih Arus Penumpang")
    st.caption("Perhitungan selisih penumpang memisahkan terminal yang lebih banyak memberangkatkan penumpang vs terminal tempat kedatangan.")
    
    hub_summary = df.groupby('terminal').agg({
        'jumlah_penumpang_datang': 'sum',
        'jumlah_penumpang_berangkat': 'sum'
    }).reset_index()
    
    hub_summary['net_flow'] = hub_summary['jumlah_penumpang_berangkat'] - hub_summary['jumlah_penumpang_datang']
    
    transit_df = hub_summary[hub_summary['net_flow'] >= 0].sort_values(by='net_flow', ascending=False)
    gateway_df = hub_summary[hub_summary['net_flow'] < 0].sort_values(by='net_flow', ascending=True)
    gateway_df['net_flow_abs'] = gateway_df['net_flow'].abs()
    
    if is_filtered:
        transit_df['color'] = transit_df['terminal'].apply(lambda x: '#2563EB' if x == selected_terminal else '#CBD5E1')
        gateway_df['color'] = gateway_df['terminal'].apply(lambda x: '#E11D48' if x == selected_terminal else '#CBD5E1')
    else:
        transit_df['color'] = '#0284C7'
        gateway_df['color'] = '#E11D48'
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown("##### 🟦 Terminal Keberangkatan Utama (Lebih Banyak Berangkat)")
        fig_transit = px.bar(
            transit_df,
            x='terminal',
            y='net_flow',
            text_auto='.2s',
            color='color',
            color_discrete_map="identity",
            labels={'terminal': 'Nama Terminal', 'net_flow': 'Selisih Penumpang (Berangkat - Datang)'},
            title="Keberangkatan Lebih Dominan"
        )
        fig_transit.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig_transit, use_container_width=True)
        
    with col_t2:
        st.markdown("##### 🟥 Terminal Kedatangan Utama (Lebih Banyak Datang)")
        fig_gateway = px.bar(
            gateway_df,
            x='terminal',
            y='net_flow_abs',
            text_auto='.2s',
            color='color',
            color_discrete_map="identity",
            labels={'terminal': 'Nama Terminal', 'net_flow_abs': 'Selisih Penumpang (Datang - Berangkat)'},
            title="Kedatangan Lebih Dominan"
        )
        fig_gateway.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig_gateway, use_container_width=True)

# ==========================================
# TAB 2: KEPADATAN & KETIMPANGAN BUS
# ==========================================
with tab2:
    st.subheader("Evaluasi Kepadatan Penumpang per Bus")
    st.caption("Membandingkan jumlah penumpang per bus di setiap terminal untuk melihat terminal yang terlalu padat vs terminal yang sepi.")
    
    # Opsi slider di Tab 2
    target_capacity = st.slider(
        "Tentukan Target Penumpang Ideal per Bus:", 
        min_value=20, 
        max_value=60, 
        value=40,
        step=5,
        key="slider_tab2"
    )
    
    mismatch_summary = df.groupby('terminal').agg({
        'jumlah_penumpang_berangkat': 'sum',
        'jumlah_bus_berangkat': 'sum'
    }).reset_index()
    
    mismatch_summary['load_factor'] = (mismatch_summary['jumlah_penumpang_berangkat'] / mismatch_summary['jumlah_bus_berangkat']).round(1)
    mismatch_summary_sorted = mismatch_summary.sort_values(by='load_factor', ascending=False)
    
    if is_filtered:
        mismatch_summary_sorted['color'] = mismatch_summary_sorted['terminal'].apply(
            lambda x: '#DC2626' if x == selected_terminal else '#CBD5E1'
        )
        fig_bar_mismatch = px.bar(
            mismatch_summary_sorted,
            x='terminal',
            y='load_factor',
            color='color',
            color_discrete_map="identity",
            text='load_factor',
            labels={'terminal': 'Nama Terminal', 'load_factor': 'Rata-rata Penumpang / Bus'},
            title=f"Beban Penumpang per Bus di {selected_terminal} Dibanding Terminal Lain"
        )
    else:
        fig_bar_mismatch = px.bar(
            mismatch_summary_sorted,
            x='terminal',
            y='load_factor',
            color='load_factor',
            color_continuous_scale='Reds',
            text='load_factor',
            labels={'terminal': 'Nama Terminal', 'load_factor': 'Rata-rata Penumpang / Bus'},
            title=f"Rata-Rata Penumpang per Bus (Target Ideal = {target_capacity} Penumpang/Bus)"
        )
        
    fig_bar_mismatch.add_hline(
        y=target_capacity, 
        line_dash="dash", 
        line_color="#16A34A", 
        annotation_text=f"Target Ideal ({target_capacity} pnp/bus)"
    )
    fig_bar_mismatch.update_layout(template="plotly_white")
    st.plotly_chart(fig_bar_mismatch, use_container_width=True)

# ==========================================
# TAB 3: TREN BULANAN & PARETO 70/30
# ==========================================
with tab3:
    col_left, col_right = st.columns([6, 4])
    
    with col_left:
        st.subheader("Tren Fluktuasi Penumpang Bulanan (2024 - 2026)")
        monthly_trend = filtered_df.groupby(filtered_df['tanggal_lengkap'].dt.to_period('M')).agg({
            'jumlah_penumpang_berangkat': 'sum'
        }).reset_index()
        monthly_trend['tanggal_lengkap'] = monthly_trend['tanggal_lengkap'].dt.to_timestamp()
        
        fig_line = px.line(
            monthly_trend, 
            x='tanggal_lengkap', 
            y='jumlah_penumpang_berangkat', 
            markers=True,
            title=f"Pergerakan Penumpang Bulanan ({selected_terminal})"
        )
        fig_line.update_layout(template="plotly_white")
        st.plotly_chart(fig_line, use_container_width=True)
        
    with col_right:
        st.subheader("Prinsip Pareto 70/30 (Pusat Penumpukan)")
        
        pareto_df = df.groupby('terminal')['jumlah_penumpang_berangkat'].sum().reset_index()
        total_p = pareto_df['jumlah_penumpang_berangkat'].sum()
        pareto_df['kontribusi'] = (pareto_df['jumlah_penumpang_berangkat'] / total_p) * 100
        pareto_df = pareto_df.sort_values(by='kontribusi', ascending=False)
        
        top3 = pareto_df.head(3)['kontribusi'].sum()
        other = 100 - top3
        
        fig_pie = px.pie(
            values=[top3, other],
            names=['3 Terminal Teratas (Cililitan, Manggarai, Blok M)', '14 Terminal Lainnya'],
            title=f"3 Terminal Teratas Menyumbang {top3:.2f}% Penumpang",
            color_discrete_sequence=['#0F172A', '#94A3B8']
        )
        fig_pie.update_layout(template="plotly_white")
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Penambahan keterangan konteks makro saat mode filter aktif
        if is_filtered:
            st.caption(f"ℹ️ **Catatan Makro:** Grafik persentase di atas menampilkan proporsi konsentrasi penumpang skala provinsi DKI Jakarta (Top 3 Terminal vs Lainnya).")

# ==========================================
# TAB 4: SIMULASI RELOKASI BUS
# ==========================================
with tab4:
    st.subheader("Simulasi Alokasi Bus Ideal")
    
    # Opsi slider di Tab 4
    target_capacity_tab4 = st.slider(
        "Tentukan Target Penumpang Ideal per Bus:", 
        min_value=20, 
        max_value=60, 
        value=40,
        step=5,
        key="slider_tab4"
    )
    
    sim_df = df.groupby('terminal').agg({
        'jumlah_penumpang_berangkat': 'mean',
        'jumlah_bus_berangkat': 'mean'
    }).reset_index()
    
    sim_df.columns = ['Terminal', 'Rata_Pnp_Harian', 'Trips_Eksisting_Harian']
    sim_df['Rata_Pnp_Harian'] = sim_df['Rata_Pnp_Harian'].round(0)
    sim_df['Trips_Eksisting_Harian'] = sim_df['Trips_Eksisting_Harian'].round(0)
    sim_df['Trips_Ideal_Harian'] = (sim_df['Rata_Pnp_Harian'] / target_capacity_tab4).round(0)
    sim_df['Selisih_Trips_Harian'] = sim_df['Trips_Eksisting_Harian'] - sim_df['Trips_Ideal_Harian']
    sim_df['Status_Alokasi'] = sim_df['Selisih_Trips_Harian'].apply(lambda x: 'SURPLUS' if x >= 0 else 'DEFISIT')
    
    sim_df_sorted = sim_df.sort_values(by='Selisih_Trips_Harian')
    
    # --- INSIGHT DINAMIS BERDASARKAN FILTER TERMINAL ---
    if is_filtered:
        t_data = sim_df[sim_df['Terminal'] == selected_terminal].iloc[0]
        pnp = t_data['Rata_Pnp_Harian']
        exist_trips = t_data['Trips_Eksisting_Harian']
        ideal_trips = t_data['Trips_Ideal_Harian']
        diff = t_data['Selisih_Trips_Harian']
        status = t_data['Status_Alokasi']
        
        if status == 'DEFISIT':
            st.error(f"""
            📌 **Analisis Kebutuhan Bus - {selected_terminal}:**  
            Terminal ini melayani rata-rata **{pnp:,.0f} penumpang/hari** dengan **{exist_trips:,.0f} keberangkatan bus/hari** (Rata-rata saat ini: **{pnp/exist_trips:.1f} penumpang/bus**).  
            Dengan target **{target_capacity_tab4} penumpang/bus**, terminal ini mengalami **KEKURANGAN (DEFISIT) {abs(diff):,.0f} BUS/HARI**.
            """)
        else:
            st.success(f"""
            📌 **Analisis Kebutuhan Bus - {selected_terminal}:**  
            Terminal ini melayani rata-rata **{pnp:,.0f} penumpang/hari** dengan **{exist_trips:,.0f} keberangkatan bus/hari** (Rata-rata saat ini: **{pnp/exist_trips:.1f} penumpang/bus**).  
            Dengan target **{target_capacity_tab4} penumpang/bus**, terminal ini memiliki **KELEBIHAN (SURPLUS) {diff:,.0f} BUS/HARI** yang bisa dialihkan ke terminal lain.
            """)
    else:
        defisits = sim_df[sim_df['Status_Alokasi'] == 'DEFISIT']['Terminal'].tolist()
        surpluses = sim_df[sim_df['Status_Alokasi'] == 'SURPLUS']['Terminal'].tolist()
        st.info(f"""
        📌 **Ringkasan Alokasi Bus Se-Jakarta (Target: {target_capacity_tab4} penumpang/bus):**  
        • **Terminal Kekurangan Bus (Defisit):** {', '.join(defisits)}  
        • **Terminal Kelebihan Bus (Surplus):** {len(surpluses)} terminal lain memiliki armada berlebih yang bisa dialihkan secara efisien.
        """)
        
    st.dataframe(
        sim_df_sorted,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rata_Pnp_Harian": st.column_config.NumberColumn("Rata-Rata Penumpang/Hari", format="%,.0f"),
            "Trips_Eksisting_Harian": st.column_config.NumberColumn("Jumlah Bus Saat Ini/Hari", format="%,.0f"),
            "Trips_Ideal_Harian": st.column_config.NumberColumn("Kebutuhan Bus Ideal/Hari", format="%,.0f"),
            "Selisih_Trips_Harian": st.column_config.NumberColumn("Status Alokasi (Kelebihan/Kekurangan)", format="%+,.0f")
        }
    )
