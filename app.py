import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Função para login simples
def login():
    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    login_button = st.button("Entrar")
    
    if login_button:
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
        else:
            st.error("Usuário ou senha incorretos.")

# Função para upload e carregamento de planilha
def upload_excel():
    st.title("Upload de Planilha")
    uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        fase_categories = df['Fase'].unique()
        print(fase_categories)
        df['Fase'] = pd.Categorical(df['Fase'], categories=fase_categories)
        momento_categories = df['Momento'].unique()
        print(momento_categories)
        df['Momento'] = pd.Categorical(df['Momento'], categories=momento_categories)

        submomento_categories = df['Submomento'].unique()
        print(submomento_categories)
        df['Submomento'] = pd.Categorical(df['Submomento'], categories=submomento_categories)

        bola_parada_categories = df['Lance de Bola Parada?'].unique()
        print(bola_parada_categories)
        df['Lance de Bola Parada?'] = pd.Categorical(df['Lance de Bola Parada?'], categories=bola_parada_categories)
        
        com_bola_categories = df['Atleta com bola?'].unique()
        print(com_bola_categories)
        df['Atleta com bola?'] = pd.Categorical(df['Atleta com bola?'], categories=com_bola_categories)

        positivo_negativo_categories = df['Positivo ou Negativo'].unique()
        print(positivo_negativo_categories)
        df['Positivo ou Negativo'] = pd.Categorical(df['Positivo ou Negativo'], categories=positivo_negativo_categories)

        qualidade_categories = df['Qualidade técnica da execução'].unique()
        print(qualidade_categories)
        df['Qualidade técnica da execução'] = pd.Categorical(df['Qualidade técnica da execução'], categories=qualidade_categories)

        relevancia_categories = df['Relevância'].unique()
        print(relevancia_categories)
        df['Relevância'] = pd.Categorical(df['Relevância'], categories=relevancia_categories)

        dvd_categories = df['Vai pro DVD'].unique()
        print(dvd_categories)
        df['Vai pro DVD'] = pd.Categorical(df['Vai pro DVD'], categories=dvd_categories)





        st.session_state['data'] = df
        st.success("Planilha carregada com sucesso!")
        st.dataframe(df)
        return True
    return False

# Função para ajuste de metadados
def adjust_metadata():
    st.title("Ajuste de Metadados")
    df = st.session_state['data']
    
    st.subheader("Renomear Colunas")
    new_names = {}
    for col in df.columns:
        new_name = st.text_input(f"Novo nome para coluna '{col}'", value=col)
        new_names[col] = new_name
    
    if st.button("Aplicar mudanças"):
        df = df.rename(columns=new_names)
        st.session_state['data'] = df
        st.success("Metadados ajustados!")
        st.dataframe(df)

# Função para mostrar métricas (dashboard)
def dashboard():
    st.title("Dashboard de Métricas")
    df = st.session_state['data']

    st.subheader("Informações Gerais")
    st.metric("Número de linhas", df.shape[0])
    st.metric("Número de colunas", df.shape[1])

    st.subheader("Visualização rápida")
    st.dataframe(df.head())

    st.subheader("Estatísticas descritivas")
    st.write(df.info())

    st.title("Dashboard Interativo com Plotly")

    # Select categorical columns
    categorical_cols = df.select_dtypes(include=['category']).columns.tolist()

    # for col in categorical_cols:
    #     st.subheader(f"Frequência de '{col}'")
    #     fig = px.histogram(df, x=col, color=col, text_auto=True)
    #     st.plotly_chart(fig, use_container_width=True)

    tabs = st.tabs(categorical_cols)

    for tab, category in zip(tabs, categorical_cols):
        with tab:
            st.subheader(f"Frequência de '{category}'")
            fig = px.histogram(df, x=category, color=category, text_auto=True)
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{category}")





# Função principal
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login()
    else:
        st.sidebar.title("Navegação")
        page = st.sidebar.radio("Ir para", ["Upload Planilha", "Ajuste de Metadados", "Dashboard"])

        if page == "Upload Planilha":
            upload_excel()
        elif page == "Ajuste de Metadados":
            if 'data' in st.session_state:
                adjust_metadata()
            else:
                st.warning("Faça o upload de uma planilha primeiro.")
        elif page == "Dashboard":
            if 'data' in st.session_state:
                dashboard()
            else:
                st.warning("Faça o upload de uma planilha primeiro.")

if __name__ == "__main__":
    main()
