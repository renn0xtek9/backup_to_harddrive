#!/bin/bash
set -euxo pipefail
cd "$USER"
rsync -avc --delete Videos "$HOME"
