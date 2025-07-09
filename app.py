import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from PIL import Image
import io
from datetime import datetime
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import sqlite3
import re
from collections import Counter
import requests
import json

from sqlalchemy import create_engine

API_BASE_URL = st.secrets['API_BASE_URL']
def login():
    st.title("Login")

    # Check existing session
    token = st.context.cookies.to_dict()['access_token']
    if token:
        try:
            response = requests.post(f"{API_BASE_URL}/dashboard-auth", json={"token": token})
            if response.status_code == 200:
                user_data = response.json()
                st.session_state.logged_in = True
                st.session_state.username = user_data['user']
                st.success(f"Bem-vindo de volta, {st.session_state.username}!")
                return main()
        except requests.RequestException:
            pass  # Token expired or invalid

    # Show login form
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    login_button = st.button("Entrar")

    if login_button:
        if not username or not password:
            st.warning("Por favor, preencha todos os campos.")
            return

        try:
            response = requests.post(f"{API_BASE_URL}/login", json={
                "username": username,
                "password": password
            })

            if response.status_code == 200:
                data = response.json()
                st.session_state.access_token = data.get("access_token")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login realizado com sucesso!")
                return main()
            else:
                st.error("Usuário ou senha incorretos.")
        except requests.RequestException:
            st.error("Erro de conexão com o servidor.")


# Função para upload e carregamento de planilha
def upload_excel():
    st.title("Upload de Planilha")
    uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.dropna(inplace=True)
        try:
            fase_categories = df["Fase"].unique()
            print(fase_categories)
            df["Fase"] = pd.Categorical(df["Fase"], categories=fase_categories)
            momento_categories = df["Momento"].unique()
            print(momento_categories)
            df["Momento"] = pd.Categorical(df["Momento"], categories=momento_categories)

            submomento_categories = df["Submomento"].unique()
            print(submomento_categories)
            df["Submomento"] = pd.Categorical(
                df["Submomento"], categories=submomento_categories
            )

            bola_parada_categories = df["Lance de Bola Parada?"].unique()
            print(bola_parada_categories)
            df["Lance de Bola Parada?"] = pd.Categorical(
                df["Lance de Bola Parada?"], categories=bola_parada_categories
            )

            com_bola_categories = df["Atleta com bola?"].unique()
            print(com_bola_categories)
            df["Atleta com bola?"] = pd.Categorical(
                df["Atleta com bola?"], categories=com_bola_categories
            )

            positivo_negativo_categories = df["Positivo ou Negativo"].unique()
            print(positivo_negativo_categories)
            df["Positivo ou Negativo"] = pd.Categorical(
                df["Positivo ou Negativo"], categories=positivo_negativo_categories
            )

            qualidade_categories = df["Qualidade técnica da execução"].unique()
            print(qualidade_categories)
            df["Qualidade técnica da execução"] = pd.Categorical(
                df["Qualidade técnica da execução"], categories=qualidade_categories
            )

            relevancia_categories = df["Relevância"].unique()
            print(relevancia_categories)
            df["Relevância"] = pd.Categorical(
                df["Relevância"], categories=relevancia_categories
            )

            dvd_categories = df["Vai pro DVD"].unique()
            print(dvd_categories)
            df["Vai pro DVD"] = pd.Categorical(
                df["Vai pro DVD"], categories=dvd_categories
            )
        except Exception as e:
            print(f"Error trying to categorize cols. {e}")

        st.session_state["data"] = df
        st.success("Planilha carregada com sucesso!")
        st.dataframe(df)
        return True
    return False


def adjust_column_types():
    st.title("Ajustar Tipos de Colunas")
    df = st.session_state["data"]

    st.subheader("Selecione o tipo de dado para cada coluna")
    column_types = {}
    data_types = [
        "category",
        "int64",
        "float64",
        "object",
        "datetime64",
    ]  # Common pandas data types

    with st.form("column_types_form"):
        for col in df.columns:
            selected_type = st.selectbox(
                f"Tipo para coluna '{col}'",
                data_types,
                key=f"type_{col}",
                index=data_types.index(df[col].dtype.name)
                if df[col].dtype.name in data_types
                else 0,
            )
            column_types[col] = selected_type

        submitted = st.form_submit_button("Aplicar mudanças")
        if submitted:
            for col, dtype in column_types.items():
                if dtype == "category":
                    df[col] = pd.Categorical(df[col])
                elif dtype == "datetime64":
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                else:
                    df[col] = df[col].astype(dtype, errors="ignore")
            st.session_state["data"] = df
            st.success("Tipos de colunas ajustados com sucesso!")
            st.dataframe(df)


# Função para ajuste de metadados
def adjust_metadata():
    st.title("Ajuste de Metadados")
    df = st.session_state["data"]

    st.subheader("Renomear Colunas")
    new_names = {}
    for col in df.columns:
        new_name = st.text_input(f"Novo nome para coluna '{col}'", value=col)
        new_names[col] = new_name

    if st.button("Aplicar mudanças"):
        df = df.rename(columns=new_names)
        st.session_state["data"] = df
        st.success("Metadados ajustados!")
        st.dataframe(df)


# Função para mostrar métricas (dashboard)
def dashboard():
    st.title("Dashboard de Métricas")

    # Replace with your actual database connection URL
    # Example for PostgreSQL: "postgresql://user:password@host:port/dbname"
    # Example for SQLite: "sqlite:///path/to/db.sqlite"
    db_url = st.secrets["db_url"]
    engine = create_engine(db_url)

    # Query the data
    query = "SELECT id_atleta, nome FROM cadastro_atletas"
    atletas = pd.read_sql(query, engine)

    # st.dataframe(atletas)

    selected_atletas = st.multiselect(
        "Nome do atleta", options=atletas["nome"].unique()
    )
    if selected_atletas:
        id_atleta = atletas.loc[
            atletas["nome"].isin(selected_atletas), "id_atleta"
        ].to_list()
        #st.header(id_atleta)

        # Converte a lista de IDs para uma string tipo "49, 57"
        id_string = ", ".join(map(str, id_atleta))

        query_sessoes = f"""
            SELECT cadastro_atletas.nome, sessoes.* 
            FROM sessoes
            JOIN cadastro_atletas ON sessoes.id_atleta = cadastro_atletas.id_atleta
            WHERE sessoes.id_atleta IN ({id_string})
            """
        sessoes = pd.read_sql(query_sessoes, engine)
        #st.dataframe(sessoes)

        query_relatorio = f"""
    SELECT 
        s.data_sessao as "Data da Sessão",
        a.nome AS nome_atleta,
        rel.cena,
        fa.nome AS "Fase",
        mo.nome AS "Momento",
        sub.nome AS "Submomento",
        acb.nome AS "Atleta com Bola",
        pn.nome AS "Positivo ou Negativo",
        q.nome AS "Qualidade técnica da execução",
        relv.nome AS "Relevância",
        vpd.nome AS "Vai pro DVD",
        rel.descricao as "Descrição",
        rel.id_relatorio,
        s.id_sessao   
    FROM relatorio_sessao_analise rel
    JOIN sessoes s ON rel.id_sessao = s.id_sessao
    JOIN cadastro_atletas a ON s.id_atleta = a.id_atleta
    LEFT JOIN fases_jogo fa ON rel.fase = fa.id_fase
    LEFT JOIN momentos_jogo mo ON rel.momento = mo.id_momento
    LEFT JOIN submomentos_jogo sub ON rel.sub_momento = sub.id_submomento
    LEFT JOIN atleta_com_bola acb ON rel.atleta_com_bola = acb.id_acb
    LEFT JOIN positivo_negativo pn ON rel.positivo_negativo = pn.id_pn
    LEFT JOIN qualidade_execucao q ON rel.qualidade = q.id_qualidade
    LEFT JOIN relevancia relv ON rel.relevancia = relv.id_relevancia
    LEFT JOIN vai_pro_dvd vpd ON rel.vai_pro_dvd = vpd.id_vpd
    WHERE s.id_atleta IN ({id_string})
    """
        df = pd.read_sql(query_relatorio, engine)
        try:
            fase_categories = df["Fase"].unique()
            print(fase_categories)
            df["Fase"] = pd.Categorical(df["Fase"], categories=fase_categories)
            momento_categories = df["Momento"].unique()
            print(momento_categories)
            df["Momento"] = pd.Categorical(df["Momento"], categories=momento_categories)

            submomento_categories = df["Submomento"].unique()
            print(submomento_categories)
            df["Submomento"] = pd.Categorical(
                df["Submomento"], categories=submomento_categories
            )

            com_bola_categories = df["Atleta com Bola"].unique()
            print(com_bola_categories)
            df["Atleta com Bola"] = pd.Categorical(
                df["Atleta com Bola"], categories=com_bola_categories
            )

            positivo_negativo_categories = df["Positivo ou Negativo"].unique()
            print(positivo_negativo_categories)
            df["Positivo ou Negativo"] = pd.Categorical(
                df["Positivo ou Negativo"], categories=positivo_negativo_categories
            )

            qualidade_categories = df["Qualidade técnica da execução"].unique()
            print(qualidade_categories)
            df["Qualidade técnica da execução"] = pd.Categorical(
                df["Qualidade técnica da execução"], categories=qualidade_categories
            )

            relevancia_categories = df["Relevância"].unique()
            print(relevancia_categories)
            df["Relevância"] = pd.Categorical(
                df["Relevância"], categories=relevancia_categories
            )

            dvd_categories = df["Vai pro DVD"].unique()
            print(dvd_categories)
            df["Vai pro DVD"] = pd.Categorical(
                df["Vai pro DVD"], categories=dvd_categories
            )
        except Exception as e:
            print(f"Error trying to categorize cols. {e}")
        #st.dataframe(df)

    #     st.header("🔎 Filtros")
    #     st.write("Use os filtros abaixo para selecionar os dados que deseja visualizar.")

        # Filters
        if 'Data da Sessão'  in df.columns:
            key = 'Data da Sessão'
            selected_session = st.multiselect("Sessão (Data da Sessão)", options=df['Data da Sessão'].unique())
        else:
            key = 'Sessão'
            selected_session = st.multiselect("Sessão", options=df['Sessão'].unique())


        selected_momento = st.multiselect("Momento", options=df['Momento'].unique())
        selected_submomento = st.multiselect("Submomento", options=df['Submomento'].unique())
        selected_pos_neg = st.multiselect("Positivo ou Negativo", options=df['Positivo ou Negativo'].unique())

        # Apply filters
        filtered_df = df.copy()
        if selected_session:
            filtered_df = filtered_df[filtered_df[key].isin(selected_session)]
        if selected_momento:
            filtered_df = filtered_df[filtered_df['Momento'].isin(selected_momento)]
        if selected_submomento:
            filtered_df = filtered_df[filtered_df['Submomento'].isin(selected_submomento)]
        if selected_pos_neg:
            filtered_df = filtered_df[filtered_df['Positivo ou Negativo'].isin(selected_pos_neg)]

        st.success(f"{len(filtered_df)} registros encontrados após aplicar os filtros.")


        st.title("Dashboard Interativo com Plotly")
        # add a paragraph to explain how to use the dashboard

        st.write("Os gráficos abaixo mostram a distribuição dos dados filtrados.")


        # Select categorical columns
        categorical_cols = filtered_df.select_dtypes(include=['category']).columns.tolist()

        for col in categorical_cols:
            st.subheader(f"Frequência de '{col}'")
            fig = px.histogram(df, x=col, color=col, text_auto=True)
            st.plotly_chart(fig, use_container_width=True)


        if len(categorical_cols) > 0:
            tabs = st.tabs(categorical_cols)

            for tab, category in zip(tabs, categorical_cols):
                with tab:
                    st.subheader(f"Frequência de '{category}'")
                    fig = px.histogram(filtered_df, x=category, color=category, text_auto=True)
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{category}")


        st.title("Dashboard Interativo com Gráfico de Barras Agrupado")
        # explain how to use the stacked bar chart
        st.write("Selecione as colunas para o eixo X e para agrupar (cor). O gráfico de barras será exibido abaixo.")

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
            # update hove to portuguese
            fig.update_traces(hovertemplate=f'{x_axis}: %{{x}}<br>Contagem: %{{y}}')
            fig.update_layout(
                xaxis_title=x_axis,
                yaxis_title="Contagem",
                legend_title=group_color,
            )
            st.plotly_chart(fig, use_container_width=True)


        st.header("🔥 Ações Positivas por Momento e Submomento")
        # explain how to use the heatmap
        st.write("O gráfico de calor abaixo mostra a contagem de ações positivas por Momento e Submomento.")

        # Count Positives per Moment/Submoment
        df_moment = filtered_df[filtered_df['Positivo ou Negativo'] == 'Positivo'].groupby(['Momento', 'Submomento']).size().reset_index(name='Positive Count')

        fig_heatmap = px.density_heatmap(df_moment, x='Momento', y='Submomento', z='Positive Count',
                                        color_continuous_scale='Reds',
                                        title='Positive Actions Heatmap')
        # add black lines between the cells
        fig_heatmap.update_traces(showscale=False, hoverinfo='none')
        fig_heatmap.update_traces(hovertemplate='Momento: %{x}<br>Submomento: %{y}<br>Contagem: %{z}')

        fig_heatmap.update_layout(xaxis_showgrid=True, yaxis_showgrid=True)

        st.plotly_chart(fig_heatmap)

        st.header("Ações Positivas vs Negativas")
        # explain how to use the pie chart
        st.write("O gráfico de pizza abaixo mostra a distribuição de ações positivas e negativas.")

        df_pie = filtered_df['Positivo ou Negativo'].value_counts().reset_index()
        df_pie.columns = ['Label', 'Count']

        fig_pie = px.pie(df_pie, names='Label', values='Count', title='Positive vs Negative Distribution',
                        color_discrete_sequence=px.colors.sequential.RdBu)
        fig_pie.update_traces(hovertemplate='Ação: %{label}<br>Contagem: %{value}')
        fig_pie.update_layout(showlegend=True, legend_title_text='Ação')
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')


        st.plotly_chart(fig_pie)


        # Gráfico de palavras-chave (Wordcloud) - opcional
        try:


            st.subheader("Wordcloud das Descrições")
            texto = " ".join(df.loc[df['Positivo ou Negativo'] == 'Positivo']["Descrição"])
            # Filter words with more than 2 characters using regular expressions
            texto_filtrado = " ".join(
                [word for word in texto.split() if len(word) > 4 and word.lower() not in STOPWORDS]
            )

            word_counts = Counter(texto_filtrado.split())

    # Get the 10 most frequent words
            top_10_words = word_counts.most_common(6)


            # Display the top 10 most frequent words
            st.subheader("Top palavras mais frequentes em descrições positivas")
            #for word, count in top_10_words:
            #    st.write(f"{word}: {count}")

            # Generate a WordCloud using only the top 10 most frequent words
            top_words_dict = dict(top_10_words)  # Convert to dictionary for WordCloud
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(top_words_dict)

            # Plot the WordCloud
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)


            st.subheader("Top palavras mais frequentes em descrições negativas")

            texto = " ".join(df.loc[df['Positivo ou Negativo'] == 'Negativo']["Descrição"])
            # Filter words with more than 2 characters using regular expressions
            texto_filtrado = " ".join(
                [word for word in texto.split() if len(word) > 4 and word.lower() not in STOPWORDS]
            )

            word_counts = Counter(texto_filtrado.split())

    # Get the 10 most frequent words
            top_10_words = word_counts.most_common(3)
            #for word, count in top_10_words:
            #    st.write(f"{word}: {count}")

            # Generate a WordCloud using only the top 10 most frequent words
            top_words_dict = dict(top_10_words)  # Convert to dictionary for WordCloud
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(top_words_dict)

            # Plot the WordCloud
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
        except ImportError:
            st.warning("Wordcloud não está disponível. Instale 'wordcloud' para habilitar.")


    # # Function for editing the table
    # def edit_table():
    #     st.title("Soccer Data Manager")

    #     # Fetch all rows from the database
    #     rows = fetch_all_rows()
    #     df = pd.DataFrame(rows, columns=[
    #         "id", "sessao", "cena", "jogo", "fase", "momento", "submomento", "atleta_com_bola",
    #         "positivo_negativo", "qualidade_execucao", "relevancia", "descricao", "vai_pro_dvd", "orientacao_sessao"
    #     ])

    #     st.subheader("Database Contents")
    #     st.dataframe(df)

    #     # Form to add a new row
    #     st.subheader("Add New Row")
    #     sessao = str(st.date_input("Sessão", value=datetime.now())  )
    #     cena = st.number_input("Cena", step=1)
    #     jogo = st.text_input("Jogo")
    #     fase = st.selectbox("Fase", ["Defensiva", "Ofensiva"])
    #     momento = st.selectbox("Momento", ["Organização", "Transição", "Bola Parada"])
    #     submomento = st.selectbox("Submomento", [
    #         "Bloco Alto", "Bloco Medio Alto", "Bloco Medio", "Bloco Medio Baixo", "Bloco Baixo",
    #         "Recomposição", "Pressão Pos Perda", "Saida de bola", "Construção", "Criação",
    #         "Finalização", "Temporização", "Ataque Rapido", "Contra ataque", "Campo de Ataque",
    #         "Campo de Defesa", "Tiro de Meta", "Escanteio", "Falta Lateral", "Falta Frontal",
    #         "Lateral", "Penalti"
    #     ])
    #     atleta_com_bola = st.selectbox("Atleta com bola", ["Com", "Sem"])
    #     positivo_negativo = st.selectbox("Positivo ou Negativo", ["Positivo", "Negativo"])
    #     qualidade_execucao = st.selectbox("Qualidade Técnica da Execução", ["Alta", "Media", "Baixa"])
    #     relevancia = st.selectbox("Relevância", ["Alta", "Media", "Baixa"])
    #     descricao = st.text_area("Descrição")
    #     vai_pro_dvd = st.selectbox("Vai pro DVD", ["SIM", "TALVEZ", "NAO"])
    #     orientacao_sessao = st.text_area("Orientação na Sessão")

    #     if st.button("Add Row"):
    #         insert_row((
    #             sessao, cena, jogo, fase, momento, submomento, atleta_com_bola,
    #             positivo_negativo, qualidade_execucao, relevancia, descricao, vai_pro_dvd, orientacao_sessao
    #         ))
    #         st.success("Row added successfully!")
    #         st.experimental_rerun()


# Update sidebar for navigation to include the new page
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
            [
                "Home",
                "Dashboard",
            ],
            index=0,
        )
        st.markdown("---")

        # Logout Button
        if st.button("🔒 Logout"):
            try:
                # Ask backend to clear the cookie
                token = st.context.cookies.to_dict().get("access_token")
                if token:
                    requests.post(f"{API_BASE_URL}/logout", json={"token": token})
                    st.context.cookies = 0
                    login()
            except Exception as e:
                st.warning("Erro ao limpar cookie no servidor.")

            # Clear Streamlit session state
            st.session_state.clear()
            st.success("Você saiu com sucesso.")
            st.markdown('<meta http-equiv="refresh" content="0; url=/logout">', unsafe_allow_html=True)
    return page


# Main function
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    if not st.session_state.logged_in:
        login()
    else:
        page = sidebar()
        if page == "Home":
            st.title("Bem-vindo à Aplicação de Dashboard!")
            st.write("Faça upload de uma planilha, ajuste dados e veja o dashboard!")
        elif page == "Upload Planilha":
            upload_excel()
        elif page == "Ajuste de Metadados":
            if "data" in st.session_state:
                adjust_metadata()
            else:
                st.warning("Faça o upload de uma planilha primeiro.")
        elif page == "Ajustar Tipos de Colunas":
            if "data" in st.session_state:
                adjust_column_types()
            else:
                st.warning("Faça o upload de uma planilha primeiro.")
        elif page == "Dashboard":
            dashboard()
        elif page == "Editar Tabela":
            if "data" in st.session_state:
                print("data")
                # edit_table()
            else:
                st.warning("Faça o upload de uma planilha primeiro.")


if __name__ == "__main__":
    # init_db()
    main()
