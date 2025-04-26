### Codex CLI setup - start
# TODO: 以下にcodex_query.pyのパスを指定してください
$nl_cli_script = "<path-to-your-codex_query.py>"

# この関数はバッファからの入力を取得しcodex_query.pyに渡します
function global:SendToCodex {
    param (
        [Parameter (Mandatory = $true)] [string] $buffer
    )
    
    if ($nl_cli_script -eq "" -or !(Test-Path($nl_cli_script))) {
        Write-Output "# コードパスが設定されていません。プロファイルを確認してください！"
        return "`nnotepad $profile"
    }

    try {
        Write-Host "# Codex CLI処理中..." -ForegroundColor Cyan
        
        # バッファをUTF-8エンコードでエンコード
        $bufferBytes = [System.Text.Encoding]::UTF8.GetBytes($buffer)
        $encodedBuffer = [System.Text.Encoding]::UTF8.GetString($bufferBytes)
        
        # 直接パイプを使用してPythonスクリプトに渡す
        $output = $encodedBuffer | python $nl_cli_script
        
        if ($null -eq $output -or $output -eq "") {
            # 出力が空の場合、直接実行を試みる
            Write-Host "# パイプ経由での実行に失敗しました。直接実行を試みます..." -ForegroundColor Yellow
            
            # 一時ファイルを使用
            $tempFile = [System.IO.Path]::GetTempFileName()
            [System.IO.File]::WriteAllText($tempFile, $buffer, [System.Text.Encoding]::UTF8)
            
            # 直接実行
            $output = python $nl_cli_script $tempFile
            
            # 一時ファイルを削除
            if (Test-Path $tempFile) {
                Remove-Item $tempFile -Force
            }
        }
        
        if ($null -eq $output -or $output -eq "") {
            Write-Host "# 警告: 出力が空です" -ForegroundColor Yellow
            return "# 警告: 応答が空でした。再試行してください。"
        }
        
        Write-Host "# 出力を受信しました" -ForegroundColor Green
        return $output
    }
    catch {
        Write-Host "# エラー: $($_.Exception.Message)" -ForegroundColor Red
        return "# エラー: $($_.Exception.Message)"
    }
}

# ショートカットキーの設定
if (Get-Module -ListAvailable -Name PSReadLine) {
    Import-Module PSReadLine
    Set-PSReadLineKeyHandler -Key Ctrl+g -ScriptBlock {
        param($key, $arg)
        
        $line = $null
        $cursor = $null
        
        try {
            [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)
            
            # 関数を呼び出す
            $output = SendToCodex($line)
            
            # 結果を挿入
            if ($null -ne $output) {
                foreach ($str in $output) {
                    if ($null -ne $str -and $str -ne "") {
                        [Microsoft.PowerShell.PSConsoleReadLine]::AddLine()
                        [Microsoft.PowerShell.PSConsoleReadLine]::Insert($str)
                    }
                }
            }
        }
        catch {
            [Microsoft.PowerShell.PSConsoleReadLine]::AddLine()
            [Microsoft.PowerShell.PSConsoleReadLine]::Insert("# エラー: $($_.Exception.Message)")
        }
    } -Description "Codex CLI: 自然言語をコマンドに変換"

    Write-Host "Codex CLI: Ctrl+G でコマンドを生成できます" -ForegroundColor Cyan
} 
else {
    Write-Error "PSReadLine モジュールが見つかりません。Codex CLI のキーバインディングは機能しません。"
    Write-Host "代わりに、次のように直接呼び出せます: SendToCodex '# コマンド'" -ForegroundColor Yellow
}
### Codex CLI setup - end