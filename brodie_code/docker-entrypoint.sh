#!/bin/bash
set -e

case "$1" in
    process)
        # Original behavior - run the PDF processor
        exec python -m accessibility_checker.core.batch
        ;;
    post-process)
        # Run post-processing for PDF/UA compliance
        exec python -m accessibility_checker.post_processor
        ;;
    *)
        # Run any other command as is (maintains original shell access)
        exec "$@"
        ;;
esac
