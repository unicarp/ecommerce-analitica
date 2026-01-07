import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.io as pio

# Definimos los colores
gold_palette = ['#D4AF37', '#F5F5F0', '#C0C0C0', '#B8860B', '#8A6642']

# 1. Configurar el tema base oscuro
pio.templates.default = "plotly_dark"

# 2. Forzar los colores en el layout y en los ciclos de color
pio.templates["plotly_dark"].layout.colorway = gold_palette
pio.templates["plotly_dark"].layout.paper_bgcolor = '#0E1117' # Fondo app
pio.templates["plotly_dark"].layout.plot_bgcolor = '#0E1117'  # Fondo gráfica

# 3. Actualizar la secuencia de colores discreta por defecto de PX
px.defaults.color_discrete_sequence = gold_palette

# ==========================================
# 1. CONFIGURACIÓN VISUAL
# ==========================================
st.set_page_config(
    page_title="Monitor de Estrategia Comercial",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para limpiar la interfaz
st.markdown("""
<style>
    /* Estilo para tarjetas de métricas */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* Textos oscuros para mejor lectura */
    [data-testid="stMetricLabel"] {color: #555 !important;}
    [data-testid="stMetricValue"] {color: #000 !important;}
    
    /* Encabezados amigables */
    h1, h2, h3 {
        font-family: 'Helvetica', sans-serif;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CARGA DE DATOS
# ==========================================
@st.cache_data
def load_data():
    FILE_PATH = 'Ecommerce_Data_Tableau.csv'
    try:
        df = pd.read_csv(FILE_PATH)
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
        
        if 'Cluster' in df.columns:
            df['Cluster'] = df['Cluster'].astype(str)
            # ETIQUETADO DE NEGOCIO
            cluster_spend = df.groupby('Cluster')['TotalAmount'].mean().sort_values(ascending=False)
            top_cluster = cluster_spend.index[0]
            bottom_cluster = cluster_spend.index[-1]
            
            def label_cluster(c):
                if c == top_cluster: return "Grupo Oro (VIP)"
                elif c == bottom_cluster: return "Grupo Bronce (Ocasional)"
                else: return "Grupo Plata (Recurrente)"
            
            df['Grupo'] = df['Cluster'].apply(label_cluster)
            
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is None:
    st.error("⚠️ Falta el archivo de datos. Ejecuta el notebook de procesamiento primero.")
    st.stop()

# ==========================================
# 3. BARRA LATERAL (FILTROS DE NEGOCIO)
# ==========================================
st.sidebar.header("Panel de Control")

# Filtro de Fechas
min_date = df['InvoiceDate'].min().date()
max_date = df['InvoiceDate'].max().date()
start_date, end_date = st.sidebar.date_input(
    "📅 Periodo de Análisis:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# --- Lógica del Botón "Seleccionar Todos" ---
all_countries = sorted(df['Country'].unique())

# Inicializamos la lista de países seleccionados
if 'paises_seleccionados' not in st.session_state:
    defaults = ['United Kingdom', 'Germany', 'France'] if 'United Kingdom' in all_countries else all_countries[:3]
    st.session_state.paises_seleccionados = [c for c in defaults if c in all_countries]

def seleccionar_todos():
    st.session_state.paises_seleccionados = all_countries

# Botón para activar todos
st.sidebar.button("🌍 Seleccionar Todos los Países", on_click=seleccionar_todos)

# Filtro Multiselect conectado a la memoria
sel_countries = st.sidebar.multiselect(
    "Filtrar Mercados:",
    options=all_countries,
    key='paises_seleccionados' 
)

if not sel_countries:
    st.sidebar.warning("Selecciona al menos un mercado.")
    st.stop()

# Aplicar filtros
mask = (
    (df['InvoiceDate'].dt.date >= start_date) & 
    (df['InvoiceDate'].dt.date <= end_date) & 
    (df['Country'].isin(sel_countries))
)
df_filtered = df.loc[mask]

st.sidebar.markdown("---")
st.sidebar.caption(f"📊 Analizando {df_filtered.shape[0]:,} transacciones")

# Menú de Navegación
page = st.sidebar.radio("📍 Navegación:", 
    ["1. Salud de los Datos", "2. Perfil de Clientes (Grupos)", "3. Oportunidades de Venta", "4. Análisis Geográfico Global"]
)

# ==========================================
# 4. PÁGINAS DEL REPORTE
# ==========================================

# --- PÁGINA 1: SALUD DE LOS DATOS ---
if page == "1. Salud de los Datos":
    st.title("Diagnóstico de la Información")
    st.markdown("Validación técnica para asegurar decisiones basadas en datos reales.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tendencia de Ventas")
        days_diff = (end_date - start_date).days
        freq = 'D' if days_diff < 60 else 'W' if days_diff < 365 else 'ME'
        label_freq = {'D': 'Diaria', 'W': 'Semanal', 'ME': 'Mensual'}
        
        sales_time = df_filtered.set_index('InvoiceDate').resample(freq)['TotalAmount'].sum().reset_index()
        fig = px.line(sales_time, x='InvoiceDate', y='TotalAmount', markers=True, 
                      title=f"Evolución de Ingresos ({label_freq.get(freq)})")
        fig.update_layout(xaxis_title="Fecha", yaxis_title="Ventas ($)")
        fig.update_traces(line_width=3)
        st.plotly_chart(fig, use_container_width=True, theme=None)

    with col2:
        st.subheader("¿Cada cuánto nos compran? (Ciclicidad)")
        
        daily_sales = df_filtered.set_index('InvoiceDate').resample('D')['TotalAmount'].sum().fillna(0)
        N = len(daily_sales)
        
        if N > 14:
            yf = fft(daily_sales.values)
            xf = fftfreq(N, 1)
            
            mask_fft = (xf > 0) & (xf < 0.5)
            fft_df = pd.DataFrame({
                'Frecuencia': xf[mask_fft],
                'Intensidad': np.abs(yf[mask_fft]),
                'Días': 1 / xf[mask_fft]
            })
            
            fig_fft = px.line(
                fft_df, 
                x='Frecuencia', 
                y='Intensidad',
                title="Intensidad de los Patrones de Compra",
                labels={'Intensidad': 'Relevancia del Patrón'},
                hover_data={'Días': ':.1f', 'Frecuencia': False, 'Intensidad': False}
            )
            
            fig_fft.add_vline(x=1/7, line_dash="dot", line_color="red", annotation_text="Ciclo Semanal (7 días)")
            fig_fft.update_traces(hovertemplate='<b>Se repite cada: %{customdata[0]:.1f} días</b><br>Intensidad: %{y:.2f}')
            fig_fft.update_xaxes(showticklabels=False, title_text="<-- Patrones Largos (Meses) ............ Patrones Cortos (Días) -->")
            
            st.plotly_chart(fig_fft, use_container_width=True, theme=None)
        else:
            st.warning("Selecciona un rango de fechas mayor a 2 semanas.")

# --- PÁGINA 2: PERFIL DE CLIENTES (CORREGIDA) ---
elif page == "2. Perfil de Clientes (Grupos)":
    st.title("👥 Análisis de Grupos de Clientes")
    st.markdown("Hemos segmentado su base de datos en 3 grupos según su comportamiento real.")

    if df_filtered.empty:
        st.warning("No hay datos.")
    else:
        df_users = df_filtered.groupby(['CustomerID', 'Grupo']).agg({
            'TotalAmount': 'sum', 
            'Quantity': 'sum', 
            'InvoiceNo': 'nunique'
        }).reset_index()
        
        df_users.columns = ['ID Cliente', 'Grupo', 'Gasto Total ($)', 'Volumen (Unidades)', 'Veces que Compró']

        with st.expander("Personalizar Gráfico", expanded=True):
            c1, c2 = st.columns(2)
            x_axis = c1.selectbox("Eje Horizontal", ['Veces que Compró', 'Gasto Total ($)', 'Volumen (Unidades)'], index=1)
            y_axis = c2.selectbox("Eje Vertical", ['Veces que Compró', 'Gasto Total ($)', 'Volumen (Unidades)'], index=0)
        
        color_map_fijo = {
            "Grupo Oro (VIP)": "#FFD700",          # Dorado
            "Grupo Plata (Recurrente)": "#C0C0C0", # Plateado
            "Grupo Bronce (Ocasional)": "#CD7F32"  # Bronce
        }

        col_viz, col_stats = st.columns([3, 1])
        
        with col_viz:
            fig_scatter = px.scatter(
                df_users, 
                x=x_axis, 
                y=y_axis, 
                color='Grupo', 
                size='Gasto Total ($)',
                hover_name='Grupo',
                log_x=True, log_y=True,
                title=f"Mapa de Distribución: {y_axis} vs {x_axis}",
                color_discrete_map=color_map_fijo,
                height=550
            )
            # Corrección de bordes para UK
            fig_scatter.update_traces(marker=dict(line=dict(width=0)))
            st.plotly_chart(fig_scatter, use_container_width=True, theme=None)

        with col_stats:
            st.subheader("Resumen por Grupo")
            stats = df_users.groupby('Grupo')[['Gasto Total ($)', 'Veces que Compró']].mean().sort_values('Gasto Total ($)', ascending=False)
            st.dataframe(stats.style.format("{:,.0f}"))

# --- PÁGINA 3: OPORTUNIDADES ---
elif page == "3. Oportunidades de Venta":
    st.title("Tablero de Oportunidades")
    
    selected_groups = st.multiselect("Filtrar por Grupo:", df_filtered['Grupo'].unique(), default=df_filtered['Grupo'].unique())
    df_opp = df_filtered[df_filtered['Grupo'].isin(selected_groups)]

    if not df_opp.empty:
        rev = df_opp['TotalAmount'].sum()
        cli = df_opp['CustomerID'].nunique()
        ticket = df_opp['TotalAmount'].mean()
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Ventas Potenciales", f"${rev:,.0f}")
        k2.metric("Clientes Activos", f"{cli:,}")
        k3.metric("Ticket Promedio", f"${ticket:,.2f}")
        
        st.markdown("---")
        
        g1, g2 = st.columns(2)
        with g1:
            st.subheader("📍 ¿Dónde vender más?")
            geo = df_opp.groupby('Country')['TotalAmount'].sum().sort_values(ascending=False).head(8).reset_index()
            fig = px.bar(geo, x='TotalAmount', y='Country', orientation='h', title="Top Mercados")
            fig.update_traces(
                marker_color='#D4AF37',
                marker_line_color='#FAFAFA',
                marker_line_width=1,
                opacity=0.9
            )

            fig.update_layout(
                plot_bgcolor='#0E1117',
                paper_bgcolor='#0E1117',
                font_color='#FAFAFA'
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="Ingresos ($)", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True, theme=None)
            
        with g2:
            st.subheader("¿Qué productos ofrecer?")
            prod = df_opp.groupby('Description')['TotalAmount'].sum().sort_values(ascending=False).head(8).reset_index()
            fig = px.bar(prod, x='TotalAmount', y='Description', orientation='h', title="Top Productos")
            fig.update_traces(
                marker_color='#D4AF37',
                marker_line_color='#FAFAFA',
                marker_line_width=1,
                opacity=0.9
            )

            fig.update_layout(
                plot_bgcolor='#0E1117',
                paper_bgcolor='#0E1117',
                font_color='#FAFAFA'
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="Ingresos ($)", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True, theme=None)
            
        csv = df_opp.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Listado (CSV)", csv, "listado_clientes.csv", "text/csv")
    else:
        st.warning("Selecciona un grupo para ver detalles.")

# --- PÁGINA 4: ANÁLISIS GEOGRÁFICO ---
elif page == "4. Análisis Geográfico Global":
    st.title("Análisis de Mercado por País")
    st.markdown("Visión completa del rendimiento geográfico.")

    if df_filtered.empty:
        st.warning("No hay datos para mostrar.")
    else:
        # Preparación de datos
        geo_data = df_filtered.groupby('Country').agg({
            'TotalAmount': 'sum',
            'CustomerID': 'nunique'
        }).reset_index().sort_values('TotalAmount', ascending=False)

        # Métricas de Dominancia
        top_country = geo_data.iloc[0]
        total_sales = geo_data['TotalAmount'].sum()
        dominance = (top_country['TotalAmount'] / total_sales) * 100
        
        m1, m2, m3 = st.columns(3)
        m1.metric("País Líder", top_country['Country'])
        m2.metric("Ventas del Líder", f"${top_country['TotalAmount']:,.0f}")
        m3.metric("Dominancia (% del Total)", f"{dominance:.1f}%")
        
        st.markdown("---")

        # Gráficos
        col_map, col_bar = st.columns([2, 1])
        
        with col_map:
            st.subheader("Mapa Global de Ventas")
            fig_map = px.choropleth(
                geo_data,
                locations="Country",
                locationmode='country names',
                color="TotalAmount",
                hover_name="Country",
                title="Distribución Geográfica",
                color_continuous_scale='Plasma'
            )
            fig_map.update_geos(showframe=False, projection_type="natural earth")
            st.plotly_chart(fig_map, use_container_width=True, theme=None)

        with col_bar:
            st.subheader("Ranking de Países")
            # Mostramos Top 15
            fig_bar = px.bar(
                geo_data.head(15), 
                x='TotalAmount', 
                y='Country', 
                orientation='h', 
                color='TotalAmount',
                title="Top 15 Mercados"
            )
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="Ventas ($)", yaxis_title="")
            st.plotly_chart(fig_bar, use_container_width=True, theme=None)

st.markdown("---")
st.caption("Herramienta de Inteligencia de Negocios | Datos actualizados en tiempo real")