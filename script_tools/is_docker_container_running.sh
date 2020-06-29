result=`docker ps | grep "$1"`
if [ $? != 0 ]; then
    echo "container is NOT running"
    exit -1
else
  echo "container IS running"
fi
