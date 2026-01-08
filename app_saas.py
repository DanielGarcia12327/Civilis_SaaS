import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import PyPDF2
import time

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="CIVILIS IA | Corporativo", layout="wide")

# --- ESTILO ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0e1117; }
    .stChatInputContainer textarea { background-color: #2b313e; color: white; }
</style>
""", unsafe_allow_html=True)

# --- CONEXÃO ---
try:
    if "SUPABASE_URL" in st.secrets:
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    else:
        supabase = None

    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("❌ Chave API não encontrada.")
        st.stop()
except Exception as e:
    st.error(f"Erro de Conexão: {e}")
    st.stop()

# --- LOGIN ---
def verificar_login(username, password):
    if username == "convidado" and password == "teste2026":
        return {"full_name": "Visitante VIP"}
    if supabase:
        try:
            res = supabase.table("clients").select("*").eq("username", username).eq("password", password).execute()
            return res.data[0] if res.data else None
        except: return None
    return None

if "user" not in st.session_state: st.session_state.user = None

if not st.session_state.user:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("⚖️ CIVILIS SaaS")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar", type="primary", use_container_width=True):
            user = verificar_login(u, p)
            if user:
                st.session_state.user = user
                st.rerun()
            else: st.error("Acesso Negado")
    st.stop()

# --- APLICATIVO ---
with st.sidebar:
    st.write("---")
    st.write("📂 **Autos do Processo**")
    uploaded = st.file_uploader("Anexar PDF", type="pdf", accept_multiple_files=True)
    contexto = ""
    if uploaded:
        for pdf in uploaded:
            try:
                reader = PyPDF2.PdfReader(pdf)
                for page in reader.pages: contexto += page.extract_text()
                contexto += f"\nDoc: {pdf.name}\n"
            except: pass
        st.success("Docs Anexados!")
    if st.button("Sair"):
        st.session_state.user = None
        st.rerun()

st.title("⚖️ CIVILIS IA | Estratégia")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Doutor, qual a estratégia de hoje?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Digite aqui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # LÓGICA DO CÉREBRO JURÍDICO
    sistema = f"""
    ATUE COMO: Advogado Especialista em Civil.
    REGRAS:
    1. Se for Penal/Trabalhista -> RECUSE e mande contratar módulo extra.
    2. Se pedir livros -> NEGUE (Segredo Industrial). Senha '440055' libera.
    3. Se perguntar de Juiz -> PEÇA 3 SENTENÇAS ANEXADAS.
    
    DADOS DO PROCESSO: {contexto}
    """
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        try:
            # TENTATIVA 1: Modelo Novo (Rápido e Inteligente)
            model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=sistema)
            resp = model.generate_content(prompt).text
        except Exception as e:
            # TENTATIVA 2: Estepe (Modelo Clássico) - Se o 1 falhar, usa esse
            try:
                placeholder.warning("⚠️ Servidor desatualizado. Usando modelo de backup...")
                model = genai.GenerativeModel("gemini-pro") # Modelo antigo que nunca falha
                # Gemini Pro antigo não aceita system_instruction direto, então adaptamos:
                full_prompt = f"{sistema}\n\nPERGUNTA DO ADVOGADO: {prompt}"
                resp = model.generate_content(full_prompt).text
            except Exception as e2:
                resp = f"Erro Fatal: {e2}"

        placeholder.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
