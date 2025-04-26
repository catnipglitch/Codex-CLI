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
    filename='d:/catglitch_work/Codex-CLI/codex_debug.log',
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
        # Codex CLI専用設定ファイル(~/.openai/codex-cli.json)だけをチェック
        home = os.path.expanduser("~")
        codex_cli_path = os.path.join(home, ".openai", "codex-cli.json")
        logging.debug(f"Codex CLI設定ファイルを確認中: {codex_cli_path}")
        
        if os.path.exists(codex_cli_path):
            logging.debug(f"Codex CLI設定ファイル発見: {codex_cli_path}")
            with open(codex_cli_path, 'r') as file:
                config = json.load(file)
            return config.get("api_key"), config.get("organization"), config.get("model", "gpt-4o")
        
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
        print('  "model": "gpt-4o"')
        print('}')
        sys.exit(1)

def initialize():
    """
    Initialize openAI and shell mode
    """
    global MODEL

    # Check if file at API_KEYS_LOCATION exists
    create_template_ini_file()
    api_key, org_id, model_name = load_config()

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
        'token_count': 0
    }
    
    return PromptFile(PROMPT_CONTEXT.name, prompt_config), client

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
        if DEBUG_MODE:
            entry = input("prompt: ") + '\n'
        else:
            entry = sys.stdin.read()
            
        # サロゲートペア文字など不正なUTF-8シーケンスをエスケープ処理
        if isinstance(entry, str):
            # サロゲートペアの文字をエスケープ処理
            entry = entry.encode('utf-8', 'surrogateescape').decode('utf-8', 'replace')
            
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
        parent_process_name = psutil.Process(os.getppid()).name().lower()
        logging.debug(f"親プロセス名: {parent_process_name}")
        
        # PowerShellの検出を強化
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
        
        # Windowsプラットフォームの場合、デフォルトでPowerShellと見なす
        if os.name == 'nt' and not (POWERSHELL_MODE or BASH_MODE or ZSH_MODE):
            POWERSHELL_MODE = True
            logging.debug("Windowsプラットフォームを検出: PowerShellをデフォルトとして使用")
            
        SHELL = "powershell" if POWERSHELL_MODE else "bash" if BASH_MODE else "zsh" if ZSH_MODE else "unknown"
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
    prompt_file, client = initialize()

    try:
        user_query, prompt_file = get_query(prompt_file)
        
        config = prompt_file.config if prompt_file else {
            'model': MODEL,
            'temperature': TEMPERATURE,
            'max_tokens': MAX_TOKENS,
            'shell': SHELL,
            'multi_turn': MULTI_TURN,
            'token_count': 0
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
            print("\n#\tUnsupported shell type, please use # set shell <shell>")
        else:
            prefix = '#' + config['shell'] + '\n\n'

        codex_query = prefix + prompt_file.read_prompt_file(user_query) + user_query

        # サロゲートペア文字など不正なUTF-8シーケンスを処理
        try:
            # 新しいOpenAI APIの呼び出し方法を使用
            response = client.chat.completions.create(
                model=config['model'],
                messages=[{"role": "user", "content": codex_query}],
                temperature=config['temperature'],
                max_tokens=config['max_tokens'],
                stop=["#"]
            )
            generated_text = response.choices[0].message.content
        except UnicodeError as e:
            logging.error(f'API呼び出し時のUnicodeエラー: {str(e)}')
            # エラーが発生した場合は問題のある文字を置換
            clean_query = codex_query.encode('utf-8', 'replace').decode('utf-8')
            response = client.chat.completions.create(
                model=config['model'],
                messages=[{"role": "user", "content": clean_query}],
                temperature=config['temperature'],
                max_tokens=config['max_tokens'],
                stop=["#"]
            )
            generated_text = response.choices[0].message.content

        if is_sensitive_content(user_query + '\n' + generated_text, client):
            print("\n#   Sensitive content detected, response has been redacted")
        else:
            print(generated_text)

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
