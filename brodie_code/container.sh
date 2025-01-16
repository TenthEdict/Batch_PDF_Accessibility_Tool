#!/bin/bash

docker run --rm -it \
  -v "$(pwd)/input":/app/input \
  -v "$(pwd)/output":/app/output \
  pdf-accessibility /bin/bash
