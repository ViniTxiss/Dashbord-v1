# ⚖️ LegalInsights Dashboard

Dashboard de inteligência jurídica de alta performance construído com Streamlit, Pandas e Plotly.

## 🚀 Como executar localmente

1. **Clone o repositório**
2. **Crie um ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   .\venv\Scripts\activate   # Windows
   ```
3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Execute o App:**
   ```bash
   streamlit run app.py
   ```

## 🐳 Deploy com Docker

Para garantir que o app rode em qualquer lugar (AWS, Google Cloud, Azure), use o Docker:

1. **Build da imagem:**
   ```bash
   docker build -t legal-dashboard .
   ```
2. **Executar o container:**
   ```bash
   docker run -p 8501:8501 legal-dashboard
   ```
3. **Acesse em:** `http://localhost:8501`

## 📊 Estrutura de Dados
O app espera um arquivo `dados_juridicos.xlsx`. Se não existir, o script `gerar_dados.py` criará um automaticamente para demonstração.

## 🛠️ Stack Tecnológica
- **Python 3.10+**
- **Streamlit** (Interface)
- **Pandas** (Processamento)
- **Plotly** (Gráficos Interativos)
- **Docker** (Deployment)
