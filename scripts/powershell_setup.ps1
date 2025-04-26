### 
# PowerShell script to setup Codex CLI for PowerShell
###
param
(
    [Parameter()]
    [System.IO.FileInfo]
    [ValidateScript( {
            if (-Not ($_ | Test-Path) ) {
                throw "Folder does not exist. Did you clone the Codex CLI repo?" 
            }
            return $true
        })]
    [string]$RepoRoot = (Get-Location),

    [Parameter(Mandatory = $false)]
    [SecureString]
    $OpenAIApiKey,

    [Parameter(Mandatory = $false)]
    [string]
    $OpenAIOrganizationId,

    [Parameter(Mandatory = $false)]
    [string]
    $OpenAIModelName = "gpt-4o"
)

$plugInScriptPath = Join-Path $RepoRoot -ChildPath "scripts\powershell_plugin.ps1"
$codexQueryPath = Join-Path $RepoRoot -ChildPath "src\codex_query.py"
$openAIConfigPath = Join-Path $RepoRoot -ChildPath "src\openaiapirc"

# 環境変数からAPIキーとOrganization IDを取得
$envApiKey = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY")
$envOrgId = [Environment]::GetEnvironmentVariable("OPENAI_ORGANIZATION_ID")
$envModel = [Environment]::GetEnvironmentVariable("OPENAI_MODEL") 

# パラメータが空の場合は環境変数から取得
if (-not $OpenAIApiKey) {
    if ($envApiKey) {
        Write-Host "環境変数からAPIキーを取得しました"
        $OpenAIApiKey = ConvertTo-SecureString $envApiKey -AsPlainText -Force
    }
    else {
        $OpenAIApiKey = Read-Host "OpenAI APIキーを入力してください" -AsSecureString
    }
}

if (-not $OpenAIOrganizationId) {
    if ($envOrgId) {
        Write-Host "環境変数からOrganization IDを取得しました"
        $OpenAIOrganizationId = $envOrgId
    }
    else {
        $OpenAIOrganizationId = Read-Host "OpenAI Organization IDを入力してください"
    }
}

if (-not $OpenAIModelName -or $OpenAIModelName -eq "gpt-4o") {
    if ($envModel) {
        Write-Host "環境変数からモデル名を取得しました: $envModel"
        $OpenAIModelName = $envModel
    }
    # デフォルト値が設定されているので入力は不要
}

# The major version of PowerShell
$PSMajorVersion = $PSVersionTable.PSVersion.Major

# APIキーの検証
if ($null -eq $OpenAIApiKey -or $OpenAIApiKey.Length -eq 0) {
    Write-Error "OpenAI APIキーが設定されていません。環境変数OPENAI_API_KEYを設定するか、パラメータで指定してください。"
    exit 1
}

# Convert secure string to plain text
try {
    if ($PSMajorVersion -lt 7) {
        $binaryString = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($OpenAIApiKey);
        $openAIApiKeyPlainText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($binaryString);
    }
    else {
        $openAIApiKeyPlainText = ConvertFrom-SecureString -SecureString $OpenAIApiKey -AsPlainText
    }

    if ([string]::IsNullOrEmpty($openAIApiKeyPlainText)) {
        Write-Error "APIキーの変換に失敗しました。有効なAPIキーを入力してください。"
        exit 1
    }
}
catch {
    Write-Error "APIキーの処理中にエラーが発生しました: $_"
    exit 1
}

# Check the access with OpenAI API
Write-Host "Checking OpenAI access..."
$modelsApiUri = "https://api.openai.com/v1/models"
$response = $null
try {
    if ($PSMajorVersion -lt 7) {
        $response = (Invoke-WebRequest -Uri $modelsApiUri -Headers @{"Authorization" = "Bearer $openAIApiKeyPlainText"; "OpenAI-Organization" = "$OpenAIOrganizationId" })
    }
    else {
        $response = (Invoke-WebRequest -Uri $modelsApiUri -Authentication Bearer -Token $OpenAIApiKey -Headers @{"OpenAI-Organization" = "$OpenAIOrganizationId" })
    }
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Error "Failed to access OpenAI api [$statusCode]. Please check your OpenAI API key (https://platform.openai.com/api-keys) and Organization ID (https://platform.openai.com/account/organization)."
    exit 1
}

# Check if target model is available to the user
if ($null -eq (($response.Content | ConvertFrom-Json).data | Where-Object { $_.id -eq $OpenAIModelName })) {
    Write-Warning "Could not find OpenAI model: $OpenAIModelName in your available models. This might be because the model is not available to your account, or because the API response format has changed."
    Write-Host "Continuing setup anyway, but you may need to update the model name later."
}

# Create new PowerShell profile if doesn't exist. The profile type is for current user and current host.
# To learn more about PowerShell profile, please refer to 
# https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles
if (!(Test-Path -Path $PROFILE)) {
    New-Item -Type File -Path $PROFILE -Force 
}
else {
    # Clean up the content before append new one. This allow users to setup multiple times without running cleanup script
    (Get-Content -Path $PROFILE -Raw) -replace "(?ms)### Codex CLI setup - start.*?### Codex CLI setup - end", "" | Set-Content -Path $PROFILE
    Write-Host "Removed previous setup script from $PROFILE."
}

# Add our plugin script into PowerShell profile. It involves three steps:
# 1. Read the plugin script content,
# 2. Replace hardcode variable with the actual path to codex_query.py, 
# 3. Add the plugin script to the content of PowerShell profile.
(Get-Content -Path $plugInScriptPath) -replace "{{codex_query_path}}", $codexQueryPath | Add-Content -Path $PROFILE
Write-Host "Added plugin setup to $PROFILE."

# Create OpenAI configuration file to store secrets
if (!(Test-Path -Path $openAIConfigPath)) {
    New-Item -Type File -Path $openAIConfigPath -Force 
}

Set-Content -Path $openAIConfigPath "[openai]
organization_id=$OpenAIOrganizationId
secret_key=$openAIApiKeyPlainText
model=$OpenAIModelName"
Write-Host "Updated OpenAI configuration file with secrets."

# デバッグ情報の追加
Write-Host "セットアップ情報の確認:"
Write-Host "- プロファイル場所: $PROFILE"
Write-Host "- 設定ファイル場所: $openAIConfigPath"
Write-Host "- Pythonスクリプト場所: $codexQueryPath"

# 一般的な問題のトラブルシューティング
if (!(Test-Path $codexQueryPath)) {
    Write-Warning "警告: codex_query.py ファイルが見つかりません。リポジトリが正しくクローンされているか確認してください。"
}

if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Warning "警告: Python が見つかりません。Python がインストールされ、PATHに追加されていることを確認してください。"
}
else {
    $pythonVersion = python --version
    Write-Host "検出されたPythonバージョン: $pythonVersion"
    
    # Pythonの依存関係を確認
    $requirementsPath = Join-Path $RepoRoot -ChildPath "requirements.txt"
    if (Test-Path $requirementsPath) {
        Write-Host "requirements.txt が見つかりました。依存関係をインストールするには次のコマンドを実行してください："
        Write-Host "python -m pip install -r $requirementsPath"
    }
}

Write-Host -ForegroundColor Blue "Codex CLI PowerShell (v$PSMajorVersion) setup completed. Please open a new PowerShell session, type in # followed by your natural language command and hit Ctrl+G!"

Write-Host -ForegroundColor Yellow @"

トラブルシューティング:
1. 新しいPowerShellセッションを開いたことを確認してください（現在のセッションを閉じて新しいものを開く）
2. Pythonとその依存関係がインストールされていることを確認してください
   - 'python -m pip install -r $(Join-Path $RepoRoot -ChildPath "requirements.txt")'
3. '#' の後に自然言語コマンドを入力し、Ctrl+Gを押してください
4. それでも動作しない場合は、以下のコマンドを実行してエラーをチェックしてください:
   - 'Test-Path $PROFILE' (Trueが返るべき)
   - 'Get-Content $PROFILE' (プロファイルにCodex CLIスクリプトが含まれているか確認)
   - 'Test-Path "$openAIConfigPath"' (設定ファイルが存在するか確認)
"@
