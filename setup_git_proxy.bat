@echo off
chcp 65001 >nul
echo ========================================
echo Git 代理配置工具
echo ========================================
echo.

echo 请选择代理配置方式：
echo 1. 使用 Clash/V2Ray 等代理工具（默认端口 7890）
echo 2. 使用自定义代理地址
echo 3. 仅对 GitHub 设置代理
echo 4. 取消代理设置
echo.
set /p choice="请输入选项 (1-4): "

if "%choice%"=="1" (
    echo.
    echo 配置 Clash/V2Ray 代理（127.0.0.1:7890）...
    git config --global http.proxy http://127.0.0.1:7890
    git config --global https.proxy http://127.0.0.1:7890
    echo 代理已设置为: http://127.0.0.1:7890
    goto :end
)

if "%choice%"=="2" (
    echo.
    set /p proxy_url="请输入代理地址（格式：http://127.0.0.1:端口）: "
    git config --global http.proxy %proxy_url%
    git config --global https.proxy %proxy_url%
    echo 代理已设置为: %proxy_url%
    goto :end
)

if "%choice%"=="3" (
    echo.
    set /p proxy_url="请输入代理地址（格式：http://127.0.0.1:端口）: "
    git config --global http.https://github.com.proxy %proxy_url%
    echo GitHub 代理已设置为: %proxy_url%
    goto :end
)

if "%choice%"=="4" (
    echo.
    echo 取消代理设置...
    git config --global --unset http.proxy
    git config --global --unset https.proxy
    git config --global --unset http.https://github.com.proxy
    echo 代理设置已取消
    goto :end
)

echo 无效选项！
goto :end

:end
echo.
echo 当前 Git 代理配置：
git config --global --get http.proxy
git config --global --get https.proxy
git config --global --get http.https://github.com.proxy
echo.
echo ========================================
echo 配置完成！
echo ========================================
pause

