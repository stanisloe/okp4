### Gas consumption analyses script
To use this script pass the required variables like in example below
```
export EXECUTIONS_NUMBER=10 && \
export EXECUTION_PARALLELISM=1 && \
export BINARY_PATH="" && \
export WALLET_NAME="" && \
export ADMIN_ADDRESS="" && \
export OBJECTARIUM_ADDRESS="" && \
export LAW_STONE_ADDRESS=""
export RPC="" && \
export WALLET_PASSPHRASE="" && \
export FEES="2500uknow"
```
and run the following command `python3 gas_consumption.py`

Program assumes is that you have already created objectarium and law stone contracts.
The output will be a csv with all the operation names and their corresponding gas usage.

You can change how many times script is executed and increase execution parallelism by changing
corresponding parameters. The default ones will execute 10 times in 1 thread.