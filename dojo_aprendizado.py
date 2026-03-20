import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURAÇÃO ---
FILE_DOJO = "dojo_completo.csv"

def carregar_dados():
    if not os.path.exists(FILE_DOJO):
        return pd.DataFrame(columns=["Operador", "Amostra", "Ativ_1", "Ativ_2", "Ativ_3", "Ativ_4", "Total"])
    return pd.read_csv(FILE_DOJO)

st.set_page_config(page_title="DojoNHS - Analisador Geral", layout="wide")

# --- 2. ESTILO ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #000000 !important; }
    .stButton > button { background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

df_dojo = carregar_dados()

st.title("📈 DojoNHS - Cronoanálise e Curva de Aprendizado")

tab_cad, tab_analise = st.tabs(["📝 Cadastrar Tempos (4 Atividades)", "📊 Análise Geral da Equipe"])

# --- ABA 1: CADASTRO DETALHADO ---
with tab_cad:
    st.subheader("Registrar Cronoanálise do Dojo")
    with st.form("form_dojo", clear_on_submit=True):
        col_op, col_am = st.columns([2, 1])
        nome = col_op.text_input("Nome do Operador")
        amostra = col_am.selectbox("Qual Amostra?", ["Amostra 1", "Amostra 2", "Amostra 3", "Amostra 4", "Amostra 5"])
        
        st.write("Digite os tempos das atividades (segundos):")
        c1, c2, c3, c4 = st.columns(4)
        a1 = c1.number_input("Atividade 1", min_value=0.0, step=1.0)
        a2 = c2.number_input("Atividade 2", min_value=0.0, step=1.0)
        a3 = c3.number_input("Atividade 3", min_value=0.0, step=1.0)
        a4 = c4.number_input("Atividade 4", min_value=0.0, step=1.0)
        
        total_calc = a1 + a2 + a3 + a4
        st.info(f"🟢 **Tempo Total Calculado: {total_calc} segundos**")
        
        btn_salvar = st.form_submit_button("💾 SALVAR CRONOANÁLISE")
        
        if btn_salvar and nome:
            nova_linha = pd.DataFrame([{"Operador": nome, "Amostra": amostra, "Ativ_1": a1, "Ativ_2": a2, "Ativ_3": a3, "Ativ_4": a4, "Total": total_calc}])
            df_dojo = pd.concat([df_dojo, nova_linha], ignore_index=True)
            df_dojo.to_csv(FILE_DOJO, index=False)
            st.success(f"Dados de {nome} salvos!")
            st.rerun()

# --- ABA 2: ANÁLISE GERAL ---
with tab_analise:
    if not df_dojo.empty:
        # --- MÉTRICAS GERAIS ---
        media_geral = df_dojo["Total"].mean()
        melhor_tempo = df_dojo["Total"].min()
        operadores_count = df_dojo["Operador"].nunique()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Média Geral da Equipe", f"{media_geral:.1f}s")
        m2.metric("Melhor Tempo Registrado", f"{melhor_tempo:.1f}s")
        m3.metric("Total de Operadores", operadores_count)
        
        st.divider()
        
        # --- GRÁFICO DE CURVA COLETIVA ---
        st.subheader("Curva de Aprendizado Coletiva")
        # Ordenar amostras para o gráfico não ficar bagunçado
        ordem_am = ["Amostra 1", "Amostra 2", "Amostra 3", "Amostra 4", "Amostra 5"]
        
        fig = px.line(df_dojo, x="Amostra", y="Total", color="Operador", 
                     markers=True, line_shape="spline",
                     category_orders={"Amostra": ordem_am},
                     title="Evolução de Todos os Operadores")
        st.plotly_chart(fig, use_container_width=True)
        
        # --- TABELA DE RESULTADOS GERAIS ---
        st.subheader("Ranking e Comparativo")
        # Criar uma visão onde vemos o primeiro e o último tempo de cada um
        resumo = df_dojo.groupby("Operador").agg(
            Inicio=("Total", "first"),
            Ultimo=("Total", "last"),
            Media=("Total", "mean")
        ).reset_index()
        resumo["Melhora %"] = ((resumo["Inicio"] - resumo["Ultimo"]) / resumo["Inicio"] * 100).round(1)
        
        st.dataframe(resumo.sort_values(by="Melhora %", ascending=False), use_container_width=True)
        
        # Exibir Base de Dados completa embaixo
        with st.expander("Ver Base de Dados Completa"):
            st.write(df_dojo)
            if st.button("Limpar Dados"):
                os.remove(FILE_DOJO)
                st.rerun()
    else:
        st.info("Nenhum dado cadastrado ainda.")
