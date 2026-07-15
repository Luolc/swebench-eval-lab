#!/bin/bash
echo "received: $1"
# Split on comma and print each token, as the real run_script.sh would
IFS=',' read -r -a TESTS <<< "$1"
echo "token count: ${#TESTS[@]}"
for t in "${TESTS[@]}"; do
    echo "  token: $t"
done
