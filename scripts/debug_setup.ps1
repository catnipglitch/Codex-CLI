#
# Codex CLI デバッグスクリプト
#

param(
    [Parameter()]
    [string]$RepoRoot = (Get-Location)
)

$ErrorActionPreference = "Continue"

Write-Host "Codex CLI デバッグ診断を実行中..." -ForegroundColor Cyan

# 1. PowerShell情報を確認
Write-Host "`n[1] PowerShell情報" -ForegroundColor Green
Write-Host "PowerShell バージョン: $($PSVersionTable.PSVersion)"
Write-Host "PowerShell エディション: $($PSVersionTable.PSEdition)"
Write-Host "プロファイルパス: $PROFILE"

# 2. プロファイルの内容を確認
Write-Host "`n[2] PowerShellプロファイル内容" -ForegroundColor Green
if (Test-Path $PROFILE) {
    Write-Host "プロファイルが存在します。"
    $profileContent = Get-Content $PROFILE -Raw
    if ($profileContent -match "### Codex CLI setup - start(.*?)### Codex CLI setup - end") {
        Write-Host "Codex CLI設定がプロファイルに見つかりました。" -ForegroundColor Green
    }
    else {
        Write-Host "Codex CLI設定がプロファイルに見つかりません。" -ForegroundColor Red
        Write-Host "セットアップを再実行する必要があります:" 
        Write-Host "  .\scripts\powershell_setup.ps1 -OpenAIModelName 'gpt-4o'" -ForegroundColor Yellow
    }
}
else {
    Write-Host "プロファイルが見つかりません。" -ForegroundColor Red
}

# 3. Pythonの設定を確認
Write-Host "`n[3] Python 設定" -ForegroundColor Green
try {
    $pythonInfo = python --version
    Write-Host "Python: $pythonInfo"
    
    $pipInfo = python -m pip --version
    Write-Host "Pip: $pipInfo"
    
    $codexQueryPath = Join-Path $RepoRoot -ChildPath "src\codex_query_integrated.py"
    if (Test-Path $codexQueryPath) {
        Write-Host "codex_query_integrated.py が存在します。" -ForegroundColor Green
    }
    else {
        Write-Host "codex_query_integrated.py が見つかりません。" -ForegroundColor Red
    }
}
catch {
    Write-Host "Python情報の取得に失敗しました: $_" -ForegroundColor Red
}

# 4. 環境変数設定を確認
Write-Host "`n[4] 環境変数設定の確認" -ForegroundColor Green
$apiKey = $env:OPENAI_API_KEY
$orgId = $env:OPENAI_ORGANIZATION_ID
$modelName = $env:OPENAI_MODEL

if ($apiKey) {
    Write-Host "OPENAI_API_KEY: 設定されています" -ForegroundColor Green
    Write-Host "  長さ: " -NoNewline
    Write-Host "$($apiKey.Length) 文字" -ForegroundColor Green
}
else {
    Write-Host "OPENAI_API_KEY: 設定されていません" -ForegroundColor Red
    Write-Host "  以下のコマンドで設定してください:" -ForegroundColor Yellow
    Write-Host "  `$env:OPENAI_API_KEY=`"your_api_key_here`"" -ForegroundColor Yellow
}

if ($orgId) {
    Write-Host "OPENAI_ORGANIZATION_ID: 設定されています" -ForegroundColor Green
}
else {
    Write-Host "OPENAI_ORGANIZATION_ID: 設定されていません (省略可能)" -ForegroundColor Yellow
}

if ($modelName) {
    Write-Host "OPENAI_MODEL: $modelName" -ForegroundColor Green
}
else {
    Write-Host "OPENAI_MODEL: デフォルト設定 (gpt-4o) を使用します" -ForegroundColor Yellow
}

# 5. 設定ファイルの確認
Write-Host "`n[5] 設定ファイル" -ForegroundColor Green
$configJsonPath = Join-Path $HOME -ChildPath ".openai\codex-cli.json"
if (Test-Path $configJsonPath) {
    Write-Host "設定ファイルが存在します。" -ForegroundColor Green
    
    # 設定ファイルの内容を安全に表示
    try {
        $config = Get-Content $configJsonPath -Raw | ConvertFrom-Json
        if ($config.model) {
            Write-Host "モデル: $($config.model)" -ForegroundColor Green
        }
        if ($config.language) {
            Write-Host "言語: $($config.language)" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "設定ファイルの読み取りに失敗しました: $_" -ForegroundColor Red
    }
}
else {
    Write-Host "設定ファイルが見つかりません。" -ForegroundColor Red
}

# 6. 手動テストの方法
Write-Host "`n[6] 手動テスト方法" -ForegroundColor Green
Write-Host "以下のコマンドで直接Pythonスクリプトを実行してみてください:" -ForegroundColor Yellow
Write-Host "  python $codexQueryPath `"現在の時刻を表示して`""

Write-Host "`n問題が解決しない場合は、以下の対処法を試してください:" -ForegroundColor Cyan
Write-Host "1. セットアップスクリプトを再実行: .\scripts\powershell_setup.ps1 -OpenAIModelName 'gpt-4o'"
Write-Host "2. 環境変数を確認: `$env:OPENAI_API_KEY が設定されていることを確認"
Write-Host "3. PowerShellを再起動してください"
Write-Host "4. 新しいPowerShellウィンドウで '#' の後に何か入力してCtrl+Gを押してください"
Write-Host "5. '#' と入力内容の間に必ずスペースを入れてください"
Write-Host "   正しい例: '# 現在時刻は？'"
Write-Host "   誤った例: '#現在時刻は？'"
Write-Host "6. デバッグログを確認: $(Join-Path $RepoRoot -ChildPath 'codex_debug.log')`n"
