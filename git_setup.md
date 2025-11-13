# Git 上传指南

## 1. 初始化 Git 仓库（如果还没有）

```bash
git init
```

## 2. 添加远程仓库

```bash
git remote add origin https://github.com/schrodinger12138/AIMind_Card.git
```

如果远程仓库已存在，使用：
```bash
git remote set-url origin https://github.com/schrodinger12138/AIMind_Card.git
```

## 3. 添加所有文件

```bash
git add .
```

## 4. 提交更改

```bash
git commit -m "Initial commit: AI阅读卡片思维导图工具"
```

## 5. 推送到主分支

```bash
git branch -M main
git push -u origin main
```

## 注意事项

- 确保 `.gitignore` 已正确配置，避免上传不必要的文件
- 如果仓库已有内容，可能需要先拉取：`git pull origin main --allow-unrelated-histories`
- 如果遇到认证问题，可能需要配置 GitHub 的访问令牌

