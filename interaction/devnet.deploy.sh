#!/usr/bin/env bash
set -euo pipefail

# Example deploy script for MultiversX devnet using mxpy
# Usage:
# 1) Install mxpy (pip install multiversx-sdk) and ensure `mxpy` is on PATH
# 2) Set PEM path: export ALICE_PEM="/path/to/your/devnet-wallet.pem"
# 3) Run: ./devnet.deploy.sh

PROJECT="../wasm/target/wasm32-unknown-unknown/release/trail_control_wasm.wasm"
PROXY="https://devnet-gateway.multiversx.com"

# Accept PEM as first argument or from env
PEM="${1:-${ALICE_PEM:-}}"
# Accept gas limit as second argument or from env
GAS_LIMIT="${2:-${GAS_LIMIT:-10000000}}"

if [ -z "${PEM}" ]; then
  echo "Please provide path to your PEM file as first argument or export ALICE_PEM env var."
  echo "Example: ./devnet.deploy.sh /home/user/.mx/devnet-deployer.pem"
  exit 1
fi
if [ "$#" -ge 2 ]; then
  GAS_LIMIT="$2"
fi

if [ ! -f "${PROJECT}" ]; then
  echo "WASM artifact not found at ${PROJECT}. Build it first:"
  echo "  cd samples/trailControl/wasm && cargo build --release --target wasm32-unknown-unknown"
  exit 1
fi

echo "Deploying trail_control to devnet..."

mxpy --verbose contract deploy \
  --bytecode="${PROJECT}" \
  --pem="${PEM}" \
  --send \
  --outfile="deploy-devnet.interaction.json" \
  --proxy="${PROXY}" \
  --gas-limit="${GAS_LIMIT}"

TRANSACTION=$(mxpy data parse --file="deploy-devnet.interaction.json" --expression="data['emittedTransactionHash']")
ADDRESS=$(mxpy data parse --file="deploy-devnet.interaction.json" --expression="data['contractAddress']")

echo "Deployed contract address: ${ADDRESS}"
echo "Transaction hash: ${TRANSACTION}"

mxpy data store --key=address-devnet --value="${ADDRESS}"
mxpy data store --key=deployTransaction-devnet --value="${TRANSACTION}"

echo "now you can call markCheckpoint and query getCheckpointsFor. Example:" 
echo "mxpy --verbose contract call ${ADDRESS} --pem=${ALICE_PEM} --function=markCheckpoint --arguments 1 --send --proxy=${PROXY} --gas-limit=10000000"
echo "mxpy --verbose contract query ${ADDRESS} --function=getCheckpointsFor --arguments $(mxpy wallet bech32 --decode $(mxpy data load --key=address-devnet)) --proxy=${PROXY}"
