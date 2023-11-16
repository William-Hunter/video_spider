#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import requests
import json
import time
import subprocess
import util

from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(10)


def postList(uid):
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"

    HEADERS = {'user-agent': user_agent}

    url = "https://www.googleapis.com/youtube/v3/search"

    config=util.readJson("/opt/workspace/video_spider/config.json")
    
    print("JSON")

    payload = {
        "key": config['prod']['youtube']['key'],
        "part": "snippet",
        "channelId": uid,
        "maxResults": "5",
        "order": "date",
        "type": "video"
    }

    print(payload)

    response = requests.get(url, params=payload, headers=HEADERS)

    if response.status_code == 200:
        response = json.loads(response.text)
        return response
    else:
        print(response.status_code, response.text)
        return {}


def parseList(response, last_timestamp, _type, folder, testMode=False):
    #    print(response)
    try:
        for video in response['items']:
            if 'videoId' not in video['id']:
                print("没有video,跳过")
                continue  #

            videoID = video['id']['videoId']
            title = video['snippet']['title']
            publishedAt = video['snippet']['publishedAt'].replace(
                "Z", "").replace("T", " ")

            if 'upcoming' == video['snippet']['liveBroadcastContent']:
                print("未上映视频,跳过")
                continue
#            print(publishedAt,title,videoID,"\n")

            timestampp = int(util.date2stamp(publishedAt))
            if timestampp > int(last_timestamp):
                video_url = "https://www.youtube.com/watch?v={videoID}".format(
                    videoID=videoID)
                print(video_url, title, publishedAt, "\n")
                if not testMode:
                    download(video_url, _type, folder)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise Exception(f"解析異常 \n {err=} \n {response=}")


def parseListByTitle(response, _type, folder, last_title=[], testMode=False):
    #    print(response)
    try:
        for video in response['items']:

            title = video['snippet']['title']
            if 'upcoming' == video['snippet']['liveBroadcastContent']:
                print("upcoming\t",title)
                continue

            if 'videoId' not in video['id']:
                print("没有videoID,跳过\t",title)
                continue  #
            videoID = video['id']['videoId']

            if title in last_title:
                print("in list\t",title)
                continue  # already download
            else:
                video_url = "https://www.youtube.com/watch?v={videoID}".format(
                    videoID=videoID)
                if not testMode:
                    print("download\t",video_url, title)
                    download(video_url, _type, folder)
                    last_title.append(title)

    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise Exception(f"解析異常 \n {err=} \n {response=}")

    return last_title


def download(url, _type, user_name):
    shell_path = "/opt/workspace/flask/ytdlpmod/download.sh"
    executor.submit(run_cmds, [shell_path, str(url),
                    str(_type), str(user_name)])


def run_cmds(cmds):
    print("开始执行终端命令")
    print(cmds)
    p = subprocess.Popen(cmds)
    # print(p)
    return_code = p.wait()
    print("终端命令执行完毕")


if __name__ == "__main__":
    testMode = False
    # testMode=True
    media_type = 'mp4'

    uid = 'UCiL5EGUQfROCmRokN2q1LCg'
    username = '徐某人'
    last_time = "2023-05-18 00:00:00"

    response = postList(uid)
    lists = parseListByTitle(response,  media_type, "", [], testMode)
    print("-------------------------------")
    print(lists)
