@echo off
chcp 65001 >nul
title 马赛克去除工具
echo ========================================
echo    马赛克去除工具 - 启动中...
echo ========================================
echo.

:: 启动服务器并打开浏览器
start /b python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

:: 等待服务器启动
timeout /t 3 /nobreak >nul

:: 打开浏览器
start http://localhost:8000

echo.
echo 服务器已启动！
echo 浏览器已打开！
echo.
echo 按任意键停止服务器...
pause >nul

:: 停止服务器
taskkill /f /im python.exe >nul 2>&1
echo 服务器已停止
