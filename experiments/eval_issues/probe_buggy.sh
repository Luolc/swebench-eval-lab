#!/bin/bash
# Simulates the entryscript line that build_entryscript currently generates.
# The run_script.sh receives a "receiver" script that just prints its $1 arg.
bash /workspace/receiver.sh TestMalformedOpMsg/empty_$db_key,TestMalformedOpMsg/invalid_$db_value,TestMalformedOpMsg/missing_$db_key
