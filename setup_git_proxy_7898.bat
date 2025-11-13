@echo off
chcp 65001 >nul
echo ========================================
echo 配置 Git 代理 (端口 7898)
echo ========================================
echo.

echo [1/3] 设置 HTTP 代理...
git config --global http.proxy http://127.0.0.1:7898
if errorlevel 1 (
    echo 错误: 设置 HTTP 代理失败
    pause
    exit /b 1
)
echo HTTP 代理已设置: http://127.0.0.1:7898
echo.

echo [2/3] 设置 HTTPS 代理...
git config --global https.proxy http://127.0.0.1:7898
if errorlevel 1 (
    echo 错误: 设置 HTTPS 代理失败
    pause
    exit /b 1
)
echo HTTPS 代理已设置: http://127.0.0.1:7898
echo.

echo [3/3] 验证代理配置...
echo.
echo 当前 Git 代理配置:
git config --global --get http.proxy
git config --global --get https.proxy
echo.

echo ========================================
echo 代理配置完成！
echo ========================================
echo.
echo 注意: 
echo - 如果使用 SSH 连接 (git@github.com)，需要配置 SSH 代理
echo - 如果使用 HTTPS 连接，上述配置已生效
echo.
echo 测试连接:
echo git ls-remote git@github.com:schrodinger12138/AIMind_Card.git
echo.
pause

