import os
import subprocess
import json
import uuid
import csv
import concurrent.futures

EXECUTIONS_NUMBER = int(os.environ['EXECUTIONS_NUMBER'])
EXECUTION_PARALLELISM = int(os.environ['EXECUTION_PARALLELISM'])
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


    def to_dict(self):
        return {'operation_name': self.operation_name, 'gas_wanted': self.gas_wanted, 'gas_used': self.gas_used}


def execute(command, operation_name):
    error_tx = TransactionInfo('N/A', 'N/A', 'N/A', 'N/A')
    try:
        result = subprocess.check_output(command, shell=True).decode('utf-8')
    except Exception:
        return error_tx

    result_json = json.loads(result)
    if result_json.get('code', 0) == 0:
        gas_used = result_json['gas_used'] if 'gas_used' in result_json else result_json['data']['gas_used']
        return TransactionInfo(operation_name, result_json.get('gas_wanted', 'N/A'), gas_used, result)
    else:
        # if there was an error - ignore such transaction
        return error_tx



def get_objectarium_object_id(store_response):
    parsed_data = json.loads(store_response)
    for log in parsed_data['logs']:
        for event in log['events']:
            for attr in event['attributes']:
                if attr['key'] == 'id':
                    id_value = attr['value']
                    return id_value


def execute_transactions():
    tx_info_array = []
    for i in range(EXECUTIONS_NUMBER):
        store_response = execute(OBJECTARIUM_STORE_TEMPLATE.format(data=uuid.uuid4()), 'store_object')
        if store_response.operation_name != 'N/A':
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
    return tx_info_array


if __name__ == '__main__':
    tx_info_array = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i in range(EXECUTION_PARALLELISM):
            futures.append(executor.submit(execute_transactions))
        for future in concurrent.futures.as_completed(futures):
            tx_info_array.extend(future.result())


    with open('report.csv', mode='w') as csv_file:
        writer = csv.writer(csv_file)
        for tx_info in tx_info_array:
            print(tx_info.to_dict())
            if tx_info.operation_name == 'N/A':
                continue
            tx_dict = tx_info.to_dict()
            writer.writerow(tx_dict.keys())
            writer.writerow(tx_dict.values())