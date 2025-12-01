#!/bin/bash
set -e

# Contract address on devnet (from previous deploy)
CONTRACT_ADDRESS="erd1qqqqqqqqqqqqqpgqavsxww8a7d8g225qf2hxhmcg46nw8fkpafls9dgeg9"

# PEM file path (can be passed as first argument or env variable)
PEM="${1:-${ALICE_PEM:-}}"
if [ -z "$PEM" ]; then
  echo "Error: PEM file path required. Pass as first argument or set ALICE_PEM env variable."
  exit 1
fi

# Gas limit (can be passed as second argument or env variable)
GAS_LIMIT="${2:-${GAS_LIMIT:-50000000}}"

WASM_PATH="../wasm/target/wasm32-unknown-unknown/release/trail_control_wasm.wasm"
PROXY="https://devnet-gateway.multiversx.com"

echo "Upgrading trail_control contract on devnet..."
echo "Contract: $CONTRACT_ADDRESS"
echo "PEM: $PEM"
echo "Gas limit: $GAS_LIMIT"

mxpy --verbose contract upgrade "$CONTRACT_ADDRESS" \
  --bytecode="$WASM_PATH" \
  --pem="$PEM" \
  --send \
  --proxy="$PROXY" \
  --gas-limit="$GAS_LIMIT" \
  --outfile="upgrade-devnet.interaction.json"

echo ""
echo "Contract upgraded successfully!"
echo "You can now query getCheckpointsFor and it should work correctly."
