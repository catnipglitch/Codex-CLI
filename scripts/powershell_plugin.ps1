### Codex CLI setup - start
# コンソールエンコーディングをUTF-8に設定
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$nl_cli_script = "{{codex_query_path}}"

# この関数はバッファからの入力を取得しcodex_query_integrated.pyに渡します
function global:SendToCodex {
    param (
        [Parameter(Mandatory = $true)] [string] $buffer
    )
    
    if ($nl_cli_script -eq "" -or !(Test-Path($nl_cli_script))) {
        Write-Output "# コードパスが設定されていません。プロファイルを確認してください！"
        return "`nnotepad $profile"
    }

    try {
        Write-Host "# Codex CLI処理中..." -ForegroundColor Cyan
        
        # 一時ファイルを使用する方法に変更（パイプ処理の問題を回避）
        $tempFile = [System.IO.Path]::GetTempFileName()
        
        # バッファの内容をUTF-8エンコードで一時ファイルに書き込み
        [System.IO.File]::WriteAllText($tempFile, $buffer, [System.Text.Encoding]::UTF8)
        
        # 直接--fileオプションでPythonスクリプトに渡す
        $output = & python -u $nl_cli_script "--file" "$tempFile" 2>&1
        
        # 一時ファイルを削除
        if (Test-Path $tempFile) {
            Remove-Item $tempFile -Force
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

# 新しい Invoke-Codex 関数 - コマンドラインからの直接呼び出し用
function global:Invoke-Codex {
    [CmdletBinding()]
    param(
        [Parameter(ValueFromPipeline = $true, Position = 0)]
        [string]$Query
    )

    begin {
        # Codexスクリプトのパスを取得
        $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
        $scriptRoot = Split-Path -Parent $scriptPath
        $codexPath = Join-Path $scriptRoot "src\codex_query_integrated.py"
        
        # 一時ファイルのパス
        $tempQueryFile = [System.IO.Path]::GetTempFileName()
        Write-Debug "一時ファイル: $tempQueryFile"
    }

    process {
        try {
            # クエリ文字列の処理
            if ([string]::IsNullOrWhiteSpace($Query)) {
                # パイプ入力がない場合、対話的に入力を促す
                Write-Host "# 何について調べますか？ > " -NoNewline -ForegroundColor Cyan
                $Query = Read-Host
            }

            if ([string]::IsNullOrWhiteSpace($Query)) {
                Write-Host "# エラー: クエリが空です" -ForegroundColor Red
                return
            }
            
            # クエリを一時ファイルに保存（文字コード問題を回避）
            $Query | Out-File -Encoding utf8 -FilePath $tempQueryFile
            Write-Host "# Codex CLI処理中..." -ForegroundColor Cyan
            
            # Pythonスクリプトを実行（引数で一時ファイルを指定）
            python $codexPath "--file" $tempQueryFile
            
            # エラー処理
            if ($LASTEXITCODE -ne 0) {
                Write-Host "# エラー: Codex CLIの実行に失敗しました (終了コード: $LASTEXITCODE)" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "# エラー: $($_.Exception.Message)" -ForegroundColor Red
            Write-Debug $_.Exception.StackTrace
        }
        finally {
            # 一時ファイルの削除
            if (Test-Path $tempQueryFile) {
                Remove-Item -Path $tempQueryFile -Force
            }
        }
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
    Write-Host "代わりに、次のように直接呼び出せます: Invoke-Codex '何について調べますか？'" -ForegroundColor Yellow
}
### Codex CLI setup - end