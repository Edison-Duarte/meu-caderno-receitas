import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="King Snake Recipes", page_icon="🐍", layout="centered")

# --- FUNÇÕES DO BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('receitas_king.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS receitas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  nome TEXT, categoria TEXT, tempo TEXT, conteudo TEXT)''')
    conn.commit()
    conn.close()

def salvar_receita(nome, categoria, tempo, conteudo):
    conn = sqlite3.connect('receitas_king.db')
    c = conn.cursor()
    c.execute("INSERT INTO receitas (nome, categoria, tempo, conteudo) VALUES (?, ?, ?, ?)", 
              (nome, categoria, tempo, conteudo))
    conn.commit()
    conn.close()

def atualizar_receita(id_rec, nome, categoria, tempo, conteudo):
    conn = sqlite3.connect('receitas_king.db')
    c = conn.cursor()
    c.execute("""UPDATE receitas SET nome=?, categoria=?, tempo=?, conteudo=? 
                 WHERE id=?""", (nome, categoria, tempo, conteudo, id_rec))
    conn.commit()
    conn.close()

def excluir_receita(id_rec):
    conn = sqlite3.connect('receitas_king.db')
    c = conn.cursor()
    c.execute("DELETE FROM receitas WHERE id = ?", (id_rec,))
    conn.commit()
    conn.close()

def listar_receitas():
    conn = sqlite3.connect('receitas_king.db')
    df = pd.read_sql_query("SELECT * FROM receitas", conn)
    conn.close()
    return df

init_db()

# --- ESTILO VISUAL "KING SNAKE" ---
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #e0e0e0; }
    .stApp { background-color: #0d1117; }
    h1 { color: #2ecc71 !important; font-family: 'Georgia', serif; text-align: center; }
    .recipe-card {
        padding: 15px; border-radius: 12px; background-color: #161b22;
        border: 1px solid #2ecc71; margin-bottom: 5px;
    }
    .stButton>button { border-radius: 5px; font-weight: bold; }
    /* Cor do botão salvar */
    div.stButton > button:first-child { background-color: #2ecc71; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULO ---
st.markdown("<h1>Caderno de Receitas KING SNAKE 🐍</h1>", unsafe_allow_html=True)
st.write("---")

# --- CADASTRO ---
with st.expander("➕ Adicionar Nova Presa (Receita)", expanded=False):
    n_nome = st.text_input("Nome da Receita")
    c1, c2 = st.columns(2)
    n_cat = c1.selectbox("Estilo", ["Salgado", "Doce", "Bebida", "Veneno (Drinks)"])
    n_tmp = c2.text_input("Tempo de Preparo")
    n_cont = st.text_area("Ingredientes e Modo de Preparo (Ctrl+C / Ctrl+V)", height=150)
    
    if st.button("💾 Guardar no Ninho"):
        if n_nome and n_cont:
            salvar_receita(n_nome, n_cat, n_tmp, n_cont)
            st.success("Receita capturada!")
            st.rerun()

# --- BUSCA E LISTAGEM ---
df = listar_receitas()
busca = st.text_input("🔍 Rastrear receita...", placeholder="Digite o nome ou ingrediente")

if not df.empty:
    # Filtro de busca
    mask = df['nome'].str.contains(busca, case=False) | df['conteudo'].str.contains(busca, case=False)
    for idx, row in df[mask].iterrows():
        rid = row['id']
        
        st.markdown(f"""
        <div class="recipe-card">
            <h3 style='margin:0; color:#2ecc71;'>🐍 {row['nome']}</h3>
            <small><b>{row['categoria']}</b> | ⏳ {row['tempo']}</small>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        
        # VER
        with col1.expander("📖 Ver"):
            st.write(row['conteudo'])
            txt_data = f"KING SNAKE RECIPES - {row['nome']}\n\n{row['conteudo']}"
            st.download_button("📥 Baixar TXT", txt_data, f"{row['nome']}.txt", key=f"dl_{rid}")

        # EDITAR
        with col2.expander("✏️ Editar"):
            e_nome = st.text_input("Nome", value=row['nome'], key=f"en_{rid}")
            e_cat = st.selectbox("Cat", ["Salgado", "Doce", "Bebida", "Veneno (Drinks)"], 
                                index=["Salgado", "Doce", "Bebida", "Veneno (Drinks)"].index(row['categoria']), 
                                key=f"ec_{rid}")
            e_tmp = st.text_input("Tempo", value=row['tempo'], key=f"et_{rid}")
            e_cont = st.text_area("Preparo", value=row['conteudo'], height=200, key=f"ect_{rid}")
            
            if st.button("✅ Atualizar", key=f"btn_ed_{rid}"):
                atualizar_receita(rid, e_nome, e_cat, e_tmp, e_cont)
                st.rerun()

        # EXCLUIR
        with col3.expander("🗑️ Excluir"):
            if st.button("Confirmar Morte", key=f"del_{rid}"):
                excluir_receita(rid)
                st.rerun()
        st.write("") 
else:
    st.info("O ninho está vazio. Adicione sua primeira receita!")
