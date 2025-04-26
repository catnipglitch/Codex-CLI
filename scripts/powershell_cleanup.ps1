### 
# PowerShell script to clean up the Codex CLI settings for PowerShell
#
# File/Content to be removed:
# 1. PowerShell profile (Remove file if the content only has Codex CLI setup; otherwise, wipe the Codex CLI setup content)
# 2. OpenAI configuration file (openaiapirc)
# 3. Codex CLI settings file (codex-cli.json)
# 4. Old settings file (settings.json)
###

Write-Host "Starting Codex CLI PowerShell clean up..."

# Get the current path
$currentPath = Get-Location

# Remove plugin call from PowerShell profile
if (Test-Path -Path $PROFILE) {
    (Get-Content -Path $PROFILE -Raw) -replace "(?ms)### Codex CLI setup - start.*?### Codex CLI setup - end", "" | Set-Content -Path $PROFILE
    Write-Host "Removed setup script from $PROFILE."
}

# Remove the OpenAI API key file if exists
$openAIConfigPath = Join-Path (Split-Path (Split-Path $currentPath -Parent) -Parent) -ChildPath "src\openaiapirc"
if (Test-Path -Path $openAIConfigPath) {
    Remove-Item -Path $openAIConfigPath -Force
    Write-Host "Removed OpenAI configuration file."
}

# Remove codex-cli.json settings file
$codexCliJsonPath = Join-Path $HOME -ChildPath ".openai\codex-cli.json"
if (Test-Path -Path $codexCliJsonPath) {
    Remove-Item -Path $codexCliJsonPath -Force
    Write-Host "Removed $codexCliJsonPath"
}

# Also clean up the old settings.json for backward compatibility
$settingsJsonPath = Join-Path $HOME -ChildPath ".openai\settings.json"
if (Test-Path -Path $settingsJsonPath) {
    Remove-Item -Path $settingsJsonPath -Force
    Write-Host "Removed old settings file $settingsJsonPath"
}

Write-Host "Codex CLI cleanup complete. Please restart PowerShell to complete the cleanup."