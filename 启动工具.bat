@echo off
chcp 65001 >nul
title 马赛克去除工具

echo.
echo ========================================
echo     马赛克去除工具 - 启动中...
echo ========================================
echo.

cd /d "%~dp0"
python 启动工具.pyw

if errorlevel 1 (
    echo.
    echo 启动失败！请检查Python是否正确安装。
    echo.
    pause
)
