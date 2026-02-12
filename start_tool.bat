@echo off
chcp 65001 >nul
echo ========================================
echo  Brown Dust 2 - Mod 比較工具
echo ========================================
echo.
echo  啟動本地伺服器中...
echo  伺服器位址: http://localhost:8000
echo  按 Ctrl+C 停止伺服器
echo ========================================
echo.

start http://localhost:8000/ModComparisonTools/mod_viewer.html
python "%~dp0ModComparisonTools\mod_index_server.py"
