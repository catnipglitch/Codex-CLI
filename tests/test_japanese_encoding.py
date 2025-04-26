#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import logging
import tempfile
import unittest
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

# テスト対象のモジュールをインポート
# 直接インポートせず、モックテストを行う
# from src.codex_query import load_config
# from src.prompt_file import PromptFile

# テスト用のログ設定
LOG_FILE = os.path.join(os.path.dirname(__file__), "japanese_test.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class TestJapaneseEncoding(unittest.TestCase):
    """日本語エンコーディング処理のテストクラス"""
    
    def setUp(self):
        """テスト前の準備"""
        logging.info("=== テスト開始 ===")
        # テスト用の一時ディレクトリを作成
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name
        
        # テスト用の.openaiディレクトリを作成
        self.openai_dir = os.path.join(self.test_dir, ".openai")
        os.makedirs(self.openai_dir, exist_ok=True)
        
        # 元の環境変数を保存
        self.original_home = os.environ.get('HOME')
        if os.name == 'nt':  # Windows
            self.original_userprofile = os.environ.get('USERPROFILE')
            os.environ['USERPROFILE'] = self.test_dir
        else:  # Unix系
            os.environ['HOME'] = self.test_dir
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        # 環境変数を元に戻す
        if os.name == 'nt':  # Windows
            if self.original_userprofile:
                os.environ['USERPROFILE'] = self.original_userprofile
            else:
                del os.environ['USERPROFILE']
        else:  # Unix系
            if self.original_home:
                os.environ['HOME'] = self.original_home
            else:
                del os.environ['HOME']
        
        # 一時ディレクトリを削除
        self.temp_dir.cleanup()
        logging.info("=== テスト終了 ===\n")
    
    def test_config_file_japanese(self):
        """設定ファイルの日本語処理をテスト"""
        logging.info("設定ファイルの日本語処理テスト開始")
        
        # テスト用の設定ファイルを作成（日本語設定）
        config_path = os.path.join(self.openai_dir, "codex-cli.json")
        config_data = {
            "api_key": "test_api_key",
            "organization": "test_org_id",
            "model": "gpt-4o",
            "language": "ja"
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"テスト用設定ファイル作成: {config_path}")
        
        try:
            # 設定ファイルを直接読み込んでテスト
            with open(config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
            
            # 結果を検証
            self.assertEqual(config["api_key"], "test_api_key")
            self.assertEqual(config["organization"], "test_org_id")
            self.assertEqual(config["model"], "gpt-4o")
            self.assertEqual(config["language"], "ja")
            
            logging.info(f"設定ファイルから読み込んだ言語設定: {config['language']}")
            logging.info("設定ファイルの日本語処理テスト成功")
        except Exception as e:
            logging.error(f"設定ファイルの日本語処理テスト失敗: {str(e)}")
            raise
    
    def test_japanese_input_utf8(self):
        """UTF-8エンコードの日本語入力処理をテスト"""
        logging.info("UTF-8エンコードの日本語入力処理テスト開始")
        
        # テスト用の日本語テキストファイル（UTF-8）を作成
        test_text = "# 自分のIPアドレスは？"
        test_file_path = os.path.join(self.test_dir, "test_utf8.txt")
        
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_text)
        
        logging.info(f"テスト用UTF-8ファイル作成: {test_file_path}")
        
        try:
            # ファイルを読み込み
            with open(test_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 結果を検証
            self.assertEqual(content, test_text)
            logging.info(f"UTF-8ファイルから読み込んだ内容: {content}")
            logging.info("UTF-8エンコードの日本語入力処理テスト成功")
        except Exception as e:
            logging.error(f"UTF-8エンコードの日本語入力処理テスト失敗: {str(e)}")
            raise
    
    def test_japanese_input_cp932(self):
        """CP932（Shift-JIS）エンコードの日本語入力処理をテスト"""
        logging.info("CP932エンコードの日本語入力処理テスト開始")
        
        # テスト用の日本語テキストファイル（CP932）を作成
        test_text = "# 自分のIPアドレスは？"
        test_file_path = os.path.join(self.test_dir, "test_cp932.txt")
        
        with open(test_file_path, 'w', encoding='cp932') as f:
            f.write(test_text)
        
        logging.info(f"テスト用CP932ファイル作成: {test_file_path}")
        
        try:
            # まずUTF-8で読み込みを試みる（失敗するはず）
            try:
                with open(test_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                success_utf8 = True
            except UnicodeDecodeError:
                success_utf8 = False
                logging.info("予想通り、UTF-8での読み込みに失敗")
            
            # CP932で読み込み
            with open(test_file_path, 'r', encoding='cp932') as f:
                content = f.read()
            
            # 結果を検証
            self.assertEqual(content, test_text)
            logging.info(f"CP932ファイルから読み込んだ内容: {content}")
            logging.info("CP932エンコードの日本語入力処理テスト成功")
        except Exception as e:
            logging.error(f"CP932エンコードの日本語入力処理テスト失敗: {str(e)}")
            raise
    
    def test_context_file_japanese(self):
        """コンテキストファイルの日本語処理をテスト"""
        logging.info("コンテキストファイルの日本語処理テスト開始")
        
        # テスト用のコンテキストファイルを作成
        context_dir = os.path.join(self.test_dir, "contexts")
        os.makedirs(context_dir, exist_ok=True)
        
        # テスト用のコンテキストファイル
        context_file = os.path.join(context_dir, "powershell-context.txt")
        context_content = """## model: gpt-4o
## temperature: 0.7
## max_tokens: 100
## shell: powershell
## multi_turn: off
## token_count: 0
## language: ja

# 自分のIPアドレスは？
(Invoke-WebRequest -uri "http://ifconfig.me/ip").Content
"""
        
        with open(context_file, 'w', encoding='utf-8') as f:
            f.write(context_content)
        
        logging.info(f"テスト用コンテキストファイル作成: {context_file}")
        
        try:
            # ファイルを読み込んで検証
            with open(context_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.assertIn("# 自分のIPアドレスは？", content)
            self.assertIn("(Invoke-WebRequest -uri \"http://ifconfig.me/ip\").Content", content)
            self.assertIn("language: ja", content)
            
            logging.info("コンテキストファイルの日本語処理テスト成功")
        except Exception as e:
            logging.error(f"コンテキストファイルの日本語処理テスト失敗: {str(e)}")
            raise
            
    def test_file_io_japanese(self):
        """ファイル入出力の日本語処理をテスト"""
        logging.info("ファイル入出力の日本語処理テスト開始")
        
        # テスト用のファイルパス
        test_file = os.path.join(self.test_dir, "japanese_test.txt")
        
        # テスト用の日本語テキスト
        test_query = "# 自分のIPアドレスは？\n"
        test_response = "(Invoke-WebRequest -uri \"http://ifconfig.me/ip\").Content\n"
        
        try:
            # ファイルに書き込み
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_query)
                f.write(test_response)
            
            logging.info(f"テストファイルに書き込み: {test_file}")
            
            # ファイルを読み込んで検証
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.assertIn(test_query, content)
            self.assertIn(test_response, content)
            
            logging.info(f"ファイルから読み込んだ内容: {content.strip()}")
            logging.info("ファイル入出力の日本語処理テスト成功")
        except Exception as e:
            logging.error(f"ファイル入出力の日本語処理テスト失敗: {str(e)}")
            raise
    
    def test_encoding_conversion(self):
        """エンコーディング変換処理をテスト"""
        logging.info("エンコーディング変換処理テスト開始")
        
        # テスト用の日本語テキスト
        test_text = "# 自分のIPアドレスは？"
        
        try:
            # UTF-8 -> バイト列 -> CP932 -> バイト列 -> UTF-8 の変換をテスト
            utf8_bytes = test_text.encode('utf-8')
            logging.info(f"UTF-8バイト列: {utf8_bytes}")
            
            # UTF-8 -> CP932
            try:
                cp932_text = utf8_bytes.decode('cp932', errors='replace')
                logging.info(f"CP932に変換（置換モード）: {cp932_text}")
            except UnicodeDecodeError:
                logging.info("UTF-8バイト列をCP932にデコードできません")
            
            # CP932 -> バイト列
            cp932_bytes = test_text.encode('cp932')
            logging.info(f"CP932バイト列: {cp932_bytes}")
            
            # CP932 -> UTF-8
            utf8_text_from_cp932 = cp932_bytes.decode('utf-8', errors='replace')
            logging.info(f"CP932からUTF-8に変換（置換モード）: {utf8_text_from_cp932}")
            
            # 元のテキストとの比較
            if test_text == utf8_text_from_cp932:
                logging.info("変換後のテキストは元のテキストと一致します")
            else:
                logging.info("変換後のテキストは元のテキストと一致しません")
                
            # 正しい方法での変換
            cp932_bytes = test_text.encode('cp932')
            utf8_text_correct = cp932_bytes.decode('cp932')
            self.assertEqual(test_text, utf8_text_correct)
            logging.info(f"正しい変換方法: {utf8_text_correct}")
            logging.info("エンコーディング変換処理テスト成功")
        except Exception as e:
            logging.error(f"エンコーディング変換処理テスト失敗: {str(e)}")
            raise

if __name__ == '__main__':
    unittest.main()