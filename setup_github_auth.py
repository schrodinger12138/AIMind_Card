#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置 GitHub 认证（使用个人访问令牌）
"""
import subprocess
import sys
import os

def run_command(cmd, check=True):
    """执行命令并返回结果"""
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
        if e.stderr:
            print(e.stderr.strip())
        return False, e.stdout if hasattr(e, 'stdout') else '', e.stderr if hasattr(e, 'stderr') else ''

def main():
    print("=" * 60)
    print("配置 GitHub 认证")
    print("=" * 60)
    print()
    print("GitHub 现在要求使用个人访问令牌（Personal Access Token）")
    print("而不是密码进行 HTTPS 认证。")
    print()
    print("步骤：")
    print("1. 访问: https://github.com/settings/tokens")
    print("2. 点击 'Generate new token (classic)'")
    print("3. 设置名称（如：AIMind_Card_Upload）")
    print("4. 选择过期时间")
    print("5. 勾选 'repo' 权限（完整仓库访问权限）")
    print("6. 点击 'Generate token'")
    print("7. 复制生成的令牌（只显示一次！）")
    print()
    
    # 获取远程仓库 URL
    success, output, _ = run_command("git remote get-url origin", check=False)
    if not success:
        print("错误: 未找到远程仓库，请先配置远程仓库")
        sys.exit(1)
    
    remote_url = output.strip()
    print(f"当前远程仓库: {remote_url}")
    print()
    
    # 如果是 HTTPS URL，提供配置选项
    if remote_url.startswith("https://"):
        print("检测到 HTTPS URL，可以配置令牌认证。")
        print()
        print("选项 1: 在 URL 中嵌入令牌（推荐，但令牌会保存在配置中）")
        print("选项 2: 使用 Git Credential Manager（推荐，更安全）")
        print("选项 3: 手动输入（推送时输入）")
        print()
        
        choice = input("请选择 (1/2/3，默认 2): ").strip() or "2"
        
        if choice == "1":
            # 在 URL 中嵌入令牌
            print()
            print("请输入您的 GitHub 用户名: ", end='')
            username = input().strip()
            print("请输入您的个人访问令牌: ", end='')
            token = input().strip()
            
            if username and token:
                # 更新 URL 格式: https://username:token@github.com/...
                new_url = remote_url.replace(
                    "https://github.com/",
                    f"https://{username}:{token}@github.com/"
                )
                success, _, _ = run_command(f"git remote set-url origin {new_url}")
                if success:
                    print("✓ 认证信息已配置到远程 URL")
                    print("注意: 令牌已嵌入 URL，请妥善保管！")
                else:
                    print("✗ 配置失败")
            else:
                print("用户名和令牌不能为空")
                
        elif choice == "2":
            # 使用 Git Credential Manager
            print()
            print("配置 Git Credential Manager...")
            print()
            print("方法 A: Windows Credential Manager（自动）")
            print("  推送时会自动弹出 Windows 凭据窗口")
            print("  用户名: 您的 GitHub 用户名")
            print("  密码: 您的个人访问令牌")
            print()
            print("方法 B: 使用 git credential-store")
            print("  请输入您的 GitHub 用户名: ", end='')
            username = input().strip()
            print("  请输入您的个人访问令牌: ", end='')
            token = input().strip()
            
            if username and token:
                # 配置 credential helper
                run_command("git config --global credential.helper store")
                
                # 创建凭据文件（临时）
                from urllib.parse import urlparse
                parsed = urlparse(remote_url)
                host = parsed.netloc or parsed.hostname
                
                # 使用 git credential approve
                credential_input = f"protocol=https\nhost={host}\nusername={username}\npassword={token}\n\n"
                process = subprocess.Popen(
                    "git credential approve",
                    stdin=subprocess.PIPE,
                    shell=True,
                    text=True
                )
                process.communicate(input=credential_input)
                
                print("✓ 凭据已保存")
            else:
                print("用户名和令牌不能为空")
                
        else:
            print()
            print("您选择手动输入。")
            print("推送时会提示输入用户名和密码（令牌）")
            print()
    else:
        print("当前使用 SSH 方式，需要配置 SSH 密钥。")
        print("如需使用 HTTPS，请先更改远程 URL:")
        print("  git remote set-url origin https://github.com/schrodinger12138/AIMind_Card.git")
        print()
    
    print()
    print("=" * 60)
    print("配置完成！")
    print("=" * 60)
    print()
    print("现在可以尝试推送:")
    print("  git push -u origin main")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

