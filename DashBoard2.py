import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração inicial da página
st.set_page_config(layout="wide", page_title="Dashboard de Calibração do Ciclo")

st.title("Análise de Calibração do Ciclo")
st.markdown("---")

# 2. Carregamento e Tratamento dos Dados
@st.cache_data
def load_data():
    file_name = "ApresentaçãoCicloCompleto.csv"
    # Se estiver a usar o ficheiro Excel diretamente
    df = pd.read_csv(file_name, nrows=5,encoding='latin1', sep=';', decimal=',')
    
    # Propriedades e etiquetas das condições
    properties = ['Tdesc', 'Tsaid GC', 'Tsaid Aque', 'Tsaid Res', 'mpri', 'W', 'Qevap', 'Qcond', 'COP', 'SOMA']
    condicoes = ['Condição 1', 'Condição 2', 'Condição 3', 'Condição 4', 'Condição 5']
    
    # EXTRAÇÃO DOS TRÊS BLOCOS (conforme a estrutura das colunas)
    
    # Bloco 1: MEDIA (Erro Médio) - Geralmente colunas 3 a 12
    df_mean = df.iloc[:, 3:13].copy()
    df_mean.columns = properties
    df_mean['Condição'] = condicoes

    # Bloco 2: MAIOR (Erro Máximo) - Colunas 16 a 25
    df_max = df.iloc[:, 16:26].copy()
    df_max.columns = properties
    df_max['Condição'] = condicoes
    
    # Bloco 3: DESVIO (Desvio Padrão) - Colunas 29 a 38
    df_std = df.iloc[:, 29:39].copy()
    df_std.columns = properties
    df_std['Condição'] = condicoes
    
    for prop in properties:
        # Pega a coluna, garante que é texto, troca vírgula por ponto (caso exista) e converte para número
        df_mean[prop] = pd.to_numeric(df_mean[prop].astype(str).str.replace(',', '.'), errors='coerce') * 100
        df_max[prop]  = pd.to_numeric(df_max[prop].astype(str).str.replace(',', '.'), errors='coerce') * 100
        df_std[prop]  = pd.to_numeric(df_std[prop].astype(str).str.replace(',', '.'), errors='coerce') * 100
        
    return df_mean, df_max, df_std

# IMPORTANTE: Desempacotar os 3 valores aqui
df_mean, df_max, df_std = load_data()

# 3. Barra Lateral
# 3. Barra Lateral
st.sidebar.header("Seletor de Propriedade")

# Mapeamento: nome exibido -> nome real da coluna
mapa_propriedades = {
    'COP': 'COP',
    'Fluxo de Massa kg/s': 'mpri',
    'Gas Cooler (W)': 'Qcond',
    'Saída Água ºC': 'Tsaid Aque',
    'Evaporador (W)': 'Qevap',
    'Compressor (W)': 'W',
    'SOMA': 'SOMA',
    'Descarga ºC': 'Tdesc',
    'Saída Glicol ºC': 'Tsaid Res',
    'Gas Cooler Saída ºC': 'Tsaid GC'
}

nome_exibido = st.sidebar.radio("Selecione a Propriedade:", list(mapa_propriedades.keys()))
propriedade_selecionada = mapa_propriedades[nome_exibido]  # nome real da coluna


# 4. Layout em Três Colunas
col1, col2, col3 = st.columns(3)

# --- Gráfico 1: Erro Médio ---
with col1:
    st.markdown(f"### Erro médio por condição ({propriedade_selecionada})")
    fig_mean = px.bar(
        df_mean, x='Condição', y=propriedade_selecionada, text_auto='.3f',
        labels={propriedade_selecionada: 'Erro Médio(%)'}
    )
    fig_mean.update_traces(marker_color='#11258F', textposition='outside')
    fig_mean.update_layout(yaxis_title='Erro Médio(%)', xaxis_title='Condição de Teste', 
                           yaxis_range=[0, df_mean[propriedade_selecionada].max() * 1.3])
    st.plotly_chart(fig_mean, use_container_width=True)

# --- Gráfico 2: Erro Máximo ---
with col2:
    st.markdown(f"### Erro máximo por condição ({propriedade_selecionada})")
    fig_max = px.bar(
        df_max, x='Condição', y=propriedade_selecionada, text_auto='.3f',
        labels={propriedade_selecionada: 'Erro Máximo(%)'}
    )
    fig_max.update_traces(marker_color='#11258F', textposition='outside')
    fig_max.update_layout(yaxis_title='Erro Máximo(%)', xaxis_title='Condição de Teste', 
                          yaxis_range=[0, df_max[propriedade_selecionada].max() * 1.3])
    st.plotly_chart(fig_max, use_container_width=True)

# --- Gráfico 3: Desvio Padrão ---
with col3:
    st.markdown(f"### Desvio Padrão por condição ({propriedade_selecionada})")
    fig_std = px.bar(
        df_std, x='Condição', y=propriedade_selecionada, text_auto='.3f',
        labels={propriedade_selecionada: 'Desvio Padrão(%)'}
    )
    fig_std.update_traces(marker_color='#11258F', textposition='outside')
    fig_std.update_layout(yaxis_title='Desvio Padrão(%)', xaxis_title='Condição de Teste', 
                          yaxis_range=[0, df_std[propriedade_selecionada].max() * 1.3])
    st.plotly_chart(fig_std, use_container_width=True)

# 5. Legenda das Condições
st.markdown("---")
st.subheader("Condições de Teste")
st.markdown("""
            Ficou indefinido se a pressão dos testes eram de pressão absoluta ou manométrica fica então a comparação dos casos
* **Condição 1:** Pressão absoluta | Calibração calibrada com dados de medição considerados pressão absoluta.
* **Condição 2:** Pressão manométrica | Calibração da primeira condição supondo dados com medição manométrica.
* **Condição 3:** Pressão absoluta | Calibração do artigo de Richard Samir Hernandez Mesa considerando pressão absoluta.
* **Condição 4:** Pressão manométrica | Calibração do artigo supondo dados com medição manométrica.
* **Condição 5:** Pressão manométrica | Tentativa de recalibração do modelo supondo dados com medição manométrica.
""")
