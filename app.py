import streamlit as st
import pandas as pd
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Vestibulinho Etecs 2026", layout="wide")

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=500)

st.title("Classificações Vestibulinho Etec 2026")
st.markdown("Dados referentes ao 1º semestre de 2026.")

# 2. CARREGAMENTO DOS DADOS
@st.cache_data
def carregar_dados():
    arquivo = 'classificacao_etec_2026.csv'
    if not os.path.exists(arquivo): return None
    
    df = pd.read_csv(arquivo, sep=';', encoding='utf-8-sig')
    df['Nome da Etec'] = df['Nome da Etec'].fillna('Não identificada')
    df['Cidade'] = df['Cidade'].fillna('Não identificada')
    df['Nota_Calc'] = df['Nota'].replace('AUSENTE', pd.NA)
    df['Nota_Calc'] = df['Nota_Calc'].astype(str).str.replace(',', '.')
    df['Nota_Calc'] = pd.to_numeric(df['Nota_Calc'], errors='coerce')
    return df

@st.cache_data
def carregar_demanda():
    arquivo = 'Demanda_ETEC_1SEM_2026 - Etec.xlsm'
    if not os.path.exists(arquivo): return None
    
    df_demanda = pd.read_excel(arquivo, engine='openpyxl')
    
    df_demanda.columns = ['Unidade', 'Curso', 'Período', 'Inscritos', 'Vagas', 'Demanda']
    
    df_demanda = df_demanda.sort_values(by='Unidade')
    return df_demanda

df = carregar_dados()
df_demanda = carregar_demanda()

# 3. INTERFACE E FILTROS
if df is None:
    st.error("Arquivo 'classificacao_etec_2026.csv' não encontrado!")
else:
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        lista_cidades = ["Todas"] + sorted(list(df['Cidade'].unique()))
        cidade_selecionada = st.selectbox("Selecione a Cidade:", lista_cidades)
        
    with col2:
        if cidade_selecionada != "Todas":
            etecs_disponiveis = ["Todas"] + sorted(list(df[df['Cidade'] == cidade_selecionada]['Nome da Etec'].unique()))
        else:
            etecs_disponiveis = ["Todas"] + sorted(list(df['Nome da Etec'].unique()))
        etec_selecionada = st.selectbox("Selecione a Etec:", etecs_disponiveis)
        
    with col3:
        termo_pesquisa = st.text_input("Pesquisar Nome ou Curso:", placeholder="Ex: Técnico em Enfermagem")

    df_filtrado = df.copy()
    if cidade_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Cidade'] == cidade_selecionada]
    if etec_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Nome da Etec'] == etec_selecionada]
    if termo_pesquisa:
        filtro_nome = df_filtrado['Nome'].str.contains(termo_pesquisa, case=False, na=False)
        filtro_curso = df_filtrado['Nome do Curso'].str.contains(termo_pesquisa, case=False, na=False)
        df_filtrado = df_filtrado[filtro_nome | filtro_curso]

    df_demanda_filtrado = df_demanda.copy() if df_demanda is not None else None
    if df_demanda_filtrado is not None and (cidade_selecionada != "Todas" or etec_selecionada != "Todas" or termo_pesquisa):

        if cidade_selecionada != "Todas":
            df_demanda_filtrado = df_demanda_filtrado[df_demanda_filtrado['Unidade'].str.contains(cidade_selecionada, case=False, na=False)]
        if etec_selecionada != "Todas":
            df_demanda_filtrado = df_demanda_filtrado[df_demanda_filtrado['Unidade'].str.contains(etec_selecionada, case=False, na=False)]

    aba1, aba2, aba3 = st.tabs(["📋 Classificação", "📈 Média de Notas", "👥 Demanda"])

    # ABAS
    with aba1:
        st.header("Consultar Classificação")
        PAGE_SIZE = 50
        if 'page' not in st.session_state: st.session_state.page = 1
        total_paginas = (len(df_filtrado) // PAGE_SIZE) + 1
        
        start_idx = (st.session_state.page - 1) * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        st.dataframe(df_filtrado.iloc[start_idx:end_idx].drop(columns=['Nota_Calc']), use_container_width=True, hide_index=True)
        
        cols_nav = st.columns([1, 1, 3])
        with cols_nav[0]:
            if st.button("Anterior"):
                if st.session_state.page > 1: st.session_state.page -= 1
        with cols_nav[1]:
            if st.button("Próximo"):
                if st.session_state.page < total_paginas: st.session_state.page += 1
        st.write(f"Página **{st.session_state.page}** de **{total_paginas}** | Total: {len(df_filtrado)} candidatos")

    with aba2:
        st.header("Média de Notas")
        df_medias = df_filtrado.groupby(['Cidade', 'Nome da Etec', 'Nome do Curso', 'Período'])['Nota_Calc'].mean().reset_index()
        df_medias['Média de Notas'] = df_medias['Nota_Calc'].round(2)
        st.dataframe(df_medias.drop(columns=['Nota_Calc']).sort_values(by=['Cidade', 'Nome da Etec']), use_container_width=True, hide_index=True)

    with aba3:
        st.header("Demanda de Candidatos")
        if df_demanda_filtrado is not None:
            st.dataframe(df_demanda_filtrado, use_container_width=True, hide_index=True)
        else:
            st.warning("Arquivo de demanda não encontrado.")