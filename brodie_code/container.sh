#!/bin/bash

# Get absolute paths
INPUT_DIR=$(realpath "$(pwd)/input")
OUTPUT_DIR=$(realpath "$(pwd)/output")

docker run --rm -it \
  -v "$INPUT_DIR":/app/input \
  -v "$OUTPUT_DIR":/app/output \
  pdf-accessibility /bin/bash
