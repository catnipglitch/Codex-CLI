# PowerShell Setup for Codex CLI
#
# このファイルはPowerShellプロファイルの準備を行い、
# Codex CLIのショートカットキーをセットアップします。

param(
    [Parameter(Mandatory = $false)]
    [string]$RepoRoot = (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)),

    [Parameter(Mandatory = $false)]
    [string]$OpenAIModelName = "gpt-4o"
)

# スクリプトのパスを取得
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootPath = Split-Path -Parent $scriptPath
# 統合版スクリプトへのパスを使用
$nl_cli_script_path = Join-Path $rootPath "src\codex_query_integrated.py"

Write-Host "Codex CLI セットアップを開始します..." -ForegroundColor Cyan
Write-Host "使用するモデル: $OpenAIModelName" -ForegroundColor Green

# プロファイルパスの取得
$profileExists = Test-Path $PROFILE
if (-not $profileExists) {
    # プロファイルが存在しない場合は作成
    New-Item -Type File -Path $PROFILE -Force
    Write-Host "PowerShellプロファイルが存在しなかったため、作成しました: $PROFILE" -ForegroundColor Green
}

# プロファイル内容を取得
$profileContent = Get-Content $PROFILE -Raw

# プラグインファイルへのパス
$pluginPath = Join-Path $scriptPath "powershell_plugin.ps1"
$pluginPathWindows = $pluginPath.Replace("\", "\\")

# テンプレートプラグインの内容を取得
$pluginTemplateContent = Get-Content $pluginPath -Raw

# プラグイン内のパス置換
$pluginContent = $pluginTemplateContent.Replace("{{codex_query_path}}", $nl_cli_script_path.Replace("\", "\\"))

# プラグインの有効/無効フラグを調べる
$codexPluginMarkerStart = "### Codex CLI setup - start"
$codexPluginMarkerEnd = "### Codex CLI setup - end"
$hasCodexPlugin = $profileContent -match [regex]::Escape($codexPluginMarkerStart)

# バックアップ作成
$backupPath = $PROFILE + ".codex_backup"
if (-not (Test-Path $backupPath)) {
    Copy-Item $PROFILE $backupPath
    Write-Host "PowerShellプロファイルのバックアップを作成しました: $backupPath" -ForegroundColor Green
}

if ($hasCodexPlugin) {
    # 既存のプラグイン部分を更新
    $pattern = "(?s)" + [regex]::Escape($codexPluginMarkerStart) + ".*?" + [regex]::Escape($codexPluginMarkerEnd)
    $profileContent = [regex]::Replace($profileContent, $pattern, $pluginContent)
    Set-Content -Path $PROFILE -Value $profileContent
    Write-Host "既存のCodex CLIプラグインを更新しました。" -ForegroundColor Green
}
else {
    # プラグイン部分がない場合は追加
    Add-Content -Path $PROFILE -Value "`n$pluginContent"
    Write-Host "PowerShellプロファイルにCodex CLIプラグインを追加しました。" -ForegroundColor Green
}

# PSReadLineモジュールの確認
if (-not (Get-Module -ListAvailable -Name PSReadLine)) {
    Write-Warning "PSReadLineモジュールが見つかりません。インストールを推奨します。"
    Write-Host "インストールするには以下のコマンドを実行してください: Install-Module -Name PSReadLine -AllowPrerelease -Force" -ForegroundColor Yellow
}

# 設定ファイルの作成や確認
$codexConfigDir = Join-Path $HOME ".openai"
$codexConfigPath = Join-Path $codexConfigDir "codex-cli.json"

if (-not (Test-Path $codexConfigDir)) {
    New-Item -ItemType Directory -Path $codexConfigDir -Force | Out-Null
    Write-Host "設定ディレクトリを作成しました: $codexConfigDir" -ForegroundColor Green
}

if (-not (Test-Path $codexConfigPath)) {
    # OpenAI APIキーの入力を促す
    $apiKey = ""
    While ([string]::IsNullOrWhiteSpace($apiKey)) {
        $apiKey = Read-Host "OpenAI APIキーを入力してください (https://platform.openai.com/api-keys より取得)"
    }
    
    # 組織IDは任意
    $orgId = Read-Host "OpenAI Organization IDを入力してください (省略可能)"
    
    # 設定ファイル作成
    $configJson = @{
        api_key      = $apiKey
        organization = $orgId
        model        = $OpenAIModelName
        language     = "ja"  # デフォルト言語
    } | ConvertTo-Json

    Set-Content -Path $codexConfigPath -Value $configJson -Encoding UTF8
    Write-Host "設定ファイルを作成しました: $codexConfigPath" -ForegroundColor Green
}
else {
    Write-Host "既存の設定ファイルを使用します: $codexConfigPath" -ForegroundColor Green
    # 既存ファイルのモデルを更新
    try {
        $configJson = Get-Content -Path $codexConfigPath -Raw | ConvertFrom-Json
        if ($configJson.model -ne $OpenAIModelName) {
            $configJson.model = $OpenAIModelName
            $configJson | ConvertTo-Json | Set-Content -Path $codexConfigPath -Encoding UTF8
            Write-Host "設定ファイルのモデルを更新しました: $OpenAIModelName" -ForegroundColor Green
        }
    }
    catch {
        Write-Warning "設定ファイルの更新中にエラーが発生しました: $_"
    }
}

Write-Host "`nセットアップが完了しました。" -ForegroundColor Cyan
Write-Host "Ctrl+G キーを押すと、自然言語をコマンドに変換できます。" -ForegroundColor Cyan
Write-Host "または、Invoke-Codex 'クエリ' でも直接実行できます。" -ForegroundColor Cyan
Write-Host "`n新しいPowerShellセッションを開始するか、以下のコマンドを実行してください: . $PROFILE" -ForegroundColor Yellow
