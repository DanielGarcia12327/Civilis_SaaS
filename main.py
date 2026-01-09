import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

# Chave de API vinda dos Secrets do Streamlit
api_key = st.secrets.get("GROQ_API_KEY")

@st.cache_resource(show_spinner=False)
def processar_base():
    # O sistema agora busca especificamente na pasta organizada
    loader = DirectoryLoader('./base_conhecimento', glob="**/*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.from_documents(splits, embeddings)

st.set_page_config(page_title="Civilis SaaS", page_icon="⚖️")
st.title("⚖️ Civilis SaaS - Inteligência Jurídica")

if "vs" not in st.session_state:
    with st.spinner("Analisando base de conhecimento jurídica..."):
        st.session_state.vs = processar_base()

prompt = st.chat_input("Digite sua dúvida jurídica aqui...")
if prompt:
    llm = ChatGroq(model_name="llama3-70b-8192", groq_api_key=api_key)
    qa_chain = RetrievalQA.from_chain_type(
        llm, retriever=st.session_state.vs.as_retriever(), 
        return_source_documents=True
    )
    res = qa_chain.invoke({"query": prompt})
    st.write(res["result"])
    with st.expander("Fontes citadas"):
        for doc in res["source_documents"]:
            st.write(f"- {os.path.basename(doc.metadata['source'])}")

