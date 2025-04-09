#!/bin/bash
INPUT_DIR=$(realpath "$(pwd)/input")
OUTPUT_DIR=$(realpath "$(pwd)/output")
docker run --rm -it \
  -v "$INPUT_DIR":/app/input \
  -v "$OUTPUT_DIR":/app/output \
  schipp0/pdf-accessibility /bin/bash
