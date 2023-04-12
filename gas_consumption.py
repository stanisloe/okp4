import os
import subprocess


BINARY_PATH = os.environ['BINARY_PATH']
WALLET_NAME = os.environ['WALLET_NAME']
WALLET_PASSPHRASE = os.environ['WALLET_PASSPHRASE']
ADMIN_ADDRESS = os.environ['ADMIN_ADDRESS']
FEES=os.environ['FEES']
RPC = os.environ['RPC']
OBJECTARIUM_ADDRESS=os.environ['OBJECTARIUM_ADDRESS']
LAW_STONE_ADDRESS=os.environ['LAW_STONE_ADDRESS']



PASSPHRASE_PREFIX=f"yes \"{WALLET_PASSPHRASE}\" | "
DEFAULT_FLAGS="" \
    f"--gas 1000000 " \
    f"--node {RPC} " \
    f"--fees {FEES} " \
    "--chain-id okp4-nemeton-1 " \
    "-y"

OBJECTARIUM_STORE = f"{PASSPHRASE_PREFIX}" \
    f"{BINARY_PATH} tx wasm execute {OBJECTARIUM_ADDRESS} " \
    f"--from {WALLET_NAME} " \
    "--broadcast-mode block " \
    "\"{\\\"store_object\\\":{\\\"data\\\": \\\"aGVsbG8K\\\",\\\"pin\\\":true}}\" " \
    f"{DEFAULT_FLAGS}"

if __name__ == '__main__':
    result = subprocess.check_output(OBJECTARIUM_STORE, shell=True)
    print(result.decode('utf-8'))
