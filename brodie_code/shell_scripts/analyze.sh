#!/bin/bash

export ANTHROPIC_API_KEY=$(cat ./key.txt)

docker run --rm -v "$(pwd):/app" pdf-accessibility python3 -c "from accessibility_checker.utils.code_analyzer import main; main()"

