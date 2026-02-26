import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chef Digital Permanente", page_icon="📖", layout="centered")

# --- FUNÇÕES DO BANCO DE DADOS (SQLite) ---
def init_db():
    conn = sqlite3.connect('receitas.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS receitas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  nome TEXT, categoria TEXT, tempo TEXT, conteudo TEXT)''')
    conn.commit()
    conn.close()

def salvar_receita(nome, categoria, tempo, conteudo):
    conn = sqlite3.connect('receitas.db')
    c = conn.cursor()
    c.execute("INSERT INTO receitas (nome, categoria, tempo, conteudo) VALUES (?, ?, ?, ?)", 
              (nome, categoria, tempo, conteudo))
    conn.commit()
    conn.close()

def listar_receitas():
    conn = sqlite3.connect('receitas.db')
    df = pd.read_sql_query("SELECT * FROM receitas", conn)
    conn.close()
    return df

# NOVA FUNÇÃO: Excluir uma receita específica
def excluir_receita(id_receita):
    conn = sqlite3.connect('receitas.db')
    c = conn.cursor()
    c.execute("DELETE FROM receitas WHERE id = ?", (id_receita,))
    conn.commit()
    conn.close()

def excluir_todas():
    conn = sqlite3.connect('receitas.db')
    c = conn.cursor()
    c.execute("DELETE FROM receitas")
    conn.commit()
    conn.close()

# Inicializa o banco
init_db()

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .main { background-color: #fffaf0; }
    .recipe-box {
        padding: 20px;
        border-radius: 15px;
        background-color: #ffffff;
        border: 2px solid #ffccbc;
        margin-bottom: 10px;
    }
    /* Estilo para o botão de excluir ficar discreto e vermelho */
    .stButton>button[key^="del_"] {
        color: #d32f2f;
        border-color: #d32f2f;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Meu Livro de Receitas Eterno")

# --- SIDEBAR ---
with st.sidebar:
    st.header("📊 Acervo")
    df_atual = listar_receitas()
    st.metric("Total", len(df_atual))
    if st.button("🚨 Apagar Tudo"):
        excluir_todas()
        st.rerun()

# --- CADASTRO ---
with st.expander("➕ Adicionar Nova Receita", expanded=False):
    nome = st.text_input("Nome do Prato")
    c1, c2 = st.columns(2)
    cat = c1.selectbox("Categoria", ["Salgado", "Doce", "Bebida", "Fit"])
    tmp = c2.text_input("Tempo", placeholder="Ex: 15 min")
    cont = st.text_area("Ingredientes e Modo de Preparo", height=150)
    
    if st.button("💾 Salvar"):
        if nome and cont:
            salvar_receita(nome, cat, tmp, cont)
            st.success("Salvo!")
            st.rerun()

st.divider()

# --- BUSCA E EXIBIÇÃO ---
busca = st.text_input("🔍 Procurar receita...")

if not df_atual.empty:
    mask = df_atual['nome'].str.contains(busca, case=False) | df_atual['conteudo'].str.contains(busca, case=False)
    resultados = df_atual[mask]

    for index, row in resultados.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="recipe-box">
                <h3 style='color: #e64a19; margin-top:0;'>🍴 {row['nome']}</h3>
                <small>{row['categoria']} | ⏱️ {row['tempo']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Dentro do expander colocamos as opções de ver, baixar e EXCLUIR
            with st.expander("📖 Detalhes e Opções"):
                st.write(row['conteudo'])
                
                col_btn1, col_btn2 = st.columns([1, 1])
                
                # Botão de Download
                txt_data = f"RECEITA: {row['nome']}\n\n{row['conteudo']}"
                col_btn1.download_button(
                    label="📥 Baixar TXT",
                    data=txt_data,
                    file_name=f"{row['nome']}.txt",
                    key=f"dl_{row['id']}"
                )
                
                # BOTÃO DE EXCLUIR INDIVIDUAL
                if col_btn2.button(f"🗑️ Excluir Receita", key=f"del_{row['id']}"):
                    excluir_receita(row['id'])
                    st.toast(f"'{row['nome']}' removida!")
                    st.rerun()
else:
    st.info("Nenhuma receita encontrada.")
