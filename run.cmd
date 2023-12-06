flask run --reload --debugger --host 0.0.0.0 --port 5000
exit /b 0
:LOCAL
echo %myip% run
rem 切換工作目錄至批次檔
cd /d "%~dp0"
echo start waitress
set FLASK_ENV=development
set FLASK_APP=main.py
flask run --reload --debugger --host 0.0.0.0 --port 80
exit /b 0