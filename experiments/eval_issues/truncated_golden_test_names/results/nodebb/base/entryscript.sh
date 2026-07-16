cd /app
git reset --hard ae3fa85f40db0dca83d19dda1afb96064dffcc83
git checkout ae3fa85f40db0dca83d19dda1afb96064dffcc83
git checkout 00c70ce7b0541cfc94afe567921d7668cdc8f4ac -- test/mocks/databasemock.js test/socket.io.js test/user.js
bash /workspace/run_script.sh test/mocks/databasemock.js,test/translator.js,test/user.js,test/socket.io.js,test/database.js,test/meta.js > /workspace/stdout.log 2> /workspace/stderr.log
python /workspace/parser.py /workspace/stdout.log /workspace/stderr.log /workspace/output.json
