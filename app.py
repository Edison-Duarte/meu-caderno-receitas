import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from PIL import Image, ImageOps
from supabase import create_client, Client

# --- CONEXÃO COM SUPABASE ---
try:
    url: str = st.secrets["SUPABASE_URL"].strip()
    key: str = st.secrets["SUPABASE_KEY"].strip()
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Erro de configuração: Verifique os Secrets.")
    st.stop()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Caderno da Marcia", page_icon="👩‍🍳", layout="centered")

# --- FUNÇÕES DO BANCO DE DADOS ---
def salvar_receita(nome, categoria, tempo, ingredientes, conteudo, foto_base64):
    data = {
        "nome": nome, "categoria": categoria, "tempo": tempo, 
        "ingredientes": ingredientes, "conteudo": conteudo, "foto": foto_base64
    }
    return supabase.table("receitas").insert(data).execute()

def listar_receitas():
    try:
        response = supabase.table("receitas").select("*").order("id", desc=True).execute()
        return pd.DataFrame(response.data)
    except:
        return pd.DataFrame()

def atualizar_receita(id_rec, nome, ingredientes, conteudo):
    data = {"nome": nome, "ingredientes": ingredientes, "conteudo": conteudo}
    supabase.table("receitas").update(data).eq("id", id_rec).execute()

def excluir_receita(id_rec):
    supabase.table("receitas").delete().eq("id", id_rec).execute()

def converter_imagem(img_file):
    if img_file:
        try:
            img = Image.open(img_file)
            img = ImageOps.exif_transpose(img)
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            img.thumbnail((600, 600))
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=60, optimize=True)
            return base64.b64encode(buffer.getvalue()).decode()
        except: return None
    return None

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #0f0a1a; color: #e0d0f0; }
    .main-title { color: #ff79c6; font-weight: 800; font-size: 1.8rem; text-align: center; margin-bottom: 20px; }
    .recipe-card {
        background-color: #1a1425; padding: 15px; border-radius: 12px;
        border: 1px solid #3d2b52; border-left: 5px solid #bd93f9; margin-bottom: 10px;
    }
    .stButton>button {
        width: 100%; border-radius: 8px; background: linear-gradient(45deg, #bd93f9, #ff79c6);
        color: white; border: none; font-weight: bold;
    }
    label { color: #bd93f9 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-title">👩‍🍳 Caderno da Marcia</h1>', unsafe_allow_html=True)

# --- CADASTRO ---
with st.expander("💜 ADICIONAR NOVA RECEITA", expanded=False):
    with st.form("form_limpo", clear_on_submit=True):
        nome = st.text_input("Nome da Receita")
        c1, c2 = st.columns(2)
        cat = c1.selectbox("Tipo", ["Salgado", "Doce", "Bebida", "Saudável"])
        tempo = c2.text_input("Tempo (ex: 45 min)")
        
        ingredientes = st.text_area("Ingredientes (um por linha)", height=100)
        preparo = st.text_area("Modo de Preparo", height=150)
        foto_up = st.file_uploader("Adicionar Foto", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("SALVAR NO MEU CADERNO"):
            if nome and ingredientes and preparo:
                f_b64 = converter_imagem(foto_up)
                salvar_receita(nome, cat, tempo, ingredientes, preparo, f_b64)
                st.toast("Sucesso! 🍰")
                st.rerun()
            else:
                st.warning("Preencha Nome, Ingredientes e Preparo!")

st.divider()

# --- LISTAGEM ---
df = listar_receitas()
if not df.empty:
    busca = st.text_input("🔍 PESQUISAR...", placeholder="Buscar por nome ou ingrediente...")
    
    mask = df['nome'].str.contains(busca, case=False, na=False) | \
           df['ingredientes'].str.contains(busca, case=False, na=False)
    dados = df[mask]

    for _, row in dados.iterrows():
        rid = row['id']
        st.markdown(f"""<div class="recipe-card">
            <div style='font-size:11px; color:#bd93f9;'>{row.get('categoria')} • {row.get('tempo')}</div>
            <h3 style='margin:0; color:white;'>{row['nome']}</h3>
        </div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            with st.expander("📖 VER"):
                if row.get('foto'):
                    try:
                        st.image(base64.b64decode(row['foto']), use_container_width=True)
                    except: st.write("Imagem indisponível")
                st.subheader("🛒 Ingredientes")
                st.write(row.get('ingredientes', 'Não informado'))
                st.subheader("👨‍🍳 Preparo")
                st.write(row['conteudo'])
        with c2:
            with st.expander("✏️ ED"):
                n_nome = st.text_input("Nome", value=row['nome'], key=f"n_{rid}")
                n_ing = st.text_area("Ingredientes", value=row.get('ingredientes',''), key=f"i_{rid}")
                n_pre = st.text_area("Preparo", value=row['conteudo'], key=f"p_{rid}")
                if st.button("SALVAR", key=f"b_{rid}"):
                    atualizar_receita(rid, n_nome, n_ing, n_pre)
                    st.rerun()
        with col3: # Nota: Corrigi de c3 para col3 se necessário, mas mantendo a lógica do seu código anterior
            with st.expander("🗑️ EX"):
                if st.button("OK", key=f"d_{rid}"):
                    excluir_receita(rid)
                    st.rerun()
else:
    st.info("Caderno vazio! ✨")
