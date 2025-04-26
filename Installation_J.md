# Codex CLIのインストール

Codex CLIツールを活用するには、お好みのシェル環境を準備する必要があります。各サポートされているシェル環境のインストール手順は以下の通りです。

以下の端末環境がサポートされています：

* [Powershell](#powershellの手順)
* [Bash](#bashの手順)
* [Zsh](#zshの手順) (または [Bash 5.1](#bashの手順))

Linux/MacOSでのPowerShellのインストール方法は[こちら](https://docs.microsoft.com/powershell/scripting/install/installing-powershell)を参照してください。

## 前提条件

Codex CLIを実行するために、Pythonがインストールされていることを確認してください。必要なPythonパッケージをインストールするには、お好みのシェルのコマンドラインで以下のコマンドを入力してください：

```
python -m pip install -r requirements.txt
```

さらに、Codex CLIツールを実行するには、OpenAI APIキーとモデル名が必要です。Organization IDは省略可能です（複数の組織に所属している場合のみ必要）。

OpenAI APIキー情報を取得するには、(https://platform.openai.com/api-keys) にアクセスしてアカウントにログインしてください。

ログインすると、次の画面が表示されます：
![](images/OpenAI-apikey.png)

_Copy_ ボタンをクリックしてAPIキーをコピーし、後で取り出せる場所に保存してください。

もし複数のOpenAI組織に所属していて、特定の組織でAPIを使用したい場合は、OpenAI設定ページ(https://platform.openai.com/account/organization)にアクセスし、_Organization ID_見出しの下に表示されているIDをコピーしてください。前のステップで保存したAPIキーと一緒にコピーしたIDを保存してください。

参考のため、以下の画像をご覧ください：
![](images/OpenAI-orgid.png)

OpenAIモデル名については、最良の結果を得るために `gpt-4o` を使用してください。FAQセクションで説明されているように、APIを使用して利用可能なモデルを確認できます。

参考のため、以下の画像をご覧ください：
![](images/OpenAI-engineid.png)

## Bashの手順

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

	環境をセットアップするために次のコマンドを実行してください。スクリプトは組織ID、APIキー、エンジンIDの入力を求めます：
	```
	cd scripts
	source bash_setup.sh
	```
	
	スクリプトはOpenAI設定ファイルを作成し、Bash環境を更新します。

4. 新しいBashターミナルを開きます。`#`に続いて自然言語でリクエストを入力します。`Ctrl + G`を押して実行します！

### クリーンアップ

Codex CLIツールの使用が終わったら、Codex CLIコードが含まれるフォルダに移動します。例：`cd ~/your/custom/path/Codex-CLI`。次のコマンドを実行してCodex CLI Bash環境をクリーンアップします。
```
source ./scripts/bash_cleanup.sh
```
終了したら、ターミナルセッションを閉じます。

### bash_setup.shについて

デフォルトでは、`bash_setup.sh`は必要な設定の入力を求めます。コマンドラインから以下のパラメータを使用して、これらの値を渡すこともできます：

| パラメータ   | 説明                                                                                                                                 |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| `-o <value>` | [OpenAI Organization Id](https://beta.openai.com/account/org-settings)を渡すため（オプション：複数の組織に所属している場合のみ必要） |
| `-k <value>` | [OpenAI APIキー](https://beta.openai.com/account/api-keys)を渡すため（必須）                                                         |
| `-e <value>` | OpenAIモデル名を指定するため（例：`gpt-4o`）（必須）                                                                                 |

例：

```
source bash_setup.sh -o myorgid -k myapikey -e someengineid
```

Codex CLI Bashセットアップの実行に関するヘルプについては、次のコマンドを実行してください：
```
source bash_setup.sh -h
```

![](images/Codex-CLI-bashhelp.png)

## Zshの手順

1. このプロジェクトを `~/your/custom/path/` にダウンロードします。

```
$ git clone https://github.com/microsoft/Codex-CLI.git ~/your/custom/path/
```

2. zshで、`~/your/custom/path/`（Codex CLIコードが含まれるフォルダ）に移動し、次のコマンドを実行してzsh環境をセットアップします。スクリプトは組織ID、APIキー、エンジンIDの入力を求めます：

```
./scripts/zsh_setup.sh
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;スクリプトパラメータについては[zsh_setup.shについて](#zshsetupshについて)セクションを参照してください。

3. `zsh`を実行し、入力を開始して`^G`で完了します！

### クリーンアップ
使用が終わったら、`~/your/custom/path/`（Codex CLIコードが含まれるフォルダ）に移動し、次のコマンドを実行してクリーンアップします。
```
./scripts/zsh_cleanup.sh
```

### zsh_setup.shについて
`zsh_setup.sh`は以下のパラメータをサポートしています：
| パラメータ   | 説明                                                                                                                                 |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| `-o <value>` | [OpenAI Organization Id](https://beta.openai.com/account/org-settings)を渡すため（オプション：複数の組織に所属している場合のみ必要） |
| `-k <value>` | [OpenAI APIキー](https://beta.openai.com/account/api-keys)を渡すため（必須）                                                         |
| `-e <value>` | OpenAIモデル名を指定するため（例：`gpt-4o`）（必須）                                                                                 |


## PowerShellの手順

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


3. 同じPowerShellターミナルで、`C:\your\custom\path\Codex-CLI\`（クローンしたCodex CLIプロジェクトが含まれるフォルダ）に移動します。次のコマンドをコピーし、`YOUR_OPENAI_ORGANIZATION_ID`（省略可能）と`MODEL_NAME`をOpenAI組織IDとOpenAIモデル名に置き換えます。コマンドを実行してPowerShell環境をセットアップします。OpenAIアクセスキーの入力を求められます。

```PowerShell
.\scripts\powershell_setup.ps1 -OpenAIOrganizationId 'YOUR_OPENAI_ORGANIZATION_ID' -OpenAIModelName 'gpt-4o'
```

または、組織IDが不要な場合は、次のように簡略化したコマンドも使用できます：

```PowerShell
.\scripts\powershell_setup.ps1 -OpenAIModelName 'gpt-4o'
```

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;スクリプトパラメータについては[powershell_setup.ps1について](#powershell_setupps1について)セクションを参照してください。

4. 新しいPowerShellセッションを開き、`#`に続いて自然言語コマンドを入力し、`Ctrl + G`を押します！

### クリーンアップ
使用が終わったら、`C:\your\custom\path\`（クローンしたCodex CLIプロジェクトが含まれるフォルダ）に移動し、次のコマンドを実行してクリーンアップします。
```
.\scripts\powershell_cleanup.ps1
```

実行ポリシーを元に戻す場合は、このコマンドを実行します
```
Set-ExecutionPolicy Undefined -Scope CurrentUser
```

### PowerShellでのトラブルシューティング

セットアップが正常に完了したにもかかわらず、Codex CLIが動作しない場合は、以下の問題を確認してください：

1. **Ctrl+G キーバインディングの競合**:
   
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

2. **Python関連の問題**:
   - Pythonがインストールされ、PATHに設定されていることを確認
   - 必要なパッケージがインストールされていることを確認：
     ```
     python -m pip install -r <リポジトリパス>/requirements.txt
     ```
     
3. **設定ファイルの確認**:
   以下のファイルが存在し、正しく設定されていることを確認します：
   - $PROFILE（PowerShellプロファイル）
   - $HOME/.openai/settings.json（OpenAI設定ファイル）
   
   設定を確認するには：
   ```PowerShell
   # プロファイルファイルを表示
   Get-Content $PROFILE
   
   # 設定ファイルを表示（存在する場合）
   Get-Content -Path "$HOME/.openai/settings.json" -ErrorAction SilentlyContinue
   ```

4. **手動でコマンドを実行**:
   PowerShellプロファイルに追加された関数を手動で呼び出してみてください：
   ```PowerShell
   SendToCodex "ディレクトリの内容をリストアップする"
   ```
   エラーメッセージが表示された場合は、具体的な問題を特定するのに役立ちます。

### powershell_setup.ps1について
`powershell_setup.ps1`は以下のパラメータをサポートしています：
| パラメータ              | 型                                                                                       | 説明                                                                                                                                                                                                                                                                                                                                                |
| ----------------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-OpenAIApiKey`         | [SecureString](https://docs.microsoft.com/en-us/dotnet/api/system.security.securestring) | 必須。提供されない場合、スクリプトは値の入力を求めます。この値は[https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)で確認できます。PowerShellパラメータを通じて値を提供するには、PowerShell 7の例：<br/> `.\scripts\powershell_setup.ps1 -OpenAIApiKey (ConvertTo-SecureString "YOUR_OPENAI_API_KEY" -AsPlainText -Force)` |
| `-OpenAIOrganizationId` | String                                                                                   | オプション。複数の組織に所属している場合のみ必要。あなたの[OpenAI organization Id](https://platform.openai.com/account/organization)。                                                                                                                                                                                                              |
| `-OpenAIModelName`      | String                                                                                   | 必須。OpenAIモデル名（例：`gpt-4o`）。モデルへのアクセスを提供します。                                                                                                                                                                                                                                                                              |
| `-Language`             | String                                                                                   | オプション。使用する言語を指定します（例：`ja`、`en`）。デフォルトは`en`（英語）です。日本語のメッセージを表示するには`ja`を指定してください。                                                                                                                                                                                                      |
| `-RepoRoot`             | [FileInfo](https://docs.microsoft.com/en-us/dotnet/api/system.io.fileinfo)               | オプション。デフォルトでは現在のフォルダ。<br>値はCodex CLIフォルダのパスである必要があります。例：<br/>`.\scripts\powershell_setup.ps1 -RepoRoot 'C:\your\custom\path'`                                                                                                                                                                            |

## セキュリティ情報の保存場所

入力したOpenAI APIキーなどの情報は、各シェル環境に応じて以下の場所に保存されます：

### Bashでの保存先
Bashを使用している場合、APIキーと関連情報は次のファイルに保存されます：
```
~/.openai/settings.json
```

### Zshでの保存先 
Zshを使用している場合、APIキーと関連情報は次のファイルに保存されます：
```
~/.openai/settings.json
```

### PowerShellでの保存先
PowerShellを使用している場合、APIキーと関連情報は次のファイルに保存されます：
```
$HOME/.openai/settings.json
```
(Windowsでは通常 `C:\Users\ユーザー名\.openai\settings.json`)

これらの設定ファイルは、各シェル環境のクリーンアッププロセス（例：`bash_cleanup.sh`、`zsh_cleanup.sh`、`powershell_cleanup.ps1`）を実行すると、適切に削除または初期化されます。セキュリティのために、使用が終わったらクリーンアップスクリプトを実行することをお勧めします。
