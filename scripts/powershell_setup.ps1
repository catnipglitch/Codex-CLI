# PowerShell Setup for Codex CLI
#
# このファイルはPowerShellプロファイルの準備を行い、
# Codex CLIのショートカットキーをセットアップします。

# スクリプトのパスを取得
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootPath = Split-Path -Parent $scriptPath
$nl_cli_script_path = Join-Path $rootPath "src\codex_query_fixed.py"

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

Write-Host "`nセットアップが完了しました。" -ForegroundColor Cyan
Write-Host "Ctrl+G キーを押すと、自然言語をコマンドに変換できます。" -ForegroundColor Cyan
Write-Host "または、Invoke-Codex 'クエリ' でも直接実行できます。" -ForegroundColor Cyan
Write-Host "`n新しいPowerShellセッションを開始するか、以下のコマンドを実行してください: . $PROFILE" -ForegroundColor Yellow
