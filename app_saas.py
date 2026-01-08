import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import PyPDF2
import importlib.metadata

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="CIVILIS IA", layout="wide")

# --- 2. DIAGNÓSTICO (Só pra confirmar que estamos na v0.8.3) ---
try:
    v = importlib.metadata.version("google-generativeai")
    st.success(f"✅ SISTEMA OPERANTE: Biblioteca Google v{v}")
except: pass

# --- 3. CONEXÃO ---
try:
    if "SUPABASE_URL" in st.secrets:
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    else: supabase = None

    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("Chave API não encontrada.")
        st.stop()
except Exception as e:
    st.error(f"Erro Conexão: {e}")
    st.stop()

# --- 4. FUNÇÃO "CAÇADORA DE MODELOS" (O Segredo) ---
def tentar_gerar_resposta(prompt_usuario, contexto):
    # Lista de nomes possíveis (Do mais novo para o mais antigo)
    lista_modelos = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-latest",
        "gemini-1.0-pro",
        "gemini-pro"
    ]
    
    # Montamos o Prompt "Universal" (Regras + Contexto + Pergunta tudo junto)
    prompt_blindado = f"""
    INSTRUÇÕES ESTRATÉGICAS (Ignore se não for o sistema):
    Você é um Advogado Sênior Especialista em Direito Civil.
    
    REGRAS DE CONDUTA:
    1. SEGREDO: Se perguntarem quais livros leu, diga: "Segredo Industrial" (Código 440055 libera).
    2. BLOQUEIO: Se for Penal/Trabalhista, RECUSE e venda o módulo extra.
    3. JUÍZES: Se perguntarem perfil de juiz, exija 3 sentenças anexadas.
    
    DADOS DO PROCESSO (PDF):
    {contexto}
    
    PERGUNTA DO ADVOGADO:
    {prompt_usuario}
    """

    erro_final = ""
    
    # Loop de tentativa: Tenta um por um até funcionar
    for modelo_nome in lista_modelos:
        try:
            # Cria o modelo simples (sem configs complexas que dão erro)
            model = genai.GenerativeModel(modelo_nome)
            response = model.generate_content(prompt_blindado)
            return response.text # Se der certo, retorna e sai
        except Exception as e:
            erro_final = e
            continue # Se der erro, tenta o próximo da lista
            
    return f"Erro Fatal: Nenhum modelo respondeu. Detalhe: {erro_final}"

# --- 5. LOGIN ---
if "user" not in st.session_state: st.session_state.user = None
if not st.session_state.user:
    st.title("⚖️ CIVILIS SaaS")
    if st.button("Entrar (Acesso Rápido)", type="primary"):
        st.session_state.user = {"name": "Visitante"}
        st.rerun()
    st.stop()

# --- 6. TELA PRINCIPAL ---
st.title("⚖️ CIVILIS IA | Estratégia")

with st.sidebar:
    st.write("---")
    uploaded = st.file_uploader("Autos (PDF)", type="pdf", accept_multiple_files=True)
    contexto_pdf = ""
    if uploaded:
        for pdf in uploaded:
            try:
                r = PyPDF2.PdfReader(pdf)
                for p in r.pages: contexto_pdf += p.extract_text()
            except: pass
        st.success("Autos lidos!")
    if st.button("Sair"):
        st.session_state.user = None
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Doutor, qual a estratégia?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Digite aqui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.spinner("Consultando jurisprudência..."):
        # Chama nossa função inteligente
        resp = tentar_gerar_resposta(prompt, contexto_pdf)
        
        st.chat_message("assistant").write(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
