#
# Codex CLI 修正スクリプト
#

param(
    [Parameter()]
    [string]$RepoRoot = (Get-Location),

    [Parameter(Mandatory = $false)]
    [string]$OpenAIModelName = "gpt-4o"
)

$ErrorActionPreference = "Continue"

Write-Host "Codex CLI 修正プロセスを開始します..." -ForegroundColor Cyan

# 1. OpenAIライブラリを最新版に更新
Write-Host "`n[1] OpenAIライブラリの更新" -ForegroundColor Green
try {
    python -m pip install --upgrade openai
    Write-Host "OpenAIライブラリを最新版に更新しました" -ForegroundColor Green
}
catch {
    Write-Host "OpenAIライブラリの更新に失敗しました: $_" -ForegroundColor Red
    exit 1
}

# 2. 修正版スクリプトを適用
Write-Host "`n[2] 修正版スクリプトの適用" -ForegroundColor Green
$fixedScriptPath = Join-Path $RepoRoot -ChildPath "src\codex_query_fixed.py"
$originalScriptPath = Join-Path $RepoRoot -ChildPath "src\codex_query.py"

if (Test-Path $fixedScriptPath) {
    # オリジナルファイルをバックアップ
    $backupPath = "$originalScriptPath.bak"
    if (Test-Path $originalScriptPath) {
        Copy-Item $originalScriptPath $backupPath -Force
        Write-Host "元のスクリプトをバックアップしました: $backupPath" -ForegroundColor Green
    }
    
    # 修正版を適用
    Copy-Item $fixedScriptPath $originalScriptPath -Force
    Write-Host "修正版スクリプトを適用しました" -ForegroundColor Green
}
else {
    Write-Host "修正版スクリプトが見つかりません。セットアップを続行します。" -ForegroundColor Yellow
}

# 3. PowerShellセットアップを再実行
Write-Host "`n[3] PowerShellセットアップの再実行" -ForegroundColor Green

$setupScript = Join-Path $RepoRoot -ChildPath "scripts\powershell_setup.ps1"
if (Test-Path $setupScript) {
    try {
        # PowerShellセットアップスクリプトを実行
        Write-Host "PowerShellプロファイルを設定中..."
        
        # API Keyの入力を促す
        Write-Host "OpenAI APIキーを入力してください:" -ForegroundColor Yellow
        $apiKey = Read-Host -AsSecureString
        
        # 組織IDの入力（オプショナル）
        Write-Host "OpenAI Organization ID（省略可能）を入力してください:" -ForegroundColor Yellow
        $orgId = Read-Host
        
        if ([string]::IsNullOrWhiteSpace($orgId)) {
            # 組織IDなしでセットアップ
            & $setupScript -OpenAIApiKey $apiKey -OpenAIModelName $OpenAIModelName -RepoRoot $RepoRoot
        }
        else {
            # 組織IDありでセットアップ
            & $setupScript -OpenAIApiKey $apiKey -OpenAIOrganizationId $orgId -OpenAIModelName $OpenAIModelName -RepoRoot $RepoRoot
        }
        
        Write-Host "PowerShellセットアップが完了しました" -ForegroundColor Green
    }
    catch {
        Write-Host "PowerShellセットアップに失敗しました: $_" -ForegroundColor Red
    }
}
else {
    Write-Host "PowerShellセットアップスクリプトが見つかりません" -ForegroundColor Red
    exit 1
}

Write-Host "`n修正プロセスが完了しました。以下の手順に従ってください:" -ForegroundColor Cyan
Write-Host "1. 新しいPowerShellウィンドウを開いてください"
Write-Host "2. 次のように入力してテストしてください: '# 現在の時刻を表示'"
Write-Host "3. Ctrl+Gを押して実行してください" 
Write-Host "4. それでも動作しない場合は、デバッグログを確認してください: $LOG_FILE"
