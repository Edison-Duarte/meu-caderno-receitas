import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Caderno da Marcia", page_icon="📝", layout="centered")

# --- FUNÇÕES DO BANCO DE DADOS ---
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

# --- ESTILO VISUAL EQUILIBRADO (Rosa + Neutro) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #ffe4e1; /* O rosa que você gostou */
    }
    
    h1 { 
        color: #4a4a4a !important; 
        font-family: 'Segoe UI', sans-serif;
        font-weight: 800;
        text-align: center;
    }

    .recipe-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 6px solid #d1478a; 
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .stButton>button {
        border-radius: 5px !important;
        background-color: #d1478a !important;
        color: white !important;
        border: none !important;
    }

    .category-badge {
        background-color: #f0f0f0;
        color: #555;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown("<h1>Caderno de Receitas da Marcia</h1>", unsafe_allow_html=True)

# --- CADASTRO ---
with st.expander("📥 Cadastrar Nova Receita", expanded=False):
    nome = st.text_input("Nome da Receita")
    col1, col2 = st.columns(2)
    cat = col1.selectbox("Categoria", ["Salgado", "Doce", "Bebida", "Saudável"])
    tempo = col2.text_input("Tempo de Preparo")
    conteudo = st.text_area("Ingredientes e Modo de Preparo", height=150)
    
    if st.button("Salvar no Caderno"):
        if nome and conteudo:
            salvar_receita(nome, cat, tempo, conteudo)
            st.rerun()

st.write("---")

# --- BUSCA ---
df = listar_receitas()
busca = st.text_input("🔍 Pesquisar receitas...", placeholder="Busque por nome ou ingrediente")

# --- LISTAGEM ---
if not df.empty:
    mask = df['nome'].str.contains(busca, case=False) | df['conteudo'].str.contains(busca, case=False)
    for idx, row in df[mask].iterrows():
        rid = row['id']
        
        # Card com visual limpo
        st.markdown(f"""
        <div class="recipe-card">
            <span class="category-badge">{row['categoria']}</span>
            <h3 style='margin: 10px 0 5px 0; color: #333;'>{row['nome']}</h3>
            <p style='color: #777; font-size: 14px; margin: 0;'>⏱ {row['tempo']}</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        
        with c1.expander("📄 Ver"):
            st.write(row['conteudo'])
            st.download_button("Exportar TXT", f"{row['nome']}\n\n{row['conteudo']}", f"{row['nome']}.txt", key=f"dl_{rid}")

        with c2.expander("⚙️ Editar"):
            e_nome = st.text_input("Nome", value=row['nome'], key=f"en_{rid}")
            e_cat = st.selectbox("Categoria", ["Salgado", "Doce", "Bebida", "Saudável"], 
                                index=["Salgado", "Doce", "Bebida", "Saudável"].index(row['categoria']), 
                                key=f"ec_{rid}")
            e_tmp = st.text_input("Tempo", value=row['tempo'], key=f"et_{rid}")
            e_cont = st.text_area("Preparo", value=row['conteudo'], height=200, key=f"ect_{rid}")
            if st.button("Atualizar", key=f"btn_ed_{rid}"):
                atualizar_receita(rid, e_nome, e_cat, e_tmp, e_cont)
                st.rerun()

        with c3.expander("❌ Excluir"):
            if st.button("Remover", key=f"del_{rid}"):
                excluir_receita(rid)
                st.rerun()
        st.write("") 
else:
    st.info("Nenhuma receita cadastrada.")
