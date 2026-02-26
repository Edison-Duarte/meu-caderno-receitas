import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chef Digital 3.0", page_icon="🥘", layout="centered")

# --- FUNÇÕES DO BANCO DE DADOS ---
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

def atualizar_receita(id_rec, nome, categoria, tempo, conteudo):
    conn = sqlite3.connect('receitas.db')
    c = conn.cursor()
    c.execute("""UPDATE receitas SET nome=?, categoria=?, tempo=?, conteudo=? 
                 WHERE id=?""", (nome, categoria, tempo, conteudo, id_rec))
    conn.commit()
    conn.close()

def excluir_receita(id_rec):
    conn = sqlite3.connect('receitas.db')
    c = conn.cursor()
    c.execute("DELETE FROM receitas WHERE id = ?", (id_rec,))
    conn.commit()
    conn.close()

def listar_receitas():
    conn = sqlite3.connect('receitas.db')
    df = pd.read_sql_query("SELECT * FROM receitas", conn)
    conn.close()
    return df

init_db()

# --- ESTILO ---
st.markdown("""
    <style>
    .main { background-color: #fffaf0; }
    .recipe-box {
        padding: 15px; border-radius: 12px; background-color: white;
        border: 2px solid #ffd180; margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Livro de Receitas Inteligente")

# --- CADASTRO ---
with st.expander("➕ Nova Receita", expanded=False):
    n_nome = st.text_input("Nome")
    c1, c2 = st.columns(2)
    n_cat = c1.selectbox("Categoria", ["Salgado", "Doce", "Bebida", "Fit"], key="new_cat")
    n_tmp = c2.text_input("Tempo", key="new_time")
    n_cont = st.text_area("Preparo", height=150, key="new_cont")
    
    if st.button("💾 Salvar Nova"):
        if n_nome and n_cont:
            salvar_receita(n_nome, n_cat, n_tmp, n_cont)
            st.rerun()

st.divider()

# --- BUSCA E LISTAGEM ---
df = listar_receitas()
busca = st.text_input("🔍 Buscar no caderno...", placeholder="Ex: Lasanha")

if not df.empty:
    mask = df['nome'].str.contains(busca, case=False) | df['conteudo'].str.contains(busca, case=False)
    for idx, row in df[mask].iterrows():
        rid = row['id']
        
        st.markdown(f"""
        <div class="recipe-box">
            <h3 style='margin:0; color:#e65100;'>🍴 {row['nome']}</h3>
            <small><b>{row['categoria']}</b> | ⏳ {row['tempo']}</small>
        </div>
        """, unsafe_allow_html=True)

        # Ações da Receita
        col1, col2, col3 = st.columns(3)
        
        # 1. VER DETALHES
        with col1.expander("📖 Ver"):
            st.write(row['conteudo'])

        # 2. EDITAR
        with col2.expander("✏️ Editar"):
            edit_nome = st.text_input("Nome", value=row['nome'], key=f"en_{rid}")
            edit_cat = st.selectbox("Cat", ["Salgado", "Doce", "Bebida", "Fit"], 
                                    index=["Salgado", "Doce", "Bebida", "Fit"].index(row['categoria']), 
                                    key=f"ec_{rid}")
            edit_tmp = st.text_input("Tempo", value=row['tempo'], key=f"et_{rid}")
            edit_cont = st.text_area("Preparo", value=row['conteudo'], height=200, key=f"ect_{rid}")
            
            if st.button("✅ Confirmar Alteração", key=f"btn_ed_{rid}"):
                atualizar_receita(rid, edit_nome, edit_cat, edit_tmp, edit_cont)
                st.success("Atualizado!")
                st.rerun()

        # 3. EXCLUIR
        with col3.expander("🗑️ Excluir"):
            st.warning("Tem certeza?")
            if st.button("Sim, apagar", key=f"del_{rid}"):
                excluir_receita(rid)
                st.rerun()
        st.divider()
else:
    st.info("Caderno vazio.")
