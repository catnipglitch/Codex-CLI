### 
# PowerShell script to clean up the Codex CLI settings for PowerShell
#
# File/Content to be removed:
# 1. PowerShell profile (Remove file if the content only has Codex CLI setup; otherwise, wipe the Codex CLI setup content)
# 2. Settings file (codex-cli.json) - Only model and language settings are kept
###

Write-Host "Codex CLI PowerShellクリーンアップを開始します..." -ForegroundColor Cyan

# 現在のパスを取得
$currentPath = Get-Location

# PowerShellプロファイルからプラグイン呼び出しを削除
if (Test-Path -Path $PROFILE) {
    (Get-Content -Path $PROFILE -Raw) -replace "(?ms)### Codex CLI setup - start.*?### Codex CLI setup - end", "" | Set-Content -Path $PROFILE
    Write-Host "PowerShellプロファイル($PROFILE)からCodex CLI設定を削除しました。" -ForegroundColor Green
}

# 設定ファイルの存在を確認し、必要に応じて更新
$codexCliJsonPath = Join-Path $HOME -ChildPath ".openai\codex-cli.json"
if (Test-Path -Path $codexCliJsonPath) {
    try {
        # 既存の設定ファイルを読み込む
        $configJson = Get-Content -Path $codexCliJsonPath -Raw | ConvertFrom-Json
        
        # 新しい設定オブジェクトを作成（APIキーと組織IDを除外）
        $newConfigJson = @{
            model    = $configJson.model
            language = $configJson.language
        } | ConvertTo-Json
        
        # 更新された設定ファイルを保存
        Set-Content -Path $codexCliJsonPath -Value $newConfigJson -Encoding UTF8
        Write-Host "設定ファイル($codexCliJsonPath)からAPIキー情報を削除しました。" -ForegroundColor Green
    }
    catch {
        Write-Host "設定ファイルの更新中にエラーが発生しました: $_" -ForegroundColor Red
    }
}

# 古い設定ファイルを確認（backward compatibility）
$settingsJsonPath = Join-Path $HOME -ChildPath ".openai\settings.json"
if (Test-Path -Path $settingsJsonPath) {
    Remove-Item -Path $settingsJsonPath -Force
    Write-Host "古い設定ファイル($settingsJsonPath)を削除しました" -ForegroundColor Green
}

Write-Host "`nCodex CLIクリーンアップが完了しました。以下の環境変数も削除することを推奨します:" -ForegroundColor Cyan
Write-Host "  - OPENAI_API_KEY" -ForegroundColor Yellow
Write-Host "  - OPENAI_ORGANIZATION_ID" -ForegroundColor Yellow
Write-Host "  - OPENAI_MODEL" -ForegroundColor Yellow
Write-Host "`n環境変数を削除するPowerShellコマンド例:" -ForegroundColor Cyan
Write-Host '  Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue' -ForegroundColor Cyan
Write-Host '  Remove-Item Env:OPENAI_ORGANIZATION_ID -ErrorAction SilentlyContinue' -ForegroundColor Cyan
Write-Host '  Remove-Item Env:OPENAI_MODEL -ErrorAction SilentlyContinue' -ForegroundColor Cyan
Write-Host "`n変更を完全に反映するには、PowerShellを再起動してください。" -ForegroundColor Cyan