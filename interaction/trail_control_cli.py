#!/usr/bin/env python3
"""
TrailControl CLI - Gestió de checkpoints al smart contract
Usage: python trail_control_cli.py [command] [options]
"""

import sys
import json
import subprocess
import datetime
from pathlib import Path

# Configuration
CONTRACT_ADDRESS = "erd1qqqqqqqqqqqqqpgq9xrcm5t9axzsdgak3xz3ljqd3gc62xvcafls8uljtt"
PROXY = "https://devnet-gateway.multiversx.com"
GAS_LIMIT = "10000000"

# Bech32 encoding functions
CHARSET = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l'

def bech32_polymod(values):
    GENERATORS = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for v in values:
        b = (chk >> 25)
        chk = ((chk & 0x1ffffff) << 5) ^ v
        for i in range(5):
            if (b >> i) & 1:
                chk ^= GENERATORS[i]
    return chk

def bech32_hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def bech32_create_checksum(hrp, data):
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + [0]*6) ^ 1
    return [(polymod >> 5*(5-i)) & 31 for i in range(6)]

def bech32_encode(hrp, data):
    combined = data + bech32_create_checksum(hrp, data)
    return hrp + '1' + ''.join([CHARSET[d] for d in combined])

def convertbits(data, frombits, tobits, pad=True):
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    for b in data:
        acc = (acc << frombits) | b
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad and bits:
        ret.append((acc << (tobits-bits)) & maxv)
    return ret

def hex_to_bech32(hrp, hexstr):
    b = bytes.fromhex(hexstr)
    five = convertbits(list(b), 8, 5)
    return bech32_encode(hrp, five)

def get_address_from_pem(pem_path):
    """Extract bech32 address from PEM file"""
    with open(pem_path, 'r') as f:
        first_line = f.readline()
        # Format: -----BEGIN PRIVATE KEY for erd1...-----
        if 'erd1' in first_line:
            start = first_line.index('erd1')
            end = first_line.index('-----', start)
            return first_line[start:end].strip()
    raise ValueError(f"Could not extract address from {pem_path}")

def format_timestamp(ts):
    """Convert unix timestamp to readable date"""
    dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
    return dt.strftime('%Y-%m-%d %H:%M:%S UTC')

def mark_checkpoint(pem_path, checkpoint_id):
    """Mark a checkpoint using the specified PEM wallet"""
    print(f"\n🏁 Marcant checkpoint {checkpoint_id}...")
    print(f"   PEM: {pem_path}")
    
    if not Path(pem_path).exists():
        print(f"❌ Error: Fitxer PEM no trobat: {pem_path}")
        return False
    
    try:
        address = get_address_from_pem(pem_path)
        print(f"   Wallet: {address}")
        
        cmd = [
            "mxpy", "contract", "call", CONTRACT_ADDRESS,
            f"--pem={pem_path}",
            "--function=markCheckpoint",
            f"--arguments={checkpoint_id}",
            "--send",
            f"--proxy={PROXY}",
            f"--gas-limit={GAS_LIMIT}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Error executant transacció:")
            print(result.stderr)
            return False
        
        # Extract transaction hash from output
        for line in result.stdout.split('\n'):
            if 'devnet-explorer.multiversx.com/transactions/' in line:
                tx_hash = line.strip().split('/')[-1]
                print(f"✅ Checkpoint marcat correctament!")
                print(f"   TX: https://devnet-explorer.multiversx.com/transactions/{tx_hash}")
                return True
        
        print("✅ Checkpoint marcat (no s'ha pogut extreure el hash)")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def query_checkpoints(address):
    """Query checkpoints for a specific wallet address"""
    print(f"\n📋 Consultant checkpoints per a: {address}")
    
    cmd = [
        "mxpy", "contract", "query", CONTRACT_ADDRESS,
        "--function=getCheckpointsFor",
        f"--arguments=addr:{address}",
        f"--proxy={PROXY}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return
        
        checkpoints_raw = json.loads(result.stdout.strip())
        
        if len(checkpoints_raw) == 0:
            print("   No hi ha checkpoints marcats per aquesta wallet")
            return
        
        print(f"\n   {'ID':<6} {'Timestamp':<15} {'Data/Hora'}")
        print(f"   {'-'*6} {'-'*15} {'-'*30}")
        
        for i in range(0, len(checkpoints_raw), 2):
            cp_id = int(checkpoints_raw[i], 16)
            timestamp = int(checkpoints_raw[i+1], 16)
            date_str = format_timestamp(timestamp)
            print(f"   {cp_id:<6} {timestamp:<15} {date_str}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def list_all_wallets():
    """List all wallets with checkpoints"""
    print(f"\n👥 Consultant totes les wallets amb checkpoints...")
    
    cmd = [
        "mxpy", "contract", "query", CONTRACT_ADDRESS,
        "--function=getAllWallets",
        f"--proxy={PROXY}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return
        
        wallets_raw = json.loads(result.stdout.strip())
        
        if len(wallets_raw) == 0:
            print("   No hi ha wallets amb checkpoints")
            return
        
        print(f"\n{'='*80}")
        print(f"RESUM DE TOTES LES WALLETS")
        print(f"{'='*80}\n")
        
        # Handle concatenated hex addresses
        if len(wallets_raw) == 1:
            long_hex = wallets_raw[0]
            num_addresses = len(long_hex) // 64
            print(f"Total wallets: {num_addresses}\n")
            
            for i in range(num_addresses):
                hex_addr = long_hex[i*64:(i+1)*64]
                bech = hex_to_bech32('erd', hex_addr)
                
                print(f"Wallet {i+1}: {bech}")
                
                # Query checkpoints
                cmd2 = [
                    "mxpy", "contract", "query", CONTRACT_ADDRESS,
                    "--function=getCheckpointsFor",
                    f"--arguments=addr:{bech}",
                    f"--proxy={PROXY}"
                ]
                
                result2 = subprocess.run(cmd2, capture_output=True, text=True)
                checkpoints = json.loads(result2.stdout.strip())
                
                if len(checkpoints) == 0:
                    print("  Cap checkpoint\n")
                else:
                    print("  Checkpoints:")
                    for j in range(0, len(checkpoints), 2):
                        cp_id = int(checkpoints[j], 16)
                        timestamp = int(checkpoints[j+1], 16)
                        date_str = format_timestamp(timestamp)
                        print(f"    • ID {cp_id:2d} - {date_str}")
                    print()
        else:
            for idx, hex_addr in enumerate(wallets_raw, 1):
                print(f"Wallet {idx}: {hex_addr}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def show_help():
    """Show usage information"""
    help_text = f"""
╔═══════════════════════════════════════════════════════════════════╗
║                  TRAILCONTROL CLI - Ajuda                         ║
╚═══════════════════════════════════════════════════════════════════╝

Contract: {CONTRACT_ADDRESS}
Proxy:    {PROXY}

COMANDES DISPONIBLES:

  1. Marcar un checkpoint:
     python trail_control_cli.py mark <pem_file> <checkpoint_id>
     
     Exemple:
       python trail_control_cli.py mark ../walletg.pem 5

  2. Consultar checkpoints d'una wallet:
     python trail_control_cli.py query <address>
     
     Exemple:
       python trail_control_cli.py query erd1d8sf28qdes9rjj2rkpvndydanc9n24xsnldnls9gqpy6km3xaflszh8a6c

  3. Consultar checkpoints des d'un fitxer PEM:
     python trail_control_cli.py query-pem <pem_file>
     
     Exemple:
       python trail_control_cli.py query-pem ../corredor1.pem

  4. Llistar totes les wallets amb checkpoints:
     python trail_control_cli.py list
     
     Exemple:
       python trail_control_cli.py list

  5. Mostrar aquesta ajuda:
     python trail_control_cli.py help

═══════════════════════════════════════════════════════════════════

FITXERS PEM DISPONIBLES:
  ../walletg.pem
  ../corredor1.pem
  ../corredor2.pem

"""
    print(help_text)

def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == "help" or command == "--help" or command == "-h":
        show_help()
    
    elif command == "mark":
        if len(sys.argv) < 4:
            print("❌ Error: Falten arguments")
            print("Usage: python trail_control_cli.py mark <pem_file> <checkpoint_id>")
            sys.exit(1)
        
        pem_path = sys.argv[2]
        checkpoint_id = sys.argv[3]
        mark_checkpoint(pem_path, checkpoint_id)
    
    elif command == "query":
        if len(sys.argv) < 3:
            print("❌ Error: Falta l'adreça")
            print("Usage: python trail_control_cli.py query <address>")
            sys.exit(1)
        
        address = sys.argv[2]
        query_checkpoints(address)
    
    elif command == "query-pem":
        if len(sys.argv) < 3:
            print("❌ Error: Falta el fitxer PEM")
            print("Usage: python trail_control_cli.py query-pem <pem_file>")
            sys.exit(1)
        
        pem_path = sys.argv[2]
        if not Path(pem_path).exists():
            print(f"❌ Error: Fitxer PEM no trobat: {pem_path}")
            sys.exit(1)
        
        address = get_address_from_pem(pem_path)
        query_checkpoints(address)
    
    elif command == "list":
        list_all_wallets()
    
    else:
        print(f"❌ Comanda desconeguda: {command}")
        print("Executa 'python trail_control_cli.py help' per veure les comandes disponibles")
        sys.exit(1)

if __name__ == "__main__":
    main()
