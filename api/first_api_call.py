import requests

tip_hash = requests.get("https://blockstream.info/api/blocks/tip/hash", timeout=15).text.strip()
block = requests.get(f"https://blockstream.info/api/block/{tip_hash}", timeout=15).json()
print("height:", block["height"])
print("hash:", block["id"])
print("difficulty:", block["difficulty"])
print("nonce:", block["nonce"])
print("tx_count:", block["tx_count"])
# Observation: valid Bitcoin block hashes usually start with many leading zeros because PoW requires the hash to stay below a target.
# Observation: the bits field stores that target in compact form, so it connects directly to the mining threshold seen in class.
