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

# 設定ファイルがあるかどうかに関わらず、言語設定のみの設定ファイルを作成/更新
$configJson = @{
    model    = $OpenAIModelName
    language = "ja"  # デフォルト言語
} | ConvertTo-Json

Set-Content -Path $codexConfigPath -Value $configJson -Encoding UTF8
Write-Host "言語設定ファイルを更新しました: $codexConfigPath" -ForegroundColor Green

Write-Host "`n環境変数の設定が必要です:" -ForegroundColor Yellow
Write-Host "APIキーと組織IDは環境変数から取得されるようになりました。以下の環境変数を設定してください:" -ForegroundColor Yellow
Write-Host "  - OPENAI_API_KEY: OpenAI APIキー (必須)" -ForegroundColor Yellow
Write-Host "  - OPENAI_ORGANIZATION_ID: OpenAI 組織ID (省略可能)" -ForegroundColor Yellow
Write-Host "  - OPENAI_MODEL: OpenAIモデル名 (省略可能、デフォルト: $OpenAIModelName)" -ForegroundColor Yellow
Write-Host "`nPowerShellでの環境変数設定例:" -ForegroundColor Cyan
Write-Host '  $env:OPENAI_API_KEY="your_api_key_here"' -ForegroundColor Cyan
Write-Host '  $env:OPENAI_ORGANIZATION_ID="your_org_id_here"  # 省略可能' -ForegroundColor Cyan

Write-Host "`nセットアップが完了しました。" -ForegroundColor Cyan
Write-Host "Ctrl+G キーを押すと、自然言語をコマンドに変換できます。" -ForegroundColor Cyan
Write-Host "または、Invoke-Codex 'クエリ' でも直接実行できます。" -ForegroundColor Cyan
Write-Host "`n新しいPowerShellセッションを開始するか、以下のコマンドを実行してください: . $PROFILE" -ForegroundColor Yellow
