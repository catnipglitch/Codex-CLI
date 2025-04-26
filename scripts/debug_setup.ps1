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
    
    $codexQueryPath = Join-Path $RepoRoot -ChildPath "src\codex_query.py"
    if (Test-Path $codexQueryPath) {
        Write-Host "codex_query.py が存在します。" -ForegroundColor Green
    }
    else {
        Write-Host "codex_query.py が見つかりません。" -ForegroundColor Red
    }
}
catch {
    Write-Host "Python情報の取得に失敗しました: $_" -ForegroundColor Red
}

# 4. OpenAI設定を確認
Write-Host "`n[4] OpenAI 設定" -ForegroundColor Green
$openAIConfigPath = Join-Path $RepoRoot -ChildPath "src\openaiapirc"
if (Test-Path $openAIConfigPath) {
    Write-Host "OpenAI設定ファイルが存在します。" -ForegroundColor Green
    
    # 設定ファイルの内容を安全に表示(APIキーは隠す)
    $content = Get-Content $openAIConfigPath -Raw
    if ($content -match "model=(.*)") {
        Write-Host "モデル: $($matches[1])"
    }
    Write-Host "（セキュリティのため、APIキーは表示されません）"
}
else {
    Write-Host "OpenAI設定ファイルが見つかりません。" -ForegroundColor Red
}

# 5. 手動テストの方法
Write-Host "`n[5] 手動テスト方法" -ForegroundColor Green
Write-Host "以下のコマンドで直接Pythonスクリプトを実行してみてください:" -ForegroundColor Yellow
Write-Host "  python $codexQueryPath `"現在の時刻を表示して`""

Write-Host "`n問題が解決しない場合は、以下の対処法を試してください:" -ForegroundColor Cyan
Write-Host "1. セットアップスクリプトを再実行: .\scripts\powershell_setup.ps1 -OpenAIModelName 'gpt-4o'"
Write-Host "2. PowerShellを再起動してください"
Write-Host "3. 新しいPowerShellウィンドウで '#' の後に何か入力してCtrl+Gを押してください"
Write-Host "4. '#' と入力内容の間に必ずスペースを入れてください"
Write-Host "   正しい例: '# 現在時刻は？'"
Write-Host "   誤った例: '#現在時刻は？'"
Write-Host "5. デバッグログを確認: $(Join-Path $RepoRoot -ChildPath 'codex_debug.log')`n"
