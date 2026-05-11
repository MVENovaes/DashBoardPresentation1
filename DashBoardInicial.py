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
    # Lê apenas as 5 primeiras linhas que contêm os dados reais das condições
    file_name = "ApresentaçãoCicloCompleto.xlsx"
    df = pd.read_excel(file_name, nrows=5)
    
    # As propriedades termodinâmicas avaliadas
    properties = ['Tdesc', 'Tsaid GC', 'Tsaid Aque', 'Tsaid Res', 'mpri', 'W', 'Qevap', 'Qcond', 'COP', 'SOMA']
    
    # Fatiamento do DataFrame baseado nos índices das colunas geradas pelo Excel
    # Índices 16 a 25 correspondem aos valores da seção "MAIOR" (Erro Máximo)
    df_max = df.iloc[:, 16:26].copy()
    df_max.columns = properties
    df_max['Condição'] = ['Condição 1', 'Condição 2', 'Condição 3', 'Condição 4', 'Condição 5']
    
    # Índices 29 a 38 correspondem aos valores da seção "DESVIO" (Desvio Padrão)
    df_std = df.iloc[:, 29:39].copy()
    df_std.columns = properties
    df_std['Condição'] = ['Condição 1', 'Condição 2', 'Condição 3', 'Condição 4', 'Condição 5']
    
    # Multiplicando por 100 para converter os decimais em porcentagem (%)
    for prop in properties:
        df_max[prop] = df_max[prop] * 100
        df_std[prop] = df_std[prop] * 100
        
    return df_max, df_std

df_max, df_std = load_data()

# 3. Construção da Barra Lateral (Menu de Seleção)
st.sidebar.header("Seletor de Propriedade")
propriedades_opcoes = ['COP', 'mpri', 'Qcond', 'Tsaid Res', 'Qevap', 'W', 'SOMA', 'Tdesc', 'Tsaid Aque', 'Tsaid GC']

# Substitui as múltiplas caixas de seleção do PowerBI por radio buttons para simplificar a lógica de visualização
propriedade_selecionada = st.sidebar.radio("Selecione a Propriedade:", propriedades_opcoes)

# 4. Layout dos Gráficos em Duas Colunas
col1, col2 = st.columns(2)

# Gráfico de Erro Máximo
with col1:
    st.markdown(f"### Erro máximo por condição ({propriedade_selecionada})")
    fig_max = px.bar(
        df_max, 
        x='Condição', 
        y=propriedade_selecionada, 
        text_auto='.3f', # Formata a etiqueta de dados com 3 casas decimais
        labels={propriedade_selecionada: 'Erro Máximo(%)'}
    )
    # Estilização para ficar idêntico ao PowerBI (barras azul escuro, texto fora)
    fig_max.update_traces(marker_color='#11258F', textposition='outside')
    fig_max.update_layout(yaxis_title='Erro Máximo(%)', xaxis_title='Condição de Teste', yaxis_range=[0, df_max[propriedade_selecionada].max() * 1.2])
    st.plotly_chart(fig_max, use_container_width=True)

# Gráfico de Desvio Padrão
with col2:
    st.markdown(f"### Desvio Padrão por condição ({propriedade_selecionada})")
    fig_std = px.bar(
        df_std, 
        x='Condição', 
        y=propriedade_selecionada, 
        text_auto='.3f',
        labels={propriedade_selecionada: 'Desvio Padrão(%)'}
    )
    fig_std.update_traces(marker_color='#11258F', textposition='outside')
    fig_std.update_layout(yaxis_title='Desvio Padrão(%)', xaxis_title='Condição de Teste', yaxis_range=[0, df_std[propriedade_selecionada].max() * 1.2])
    st.plotly_chart(fig_std, use_container_width=True)

# 5. Legenda das Condições na parte inferior
st.markdown("---")
st.subheader("Condições de Teste")
st.markdown("""
* **Condição 1:** Leva em consideração que a pressão é absoluta nos dados coletados e é calibrado com essa informação.
* **Condição 2:** Usa pressão manométrica dos dados mas a calibração da primeira condição.
* **Condição 3:** Usa a calibração do artigo com o código e pressão absoluta.
* **Condição 4:** Usa a calibração do artigo e pressão manométrica.
* **Condição 5:** Tentativa de calibrar novamente o modelo usando pressão manométrica.
""")