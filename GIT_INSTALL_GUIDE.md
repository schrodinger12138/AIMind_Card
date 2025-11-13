# Git 安装和配置指南

## 问题
系统未检测到 Git 命令，需要先安装 Git。

## 解决方案

### 方法一：安装 Git for Windows（推荐）

1. **下载 Git**
   - 访问：https://git-scm.com/download/win
   - 下载最新版本的 Git for Windows
   - 或者使用包管理器安装：
     ```powershell
     # 使用 Chocolatey
     choco install git
     
     # 使用 winget
     winget install --id Git.Git -e --source winget
     ```

2. **安装后重启终端**
   - 关闭当前 PowerShell/CMD 窗口
   - 重新打开终端
   - 验证安装：`git --version`

3. **配置 Git（首次使用）**
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

### 方法二：使用 GitHub Desktop

1. 下载并安装 GitHub Desktop：https://desktop.github.com/
2. 使用图形界面进行 Git 操作

### 方法三：使用 Conda 安装 Git

如果已安装 Conda/Miniconda：
```bash
conda install -c conda-forge git
```

## 安装完成后

重新运行 `git_push.bat` 或执行以下命令：

```bash
git init
git remote add origin https://github.com/schrodinger12138/AIMind_Card.git
git add .
git commit -m "Initial commit: AI阅读卡片思维导图工具"
git branch -M main
git push -u origin main
```

## 注意事项

- 首次推送到 GitHub 需要身份验证
- 推荐使用 Personal Access Token（PAT）而不是密码
- 生成 PAT：GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)

