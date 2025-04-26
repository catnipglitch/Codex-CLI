#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Codex CLI設定ファイルテスト用スクリプト
設定ファイルが正しく読み込まれるかをテストします
"""

import os
import sys
import json
import logging
import configparser

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# srcディレクトリをパスに追加
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src')
sys.path.insert(0, src_dir)

# api keys location (same as in codex_query.py)
API_KEYS_LOCATION = os.path.join(src_dir, 'openaiapirc')

def check_settings_files():
    """利用可能な設定ファイルを確認"""
    home = os.path.expanduser("~")
    
    # 設定ファイルパス
    codex_cli_path = os.path.join(home, ".openai", "codex-cli.json")
    settings_path = os.path.join(home, ".openai", "settings.json")
    openaiapirc_path = API_KEYS_LOCATION
    
    print("=== Codex CLI設定ファイルチェック ===")
    
    # codex-cli.json
    if os.path.exists(codex_cli_path):
        print(f"✓ codex-cli.json が見つかりました: {codex_cli_path}")
        try:
            with open(codex_cli_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
            
            print("  内容:")
            api_key = config.get("api_key", "")
            if api_key:
                masked_key = f"{api_key[:5]}...{api_key[-4:]}" if len(api_key) > 9 else "***"
                print(f"  - api_key: {masked_key}")
            else:
                print("  - api_key: 未設定")
                
            print(f"  - organization: {config.get('organization', '未設定')}")
            print(f"  - model: {config.get('model', '未設定')}")
            print(f"  - language: {config.get('language', '未設定')}")
        except Exception as e:
            print(f"  ✗ 読み込みエラー: {str(e)}")
    else:
        print(f"✗ codex-cli.json が見つかりません")
    
    # settings.json (旧バージョン)
    if os.path.exists(settings_path):
        print(f"\n✓ 旧形式のsettings.json が見つかりました: {settings_path}")
        try:
            with open(settings_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
            print("  内容: [旧形式のファイル - 削除することを推奨]")
            if "api_key" in config:
                masked_key = "***"
                print(f"  - api_key: {masked_key}")
        except Exception as e:
            print(f"  ✗ 読み込みエラー: {str(e)}")
    
    # openaiapirc
    if os.path.exists(openaiapirc_path):
        print(f"\n✓ openaiapirc が見つかりました: {openaiapirc_path}")
        try:
            config = configparser.ConfigParser()
            config.read(openaiapirc_path)
            print("  内容:")
            if 'openai' in config:
                if 'secret_key' in config['openai']:
                    key = config['openai']['secret_key']
                    masked_key = f"{key[:5]}...{key[-4:]}" if len(key) > 9 else "***"
                    print(f"  - secret_key: {masked_key}")
                else:
                    print("  - secret_key: 未設定")
                
                print(f"  - organization_id: {config['openai'].get('organization_id', '未設定')}")
                print(f"  - model: {config['openai'].get('model', '未設定')}")
                print(f"  - language: {config['openai'].get('language', '未設定')}")
        except Exception as e:
            print(f"  ✗ 読み込みエラー: {str(e)}")
    
    # 設定が見つからない場合
    if not (os.path.exists(codex_cli_path) or os.path.exists(openaiapirc_path)):
        print("\n✗ 有効な設定ファイルが見つかりません。セットアップを再実行してください:")
        print("  PowerShell: .\\scripts\\powershell_setup.ps1 -Language ja")

def check_environment():
    """環境変数を確認"""
    print("\n=== 環境変数チェック ===")
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        masked_key = f"{api_key[:5]}...{api_key[-4:]}" if len(api_key) > 9 else "***"
        print(f"✓ OPENAI_API_KEY: {masked_key}")
    else:
        print("✗ OPENAI_API_KEY: 未設定")
    
    org_id = os.environ.get('OPENAI_ORGANIZATION_ID') 
    if org_id:
        print(f"✓ OPENAI_ORGANIZATION_ID: {org_id}")
    else:
        print("✗ OPENAI_ORGANIZATION_ID: 未設定")
    
    model = os.environ.get('OPENAI_MODEL')
    if model:
        print(f"✓ OPENAI_MODEL: {model}")
    else:
        print("✗ OPENAI_MODEL: 未設定")

def test_invoke_script():
    """codex_query.py の呼び出しテスト"""
    print("\n=== コマンド実行テスト ===")
    try:
        import subprocess
        script_path = os.path.join(src_dir, 'codex_query.py')
        
        # 一時ファイルを作成
        temp_file = os.path.join(script_dir, "temp_test.txt")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write("# what is my IP address?")
        
        print(f"テストコマンド: python {script_path} {temp_file}")
        
        # スクリプトを実行
        try:
            result = subprocess.run(
                ["python", script_path, temp_file], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            print(f"終了コード: {result.returncode}")
            if result.stdout:
                print(f"出力:\n{result.stdout[:300]}{'...' if len(result.stdout) > 300 else ''}")
            if result.stderr:
                print(f"エラー:\n{result.stderr}")
        except subprocess.TimeoutExpired:
            print("タイムアウト: コマンドの実行に時間がかかりすぎました")
        
        # 一時ファイルを削除
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    except Exception as e:
        print(f"テスト実行エラー: {str(e)}")

def check_profile():
    """PowerShellプロファイルを確認"""
    print("\n=== PowerShellプロファイルチェック ===")
    try:
        import subprocess
        
        # PowerShellコマンドを実行してプロファイルパスを取得
        ps_command = "powershell -Command \"Write-Output $PROFILE\""
        result = subprocess.run(ps_command, capture_output=True, text=True, shell=True)
        profile_path = result.stdout.strip()
        
        print(f"PowerShellプロファイルパス: {profile_path}")
        
        if os.path.exists(profile_path):
            print("✓ プロファイルファイルが存在します")
            
            # プロファイル内のCodex CLI設定を確認
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_content = f.read()
            
            if "### Codex CLI setup - start" in profile_content and "### Codex CLI setup - end" in profile_content:
                print("✓ Codex CLI設定が見つかりました")
                
                # キーバインディングを確認
                if "Set-PSReadLineKeyHandler -Key Ctrl+g" in profile_content:
                    print("✓ Ctrl+Gキーバインディングが設定されています")
                else:
                    print("✗ Ctrl+Gキーバインディングが見つかりません")
                
                # スクリプトパスを確認
                script_path = None
                for line in profile_content.splitlines():
                    if "$nl_cli_script =" in line:
                        script_path = line.split("=")[1].strip().strip('"')
                        break
                
                if script_path:
                    print(f"✓ スクリプトパス: {script_path}")
                    if os.path.exists(script_path.strip('"')):
                        print("✓ スクリプトファイルが存在します")
                    else:
                        print(f"✗ スクリプトファイルが存在しません: {script_path}")
                else:
                    print("✗ スクリプトパスが設定されていません")
            else:
                print("✗ Codex CLI設定が見つかりません")
        else:
            print(f"✗ プロファイルファイルが存在しません: {profile_path}")
    except Exception as e:
        print(f"プロファイルチェックエラー: {str(e)}")

def main():
    """メイン関数"""
    print("Codex CLI 設定診断ツール (v1.0)")
    print("================================\n")
    
    # Pythonバージョン確認
    print(f"Pythonバージョン: {sys.version}")
    
    # 設定ファイル確認
    check_settings_files()
    
    # 環境変数確認
    check_environment()
    
    # PowerShellプロファイル確認
    check_profile()
    
    # コマンド実行テスト
    test_invoke_script()
    
    print("\nトラブルシューティング:")
    print("1. 設定ファイルが見つからない場合は、セットアップスクリプトを再実行してください")
    print("2. PowerShellセッションを再起動してください")
    print("3. スクリプトエラーがある場合は、Pythonの依存関係が正しくインストールされているか確認してください")
    print("   python -m pip install -r requirements.txt")
    print("4. 手動でコマンドを実行してテスト:")
    print("   SendToCodex \"# 自分のIPアドレスは？\"")

if __name__ == "__main__":
    main()