# V2Ray 代理配置指南

## 问题说明

Windows 上的 Git 不支持 SOCKS5 代理，需要使用 HTTP 代理。

## 步骤 1：检查 V2Ray 的 HTTP 代理端口

1. 打开 V2Ray 客户端（如 V2RayN）
2. 查看"参数设置"或"系统代理设置"
3. 找到 **HTTP 代理端口**（不是 SOCKS5 端口）
   - 常见端口：`10809`, `8080`, `7890`, `1080`
   - 不同客户端默认端口可能不同

## 步骤 2：配置 Git 代理

### 方法 1：使用脚本（推荐）

运行 `setup_v2ray_proxy.bat`，输入你的 V2Ray HTTP 代理端口。

### 方法 2：手动配置

```bash
# 替换 <端口> 为你的 V2Ray HTTP 代理端口
git config --global http.proxy http://127.0.0.1:<端口>
git config --global https.proxy http://127.0.0.1:<端口>
```

### 方法 3：仅对 GitHub 设置代理

```bash
git config --global http.https://github.com.proxy http://127.0.0.1:<端口>
```

## 步骤 3：验证配置

```bash
# 查看当前配置
git config --global --get http.proxy
git config --global --get https.proxy

# 测试连接
git ls-remote https://github.com/schrodinger12138/AIMind_Card.git
```

## 步骤 4：推送代码

```bash
git push -u origin develop
```

## 常见问题

### 1. 连接失败

- **检查 V2Ray 是否运行**：确保 V2Ray 客户端正在运行
- **检查端口是否正确**：确认使用的是 HTTP 代理端口，不是 SOCKS5 端口
- **检查防火墙**：确保防火墙允许 Git 访问本地代理

### 2. 认证失败

如果出现认证错误，需要：

1. **使用 Personal Access Token**（推荐）：
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - 生成新 token，勾选 `repo` 权限
   - 推送时使用 token 作为密码

2. **使用 SSH 方式**（推荐）：
   ```bash
   # 切换到 SSH URL
   git remote set-url origin git@github.com:schrodinger12138/AIMind_Card.git
   ```

### 3. 取消代理设置

```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

## 替代方案：使用 SSH

如果代理配置困难，可以使用 SSH 方式：

```bash
# 1. 生成 SSH 密钥（如果还没有）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. 将公钥添加到 GitHub
# 复制 ~/.ssh/id_ed25519.pub 的内容到 GitHub → Settings → SSH and GPG keys

# 3. 切换远程仓库为 SSH
git remote set-url origin git@github.com:schrodinger12138/AIMind_Card.git

# 4. 推送
git push -u origin develop
```

