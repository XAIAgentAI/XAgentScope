#!/bin/bash

# Ensure script fails on any error
set -e

# Configure terminal and locale for proper UTF-8 support
setup_terminal() {
    # Reset terminal to known state
    reset
    stty sane

    # Set up locale environment
    export LANG=C.UTF-8
    export LC_ALL=C.UTF-8
    export LC_CTYPE=C.UTF-8

    # Configure terminal for UTF-8
    export TERM=xterm-256color
    stty iutf8 2>/dev/null || true

    # Configure Python
    export PYTHONIOENCODING=utf-8
    export PYTHONUNBUFFERED=1
    export PYTHONUTF8=1

    # Ensure stdin/stdout use UTF-8
    exec 1> >(iconv -f utf-8 -t utf-8)
    exec 2> >(iconv -f utf-8 -t utf-8)

    # Verify locale
    locale >/dev/null 2>&1 || true
}

# Run dialog with proper environment
run_dialog() {
    local role=$1
    local host=$2
    local port=$3

    # Set up environment
    setup_terminal

    # Start Python with UTF-8 mode
    PYTHONIOENCODING=utf-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    python3 -X utf8 distributed_dialog.py \
        --role "$role" \
        --assistant-host "$host" \
        --assistant-port "$port"
}

# Main script
case "$1" in
    "assistant")
        run_dialog "assistant" "localhost" "12010"
        ;;
    "user")
        run_dialog "user" "localhost" "12010"
        ;;
    *)
        echo "用法：$0 [assistant|user]"
        echo "Usage: $0 [assistant|user]"
        exit 1
        ;;
esac
