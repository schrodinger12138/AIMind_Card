# 开发分支工作流程

## 分支策略

- **main**: 主分支，用于生产环境
- **develop**: 开发分支，用于日常开发

## 开发分支操作

### 1. 克隆仓库（如果还没有）

```bash
git clone https://github.com/schrodinger12138/AIMind_Card.git
cd AIMind_Card
```

### 2. 创建并切换到开发分支

```bash
# 创建并切换到 develop 分支
git checkout -b develop

# 或者如果远程已有 develop 分支
git checkout -b develop origin/develop
```

### 3. 日常开发流程

```bash
# 1. 确保在 develop 分支
git checkout develop

# 2. 拉取最新代码
git pull origin develop

# 3. 创建功能分支（可选，推荐）
git checkout -b feature/功能名称

# 4. 进行开发...

# 5. 提交更改
git add .
git commit -m "feat: 添加新功能描述"

# 6. 推送到远程
git push origin develop
# 或推送功能分支
git push origin feature/功能名称
```

### 4. 合并到主分支（发布时）

```bash
# 1. 切换到 main 分支
git checkout main

# 2. 拉取最新代码
git pull origin main

# 3. 合并 develop 分支
git merge develop

# 4. 推送到远程
git push origin main

# 5. 切换回 develop 继续开发
git checkout develop
```

## 分支命名规范

- `develop` - 开发分支
- `feature/功能名称` - 功能分支
- `bugfix/问题描述` - 修复分支
- `hotfix/紧急修复` - 紧急修复分支

## 提交信息规范

- `feat:` - 新功能
- `fix:` - 修复bug
- `docs:` - 文档更新
- `style:` - 代码格式调整
- `refactor:` - 代码重构
- `test:` - 测试相关
- `chore:` - 构建/工具相关

