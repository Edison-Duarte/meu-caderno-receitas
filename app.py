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
        img.thumbnail((500, 500)) # Imagem menor para mobile
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=60)
        return base64.b64encode(buffer.getvalue()).decode()
    return None

init_db()

# --- ESTILO VISUAL ULTRA COMPACTO PARA MOBILE ---
st.markdown("""
    <style>
    .stApp { background-color: #ffe4e1; }
    
    /* Título que se ajusta ao celular */
    .main-title-text { 
        color: #4a4a4a; 
        font-family: sans-serif; 
        font-weight: 800; 
        font-size: clamp(1.2rem, 5vw, 2.2rem); 
        text-align: center;
        width: 100%;
        margin: 10px 0;
        line-height: 1.2;
    }
    
    /* Remove espaços excessivos do Streamlit no Mobile */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* Cards super compactos */
    .recipe-card {
        background-color: #ffffff; 
        padding: 12px; 
        border-radius: 8px;
        border-left: 4px solid #d1478a; 
        margin-bottom: 5px; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .recipe-card h3 {
        font-size: 16px !important;
        margin: 0 !important;
    }

    /* Botões otimizados para toque */
    .stButton>button {
        width: 100%;
        border-radius: 6px !important;
        background-color: #d1478a !important;
        height: 40px;
        font-size: 14px;
        margin-top: 5px;
    }

    /* Ajuste de Expander para não ocupar tanto espaço */
    .streamlit-expanderHeader {
        font-size: 14px !important;
        padding: 5px 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULO ---
st.markdown('<h1 class="main-title-text">Caderno de Receitas da Marcia</h1>', unsafe_allow_html=True)

# --- CADASTRO ---
with st.expander("➕ Nova Receita", expanded=False):
    nome = st.text_input("Nome")
    cat = st.selectbox("Cat", ["Salgado", "Doce", "Bebida", "Saudável"])
    tempo = st.text_input("Tempo")
    conteudo = st.text_area("Preparo", height=120)
    foto_upload = st.file_uploader("Foto", type=['jpg', 'png', 'jpeg'])
    
    if st.button("Salvar Receita"):
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
            <div style='font-size:9px; color:#d1478a; font-weight:bold;'>{row['categoria']} • {row['tempo']}</div>
            <h3>{row['nome']}</h3>
        </div>""", unsafe_allow_html=True)

        # Botões de ação simplificados
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.expander("📄 Ver"):
                if row['foto']:
                    st.image(base64.b64decode(row['foto']), use_container_width=True)
                st.write(row['conteudo'])

        with col2:
            with st.expander("✏️ Ed"):
                e_nome = st.text_input("Nome", value=row['nome'], key=f"en_{rid}")
                e_cont = st.text_area("Preparo", value=row['conteudo'], height=150, key=f"ect_{rid}")
                e_foto = st.file_uploader("Foto", type=['jpg', 'png'], key=f"ef_{rid}")
                if st.button("OK", key=f"btn_ed_{rid}"):
                    nova_foto = converter_imagem(e_foto)
                    atualizar_receita(rid, e_nome, row['categoria'], row['tempo'], e_cont, nova_foto)
                    st.rerun()

        with col3:
            with st.expander("🗑️ Ex"):
                if st.button("Apagar", key=f"del_{rid}"):
                    excluir_receita(rid)
                    st.rerun()
else:
    st.info("Vazio.")
