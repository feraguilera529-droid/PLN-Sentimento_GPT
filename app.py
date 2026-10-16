"""
MIT License

Copyright (c) 2026 Arquiteto de Software Especialista em IA e Python

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import streamlit as st
from openai import AzureOpenAI

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="EXTRATOR DE DADOS INTELIGENTE | Futurist UI",
    page_icon="🤖",
    layout="wide",
)

# ==============================================================================
# ESTILIZAÇÃO CSS CUSTOMIZADA (FUTURIST UI)
# ==============================================================================
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #0a0e17 0%, #030509 100%);
        color: #e0f0ff;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    h1, h2, h3, .stMarkdown {
        color: #e0f0ff;
        text-shadow: 0 0 10px #00e5ff;
    }

    .holographic-panel {
        background: rgba(10, 25, 41, 0.4);
        border: 1px solid rgba(0, 229, 255, 0.3);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 30px rgba(0, 110, 255, 0.2), inset 0 0 10px rgba(0, 229, 255, 0.1);
        margin-bottom: 20px;
    }

    .stTextArea>div>div>textarea {
        background-color: rgba(5, 10, 20, 0.6) !important;
        border: 1px solid rgba(0, 229, 255, 0.4) !important;
        color: #00e5ff !important;
        border-radius: 8px !important;
        font-family: 'Courier New', monospace;
    }

    .stButton>button {
        background: linear-gradient(135deg, #0078D4 0%, #00e5ff 100%);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 50px;
        width: 100%;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.6);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #00e5ff 0%, #0078D4 100%);
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.9);
        transform: scale(1.02);
    }

    .metric-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 10px;
        padding: 15px;
        background: rgba(10, 25, 41, 0.2);
        margin: 5px;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00e5ff;
        text-shadow: 0 0 15px #00e5ff;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #a0c0ff;
        text-transform: uppercase;
    }
    .status-bar {
        width: 100%;
        height: 10px;
        border-radius: 5px;
        background: #304060;
        margin-top: 10px;
    }

    hr {
        border-color: rgba(0, 229, 255, 0.3) !important;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.2);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# BARRA LATERAL (CONFIGURAÇÕES)
# ==============================================================================
with st.sidebar:
  st.markdown(
      '<div class="holographic-panel">'
      '<h2 style="text-align:center; color:#00e5ff; text-shadow: 0 0 10px #00e5ff;">⚙️ Configurações</h2>'
      "Este aplicativo futurista utiliza o modelo **gpt-4.1-mini** no **Azure OpenAI** "
      "para analisar e extrair dados estruturados como sentimento, assunto, pessoas citadas e nível de urgência."
      "</div>",
      unsafe_allow_html=True,
  )

# ==============================================================================
# CABEÇALHO DA APLICAÇÃO
# ==============================================================================
st.markdown(
    '<p style="font-size: 2.2rem; color: #e0f0ff; text-shadow: 0 0 15px #00e5ff; font-weight: 700; margin-bottom: 0px;">🤖 EXTRATOR DE DADOS INTELIGENTE</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="font-size: 1rem; color: #a0c0ff; margin-bottom: 25px;">Powered by Microsoft Azure OpenAI & Python - Futurist UI</p>',
    unsafe_allow_html=True,
)
st.divider()

# ==============================================================================
# ENTRADA DE DADOS
# ==============================================================================
st.markdown('<div class="holographic-panel">', unsafe_allow_html=True)
st.subheader("📝 Digite ou cole o texto para análise")
texto_usuario = st.text_area(
    label="Texto fonte:",
    height=150,
    placeholder=(
        "Exemplo: 'Urgente! O Carlos e a Ana relataram um atraso crítico no projeto Alpha devido a problemas de infraestrutura...'"
    ),
    label_visibility="collapsed",
)
st.markdown("</div>", unsafe_allow_html=True)

# Botão de Ação
if st.button("🚀 Processar Texto"):
  if not texto_usuario.strip():
    st.warning("⚠️ Por favor, insira algum texto antes de clicar em Processar.")
  else:
    try:
      api_key = st.secrets["azure_openai"]["api_key"]
      endpoint = st.secrets["azure_openai"]["endpoint"]
      model_name = st.secrets["azure_openai"]["model_name"]
    except Exception:
      api_key = (
          "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os"
      )
      endpoint = "https://marcelomaffeis-05082026-resource.services.ai.azure.com/"
      model_name = "gpt-4.1-mini"

    endpoint = endpoint.replace("&quot;", "").strip()

    with st.spinner("🔄 Processando análise no Azure OpenAI..."):
      try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version="2024-08-01-preview",
            azure_endpoint=endpoint,
        )

        system_prompt = (
            "Você é um assistente especialista em extração de dados e análise de"
            " texto. Sua tarefa é analisar o texto fornecido pelo usuário e"
            " retornar ESTRITAMENTE um objeto JSON válido contendo exatas"
            " chaves:\n1. 'sentimento': string indicando o sentimento geral"
            " (ex: Positivo, Neutro, Negativo).\n2. 'porcentagem_sentimento':"
            " número inteiro de 0 a 100 representando a intensidade/certeza"
            " desse sentimento.\n3. 'assunto_principal': string com o resumo do"
            " tema central.\n4. 'pessoas_citadas': lista de strings contendo os"
            " nomes das pessoas mencionadas no texto (vazia se nenhuma).\n5."
            " 'nivel_de_urgencia': string restrita a exatamente uma das"
            " opções: 'Baixo', 'Medio', 'Alto'."
        )

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": texto_usuario},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        conteudo_resposta = response.choices[0].message.content
        dados_json = json.loads(conteudo_resposta)

        st.success("✅ Processamento concluído com sucesso!")
        st.divider()

        # ==============================================================================
        # EXIBIÇÃO DOS RESULTADOS
        # ==============================================================================
        st.subheader("📊 Resultados da Análise")

        col1, col2, col3 = st.columns(3)

        sentimento = dados_json
