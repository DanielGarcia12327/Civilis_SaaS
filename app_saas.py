import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import PyPDF2
import time

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(
    page_title="CIVILIS IA | Corporativo",
    page_icon="⚖️",
    layout="wide"
)

# --- 2. CONEXÃO SEGURA ---
try:
    # Conexão com Banco de Dados (Supabase)
    if "SUPABASE_URL" in st.secrets:
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    else:
        supabase = None

    # Conexão com Inteligência Artificial (Google)
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("❌ ERRO CRÍTICO: Chave API do Google não configurada nos Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Erro de Conexão: {e}")
    st.stop()

# --- 3. SISTEMA DE LOGIN ---
def verificar_login(username, password):
    # Backdoor para o Dono (Você) testar rápido
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
        st.markdown("Acesso Restrito - Alta Estratégia Jurídica")
        
        u = st.text_input("Usuário Licenciado")
        p = st.text_input("Chave de Acesso", type="password")
        
        if st.button("Entrar no Sistema", type="primary", use_container_width=True):
            with st.spinner("Autenticando..."):
                time.sleep(1) # Efeito visual de segurança
                user = verificar_login(u, p)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("🚫 Acesso Negado.")
    st.stop()

# --- 4. APLICAÇÃO PRINCIPAL ---
st.title("⚖️ CIVILIS IA | Estratégia")
st.caption(f"Logado como: {st.session_state.user.get('full_name', 'Advogado')}")

# Barra Lateral (Uploads)
with st.sidebar:
    st.header("📂 Autos do Processo")
    uploaded_files = st.file_uploader("Anexar PDF (Processo/Sentença)", type="pdf", accept_multiple_files=True)
    
    contexto_processual = ""
    if uploaded_files:
        st.success(f"{len(uploaded_files)} documentos identificados.")
        for pdf in uploaded_files:
            try:
                reader = PyPDF2.PdfReader(pdf)
                texto_doc = ""
                for page in reader.pages:
                    texto_doc += page.extract_text()
                contexto_processual += f"\n--- DOCUMENTO: {pdf.name} ---\n{texto_doc}\n"
            except Exception as e:
                st.warning(f"Erro ao ler {pdf.name}")
    
    st.divider()
    if st.button("Sair / Logout"):
        st.session_state.user = None
        st.rerun()

# --- 5. LÓGICA DO CHAT (CÉREBRO JURÍDICO) ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistema Online. Doutor, qual a tese ou estratégia precisamos desenvolver hoje?"}]

# Exibe histórico
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Input do Advogado
if prompt := st.chat_input("Digite o comando estratégico..."):
    # 1. Mostra a pergunta do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # 2. Configura o Cérebro (Prompt System)
    regras_sistema = f"""
    VOCÊ É: Um Advogado Sênior Especialista em Direito Civil e Processual Civil (30 anos de experiência).
    
    SUAS REGRAS INEGOCIÁVEIS (LEIA COM ATENÇÃO):
    1.  **COMPETÊNCIA:** Você só resolve casos CÍVEIS.
        * Se o usuário perguntar de Penal, Trabalhista ou Tributário: RECUSE e diga "Doutor, minha especialidade é Civil. Recomendo contratar o módulo específico para essa área."
    
    2.  **SEGREDO INDUSTRIAL:**
        * Se perguntarem quais livros você leu ou sua base de dados: DIGA "Minha base é protegida por Segredo Industrial da Civilis."
        * EXCEÇÃO: Se a mensagem contiver a senha "440055", LISTE: "Base ativa: Caio Mário, Maria Helena Diniz, Pontes de Miranda."

    3.  **ANÁLISE DE JUÍZES:**
        * NUNCA invente perfis de juízes.
        * Se perguntarem "Qual o perfil do Juiz X?", RESPONDA: "Doutor, para traçar o perfil comportamental, por favor anexe 3 sentenças (PDF) deste magistrado."

    CONTEXTO DOS AUTOS ANEXADOS:
    {contexto_processual if contexto_processual else "Nenhum documento anexado ainda."}
    """
    
    # 3. Gera a resposta usando GEMINI 2.0 FLASH (Confirmado na sua imagem)
    with st.chat_message("assistant"):
        with st.spinner("Analisando jurisprudência e doutrina..."):
            try:
                # Usando o modelo que apareceu no seu Raio-X
                model = genai.GenerativeModel(
                    model_name="gemini-2.0-flash", 
                    system_instruction=regras_sistema
                )
                
                response = model.generate_content(prompt)
                texto_resposta = response.text
                
                st.markdown(texto_resposta)
                st.session_state.messages.append({"role": "assistant", "content": texto_resposta})
                
            except Exception as e:
                # Tratamento de erro amigável
                st.error(f"⚠️ Erro de Processamento: {e}")
