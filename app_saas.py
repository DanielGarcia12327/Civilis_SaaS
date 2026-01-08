import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="CIVILIS DIAGNÓSTICO", layout="wide")

st.title("🕵️‍♂️ RAIO-X DOS MODELOS GOOGLE")

# 1. PEGAR A CHAVE
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    st.success("✅ Chave Encontrada.")
except Exception as e:
    st.error(f"❌ Erro na Chave: {e}")
    st.stop()

# 2. PERGUNTAR PRO GOOGLE O QUE TEM DISPONÍVEL
st.write("---")
st.write("🔍 **Consultando o servidor do Google...**")

try:
    # Esta função lista tudo o que sua conta tem permissão de usar
    modelos_disponiveis = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            modelos_disponiveis.append(m.name)
            st.info(f"🟢 Modelo Encontrado: **{m.name}**")
            
    if not modelos_disponiveis:
        st.error("❌ NENHUM modelo encontrado. Sua chave API pode estar bloqueada ou sem permissões.")
    else:
        st.success(f"✅ Total de {len(modelos_disponiveis)} modelos disponíveis para uso.")
        
        # 3. TESTE REAL COM O PRIMEIRO MODELO DA LISTA
        primeiro_modelo = modelos_disponiveis[0]
        st.write(f"🧪 **Tentando teste real com: {primeiro_modelo}**...")
        
        try:
            model = genai.GenerativeModel(primeiro_modelo)
            response = model.generate_content("Diga 'Sistema Operante' se estiver me ouvindo.")
            st.warning(f"🤖 RESPOSTA DA IA: {response.text}")
            st.balloons()
        except Exception as e:
            st.error(f"❌ Falha ao gerar texto: {e}")

except Exception as e:
    st.error(f"❌ Erro ao listar modelos: {e}")
