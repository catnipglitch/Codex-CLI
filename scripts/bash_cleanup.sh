#!/usr/bin/env bash

echo "*** Starting Codex CLI bash clean up ***"

# Clean up plugin and source
if grep -Fq ".codexclirc" $HOME/.bashrc; then
    # Remove call to .codexclirc from .bashrc
    sed -i "/# Initialize Codex CLI/,+3d" $HOME/.bashrc
    echo "*** Removed app initialization from $HOME/.bashrc ***"
fi

# Clean up codexclirc
if [ -f "$HOME/.codexclirc" ]; then
    # Get the path to src/openaiapirc
    if [ -f "$HOME/.codexclirc" ]; then
        CODEX_CLI_PATH=$(grep "CODEX_CLI_PATH=" $HOME/.codexclirc | cut -d'"' -f2)
        if [ -f "$CODEX_CLI_PATH/src/openaiapirc" ]; then
            echo "*** Removing $CODEX_CLI_PATH/src/openaiapirc ***"
            rm "$CODEX_CLI_PATH/src/openaiapirc"
        fi
    fi

    # Remove .codexclirc file
    rm "$HOME/.codexclirc"
    echo "*** Removed $HOME/.codexclirc ***"
fi

# Clean up settings.json and codex-cli.json
if [ -f "$HOME/.openai/codex-cli.json" ]; then
    rm "$HOME/.openai/codex-cli.json"
    echo "*** Removed $HOME/.openai/codex-cli.json ***"
fi

# Old settings file for backward compatibility
if [ -f "$HOME/.openai/settings.json" ]; then
    rm "$HOME/.openai/settings.json"
    echo "*** Removed $HOME/.openai/settings.json ***"
fi

echo "*** Clean up complete! ***"
echo "*** Close this terminal and open a new one to finalize. ***"
