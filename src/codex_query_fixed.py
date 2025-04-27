import re
import os
import sys
import time
import configparser
import openai
import json
import logging
from prompt_file import PromptFile

# デバッグログ設定
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "codex_debug.log")
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, 
                   format='%(asctime)s - %(levelname)s - %(message)s')

def read_openai_api_key():
    """
    環境変数からOpenAI APIキーを読み込みます。
    """
    try:
        # 環境変数からAPIキーを取得
        api_key = os.environ.get('OPENAI_API_KEY')
        model = os.environ.get('OPENAI_MODEL', 'gpt-4o')
        # APIキー未設定の場合はエラー
        if not api_key:
            logging.error("環境変数OPENAI_API_KEYが設定されていません")
            print("エラー: 環境変数OPENAI_API_KEYを設定してください")
            sys.exit(1)
        # 組織IDは環境変数から取得（必須ではない）
        organization = os.environ.get('OPENAI_ORG_ID')
        return api_key, organization, model
    except Exception as e:
        logging.error(f"API設定の読み込みエラー: {str(e)}")
        print(f"\n# エラー: API設定の読み込みに失敗しました: {str(e)}")
        sys.exit(1)

def format_prompt(input_text):
    """
    プロンプトをフォーマットする（システムプロンプトを含む）
    """
    # シェル設定（環境変数やユーザー設定から取得可能）
    shell_type = "powershell"  # デフォルトは PowerShell
    
    # OSの種類を検出
    import platform
    os_type = platform.system()
    
    # システムプロンプト - Codex CLI用に特化（説明とコマンド両方を含む）
    system_prompt = f"""あなたはコマンドライン専門のアシスタントです。
以下のフォーマットで回答してください：
1. まず「# 」で始まる1行のコメントで、何をするコマンドかを簡潔に説明する
2. 次の行に実行可能な{shell_type}のコマンドを提示する（説明なし）
3. 必要に応じて、追加の「# 」コメント行とコマンド行のペアを続ける

コマンドの前後にはバッククォート(`)やその他の記号を付けないでください。
複数のコマンドが必要な場合は、それらを別々の行に表示してください。
長い説明は避け、簡潔なコメントと実用的なコマンドに集中してください。
現在のOSは{os_type}です。

例：
# 現在のIPアドレスを表示
Get-NetIPAddress | Where-Object AddressFamily -eq IPv4 | Select-Object IPAddress, InterfaceAlias

# ディスク使用量を確認
Get-Volume | Where-Object DriveLetter | Sort-Object SizeRemaining
"""
    
    # フォーマット済みのプロンプト文字列を返す
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input_text}
    ]

def get_input_from_args():
    """
    コマンドライン引数から入力を取得
    """
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])
    return None

def get_input_from_stdin():
    """
    標準入力から入力を取得（パイプ入力とインタラクティブ入力の両方に対応）
    """
    import select
    import platform
    
    # Windowsの場合のパイプ処理特別対応
    is_windows = platform.system() == "Windows"
    
    try:
        # パイプからの入力があるか確認
        if is_windows:
            # Windowsでは select が stdin に対して正しく動作しないため、
            # 別のアプローチを使用
            import msvcrt
            if msvcrt.kbhit():
                # キーボード入力あり - インタラクティブモード
                print("# コマンドを入力してください (Ctrl+Cで終了):")
                return input().strip()
            else:
                # パイプ入力の可能性あり
                try:
                    data = sys.stdin.buffer.read()
                    if data:
                        return data.decode('utf-8', errors='replace').strip()
                    else:
                        print("# パイプ入力が空です")
                        print("# コマンドを入力してください:")
                        return input().strip()
                except Exception as e:
                    logging.debug(f"パイプ入力の読み取りに失敗: {str(e)}")
                    print("# パイプ経由での実行に失敗しました。直接入力を試みます...")
                    print("# コマンドを入力してください:")
                    return input().strip()
        else:
            # Unix系OSの場合
            print("# コマンドを入力してください (Ctrl+Cで終了):")
            # 5秒間の入力待機
            ready, _, _ = select.select([sys.stdin], [], [], 5.0)
            if ready:
                return sys.stdin.readline().strip()
            else:
                print("# 入力がタイムアウトしました")
                return None
    except Exception as e:
        logging.error(f"入力の取得中にエラーが発生: {str(e)}")
        print(f"# 入力エラー: {str(e)}")
        print("# コマンドを直接入力してください:")
        return input().strip()

def get_input_from_file(file_path):
    """
    指定されたファイルから入力を読み込む
    """
    try:
        logging.debug(f"ファイルから入力を読み込みます: {file_path}")
        if not os.path.exists(file_path):
            logging.error(f"ファイルが存在しません: {file_path}")
            print(f"# エラー: ファイル {file_path} が見つかりません")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            logging.debug(f"ファイルからの入力: {file_path} (サイズ: {len(content)} バイト)")
            logging.debug(f"ファイル内容の最初の100文字: {content[:100]}")
            print(f"# ファイルから入力を読み込みました: {len(content)} バイト")
            return content
    except UnicodeDecodeError:
        logging.error(f"ファイルのエンコーディングエラー: {file_path}")
        # UTF-8以外のエンコーディングを試す
        try:
            with open(file_path, 'r', encoding='shift-jis') as file:
                content = file.read().strip()
                logging.debug(f"Shift-JISエンコーディングで読み込み成功: {file_path}")
                return content
        except:
            pass
        print(f"# エラー: ファイル {file_path} のエンコーディングが不明です")
        return None
    except Exception as e:
        logging.error(f"ファイル読み込みエラー: {str(e)}")
        print(f"# エラー: ファイル {file_path} の読み込みに失敗しました: {str(e)}")
        return None

def generate_response(prompt, model, config):
    """
    OpenAI APIを使用して応答を生成
    """
    logging.debug(f"APIリクエスト: モデル={model}, プロンプト長={len(str(prompt))}")
    
    try:
        # 新しいOpenAI APIのクライアント初期化
        api_key, organization, _ = read_openai_api_key()
        client = openai.OpenAI(api_key=api_key, organization=organization)
        
        # ストリーミング応答の生成
        temperature = config['temperature']
        stream = client.chat.completions.create(
            model=model,
            messages=prompt,  # メッセージ形式のプロンプト
            temperature=temperature,
            stream=True
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                # コンテンツを処理
                print(content, end="", flush=True)
    
    except openai.RateLimitError as e:
        # レート制限エラー
        logging.error(f"OpenAI レート制限エラー: {str(e)}")
        return f"\n# エラー: APIレート制限に達しました。しばらく待ってから再試行してください。\n# {str(e)}"
    
    except openai.APIError as e:
        # 一般的なAPI エラー
        logging.error(f"OpenAI API エラー: {str(e)}")
        return f"\n# エラー: API呼び出し中にエラーが発生しました。\n# {str(e)}"
    
    except Exception as e:
        # その他の例外
        logging.error(f"予期しないエラー: {str(e)}", exc_info=True)
        return f"\n# エラー: 予期しないエラーが発生しました。\n# {str(e)}"

def main():
    """
    メイン処理
    """
    try:
        # OpenAI API設定の読み込み
        api_key, organization, model = read_openai_api_key()
        logging.debug(f"使用するモデル: {model}")
        
        # 引数の解析
        input_text = None
        file_path = None
        
        logging.debug(f"コマンドライン引数: {sys.argv}")
        
        # --file オプションのチェック
        if len(sys.argv) >= 3 and sys.argv[1] == "--file":
            file_path = sys.argv[2]
            logging.debug(f"ファイルオプション検出: {file_path}")
            input_text = get_input_from_file(file_path)
        else:
            # 通常のコマンドライン引数からの入力取得
            logging.debug("コマンドライン引数から入力を取得します")
            input_text = get_input_from_args()
        
        # 引数がなければ標準入力から取得
        if not input_text:
            logging.debug("標準入力から入力を取得します")
            input_text = get_input_from_stdin()
        
        # 入力がない場合は終了
        if not input_text or input_text.strip() == '':
            logging.error("入力がありません")
            print("# エラー: 入力がありません")
            return
            
        logging.debug(f"処理する入力: '{input_text[:100]}...'")
        
        # 設定の準備
        config = {
            'model': model,
            'temperature': 0.7,
            'max_tokens': 1000,
            'shell': 'powershell',
            'multi_turn': 'off',
            'token_count': 0
        }
        
        # プロンプトファイルの初期化
        prompt_file = PromptFile("current_context.txt", config)
        
        # プロンプトのフォーマット
        formatted_prompt = format_prompt(input_text)
        
        # 応答の生成
        generate_response(formatted_prompt, model, config)
        
        # マルチターンモードの場合、会話をファイルに保存
        if config['multi_turn'] == 'on':
            prompt_file.add_input_output_pair(formatted_prompt, None)
        
    except KeyboardInterrupt:
        print("\n# 処理がキャンセルされました")
    
    except Exception as e:
        logging.error(f"実行エラー: {str(e)}", exc_info=True)
        print(f"\n# エラー: {str(e)}")

if __name__ == "__main__":
    main()
