# Codex CLI - 自然言語コマンドラインインターフェース

このプロジェクトは[GPT-4o](https://openai.com/gpt-4o)を使用して、自然言語コマンドをPowerShell、Z shellおよびBashのコマンドに変換します。

**⚠️ 重要なお知らせ: 現在はPowerShellのみが完全にサポートされています。BashとZSHのサポートは実験的であり、十分にテストされていません。**

![Codex Cli GIF](codex_cli.gif)

コマンドラインインターフェース（CLI）は、私たちが機械と対話するための最初の主要なユーザーインターフェースでした。CLIは非常に強力であり、ほぼすべてのことが可能ですが、ユーザーが自分の意図を非常に正確に表現する必要があります。ユーザーは「コンピューターの言語を知る」必要があります。

大規模言語モデル（LLM）の登場、特にコードに関して訓練されたモデルにより、自然言語（NL）を使用してCLIと対話することが可能になりました。実際、これらのモデルは自然言語とコードの両方を十分に理解しており、一方から他方へ変換することができます。

このプロジェクトは、クロスシェルのNL->Codeエクスペリエンスを提供し、ユーザーが自然言語を使って好みのCLIと対話できるようにすることを目的としています。ユーザーはコマンドを入力し（例：「私のIPアドレスは何？」）、`Ctrl + G`を押すと、使用しているシェルに適したコマンドの提案を得られます。このプロジェクトではOpenAIのGPT-4oモデルを使用しており、優れたコード生成能力を持っています。プロンプトエンジニアリングと呼ばれる手法（下記の[セクション](#プロンプトエンジニアリングとコンテキストファイル)参照）を使用して、モデルから適切なコマンドを引き出しています。

**注意：モデルは間違える可能性があります！理解できないコマンドは実行しないでください。コマンドの動作がわからない場合は、`Ctrl + C`を押してキャンセルしてください**。

このプロジェクトは[zsh_codex](https://github.com/tom-doerr/zsh_codex)プロジェクトからの技術的なインスピレーションを得て、複数のシェルに対応できるよう機能を拡張し、モデルに渡すプロンプトをカスタマイズしています（下記のプロンプトエンジニアリングのセクションを参照）。

## 目的声明
このリポジトリは、[Microsoft Build conference 2022](https://mybuild.microsoft.com/)をサポートするための実装例とリファレンスを提供することで、アプリケーションでのCodexの使用理解を深めることを目的としています。これはリリース製品として意図されたものではありません。したがって、このリポジトリではOpenAI APIに関する議論や新機能のリクエストは対象外です。

## 要件
* [Python 3.7.1+](https://www.python.org/downloads/)
    * \[Windows\]: PythonがPATHに追加されていること。
* [OpenAIアカウント](https://openai.com/api/)
    * [OpenAI APIキー](https://platform.openai.com/api-keys)
    * [OpenAI Organization Id](https://platform.openai.com/account/organization) (省略可能。複数の組織がある場合のみ必要です)
    * OpenAIモデル名：最良の結果を得るには`gpt-4o`を使用してください。利用可能なモデルの確認については[こちら](#利用可能なopenaiモデルを確認する方法)を参照してください。
* 完全な機能を使用するには: Windows PowerShell（CoreまたはWindows PowerShell 5.1+）

## 環境変数
APIキーと組織IDは、以下の環境変数を使用して構成する必要があります。

* `OPENAI_API_KEY` - あなたのOpenAI APIキー（必須）
* `OPENAI_ORGANIZATION_ID` - あなたのOpenAI Organization ID（省略可能）
* `OPENAI_MODEL` - 使用するモデル名（省略可能、デフォルトは`gpt-4o`）

環境変数の設定例：

PowerShellでの設定:
```powershell
$env:OPENAI_API_KEY = "your_api_key_here"
$env:OPENAI_ORGANIZATION_ID = "your_org_id_here"  # 省略可能
```

Bash/Zshでの設定:
```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_ORGANIZATION_ID="your_org_id_here"  # 省略可能
```

## インストール

Codex CLIツールを活用するには、お好みのシェル環境を準備する必要があります。各サポートされているシェル環境のインストール手順は以下の通りです。

以下の端末環境がサポートされています：

* [PowerShell](#powershellの手順)（推奨 - 完全サポート）
* [Bash](#bashの手順)（実験的 - 動作未確認）
* [Zsh](#zshの手順)（実験的 - 動作未確認）

Linux/macOSでのPowerShellのインストール方法は[こちら](https://docs.microsoft.com/powershell/scripting/install/installing-powershell)を参照してください。

### 前提条件

Codex CLIを実行するために、Pythonがインストールされていることを確認してください。必要なPythonパッケージをインストールするには、お好みのシェルのコマンドラインで以下のコマンドを入力してください：

```
python -m pip install -r requirements.txt
```

OpenAI APIキー情報を取得するには、(https://platform.openai.com/api-keys) にアクセスしてアカウントにログインしてください。

ログインすると、次の画面が表示されます：
![](images/OpenAI-apikey.png)

_Copy_ ボタンをクリックしてAPIキーをコピーし、環境変数として設定してください。

もし複数のOpenAI組織に所属していて、特定の組織でAPIを使用したい場合は、OpenAI設定ページ(https://platform.openai.com/account/organization)にアクセスし、_Organization ID_見出しの下に表示されているIDをコピーしてください。

参考のため、以下の画像をご覧ください：
![](images/OpenAI-orgid.png)

OpenAIモデル名については、最良の結果を得るために `gpt-4o` を使用してください。[FAQ](#よくある質問)セクションで説明されているように、APIを使用して利用可能なモデルを確認できます。

参考のため、以下の画像をご覧ください：
![](images/OpenAI-engineid.png)

### 設定ファイル

Codex CLIは以下の設定ファイルを使用します：

**~/.openai/codex-cli.json** - 言語設定とモデル情報を含む設定ファイル：
```json
{
  "model": "gpt-4o",
  "language": "ja"  // 言語設定: "en"（英語）または "ja"（日本語）
}
```

`language`設定は、コマンド生成時に使用されるシステムプロンプトの言語を決定します。指定されていない場合、デフォルトで英語が使用されます。

**注意**: APIキーや組織IDは設定ファイルではなく環境変数から取得されます。

### PowerShellの手順

1. このプロジェクトを好きな場所にダウンロードします。例えば、`C:\your\custom\path\`または`~/your/custom/path`。

```PowerShell
git clone https://github.com/microsoft/Codex-CLI.git C:\your\custom\path\
```

2. PowerShellを開き、次のコマンドを実行します。Windowsで実行する場合は、PowerShellを「管理者として」起動してください。

```PowerShell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

実行ポリシーの詳細については、
[about_Execution_Policies](https://docs.microsoft.com/powershell/module/microsoft.powershell.core/about/about_execution_policies)を参照してください。

3. 同じPowerShellターミナルで、`C:\your\custom\path\Codex-CLI\`（クローンしたCodex CLIプロジェクトが含まれるフォルダ）に移動します。以下のコマンドを実行してPowerShell環境をセットアップします：

```PowerShell
.\scripts\powershell_setup.ps1 -OpenAIModelName 'gpt-4o'
```

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;スクリプトパラメータについては[powershell_setup.ps1について](#powershell_setupps1について)セクションを参照してください。

4. 環境変数を設定します：

```PowerShell
$env:OPENAI_API_KEY = "your_api_key_here"
$env:OPENAI_ORGANIZATION_ID = "your_org_id_here"  # 省略可能
```

5. 新しいPowerShellセッションを開き、`#`に続いて自然言語コマンドを入力し、`Ctrl + G`を押します！

#### クリーンアップ
使用が終わったら、`C:\your\custom\path\`（クローンしたCodex CLIプロジェクトが含まれるフォルダ）に移動し、次のコマンドを実行してクリーンアップします。
```
.\scripts\powershell_cleanup.ps1
```

これにより、設定ファイルからAPIキーや組織IDの情報が削除されます。また、環境変数も削除することをお勧めします：

```PowerShell
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_ORGANIZATION_ID -ErrorAction SilentlyContinue
```

実行ポリシーを元に戻す場合は、このコマンドを実行します
```
Set-ExecutionPolicy Undefined -Scope CurrentUser
```

#### PowerShellでのトラブルシューティング

セットアップが正常に完了したにもかかわらず、Codex CLIが動作しない場合は、以下の問題を確認してください：

1. **環境変数が設定されていない**:
   ```PowerShell
   # 環境変数が正しく設定されているか確認
   echo $env:OPENAI_API_KEY
   echo $env:OPENAI_ORGANIZATION_ID
   
   # 設定されていない場合は設定
   $env:OPENAI_API_KEY = "your_api_key_here"
   ```

2. **Ctrl+G キーバインディングの競合**:
   
   VSCode、ブラウザ、または他のアプリケーションがCtrl+Gキーを使用している場合、以下の方法で対処できます：
   
   a. **代替キーバインディングの使用**:
      PowerShellプロファイルを編集して、別のキーバインディングを設定します。
      ```PowerShell
      # $PROFILEファイルを開く
      notepad $PROFILE
      ```
      
      次の行を探します（"### Codex CLI setup - start"と"### Codex CLI setup - end"の間にあります）：
      ```
      Set-PSReadLineKeyHandler -Key Ctrl+g -Function SendToCodex
      ```
      
      これを別のキーバインディング（例：Ctrl+Alt+G）に変更します：
      ```
      Set-PSReadLineKeyHandler -Key Ctrl+Alt+g -Function SendToCodex
      ```
      
   b. **一時的にアプリケーションを終了**:
      Ctrl+Gキーを使用している他のアプリケーションを一時的に閉じてみてください。

3. **Python関連の問題**:
   - Pythonがインストールされて、PATHに設定されていることを確認
   - 必要なパッケージがインストールされていることを確認：
     ```
     python -m pip install -r <リポジトリパス>/requirements.txt
     ```
     
4. **設定ファイルの確認**:
   以下のファイルが存在し、正しく設定されていることを確認します：
   - $PROFILE（PowerShellプロファイル）
   - $HOME/.openai/codex-cli.json（設定ファイル）
   
   設定を確認するには：
   ```PowerShell
   # プロファイルファイルを表示
   Get-Content $PROFILE
   
   # 設定ファイルを表示（存在する場合）
   Get-Content -Path "$HOME/.openai/codex-cli.json" -ErrorAction SilentlyContinue
   ```

5. **手動でコマンドを実行**:
   PowerShellプロファイルに追加された関数を手動で呼び出してみてください：
   ```PowerShell
   Invoke-Codex "ディレクトリの内容をリストアップする"
   ```
   エラーメッセージが表示された場合は、具体的な問題を特定するのに役立ちます。

6. **診断スクリプトの実行**:
   問題が続く場合は、診断スクリプトを実行してください：
   ```powershell
   .\scripts\debug_setup.ps1
   ```

#### powershell_setup.ps1について
`powershell_setup.ps1`は以下のパラメータをサポートしています：
| パラメータ         | 型                                                                         | 説明                                                                                                                                                                     |
| ------------------ | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `-OpenAIModelName` | String                                                                     | オプション。OpenAIモデル名（例：`gpt-4o`）。モデルへのアクセスを提供します。デフォルトは`gpt-4o`です。                                                                   |
| `-Language`        | String                                                                     | オプション。使用する言語を指定します（例：`ja`、`en`）。デフォルトは`ja`（日本語）です。                                                                                 |
| `-RepoRoot`        | [FileInfo](https://docs.microsoft.com/en-us/dotnet/api/system.io.fileinfo) | オプション。デフォルトでは現在のフォルダ。<br>値はCodex CLIフォルダのパスである必要があります。例：<br/>`.\scripts\powershell_setup.ps1 -RepoRoot 'C:\your\custom\path'` |

### Bashの手順（実験的 - 動作未確認）

**注意: BashサポートはWindows Subsystem for Linux (WSL)およびLinux環境での使用を想定していますが、現在は実験的な段階であり、十分にテストされていません。問題が発生する可能性があります。**

WSLおよびLinux環境でBashを使用してCodex CLIを活用するには、以下の手順に従ってください：

1. Bashシェルを開き、次のコマンドを使用してCodex CLIリポジトリをクローンして、Linuxのお好みの場所にCodex CLIプロジェクトをダウンロードします：
    ```
    $ git clone https://github.com/microsoft/Codex-CLI.git /your/custom/path/
    ```

2. プロジェクトをクローンしたら、Codex CLIコードが含まれるディレクトリに移動します。
    ```
    cd </your/custom/path>/Codex-CLI
    ```

3. Bash Codex CLI環境をセットアップします。

    Codex CLIフォルダには、`scripts`という名前のフォルダがあり、その中にBash環境をセットアップするための`bash_setup.sh`スクリプトがあります。

    環境をセットアップするために次のコマンドを実行してください：
    ```
    cd scripts
    source bash_setup.sh -e gpt-4o
    ```
    
    スクリプトはOpenAI設定ファイルを作成し、Bash環境を更新します。

4. 環境変数を設定します：
    ```bash
    export OPENAI_API_KEY="your_api_key_here"
    export OPENAI_ORGANIZATION_ID="your_org_id_here"  # 省略可能
    ```

5. 新しいBashターミナルを開きます。`#`に続いて自然言語でリクエストを入力します。`Ctrl + G`を押して実行します！

#### クリーンアップ

Codex CLIツールの使用が終わったら、Codex CLIコードが含まれるフォルダに移動します。例：`cd ~/your/custom/path/Codex-CLI`。次のコマンドを実行してCodex CLI Bash環境をクリーンアップします。
```
source ./scripts/bash_cleanup.sh
```

環境変数を削除するには：
```bash
unset OPENAI_API_KEY
unset OPENAI_ORGANIZATION_ID
```

終了したら、ターミナルセッションを閉じます。

#### bash_setup.shについて

`bash_setup.sh`は以下のパラメータをサポートしています：

| パラメータ   | 説明                                                     |
| ------------ | -------------------------------------------------------- |
| `-e <value>` | OpenAIモデル名を指定するため（例：`gpt-4o`）（必須）     |
| `-l <value>` | 言語設定（例：`ja`、`en`）。デフォルトは`en`（英語）です |

例：

```
source bash_setup.sh -e gpt-4o -l ja
```

Codex CLI Bashセットアップの実行に関するヘルプについては、次のコマンドを実行してください：
```
source bash_setup.sh -h
```

### Zshの手順（実験的 - 動作未確認）

**注意: Zshサポートは現在実験的な段階であり、十分にテストされていません。問題が発生する可能性があります。**

1. このプロジェクトを `~/your/custom/path/` にダウンロードします。

```
$ git clone https://github.com/microsoft/Codex-CLI.git ~/your/custom/path/
```

2. zshで、`~/your/custom/path/`（Codex CLIコードが含まれるフォルダ）に移動し、次のコマンドを実行してzsh環境をセットアップします：

```
./scripts/zsh_setup.sh -e gpt-4o
```

3. 環境変数を設定します：

```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_ORGANIZATION_ID="your_org_id_here"  # 省略可能
```

4. `zsh`を実行し、入力を開始して`^G`（Ctrl+G）で完了します！

#### クリーンアップ
使用が終わったら、`~/your/custom/path/`（Codex CLIコードが含まれるフォルダ）に移動し、次のコマンドを実行してクリーンアップします。
```
./scripts/zsh_cleanup.sh
```

環境変数を削除するには：
```bash
unset OPENAI_API_KEY
unset OPENAI_ORGANIZATION_ID
```

#### zsh_setup.shについて
`zsh_setup.sh`は以下のパラメータをサポートしています：
| パラメータ   | 説明                                                     |
| ------------ | -------------------------------------------------------- |
| `-e <value>` | OpenAIモデル名を指定するため（例：`gpt-4o`）（必須）     |
| `-l <value>` | 言語設定（例：`ja`、`en`）。デフォルトは`en`（英語）です |

### セキュリティ情報の保存場所

入力したOpenAI APIキーなどの情報は環境変数として保存されます。また、言語設定やモデル情報は各シェル環境に応じて以下の場所に保存されます：

#### PowerShellでの保存先
PowerShellを使用している場合、設定情報は次のファイルに保存されます：
```
$HOME/.openai/codex-cli.json
```
(Windowsでは通常 `C:\Users\ユーザー名\.openai\codex-cli.json`)

#### Bashでの保存先
Bashを使用している場合、設定情報は次のファイルに保存されます：
```
~/.openai/settings.json
```

#### Zshでの保存先 
Zshを使用している場合、設定情報は次のファイルに保存されます：
```
~/.openai/settings.json
```

これらの設定ファイルは、各シェル環境のクリーンアッププロセス（例：`bash_cleanup.sh`、`zsh_cleanup.sh`、`powershell_cleanup.ps1`）を実行すると、適切に削除または初期化されます。セキュリティのために、使用が終わったらクリーンアップスクリプトを実行してAPIキーの環境変数を削除することをお勧めします。

## 最近の更新

プロジェクトは現在、以前のバージョンの機能を統合した統一スクリプト（`codex_query_integrated.py`）を使用しています：

- **ストリーミングレスポンス**: 生成されるコマンドをリアルタイムで確認できます
- **多言語サポート**: 英語と日本語のインターフェースをサポート
- **シェル検出**: シェル環境を自動的に検出（現在はPowerShellに最適化）
- **改善されたUTF-8サポート**: 非ASCII文字の処理が向上
- **環境変数ベースの認証**: APIキーと組織IDは環境変数から取得されるようになりました

## 使用方法

PowerShell用の設定が完了したら、シェルにコメント（`#`で始まる）を書き込み、`Ctrl + G`を押すことでCodex CLIを使用できます。

また、`Invoke-Codex`コマンドを使用して直接CLIを呼び出すこともできます：
```powershell
Invoke-Codex "1GB以上の大きいファイルを検索"
```

Codex CLIは主に2つのモード、シングルターンとマルチターンをサポートしています。

デフォルトでは、マルチターンモードはオフになっています。`# start multi-turn`と`# stop multi-turn`のコマンドを使用してオン/オフを切り替えることができます。

マルチターンモードがオンの場合、Codex CLIはモデルとの過去のやり取りを「記憶」し、以前のアクションやエンティティを参照できるようになります。例えば、Codex CLIでタイムゾーンをマウンテンに変更し、その後「パシフィックに戻して」と言うと、モデルは前回のやり取りから「それ」がユーザーのタイムゾーンであることを認識します：

```powershell
# change my timezone to mountain
tzutil /s "Mountain Standard Time"

# change it back to pacific
tzutil /s "Pacific Standard Time"
```

このツールは`current_context.txt`ファイルを作成し、過去のやり取りを追跡して、各後続コマンドでモデルに渡します。

マルチターンモードがオフの場合、このツールはやり取りの履歴を追跡しません。マルチターンモードには長所短所があります - 文脈解決を可能にする一方で、オーバーヘッドも増加します。例えば、モデルが間違ったスクリプトを生成した場合、ユーザーはそれをコンテキストから削除したいと考えるでしょう。そうしないと、将来の会話ターンでも間違ったスクリプトが生成される可能性が高くなります。マルチターンモードをオフにすると、モデルは完全に決定論的に動作します - 同じコマンドは常に同じ出力を生成します。

モデルが一貫して間違ったコマンドを出力しているように見える場合は、`# stop multi-turn`コマンドを使用してモデルが過去のやり取りを記憶するのを停止し、デフォルトのコンテキストをロードできます。または、`# default context`コマンドは、マルチターンモードをオンに保ちながら同様の効果を持ちます。

## コマンド

| コマンド                          | 説明                                                                                                       |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `start multi-turn`                | マルチターン体験を開始します                                                                               |
| `stop multi-turn`                 | マルチターン体験を停止し、デフォルトコンテキストをロードします                                             |
| `load context <filename>`         | `contexts`フォルダからコンテキストファイルをロードします                                                   |
| `default context`                 | デフォルトのシェルコンテキストをロードします                                                               |
| `view context`                    | テキストエディタでコンテキストファイルを開きます                                                           |
| `save context <filename>`         | コンテキストファイルを`contexts`フォルダに保存します。名前が指定されていない場合は、現在の日時を使用します |
| `show config`                     | モデルとのインタラクションの現在の設定を表示します                                                         |
| `set <config-key> <config-value>` | モデルとのインタラクションの設定を変更します                                                               |

setコマンドを使用してトークン制限、モデル名、温度を変更することで、体験を向上させることができます。例：`# set engine gpt-4o`、`# set temperature 0.5`、`# set max_tokens 50`。

## プロンプトエンジニアリングとコンテキストファイル

このプロジェクトでは、自然言語からコマンドを生成するようGPT-4oを調整するために、「プロンプトエンジニアリング」と呼ばれる手法を使用しています。具体的には、NL->Commandsの一連の例をモデルに渡し、どのようなコードを書くべきかの感覚を与え、また使用しているシェルに適したコマンドを生成するよう促します。これらの例は`contexts`ディレクトリにあります。以下はPowerShellコンテキストの抜粋です：

```powershell
# what's the weather in New York?
(Invoke-WebRequest -uri "wttr.in/NewYork").Content

# make a git ignore with node modules and src in it
"node_modules
src" | Out-File .gitignore

# open it in notepad
notepad .gitignore
```

このプロジェクトでは自然言語コマンドをコメントとしてモデル化し、モデルに期待するPowerShellスクリプトの例を提供しています。これらの例には、一行の補完、複数行の補完、マルチターンの補完（「open it in notepad」の例は前のターンで生成された`.gitignore`ファイルを参照）が含まれています。

ユーザーが新しいコマンド（例えば「what's my IP address」）を入力すると、そのコマンドをコンテキストに（コメントとして）追加し、それに続くコードを生成するようGPT-4oに依頼します。上記の例を見て、GPT-4oはコメントを満たす短いPowerShellスクリプトを書くべきだと理解するでしょう。

## 独自のコンテキストの構築

このプロジェクトには各シェル用のコンテキストと、その他の機能を備えたボーナスコンテキストがプリロードされています。これらに加えて、モデルから他の動作を引き出すための独自のコンテキストを構築できます。例えば、Codex CLIにKubernetesスクリプトを生成させたい場合、コマンドの例とモデルが生成する可能性のある`kubectl`スクリプトを含む新しいコンテキストを作成できます：

```bash
# make a K8s cluster IP called my-cs running on 5678:8080
kubectl create service clusterip my-cs --tcp=5678:8080
```

コンテキストを`contexts`フォルダに追加し、`load context <filename>`を実行してロードします。`src\prompt_file.py`内のデフォルトコンテキストを自分のコンテキストファイルに変更することもできます。

GPT-4oは例がなくても正しいスクリプトを生成することがよくあります。大量のコードで訓練されているため、特定のコマンドの生成方法を知っていることが多いです。ただし、独自のコンテキストを構築することで、求めている特定の種類のスクリプト（長いか短いか、変数を宣言するかどうか、以前のコマンドを参照するかどうかなど）を引き出すのに役立ちます。また、自分のCLIコマンドやスクリプトの例を提供して、GPT-4oが使用を考慮すべき他のツールを示すこともできます。

重要なことは、新しいコンテキストを追加する場合、マルチターンモードをオンにして自動デフォルト設定（エクスペリエンスが壊れることを防ぐために追加された機能）を避けることです。

例として、テキスト読み上げタイプのレスポンスを提供するCognitive Services APIを使用した[cognitive services context](./contexts/CognitiveServiceContext.md)を追加しました。

## トラブルシューティング

### よくある問題
- **Ctrl+Gを押しても応答がない**: クエリが`#`で始まり、その後にスペースがあることを確認してください
- **APIキーがないというエラー**: 環境変数`OPENAI_API_KEY`が正しく設定されているか確認してください
- **日本語テキストが正しく表示されない**: コンソールがUTF-8エンコーディングに設定されていることを確認してください

### デバッグ
`DEBUG_MODE`を使用して、標準入力の代わりにターミナル入力を使用し、コードをデバッグします。これは新しいコマンドを追加する際やツールが応答しない理由を理解する際に役立ちます。

PowerShellユーザーで問題が発生している場合は、診断スクリプトを実行してください：
```powershell
.\scripts\debug_setup.ps1
```

`openai`パッケージがツールでキャッチされないエラーをスローすることがあります。この場合、`codex_query_integrated.py`の最後にその例外用のcatchブロックを追加し、カスタムエラーメッセージを表示できます。

## よくある質問
### 利用可能なOpenAIモデルを確認する方法
OpenAI組織ごとに異なるOpenAIモデルにアクセスできる可能性があります。利用可能なモデルを確認するには、[List models API](https://platform.openai.com/docs/api-reference/models/list)を使用できます。以下のコマンドを参照してください：

* Shell
    ```
    curl https://api.openai.com/v1/models \
      -H 'Authorization: Bearer YOUR_API_KEY' \
      -H 'OpenAI-Organization: YOUR_ORG_ID'
    ```

* PowerShell

    PowerShell v5（Windowsに付属のデフォルトバージョン）
    ```powershell
    (Invoke-WebRequest -Uri https://api.openai.com/v1/models -Headers @{"Authorization" = "Bearer YOUR_API_KEY"; "OpenAI-Organization" = "YOUR_ORG_ID"}).Content
    ```

    PowerShell v7
    ```powershell
    (Invoke-WebRequest -Uri https://api.openai.com/v1/models -Authentication Bearer -Token (ConvertTo-SecureString "YOUR_API_KEY" -AsPlainText -Force) -Headers @{"OpenAI-Organization" = "YOUR_ORG_ID"}).Content
    ```

### Azureでサンプルを実行できますか？
サンプルコードはOpenAI APIのGPT-4oで使用できます。また、Azure経由でGPT-4oにアクセスできる場合は、[Azure OpenAI Service](https://aka.ms/azure-openai)でも使用できます。

## PowerShell環境用スクリプトファイルについて

Codex CLIプロジェクトには、PowerShell環境のセットアップや管理を容易にするための複数のスクリプトファイルが含まれています。

### scripts\powershell_setup.ps1
このスクリプトはCodex CLIをPowerShell環境にセットアップするためのメインスクリプトです。具体的に次の処理を行います：
- PowerShellプロファイル（`$PROFILE`）の作成または更新
- `PSReadLine`モジュールの確認（キーバインディングに必要）
- OpenAIモデル名の設定
- 設定ファイル（`~/.openai/codex-cli.json`）の作成

使用例：
```powershell
# 基本的な使用方法
.\scripts\powershell_setup.ps1 -OpenAIModelName 'gpt-4o'

# カスタムリポジトリパスを指定する場合
.\scripts\powershell_setup.ps1 -RepoRoot 'C:\path\to\repo' -OpenAIModelName 'gpt-4o'
```

### scripts\powershell_cleanup.ps1
このスクリプトはCodex CLIの設定をすべて削除し、PowerShell環境を元の状態に戻します。以下の処理を行います：
- PowerShellプロファイルからCodex CLI関連の設定を削除
- OpenAI API設定ファイルの削除
- `~/.openai/codex-cli.json`ファイルの更新（APIキー情報を削除）

使用例：
```powershell
.\scripts\powershell_cleanup.ps1
```
実行後はPowerShellを再起動して変更を反映させてください。

### scripts\debug_setup.ps1
問題のトラブルシューティングのために使用される診断スクリプトです。Codex CLIが正しく動作しない場合は、このスクリプトを実行して環境設定やパスの問題を特定できます：

```powershell
.\scripts\debug_setup.ps1
```

### scripts\powershell_plugin.ps1
このファイルはPowerShellプロファイルに挿入されるテンプレートであり、以下の機能を提供します：
- `SendToCodex`関数の定義（自然言語クエリをコマンドに変換）
- `Invoke-Codex`エイリアス関数（直接コマンドラインから呼び出し可能）
- Ctrl+Gキーバインディングの設定

このファイルを直接編集する必要はありませんが、キーバインディングをカスタマイズしたい場合などに参考にできます。
