import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from PIL import Image

# Função para login simples
def login():
    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    login_button = st.button("Entrar")
    
    if login_button:
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.username = username  # Save it
        else:
            st.error("Usuário ou senha incorretos.")

# Função para upload e carregamento de planilha
def upload_excel():
    st.title("Upload de Planilha")
    uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
    #     fase_categories = df['Fase'].unique()
    #     print(fase_categories)
    #     df['Fase'] = pd.Categorical(df['Fase'], categories=fase_categories)
    #     momento_categories = df['Momento'].unique()
    #     print(momento_categories)
    #     df['Momento'] = pd.Categorical(df['Momento'], categories=momento_categories)

    #     submomento_categories = df['Submomento'].unique()
    #     print(submomento_categories)
    #     df['Submomento'] = pd.Categorical(df['Submomento'], categories=submomento_categories)

    #     bola_parada_categories = df['Lance de Bola Parada?'].unique()
    #     print(bola_parada_categories)
    #     df['Lance de Bola Parada?'] = pd.Categorical(df['Lance de Bola Parada?'], categories=bola_parada_categories)
        
    #     com_bola_categories = df['Atleta com bola?'].unique()
    #     print(com_bola_categories)
    #     df['Atleta com bola?'] = pd.Categorical(df['Atleta com bola?'], categories=com_bola_categories)

    #     positivo_negativo_categories = df['Positivo ou Negativo'].unique()
    #     print(positivo_negativo_categories)
    #     df['Positivo ou Negativo'] = pd.Categorical(df['Positivo ou Negativo'], categories=positivo_negativo_categories)

    #     qualidade_categories = df['Qualidade técnica da execução'].unique()
    #     print(qualidade_categories)
    #     df['Qualidade técnica da execução'] = pd.Categorical(df['Qualidade técnica da execução'], categories=qualidade_categories)

    #     relevancia_categories = df['Relevância'].unique()
    #     print(relevancia_categories)
    #     df['Relevância'] = pd.Categorical(df['Relevância'], categories=relevancia_categories)

    #     dvd_categories = df['Vai pro DVD'].unique()
    #     print(dvd_categories)
    #     df['Vai pro DVD'] = pd.Categorical(df['Vai pro DVD'], categories=dvd_categories)





        st.session_state['data'] = df
        st.success("Planilha carregada com sucesso!")
        st.dataframe(df)
        return True
    return False

def adjust_column_types():
    st.title("Ajustar Tipos de Colunas")
    df = st.session_state['data']

    st.subheader("Selecione o tipo de dado para cada coluna")
    column_types = {}
    data_types = ['category', 'int64', 'float64', 'object', 'datetime64']  # Common pandas data types

    with st.form("column_types_form"):
        for col in df.columns:
            selected_type = st.selectbox(f"Tipo para coluna '{col}'", data_types, key=f"type_{col}", index=data_types.index(df[col].dtype.name) if df[col].dtype.name in data_types else 0)
            column_types[col] = selected_type

        submitted = st.form_submit_button("Aplicar mudanças")
        if submitted:
            for col, dtype in column_types.items():
                if dtype == 'category':
                    df[col] = pd.Categorical(df[col])
                elif dtype == 'datetime64':
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                else:
                    df[col] = df[col].astype(dtype, errors='ignore')
            st.session_state['data'] = df
            st.success("Tipos de colunas ajustados com sucesso!")
            st.dataframe(df)    

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

    st.header("🔎 Filtros")

    # Filters
    selected_session = st.multiselect("Sessão (Data da Sessão)", options=df['Data da Sessão'].unique())
    selected_momento = st.multiselect("Momento", options=df['Momento'].unique())
    selected_submomento = st.multiselect("Submomento", options=df['Submomento'].unique())
    selected_pos_neg = st.multiselect("Positivo ou Negativo", options=df['Positivo ou Negativo'].unique())

    # Apply filters
    filtered_df = df.copy()
    if selected_session:
        filtered_df = filtered_df[filtered_df['Data da Sessão'].isin(selected_session)]
    if selected_momento:
        filtered_df = filtered_df[filtered_df['Momento'].isin(selected_momento)]
    if selected_submomento:
        filtered_df = filtered_df[filtered_df['Submomento'].isin(selected_submomento)]
    if selected_pos_neg:
        filtered_df = filtered_df[filtered_df['Positivo ou Negativo'].isin(selected_pos_neg)]

    st.success(f"{len(filtered_df)} registros encontrados após aplicar os filtros.")

    

    st.title("Dashboard Interativo com Plotly")

    # Select categorical columns
    categorical_cols = filtered_df.select_dtypes(include=['category']).columns.tolist()

    # for col in categorical_cols:
    #     st.subheader(f"Frequência de '{col}'")
    #     fig = px.histogram(df, x=col, color=col, text_auto=True)
    #     st.plotly_chart(fig, use_container_width=True)

    tabs = st.tabs(categorical_cols)

    for tab, category in zip(tabs, categorical_cols):
        with tab:
            st.subheader(f"Frequência de '{category}'")
            fig = px.histogram(filtered_df, x=category, color=category, text_auto=True)
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{category}")


    st.title("Dashboard Interativo com Gráfico de Barras Agrupado")

    # Get only categorical columns
    categorical_cols = filtered_df.select_dtypes(include=['category']).columns.tolist()

    # User selects X and Color group
    x_axis = st.selectbox("Escolha a coluna para o eixo X", categorical_cols, key="x_axis")
    group_color = st.selectbox("Escolha a coluna para agrupar (cor)", categorical_cols)

    if x_axis and group_color:
        fig = px.histogram(
            filtered_df,
            x=x_axis,
            color=group_color,
            barmode='group',  # THIS makes it grouped instead of stacked
            text_auto=True,
        )
        fig.update_layout(
            xaxis_title=x_axis,
            yaxis_title="Contagem",
            legend_title=group_color,
        )
        st.plotly_chart(fig, use_container_width=True)


    st.header("🔥 Performance by Moment/Submoment")

    # Count Positives per Moment/Submoment
    df_moment = filtered_df[filtered_df['Positivo ou Negativo'] == 'Positivo'].groupby(['Momento', 'Submomento']).size().reset_index(name='Positive Count')

    fig_heatmap = px.density_heatmap(df_moment, x='Momento', y='Submomento', z='Positive Count',
                                    color_continuous_scale='Blues',
                                    title='Positive Actions Heatmap')

    st.plotly_chart(fig_heatmap)

    st.header("Positive vs Negative Actions")

    df_pie = filtered_df['Positivo ou Negativo'].value_counts().reset_index()
    df_pie.columns = ['Label', 'Count']

    fig_pie = px.pie(df_pie, names='Label', values='Count', title='Positive vs Negative Distribution',
                    color_discrete_sequence=px.colors.sequential.RdBu)

    st.plotly_chart(fig_pie)
 

def sidebar():
    with st.sidebar:
        # Logo
        logo = Image.open("logo.png")  # Your logo file
        st.image(logo, use_container_width=True)

        # Welcome Message
        st.markdown(f"### Bem-vindo, {st.session_state.get('username', 'Usuário')}!")

        st.markdown("---")

        # Navigation
        page = st.radio(
            "Navegação",
            ["Home", "Upload Planilha", "Ajuste de Metadados", "Ajustar Tipos de Colunas", "Dashboard"],
            index=0
        )

        st.markdown("---")

        # Logout Button
        if st.button("🔒 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.success("Você saiu com sucesso.")

    return page



# Função principal
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""

    if not st.session_state.logged_in:
        login()
    else:
        page = sidebar()  # ← Use the new professional sidebar

        if page == "Home":
            st.title("Bem-vindo à Aplicação de Dashboard!")
            st.write("Faça upload de uma planilha, ajuste dados e veja o dashboard!")
        elif page == "Upload Planilha":
            upload_excel()
        elif page == "Ajuste de Metadados":
            if 'data' in st.session_state:
                adjust_metadata()
            else:
                st.warning("Faça o upload de uma planilha primeiro.")
        elif page == "Ajustar Tipos de Colunas":
            if 'data' in st.session_state:
                adjust_column_types()
            else:
                st.warning("Faça o upload de uma planilha primeiro.")
        elif page == "Dashboard":
            if 'data' in st.session_state:
                dashboard()
            else:
                st.warning("Faça o upload de uma planilha primeiro.")

if __name__ == "__main__":
    main()
