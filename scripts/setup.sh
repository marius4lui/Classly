#!/bin/bash
# Classly Setup Wrapper (Docker config wizard + legacy class bootstrap)

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Classly Setup Wizard${NC}"
echo "--------------------------------"

# Detect Environment (Docker vs Local)
if [ -f "/.dockerenv" ] || [ -f "docker-compose.yml" ]; then
    # We are either inside docker or have docker-compose available
    echo "Running setup..."
else
    echo "Warning: Not a standard Classly directory structure."
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WIZARD_PATH="$SCRIPT_DIR/classly_setup_cli.py"
LEGACY_PATH="$SCRIPT_DIR/setup_class.py"

run_python_script() {
    local script="$1"
    shift
    if command -v python3 &>/dev/null; then
        python3 "$script" "$@"
    elif command -v python &>/dev/null; then
        python "$script" "$@"
    else
        echo -e "${RED}Error: Python not found.${NC}"
        exit 1
    fi
}

# Backwards compatibility:
# If legacy class bootstrap args are used, keep old behavior.
for arg in "$@"; do
    if [[ "$arg" == "--class-name" ]] || [[ "$arg" == "--user-name" ]]; then
        if [ ! -f "$LEGACY_PATH" ]; then
            echo "Downloading legacy helper script..."
            curl -sL https://scripts.classly.site/setup_class.py -o setup_class_temp.py
            LEGACY_PATH="setup_class_temp.py"
        fi
        run_python_script "$LEGACY_PATH" "$@"
        if [ "$LEGACY_PATH" == "setup_class_temp.py" ]; then
            rm setup_class_temp.py
        fi
        exit 0
    fi
done

# New Docker setup wizard.
if [ ! -f "$WIZARD_PATH" ]; then
    echo "Downloading setup CLI..."
    curl -sL https://scripts.classly.site/classly_setup_cli.py -o classly_setup_cli_temp.py
    WIZARD_PATH="classly_setup_cli_temp.py"
fi

if [ $# -eq 0 ]; then
    run_python_script "$WIZARD_PATH" wizard
else
    run_python_script "$WIZARD_PATH" "$@"
fi

if [ "$WIZARD_PATH" == "classly_setup_cli_temp.py" ]; then
    rm classly_setup_cli_temp.py
fi
