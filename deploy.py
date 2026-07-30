#!/usr/bin/env python3
"""GitHub automation: login, create repo, enable Pages, push code."""

import subprocess
import time
import os
import json

BASE = "/workspace/amumu"
GITHUB_USER = "yue160"
REPO_NAME = "amumu"

from playwright.sync_api import sync_playwright

def main():
    # First, check if we need to get GitHub credentials
    # Ask user for GitHub token or use browser login
    
    print("=" * 60)
    print(" 阿沐的菜单 - 部署到 GitHub Pages")
    print("=" * 60)
    print()
    
    # We need a GitHub Personal Access Token to push
    # Let's try browser login first, then create a token
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        
        # Step 1: Login to GitHub
        print("[1/5] 登录 GitHub...")
        page.goto("https://github.com/login", wait_until="networkidle", timeout=30000)
        page.screenshot(path=os.path.join(BASE, "screenshot_login.png"))
        print("  截图已保存: screenshot_login.png")
        
        # Check if already logged in (cookie persistence)
        try:
            page.wait_for_selector('input[name="login"]', timeout=3000)
            print("  需要登录，请在下面输入GitHub用户名和密码：")
            print("  注意：由于安全限制，请使用Personal Access Token登录")
        except:
            print("  可能已登录或页面加载异常")
        
        browser.close()
    
    print()
    print("请提供以下信息以完成部署：")
    print("1. GitHub Personal Access Token (需要 repo 和 workflow 权限)")
    print("2. 或者提供 GitHub 用户名和密码")
    
if __name__ == "__main__":
    main()
