# TrailControl CLI

Script Python per interactuar amb el smart contract TrailControl a la devnet de MultiversX.

## Contract Desplegat

- **Adreça:** `erd1qqqqqqqqqqqqqpgq9xrcm5t9axzsdgak3xz3ljqd3gc62xvcafls8uljtt`
- **Network:** MultiversX Devnet
- **Explorer:** [View Contract](https://devnet-explorer.multiversx.com/accounts/erd1qqqqqqqqqqqqqpgq9xrcm5t9axzsdgak3xz3ljqd3gc62xvcafls8uljtt)

## Prerequisits

- Python 3.7+
- `mxpy` (MultiversX CLI) instal·lat i disponible al PATH
  ```bash
  pip install multiversx-sdk-cli
  ```

## Ús

### 1. Marcar un checkpoint

Registra un nou checkpoint per a una wallet específica:

```bash
python trail_control_cli.py mark <pem_file> <checkpoint_id>
```

**Exemple:**
```bash
python trail_control_cli.py mark ../walletg.pem 5
```

**Sortida:**
```
🏁 Marcant checkpoint 5...
   PEM: ../walletg.pem
   Wallet: erd1d8sf28qdes9rjj2rkpvndydanc9n24xsnldnls9gqpy6km3xaflszh8a6c
✅ Checkpoint marcat correctament!
   TX: https://devnet-explorer.multiversx.com/transactions/abc123...
```

### 2. Consultar checkpoints d'una wallet (per adreça)

Consulta tots els checkpoints marcats per una adreça específica:

```bash
python trail_control_cli.py query <address>
```

**Exemple:**
```bash
python trail_control_cli.py query erd1d8sf28qdes9rjj2rkpvndydanc9n24xsnldnls9gqpy6km3xaflszh8a6c
```

**Sortida:**
```
📋 Consultant checkpoints per a: erd1d8sf28...zh8a6c

   ID     Timestamp       Data/Hora
   ------ --------------- ------------------------------
   1      1764585596      2025-12-01 10:39:56 UTC
   2      1764585614      2025-12-01 10:40:14 UTC
   3      1764585620      2025-12-01 10:40:20 UTC
```

### 3. Consultar checkpoints d'una wallet (des d'un fitxer PEM)

Consulta els checkpoints usant directament un fitxer PEM:

```bash
python trail_control_cli.py query-pem <pem_file>
```

**Exemple:**
```bash
python trail_control_cli.py query-pem ../corredor1.pem
```

**Sortida:**
```
📋 Consultant checkpoints per a: erd1f2y6uj...hlaj7l

   ID     Timestamp       Data/Hora
   ------ --------------- ------------------------------
   10     1764585776      2025-12-01 10:42:56 UTC
   20     1764585782      2025-12-01 10:43:02 UTC
```

### 4. Llistar totes les wallets amb checkpoints

Mostra un resum de totes les wallets que han marcat almenys un checkpoint:

```bash
python trail_control_cli.py list
```

**Sortida:**
```
👥 Consultant totes les wallets amb checkpoints...

================================================================================
RESUM DE TOTES LES WALLETS
================================================================================

Total wallets: 3

Wallet 1: erd1d8sf28qdes9rjj2rkpvndydanc9n24xsnldnls9gqpy6km3xaflszh8a6c
  Checkpoints:
    • ID  1 - 2025-12-01 10:39:56 UTC
    • ID  2 - 2025-12-01 10:40:14 UTC
    • ID  3 - 2025-12-01 10:40:20 UTC

Wallet 2: erd1f2y6uj9wrm4xn7py437x8atc9y6gvu08w4ahmfehq5jw7za90urqhlaj7l
  Checkpoints:
    • ID 10 - 2025-12-01 10:42:56 UTC
    • ID 20 - 2025-12-01 10:43:02 UTC

Wallet 3: erd1e0kx7qn5um9cphy6dzhzy9hukjggqh0xctwxhm9ty2atalcwtydqkkaana
  Checkpoints:
    • ID 15 - 2025-12-01 10:43:08 UTC
    • ID 30 - 2025-12-01 10:49:56 UTC
```

### 5. Ajuda

Mostra la informació d'ús:

```bash
python trail_control_cli.py help
```

## Wallets Disponibles

Fitxers PEM disponibles al directori `samples/trailControl/`:

- `walletg.pem` - Wallet principal de test
- `corredor1.pem` - Wallet corredor 1
- `corredor2.pem` - Wallet corredor 2

## Estructura del Projecte

```
samples/trailControl/
├── src/
│   └── lib.rs                    # Codi del smart contract
├── wasm/                         # Wrapper per generar WASM
├── interaction/
│   ├── trail_control_cli.py     # CLI Python (aquest script)
│   ├── devnet.deploy.sh         # Script de deploy
│   ├── devnet.upgrade.sh        # Script d'upgrade
│   └── CLI_README.md            # Aquesta documentació
├── walletg.pem                  # Wallet de test
├── corredor1.pem                # Wallet corredor 1
└── corredor2.pem                # Wallet corredor 2
```

## Notes Tècniques

- **Gas Limit:** Per defecte s'usa 10,000,000 gas per cada transacció
- **Timestamps:** Els timestamps s'emmagatzemen en format Unix (segons des de 1970)
- **Checkpoint IDs:** Qualsevol enter positiu (u32) és vàlid com a ID de checkpoint
- **Encoding:** Les adreces es retornen en format hex pel contract i es converteixen a bech32 pel CLI

## Exemples d'Ús Complet

### Cas d'ús: Carregar corredor amb múltiples checkpoints

```bash
# Marcar checkpoint 1 per corredor1
python trail_control_cli.py mark ../corredor1.pem 1

# Marcar checkpoint 2 per corredor1
python trail_control_cli.py mark ../corredor1.pem 2

# Marcar checkpoint 3 per corredor1
python trail_control_cli.py mark ../corredor1.pem 3

# Veure tots els checkpoints
python trail_control_cli.py query-pem ../corredor1.pem
```

### Cas d'ús: Comparar progressió de múltiples corredors

```bash
# Veure resum global
python trail_control_cli.py list
```

## Troubleshooting

### Error: "mxpy: command not found"

Assegura't que `mxpy` està instal·lat:
```bash
pip install multiversx-sdk-cli
```

### Error: "Fitxer PEM no trobat"

Verifica que la ruta al fitxer PEM és correcta. Els fitxers PEM es troben al directori `samples/trailControl/`.

### Error al marcar checkpoint: "insufficient funds"

La wallet necessita tenir EGLD a la devnet. Pots obtenir tokens de test a:
https://devnet-wallet.multiversx.com/faucet

## Autor

Creat per al projecte TrailControl - Smart Contract de gestió de checkpoints a MultiversX.
