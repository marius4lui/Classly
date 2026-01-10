#!/bin/bash
# Classly Setup Wrapper

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

# Check if arguments provided, otherwise interactive
if [ $# -eq 0 ]; then
    echo "No arguments provided. Starting interactive mode..."
    echo ""
    read -p "Class Name (e.g. 10B): " CLASS_NAME
    read -p "Owner Name (e.g. Mr. Smith): " OWNER_NAME
    read -p "Email (Optional): " EMAIL
    read -p "Password (Optional): " PASSWORD

    ARGS="--class-name \"$CLASS_NAME\" --user-name \"$OWNER_NAME\""
    
    if [ ! -z "$EMAIL" ]; then
        ARGS="$ARGS --email \"$EMAIL\""
    fi
    if [ ! -z "$PASSWORD" ]; then
        ARGS="$ARGS --password \"$PASSWORD\""
    fi
    
    # Run python script
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    SCRIPT_PATH="$SCRIPT_DIR/setup_class.py"
    
    # Check if setup_class.py exists. If not (e.g. piped via curl), download it.
    if [ ! -f "$SCRIPT_PATH" ]; then
        echo "Downloading helper script..."
        curl -sL https://scripts.classly.site/setup_class.py -o setup_class_temp.py
        SCRIPT_PATH="setup_class_temp.py"
    fi
    
    if command -v python3 &>/dev/null; then
        eval python3 "$SCRIPT_PATH" $ARGS
    elif command -v python &>/dev/null; then
        eval python "$SCRIPT_PATH" $ARGS
    else
        echo -e "${RED}Error: Python not found.${NC}"
        exit 1
    fi
    
    # Cleanup temp file
    if [ "$SCRIPT_PATH" == "setup_class_temp.py" ]; then
        rm setup_class_temp.py
    fi
else
    # Arguments provided, pass through
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    SCRIPT_PATH="$SCRIPT_DIR/setup_class.py"
    
    if [ ! -f "$SCRIPT_PATH" ]; then
         # Try current directory or download
         if [ -f "setup_class.py" ]; then
             SCRIPT_PATH="setup_class.py"
         else
             curl -sL https://docs.classly.site/scripts/setup_class.py -o setup_class_temp.py
             SCRIPT_PATH="setup_class_temp.py"
         fi
    fi

    if command -v python3 &>/dev/null; then
        python3 "$SCRIPT_PATH" "$@"
    elif command -v python &>/dev/null; then
        python "$SCRIPT_PATH" "$@"
    else
        echo -e "${RED}Error: Python not found.${NC}"
        exit 1
    fi
    
    if [ "$SCRIPT_PATH" == "setup_class_temp.py" ]; then
        rm setup_class_temp.py
    fi
fi
