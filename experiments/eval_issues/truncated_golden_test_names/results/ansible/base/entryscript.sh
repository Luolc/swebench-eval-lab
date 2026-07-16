cd /app
git reset --hard a1730af91f94552e8aaff4bedfb8dcae00bd284d
git checkout a1730af91f94552e8aaff4bedfb8dcae00bd284d
git checkout de5858f48dc9e1ce9117034e0d7e76806f420ca8 -- test/integration/targets/ansible-galaxy-collection/library/setup_collections.py test/integration/targets/ansible-galaxy-collection/tasks/install.yml test/integration/targets/ansible-galaxy-collection/tasks/main.yml test/integration/targets/ansible-galaxy-collection/vars/main.yml test/units/galaxy/test_api.py
bash /workspace/run_script.sh test/integration/targets/ansible-galaxy-collection/library/setup_collections.py,test/units/galaxy/test_api.py > /workspace/stdout.log 2> /workspace/stderr.log
python /workspace/parser.py /workspace/stdout.log /workspace/stderr.log /workspace/output.json
