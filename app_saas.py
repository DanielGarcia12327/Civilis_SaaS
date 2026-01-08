import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Civilis SaaS - Mente Jurídica", page_icon="⚖️", layout="wide")

# --- CSS PARA ESTILO PROFISSIONAL ---
st.markdown("""
<style>
    .stChatInput {border-radius: 15px;}
    div[data-testid="stToolbar"] {visibility: hidden;}
    .reportview-container .main .block-container {padding-top: 2rem;}
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://img.icons8.com/ios-filled/100/4a90e2/law.png", width=80) # Ícone genérico
with col2:
    st.title("Civilis SaaS - Doutrina Secreta")
    st.markdown("**IA Jurídica Baseada em Evidências e Doutrina**")

st.divider()

# --- CONFIGURAÇÃO DE SEGREDOS ---
# Tenta pegar a chave do st.secrets (produção) ou do ambiente local
api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

if not api_key:
    st.error("⚠️ ERRO CRÍTICO: Chave da API GROQ não encontrada. Configure os 'Secrets' no Streamlit Cloud.")
    st.stop()

# --- MOTOR DE INTELIGÊNCIA (RAG) ---
@st.cache_resource(show_spinner=False)
def carregar_e_processar_pdfs():
    """
    Lê todos os PDFs do repositório, quebra em chunks inteligentes
    e cria o índice vetorial para busca semântica.
    """
    # 1. Carregar PDFs da raiz e subpastas
    pdf_loaders = [
        DirectoryLoader('.', glob="**/*.pdf", loader_cls=PyPDFLoader, show_progress=True)
    ]
    
    docs = []
    for loader in pdf_loaders:
        try:
            docs.extend(loader.load())
        except Exception as e:
            pass # Ignora erros de leitura em arquivos específicos

    if not docs:
        return None

    # 2. Dividir em pedaços (Chunks) para não estourar a memória da IA
    # Chunk de 1000 caracteres com 200 de sobreposição garante contexto contínuo
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # 3. Criar Embeddings (Transformar texto em números)
    # Usamos um modelo leve e gratuito da HuggingFace para rodar rápido na nuvem
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # 4. Criar Banco Vetorial (FAISS)
    vectorstore = FAISS.from_documents(splits, embeddings)
    return vectorstore

# --- INICIALIZAÇÃO DO SISTEMA ---
if "vectorstore" not in st.session_state:
    with st.spinner("🔄 Indexando Doutrina Secreta e Legislação (Isso acontece apenas uma vez)..."):
        vs = carregar_e_processar_pdfs()
        if vs:
            st.session_state.vectorstore = vs
            st.success(f"📚 Base de Conhecimento carregada com sucesso!")
        else:
            st.warning("Nenhum PDF encontrado no repositório. O sistema funcionará sem contexto específico.")
            st.session_state.vectorstore = None

# --- CHATBOT ---

# Modelo LLM (Groq - Llama 3 para velocidade e raciocínio)
llm = ChatGroq(temperature=0.3, model_name="llama3-70b-8192", groq_api_key=api_key)

# Prompt do Sistema (A "Personalidade")
template = """
Você é o Assistente Jurídico do Civilis SaaS. Sua mente é baseada estritamente nos documentos fornecidos.
Use os seguintes pedaços de contexto recuperados para responder à pergunta.
Se você não souber a resposta baseada no contexto, diga que não consta na doutrina anexada.
Seja técnico, preciso e cite os conceitos jurídicos corretamente.

Contexto:
{context}

Pergunta:
{question}

Resposta Profissional:
"""

QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capturar input do usuário
if prompt := st.chat_input("Pergunte à Doutrina (Ex: O que diz o Código Civil sobre usucapião?)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Lógica de Resposta
        if st.session_state.vectorstore:
            # Modo RAG (Com Consulta aos Livros)
            qa_chain = RetrievalQA.from_chain_type(
                llm,
                retriever=st.session_state.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4}),
                chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
                return_source_documents=True
            )
            
            with st.spinner("Consultando jurisprudência..."):
                result = qa_chain.invoke({"query": prompt})
                response = result["result"]
                sources = result["source_documents"]
                
                # Formatar resposta + Fontes
                full_response = response + "\n\n---\n**Fontes Consultadas:**\n"
                unique_sources = set()
                for doc in sources:
                    # Tenta pegar o nome do arquivo limpo
                    source_name = os.path.basename(doc.metadata['source'])
                    page = doc.metadata.get('page', 'N/A')
                    unique_sources.add(f"- *{source_name}* (Pág. {page})")
                
                full_response += "\n".join(unique_sources)
                
                message_placeholder.markdown(full_response)
        else:
            # Modo Fallback (Sem PDFs)
            response = llm.invoke(prompt).content
            message_placeholder.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": full_response if st.session_state.vectorstore else response})
