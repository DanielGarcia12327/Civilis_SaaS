import streamlit as st
from groq import Groq
from supabase import create_client, Client
import PyPDF2
import time

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="CIVILIS IA | Llama 3", layout="wide")

# --- 2. CONEXÃO SEGURA ---
try:
    # Banco de Dados
    if "SUPABASE_URL" in st.secrets:
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    else: supabase = None

    # NOVO MOTOR: GROQ
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.error("❌ ERRO DE CONFIGURAÇÃO: A variável 'GROQ_API_KEY' não foi encontrada nos Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Erro de Conexão: {e}")
    st.stop()

# --- 3. LOGIN ---
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
        st.caption("Motor: Groq® Llama 3 (Ultra Rápido)")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Acessar Sistema", type="primary", use_container_width=True):
            user = verificar_login(u, p)
            if user:
                st.session_state.user = user
                st.rerun()
            else: st.error("Acesso Negado.")
    st.stop()

# --- 4. APP PRINCIPAL ---
st.title("⚖️ CIVILIS IA | Estratégia")
with st.sidebar:
    st.header("📂 Autos Digitais")
    uploaded = st.file_uploader("Anexar PDF", type="pdf", accept_multiple_files=True)
    contexto = ""
    if uploaded:
        for pdf in uploaded:
            try:
                r = PyPDF2.PdfReader(pdf)
                for page in r.pages: contexto += page.extract_text()
            except: pass
        st.success(f"Lidos {len(uploaded)} arquivos.")
    if st.button("Sair"):
        st.session_state.user = None
        st.rerun()

# --- 5. CHAT INTELIGENTE ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistema Online. Doutor, qual a estratégia?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Digite aqui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # CÉREBRO JURÍDICO
    system_prompt = f"""
    ATUE COMO: Advogado Sênior Especialista em Civil.
    REGRAS:
    1. Penal/Trabalhista -> RECUSE.
    2. Livros -> NEGUE (Segredo Industrial). Senha '440055' libera.
    3. Perfil Juiz -> PEÇA 3 sentenças.
    CONTEXTO: {contexto}
    """
    
    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.3,
                )
                resposta = chat_completion.choices[0].message.content
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})
            except Exception as e:
                st.error(f"Erro Groq: {e}")
