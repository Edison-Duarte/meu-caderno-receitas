import streamlit as st
import sqlite3
import pandas as pd
import base64
from io import BytesIO
from PIL import Image

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Caderno da Marcia", page_icon="👩‍🍳", layout="centered")

# --- FUNÇÕES DO BANCO DE DATAS ---
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
        # Redimensiona para não pesar no banco de dados
        img.thumbnail((800, 800))
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=70)
        return base64.b64encode(buffer.getvalue()).decode()
    return None

init_db()

# --- ESTILO VISUAL OTIMIZADO PARA MOBILE ---
st.markdown("""
    <style>
    .stApp { background-color: #ffe4e1; }
    
    /* Título Responsivo */
    .main-title-text { 
        color: #4a4a4a; 
        font-family: 'Segoe UI', sans-serif; 
        font-weight: 800; 
        font-size: clamp(1.5rem, 6vw, 2.5rem); /* Ajusta conforme o tamanho da tela */
        text-align: center;
        width: 100%;
        margin: 15px 0;
        white-space: nowrap;
    }
    
    /* Cards Ajustados */
    .recipe-card {
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 12px;
        border-left: 6px solid #d1478a; 
        margin-bottom: 8px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Botões mais fáceis de tocar */
    .stButton>button {
        width: 100%;
        border-radius: 8px !important;
        background-color: #d1478a !important;
        color: white !important;
        height: 45px;
        font-size: 16px;
    }

    /* Ajuste de inputs para mobile */
    .stTextInput>div>div>input {
        font-size: 16px !important; /* Evita zoom automático no iOS */
    }

    /* Esconde menu padrão do streamlit para ganhar espaço */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULO ---
st.markdown('<h1 class="main-title-text">Caderno de Receitas da Marcia</h1>', unsafe_allow_html=True)

# --- CADASTRO ---
with st.expander("📥 Adicionar Nova Receita", expanded=False):
    nome = st.text_input("Nome da Receita")
    cat = st.selectbox("Categoria", ["Salgado", "Doce", "Bebida", "Saudável"])
    tempo = st.text_input("Tempo de Preparo")
    conteudo = st.text_area("Ingredientes e Preparo", height=150)
    foto_upload = st.file_uploader("Foto (JPG/PNG)", type=['jpg', 'png', 'jpeg'])
    
    if st.button("Salvar no Caderno"):
        if nome and conteudo:
            foto_b64 = converter_imagem(foto_upload)
            salvar_receita(nome, cat, tempo, conteudo, foto_b64)
            st.success("Salva!")
            st.rerun()

st.divider()

# --- BUSCA ---
df = listar_receitas()
busca = st.text_input("🔍 Procurar receita...")

if not df.empty:
    mask = df['nome'].str.contains(busca, case=False) | df['conteudo'].str.contains(busca, case=False)
    for idx, row in df[mask].iterrows():
        rid = row['id']
        
        st.markdown(f"""<div class="recipe-card">
            <span style='font-size:10px; font-weight:bold; color:#d1478a; text-transform:uppercase;'>{row['categoria']}</span>
            <h3 style='margin: 4px 0; color: #333; font-size: 18px;'>{row['nome']}</h3>
            <p style='color: #888; font-size: 12px; margin: 0;'>⏱ {row['tempo']}</p>
        </div>""", unsafe_allow_html=True)

        # Ações em colunas para mobile
        c1, c2, c3 = st.columns(3)
        
        with c1.expander("📄 Ver"):
            if row['foto']:
                st.image(base64.b64decode(row['foto']), use_container_width=True)
            st.write(row['conteudo'])

        with c2.expander("⚙️ Ed"):
            e_nome = st.text_input("Nome", value=row['nome'], key=f"en_{rid}")
            e_cont = st.text_area("Preparo", value=row['conteudo'], height=150, key=f"ect_{rid}")
            e_foto = st.file_uploader("Trocar foto", type=['jpg', 'png'], key=f"ef_{rid}")
            if st.button("Salvar", key=f"btn_ed_{rid}"):
                nova_foto = converter_imagem(e_foto)
                atualizar_receita(rid, e_nome, row['categoria'], row['tempo'], e_cont, nova_foto)
                st.rerun()

        with c3.expander("❌ Ex"):
            if st.button("Apagar", key=f"del_{rid}"):
                excluir_receita(rid)
                st.rerun()
else:
    st.info("Caderno vazio.")
