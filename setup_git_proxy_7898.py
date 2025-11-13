#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置 Git 代理 (端口 7898)
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
            print(result.stdout.strip())
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
    print("配置 Git 代理 (端口 7898)")
    print("=" * 50)
    print()
    
    proxy_url = "http://127.0.0.1:7898"
    
    # 1. 设置 HTTP 代理
    print("[1/3] 设置 HTTP 代理...")
    success, _, _ = run_command(f"git config --global http.proxy {proxy_url}")
    if success:
        print(f"HTTP 代理已设置: {proxy_url}")
    else:
        print("错误: 设置 HTTP 代理失败")
        sys.exit(1)
    print()
    
    # 2. 设置 HTTPS 代理
    print("[2/3] 设置 HTTPS 代理...")
    success, _, _ = run_command(f"git config --global https.proxy {proxy_url}")
    if success:
        print(f"HTTPS 代理已设置: {proxy_url}")
    else:
        print("错误: 设置 HTTPS 代理失败")
        sys.exit(1)
    print()
    
    # 3. 验证代理配置
    print("[3/3] 验证代理配置...")
    print()
    print("当前 Git 代理配置:")
    run_command("git config --global --get http.proxy", check=False)
    run_command("git config --global --get https.proxy", check=False)
    print()
    
    print("=" * 50)
    print("代理配置完成！")
    print("=" * 50)
    print()
    print("注意: ")
    print("- 如果使用 SSH 连接 (git@github.com)，需要配置 SSH 代理")
    print("- 如果使用 HTTPS 连接，上述配置已生效")
    print()
    print("测试连接:")
    print("git ls-remote git@github.com:schrodinger12138/AIMind_Card.git")
    print()
    
    # 询问是否配置 SSH 代理
    print("是否配置 SSH 代理? (y/n): ", end='')
    try:
        choice = input().strip().lower()
        if choice == 'y':
            setup_ssh_proxy()
    except:
        pass

def setup_ssh_proxy():
    """配置 SSH 代理"""
    print()
    print("=" * 50)
    print("配置 SSH 代理")
    print("=" * 50)
    print()
    
    ssh_dir = os.path.expanduser("~/.ssh")
    ssh_config = os.path.join(ssh_dir, "config")
    
    # 创建 .ssh 目录
    if not os.path.exists(ssh_dir):
        os.makedirs(ssh_dir)
        print(f".ssh 目录已创建: {ssh_dir}")
    else:
        print(f".ssh 目录已存在: {ssh_dir}")
    print()
    
    # 检查是否已有配置
    github_config_exists = False
    if os.path.exists(ssh_config):
        with open(ssh_config, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'Host github.com' in content:
                github_config_exists = True
                print("警告: github.com 配置已存在")
                print(f"请手动编辑: {ssh_config}")
    
    if not github_config_exists:
        print("添加 SSH 配置...")
        config_content = """
# GitHub proxy configuration
Host github.com
    ProxyCommand connect -H 127.0.0.1:7898 %h %p
    Hostname github.com
    Port 22
    User git
"""
        try:
            with open(ssh_config, 'a', encoding='utf-8') as f:
                f.write(config_content)
            print(f"SSH 配置已添加到: {ssh_config}")
        except Exception as e:
            print(f"错误: 写入 SSH 配置失败: {e}")
            print()
            print("请手动添加以下内容到 ~/.ssh/config:")
            print(config_content)
    print()
    print("注意: 需要安装 connect 工具 (Git for Windows 自带)")
    print("测试连接: ssh -T git@github.com")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n发生错误: {e}")
        sys.exit(1)

