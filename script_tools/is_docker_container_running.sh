set -x
result=`docker ps | grep "$1"`
if [ $? != 0 ]; then
    echo "nope"
    exit -1
else
  echo "yea"
fi
