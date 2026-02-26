import streamlit as st
import sqlite3
import pandas as pd
import base64
from io import BytesIO
from PIL import Image

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Caderno da Marcia", page_icon="👩‍🍳", layout="centered")

# --- FUNÇÕES DO BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('receitas_marcia_fotos.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS receitas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  nome TEXT, categoria TEXT, tempo TEXT, conteudo TEXT, foto TEXT)''')
    conn.commit()
    conn.close()

def salvar_receita(nome, categoria, tempo, conteudo, foto_base64):
    conn = sqlite3.connect('receitas_marcia_fotos.db')
    c = conn.cursor()
    c.execute("INSERT INTO receitas (nome, categoria, tempo, conteudo, foto) VALUES (?, ?, ?, ?, ?)", 
              (nome, categoria, tempo, conteudo, foto_base64))
    conn.commit()
    conn.close()

def atualizar_receita(id_rec, nome, categoria, tempo, conteudo, foto_base64):
    conn = sqlite3.connect('receitas_marcia_fotos.db')
    c = conn.cursor()
    if foto_base64:
        c.execute("""UPDATE receitas SET nome=?, categoria=?, tempo=?, conteudo=?, foto=? 
                     WHERE id=?""", (nome, categoria, tempo, conteudo, foto_base64, id_rec))
    else:
        c.execute("""UPDATE receitas SET nome=?, categoria=?, tempo=?, conteudo=? 
                     WHERE id=?""", (nome, categoria, tempo, conteudo, id_rec))
    conn.commit()
    conn.close()

def excluir_receita(id_rec):
    conn = sqlite3.connect('receitas_marcia_fotos.db')
    c = conn.cursor()
    c.execute("DELETE FROM receitas WHERE id = ?", (id_rec,))
    conn.commit()
    conn.close()

def listar_receitas():
    conn = sqlite3.connect('receitas_marcia_fotos.db')
    df = pd.read_sql_query("SELECT * FROM receitas", conn)
    conn.close()
    return df

def converter_imagem(img_file):
    if img_file:
        img = Image.open(img_file)
        img.thumbnail((500, 500))
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=80)
        return base64.b64encode(buffer.getvalue()).decode()
    return None

init_db()

# --- ESTILO DARK PURPLE & PINK ---
st.markdown("""
    <style>
    /* Fundo Roxo Profundo */
    .stApp { 
        background-color: #0f0a1a; 
        color: #e0d0f0; 
    }
    
    /* CORREÇÃO DE POSICIONAMENTO DO TOPO */
    .block-container {
        padding-top: 4rem !important;
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
    }

    /* Título em Lilás/Rosa Neon */
    .main-title-text { 
        color: #ff79c6; /* Rosa Choque */
        font-family: 'Segoe UI', sans-serif; 
        font-weight: 800; 
        font-size: clamp(1.2rem, 6vw, 1.8rem); 
        text-align: center;
        margin-bottom: 25px;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-shadow: 0px 0px 10px rgba(255, 121, 198, 0.3);
    }
    
    /* Cards Escuros com Borda Lilás */
    .recipe-card {
        background-color: #1a1425; 
        padding: 14px; 
        border-radius: 12px;
        border: 1px solid #3d2b52;
        border-left: 5px solid #bd93f9; /* Lilás */
        margin-bottom: 10px; 
    }
    
    .recipe-card h3 {
        font-size: 16px !important;
        color: #f8f8f2 !important;
        margin: 4px 0 !important;
    }

    /* Botões em Gradiente Roxo/Rosa */
    .stButton>button {
        width: 100%;
        border-radius: 8px !important;
        background: linear-gradient(45deg, #bd93f9, #ff79c6) !important;
        color: #ffffff !important;
        border: none !important;
        height: 45px;
        font-size: 14px;
        font-weight: bold;
        text-transform: uppercase;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }

    /* Campos de Input */
    input, textarea, select {
        background-color: #282a36 !important;
        color: white !important;
        border: 1px solid #44475a !important;
    }
    
    .category-text {
        font-size: 10px; 
        color: #bd93f9; 
        font-weight: bold; 
    }

    footer {display:none !important;}
    #MainMenu {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULO ---
st.markdown('<h1 class="main-title-text">Caderno de Receitas da Marcia</h1>', unsafe_allow_html=True)

# --- CADASTRO ---
with st.expander("💜 ADICIONAR NOVA DELÍCIA", expanded=False):
    nome = st.text_input("Nome")
    c1, c2 = st.columns(2)
    cat = c1.selectbox("Tipo", ["Salgado", "Doce", "Bebida", "Saudável"])
    tempo = c2.text_input("Tempo")
    conteudo = st.text_area("Ingredientes e Preparo", height=150)
    foto_upload = st.file_uploader("Foto", type=['jpg', 'png', 'jpeg'])
    
    if st.button("SALVAR NO CADERNO"):
        if nome and conteudo:
            foto_b64 = converter_imagem(foto_upload)
            salvar_receita(nome, cat, tempo, conteudo, foto_b64)
            st.rerun()

st.divider()

# --- BUSCA ---
df = listar_receitas()
busca = st.text_input("🔍 PESQUISAR...")

if not df.empty:
    # Filtragem
    mask = df['nome'].str.contains(busca, case=False) | df['conteudo'].str.contains(busca, case=False)
    for idx, row in df[mask].iterrows():
        rid = row['id']
        
        st.markdown(f"""<div class="recipe-card">
            <div class="category-text">{row['categoria']} • {row['tempo']}</div>
            <h3>{row['nome']}</h3>
        </div>""", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.expander("VER"):
                if row['foto']:
                    st.image(base64.b64decode(row['foto']), use_container_width=True)
                st.write(row['conteudo'])

        with col2:
            with st.expander("ED"):
                e_nome = st.text_input("Nome", value=row['nome'], key=f"en_{rid}")
                e_cont = st.text_area("Preparo", value=row['conteudo'], height=150, key=f"ect_{rid}")
                e_foto = st.file_uploader("Trocar", type=['jpg', 'png'], key=f"ef_{rid}")
                if st.button("OK", key=f"btn_ed_{rid}"):
                    nova_foto = converter_imagem(e_foto)
                    atualizar_receita(rid, e_nome, row['categoria'], row['tempo'], e_cont, nova_foto)
                    st.rerun()

        with col3:
            with st.expander("EX"):
                if st.button("SIM", key=f"del_{rid}"):
                    excluir_receita(rid)
                    st.rerun()
else:
    st.info("Vazio.")
