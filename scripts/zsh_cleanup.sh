#!/bin/zsh
#
# A shell script to clean up the setup of Codex CLI for zsh
# 
set -e

CODEX_CLI_PATH="$( cd "$( dirname "$0" )" && cd .. && pwd )"
openAIConfigPath="$CODEX_CLI_PATH/src/openaiapirc"
zshrcPath="$HOME/.zshrc"
codexCliJsonPath="$HOME/.openai/codex-cli.json"

# 1. Remove settings in .zshrc
sed -i '' '/### Codex CLI setup - start/,/### Codex CLI setup - end/d' $zshrcPath
echo "Removed settings in $zshrcPath if present"

# 2. Remove opanaiapirc in /.config
rm -f $openAIConfigPath
echo "Removed $openAIConfigPath"

# 3. Remove codex-cli.json if exists
if [ -f "$codexCliJsonPath" ]; then
    rm -f $codexCliJsonPath
    echo "Removed $codexCliJsonPath"
fi

echo "Codex CLI clean up completed. Please open a new zsh to continue."