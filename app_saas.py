import streamlit as st
from supabase import create_client, Client
import uuid
import time
from google import genai
from google.genai import types
import PyPDF2

# ==================================================
# 1. CONFIGURAÇÃO INICIAL (SaaS MODE)
# ==================================================
st.set_page_config(page_title="Civilis SaaS | Acesso Restrito", layout="wide")

# --- CREDENCIAIS DO SUPABASE (JÁ CONFIGURADAS) ---
SUPABASE_URL = "https://otqdqdmggxtczruipley.supabase.co"
SUPABASE_KEY = "sb_publishable_frd8g5qFAL1eTXexbZniDg_ZEF1SYKC"

# --- CONEXÃO COM O BANCO ---
@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None

supabase = init_supabase()

if not supabase:
    st.error("Erro Crítico: Falha ao conectar no Supabase. Verifique sua internet.")
    st.stop()

# --- ESTILO PROFISSIONAL (CSS INJETADO) ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stTextInput input {border-radius: 5px;}
    div[data-testid="stSidebar"] {background-color: #f0f2f6;}
</style>
""", unsafe_allow_html=True)

# ==================================================
# 2. SISTEMA DE SEGURANÇA (SINGLE SESSION)
# ==================================================

def check_session_validity():
    """Verifica se o token do navegador ainda é o token válido no banco."""
    if "user_data" in st.session_state:
        user = st.session_state["user_data"]
        try:
            response = supabase.table("clients").select("session_token").eq("username", user['username']).execute()
            
            if response.data:
                db_token = response.data[0]['session_token']
                local_token = st.session_state.get('session_token')
                
                # SE O TOKEN DO BANCO MUDOU, ALGUÉM LOGOU EM OUTRO LUGAR!
                if db_token and local_token and db_token != local_token:
                    st.session_state.clear()
                    st.error("⚠️ SESSÃO DERRUBADA!")
                    st.warning("Sua conta foi acessada em outro dispositivo. Por segurança, desconectamos esta sessão.")
                    if st.button("Reconectar Agora"):
                        st.rerun()
                    st.stop()
        except Exception:
            pass 

def login_procedure(username, password):
    """Realiza o login e DERRUBA quem estiver logado antes."""
    try:
        # 1. Busca usuário e senha
        response = supabase.table("clients").select("*").eq("username", username).eq("password", password).execute()
        
        if len(response.data) > 0:
            user = response.data[0]
            
            # 2. GERA NOVO TOKEN DE SESSÃO (Isso derruba o anterior)
            new_token = str(uuid.uuid4())
            
            # 3. Atualiza no Banco
            supabase.table("clients").update({"session_token": new_token}).eq("username", username).execute()
            
            # 4. Salva na Sessão Local
            st.session_state["authenticated"] = True
            st.session_state["user_data"] = user
            st.session_state["session_token"] = new_token
            
            st.success(f"Login Autorizado. Iniciando Ambiente Seguro...")
            time.sleep(1)
            st.rerun()
        else:
            st.error("⛔ Acesso Negado. Usuário ou senha incorretos.")
    except Exception as e:
        st.error(f"Erro de conexão com o servidor: {e}")

# ==================================================
# 3. TELA DE LOGIN (PORTÃO DE ENTRADA)
# ==================================================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if st.session_state["authenticated"]:
    check_session_validity()
else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("")
        st.write("")
        st.markdown("## ⚖️ CIVILIS SaaS | Acesso Corporativo")
        st.caption("Ambiente Jurídico Seguro v1.0 MVP")
        
        with st.form("login_form"):
            user_input = st.text_input("Usuário")
            pass_input = st.text_input("Chave de Acesso", type="password")
            submitted = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if submitted:
                login_procedure(user_input, pass_input)
            
        st.info("Credenciais de Teste: admin / 123")
    
    st.stop()

# ==================================================
# 4. O SISTEMA (AGENTE CIVILIS)
# ==================================================

API_KEY = "AIzaSyDCgTiiPthpnH6jdH4d7hH2EoHmRj-nzwk" 

INSTRUCOES_DO_SISTEMA = """
IDENTIDADE: Civilis IA (SaaS Version).
ROLE: Advogado Sênior e Estrategista Processual.
DIRETRIZES:
1. Respostas diretas e técnicas.
2. Formato: Relatório de Risco seguido da Peça/Minuta.
3. PROIBIDO: Markdown (negrito, titulos com #). Use CAIXA ALTA para títulos.
"""

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"Erro de conexão com o motor de IA: {e}")

with st.sidebar:
    st.success(f"👤 Licenciado: {st.session_state['user_data']['full_name']}")
    st.caption(f"ID Sessão: {st.session_state['session_token'][:8]}...")
    
    if st.button("Sair / Logout"):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    st.markdown("### 📂 Autos Digitais")
    arquivos_pdf = st.file_uploader("Upload de PDF", type=["pdf"], accept_multiple_files=True)

def ler_pdfs(arquivos):
    texto = ""
    for arq in arquivos:
        try:
            leitor = PyPDF2.PdfReader(arq)
            for pag in leitor.pages:
                texto += pag.extract_text()
        except: pass
    return texto

texto_pdfs = ler_pdfs(arquivos_pdf) if arquivos_pdf else ""

st.title("⚖️ CIVILIS IA | Especialista Jurídico")
st.caption("Plataforma de Inteligência Jurídica Exclusiva")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "model", "content": "Sistema Online. Qual a demanda jurídica de hoje?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Digite o comando estratégico...")

if prompt:
    check_session_validity()
    
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    final_prompt = prompt
    if texto_pdfs:
        final_prompt = f"Baseado nos arquivos: {texto_pdfs}\n\nPedido: {prompt}"

    with st.chat_message("model"):
        placeholder = st.empty()
        placeholder.text("Processando...")
        try:
            response = client.models.generate_content(
                model='gemini-flash-latest', 
                contents=final_prompt,
                config=types.GenerateContentConfig(temperature=0.2, system_instruction=INSTRUCOES_DO_SISTEMA)
            )
            placeholder.write(response.text)
            st.session_state.messages.append({"role": "model", "content": response.text})
        except Exception as e:

            placeholder.error(f"Erro: {e}")
