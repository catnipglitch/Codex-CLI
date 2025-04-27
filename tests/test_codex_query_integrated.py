#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codex_query_integrated.pyの単体テストプログラム
"""

import os
import sys
import unittest
import tempfile
import json
import time
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from io import StringIO

# テスト対象のモジュールパスを追加
sys.path.append(str(Path(__file__).parent.parent / 'src'))

# モジュールをインポート（実際のテスト実行時にロード）
# テスト用の設定
TEST_API_KEY = "test_api_key"
TEST_ORG_ID = "test_org_id"
TEST_MODEL = "gpt-4o"
TEST_LANGUAGE = "ja"

class TestCodexQueryIntegrated(unittest.TestCase):
    """codex_query_integrated.pyのテストクラス"""
    
    @classmethod
    def setUpClass(cls):
        """テスト環境のセットアップ"""
        # 環境変数の既存値を保存
        cls.old_api_key = os.environ.get('OPENAI_API_KEY')
        cls.old_org_id = os.environ.get('OPENAI_ORGANIZATION_ID')
        cls.old_model = os.environ.get('OPENAI_MODEL')
        
        # テスト用の環境変数を設定
        os.environ['OPENAI_API_KEY'] = TEST_API_KEY
        os.environ['OPENAI_ORGANIZATION_ID'] = TEST_ORG_ID
        os.environ['OPENAI_MODEL'] = TEST_MODEL
        
        # テスト用の設定ファイル
        cls.temp_config_dir = tempfile.mkdtemp()
        cls.temp_config_path = os.path.join(cls.temp_config_dir, "test_config.json")
        config_data = {
            "api_key": TEST_API_KEY,
            "organization": TEST_ORG_ID,
            "model": TEST_MODEL,
            "language": TEST_LANGUAGE
        }
        
        with open(cls.temp_config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False)
            
        # 必要なモジュールをインポート
        import codex_query_integrated
        cls.codex = codex_query_integrated
        
        # モックの準備
        cls.mock_openai = MagicMock()
        cls.mock_prompt_file = MagicMock()

    @classmethod
    def tearDownClass(cls):
        """テスト環境の後片付け"""
        # 環境変数を元に戻す
        if cls.old_api_key is not None:
            os.environ['OPENAI_API_KEY'] = cls.old_api_key
        else:
            os.environ.pop('OPENAI_API_KEY', None)
            
        if cls.old_org_id is not None:
            os.environ['OPENAI_ORGANIZATION_ID'] = cls.old_org_id
        else:
            os.environ.pop('OPENAI_ORGANIZATION_ID', None)
            
        if cls.old_model is not None:
            os.environ['OPENAI_MODEL'] = cls.old_model
        else:
            os.environ.pop('OPENAI_MODEL', None)
        
        # 一時ファイルを削除（安全にファイルの存在を確認してから）
        try:
            if os.path.exists(cls.temp_config_path):
                os.unlink(cls.temp_config_path)
                # ファイルを閉じるために少し待機
                time.sleep(0.1)
            
            if os.path.exists(cls.temp_config_dir):
                os.rmdir(cls.temp_config_dir)
        except Exception as e:
            print(f"Cleanup warning: {str(e)}")

    def setUp(self):
        """各テスト前の準備"""
        pass
        
    def tearDown(self):
        """各テスト後の後片付け"""
        pass
        
    @patch('codex_query_integrated.openai')
    @patch('codex_query_integrated.os.path.exists')
    def test_load_config_from_env(self, mock_exists, mock_openai):
        """環境変数から設定を読み込むテスト"""
        # 設定ファイルは存在しない設定
        mock_exists.return_value = False
        
        # 設定読み込み
        api_key, org_id, model, language = self.codex.load_config()
        
        # 結果の検証
        self.assertEqual(api_key, TEST_API_KEY)
        self.assertEqual(org_id, TEST_ORG_ID)
        self.assertEqual(model, TEST_MODEL)
        self.assertEqual(language, "ja")  # デフォルト値
    
    @patch('codex_query_integrated.openai')
    @patch('codex_query_integrated.os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('codex_query_integrated.json.load')
    def test_load_config_from_file(self, mock_json_load, mock_open_file, mock_exists, mock_openai):
        """設定ファイルから読み込むテスト"""
        # 設定ファイルは存在する設定
        mock_exists.return_value = True
        
        # JSONからの読み込み結果をモック
        mock_json_load.return_value = {
            "api_key": "file_api_key",
            "organization": "file_org_id",
            "model": "gpt-3.5-turbo",
            "language": "en"
        }
        
        # 環境変数を一時的にクリア
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': '',
            'OPENAI_ORGANIZATION_ID': '',
            'OPENAI_MODEL': ''
        }, clear=True):
            # 設定読み込み
            api_key, org_id, model, language = self.codex.load_config()
        
        # 結果の検証
        self.assertEqual(api_key, "file_api_key")
        self.assertEqual(org_id, "file_org_id")
        self.assertEqual(model, "gpt-3.5-turbo")
        self.assertEqual(language, "en")
    
    @patch('codex_query_integrated.openai')
    def test_detect_shell_windows(self, mock_openai):
        """Windowsでのシェル検出テスト"""
        # Windowsの環境をシミュレート
        with patch('codex_query_integrated.os.name', 'nt'):
            self.codex.detect_shell()
            
            # 検証
            self.assertEqual(self.codex.SHELL, "powershell")
    
    @patch('codex_query_integrated.openai')
    @patch('codex_query_integrated.HAS_PSUTIL', False)
    @patch('codex_query_integrated.os.environ.get')
    def test_detect_shell_unix_no_psutil(self, mock_env_get, mock_openai):
        """Unix環境でpsutilがない場合のシェル検出テスト"""
        # Unixの環境をシミュレート
        with patch('codex_query_integrated.os.name', 'posix'):
            # 環境変数でzshを設定
            mock_env_get.return_value = "/bin/zsh"
            
            self.codex.detect_shell()
            
            # 検証
            self.assertEqual(self.codex.SHELL, "zsh")
    
    @patch('codex_query_integrated.openai')
    def test_format_system_prompt(self, mock_openai):
        """システムプロンプト生成テスト"""
        # 日本語プロンプト
        ja_prompt = self.codex.format_system_prompt("ja", "powershell")
        self.assertIn("あなたはコマンドライン専門のアシスタントです", ja_prompt)
        self.assertIn("powershell", ja_prompt)
        
        # 英語プロンプト
        en_prompt = self.codex.format_system_prompt("en", "bash")
        self.assertIn("command line specialist assistant", en_prompt)
        self.assertIn("bash", en_prompt)
    
    @patch('codex_query_integrated.openai')
    @patch('codex_query_integrated.PromptFile')
    def test_initialize(self, mock_prompt_file, mock_openai):
        """初期化テスト"""
        # モックの設定
        mock_prompt_file.return_value = "mock_prompt_file"
        mock_openai.OpenAI.return_value = "mock_client"
        
        # 関数実行
        with patch('codex_query_integrated.load_config') as mock_load_config:
            mock_load_config.return_value = (TEST_API_KEY, TEST_ORG_ID, TEST_MODEL, TEST_LANGUAGE)
            result = self.codex.initialize()
        
        # 検証
        self.assertEqual(result[0], "mock_prompt_file")
        self.assertEqual(result[1], "mock_client")
        self.assertEqual(result[2], TEST_LANGUAGE)
        
        # OpenAI初期化の検証
        mock_openai.OpenAI.assert_called_once_with(
            api_key=TEST_API_KEY,
            organization=TEST_ORG_ID
        )
    
    @patch('codex_query_integrated.openai')
    def test_is_sensitive_content(self, mock_openai):
        """コンテンツモデレーションテスト"""
        # モックの設定
        mock_client = MagicMock()
        mock_results = MagicMock()
        mock_results.results = [MagicMock(flagged=True)]
        mock_client.moderations.create.return_value = mock_results
        
        # 関数実行（不適切なコンテンツ）
        result = self.codex.is_sensitive_content("inappropriate content", mock_client)
        
        # 検証
        self.assertTrue(result)
        mock_client.moderations.create.assert_called_once_with(input="inappropriate content")
        
        # リセット
        mock_client.reset_mock()
        mock_results.results = [MagicMock(flagged=False)]
        
        # 関数実行（適切なコンテンツ）
        result = self.codex.is_sensitive_content("normal content", mock_client)
        
        # 検証
        self.assertFalse(result)

    @patch('codex_query_integrated.openai')
    @patch('codex_query_integrated.get_command_result')
    def test_get_query_command(self, mock_get_command_result, mock_openai):
        """コマンド入力テスト"""
        # コマンドが認識された場合
        mock_get_command_result.return_value = ("command executed", "prompt_file")
        
        # 標準入力をモック
        with patch('codex_query_integrated.sys.stdin') as mock_stdin:
            mock_stdin.read.return_value = "# set temperature 0.8"
            # 標準入力の代わりに引数を使用
            with patch('codex_query_integrated.sys.argv', ['script.py']):
                # sys.exitをキャッチする
                with self.assertRaises(SystemExit) as cm:
                    self.codex.get_query("prompt_file")
                
                # 終了コードが0であることを確認
                self.assertEqual(cm.exception.code, 0)
    
    @patch('codex_query_integrated.openai')
    def test_generate_response_success(self, mock_openai):
        """応答生成成功テスト"""
        # モックの設定
        mock_client = MagicMock()
        
        # モックのストリーミングレスポンスを設定
        mock_delta1 = MagicMock()
        mock_delta1.content = "Hello"
        mock_choice1 = MagicMock()
        mock_choice1.delta = mock_delta1
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [mock_choice1]
        
        mock_delta2 = MagicMock()
        mock_delta2.content = " World"
        mock_choice2 = MagicMock()
        mock_choice2.delta = mock_delta2
        mock_chunk2 = MagicMock()
        mock_chunk2.choices = [mock_choice2]
        
        # ストリーミング応答をシミュレート
        mock_client.chat.completions.create.return_value = [mock_chunk1, mock_chunk2]
        
        # 標準出力をキャプチャ
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # 関数実行
            result = self.codex.generate_response("test prompt", "gpt-4o", mock_client, "en", "bash")
            
            # 検証
            self.assertEqual(result, "Hello World")
            
            # 正しいパラメータでAPIが呼び出されたことを確認
            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args
            kwargs = call_args[1]  # キーワード引数を取得
            self.assertEqual(kwargs.get('model'), 'gpt-4o')
            self.assertTrue(kwargs.get('stream'))
            self.assertEqual(len(kwargs.get('messages')), 2)
            
            # 出力の検証
            output = captured_output.getvalue()
            self.assertIn("Hello World", output)
        finally:
            # 標準出力を元に戻す
            sys.stdout = sys.__stdout__

    @patch('codex_query_integrated.openai')
    def test_generate_response_api_error(self, mock_openai):
        """API エラーテスト"""
        # モックの設定
        mock_client = MagicMock()
        mock_api_error = MagicMock()
        mock_api_error.side_effect = Exception("API Error")
        mock_client.chat.completions.create.side_effect = mock_openai.APIError("API Error")
        
        # 標準出力をキャプチャ
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # 関数実行
            result = self.codex.generate_response("test prompt", "gpt-4o", mock_client, "en", "bash")
            
            # 検証（エラー時にはNoneを返す）
            self.assertIsNone(result)
            
            # 出力の検証
            output = captured_output.getvalue()
            self.assertIn("エラー", output)
        finally:
            # 標準出力を元に戻す
            sys.stdout = sys.__stdout__

    @patch('codex_query_integrated.openai')
    @patch('codex_query_integrated.detect_shell')
    @patch('codex_query_integrated.initialize')
    @patch('codex_query_integrated.get_query')
    @patch('codex_query_integrated.is_sensitive_content')
    @patch('codex_query_integrated.generate_response')
    def test_main_success(self, mock_generate, mock_sensitive, mock_get_query, 
                         mock_initialize, mock_detect_shell, mock_openai):
        """メイン処理テスト（成功ケース）"""
        # モックの設定
        mock_prompt_file = MagicMock()
        mock_prompt_file.config = {
            'model': 'gpt-4o',
            'temperature': 0.7,
            'max_tokens': 300,
            'shell': 'bash',
            'multi_turn': 'on',
            'token_count': 0,
            'language': 'ja'
        }
        mock_prompt_file.read_prompt_file.return_value = "context"
        
        mock_client = MagicMock()
        mock_detect_shell.return_value = None
        mock_initialize.return_value = (mock_prompt_file, mock_client, 'ja')
        mock_get_query.return_value = ("user query", mock_prompt_file)
        mock_sensitive.return_value = False
        mock_generate.return_value = "generated response"
        
        # 関数実行
        self.codex.main()
        
        # 検証
        mock_detect_shell.assert_called_once()
        mock_initialize.assert_called_once()
        mock_get_query.assert_called_once()
        mock_prompt_file.read_prompt_file.assert_called_once_with("user query")
        mock_sensitive.assert_called_once()
        mock_generate.assert_called_once()
        mock_prompt_file.add_input_output_pair.assert_called_once_with("user query", "generated response")

    @patch('codex_query_integrated.openai')
    @patch('codex_query_integrated.detect_shell')
    @patch('codex_query_integrated.initialize')
    @patch('codex_query_integrated.get_query')
    def test_main_no_query(self, mock_get_query, mock_initialize, mock_detect_shell, mock_openai):
        """メイン処理テスト（クエリなし）"""
        # モックの設定
        mock_prompt_file = MagicMock()
        mock_client = MagicMock()
        mock_detect_shell.return_value = None
        mock_initialize.return_value = (mock_prompt_file, mock_client, 'ja')
        mock_get_query.return_value = (None, mock_prompt_file)
        
        # 関数実行
        self.codex.main()
        
        # 検証
        mock_detect_shell.assert_called_once()
        mock_initialize.assert_called_once()
        mock_get_query.assert_called_once()
        # プロンプトファイルのread_prompt_fileは呼ばれない
        mock_prompt_file.read_prompt_file.assert_not_called()

    @patch('codex_query_integrated.openai')
    @patch('codex_query_integrated.detect_shell')
    def test_main_exception(self, mock_detect_shell, mock_openai):
        """メイン処理テスト（例外発生）"""
        # モックの設定
        mock_detect_shell.side_effect = Exception("Test exception")
        
        # 標準出力をキャプチャ
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # 関数実行
            self.codex.main()
            
            # 検証
            mock_detect_shell.assert_called_once()
            
            # 出力の検証
            output = captured_output.getvalue()
            self.assertIn("エラー", output)
        finally:
            # 標準出力を元に戻す
            sys.stdout = sys.__stdout__

# メイン実行部
if __name__ == '__main__':
    unittest.main()