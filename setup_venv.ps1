# PowerShell script para criar e ativar venv no Windows, atualizar pip e instalar requirements
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
