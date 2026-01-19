import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import unicodedata

# Configuração da página - Deve ser a primeira instrução Streamlit
st.set_page_config(
    page_title="LegalInsights - Dashboard Jurídico",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILO CSS CUSTOMIZADO (UI/UX) ---
def apply_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        /* Tema Dark Rigoroso */
        .stApp {
            background-color: #0e1117;
            color: #ffffff;
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }

        /* Cards de Métricas Customizados */
        .metric-card {
            background-color: #161b22;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #30363d;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            text-align: center;
            transition: transform 0.3s ease, border-color 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            border-color: #00d2ff; /* Cor Neon */
        }

        .metric-label {
            color: #8b949e;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }

        .metric-value {
            color: #00d2ff; /* Cor Neon */
            font-size: 1.75rem;
            font-weight: 700;
            text-shadow: 0 0 10px rgba(0, 210, 255, 0.3);
        }

        /* Ajustes de Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0d1117;
            border-right: 1px solid #30363d;
        }

        /* Tabelas e Dataframes */
        .stDataFrame {
            border: 1px solid #30363d;
            border-radius: 10px;
        }

        /* Esconder elementos padrão */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE PROCESSAMENTO E SEGURANÇA ---
def remover_acentos(texto):
    if not isinstance(texto, str):
        return texto
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

@st.cache_data
def load_and_process_data(file_path):
    try:
        df = pd.read_excel(file_path)
        
        # Limpeza de colunas (espaços e acentos)
        df.columns = [remover_acentos(col.strip()) for col in df.columns]
        
        # Tratamento de valores nulos (Sanitização)
        df['Honorarios'] = pd.to_numeric(df['Honorarios'], errors='coerce').fillna(0)
        df['Valor_Causa'] = pd.to_numeric(df['Valor_Causa'], errors='coerce').fillna(0)
        df['Probabilidade_Exito'] = pd.to_numeric(df['Probabilidade_Exito'], errors='coerce').fillna(0)
        df['Data_Abertura'] = pd.to_datetime(df['Data_Abertura'], errors='coerce')
        
        # Anonimização de Clientes (Segurança de Dados)
        def anonimizar(nome):
            if not isinstance(nome, str): return "N/A"
            parts = nome.split()
            return f"{parts[0]} " + "*" * 5 if parts else "CLIENTE_ANONIMO"
        
        df['Cliente_Display'] = df['Cliente'].apply(anonimizar)

        # --- NOVOS CÁLCULOS (MELHORIA 1) ---
        # Previsão de Faturamento: Valor da Causa * Probabilidade de Êxito
        df['Faturamento_Estimado'] = df['Valor_Causa'] * df['Probabilidade_Exito']
        
        # Aging: Dias desde a abertura
        df['Dias_Aberto'] = (datetime.now() - df['Data_Abertura']).dt.days
        
        return df
    except Exception as e:
        st.error(f"Erro crítico ao processar o arquivo: {e}")
        return None

# --- COMPONENTES VISUAIS ---

def render_kpis(df):
    total_processos = len(df)
    faturamento_total = df['Honorarios'].sum()
    prev_faturamento = df['Faturamento_Estimado'].sum()
    taxa_exito_media = df['Probabilidade_Exito'].mean() * 100

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Processos Ativos</div><div class="metric-value">{total_processos}</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Honorários Totais</div><div class="metric-value">R$ {faturamento_total:,.2f}</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Previsão (Probabilística)</div><div class="metric-value">R$ {prev_faturamento:,.2f}</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Êxito Médio</div><div class="metric-value">{taxa_exito_media:.1f}%</div></div>""", unsafe_allow_html=True)

def render_main_charts(df):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico de Área: Evolução Temporal
        df_evolucao = df.dropna(subset=['Data_Abertura']).copy()
        df_evolucao = df_evolucao.sort_values('Data_Abertura')
        df_evolucao = df_evolucao.groupby(pd.Grouper(key='Data_Abertura', freq='W')).size().reset_index(name='Quantidade')
        
        fig_area = px.area(df_evolucao, x='Data_Abertura', y='Quantidade', 
                          title="<b>Evolução Temporal de Novos Processos (Semanal)</b>",
                          color_discrete_sequence=['#00d2ff'])
        
        fig_area.update_layout(
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis_title=None,
            xaxis_title=None,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig_area, use_container_width=True)

    with col2:
        # Donut: Processos por Status
        df_status = df['Status'].value_counts().reset_index()
        fig_status = px.pie(df_status, values='count', names='Status', hole=0.7,
                           title="<b>Status dos Processos</b>",
                           color_discrete_sequence=['#00d2ff', '#00b8e6', '#009ec2', '#0083a3', '#006982'])
        
        fig_status.update_layout(
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=False
        )
        st.plotly_chart(fig_status, use_container_width=True)

def render_secondary_charts(df):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Donut: Receita por Área
        df_area_receita = df.groupby('Area')['Honorarios'].sum().reset_index()
        fig_area_receita = px.pie(df_area_receita, values='Honorarios', names='Area', hole=0.7,
                                 title="<b>Receita por Área do Direito</b>",
                                 color_discrete_sequence=['#00d2ff', '#00b8e6', '#009ec2', '#0083a3', '#006982'])
        
        fig_area_receita.update_layout(
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig_area_receita, use_container_width=True)

    with col2:
        # Mapa de Calor: Distribuição Geográfica (UF)
        df_uf = df.groupby('UF').size().reset_index(name='Quantidade')
        
        # Coordenadas aproximadas para UFs do Brasil
        coords_br = {
            'SP': [-23.55, -46.63], 'RJ': [-22.90, -43.17], 'MG': [-19.91, -43.93],
            'RS': [-30.03, -51.21], 'PR': [-25.42, -49.27], 'SC': [-27.59, -48.54],
            'BA': [-12.97, -38.50], 'PE': [-8.05, -34.88], 'DF': [-15.78, -47.92],
            'CE': [-3.71, -38.54]
        }
        df_uf['lat'] = df_uf['UF'].map(lambda x: coords_br.get(x, [0,0])[0])
        df_uf['lon'] = df_uf['UF'].map(lambda x: coords_br.get(x, [0,0])[1])

        fig_mapa = px.scatter_geo(df_uf, lat='lat', lon='lon', size='Quantidade',
                                 hover_name='UF', title="<b>Distribuição Geográfica (UF)</b>",
                                 scope='south america', template="plotly_dark",
                                 color_discrete_sequence=['#00d2ff'])
        
        fig_mapa.update_geos(
            visible=False, 
            resolution=50,
            showcountries=True, 
            countrycolor="#30363d",
            showland=True, 
            landcolor="#161b22",
            lataxis_range=[-35, 5], 
            lonaxis_range=[-75, -30]
        )
        fig_mapa.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_mapa, use_container_width=True)

def render_performance_table(df):
    st.markdown("### 🏆 Performance por Advogado")
    
    df_perf = df.groupby('Advogado').agg({
        'Honorarios': 'sum',
        'ID': 'count',
        'Probabilidade_Exito': 'mean'
    }).reset_index()
    
    df_perf.columns = ['Advogado', 'Honorarios_Total', 'Total_Processos', 'Taxa_Exito_Media']
    df_perf = df_perf.sort_values('Honorarios_Total', ascending=False)
    
    st.dataframe(
        df_perf,
        column_config={
            "Advogado": "Nome do Advogado",
            "Honorarios_Total": st.column_config.ProgressColumn(
                "Volume de Honorários",
                format="R$ %.2f",
                min_value=0,
                max_value=float(df_perf['Honorarios_Total'].max())
            ),
            "Total_Processos": st.column_config.NumberColumn("Processos", format="%d ⚖️"),
            "Taxa_Exito_Media": st.column_config.NumberColumn("Êxito Médio", format="%.2f%%")
        },
        hide_index=True,
        use_container_width=True
    )

# --- EXECUÇÃO PRINCIPAL ---
def main():
    apply_custom_css()
    
    df = load_and_process_data('dados_juridicos.xlsx')
    
    if df is not None:
        # Sidebar com Filtros Globais (MELHORIA 2)
        with st.sidebar:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
            st.title("LegalInsights")
            st.markdown("---")
            
            st.subheader("🎯 Filtros Globais")
            
            # Filtro de Data
            min_date = df['Data_Abertura'].min().to_pydatetime()
            max_date = df['Data_Abertura'].max().to_pydatetime()
            date_range = st.date_input("Período de Abertura", [min_date, max_date], min_value=min_date, max_value=max_date)
            
            # Filtros Multiselect
            areas_sel = st.multiselect("Áreas do Direito", options=sorted(df['Area'].unique()), default=df['Area'].unique())
            status_sel = st.multiselect("Status dos Processos", options=sorted(df['Status'].unique()), default=df['Status'].unique())
            ufs_sel = st.multiselect("UFs", options=sorted(df['UF'].unique()), default=df['UF'].unique())
            
            st.markdown("---")
            st.info("💡 As alterações aplicam-se a todo o dashboard.")

        # Aplicação dos Filtros
        mask = (
            (df['Area'].isin(areas_sel)) &
            (df['Status'].isin(status_sel)) &
            (df['UF'].isin(ufs_sel))
        )
        
        # Filtro de data seguro
        if isinstance(date_range, list) and len(date_range) == 2:
            mask &= (df['Data_Abertura'].dt.date >= date_range[0]) & (df['Data_Abertura'].dt.date <= date_range[1])
        
        display_df = df.loc[mask]

        # Cabeçalho Principal
        st.title("⚖️ Dashboard de Análise Jurídica")
        
        # Abas (MELHORIA 3)
        tab1, tab2, tab3 = st.tabs(["📊 Resumo Executivo", "⚙️ Operacional", "🏆 Performance"])
        
        with tab1:
            render_kpis(display_df)
            st.markdown("<br>", unsafe_allow_html=True)
            render_main_charts(display_df)
            
        with tab2:
            col_a, col_b = st.columns([1, 1])
            with col_a:
                render_secondary_charts(display_df)
            with col_b:
                st.subheader("🕒 Aging de Processos (Dias)")
                fig_aging = px.histogram(display_df, x='Dias_Aberto', nbins=20, 
                                        title="Distribuição de Idade dos Processos",
                                        color_discrete_sequence=['#00d2ff'])
                fig_aging.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_aging, use_container_width=True)
            
            st.markdown("---")
            st.subheader("📋 Dados Detalhados")
            st.dataframe(display_df[['ID', 'Cliente_Display', 'Area', 'Status', 'Honorarios', 'Faturamento_Estimado', 'UF']], use_container_width=True)
            
            # Exportação (MELHORIA 4)
            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exportar Dados Filtrados (CSV)",
                data=csv,
                file_name=f'relatorio_juridico_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
            )
            
        with tab3:
            render_performance_table(display_df)

    else:
        st.warning("⚠️ O arquivo 'dados_juridicos.xlsx' não foi encontrado.")
        if st.button("Gerar Base de Dados de Exemplo"):
            try:
                import subprocess
                subprocess.run(["python", "gerar_dados.py"], check=True)
                st.success("Base de dados gerada com sucesso! Recarregando...")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao gerar dados: {e}")

if __name__ == "__main__":
    main()
