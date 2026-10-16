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
# INSTRUÇÕES DIDÁTICAS: COMO CONFIGURAR AS CREDENCIAIS LOCALMENTE
# ==============================================================================
"""
COMO CONFIGURAR O ARQUIVO .streamlit/secrets.toml LOCALMENTE:
------------------------------------------------------------------------------
Para que este aplicativo funcione, você deve criar uma pasta chamada '.streamlit' 
na mesma raiz onde está o seu arquivo 'app.py' e, dentro dela, criar um arquivo 
chamado 'secrets.toml' com a seguinte estrutura:

[azure_openai]
api_key = "SUA_CHAVE_DE_API_AQUI"
endpoint = "https://seu-recurso.services.ai.azure.com/"
model_name = "gpt-4.1-mini"
------------------------------------------------------------------------------
"""

# ==============================================================================
# ESTILIZAÇÃO CSS MODERNA
# ==============================================================================
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.5rem;
        color: #0078D4;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #605E5C;
        margin-bottom: 30px;
    }
    .stButton>button {
        width: 100%;
        background-color: #0078D4;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        height: 45px;
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
# CABEÇALHO DO APLICATIVO
# ==============================================================================
st.markdown(
    '<p class="main-title">🤖 Extrator de Dados Inteligente</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">Powered by Microsoft Azure OpenAI & Python</p>',
    unsafe_allow_html=True,
)

# ==============================================================================
# BARRA LATERAL (INFORMAÇÕES E CONFIGURAÇÕES)
# ==============================================================================
with st.sidebar:
  st.header("⚙️ Configurações & Ajuda")
  st.info(
      "Este aplicativo analisa textos utilizando o modelo configurado no Azure"
      " Foundry e retorna um JSON estruturado com sentimento, assunto,"
      " pessoas citadas e nível de urgência."
  )

  with st.expander("Ver modelo de Secrets.toml"):
    st.code(
        """[azure_openai]
api_key = "SUA_CHAVE_AQUI"
endpoint = "https://seu-endpoint.services.ai.azure.com/"
model_name = "gpt-4.1-mini""",
        language="toml",
    )

# ==============================================================================
# ÁREA DE ENTRADA DO USUÁRIO
# ==============================================================================
st.subheader("📝 Digite ou cole o texto para análise:")
texto_usuario = st.text_area(
    "Texto fonte:",
    height=150,
    placeholder=(
        "Exemplo: 'Reunião urgente marcada com Carlos e Ana amanhã às 14h para"
        " resolver o atraso crítico no projeto alpha...'"
    ),
)

# Botão de Processamento
if st.button("🚀 Processar Texto"):
  if not texto_usuario.strip():
    st.warning("⚠️ Por favor, insira algum texto antes de clicar em Processar.")
  else:
    # Tentativa de carregar credenciais via Streamlit Secrets
    try:
      api_key = st.secrets["azure_openai"]["api_key"]
      endpoint = st.secrets["azure_openai"]["endpoint"]
      model_name = st.secrets["azure_openai"]["model_name"]
    except Exception:
      # Fallback didático direto para fins de teste imediato fornecidos no prompt
      # ATENÇÃO: Em produção, utilize sempre o st.secrets ou variáveis de ambiente.
      api_key = (
          "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os"
      )
      endpoint = "https://marcelomaffeis-05082026-resource.services.ai.azure.com/"
      model_name = "gpt-4.1-mini"

    # Correção de URL caso contenha caracteres indesejados de encoding (&quot;)
    endpoint = endpoint.replace("&quot;", "").strip()

    with st.spinner(
        "🔄 Enviando dados para o Azure OpenAI e processando modelo..."
    ):
      try:
        # Inicialização do Cliente Oficial Azure OpenAI
        client = AzureOpenAI(
            api_key=api_key,
            api_version="2024-08-01-preview",  # Versão padrão recomendada para endpoints Azure OpenAI
            azure_endpoint=endpoint,
        )

        # System Prompt rígido garantindo o contrato estrito em JSON
        system_prompt = (
            "Você é um assistente especialista em extração de dados e análise de"
            " texto. Sua tarefa é analisar o texto fornecido pelo usuário e"
            " retornar ESTRITAMENTE um objeto JSON válido (sem blocos de código"
            " markdown adicionais, sem texto antes ou depois) contendo exatas 4"
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
            response_format={"type": "json_object"},  # Força resposta em JSON
            temperature=0.1,  # Baixa temperatura para maior determinismo
        )

        # Extração e parsing do conteúdo JSON retornado
        conteudo_resposta = response.choices[0].message.content
        dados_json = json.loads(conteudo_resposta)

        st.success("✅ Processamento concluído com sucesso!")
        st.divider()

        # ==============================================================================
        # EXIBIÇÃO ESTRUTURADA DA INTERFACE
        # ==============================================================================
        st.subheader("📊 Resultados da Análise Inteligente")

        # Layout em colunas para st.metric e resumos rápidos
        col1, col2, col3 = st.columns(3)

        sentimento = dados_json.get("sentimento", "N/A")
        porcentagem = dados_json.get("porcentagem_sentimento", 0)
        urgencia = dados_json.get("nivel_de_urgencia", "Baixo")

        with col1:
          st.metric(
              label="Sentimento Identificado",
              value=sentimento,
              delta=f"{porcentagem}% de intensidade",
          )

        with col2:
          # Cor dinâmica simulada no status do nível de urgência
          st.metric(label="Nível de Urgência", value=urgencia)

        with col3:
          pessoas = dados_json.get("pessoas_citadas", [])
          st.metric(
              label="Pessoas Citadas",
              value=len(pessoas),
              delta=(
                  ", ".join(pessoas)
                  if pessoas
                  else "Nenhuma pessoa identificada"
              ),
          )

        st.markdown("<br>", unsafe_allow_html=True)

        # Detalhes do Assunto Principal
        st.markdown("### 📌 Assunto Principal")
        st.info(
            dados_json.get(
                "assunto_principal", "Nenhum assunto principal retornado."
            )
        )

        # Exibição do JSON bruto completo para auditoria
        with st.expander("🔍 Ver JSON Bruto Retornado pela API"):
          st.json(dados_json)

      except Exception as e:
        st.error(
            "❌ Ocorreu um erro ao comunicar com a API do Azure OpenAI:"
            f" {str(e)}"
        )
        st.info(
            "Verifique se o seu Endpoint, Chave de API e Nome do Modelo estão"
            " corretos no arquivo `.streamlit/secrets.toml`."
        )
