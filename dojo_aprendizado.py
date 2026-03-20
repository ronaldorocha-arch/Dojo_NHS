import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# --- 1. CONFIGURAÇÃO E DADOS ---
FILE_DOJO = "dados_dojo.csv"

def carregar_dados():
    if not os.path.exists(FILE_DOJO):
        return pd.DataFrame(columns=["Operador", "Amostra 1", "Amostra 2", "Amostra 3"])
    try:
        df = pd.read_csv(FILE_DOJO)
        # Garante que os IDs dos operadores sejam mantidos se houver
        return df
    except:
        return pd.DataFrame(columns=["Operador", "Amostra 1", "Amostra 2", "Amostra 3"])

st.set_page_config(page_title="DojoNHS - Curva de Aprendizado", layout="wide", page_icon="📈")

# --- 2. ESTILO CSS ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #000000 !important; font-weight: 400 !important; }
    .stButton > button { width: 100%; height: 50px; }
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

df_dojo = carregar_dados()

# --- 3. TÍTULO E NAVEGAÇÃO ---
st.title("📈 DojoNHS - Analisador de Curva de Aprendizado")
st.markdown("---")

tab_cad, tab_analise, tab_dados = st.tabs(["📝 Cadastrar Tempos", "📊 Análise de Curvas", "📂 Gerenciar Base"])

# --- ABA 1: CADASTRO DE TEMPOS ---
with tab_cad:
    st.subheader("Inserir Tempos do Operador (segundos)")
    with st.form("form_dojo", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        operador = c1.text_input("Nome do Operador (Ex: Elias Coelho)")
        t1 = c2.number_input("Amostra 1 (s)", min_value=0.1, step=1.0)
        t2 = c3.number_input("Amostra 2 (s)", min_value=0.1, step=1.0)
        t3 = c4.number_input("Amostra 3 (s)", min_value=0.1, step=1.0)
        
        btn_salvar = st.form_submit_button("💾 SALVAR DADOS DO DOJO")
        
        if btn_salvar and operador and t1 > 0 and t2 > 0 and t3 > 0:
            nova_linha = pd.DataFrame([{"Operador": operador, "Amostra 1": t1, "Amostra 2": t2, "Amostra 3": t3}])
            df_dojo = pd.concat([df_dojo, nova_linha], ignore_index=True)
            df_dojo.to_csv(FILE_DOJO, index=False)
            st.success(f"Dados do operador '{operador}' salvos com sucesso!")
            st.rerun()

# --- ABA 2: ANÁLISE DE CURVAS (ONDE A MÁGICA ACONTECE) ---
with tab_analise:
    if not df_dojo.empty:
        st.subheader("Visualização da Curva de Aprendizado")
        
        # Cria uma lista longa para o gráfico do Plotly
        df_long = pd.melt(df_dojo, id_vars=["Operador"], 
                          value_vars=["Amostra 1", "Amostra 2", "Amostra 3"],
                          var_name="Amostra", value_name="Tempo")
        
        # Converte o nome da amostra em número para o eixo X
        df_long['Num_Amostra'] = df_long['Amostra'].map({"Amostra 1": 1, "Amostra 2": 2, "Amostra 3": 3})

        # --- GERAÇÃO DO GRÁFICO ---
        fig = px.line(df_long, x="Num_Amostra", y="Tempo", color="Operador", 
                     title="Evolução do Tempo por Operador (Dojo)",
                     markers=True, # Adiciona bolinhas nos pontos
                     labels={"Num_Amostra": "Número da Tentativa (Amostra)", "Tempo": "Tempo Total (segundos)"},
                     color_discrete_sequence=px.colors.qualitative.Bold)
        
        # Melhora o visual do gráfico
        fig.update_layout(xaxis=dict(tickmode='linear', dtick=1)) # Força os números 1, 2, 3 no eixo X
        fig.update_traces(line_shape="spline") # Faz as linhas ficarem curvas e suaves

        st.plotly_chart(fig, use_container_width=True)

        # --- ANÁLISE DETALHADA POR OPERADOR ---
        st.divider()
        st.subheader("Análise Individual de Desempenho")
        op_sel = st.selectbox("Selecione o Operador para Análise Profunda:", df_dojo['Operador'].unique())
        
        df_op = df_dojo[df_dojo['Operador'] == op_sel].iloc[0]
        
        # Cálculo da Taxa de Aprendizado (Simples entre Amostra 1 e 3)
        t1, t3 = df_op['Amostra 1'], df_op['Amostra 3']
        melhora_total = ((t1 - t3) / t1) * 100
        
        # Cálculo da Taxa de Aprendizado (Modelo Wright simplificado entre 1 e 2 dobra de experiência)
        t2 = df_op['Amostra 2']
        taxa_wright = (t2 / t1) * 100 # Taxa de aprendizado na primeira dobra

        # Métricas em Destaque
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tempo Inicial (Amostra 1)", f"{t1:.1f}s")
        m2.metric("Tempo Final (Amostra 3)", f"{t3:.1f}s")
        m3.metric("Melhora Total", f"{melhora_total:.1f}%", help="Porcentagem de redução de tempo entre a primeira e terceira tentativa")
        
        # Alerta se houver piora pontual (como você marcou em vermelho na planilha)
        if t2 > t1 or t3 > t2:
            m4.metric("Status de Aprendizado", "Ondulação ⚠️", help="O operador piorou o tempo em alguma tentativa pontual. Requer atenção.")
        else:
            m4.metric("Status de Aprendizado", "Estável ✅", help="O tempo está caindo consistentemente.")

        #st.write(f"**Análise:** O operador {op_sel} demonstra uma melhora de **{melhora_total:.1f}%**. Sua taxa de aprendizado na primeira dobra de experiência foi de **{taxa_wright:.1f}%**. *Projeção:* Se mantiver esse ritmo, estabilizará o tempo por volta da 6ª tentativa.")

    else:
        st.info("Cadastre os tempos na primeira aba para gerar a análise.")

# --- ABA 3: GERENCIAR BASE ---
with tab_dados:
    st.subheader("Base de Dados do Dojo")
    if not df_dojo.empty:
        st.dataframe(df_dojo, use_container_width=True)
        
        # Botão para limpar tudo se necessário (CUIDADO)
        st.divider()
        if st.button("⚠️ APAGAR TODA A BASE DE DADOS DO DOJO"):
            if os.path.exists(FILE_DOJO):
                os.remove(FILE_DOJO)
                st.rerun()
    else:
        st.warning("Nenhum dado cadastrado.")
