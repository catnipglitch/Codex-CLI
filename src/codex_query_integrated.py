#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import configparser
import json
import logging
import re
import time
from pathlib import Path

# ログ設定
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "codex_debug.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# OpenAIライブラリをインポート
try:
    import openai
    logging.debug(f"OpenAIライブラリバージョン: {openai.__version__}")
except Exception as e:
    logging.error(f"OpenAIライブラリのインポート中にエラーが発生しました: {str(e)}")
    print(f"エラー: OpenAIライブラリのインポートに失敗しました - {str(e)}")
    sys.exit(1)

# 必要に応じてpsutilをインポート（シェル検出用）
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    logging.warning("psutilモジュールが見つかりません。シェル検出機能が制限されます。")

from prompt_file import PromptFile
from commands import get_command_result

# グローバル設定
MULTI_TURN = "off"
SHELL = ""
MODEL = 'gpt-4o'
TEMPERATURE = 0.7
MAX_TOKENS = 300
DEBUG_MODE = False

# 設定ファイルのパス
CONFIG_FILE_PATH = os.path.join(os.path.expanduser("~"), ".openai", "codex-cli.json")
PROMPT_CONTEXT = Path(__file__).parent / "current_context.txt"

def load_config():
    """設定を読み込む（環境変数のみをサポート）"""
    try:
        # 環境変数から設定を読み込む
        api_key = os.environ.get('OPENAI_API_KEY')
        organization = os.environ.get('OPENAI_ORGANIZATION_ID')
        model_name = os.environ.get('OPENAI_MODEL', 'gpt-4o')
        language = "ja"  # デフォルト言語は日本語
        
        # 設定ファイルをチェック（言語設定のみ）
        logging.debug(f"設定ファイルを確認中: {CONFIG_FILE_PATH}")
        
        if os.path.exists(CONFIG_FILE_PATH):
            logging.debug(f"設定ファイル発見: {CONFIG_FILE_PATH}")
            try:
                with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as file:
                    config = json.load(file)
                # 言語設定のみファイルから読み込む
                language = config.get("language", "ja")
                logging.debug(f"言語設定: {language}")
            except Exception as load_err:
                logging.error(f"設定ファイル読み込みエラー: {str(load_err)}")
        
        if not api_key:
            # APIキーがない場合はテンプレート作成
            logging.warning("APIキーが環境変数に設定されていません。")
            create_template_config()
            sys.exit(1)
            
        logging.info("設定読み込み成功")
        return api_key, organization, model_name, language
    except Exception as e:
        logging.error(f"設定の読み込み中にエラーが発生しました: {str(e)}")
        print(f"エラー: 設定の読み込みに失敗しました - {str(e)}")
        sys.exit(1)

def create_template_config():
    """設定ファイルのテンプレートを作成（環境変数のヒントあり）"""
    home = os.path.expanduser("~")
    codex_cli_path = os.path.join(home, ".openai", "codex-cli.json")
    
    if not os.path.exists(os.path.dirname(codex_cli_path)):
        try:
            os.makedirs(os.path.dirname(codex_cli_path))
            logging.debug(f".openaiフォルダを作成しました: {os.path.dirname(codex_cli_path)}")
        except Exception as e:
            logging.error(f".openaiフォルダの作成に失敗しました: {str(e)}")
    
    if not os.path.exists(codex_cli_path):
        try:
            # テンプレート設定の作成（言語設定のみ）
            template_config = {
                "language": "ja"  # デフォルト言語を日本語に設定
            }
            
            # JSONファイルとして書き込み
            with open(codex_cli_path, 'w', encoding='utf-8') as file:
                json.dump(template_config, file, ensure_ascii=False, indent=2)
            
            logging.info(f"設定ファイルを作成しました: {codex_cli_path}")
            
            print(f'# 環境変数が設定されていません')
            print(f'# 以下の環境変数を設定してください:')
            print('# - OPENAI_API_KEY: OpenAI APIキー (必須)')
            print('# - OPENAI_ORGANIZATION_ID: OpenAI 組織ID (省略可能)')
            print('# - OPENAI_MODEL: OpenAIモデル名 (省略可能、デフォルト: gpt-4o)')
            print('')
            print('# 設定例 (Windowsコマンドプロンプト):')
            print('# set OPENAI_API_KEY=your_api_key_here')
            print('')
            print('# 設定例 (PowerShell):')
            print('# $env:OPENAI_API_KEY="your_api_key_here"')
            print('')
            print('# 設定例 (Linux/macOSのbashやzsh):')
            print('# export OPENAI_API_KEY=your_api_key_here')
            
            return template_config
        except Exception as e:
            logging.error(f"設定ファイルの作成に失敗しました: {str(e)}")
            print(f'# エラー: 設定ファイルの作成に失敗しました: {str(e)}')
            sys.exit(1)
    
    return None

def detect_shell():
    """シェルの種類を検出する"""
    global SHELL
    global PROMPT_CONTEXT
    
    try:
        # Windowsの場合は特別な処理
        if os.name == 'nt':
            # PowerShellを使用していると仮定
            SHELL = "powershell"
            logging.debug("Windows環境を検出: PowerShellを使用")
        elif HAS_PSUTIL:
            # psutilが利用可能な場合は詳細な検出を行う
            # Unix系の場合は親プロセスを確認
            parent_process_name = psutil.Process(os.getppid()).name().lower()
            logging.debug(f"親プロセス名: {parent_process_name}")
            
            # シェルタイプの検出
            POWERSHELL_MODE = 'powershell' in parent_process_name or 'pwsh' in parent_process_name
            BASH_MODE = 'bash' in parent_process_name
            ZSH_MODE = 'zsh' in parent_process_name
            
            # 環境変数からもシェルタイプを確認（バックアップ手段）
            if not (POWERSHELL_MODE or BASH_MODE or ZSH_MODE):
                shell_env = os.environ.get('SHELL', '').lower()
                if 'powershell' in shell_env or 'pwsh' in shell_env:
                    POWERSHELL_MODE = True
                elif 'bash' in shell_env:
                    BASH_MODE = True
                elif 'zsh' in shell_env:
                    ZSH_MODE = True
            
            # シェルタイプの決定
            SHELL = "powershell" if POWERSHELL_MODE else "bash" if BASH_MODE else "zsh" if ZSH_MODE else "bash"
        else:
            # psutilがない場合はより単純な検出
            shell_env = os.environ.get('SHELL', '').lower()
            if 'powershell' in shell_env or 'pwsh' in shell_env:
                SHELL = "powershell"
            elif 'bash' in shell_env:
                SHELL = "bash"
            elif 'zsh' in shell_env:
                SHELL = "zsh"
            else:
                # デフォルト
                SHELL = "bash" if os.name != 'nt' else "powershell"
            
        logging.debug(f"検出されたシェル: {SHELL}")

        # コンテキストファイルのパスを設定
        shell_prompt_file = Path(os.path.join(os.path.dirname(__file__), "..", "contexts", f"{SHELL}-context.txt"))

        if shell_prompt_file.is_file():
            PROMPT_CONTEXT = shell_prompt_file
            logging.debug(f"シェル用コンテキストファイルを使用: {PROMPT_CONTEXT}")
        else:
            logging.warning(f"シェル用コンテキストファイルが見つかりません: {shell_prompt_file}")
    except Exception as e:
        # 検出に失敗した場合はデフォルト値を使用
        SHELL = "powershell" if os.name == 'nt' else "bash"
        logging.error(f"シェル検出中にエラーが発生しました: {str(e)}。デフォルト: {SHELL}")
        
        # デフォルトコンテキストファイルを使用
        default_context = Path(os.path.join(os.path.dirname(__file__), "..", "contexts", f"{SHELL}-context.txt"))
        if default_context.is_file():
            PROMPT_CONTEXT = default_context

def format_system_prompt(language, shell_type):
    """システムプロンプトを言語設定に基づいて生成"""
    # OSの種類を検出
    import platform
    os_type = platform.system()
    
    if language == "ja":
        return f"""あなたはコマンドライン専門のアシスタントです。
以下のフォーマットで回答してください：
1. まず「# 」で始まる1行のコメントで、何をするコマンドかを簡潔に説明する
2. 次の行に実行可能な{shell_type}のコマンドを提示する（説明なし）
3. 必要に応じて、追加の「# 」コメント行とコマンド行のペアを続ける

コマンドの前後にはバッククォート(`)やその他の記号を付けないでください。
複数のコマンドが必要な場合は、それらを別々の行に表示してください。
長い説明は避け、簡潔なコメントと実用的なコマンドに集中してください。
現在のOSは{os_type}です。"""
    else:
        return f"""You are a command line specialist assistant.
Respond in the following format:
1. First, a one-line comment starting with "# " that briefly explains what the command does
2. Next line, provide an executable {shell_type} command (without explanation)
3. If needed, continue with additional "# " comment lines and command line pairs

Do not surround commands with backticks (`) or other symbols.
If multiple commands are necessary, display them on separate lines.
Avoid lengthy explanations, focus on concise comments and practical commands.
The current OS is {os_type}."""

def initialize():
    """OpenAIとシェルモードを初期化"""
    global MODEL

    # 設定ファイルの確認
    api_key, org_id, model_name, language = load_config()

    # 新しいOpenAI APIクライアント初期化方法
    client = openai.OpenAI(
        api_key=api_key,
        organization=org_id
    )

    prompt_config = {
        'model': model_name,
        'temperature': TEMPERATURE,
        'max_tokens': MAX_TOKENS,
        'shell': SHELL,
        'multi_turn': MULTI_TURN,
        'token_count': 0,
        'language': language
    }
    
    return PromptFile(PROMPT_CONTEXT.name, prompt_config), client, language

def is_sensitive_content(content, client):
    """コンテンツが不適切かチェック（OpenAIのモデレーション API使用）"""
    if len(content) == 0:
        return False
    
    try:
        # OpenAI APIのモデレーション呼び出し
        response = client.moderations.create(input=content)
        return response.results[0].flagged
    except Exception as e:
        logging.error(f"モデレーションチェックエラー: {e}")
        print(f"モデレーションチェックエラー: {e}")
        # チェックに失敗した場合、安全と仮定して処理を続行
        return False

def get_query(prompt_file):
    """
    stdin、ファイル、コマンドライン引数から入力を取得し、
    コマンドとして処理するか、Codexクエリとして扱う
    """
    try:
        # コマンドライン引数をチェック
        input_file = None
        if len(sys.argv) > 1:
            if sys.argv[1] == "--file" and len(sys.argv) > 2:
                input_file = sys.argv[2]
                logging.debug(f"--fileオプションでファイルパスを検出: {input_file}")
            elif os.path.exists(sys.argv[1]):
                input_file = sys.argv[1]
                logging.debug(f"コマンドライン引数からファイルパスを検出: {input_file}")
        
        if DEBUG_MODE:
            entry = input("prompt: ") + '\n'
        elif input_file:
            # ファイルから入力を読み込む
            try:
                # まずUTF-8で試す
                with open(input_file, 'r', encoding='utf-8') as f:
                    entry = f.read()
                logging.debug(f"UTF-8でファイルを読み込みました: {input_file}")
            except UnicodeDecodeError:
                # UTF-8で失敗した場合はcp932を試す
                try:
                    with open(input_file, 'r', encoding='cp932') as f:
                        entry = f.read()
                    logging.debug(f"cp932でファイルを読み込みました: {input_file}")
                except UnicodeDecodeError:
                    # それも失敗した場合は、バイナリモードで読み込んで適切なエンコーディングを推測
                    with open(input_file, 'rb') as f:
                        content = f.read()
                    
                    # エンコーディングを推測
                    encodings = ['utf-8', 'cp932', 'cp1252', 'ascii']
                    for enc in encodings:
                        try:
                            entry = content.decode(enc)
                            logging.debug(f"エンコーディング {enc} で成功")
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        # すべて失敗した場合
                        entry = content.decode('ascii', errors='replace')
                        logging.error("すべてのエンコーディングが失敗、ASCIIで代替")
        else:
            # 標準入力から読み込む
            if os.name == 'nt':
                # Windowsでの標準入力処理を改善
                try:
                    import select
                    import msvcrt
                    
                    # パイプからの入力があるか確認
                    if msvcrt.kbhit():
                        # インタラクティブモード
                        print("# コマンドを入力してください (Ctrl+Cで終了):")
                        entry = input().strip() + "\n"
                    else:
                        # パイプ入力の可能性あり
                        try:
                            data = sys.stdin.buffer.read()
                            if data:
                                entry = data.decode('utf-8', errors='replace').strip() + "\n"
                            else:
                                # パイプ入力が空、インタラクティブモードに切り替え
                                print("# パイプ入力が空です")
                                print("# コマンドを入力してください:")
                                entry = input().strip() + "\n"
                        except Exception as e:
                            # パイプ読み込み失敗時
                            logging.error(f"パイプ入力エラー: {str(e)}")
                            print("# 直接入力を試みます...")
                            print("# コマンドを入力してください:")
                            entry = input().strip() + "\n"
                except ImportError:
                    # fallback
                    import io
                    stdin_bytes = sys.stdin.buffer.read()
                    try:
                        entry = stdin_bytes.decode('utf-8', errors='replace') + "\n"
                    except UnicodeDecodeError:
                        # 失敗した場合は別のエンコーディングを試す
                        fallback_encodings = ['cp932', 'cp1252']
                        for enc in fallback_encodings:
                            try:
                                entry = stdin_bytes.decode(enc, errors='replace') + "\n"
                                break
                            except UnicodeDecodeError:
                                continue
                        else:
                            # すべて失敗した場合
                            entry = stdin_bytes.decode('ascii', errors='replace') + "\n"
            else:
                # Unix系の場合
                print("# コマンドを入力してください (Ctrl+Cで終了):")
                entry = sys.stdin.read()
        
        if entry:
            logging.debug(f"入力文字列（最初の50文字）: {entry[:50]}")
        else:
            logging.error("入力が空です")
            entry = ""
            print("# エラー: 入力がありません")
            return None, prompt_file
            
        # まず、入力がコマンドかどうかをチェック
        command_result, prompt_file = get_command_result(entry, prompt_file)

        # 入力がコマンドでない場合、Codexクエリとして処理、それ以外の場合は実行されたコマンドが成功して終了
        if command_result == "":
            return entry, prompt_file
        else:
            sys.exit(0)
    except UnicodeError as e:
        logging.error(f'Unicode encoding error: {str(e)}')
        print('\n\n# Codex CLI error: 文字エンコーディングエラー。マルチバイト文字や絵文字を含む可能性があります - ' + str(e))
        sys.exit(1)

def generate_response(prompt, model, client, language, shell):
    """ストリーミングレスポンスを生成（codex_query_fixed.pyの方式を採用）"""
    logging.debug(f"APIリクエスト: モデル={model}, プロンプト長={len(str(prompt))}")
    
    try:
        # システムプロンプトの準備
        system_prompt = format_system_prompt(language, shell)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # 処理中メッセージを表示
        print("\n#   処理中...", end="", flush=True)
        
        # ストリーミング応答の生成
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=TEMPERATURE,
            stream=True
        )
        
        # 処理中メッセージをクリア
        print("\r                 \r", end="", flush=True)
        
        # 応答をリアルタイムで出力
        full_response = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                print(content, end="", flush=True)
                full_response += content
        
        # 改行を追加
        if not full_response.endswith('\n'):
            print()
        
        return full_response
    
    except openai.RateLimitError as e:
        # 処理中メッセージをクリア
        print("\r                 \r", end="", flush=True)
        # レート制限エラー
        logging.error(f"OpenAI レート制限エラー: {str(e)}")
        print(f"\n# エラー: APIレート制限に達しました。しばらく待ってから再試行してください。")
        return None
    
    except openai.APIError as e:
        # 処理中メッセージをクリア
        print("\r                 \r", end="", flush=True)
        # 一般的なAPI エラー
        logging.error(f"OpenAI API エラー: {str(e)}")
        print(f"\n# エラー: API呼び出し中にエラーが発生しました。")
        return None
    
    except Exception as e:
        # 処理中メッセージをクリア
        print("\r                 \r", end="", flush=True)
        # その他の例外
        logging.error(f"予期しないエラー: {str(e)}", exc_info=True)
        print(f"\n# エラー: 予期しないエラーが発生しました。")
        return None

def main():
    """メイン処理"""
    try:
        # シェル検出（元のcodex_query.pyの機能を維持）
        detect_shell()
        
        # 初期化
        prompt_file, client, language = initialize()

        # クエリ取得
        user_query, prompt_file = get_query(prompt_file)
        if user_query is None:
            return
        
        config = prompt_file.config if prompt_file else {
            'model': MODEL,
            'temperature': TEMPERATURE,
            'max_tokens': MAX_TOKENS,
            'shell': SHELL,
            'multi_turn': MULTI_TURN,
            'token_count': 0,
            'language': language
        }

        # シェルタイプに応じたプレフィックスを使用
        prefix = ""
        if config['shell'] == "zsh":
            prefix = '#!/bin/zsh\n\n'
        elif config['shell'] == "bash":
            prefix = '#!/bin/bash\n\n'
        elif config['shell'] == "powershell":
            prefix = '<# powershell #>\n\n'
        else:
            prefix = '#' + config['shell'] + '\n\n'

        # プロンプトの構築
        codex_query = prefix + prompt_file.read_prompt_file(user_query) + user_query
        
        # モデレーションチェック
        if is_sensitive_content(user_query, client):
            print("\n#   不適切なコンテンツが検出されました。応答を制限します。")
            return

        # 応答の生成（ストリーミング方式）
        generated_text = generate_response(codex_query, config['model'], client, config['language'], config['shell'])
        
        # マルチターンモードの場合、会話履歴を保存
        if generated_text and config['multi_turn'] == "on":
            prompt_file.add_input_output_pair(user_query, generated_text)
        
    except FileNotFoundError:
        logging.error('Prompt file not found, try again')
        print('\n\n# Codex CLI error: プロンプトファイルが見つかりません')
    except UnicodeError as e:
        logging.error(f'Unicode encoding error: {str(e)}')
        print(f'\n\n# Codex CLI error: 文字エンコーディングエラー - {str(e)}')
    except Exception as e:
        logging.error(f'Unexpected exception - {str(e)}')
        print('\n\n# Codex CLI error: 予期しないエラーが発生しました - ' + str(e))

if __name__ == '__main__':
    main()