import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Caderno da Marcia", page_icon="👩‍🍳", layout="centered")

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

# --- ESTILO VISUAL "COZINHA DA MARCIA" ---
st.markdown("""
    <style>
    /* Fundo da página */
    .stApp {
        background: linear-gradient(to bottom, #fff0f5, #ffe4e1);
    }
    
    /* Título com fonte elegante */
    h1 { 
        color: #d147a3 !important; 
        font-family: 'Dancing Script', cursive; 
        font-size: 3rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        padding-bottom: 20px;
    }

    /* Estilo dos Cards de Receita */
    .recipe-card {
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        border: none;
        box-shadow: 0 10px 25px rgba(255, 182, 193, 0.4);
        margin-bottom: 20px;
        transition: transform 0.3s;
    }
    
    /* Botões */
    .stButton>button {
        border-radius: 30px !important;
        background-color: #ff69b4 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 2rem !important;
        font-weight: bold;
    }
    
    /* Input de texto */
    .stTextInput>div>div>input {
        border-radius: 15px;
        border: 2px solid #ffb6c1;
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown("<h1>Caderno de Receitas da Marcia</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #b03060;'>💖 Onde cada ingrediente vira amor!</p>", unsafe_allow_html=True)

# --- ÁREA DE CADASTRO ---
with st.expander("✨ Registrar Nova Receita Mágica", expanded=False):
    nome = st.text_input("Nome da Delícia")
    col1, col2 = st.columns(2)
    cat = col1.selectbox("Tipo", ["🍰 Doce", "🍝 Salgado", "🍹 Bebida", "🥗 Saudável"])
    tempo = col2.text_input("🕒 Tempo (ex: 45 min)")
    conteudo = st.text_area("📖 Modo de Preparo e Ingredientes (Ctrl+V liberado!)", height=150)
    
    if st.button("💝 Guardar no Caderno"):
        if nome and conteudo:
            salvar_receita(nome, cat, tempo, conteudo)
            st.toast("Receita salva com sucesso! 🎉")
            st.rerun()

st.write("---")

# --- BUSCA ---
df = listar_receitas()
busca = st.text_input("🔍 Procurar um sabor especial...", placeholder="Ex: Chocolate, Lasanha...")

# --- EXIBIÇÃO ---
if not df.empty:
    mask = df['nome'].str.contains(busca, case=False) | df['conteudo'].str.contains(busca, case=False)
    for idx, row in df[mask].iterrows():
        rid = row['id']
        
        # Card Visual
        st.markdown(f"""
        <div class="recipe-card">
            <h2 style='margin:0; color:#d147a3;'>{row['nome']}</h2>
            <p style='color:#7f8c8d; font-size:14px;'>{row['categoria']} • ⏳ {row['tempo']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Ações
        c1, c2, c3 = st.columns(3)
        
        with c1.expander("👀 Ver Detalhes"):
            st.markdown(f"### 👩‍🍳 Como fazer:")
            st.write(row['conteudo'])
            st.download_button("📂 Baixar Receita", f"RECEITA: {row['nome']}\n\n{row['conteudo']}", f"{row['nome']}.txt", key=f"dl_{rid}")

        with c2.expander("✏️ Editar"):
            e_nome = st.text_input("Editar Nome", value=row['nome'], key=f"en_{rid}")
            e_cat = st.selectbox("Mudar Tipo", ["🍰 Doce", "🍝 Salgado", "🍹 Bebida", "🥗 Saudável"], 
                                index=["🍰 Doce", "🍝 Salgado", "🍹 Bebida", "🥗 Saudável"].index(row['categoria']), 
                                key=f"ec_{rid}")
            e_tmp = st.text_input("Mudar Tempo", value=row['tempo'], key=f"et_{rid}")
            e_cont = st.text_area("Mudar Preparo", value=row['conteudo'], height=200, key=f"ect_{rid}")
            if st.button("💾 Atualizar", key=f"btn_ed_{rid}"):
                atualizar_receita(rid, e_nome, e_cat, e_tmp, e_cont)
                st.rerun()

        with c3.expander("🗑️ Remover"):
            st.write("Deseja apagar esta receita?")
            if st.button("⚠️ Confirmar", key=f"del_{rid}"):
                excluir_receita(rid)
                st.rerun()
        st.write("") 
else:
    st.info("Ainda não há receitas. Comece colando uma ali em cima! 🌸")
