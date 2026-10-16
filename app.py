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
    page_title="Extrator de Dados Inteligente | Azure OpenAI",
    page_icon="🤖",
    layout="wide",
)

# ==============================================================================
# ESTILIZAÇÃO CSS CUSTOMIZADA
# ==============================================================================
st.markdown(
    """
    <style>
    /* Estilização de cabeçalhos */
    .main-title {
        font-size: 2.2rem;
        color: #0078D4;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1rem;
        color: #605E5C;
        margin-bottom: 25px;
    }
    /* Estilização do botão principal */
    .stButton>button {
        width: 100%;
        background-color: #0078D4;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        height: 45px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #106EBE;
        color: white;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# CABEÇALHO DA APLICAÇÃO
# ==============================================================================
st.markdown(
    '<p class="main-title">🤖 Extrator de Dados Inteligente</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">Powered by Microsoft Azure OpenAI & Python</p>',
    unsafe_allow_html=True,
)
st.divider()

# ==============================================================================
# BARRA LATERAL (INSTRUÇÕES E CONFIGURAÇÃO)
# ==============================================================================
with st.sidebar:
  st.header("⚙️ Configurações & Ajuda")
  st.info(
      "Este aplicativo analisa textos utilizando o modelo configurado no Azure"
      " OpenAI e extrai dados estruturados como sentimento, assunto, pessoas"
      " citadas e nível de urgência."
  )

  with st.expander("📖 Como configurar o secrets.toml"):
    st.markdown("""
        Crie a pasta **`.streamlit`** na raiz do projeto e dentro dela o arquivo **`secrets.toml`**:
        """)
    st.code(
        """[azure_openai]
api_key = "SUA_CHAVE_DE_API"
endpoint = "https://seu-recurso.services.ai.azure.com/"
model_name = "gpt-4.1-mini"
""",
        language="toml",
    )

# ==============================================================================
# ENTRADA DE DADOS
# ==============================================================================
st.subheader("📝 Digite ou cole o texto para análise")
texto_usuario = st.text_area(
    label="Texto fonte:",
    height=150,
    placeholder=(
        "Exemplo: 'Reunião urgente marcada com Carlos e Ana amanhã às 14h para"
        " resolver o atraso crítico no projeto Alpha...'"
    ),
    label_visibility="collapsed",
)

# Botão de Ação
if st.button("🚀 Processar Texto"):
  if not texto_usuario.strip():
    st.warning("⚠️ Por favor, insira algum texto antes de clicar em Processar.")
  else:
    # 1. Tentar ler do secrets.toml
    try:
      api_key = st.secrets["azure_openai"]["api_key"]
      endpoint = st.secrets["azure_openai"]["endpoint"]
      model_name = st.secrets["azure_openai"]["model_name"]
    except Exception:
      # Fallback de credenciais fornecidas no prompt
      api_key = (
          "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os"
      )
      endpoint = (
          "https://marcelomaffeis-05082026-resource.services.ai.azure.com/"
      )
      model_name = "gpt-4.1-mini"

    # Sanitizar endpoint contra aspas e códigos HTML
    endpoint = endpoint.replace("&quot;", "").replace('"', "").strip()

    with st.spinner("🔄 Processando análise no Azure OpenAI..."):
      try:
        # Inicializar Cliente Azure OpenAI
        client = AzureOpenAI(
            api_key=api_key,
            api_version="2024-08-01-preview",
            azure_endpoint=endpoint,
        )

        system_prompt = (
            "Você é um assistente especialista em extração de dados e análise de"
            " texto. Sua tarefa é analisar o texto fornecido pelo usuário e"
            " retornar ESTRITAMENTE um objeto JSON válido (sem blocos de código"
            " markdown adicionais, sem texto antes ou depois) contendo exatas"
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

        # Exibição das métricas em 3 colunas
        col1, col2, col3 = st.columns(3)

        sentimento = dados_json.get("sentimento", "N/A")
        porcentagem = dados_json.get("porcentagem_sentimento", 0)
        urgencia = dados_json.get("nivel_de_urgencia", "Baixo")
        pessoas = dados_json.get("pessoas_citadas", [])

        with col1:
          st.metric(
              label="Sentimento Identificado",
              value=sentimento,
              delta=f"{porcentagem}% intensidade",
          )

        with col2:
          st.metric(label="Nível de Urgência", value=urgencia)

        with col3:
          st.metric(
              label="Pessoas Citadas",
              value=f"{len(pessoas)} encontrada(s)",
              delta=", ".join(pessoas) if pessoas else "Nenhuma pessoa",
          )

        st.markdown("<br>", unsafe_allow_html=True)

        # Assunto Principal
        st.markdown("### 📌 Assunto Principal")
        st.info(
            dados_json.get("assunto_principal", "Nenhum assunto retornado.")
        )

        # JSON Bruto
        with st.expander("🔍 Ver JSON retornado pela API"):
          st.json(dados_json)

      except Exception as e:
        st.error(f"❌ Erro ao comunicar com a API do Azure OpenAI: {str(e)}")
