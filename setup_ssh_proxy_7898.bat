@echo off
chcp 65001 >nul
echo ========================================
echo 配置 SSH 代理 (端口 7898)
echo ========================================
echo.

echo 注意: SSH 代理需要配置 ~/.ssh/config 文件
echo.

set SSH_CONFIG=%USERPROFILE%\.ssh\config

echo [1/3] 检查 .ssh 目录...
if not exist "%USERPROFILE%\.ssh" (
    mkdir "%USERPROFILE%\.ssh"
    echo .ssh 目录已创建
) else (
    echo .ssh 目录已存在
)
echo.

echo [2/3] 配置 SSH config...
echo.
echo 将添加以下配置到 %SSH_CONFIG%:
echo.
echo Host github.com
echo     ProxyCommand connect -H 127.0.0.1:7898 %%h %%p
echo     Hostname github.com
echo     Port 22
echo     User git
echo.

set /p confirm=是否继续? (Y/N): 
if /i not "%confirm%"=="Y" (
    echo 已取消
    pause
    exit /b 0
)

echo.
echo [3/3] 写入 SSH 配置...

REM 检查是否已有 github.com 配置
findstr /C:"Host github.com" "%SSH_CONFIG%" >nul 2>&1
if errorlevel 1 (
    echo. >> "%SSH_CONFIG%"
    echo # GitHub proxy configuration >> "%SSH_CONFIG%"
    echo Host github.com >> "%SSH_CONFIG%"
    echo     ProxyCommand connect -H 127.0.0.1:7898 %%h %%p >> "%SSH_CONFIG%"
    echo     Hostname github.com >> "%SSH_CONFIG%"
    echo     Port 22 >> "%SSH_CONFIG%"
    echo     User git >> "%SSH_CONFIG%"
    echo SSH 配置已添加
) else (
    echo 警告: github.com 配置已存在，请手动编辑 %SSH_CONFIG%
    echo 添加以下内容:
    echo.
    echo Host github.com
    echo     ProxyCommand connect -H 127.0.0.1:7898 %%h %%p
    echo     Hostname github.com
    echo     Port 22
    echo     User git
)

echo.
echo ========================================
echo SSH 代理配置完成！
echo ========================================
echo.
echo 注意: 
echo - 需要安装 connect 工具 (Git for Windows 自带)
echo - 或者使用其他代理工具如 nc (netcat)
echo.
echo 测试连接:
echo ssh -T git@github.com
echo.
pause

