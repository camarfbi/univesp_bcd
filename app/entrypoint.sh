#!/bin/bash

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate

# Instale as dependências
pip install --no-cache-dir -r requirements.txt

# Execute o script Python
python script.py
