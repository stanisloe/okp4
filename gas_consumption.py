import os
import subprocess
import json
import uuid
import array


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
    f"--node {RPC} " \
    f"--output json " \
    "--chain-id okp4-nemeton-1 "


OBJECTARIUM_STORE_TEMPLATE = f"{PASSPHRASE_PREFIX}" \
    f"{BINARY_PATH} tx wasm execute {OBJECTARIUM_ADDRESS} " \
    f"--from {WALLET_NAME} " \
    "--broadcast-mode block " \
    "\"{{\\\"store_object\\\":{{\\\"data\\\": \\\"$(echo {data} | base64)\\\",\\\"pin\\\":true}}}}\" " \
    f"{DEFAULT_FLAGS} " \
    f"--gas 1000000 " \
    f"--fees 2500uknow " \
    f"-y"

OBJECTARIUM_PIN_OBJECT_TEMPLATE = f"{PASSPHRASE_PREFIX}" \
    f"{BINARY_PATH} tx wasm execute {OBJECTARIUM_ADDRESS} " \
    f"--from {WALLET_NAME} " \
    "--broadcast-mode block " \
    "\"{{\\\"pin_object\\\":{{\\\"id\\\": \\\"{object_id}\\\"}}}}\" " \
    f"{DEFAULT_FLAGS} " \
    f"--gas 1000000 " \
    f"--fees 2500uknow " \
    f"-y"

OBJECTARIUM_UNPIN_OBJECT_TEMPLATE = f"{PASSPHRASE_PREFIX}" \
    f"{BINARY_PATH} tx wasm execute {OBJECTARIUM_ADDRESS} " \
    f"--from {WALLET_NAME} " \
    "--broadcast-mode block " \
    "\"{{\\\"unpin_object\\\":{{\\\"id\\\": \\\"{object_id}\\\"}}}}\" " \
    f"{DEFAULT_FLAGS} " \
    f"--gas 1000000 " \
    f"--fees 2500uknow " \
    f"-y"

OBJECTARIUM_FORGET_OBJECT_TEMPLATE = f"{PASSPHRASE_PREFIX}" \
    f"{BINARY_PATH} tx wasm execute {OBJECTARIUM_ADDRESS} " \
    f"--from {WALLET_NAME} " \
    "--broadcast-mode block " \
    "\"{{\\\"forget_object\\\":{{\\\"id\\\": \\\"{object_id}\\\"}}}}\" " \
    f"{DEFAULT_FLAGS} " \
    f"--gas 1000000 " \
    f"--fees 2500uknow " \
    f"-y"


LAW_STONE_CHANGE_GOVERNANCE = f"{BINARY_PATH} query wasm contract-state smart {LAW_STONE_ADDRESS} " \
    f"\"{{\\\"ask\\\": {{\\\"query\\\": \\\"can('change_governance', 'did:key:{ADMIN_ADDRESS}').\\\"}}}}\" " \
    f"{DEFAULT_FLAGS}"


class TransactionInfo:

    def __init__(self, operation_name, gas_wanted, gas_used, raw_response):
        self.operation_name = operation_name
        self.gas_wanted = gas_wanted
        self.gas_used = gas_used
        self.raw_response = raw_response

    def __str__(self):
        return f"TransactionInfo: " \
            f"operation_name={self.operation_name}, gas_wanted={self.gas_wanted}," \
            f"gas_used={self.gas_used}, raw_response={self.raw_response}"


def execute(command, operation_name):
    result = subprocess.check_output(command, shell=True).decode('utf-8')
    result_json = json.loads(result)
    if isinstance(result_json.get('raw_log', ''), array.array):
        return TransactionInfo(operation_name, result_json.get('gas_wanted', 'N/A'), result_json['gas_used'], result)
    else:
        return TransactionInfo('N/A', 'N/A', 'N/A', result)



def get_objectarium_object_id(store_response):
    parsed_data = json.loads(store_response)
    print(parsed_data)
    for log in parsed_data['logs']:
        print(log)
        for event in log['events']:
            for attr in event['attributes']:
                if attr['key'] == 'id':
                    id_value = attr['value']
                    return id_value


if __name__ == '__main__':
    tx_info_array = []
    store_response = execute(OBJECTARIUM_STORE_TEMPLATE.format(data=uuid.uuid4()), 'store_object')
    object_id = get_objectarium_object_id(store_response.raw_response)
    tx_info_array.append(store_response)

    pin_object_response = execute(OBJECTARIUM_PIN_OBJECT_TEMPLATE.format(object_id=object_id), 'pin_object')
    tx_info_array.append(pin_object_response)
    unpin_object_response = execute(OBJECTARIUM_UNPIN_OBJECT_TEMPLATE.format(object_id=object_id), 'unpin_object')
    tx_info_array.append(unpin_object_response)
    forget_object_response = execute(OBJECTARIUM_FORGET_OBJECT_TEMPLATE.format(object_id=object_id), 'forget_object')
    tx_info_array.append(forget_object_response)
    can_change_governance_response = execute(LAW_STONE_CHANGE_GOVERNANCE, 'change_governance')
    tx_info_array.append(can_change_governance_response)

    print(tx_info_array)