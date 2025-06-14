#!/bin/bash
# shellcheck disable=SC1091,SC2059
set -e

sed -i 's/\r$//' /workspaces/irr-calculator/cli/bin/irr-calculator
chmod +x /workspaces/irr-calculator/cli/bin/irr-calculator
git config --global --add safe.directory /workspaces/irr-calculator
gcloud auth application-default login

FILE="./.devcontainer/git_config.sh"
if [ -f "$FILE" ]; then
    chmod +x "$FILE"
    "$FILE"
else
    echo "$FILE not found. Follow instructions in README.md to set up git config. ### Configure Git"
fi