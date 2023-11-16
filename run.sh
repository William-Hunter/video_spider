#!/bin/bash


if [ "youtube" == "$1" ]; then
    # /opt/setproxy.sh
    export http_proxy=http://127.0.0.1:7890 && export https_proxy=http://127.0.0.1:7890 && echo 'proxy is on!'
fi


/usr/bin/python3 /opt/workspace/video_spider/main.py $1 $2 \
>> /opt/workspace/video_spider/log

