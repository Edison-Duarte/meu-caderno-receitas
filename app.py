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
    st.error("Erro de configuração: Verifique os Secrets no Streamlit Cloud.")
    st.stop()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Caderno da Marcia", page_icon="👩‍🍳", layout="centered")

# --- FUNÇÕES DO BANCO DE DADOS ---
def salvar_receita(nome, categoria, tempo, conteudo, foto_base64):
    data = {
        "nome": nome, 
        "categoria": categoria, 
        "tempo": tempo, 
        "conteudo": conteudo, 
        "foto": foto_base64
    }
    return supabase.table("receitas").insert(data).execute()

def listar_receitas():
    try:
        response = supabase.table("receitas").select("*").order("id", desc=True).execute()
        return pd.DataFrame(response.data)
    except:
        return pd.DataFrame()

def atualizar_receita(id_rec, nome, categoria, tempo, conteudo, foto_base64=None):
    data = {"nome": nome, "categoria": categoria, "tempo": tempo, "conteudo": conteudo}
    if foto_base64:
        data["foto"] = foto_base64
    supabase.table("receitas").update(data).eq("id", id_rec).execute()

def excluir_receita(id_rec):
    supabase.table("receitas").delete().eq("id", id_rec).execute()

def converter_imagem(img_file):
    if img_file:
        try:
            img = Image.open(img_file)
            img = ImageOps.exif_transpose(img) # Corrige foto virada do celular
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            img.thumbnail((600, 600)) # Reduz para ficar leve
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=60, optimize=True)
            return base64.b64encode(buffer.getvalue()).decode()
        except:
            return None
    return None

# --- ESTILO VISUAL (CSS) ---
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
    /* Estilo para campos dentro do formulário */
    .stForm { border: none !important; padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-title">👩‍🍳 Caderno da Márcia</h1>', unsafe_allow_html=True)

# --- CADASTRO (FECHA AO SALVAR E LIMPA CAMPOS) ---
with st.expander("💜 ADICIONAR NOVA RECEITA", expanded=False):
    with st.form("meu_formulario", clear_on_submit=True):
        nome = st.text_input("Nome da Delícia")
        c1, c2 = st.columns(2)
        cat = c1.selectbox("Tipo", ["Salgado", "Doce", "Bebida", "Saudável"])
        tempo = c2.text_input("Tempo (ex: 30 min)")
        conteudo = st.text_area("Modo de Preparo", height=150)
        foto_upload = st.file_uploader("Foto (Opcional)", type=['jpg', 'png', 'jpeg'])
        
        btn_salvar = st.form_submit_button("SALVAR NO MEU CADERNO")
        
        if btn_salvar:
            if nome and conteudo:
                with st.spinner('Guardando...'):
                    foto_b64 = converter_imagem(foto_upload)
                    salvar_receita(nome, cat, tempo, conteudo, foto_b64)
                    st.toast("Receita salva com sucesso! 🎉")
                    st.rerun() # Recarrega para fechar o expander e limpar tudo
            else:
                st.error("Preencha o Nome e o Preparo!")

st.divider()

# --- LISTAGEM ---
df = listar_receitas()
if not df.empty:
    busca = st.text_input("🔍 PESQUISAR...", placeholder="O que vamos cozinhar hoje?")
    
    mask = df['nome'].str.contains(busca, case=False, na=False) | \
           df['conteudo'].str.contains(busca, case=False, na=False)
    dados_filtrados = df[mask]

    for idx, row in dados_filtrados.iterrows():
        rid = row['id']
        st.markdown(f"""<div class="recipe-card">
            <div style='color:#bd93f9; font-size:11px; font-weight:bold;'>{row.get('categoria')} • {row.get('tempo')}</div>
            <h3 style='margin:5px 0; color:#ffffff;'>{row['nome']}</h3>
        </div>""", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            with st.expander("📖 VER"):
                if row.get('foto'):
                    try:
                        st.image(base64.b64decode(row['foto']), use_container_width=True)
                    except: st.write("Erro na imagem")
                st.write(row['conteudo'])
        with col2:
            with st.expander("✏️ EDITAR"):
                enome = st.text_input("Nome", value=row['nome'], key=f"en_{rid}")
                econt = st.text_area("Preparo", value=row['conteudo'], height=150, key=f"ec_{rid}")
                if st.button("SALVAR", key=f"eb_{rid}"):
                    atualizar_receita(rid, enome, row['categoria'], row['tempo'], econt)
                    st.rerun()
        with col3:
            with st.expander("🗑️ EX"):
                if st.button("SIM", key=f"db_{rid}"):
                    excluir_receita(rid)
                    st.rerun()
else:
    st.info("O caderno está vazio. Adicione uma receita acima! ✨")
