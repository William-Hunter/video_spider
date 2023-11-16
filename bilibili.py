#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import requests
import json
import time
import subprocess
import sys
import util

from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(10)


def postList(url):
    HEADERS = {
        "Origin":"https://space.bilibili.com"
        ,"Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8"
        ,"Connection":"keep-alive"
        ,"Accept-Encoding":"gzip, deflate, br"
        ,"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        ,'Pragma': "no-cache"
        ,"Dnt":"1"
        ,"Sec-Ch-Ua-Platform":"\"Windows\""
        ,"Cookie":"buvid3=9B7B3A65-EBCB-3512-C5DB-FE9C0D79953148828infoc; blackside_state=0; LIVE_BUVID=AUTO8616305842136855; i-wanna-go-back=-1; buvid_fp_plain=undefined; buvid4=BBC573A6-FFFF-01DE-34D5-0A58B09748BE07073-022012613-PV2QRDcpwMmxOM3/YhwP5A%3D%3D; rpdid=|(J|YukYu))u0J'uYYmJlk~JJ; b_ut=5; home_feed_column=4; hit-new-style-dyn=1; CURRENT_PID=acbe5b90-cd69-11ed-8c76-613c48d24333; nostalgia_conf=-1; hit-dyn-v2=1; CURRENT_FNVAL=4048; FEED_LIVE_VERSION=V8; header_theme_version=CLOSE; browser_resolution=1010-692; DedeUserID=44827547; DedeUserID__ckMd5=7a9862031f0f805a; fingerprint=0bc9c2714128b1cf5e9a4a40336c5e5d; PVID=1; _uuid=C54149110-24AA-C38C-5FF5-883BBB3542AD40105infoc; buvid_fp=0bc9c2714128b1cf5e9a4a40336c5e5d; b_nut=100; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTY2MDY5MDgsImlhdCI6MTY5NjM0NzY0OCwicGx0IjotMX0.grCC6MnZ-atOJJMOP8EZ0SAqn0QJPrQT4GsG84az364; bili_ticket_expires=1696606848; SESSDATA=f49e6c29%2C1711899731%2Cbdf30%2Aa1CjCugp2op9Jw0XCn8IGsRLMd_eiySps77gkdRLTFURHkkUQzpezl_88LsFc_H03bK3kSVmNwb2ZHNl9zemNJZGRwd2htM0dDTlluSHl0RzFWZjNmYVFDYWpfVkFWb0hTeXJWWUFlZ2RoNjltNGVZOGhTMU9QUmlrdGtPMjFIa1BTNE5uTkhBTkRnIIEC; bili_jct=558e12885b1101c8280002efcbdadd08; sid=6odipx96; b_lsid=3FFA29CC_18AF8785F0E; bsource=search_google; bp_video_offset_44827547=848264467707854887"
        ,"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        }

    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        response = json.loads(response.text)
        return response
    else:
        print(response.status_code, response.text)
        return {'code': 500}


def parseList(response, last_timestamp, _type, folder, testMode=False):
    # print(response)
    try:
        for video in response['data']['list']['vlist']:
            # print("video",video)
            timestampp = video['created']            
            if timestampp > int(last_timestamp)-60:     #时间向前推1分钟
                video_url = "https://www.bilibili.com/video/{bid}/".format(
                    bid=video['bvid'])
                show_time = time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.localtime(timestampp))
                print(video['title'],"|", show_time)
                if not testMode:
                    print("download:",video_url)
                    download(video_url, _type, folder)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise Exception(f"解析異常 \n {err=} \n {response=}")


def download(url, _type, folder):
    bbdown_base = "/opt/workspace/flask/ytdlpmod/BBdown"
    if "mp3" == str(_type):
        executor.submit(
            run_cmds, [bbdown_base+"/audio.sh", str(url), str(folder)])
    else:
        executor.submit(
            run_cmds, [bbdown_base+"/video.sh", str(url), str(folder)])


def run_cmds(cmds):
    print("开始执行终端命令")
    print(cmds)
    p = subprocess.Popen(cmds)
    # print(p)
    return_code = p.wait()
    print("终端命令执行完毕")


def repeat_call(full_url, repeat_time=0):
    response = postList(full_url)  
    count = 1
    refresh=False
    while ('code' in response and not 0 == response['code'] and count <= repeat_time):
        print(response)
        refresh=True
        response = postList(full_url)  # python_honor
        count += 1

    return response,refresh


def loopBB(user_list,check_type,testMode):
    for user_name in user_list:
        if user_name is None or ""==user_name:
            continue

        user = user_list[user_name]

        if True == user['disable']:
            continue

       # print(portal,task)
        try:
            # if ("" != user['check']):
            print(user_name)
            response_str,refresh = repeat_call(user['info']['full_url'])

            parseList(response_str, util.date2stamp(
                user['last_update']), user['_type'], user['folder'], testMode)

            # generate a new time stamp and save to file
            user['last_update'] = util.stamp2date(time.time())
            user['info']['refresh'] =refresh
                
        except Exception as err:
            print(f"異常賬戶：{user_name},Unexpected {err=}, {type(err)=}")
            # exit(1)
            user['info']['refresh'] =True

        user_list[user_name] = user

        time.sleep(20)

if __name__ == "__main__":
    # repeat_time = 8
    testMode = False
    # testMode=True
    
    username = '不姓白了'
    uid = '22836703'
    full_url="https://api.bilibili.com/x/space/wbi/arc/search?mid=1724598&ps=30&tid=0&pn=1&keyword=&order=pubdate&platform=web&web_location=1550101&order_avoided=true&w_rid=ff814b94f8a2c28f551c4e4a913c8fe2&wts=1696348198"
    last_time = "2023-10-02 00:11:01"
    media_type = 'mp4'

    response,refresh= repeat_call(full_url)
    print("response:",response)

    # parseList(response, util.date2stamp(last_time), media_type, username, testMode)

    # print("refresh:",refresh)


