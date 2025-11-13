@echo off
chcp 65001 >nul
echo ========================================
echo Git 上传到 GitHub
echo ========================================
echo.

REM 检查是否已初始化 git
if not exist .git (
    echo 初始化 Git 仓库...
    git init
    echo.
)

REM 检查远程仓库
git remote -v >nul 2>&1
if errorlevel 1 (
    echo 添加远程仓库...
    git remote add origin https://github.com/schrodinger12138/AIMind_Card.git
) else (
    echo 更新远程仓库地址...
    git remote set-url origin https://github.com/schrodinger12138/AIMind_Card.git
)
echo.

echo 添加所有文件到暂存区...
git add .
echo.

echo 提交更改...
git commit -m "Initial commit: AI阅读卡片思维导图工具 - 重构和优化版本"
echo.

echo 设置主分支...
git branch -M main
echo.

echo 推送到 GitHub...
echo 注意：如果这是第一次推送，可能需要输入 GitHub 用户名和密码/令牌
git push -u origin main
echo.

echo ========================================
echo 完成！
echo ========================================
pause

