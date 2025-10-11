#!/usr/bin/env bash
set -euo pipefail

# 1) Instalar k3s (idempotente)
if ! command -v k3s >/dev/null 2>&1; then
  curl -sfL https://get.k3s.io | sh -
fi
# Alias kubectl
if [ ! -e /usr/local/bin/kubectl ]; then
  ln -s /usr/local/bin/k3s /usr/local/bin/kubectl || true
fi

# 2) Instalar AWS CLI v2 (idempotente, sin depender de apt awscli)
if ! command -v aws >/dev/null 2>&1; then
  # Dependencias mínimas
  if ! command -v unzip >/dev/null 2>&1; then
    sudo apt-get update -y || true
    sudo apt-get install -y unzip curl || true
  fi

  ARCH="$(uname -m)"
  if [ "$ARCH" = "x86_64" ] || [ "$ARCH" = "amd64" ]; then
    BUNDLE="awscli-exe-linux-x86_64"
  else
    # t4g.* = aarch64
    BUNDLE="awscli-exe-linux-aarch64"
  fi

  TMPDIR="$(mktemp -d)"
  curl -sSL "https://awscli.amazonaws.com/${BUNDLE}.zip" -o "${TMPDIR}/awscliv2.zip"
  unzip -q "${TMPDIR}/awscliv2.zip" -d "${TMPDIR}"
  sudo "${TMPDIR}/aws/install" --update
  rm -rf "${TMPDIR}"
fi

# 3) (Opcional) abrir 80 si usas UFW
if command -v ufw >/dev/null 2>&1; then
  ufw allow 80/tcp || true
fi

echo "k3s + awscli listos."

