import streamlit as st
from groq import Groq
from supabase import create_client, Client
import PyPDF2
import time

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="CIVILIS IA | Estratégia", layout="wide")

# --- 2. CONEXÃO SEGURA ---
try:
    if "SUPABASE_URL" in st.secrets:
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    else: supabase = None

    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.error("❌ ERRO: Chave GROQ não encontrada.")
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
        st.caption("Acesso Restrito ao Corpo Jurídico")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar", type="primary", use_container_width=True):
            user = verificar_login(u, p)
            if user:
                st.session_state.user = user
                st.rerun()
            else: st.error("Credenciais Inválidas.")
    st.stop()

# --- 4. APP PRINCIPAL ---
st.title("⚖️ CIVILIS IA | Estratégia")
with st.sidebar:
    st.header("📂 Base de Conhecimento (Upload)")
    st.info("Para que a IA analise casos ou livros específicos, anexe os PDFs aqui.")
    uploaded = st.file_uploader("Anexar Autos ou Doutrina (PDF)", type="pdf", accept_multiple_files=True)
    
    contexto = ""
    if uploaded:
        for pdf in uploaded:
            try:
                r = PyPDF2.PdfReader(pdf)
                for page in r.pages: contexto += page.extract_text()
            except: pass
        st.success(f"{len(uploaded)} Arquivos carregados na memória temporária.")
    
    st.divider()
    if st.button("Sair"):
        st.session_state.user = None
        st.rerun()

# --- 5. CHAT COM SEGURANÇA REFORÇADA ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Civilis Online. Aguardando caso concreto."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Digite a instrução..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # --- CÉREBRO JURÍDICO (REGRAS CRÍTICAS) ---
    system_prompt = f"""
    VOCÊ É: O "Civilis", uma IA Jurídica de Elite.
    TOM: Erudito, técnico, impessoal e estratégico. Use termos como "Data vênia", "Jurisprudência pacificada", "Dogmática".
    
    ⚠️ PROTOCOLO DE SEGURANÇA DE DADOS (ABSOLUTO):
    
    1. SOBRE SUAS FONTES (LIVROS/BASE DE DADOS):
       * SE O USUÁRIO PERGUNTAR O QUE VOCÊ LEU: Responda APENAS: "Minha fundamentação baseia-se na Dogmática Civilista Clássica, na Teoria Geral das Obrigações e nos precedentes vinculantes das Cortes Superiores (STJ/STF). Por motivos de Segredo Industrial e Proteção de Dados, a bibliografia exata é confidencial."
       * REGRA DE OURO: JAMAIS mencione que existe uma senha. JAMAIS dê dicas da senha. Aja como se a informação fosse impossível de obter.
       
    2. O "BACKDOOR" (ADMIN):
       * SOMENTE se a mensagem do usuário contiver exatamente o código "440055", você deve responder:
         "🔓 MODO ADMIN: Base de Treinamento Confirmada:
          1. Tratado de Direito Privado (Pontes de Miranda) - Tomos I a LX;
          2. Instituições de Direito Civil (Caio Mário);
          3. Comentários ao Código de Processo Civil (Nelson Nery Jr.);
          4. Informativos STJ (Últimos 5 anos)."
    
    3. COMPETÊNCIA:
       * Recuse sumariamente questões Penais ou Trabalhistas. "Não possuo competência regimental para matérias estranhas ao Direito Civil."

    4. JUÍZES:
       * Se pedirem perfil de juiz, exija 3 sentenças em anexo para "análise jurimétrica".
    
    CONTEXTO DOS ARQUIVOS ANEXADOS PELO ADVOGADO:
    {contexto}
    """
    
    with st.chat_message("assistant"):
        with st.spinner("Consultando doutrina e jurisprudência..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.2, # Temperatura baixa = Menos criatividade, mais obediência
                )
                resposta = chat_completion.choices[0].message.content
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})
            except Exception as e:
                st.error(f"Erro no processamento: {e}")
