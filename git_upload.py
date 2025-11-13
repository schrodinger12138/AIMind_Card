#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
上传项目到 GitHub 主分支
"""
import subprocess
import sys
import os

def run_command(cmd, check=True):
    """执行命令并返回结果"""
    print(f"执行: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=check,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"错误: {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False, e.stdout if hasattr(e, 'stdout') else '', e.stderr if hasattr(e, 'stderr') else ''

def main():
    print("=" * 50)
    print("上传项目到 GitHub 主分支")
    print("=" * 50)
    print()
    
    # 检查代理配置
    print("检查 Git 代理配置...")
    proxy_check = subprocess.run(
        "git config --global --get http.proxy",
        shell=True,
        capture_output=True,
        text=True
    )
    if proxy_check.returncode == 0 and proxy_check.stdout.strip():
        print(f"当前 HTTP 代理: {proxy_check.stdout.strip()}")
    else:
        print("未配置 HTTP 代理")
        print("提示: 如果需要使用代理，请先运行 setup_git_proxy_7898.py")
    print()
    
    # 切换到项目目录
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    print(f"工作目录: {project_dir}")
    print()
    
    # 1. 检查 Git 是否已安装
    print("[1/6] 检查 Git 是否已安装...")
    success, _, _ = run_command("git --version", check=False)
    if not success:
        print("错误: Git 未安装或不在 PATH 中")
        sys.exit(1)
    print("Git 已安装")
    print()
    
    # 2. 初始化 Git 仓库（如果尚未初始化）
    print("[2/6] 初始化 Git 仓库（如果尚未初始化）...")
    if not os.path.exists('.git'):
        success, _, _ = run_command("git init")
        if success:
            print("Git 仓库已初始化")
        else:
            print("错误: 初始化 Git 仓库失败")
            sys.exit(1)
    else:
        print("Git 仓库已存在")
    print()
    
    # 3. 检查并设置远程仓库
    print("[3/6] 检查远程仓库...")
    remote_url = "git@github.com:schrodinger12138/AIMind_Card.git"
    success, output, _ = run_command("git remote get-url origin", check=False)
    if not success:
        print("添加远程仓库...")
        success, _, _ = run_command(f"git remote add origin {remote_url}")
        if success:
            print("远程仓库已添加")
        else:
            print("错误: 添加远程仓库失败")
            sys.exit(1)
    else:
        print("更新远程仓库地址...")
        success, _, _ = run_command(f"git remote set-url origin {remote_url}")
        if success:
            print("远程仓库地址已更新")
        else:
            print("警告: 更新远程仓库地址失败，继续...")
    print()
    
    # 4. 添加所有文件到暂存区
    print("[4/6] 添加所有文件到暂存区...")
    success, _, _ = run_command("git add .")
    if not success:
        print("错误: 添加文件失败")
        sys.exit(1)
    print("文件已添加到暂存区")
    print()
    
    # 5. 提交更改
    print("[5/6] 提交更改...")
    success, _, _ = run_command('git commit -m "Update: AI Mind Card project"', check=False)
    if success:
        print("更改已提交")
    else:
        print("警告: 提交可能失败（可能是没有更改或已是最新）")
    print()
    
    # 6. 推送到 GitHub 主分支
    print("[6/6] 推送到 GitHub 主分支...")
    print("注意: 如果这是第一次推送，可能需要设置 SSH 密钥")
    print("如果遇到权限问题，请检查 SSH 密钥配置")
    print()
    
    # 先尝试推送到 main 分支
    success, _, _ = run_command("git push -u origin main", check=False)
    if not success:
        # 如果 main 分支不存在，尝试 master
        print("尝试推送到 master 分支...")
        success, _, _ = run_command("git push -u origin master", check=False)
        if not success:
            print()
            print("=" * 50)
            print("推送失败！可能的原因：")
            print("1. SSH 密钥未配置")
            print("2. 网络连接问题")
            print("3. 仓库权限问题")
            print()
            print("请检查：")
            print(f"- SSH 密钥: ssh -T git@github.com")
            print(f"- 远程地址: git remote -v")
            print("=" * 50)
            sys.exit(1)
    
    print()
    print("=" * 50)
    print("上传完成！")
    print("=" * 50)
    print()
    print(f"仓库地址: {remote_url}")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n发生错误: {e}")
        sys.exit(1)

