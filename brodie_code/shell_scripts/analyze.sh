#!/bin/bash

export ANTHROPIC_API_KEY=$(cat ./key.txt)

docker run --rm -v "$(pwd):/app" pdf-accessibility python3 -m accessibility_checker.utils.code_analyzer /app/src

