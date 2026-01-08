import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import PyPDF2

# --- CONFIGURAÇÃO DA PÁGINA (Deve ser a primeira linha) ---
st.set_page_config(
    page_title="CIVILIS IA | Corporativo",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILO PROFISSIONAL (CSS) ---
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #0e1117;
        border-right: 1px solid #262730;
    }
    .stChatInputContainer textarea {
        background-color: #2b313e;
        color: white;
    }
    h1 { color: #f0f2f6; }
    p { font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

# --- SEGREDOS E CONEXÕES ---
try:
    # Supabase (Tratamento de erro se a chave não existir)
    if "SUPABASE_URL" in st.secrets:
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        st.warning("⚠️ Banco de Dados desconectado. Verifique os Secrets.")
        supabase = None

    # Google Gemini
    if "GOOGLE_API_KEY" in st.secrets:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=GOOGLE_API_KEY)
    else:
        st.error("❌ Chave da IA não encontrada.")
        st.stop()
        
except Exception as e:
    st.error(f"❌ Erro Técnico: {e}")
    st.stop()

# --- FUNÇÕES AUXILIARES ---
def ler_pdf(uploaded_file):
    """Extrai texto de arquivos PDF."""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Erro ao ler PDF: {e}"

def verificar_login(username, password):
    """Verifica credenciais no Supabase."""
    if not supabase:
        # Modo de contingência se o banco falhar
        if username == "convidado" and password == "teste2026":
            return {"full_name": "Acesso Visitante", "username": "convidado"}
        return None

    try:
        response = supabase.table("clients").select("*").eq("username", username).eq("password", password).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Erro de conexão com Login: {e}")
        return None

# --- SISTEMA DE LOGIN ---
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>⚖️ CIVILIS SaaS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Ambiente Jurídico Seguro v2.1</p>", unsafe_allow_html=True)
        st.divider()
        
        username = st.text_input("Usuário Licenciado")
        password = st.text_input("Chave de Acesso", type="password")
        
        if st.button("Entrar no Sistema", type="primary", use_container_width=True):
            user = verificar_login(username, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Credenciais inválidas ou acesso revogado.")
        
        st.info("Credencial de Teste: convidado / teste2026")
    st.stop()

# --- ÁREA LOGADA (SÓ ENTRA AQUI SE TIVER LOGADO) ---
user = st.session_state.user

# --- BARRA LATERAL (MENU) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1904/1904633.png", width=60)
    st.markdown(f"### Olá, {user.get('full_name', 'Doutor(a)')}")
    st.caption("Status: ✅ Conexão Segura")
    st.divider()
    
    # SELETOR DE MÓDULOS (Futura Monetização)
    modulo = st.selectbox("Módulo Ativo", ["🔷 Direito Civil (Civilis)", "🔒 Trabalhista (Bloqueado)", "🔒 Tributário (Bloqueado)"])
    
    if "Bloqueado" in modulo:
        st.warning(f"O módulo {modulo} não está contratado.")
        st.info("Entre em contato com o admin para liberar.")
    
    st.divider()
    
    # UPLOAD DE ARQUIVOS (Autos)
    st.markdown("### 📂 Autos Digitais")
    uploaded_files = st.file_uploader("Anexar: Processo, Sentença ou Contrato", type="pdf", accept_multiple_files=True)
    
    processo_texto = ""
    if uploaded_files:
        for pdf in uploaded_files:
            texto = ler_pdf(pdf)
            processo_texto += f"\n--- DOCUMENTO: {pdf.name} ---\n{texto}\n"
        st.success(f"{len(uploaded_files)} documentos analisados.")

    st.divider()
    if st.button("Sair / Logout"):
        st.session_state.user = None
        st.rerun()

# --- LÓGICA DO CHAT (CÉREBRO) ---
st.title("⚖️ CIVILIS IA | Estratégia Processual")
st.markdown("Plataforma de Inteligência Jurídica Exclusiva")

# Histórico de Chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistema Online. Doutor, qual o caso concreto ou a estratégia que precisamos definir hoje?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- O GRANDE PROMPT DE SISTEMA (CORRIGIDO V2.1) ---
def gerar_resposta(pergunta, contexto_pdf):
    # CORREÇÃO: Usamos 'system_instruction' separado para evitar erro de Argumento
    
    prompt_sistema = f"""
    ATUE COMO: Um Advogado Sênior Especialista em Direito Civil e Processual Civil, com 30 anos de experiência, doutorado e visão estratégica agressiva.
    
    SUA MISSÃO: Analisar o caso trazido pelo advogado e fornecer estratégias processuais de alto nível, redação de peças e análise de riscos.

    REGRAS INEGOCIÁVEIS DE COMPORTAMENTO:

    1.  **BLOQUEIO DE COMPETÊNCIA:**
        * Você é ESTRITAMENTE especialista em CIVIL e PROCESSO CIVIL.
        * Se o usuário perguntar sobre Direito Penal, Trabalhista ou Tributário, responda EXATAMENTE:
            "Doutor, minha programação neural é dedicada exclusivamente à Alta Estratégia Cível. Para esta demanda de [Área Solicitada], recomendo habilitar o módulo específico 'Laboris' ou 'Tributum' no seu painel administrativo."

    2.  **SEGREDO INDUSTRIAL:**
        * Se perguntarem quais livros ou base de dados, responda: "Minha base de conhecimento é protegida por Segredo Industrial."
        * EXCEÇÃO: Se a mensagem contiver o código "440055", liste: "Base ativa: Caio Mário, Maria Helena Diniz, Pontes de Miranda e Código Civil Comentado 2025."

    3.  **ANÁLISE DE JUÍZES:**
        * Você NÃO tem acesso direto ao TJ. Não invente perfis.
        * Se perguntarem "Qual o perfil do Juiz X?", responda:
            "Doutor, para traçar o perfil desse magistrado com precisão e evitar especulações, preciso que o senhor anexe 3 sentenças (PDF) dele. Assim farei a análise psicométrica jurídica."
        * Se JÁ TIVER anexos, analise com base neles.

    CONTEXTO DOS AUTOS (DOCUMENTOS ANEXADOS):
    {contexto_pdf if contexto_pdf else "Nenhum documento anexado pelo usuário no momento."}
    """
    
    try:
        # CORREÇÃO CRÍTICA: Passamos o prompt como 'system_instruction'
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=prompt_sistema
        )
        
        response = model.generate_content(pergunta)
        return response.text
    except Exception as e:
        return f"Erro na IA: {e}"

# Input do Usuário
if user_input := st.chat_input("Digite o comando estratégico..."):
    # Adicionar mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Gerar resposta
    with st.chat_message("assistant"):
        with st.spinner("Analisando jurisprudência e estratégia..."):
            resposta = gerar_resposta(user_input, processo_texto)
            st.markdown(resposta)
    
    # Salvar resposta
    st.session_state.messages.append({"role": "assistant", "content": resposta})
