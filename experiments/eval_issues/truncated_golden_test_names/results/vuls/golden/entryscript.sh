cd /app
git reset --hard 6fca8d97c145fbe50a247dd222947a240639fd50
git checkout 6fca8d97c145fbe50a247dd222947a240639fd50
git apply -v /workspace/patch.diff
git checkout bff6b7552370b55ff76d474860eead4ab5de785a -- scanner/redhatbase_test.go
bash /workspace/run_script.sh 'Test_redhatBase_parseUpdatablePacksLines/amazon,Test_redhatBase_parseUpdatablePacksLine,Test_redhatBase_parseUpdatablePacksLine/centos_7.0:_"shadow-utils"_"2"_"4.1.5.1_24.el7"_"rhui-REGION-rhel-server-releases",Test_redhatBase_parseUpdatablePacksLines,Test_redhatBase_parseUpdatablePacksLines/centos,Test_redhatBase_parseUpdatablePacksLine/amazon_2023:_Is_this_ok_[y/N]:_"dnf"_"0"_"4.14.0"_"1.amzn2023.0.6"_"amazonlinux",Test_redhatBase_parseUpdatablePacksLine/centos_7.0:_"zlib"_"0"_"1.2.7"_"17.el7"_"rhui-REGION-rhel-server-releases"' > /workspace/stdout.log 2> /workspace/stderr.log
python /workspace/parser.py /workspace/stdout.log /workspace/stderr.log /workspace/output.json
