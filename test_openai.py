#!/usr/bin/env python3
import sys
import logging
import os
# ログ設定
logging.basicConfig(
    filename=os.path.join(os.getcwd(), 'openai_test.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

try:
    logging.debug("Pythonバージョン: " + sys.version)
    import openai
    logging.debug(f"OpenAIライブラリバージョン: {openai.__version__}")
    
    # 互換性チェック
    if hasattr(openai, 'OpenAI'):
        logging.debug("このバージョンはnew OpenAI client (v1.0.0以降) に対応しています")
        from openai import APIError
        logging.debug("新しいエラーインポートが成功しました")
    else:
        logging.debug("このバージョンはold OpenAI client (v1.0.0未満) です")
        from openai.error import APIError
        logging.debug("古いエラーインポートが成功しました")
        
    print(f"OpenAI APIテスト成功! バージョン: {openai.__version__}")
    print("詳細はopenai_test.logを確認してください")
    
except ImportError:
    error_msg = "OpenAI APIライブラリがインストールされていないか、エラーが発生しました"
    logging.error(error_msg)
    print(error_msg)
    print("pip install openai コマンドでインストールしてください")
    sys.exit(1)
except Exception as e:
    error_msg = f"その他のエラーが発生しました: {str(e)}"
    logging.error(error_msg)
    print(error_msg)
    sys.exit(1)
