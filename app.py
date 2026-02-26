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
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()
    return None

init_db()

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #ffe4e1; }
    
    /* Centralização absoluta do título */
    .main-title-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        gap: 15px;
        margin-top: 10px;
        margin-bottom: 25px;
    }
    
    .main-title-text { 
        color: #4a4a4a; 
        font-family: sans-serif; 
        font-weight: 800; 
        font-size: 2.2rem;
        margin: 0;
        text-align: center;
    }
    
    .recipe-card {
        background-color: #ffffff; padding: 20px; border-radius: 10px;
        border-left: 6px solid #d1478a; margin-bottom: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .category-badge {
        background-color: #f0f0f0; color: #555; padding: 2px 8px;
        border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase;
    }
    img { border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULO CENTRALIZADO ---
st.markdown("""
    <div class="main-title-container">
        <span style="font-size: 2.2rem;">👩‍🍳</span>
        <h1 class="main-title-text">Caderno de Receitas da Marcia</h1>
        <span style="font-size: 2.2rem;">🍴</span>
    </div>
    """, unsafe_allow_html=True)

# --- CADASTRO ---
with st.expander("📥 Cadastrar Nova Receita", expanded=False):
    nome = st.text_input("Nome da Receita")
    c1, c2 = st.columns(2)
    cat = c1.selectbox("Categoria", ["Salgado", "Doce", "Bebida", "Saudável"])
    tempo = c2.text_input("Tempo de Preparo")
    conteudo = st.text_area("Ingredientes e Modo de Preparo", height=100)
    foto_upload = st.file_uploader("Adicionar foto do prato", type=['jpg', 'png', 'jpeg'])
    
    if st.button("Salvar no Caderno"):
        if nome and conteudo:
            foto_b64 = converter_imagem(foto_upload)
            salvar_receita(nome, cat, tempo, conteudo, foto_b64)
            st.success("Receita salva!")
            st.rerun()

st.divider()

# --- BUSCA E LISTAGEM ---
df = listar_receitas()
busca = st.text_input("🔍 Pesquisar em minhas receitas...")

if not df.empty:
    mask = df['nome'].str.contains(busca, case=False) | df['conteudo'].str.contains(busca, case=False)
    for idx, row in df[mask].iterrows():
        rid = row['id']
        
        st.markdown(f"""<div class="recipe-card">
            <span class="category-badge">{row['categoria']}</span>
            <h3 style='margin: 8px 0 4px 0; color: #333;'>{row['nome']}</h3>
            <p style='color: #888; font-size: 14px; margin: 0;'>⏱ {row['tempo']}</p>
        </div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        
        with c1.expander("📄 Ver"):
            if row['foto']:
                st.image(base64.b64decode(row['foto']), use_container_width=True)
            st.write(row['conteudo'])

        with c2.expander("⚙️ Editar"):
            e_nome = st.text_input("Nome", value=row['nome'], key=f"en_{rid}")
            e_cont = st.text_area("Preparo", value=row['conteudo'], height=150, key=f"ect_{rid}")
            e_foto = st.file_uploader("Trocar foto", type=['jpg', 'png'], key=f"ef_{rid}")
            if st.button("Atualizar", key=f"btn_ed_{rid}"):
                nova_foto = converter_imagem(e_foto)
                atualizar_receita(rid, e_nome, row['categoria'], row['tempo'], e_cont, nova_foto)
                st.rerun()

        with c3.expander("❌ Excluir"):
            if st.button("Remover", key=f"del_{rid}"):
                excluir_receita(rid)
                st.rerun()
else:
    st.info("O seu caderno está vazio.")
