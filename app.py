import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from PIL import Image
from supabase import create_client, Client

# --- CONEXÃO COM SUPABASE ---
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Caderno da Marcia", page_icon="👩‍🍳", layout="centered")

# --- FUNÇÕES DO BANCO DE DADOS (AGORA NA NUVEM) ---
def salvar_receita(nome, categoria, tempo, conteudo, foto_base64):
    data = {
        "nome": nome,
        "categoria": categoria,
        "tempo": tempo,
        "conteudo": conteudo,
        "foto": foto_base64
    }
    supabase.table("receitas").insert(data).execute()

def listar_receitas():
    response = supabase.table("receitas").select("*").execute()
    return pd.DataFrame(response.data)

def atualizar_receita(id_rec, nome, categoria, tempo, conteudo, foto_base64):
    data = {"nome": nome, "categoria": categoria, "tempo": tempo, "conteudo": conteudo}
    if foto_base64:
        data["foto"] = foto_base64
    supabase.table("receitas").update(data).eq("id", id_rec).execute()

def excluir_receita(id_rec):
    supabase.table("receitas").delete().eq("id", id_rec).execute()

def converter_imagem(img_file):
    if img_file:
        img = Image.open(img_file)
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        img.thumbnail((500, 500))
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=60, optimize=True)
        return base64.b64encode(buffer.getvalue()).decode()
    return None

# --- ESTILO VISUAL (O MESMO QUE VOCÊ GOSTOU) ---
st.markdown("""
    <style>
    .stApp { background-color: #0f0a1a; color: #e0d0f0; }
    .block-container { padding-top: 4rem !important; padding-left: 0.6rem !important; padding-right: 0.6rem !important; }
    .main-title-text { 
        color: #ff79c6; font-family: sans-serif; font-weight: 800; 
        font-size: clamp(1.2rem, 6vw, 1.8rem); text-align: center; margin-bottom: 25px;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .recipe-card {
        background-color: #1a1425; padding: 14px; border-radius: 12px;
        border: 1px solid #3d2b52; border-left: 5px solid #bd93f9; margin-bottom: 10px; 
    }
    .stButton>button {
        width: 100%; border-radius: 8px !important;
        background: linear-gradient(45deg, #bd93f9, #ff79c6) !important;
        color: #ffffff !important; border: none !important; height: 45px;
        font-weight: bold; text-transform: uppercase;
    }
    footer {display:none !important;}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-title-text">Caderno de Receitas da Marcia</h1>', unsafe_allow_html=True)

# --- CADASTRO ---
with st.expander("💜 ADICIONAR NOVA DELÍCIA", expanded=False):
    nome = st.text_input("Nome")
    c1, c2 = st.columns(2)
    cat = c1.selectbox("Tipo", ["Salgado", "Doce", "Bebida", "Saudável"])
    tempo = c2.text_input("Tempo")
    conteudo = st.text_area("Preparo", height=150)
    foto_upload = st.file_uploader("Foto", type=['jpg', 'png', 'jpeg'])
    
    if st.button("SALVAR NO CADERNO"):
        if nome and conteudo:
            with st.spinner('Salvando na nuvem...'):
                foto_b64 = converter_imagem(foto_upload)
                salvar_receita(nome, cat, tempo, conteudo, foto_b64)
            st.success("Salvo com segurança!")
            st.rerun()

st.divider()

# --- BUSCA E LISTAGEM ---
df = listar_receitas()
busca = st.text_input("🔍 PESQUISAR...")

if not df.empty:
    mask = df['nome'].str.contains(busca, case=False) | df['conteudo'].str.contains(busca, case=False)
    for idx, row in df[mask].iterrows():
        rid = row['id']
        st.markdown(f"""<div class="recipe-card">
            <div style='color:#bd93f9; font-size:10px; font-weight:bold;'>{row['categoria']} • {row['tempo']}</div>
            <h3 style='margin:4px 0; font-size:16px;'>{row['nome']}</h3>
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
    st.info("Nenhuma receita encontrada na nuvem.")
