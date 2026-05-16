# Cria o ambiente virtual
python -m venv .venv

# Ativa o ambiente virtual (Linux/macOS)
source .venv/bin/activate
# Se estiver no Windows (PowerShell), use: .venv\Scripts\activate

# Instala as bibliotecas que vamos usar
pip install "fastapi[standard]" motor httpx python-dotenv