#!/bin/bash
set -euxo pipefail
cd "$USER"
rsync -avc --delete Documents "$HOME"
