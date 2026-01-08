import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import PyPDF2
import importlib.metadata

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="CIVILIS IA", layout="wide")

# --- 🕵️‍♂️ DIAGNÓSTICO DE VERSÃO (PARA VOCÊ VER NA TELA) ---
try:
    versao_atual = importlib.metadata.version("google-generativeai")
    st.warning(f"📊 DIAGNÓSTICO TÉCNICO: A versão instalada da biblioteca Google é: {versao_atual}")
    
    if versao_atual < "0.8.0":
        st.error("❌ ERRO CRÍTICO: O servidor está usando uma versão ANTIGA. É necessário atualizar o requirements.txt e reiniciar o App (Reboot).")
        st.stop()
    else:
        st.success("✅ SISTEMA ATUALIZADO: Pronto para usar Gemini 1.5 Flash.")
except:
    st.error("⚠️ Não foi possível ler a versão da biblioteca.")

# --- CONEXÃO ---
try:
    if "SUPABASE_URL" in st.secrets:
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.error(f"Erro Conexão: {e}")
    st.stop()

# --- LOGIN ---
if "user" not in st.session_state: st.session_state.user = None
if not st.session_state.user:
    st.title("⚖️ CIVILIS SaaS")
    # Login rápido para teste
    if st.button("Entrar (Acesso Rápido)", type="primary"):
        st.session_state.user = {"name": "Admin"}
        st.rerun()
    st.stop()

# --- CHAT ---
st.title("⚖️ CIVILIS IA | Estratégia")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistema pronto. Qual o caso?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Digite aqui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    try:
        # AQUI USAMOS O MODELO NOVO (SÓ VAI FUNCIONAR SE A VERSÃO FOR > 0.8.0)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        st.chat_message("assistant").write(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Erro IA: {e}")
