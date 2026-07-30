#!/usr/bin/env python3
"""
简化版GitHub部署: 使用Playwright浏览器自动化完成完整流程
1. 打开GitHub登录页
2. 等待用户提供Token（因为无法交互输入，我们直接使用已构建好的文件通过git push）
"""

import subprocess
import time
import os
import json
import urllib.request
import urllib.error

BASE = "/workspace/amumu"
GITHUB_USER = "yue160"
REPO_NAME = "amumu"

def check_and_build():
    """确保 amumu.html 是最新的"""
    os.chdir(BASE)
    result = subprocess.run(['python3', 'build.py'], capture_output=True, text=True)
    print(result.stdout)
    return os.path.exists(os.path.join(BASE, 'amumu.html'))

def setup_git():
    """初始化Git仓库"""
    os.chdir(BASE)
    
    if not os.path.exists(os.path.join(BASE, '.git')):
        subprocess.run(['git', 'init'], check=True)
        subprocess.run(['git', 'config', 'user.name', GITHUB_USER], check=True)
        subprocess.run(['git', 'config', 'user.email', f'{GITHUB_USER}@users.noreply.github.com'], check=True)
        print("Git仓库已初始化")
    
    # 创建必要文件
    for fname, content in [
        ('.gitignore', '*.pyc\n__pycache__/\nscreenshot_*.png\nstep*.png\n.playwright/\n'),
        ('.nojekyll', ''),
    ]:
        fpath = os.path.join(BASE, fname)
        if not os.path.exists(fpath):
            with open(fpath, 'w') as f:
                f.write(content)
    
    # 确保有 index.html (GitHub Pages默认首页)
    amumu_path = os.path.join(BASE, 'amumu.html')
    index_path = os.path.join(BASE, 'index.html')
    if os.path.exists(amumu_path):
        with open(amumu_path, 'r') as src:
            with open(index_path, 'w') as dst:
                dst.write(src.read())

def push_with_token(token):
    """使用Token推送代码"""
    os.chdir(BASE)
    
    # 添加所有文件
    subprocess.run(['git', 'add', '-A'], check=True)
    
    # 检查变更
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    if result.stdout.strip():
        subprocess.run(['git', 'commit', '-m', '阿沐的菜单 v1 - 112道菜，8大分类，支持分享选菜'], check=True)
        print("已创建提交")
    else:
        print("没有新变更")
    
    # 设置远程仓库
    remote_url = f"https://{GITHUB_USER}:{token}@github.com/{GITHUB_USER}/{REPO_NAME}.git"
    
    result = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True)
    if result.returncode != 0:
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url], check=True)
    else:
        subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url], check=True)
    
    subprocess.run(['git', 'branch', '-M', 'main'], check=True)
    
    print("正在推送到 GitHub...")
    result = subprocess.run(['git', 'push', '-u', 'origin', 'main', '--force'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 推送成功!")
        return True
    else:
        # 隐藏token信息
        err = result.stderr.replace(token, '***TOKEN***')
        print(f"推送失败: {err}")
        return False

def create_repo(token):
    """通过API创建仓库"""
    url = "https://api.github.com/user/repos"
    data = json.dumps({
        "name": REPO_NAME,
        "description": "阿沐的菜单 - 点菜菜单App",
        "private": False,
        "has_pages": True,
        "auto_init": False
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', f'token {token}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"✅ 仓库创建成功: {result['html_url']}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 422:
            print("仓库已存在，将使用现有仓库")
            return True
        else:
            print(f"创建仓库失败: {e.code} - {body}")
            return False

def enable_pages(token):
    """启用GitHub Pages"""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/pages"
    data = json.dumps({"source": {"branch": "main", "path": "/"}}).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', f'token {token}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"✅ Pages已启用: {result.get('html_url', '')}")
            return True
    except urllib.error.HTTPError as e:
        if e.code == 409:  # Already exists
            # Try PUT
            req2 = urllib.request.Request(url, data=data, method='PUT')
            req2.add_header('Authorization', f'token {token}')
            req2.add_header('Accept', 'application/vnd.github.v3+json')
            req2.add_header('Content-Type', 'application/json')
            try:
                with urllib.request.urlopen(req2) as resp:
                    print("✅ Pages已更新")
                    return True
            except:
                pass
        print(f"Pages配置可能需要手动完成: {e.code}")
        return False

def main():
    print("=" * 60)
    print("  阿沐的菜单 - GitHub Pages 部署")
    print("=" * 60)
    print()
    
    # 构建
    print("[1/3] 构建应用...")
    check_and_build()
    setup_git()
    
    # 需要Token
    print()
    print("需要 GitHub Personal Access Token 来推送代码。")
    print()
    print("获取Token步骤:")
    print("  1. 访问 https://github.com/settings/tokens/new")
    print("  2. Note: amumu-deploy")
    print("  3. Expiration: 自定义 (建议7天)")
    print("  4. 勾选 scopes: repo, workflow")
    print("  5. 点击 Generate token")
    print("  6. 复制生成的 token (ghp_开头)")
    print()
    
    # 由于无法交互输入，检查环境变量
    token = os.environ.get('GITHUB_TOKEN', '')
    
    if not token:
        print("⚠️ 未检测到 GITHUB_TOKEN 环境变量")
        print("请设置环境变量后重试:")
        print("  export GITHUB_TOKEN='ghp_xxxxxxxxxxxx'")
        print("  python3 deploy_github.py")
        print()
        print("或者手动执行以下命令推送:")
        print(f"  cd {BASE}")
        print("  git remote add origin https://yue160:TOKEN@github.com/yue160/amumu.git")
        print("  git push -u origin main --force")
        return
    
    # 创建仓库
    print("\n[2/3] 创建/检查仓库...")
    if not create_repo(token):
        return
    
    # 推送
    print("\n[3/3] 推送代码...")
    if not push_with_token(token):
        return
    
    # 启用Pages
    print("\n启用GitHub Pages...")
    enable_pages(token)
    
    print()
    print("=" * 60)
    print(f" ✅ 部署完成!")
    print(f" 📱 访问地址: https://{GITHUB_USER}.github.io/{REPO_NAME}/")
    print(f" 📱 安装为App: 在Safari中打开 → 分享 → 添加到主屏幕")
    print("=" * 60)

if __name__ == "__main__":
    main()
