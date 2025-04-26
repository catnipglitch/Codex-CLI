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

def format_prompt(input):
    """
    プロンプトをフォーマットする
    """
    return f"User: {input}\nAssistant: "

def get_input_from_args():
    """
    コマンドライン引数から入力を取得
    """
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])
    return None

def get_input_from_stdin():
    """
    標準入力から入力を取得（タイムアウト付き）
    """
    import select
    
    print("# コマンドを入力してください (Ctrl+Cで終了):")
    
    # 5秒間の入力待機
    ready, _, _ = select.select([sys.stdin], [], [], 5.0)
    if ready:
        return sys.stdin.readline().strip()
    else:
        print("# 入力がタイムアウトしました")
        return None

def generate_response(prompt, model, config):
    """
    OpenAI APIを使用して応答を生成
    """
    logging.debug(f"APIリクエスト: モデル={model}, プロンプト長={len(prompt)}")
    
    try:
        # 新しいOpenAI APIのクライアント初期化
        api_key, organization, _ = read_openai_api_key()
        client = openai.OpenAI(api_key=api_key, organization=organization)
        
        # ストリーミング応答の生成
        temperature = config['temperature']
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
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
        
        # コマンドライン引数からの入力取得
        input_text = get_input_from_args()
        
        # 引数がなければ標準入力から取得
        if not input_text:
            input_text = get_input_from_stdin()
        
        # 入力がない場合は終了
        if not input_text or input_text.strip() == '':
            print("# エラー: 入力がありません")
            return
        
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
