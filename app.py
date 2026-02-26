import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Caderno da Marcia", page_icon="🍳", layout="centered")

# --- FUNÇÕES DO BANCO DE DADOS (SQLite) ---
def init_db():
    conn = sqlite3.connect('receitas_marcia.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS receitas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  nome TEXT, categoria TEXT, tempo TEXT, conteudo TEXT)''')
    conn.commit()
    conn.close()

def salvar_receita(nome, categoria, tempo, conteudo):
    conn = sqlite3.connect('receitas_marcia.db')
    c = conn.cursor()
    c.execute("INSERT INTO receitas (nome, categoria, tempo, conteudo) VALUES (?, ?, ?, ?)", 
              (nome, categoria, tempo, conteudo))
    conn.commit()
    conn.close()

def atualizar_receita(id_rec, nome, categoria, tempo, conteudo):
    conn = sqlite3.connect('receitas_marcia.db')
    c = conn.cursor()
    c.execute("""UPDATE receitas SET nome=?, categoria=?, tempo=?, conteudo=? 
                 WHERE id=?""", (nome, categoria, tempo, conteudo, id_rec))
    conn.commit()
    conn.close()

def excluir_receita(id_rec):
    conn = sqlite3.connect('receitas_marcia.db')
    c = conn.cursor()
    c.execute("DELETE FROM receitas WHERE id = ?", (id_rec,))
    conn.commit()
    conn.close()

def listar_receitas():
    conn = sqlite3.connect('receitas_marcia.db')
    df = pd.read_sql_query("SELECT * FROM receitas", conn)
    conn.close()
    return df

init_db()

# --- ESTILO VISUAL AMIGÁVEL ---
st.markdown("""
    <style>
    .main { background-color: #fdfcfb; }
    h1 { color: #d35400 !important; text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .recipe-card {
        padding: 20px; border-radius: 15px; background-color: #ffffff;
        border-left: 6px solid #e67e22; margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .stButton>button { border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULO ---
st.markdown("<h1>Caderno de Receitas da Marcia</h1>", unsafe_allow_html=True)
st.write("---")

# --- CADASTRO ---
with st.expander("➕ Adicionar Nova Receita", expanded=False):
    n_nome = st.text_input("Nome da Receita")
    c1, c2 = st.columns(2)
    n_cat = c1.selectbox("Categoria", ["Salgado", "Doce", "Bebida", "Saudável"])
    n_tmp = c2.text_input("Tempo de Preparo")
    n_cont = st.text_area("Ingredientes e Modo de Preparo (Pode usar Ctrl+V)", height=200)
    
    if st.button("💾 Salvar no Caderno"):
        if n_nome and n_cont:
            salvar_receita(n_nome, n_cat, n_tmp, n_cont)
            st.success("Receita salva com sucesso!")
            st.rerun()

st.divider()

# --- BUSCA E LISTAGEM ---
df = listar_receitas()
busca = st.text_input("🔍 O que você está procurando hoje?", placeholder="Ex: Bolo, frango, chocolate...")

if not df.empty:
    mask = df['nome'].str.contains(busca, case=False) | df['conteudo'].str.contains(busca, case=False)
    for idx, row in df[mask].iterrows():
        rid = row['id']
        
        st.markdown(f"""
        <div class="recipe-card">
            <h3 style='margin:0; color:#d35400;'>🍴 {row['nome']}</h3>
            <span style='color: #7f8c8d;'>{row['categoria']} | ⏳ {row['tempo']}</span>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        
        with col1.expander("📖 Ler"):
            st.write(row['conteudo'])
            txt_data = f"RECEITA: {row['nome']}\n\n{row['conteudo']}"
            st.download_button("📥 Baixar", txt_data, f"{row['nome']}.txt", key=f"dl_{rid}")

        with col2.expander("✏️ Editar"):
            e_nome = st.text_input("Nome", value=row['nome'], key=f"en_{rid}")
            e_cat = st.selectbox("Cat", ["Salgado", "Doce", "Bebida", "Saudável"], 
                                index=["Salgado", "Doce", "Bebida", "Saudável"].index(row['categoria']), 
                                key=f"ec_{rid}")
            e_tmp = st.text_input("Tempo", value=row['tempo'], key=f"et_{rid}")
            e_cont = st.text_area("Preparo", value=row['conteudo'], height=200, key=f"ect_{rid}")
            
            if st.button("✅ Salvar Alteração", key=f"btn_ed_{rid}"):
                atualizar_receita(rid, e_nome, e_cat, e_tmp, e_cont)
                st.rerun()

        with col3.expander("🗑️ Excluir"):
            if st.button("Confirmar Exclusão", key=f"del_{rid}"):
                excluir_receita(rid)
                st.rerun()
else:
    st.info("O seu caderno ainda está vazio. Adicione uma receita acima!")
