#!/usr/bin/env python3
"""
API Keys設定確認スクリプト
"""
import os
from dotenv import load_dotenv

def check_api_keys():
    """APIキーの設定状況を確認"""
    load_dotenv()
    
    print("=== API Keys Configuration Check ===")
    
    # Anthropic API Key
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        print(f"✅ ANTHROPIC_API_KEY: {anthropic_key[:10]}...")
    else:
        print("❌ ANTHROPIC_API_KEY: Not set")
    
    # Gemini API Key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print(f"✅ GEMINI_API_KEY: {gemini_key[:10]}...")
    else:
        print("❌ GEMINI_API_KEY: Not set")
    
    # Cursor API Key
    cursor_key = os.getenv("CURSOR_API_KEY")
    if cursor_key:
        print(f"✅ CURSOR_API_KEY: {cursor_key[:10]}...")
    else:
        print("❌ CURSOR_API_KEY: Not set")
    
    print("\n=== Configuration Instructions ===")
    print("1. Create a .env file in the project root")
    print("2. Add your API keys:")
    print("   ANTHROPIC_API_KEY=sk-ant-api03-...")
    print("   GEMINI_API_KEY=AIzaSy...")
    print("   CURSOR_API_KEY=cursor_...")
    print("3. Restart Docker containers")

if __name__ == "__main__":
    check_api_keys()
