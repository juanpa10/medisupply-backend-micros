#!/usr/bin/env bash
set -euo pipefail
if ! command -v k3s >/dev/null 2>&1; then
  curl -sfL https://get.k3s.io | sh -
fi
if [ ! -e /usr/local/bin/kubectl ]; then
  ln -s /usr/local/bin/k3s /usr/local/bin/kubectl || true
fi
if ! command -v aws >/dev/null 2>&1; then
  apt-get update -y && apt-get install -y awscli
fi
