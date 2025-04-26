# 設定ファイル修正スクリプト
$codexCliPath = Join-Path $HOME -ChildPath ".openai\codex-cli.json"

if (Test-Path $codexCliPath) {
    # 既存のファイルを読み込む
    $configContent = Get-Content $codexCliPath -Raw | ConvertFrom-Json

    # 既存のプロパティを維持しながら必要な設定を追加
    $updatedConfig = @{
        "api_key"      = $configContent.api_key
        "organization" = $configContent.organization
        "model"        = "gpt-4o" # モデルを明示的に設定
        "language"     = "ja"   # 日本語に設定
    }

    # 更新した設定を保存
    $updatedConfigJson = $updatedConfig | ConvertTo-Json
    Set-Content -Path $codexCliPath -Value $updatedConfigJson -Encoding UTF8
    
    Write-Host "設定ファイルを更新しました: $codexCliPath" -ForegroundColor Green
}
else {
    # ファイルが存在しない場合は新規作成
    $config = @{
        "api_key"      = "" # APIキーは環境変数から読み取られます
        "organization" = ""
        "model"        = "gpt-4o"
        "language"     = "ja"
    }

    # OpenAIディレクトリを作成
    $openaiDir = Join-Path $HOME -ChildPath ".openai"
    if (!(Test-Path $openaiDir)) {
        New-Item -Type Directory -Path $openaiDir -Force | Out-Null
    }

    # 設定ファイルを作成
    $config | ConvertTo-Json | Set-Content -Path $codexCliPath -Encoding UTF8
    
    Write-Host "新しい設定ファイルを作成しました: $codexCliPath" -ForegroundColor Green
}

# PowerShellプロファイルを更新する手順を表示
Write-Host "" -ForegroundColor Yellow
Write-Host "===== PowerShellプロファイル更新手順 =====" -ForegroundColor Yellow
Write-Host "以下のコマンドを実行して、PowerShellプロファイルを更新してください:" -ForegroundColor Yellow
Write-Host "1. PowerShellを管理者として起動" -ForegroundColor Cyan
Write-Host "2. 次のコマンドを実行:" -ForegroundColor Cyan
Write-Host "   Copy-Item -Path '<path-to-your-Codex-CLI>/fixed_profile.ps1' -Destination `$PROFILE -Force" -ForegroundColor White

# 動作確認方法
Write-Host "" -ForegroundColor Yellow
Write-Host "===== 動作確認方法 =====" -ForegroundColor Yellow
Write-Host "1. PowerShellを再起動" -ForegroundColor Cyan
Write-Host "2. 次のコマンドで直接関数を呼び出してテスト:" -ForegroundColor Cyan
Write-Host "   SendToCodex '# 自分のIPアドレスを表示して'" -ForegroundColor White
Write-Host "3. 正常に動作したら、通常入力で確認" -ForegroundColor Cyan
Write-Host "   (入力例: # 自分のIPアドレスを表示して → Ctrl+G)" -ForegroundColor White