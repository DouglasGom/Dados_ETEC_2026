@echo off
:: Inicia o navegador
start http://localhost:8501

:: Inicia o servidor do Streamlit
:: O "python -m" garante que ele use o Python correto instalado na máquina
C:\Users\namik\AppData\Local\Python\pythoncore-3.14-64\python.exe -m streamlit run app.py

pause