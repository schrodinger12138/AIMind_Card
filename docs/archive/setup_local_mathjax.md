# 设置本地MathJax（离线使用）

## 方法1：使用npm安装（推荐）

```bash
# 在项目根目录
npm init -y
npm install mathjax@3

# 或使用yarn
yarn add mathjax@3
```

安装后，MathJax会在 `node_modules/mathjax/` 目录。

## 方法2：手动下载

1. 访问：https://github.com/mathjax/MathJax/releases
2. 下载最新版本
3. 解压到项目目录的 `mathjax/` 文件夹

## 修改代码使用本地MathJax

修改 `markdown_preview.py` 中的MathJax路径：

```python
# 从CDN改为本地
# 原代码：
# <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

# 改为本地（假设MathJax在项目根目录的mathjax文件夹）：
# <script src="file:///path/to/mathjax/es5/tex-mml-chtml.js"></script>
```

## 使用QUrl加载本地文件

在Python中，需要使用QUrl来加载本地MathJax文件。

