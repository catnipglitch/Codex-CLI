#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import configparser
import json
import logging
import re
import psutil

from pathlib import Path
from prompt_file import PromptFile
from commands import get_command_result

# ログ設定
logging.basicConfig(
    filename=os.path.join(os.getcwd(), 'codex_debug.log'),
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

MULTI_TURN = "off"
SHELL = ""

MODEL = 'gpt-4o'
TEMPERATURE = 0
MAX_TOKENS = 300

DEBUG_MODE = False

# api keys located in the same directory as this file
API_KEYS_LOCATION = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'openaiapirc')

PROMPT_CONTEXT = Path(__file__).with_name('current_context.txt')

def load_config():
    """設定を読み込む"""
    try:
        # Codex CLI専用設定ファイル(~/.openai/codex-cli.json)をチェック
        home = os.path.expanduser("~")
        codex_cli_path = os.path.join(home, ".openai", "codex-cli.json")
        logging.debug(f"Codex CLI設定ファイルを確認中: {codex_cli_path}")
        
        api_key = None
        organization = None
        model_name = "gpt-4o"
        language = "en"  # デフォルト言語は英語
        
        # codex-cli.jsonから設定を読み込む
        if os.path.exists(codex_cli_path):
            logging.debug(f"Codex CLI設定ファイル発見: {codex_cli_path}")
            try:
                with open(codex_cli_path, 'r', encoding='utf-8') as file:
                    config = json.load(file)
                api_key = config.get("api_key")
                organization = config.get("organization")
                model_name = config.get("model", "gpt-4o")
                language = config.get("language", "en")
                logging.debug(f"言語設定: {language}")
                logging.debug(f"APIキーの長さ: {len(api_key) if api_key else 0}")
            except Exception as load_err:
                logging.error(f"設定ファイル読み込みエラー: {str(load_err)}")
        else:
            # 後方互換性のために古い設定ファイル(settings.json)もチェック
            old_settings_path = os.path.join(home, ".openai", "settings.json")
            if os.path.exists(old_settings_path):
                logging.debug(f"旧設定ファイル発見: {old_settings_path}")
                try:
                    with open(old_settings_path, 'r', encoding='utf-8') as file:
                        config = json.load(file)
                    api_key = config.get("api_key")
                    organization = config.get("organization")
                    model_name = config.get("model", "gpt-4o")
                    language = config.get("language", "en")
                    logging.debug(f"(旧設定から)言語設定: {language}")
                except Exception as old_err:
                    logging.error(f"旧設定ファイル読み込みエラー: {str(old_err)}")
        
        if api_key and organization:
            logging.info("設定読み込み成功")
            return api_key, organization, model_name, language
        
        # 設定ファイルが存在しない場合は、テンプレート作成ガイドを呼び出す
        logging.warning("設定ファイルが見つかりません")
        create_template_ini_file()
        sys.exit(1)
    except Exception as e:
        logging.error(f"設定の読み込み中にエラーが発生しました: {str(e)}")
        print(f"エラー: 設定の読み込みに失敗しました - {str(e)}")
        sys.exit(1)

def create_template_ini_file():
    """
    設定ファイルが存在しない場合、ユーザーにファイル作成を促します
    """
    home = os.path.expanduser("~")
    codex_cli_path = os.path.join(home, ".openai", "codex-cli.json")
    
    if not os.path.exists(os.path.dirname(codex_cli_path)):
        try:
            os.makedirs(os.path.dirname(codex_cli_path))
            logging.debug(f".openaiフォルダを作成しました: {os.path.dirname(codex_cli_path)}")
        except Exception as e:
            logging.error(f".openaiフォルダの作成に失敗しました: {str(e)}")
    
    if not os.path.exists(codex_cli_path):
        print(f'# 設定ファイルが見つかりません。以下の場所に作成してください: {codex_cli_path}')
        print('# フォーマットは次のとおりです:\n')
        print('{')
        print('  "api_key": "YOUR_API_KEY",')
        print('  "organization": "YOUR_ORGANIZATION_ID",')
        print('  "model": "gpt-4o",')
        print('  "language": "en"  // 言語設定: "en"(英語)または"ja"(日本語)')
        print('}')
        sys.exit(1)

def initialize():
    """
    Initialize openAI and shell mode
    """
    global MODEL

    # Check if file at API_KEYS_LOCATION exists
    create_template_ini_file()
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
    """
    Check if the content contains sensitive content
    Uses OpenAI's moderation API
    """

    if len(content) == 0:
        return False
    
    try:
        # 新しいOpenAI APIの呼び出し方法
        response = client.moderations.create(input=content)
        return response.results[0].flagged
    except Exception as e:
        logging.error(f"Error checking content moderation: {e}")
        print(f"Error checking content moderation: {e}")
        # If moderation check fails, assume it's safe to continue
        return False

def get_query(prompt_file):
    """
    uses the stdin to get user input
    input is either treated as a command or as a Codex query

    Returns: command result or context + input from stdin
    """

    # get input from terminal or stdin
    try:
        # コマンドライン引数をチェック
        input_file = None
        if len(sys.argv) > 1:
            # 引数が渡された場合、それをファイルパスとして扱う
            potential_file = sys.argv[1]
            if os.path.exists(potential_file):
                input_file = potential_file
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
            # Windows環境での標準入力処理を改善
            if os.name == 'nt':
                # Windowsの場合、コンソールのコードページを取得
                import subprocess
                try:
                    # コードページを取得
                    cp_process = subprocess.run('chcp', shell=True, capture_output=True, text=True)
                    cp_output = cp_process.stdout
                    logging.debug(f"コードページ情報: {cp_output}")
                    
                    # コードページから適切なエンコーディングを決定
                    if '932' in cp_output:  # 日本語Windows
                        encoding = 'cp932'
                    elif '65001' in cp_output:  # UTF-8
                        encoding = 'utf-8'
                    else:
                        encoding = 'cp1252'  # デフォルト
                    
                    logging.debug(f"使用するエンコーディング: {encoding}")
                except Exception as e:
                    logging.error(f"コードページ取得エラー: {str(e)}")
                    encoding = 'utf-8'  # デフォルト
                
                # バイナリモードで読み込み、適切なエンコーディングでデコード
                import io
                stdin_bytes = sys.stdin.buffer.read()
                try:
                    entry = stdin_bytes.decode(encoding, errors='replace')
                except UnicodeDecodeError:
                    # 失敗した場合は別のエンコーディングを試す
                    fallback_encodings = ['utf-8', 'cp932', 'cp1252']
                    for enc in fallback_encodings:
                        if enc != encoding:
                            try:
                                entry = stdin_bytes.decode(enc, errors='replace')
                                logging.debug(f"フォールバックエンコーディング {enc} で成功")
                                break
                            except UnicodeDecodeError:
                                continue
                    else:
                        # すべて失敗した場合
                        entry = stdin_bytes.decode('ascii', errors='replace')
                        logging.error("すべてのエンコーディングが失敗、ASCIIで代替")
            else:
                # Unix系の場合
                entry = sys.stdin.read()
        
        if entry:
            logging.debug(f"入力文字列（最初の50文字）: {entry[:50]}")
        else:
            logging.error("入力が空です")
            entry = ""
            
        # first we check if the input is a command
        command_result, prompt_file = get_command_result(entry, prompt_file)

        # if input is not a command, then query Codex, otherwise exit command has been run successfully
        if command_result == "":
            return entry, prompt_file
        else:
            sys.exit(0)
    except UnicodeError as e:
        logging.error(f'Unicode encoding error: {str(e)}')
        print('\n\n# Codex CLI error: 文字エンコーディングエラー。マルチバイト文字や絵文字を含む可能性があります - ' + str(e))
        sys.exit(1)

def detect_shell():
    global SHELL
    global PROMPT_CONTEXT

    # シェル検出をより堅牢にする
    try:
        # Windowsの場合は特別な処理
        if os.name == 'nt':
            # PowerShellを使用していると仮定
            SHELL = "powershell"
            logging.debug("Windows環境を検出: PowerShellを使用")
        else:
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
            
        logging.debug(f"検出されたシェル: {SHELL}")

        # コンテキストファイルのパスを設定
        shell_prompt_file = Path(os.path.join(os.path.dirname(__file__), "..", "contexts", "{}-context.txt".format(SHELL)))

        if shell_prompt_file.is_file():
            PROMPT_CONTEXT = shell_prompt_file
            logging.debug(f"シェル用コンテキストファイルを使用: {PROMPT_CONTEXT}")
        else:
            logging.warning(f"シェル用コンテキストファイルが見つかりません: {shell_prompt_file}")
    except Exception as e:
        # 検出に失敗した場合はデフォルト値を使用
        if os.name == 'nt':
            SHELL = "powershell"
        else:
            SHELL = "bash"
        logging.error(f"シェル検出中にエラーが発生しました: {str(e)}。デフォルト: {SHELL}")
        
        # デフォルトコンテキストファイルを使用
        default_context = Path(os.path.join(os.path.dirname(__file__), "..", "contexts", "{}-context.txt".format(SHELL)))
        if default_context.is_file():
            PROMPT_CONTEXT = default_context

if __name__ == '__main__':
    detect_shell()
    prompt_file, client, language = initialize()

    try:
        user_query, prompt_file = get_query(prompt_file)
        
        config = prompt_file.config if prompt_file else {
            'model': MODEL,
            'temperature': TEMPERATURE,
            'max_tokens': MAX_TOKENS,
            'shell': SHELL,
            'multi_turn': MULTI_TURN,
            'token_count': 0,
            'language': language
        }

        # use query prefix to prime Codex for correct scripting language
        prefix = ""
        # prime codex for the corresponding shell type
        if config['shell'] == "zsh":
            prefix = '#!/bin/zsh\n\n'
        elif config['shell'] == "bash":
            prefix = '#!/bin/bash\n\n'
        elif config['shell'] == "powershell":
            prefix = '<# powershell #>\n\n'
        elif config['shell'] == "unknown":
            # 未知のシェルの場合はPowerShellとして扱う
            prefix = '<# powershell #>\n\n'
            print("\n#\tShell type not detected, using PowerShell as default. Use # set shell <shell> to change.")
        else:
            prefix = '#' + config['shell'] + '\n\n'

        codex_query = prefix + prompt_file.read_prompt_file(user_query) + user_query

        # 文字エンコーディング処理を改善
        try:
            # システムプロンプトを言語設定に基づいて選択
            system_prompt = ""
            if config.get('language') == "ja":
                system_prompt = "あなたは自然言語をシェルコマンドに変換する助手です。説明やマークダウン形式なしで、コマンドのみを提供してください。コマンドは直接実行可能である必要があります。"
                logging.debug("日本語システムプロンプトを使用")
            else:
                system_prompt = "You are a helpful assistant that translates natural language into shell commands. Provide only the command without any explanation or markdown formatting. The command should be directly executable."
                logging.debug("英語システムプロンプトを使用")
            
            # タイムアウト処理を追加（Windowsでも動作する方法）
            import threading
            import time
            
            # タイムアウト例外クラス
            class TimeoutError(Exception):
                pass
            
            # 直接APIを呼び出す（シンプルな方法に戻す）
            logging.debug("APIリクエスト開始")
            print("\n#   処理中...", end="", flush=True)
            
            # エラーフラグ
            api_error = False
            
            try:
                # OpenAI APIの呼び出し
                response = client.chat.completions.create(
                    model=config['model'],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": codex_query}
                    ],
                    temperature=config['temperature'],
                    max_tokens=config['max_tokens'],
                    stop=["#"]
                    # timeout=60  # OpenAI APIはtimeoutパラメータをサポートしていない
                )
                
                # 処理中メッセージをクリア
                print("\r                 \r", end="", flush=True)
                
                # 応答を処理
                if response and response.choices and len(response.choices) > 0:
                    generated_text = response.choices[0].message.content.strip()
                    logging.debug(f"APIリクエスト完了: {generated_text[:50] if len(generated_text) > 50 else generated_text}...")
                else:
                    logging.error("APIレスポンスが不正な形式です")
                    print("\n#   エラー: APIからの応答が不正な形式です。再試行してください。")
                    api_error = True
                    
            except Exception as e:
                # 処理中メッセージをクリア
                print("\r                 \r", end="", flush=True)
                logging.error(f"APIリクエスト中にエラーが発生: {str(e)}")
                print(f"\n#   エラー: APIリクエスト中にエラーが発生しました: {str(e)}")
                api_error = True
                
            # タイムアウトフラグ（後方互換性のため）
            timeout_occurred = False
        except UnicodeError as e:
            logging.error(f'API呼び出し時のUnicodeエラー: {str(e)}')
            # エラーが発生した場合は問題のある文字を置換
            try:
                # まずUTF-8として処理を試みる
                clean_query = codex_query.encode('utf-8', 'replace').decode('utf-8')
            except UnicodeError:
                # UTF-8で失敗した場合、cp932（Shift-JIS）を試す
                try:
                    clean_query = codex_query.encode('cp932', 'replace').decode('cp932')
                except UnicodeError:
                    # どちらも失敗した場合は、ASCII文字のみに制限
                    clean_query = ''.join(c for c in codex_query if ord(c) < 128)
            
            logging.debug(f"クリーニング後のクエリ: {clean_query}")
            
            # システムプロンプトを言語設定に基づいて選択
            system_prompt = ""
            if config.get('language') == "ja":
                system_prompt = "あなたは自然言語をシェルコマンドに変換する助手です。説明やマークダウン形式なしで、コマンドのみを提供してください。コマンドは直接実行可能である必要があります。"
                logging.debug("日本語システムプロンプトを使用（エラー後）")
            else:
                system_prompt = "You are a helpful assistant that translates natural language into shell commands. Provide only the command without any explanation or markdown formatting. The command should be directly executable."
                logging.debug("英語システムプロンプトを使用（エラー後）")
            
            response = client.chat.completions.create(
                model=config['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": clean_query}
                ],
                temperature=config['temperature'],
                max_tokens=config['max_tokens'],
                stop=["#"]
            )
            generated_text = response.choices[0].message.content.strip()

        # エラーが発生していない場合のみ処理を続行
        if not api_error and not timeout_occurred:
            if is_sensitive_content(user_query + '\n' + generated_text, client):
                print("\n#   Sensitive content detected, response has been redacted")
            else:
                # 出力時のエンコーディングも考慮
                try:
                    # Windows環境での出力処理を改善
                    if os.name == 'nt':
                        # コンソール出力用のエンコーディングを設定
                        import subprocess
                        try:
                            # コードページを取得
                            cp_process = subprocess.run('chcp', shell=True, capture_output=True, text=True)
                            cp_output = cp_process.stdout
                            
                            # コードページから適切なエンコーディングを決定
                            if '932' in cp_output:  # 日本語Windows
                                # cp932でエンコードしてから出力
                                output_bytes = generated_text.encode('cp932', 'replace')
                                sys.stdout.buffer.write(output_bytes)
                                sys.stdout.buffer.flush()
                            else:
                                # 通常の出力
                                print(generated_text)
                        except Exception as e:
                            logging.error(f"出力処理エラー: {str(e)}")
                            print(generated_text)
                    else:
                        # Unix系の場合は通常の出力
                        print(generated_text)
                except UnicodeEncodeError:
                    # エンコーディングエラーが発生した場合の対処
                    try:
                        # cp932で再エンコード
                        encoded_text = generated_text.encode('cp932', 'replace').decode('cp932')
                        print(encoded_text)
                    except:
                        # 最終手段として、ASCII文字のみに制限
                        safe_text = ''.join(c for c in generated_text if ord(c) < 128)
                        print(safe_text)
                        print("\n# 警告: 一部の文字が表示できません")

            # append output to prompt context file
            if config['multi_turn'] == "on":
                if generated_text != "" or len(generated_text) > 0:
                    prompt_file.add_input_output_pair(user_query, generated_text)
        
    except FileNotFoundError:
        logging.error('Prompt file not found, try again')
        print('\n\n# Codex CLI error: Prompt file not found, try again')
    except openai.RateLimitError:
        logging.error('Rate limit exceeded, try later')
        print('\n\n# Codex CLI error: Rate limit exceeded, try later')
    except openai.APIError:
        logging.error('API connection error, are you connected to the internet?')
        print('\n\n# Codex CLI error: API connection error, are you connected to the internet?')
    except UnicodeError as e:
        logging.error(f'Unicode encoding error: {str(e)}')
        print(f'\n\n# Codex CLI error: 文字エンコーディングエラー - {str(e)}')
    except Exception as e:
        logging.error(f'Unexpected exception - {str(e)}')
        print('\n\n# Codex CLI error: Unexpected exception - ' + str(e))
