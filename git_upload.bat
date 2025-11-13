@echo off
chcp 65001 >nul
echo ========================================
echo 上传项目到 GitHub 主分支
echo ========================================
echo.

cd /d "%~dp0"

echo [1/6] 检查 Git 是否已安装...
git --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Git 未安装或不在 PATH 中
    pause
    exit /b 1
)
echo Git 已安装
echo.

echo [2/6] 初始化 Git 仓库（如果尚未初始化）...
if not exist .git (
    git init
    echo Git 仓库已初始化
) else (
    echo Git 仓库已存在
)
echo.

echo [3/6] 检查远程仓库...
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo 添加远程仓库...
    git remote add origin git@github.com:schrodinger12138/AIMind_Card.git
    echo 远程仓库已添加
) else (
    echo 更新远程仓库地址...
    git remote set-url origin git@github.com:schrodinger12138/AIMind_Card.git
    echo 远程仓库地址已更新
)
echo.

echo [4/6] 添加所有文件到暂存区...
git add .
if errorlevel 1 (
    echo 错误: 添加文件失败
    pause
    exit /b 1
)
echo 文件已添加到暂存区
echo.

echo [5/6] 提交更改...
git commit -m "Initial commit: AI Mind Card project"
if errorlevel 1 (
    echo 警告: 提交可能失败（可能是没有更改或已是最新）
)
echo.

echo [6/6] 推送到 GitHub 主分支...
echo 注意: 如果这是第一次推送，可能需要设置 SSH 密钥
echo 如果遇到权限问题，请检查 SSH 密钥配置
echo.
git push -u origin main
if errorlevel 1 (
    echo.
    echo 尝试推送到 master 分支...
    git push -u origin master
    if errorlevel 1 (
        echo.
        echo ========================================
        echo 推送失败！可能的原因：
        echo 1. SSH 密钥未配置
        echo 2. 网络连接问题
        echo 3. 仓库权限问题
        echo.
        echo 请检查：
        echo - SSH 密钥: ssh -T git@github.com
        echo - 远程地址: git remote -v
        echo ========================================
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo 上传完成！
echo ========================================
echo.
echo 仓库地址: git@github.com:schrodinger12138/AIMind_Card.git
echo.
pause

