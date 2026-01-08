import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import PyPDF2

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="CIVILIS IA", layout="wide")

# 2. CONEXÃO
try:
    if "SUPABASE_URL" in st.secrets:
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    else:
        supabase = None

    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("ERRO: Chave API do Google não encontrada.")
        st.stop()
except Exception as e:
    st.error(f"Erro de Conexão: {e}")
    st.stop()

# 3. LOGIN
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

# 4. APP PRINCIPAL
with st.sidebar:
    st.write("---")
    uploaded = st.file_uploader("Anexar Autos (PDF)", type="pdf", accept_multiple_files=True)
    contexto_pdf = ""
    if uploaded:
        for pdf in uploaded:
            try:
                reader = PyPDF2.PdfReader(pdf)
                for page in reader.pages: contexto_pdf += page.extract_text()
            except: pass
        st.success("PDFs Processados!")
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
    
    # CÉREBRO JURÍDICO
    sistema = f"""
    ATUE COMO: Advogado Especialista em Civil.
    REGRAS:
    1. Se for Penal/Trabalhista: RECUSE e mande contratar módulo extra.
    2. Se pedir livros: NEGUE (Segredo Industrial). Senha '440055' libera.
    3. Se perguntar de Juiz: Peça 3 sentenças anexadas.
    
    CONTEXTO: {contexto_pdf}
    """
    
    try:
        # AQUI ESTÁ O SEGREDO: Usamos 'gemini-1.5-flash'
        # E usamos a sintaxe simplificada que nunca falha
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=sistema)
        response = model.generate_content(prompt)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.chat_message("assistant").write(response.text)
        
    except Exception as e:
        st.error(f"Erro na IA: {e}")
