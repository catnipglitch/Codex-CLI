#!/usr/bin/env bash

set -e
trap 'exitScript' ERR

help()
{
    cat <<- _EOF_
Help for Codex CLI Bash setup script

Usage: source bash_setup.sh [optional parameters]

    -o orgId     Set the OpenAI organization id.
    -k apiKey    Set the OpenAI API key.
    -e modelName  Set the OpenAI model name.
    -l language  Set the language (en, ja). Default is "en".
    -d           Print some system information for debugging.
    -h           Print this help content.

To uninstall Codex CLI use bash_cleanup.sh.
For more information visit https://github.com/microsoft/Codex-CLI
_EOF_
}

# Read command line parameters
readParameters()
{
    while [ "$1" != "" ]; do
        case $1 in
            -o ) shift; ORG_ID=$1 ;;
            -k ) shift; SECRET_KEY=$1 ;;
            -e ) shift; MODEL_NAME=$1 ;;
            -l ) shift; LANGUAGE=$1 ;;
            -d ) systemInfo
                 exitScript
                ;;
            * ) help
                exitScript
                ;;
        esac
        shift
    done
}

# Prompt user for OpenAI settings
askSettings()
{
    echo "*** Starting Codex CLI bash setup ***"
    if [ -z "$ORG_ID" ]; then
        echo -n 'OpenAI Organization Id: '; read ORG_ID
    fi
    if [ -z "$SECRET_KEY" ]; then
        echo -n 'OpenAI API key: '; read -s SECRET_KEY; echo
    fi
    if [ -z "$MODEL_NAME" ]; then
        echo -n 'OpenAI Model Name: '; read MODEL_NAME
    fi
    if [ -z "$LANGUAGE" ]; then
        echo -n 'Language (en, ja): '; read LANGUAGE
    fi
}

# Call OpenAI API with the given settings to verify everything is in order
validateSettings()
{
    echo -n "*** Testing Open AI access... "
    local TEST=$(curl -s 'https://api.openai.com/v1/models' -H "Authorization: Bearer $SECRET_KEY" -H "OpenAI-Organization: $ORG_ID" -w '%{http_code}')
    local STATUS_CODE=$(echo "$TEST"|tail -n 1)
    if [ $STATUS_CODE -ne 200 ]; then
        echo "ERROR [$STATUS_CODE]"
        echo "Failed to access OpenAI API, result: $STATUS_CODE"
        echo "Please check your OpenAI API key (https://platform.openai.com/api-keys)"
        echo "and Organization ID (https://platform.openai.com/account/organization)."
        echo "*************"
        exitScript
        return
    fi
    local MODEL_FOUND=$(echo "$TEST"|grep '"id"'|grep "\"$MODEL_NAME\"")
    if [ -z "$MODEL_FOUND" ]; then
        echo "WARNING"
        echo "Could not find OpenAI model: $MODEL_NAME in your available models."
        echo "This might be because the model is not available to your account, or because the API response format has changed."
        echo "Continuing setup anyway, but you may need to update the model name later."
    else
        echo "OK ***"
    fi
}

# Store API key and other settings in `openaiapirc`
configureApp()
{ 
    echo "*** Configuring application [$OPENAI_RC_FILE] ***"
    echo '[openai]' > $OPENAI_RC_FILE
    echo "organization_id=$ORG_ID" >> $OPENAI_RC_FILE
    echo "secret_key=$SECRET_KEY" >> $OPENAI_RC_FILE
    echo "model=$MODEL_NAME" >> $OPENAI_RC_FILE
    echo "language=$LANGUAGE" >> $OPENAI_RC_FILE
    chmod +x "$CODEX_CLI_PATH/src/codex_query.py"
}

# Create and load ~/.codexclirc to setup bash 'Ctrl + G' binding
configureBash()
{
    echo "*** Configuring bash [$BASH_RC_FILE] ***"
    echo -n > $HOME/.codexclirc
    echo "export CODEX_CLI_PATH=\"${CODEX_CLI_PATH}\"" >> $BASH_RC_FILE
    echo 'source "$CODEX_CLI_PATH/scripts/bash_plugin.sh"' >> $BASH_RC_FILE
    echo "bind -x '\"\C-g\":\"create_completion\"'" >> $BASH_RC_FILE
    if [ $SOURCED -eq 1 ]; then
        echo "*** Testing bash settings [$BASH_RC_FILE] ***"
        source "$BASH_RC_FILE"
    fi
}

# Add call to .codexclirc into .bashrc
enableApp()
{
    echo "*** Activating application [$HOME/.bashrc] ***"
    # Check if already installed
    if grep -Fq ".codexclirc" $HOME/.bashrc; then
        return 0
    fi
    echo -e "\n# Initialize Codex CLI" >> $HOME/.bashrc
    echo 'if [ -f "$HOME/.codexclirc" ]; then' >> $HOME/.bashrc
    echo '    . "$HOME/.codexclirc"' >> $HOME/.bashrc
    echo 'fi' >> $HOME/.bashrc
}

# Print some system details useful to debug the script in case it's not working
systemInfo()
{
    echo "*** system ***"
    uname -smpr
    echo "*** shell ***"
    echo $SHELL
    echo "*** bash interpreter ***"
    echo $BASH_VERSION
    echo "*** python ***"
    if command -v python &> /dev/null; then
        which python
        python --version
    else
        echo "python not found"
    fi
    echo "*** curl ***"
    if command -v curl &> /dev/null; then
        which curl
        curl --version
    else
        echo "curl not found"
    fi
}

# Remove variables and functions from the environment, in case the script was sourced
cleanupEnv()
{
    unset ORG_ID SECRET_KEY MODEL_NAME LANGUAGE SOURCED OPENAI_RC_FILE BASH_RC_FILE
    unset -f askSettings validateSettings configureApp configureBash enableApp readParameters
}

# Clean exit for sourced scripts
exitScript()
{
    cleanupEnv
    kill -SIGINT $$
}

# Detect if the script is sourced
(return 0 2>/dev/null) && SOURCED=1 || SOURCED=0

# Path to Codex CLI source
CODEX_CLI_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
# Path to OpenAI API settings
OPENAI_RC_FILE="$CODEX_CLI_PATH/src/openaiapirc"
# Path to Bash settings loaded when a Bash session starts
BASH_RC_FILE="$HOME/.codexclirc"

# Start installation
readParameters $*
askSettings
validateSettings
configureApp
configureBash
enableApp
cleanupEnv

echo -e "*** Setup complete! ***\n";

echo "***********************************************"
echo "Open a new Bash terminal, type '#' followed by"
echo "your natural language command and hit Ctrl + G!"
echo "***********************************************"
