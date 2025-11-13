@echo off
chcp 65001 >nul
echo ========================================
echo 设置开发分支
echo ========================================
echo.

REM 检查是否已初始化 git
if not exist .git (
    echo 初始化 Git 仓库...
    git init
    echo.
    
    REM 添加远程仓库
    echo 添加远程仓库...
    git remote add origin https://github.com/schrodinger12138/AIMind_Card.git
    echo.
)

REM 检查是否已有提交
git rev-parse --verify HEAD >nul 2>&1
if errorlevel 1 (
    echo 首次提交，添加所有文件...
    git add .
    git commit -m "Initial commit: AI阅读卡片思维导图工具"
    echo.
)

REM 创建并切换到 develop 分支
echo 创建并切换到 develop 分支...
git checkout -b develop
echo.

REM 推送到远程（如果远程已有内容，先拉取）
echo 推送到远程仓库...
git push -u origin develop
echo.

echo ========================================
echo 开发分支设置完成！
echo 当前分支: develop
echo ========================================
echo.
echo 提示：
echo - 日常开发在 develop 分支进行
echo - 使用 git checkout develop 切换到开发分支
echo - 使用 git push origin develop 推送更改
echo.
pause

