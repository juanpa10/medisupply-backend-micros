#!/usr/bin/env bash
set -euo pipefail

# Instala k3s (idempotente)
if ! command -v k3s >/dev/null 2>&1; then
  curl -sfL https://get.k3s.io | sh -
fi

# Alias kubectl (con k3s ya viene)
if [ ! -e /usr/local/bin/kubectl ]; then
  ln -s /usr/local/bin/k3s /usr/local/bin/kubectl || true
fi

# AWS CLI para crear el imagePullSecret a ECR
if ! command -v aws >/dev/null 2>&1; then
  apt-get update -y && apt-get install -y awscli
fi

# (Opcional) abrir puerto 80 si tu SG/iptables lo requiere en esta AMI
if command -v ufw >/dev/null 2>&1; then
  ufw allow 80/tcp || true
fi

echo "k3s listo."
