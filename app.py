import streamlit as st
import sqlite3
import pandas as pd
import base64
from io import BytesIO
from PIL import Image

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Caderno da Marcia", page_icon="🍲", layout="centered")

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
        img.save(buffer, format="JPEG", quality=60)
        return base64.b64encode(buffer.getvalue()).decode()
    return None

init_db()

# --- ESTILO VISUAL "LINHO & OLIVA" (NEUTRO E SOFISTICADO) ---
st.markdown("""
    <style>
    /* Fundo creme/linho */
    .stApp { background-color: #Fdfbf7; }
    
    /* Título em Grafite */
    .main-title-text { 
        color: #333d29; 
        font-family: 'serif'; 
        font-weight: 700; 
        font-size: clamp(1.1rem, 5vw, 1.8rem); 
        text-align: center;
        width: 100%;
        margin: 10px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
    }

    /* Cards Brancos com borda Oliva */
    .recipe-card {
        background-color: #ffffff; 
        padding: 10px 14px; 
        border-radius: 4px;
        border: 1px solid #e0e0e0;
        border-left: 4px solid #6b705c; /* Verde Oliva */
        margin-bottom: 6px; 
    }
    
    .recipe-card h3 {
        font-size: 15px !important;
        color: #333d29 !important;
        margin: 0 !important;
    }

    /* Botões Oliva */
    .stButton>button {
        width: 100%;
        border-radius: 4px !important;
        background-color: #6b705c !important;
        color: #ffffff !important;
        border: none !important;
        height: 38px;
        font-size: 13px;
        text-transform: uppercase;
    }

    /* Inputs neutros */
    .stTextInput>div>div>input {
        background-color: #ffffff !important;
        border: 1px solid #dcdcdc !important;
    }
    
    .category-text {
        font-size: 9px; 
        color: #6b705c; 
        font-weight: bold; 
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULO ---
st.markdown('<h1 class="main-title-text">Caderno de Receitas da Marcia</h1>', unsafe_allow_html=True)

# --- CADASTRO ---
with st.expander("📝 Nova Receita", expanded=False):
    nome = st.text_input("Título")
    cat = st.selectbox("Categoria", ["Salgado", "Doce", "Bebida", "Saudável"])
    tempo = st.text_input("Tempo")
    conteudo = st.text_area("Modo de Preparo", height=120)
    foto_upload = st.file_uploader("Foto", type=['jpg', 'png', 'jpeg'])
    
    if st.button("Salvar"):
        if nome and conteudo:
            foto_b64 = converter_imagem(foto_upload)
            salvar_receita(nome, cat, tempo, conteudo, foto_b64)
            st.rerun()

st.divider()

# --- BUSCA ---
df = listar_receitas()
busca = st.text_input("🔍 Buscar...")

if not df.empty:
    mask = df['nome'].str.contains(busca, case=False) | df['conteudo'].str.contains(busca, case=False)
    for idx, row in df[mask].iterrows():
        rid = row['id']
        
        st.markdown(f"""<div class="recipe-card">
            <div class="category-text">{row['categoria']} • {row['tempo']}</div>
            <h3>{row['nome']}</h3>
        </div>""", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.expander("Ler"):
                if row['foto']:
                    st.image(base64.b64decode(row['foto']), use_container_width=True)
                st.write(row['conteudo'])

        with col2:
            with st.expander("Ed"):
                e_nome = st.text_input("Título", value=row['nome'], key=f"en_{rid}")
                e_cont = st.text_area("Preparo", value=row['conteudo'], height=150, key=f"ect_{rid}")
                e_foto = st.file_uploader("Foto", type=['jpg', 'png'], key=f"ef_{rid}")
                if st.button("Ok", key=f"btn_ed_{rid}"):
                    nova_foto = converter_imagem(e_foto)
                    atualizar_receita(rid, e_nome, row['categoria'], row['tempo'], e_cont, nova_foto)
                    st.rerun()

        with col3:
            with st.expander("Ex"):
                if st.button("S", key=f"del_{rid}"):
                    excluir_receita(rid)
                    st.rerun()
else:
    st.info("Vazio.")
