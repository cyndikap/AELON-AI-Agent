# 
AV Bancaire Multi-Agents

This project's goal is to build a multi agent system aiming at the resolution of technical issues encountered by the clients in the banking sector.

## Local Environment

Use the repository virtual environment only.

### Bootstrap

```powershell
Set-Location C:/Users/csileuka/AI.Agent.memoire/GEN.AI
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap-ui.ps1
```

### Run the UI

```powershell
Set-Location C:/Users/csileuka/AI.Agent.memoire/GEN.AI
powershell -ExecutionPolicy Bypass -File .\scripts\run-ui.ps1
```

### Notes

- The workspace is configured to use `.venv` as the default interpreter.
- `PYTHONNOUSERSITE=1` is enforced to prevent conflicts with packages installed under AppData.
- Privacy dependencies are installed in the local environment together with the required spaCy models.

###
###python -m venv .venv
###.venv\Scripts\Activate.ps14 
###pip install -r requirements.txt
###python -m streamlit run UI/app.py