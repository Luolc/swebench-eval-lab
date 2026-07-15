#!/bin/bash
# Simulates build_entryscript with shlex.quote applied.
bash /workspace/receiver.sh 'TestMalformedOpMsg/empty_$db_key,TestMalformedOpMsg/invalid_$db_value,TestMalformedOpMsg/missing_$db_key'
