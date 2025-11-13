@echo off
chcp 65001 >nul
echo ========================================
echo V2Ray 代理配置工具
echo ========================================
echo.
echo 注意：Windows Git 不支持 SOCKS5，需要使用 HTTP 代理
echo V2Ray 的 HTTP 代理端口通常是：10809, 8080, 7890 等
echo.
set /p proxy_port="请输入 V2Ray HTTP 代理端口（默认 10809）: "
if "%proxy_port%"=="" set proxy_port=10809

echo.
echo 配置 Git 使用 HTTP 代理: http://127.0.0.1:%proxy_port%
git config --global http.proxy http://127.0.0.1:%proxy_port%
git config --global https.proxy http://127.0.0.1:%proxy_port%

echo.
echo 当前代理配置：
git config --global --get http.proxy
git config --global --get https.proxy

echo.
echo ========================================
echo 配置完成！请确保 V2Ray 正在运行
echo ========================================
echo.
echo 测试连接：
git ls-remote https://github.com/schrodinger12138/AIMind_Card.git
echo.
pause

