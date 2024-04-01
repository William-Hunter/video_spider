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


cookie=open("/opt/workspace/video_spider/bilibili_cookie.txt").read()

def postList(url):
    global cookie

    HEADERS = {
        "Origin":"https://space.bilibili.com"
        ,"Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8"
        ,"Connection":"keep-alive"
        ,"Accept-Encoding":"gzip, deflate, br"
        ,"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        ,'Pragma': "no-cache"
        ,"Dnt":"1"
        ,"Sec-Ch-Ua-Platform":"\"Windows\""
        ,"Cookie":cookie
        ,"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

#    print("cookie:",cookie)
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
                print("video_url:",video_url)
                if not testMode:
                    print("download:"+video['title'])
                    download(video_url, _type, folder)
                    time.sleep(10)##每次下载都睡眠
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

    if 0 == response['code']:
        refresh=False
    else:
        refresh=True

    while ('code' in response and not 0 == response['code'] and count <= repeat_time):
        time.sleep(10)
        print(response)
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

        time.sleep(10)

        now = util.stamp2date(time.time())
        print(now)


if __name__ == "__main__":
    # repeat_time = 8
    # testMode = False
    testMode=True
    
    username = 'CRAZY262'
    uid = '324879'
    full_url="https://api.bilibili.com/x/space/wbi/arc/search?mid=324879&ps=30&tid=0&special_type=&pn=1&keyword=&order=pubdate&platform=web&web_location=1550101&order_avoided=true&dm_img_list=[%7B%22x%22:2228,%22y%22:1123,%22z%22:0,%22timestamp%22:8231731,%22type%22:0%7D,%7B%22x%22:2227,%22y%22:1251,%22z%22:26,%22timestamp%22:8231831,%22type%22:0%7D,%7B%22x%22:2349,%22y%22:1243,%22z%22:124,%22timestamp%22:8231931,%22type%22:0%7D,%7B%22x%22:2323,%22y%22:1217,%22z%22:98,%22timestamp%22:8232062,%22type%22:0%7D,%7B%22x%22:2427,%22y%22:1341,%22z%22:211,%22timestamp%22:8232163,%22type%22:0%7D,%7B%22x%22:2392,%22y%22:1299,%22z%22:174,%22timestamp%22:8232265,%22type%22:0%7D,%7B%22x%22:2781,%22y%22:1675,%22z%22:556,%22timestamp%22:8232365,%22type%22:0%7D,%7B%22x%22:2904,%22y%22:1798,%22z%22:679,%22timestamp%22:8232465,%22type%22:0%7D,%7B%22x%22:2229,%22y%22:1124,%22z%22:1,%22timestamp%22:8242006,%22type%22:0%7D,%7B%22x%22:2239,%22y%22:1134,%22z%22:11,%22timestamp%22:8242107,%22type%22:0%7D,%7B%22x%22:3167,%22y%22:2136,%22z%22:832,%22timestamp%22:8242208,%22type%22:0%7D,%7B%22x%22:3039,%22y%22:1957,%22z%22:742,%22timestamp%22:8242309,%22type%22:0%7D,%7B%22x%22:2483,%22y%22:1378,%22z%22:255,%22timestamp%22:8242410,%22type%22:0%7D,%7B%22x%22:3374,%22y%22:2275,%22z%22:1128,%22timestamp%22:8242510,%22type%22:0%7D,%7B%22x%22:2378,%22y%22:1596,%22z%22:676,%22timestamp%22:8242613,%22type%22:0%7D,%7B%22x%22:2675,%22y%22:1922,%22z%22:725,%22timestamp%22:8242713,%22type%22:0%7D,%7B%22x%22:2863,%22y%22:2049,%22z%22:774,%22timestamp%22:8242813,%22type%22:0%7D,%7B%22x%22:4029,%22y%22:3069,%22z%22:1619,%22timestamp%22:8242913,%22type%22:0%7D,%7B%22x%22:4402,%22y%22:3429,%22z%22:1962,%22timestamp%22:8243013,%22type%22:0%7D,%7B%22x%22:2922,%22y%22:1949,%22z%22:482,%22timestamp%22:8243117,%22type%22:1%7D,%7B%22x%22:4255,%22y%22:3282,%22z%22:1815,%22timestamp%22:8245442,%22type%22:0%7D,%7B%22x%22:5126,%22y%22:2600,%22z%22:1940,%22timestamp%22:8248387,%22type%22:0%7D,%7B%22x%22:4987,%22y%22:2830,%22z%22:1913,%22timestamp%22:8248492,%22type%22:0%7D,%7B%22x%22:4471,%22y%22:2314,%22z%22:1397,%22timestamp%22:8248593,%22type%22:0%7D,%7B%22x%22:3848,%22y%22:2551,%22z%22:1069,%22timestamp%22:8248695,%22type%22:0%7D,%7B%22x%22:3826,%22y%22:2648,%22z%22:1104,%22timestamp%22:8248795,%22type%22:0%7D,%7B%22x%22:5134,%22y%22:3984,%22z%22:2420,%22timestamp%22:8248908,%22type%22:0%7D,%7B%22x%22:4814,%22y%22:3841,%22z%22:2167,%22timestamp%22:8249010,%22type%22:0%7D,%7B%22x%22:4112,%22y%22:3201,%22z%22:1486,%22timestamp%22:8249111,%22type%22:0%7D,%7B%22x%22:4064,%22y%22:3166,%22z%22:1445,%22timestamp%22:8249253,%22type%22:0%7D,%7B%22x%22:3203,%22y%22:2503,%22z%22:772,%22timestamp%22:8249447,%22type%22:0%7D,%7B%22x%22:3184,%22y%22:2484,%22z%22:753,%22timestamp%22:8249552,%22type%22:0%7D,%7B%22x%22:5060,%22y%22:4403,%22z%22:2638,%22timestamp%22:8249940,%22type%22:0%7D,%7B%22x%22:5635,%22y%22:5168,%22z%22:3149,%22timestamp%22:8250146,%22type%22:0%7D,%7B%22x%22:5182,%22y%22:4670,%22z%22:2670,%22timestamp%22:8256292,%22type%22:0%7D,%7B%22x%22:4787,%22y%22:3883,%22z%22:2416,%22timestamp%22:8256393,%22type%22:0%7D,%7B%22x%22:2619,%22y%22:1387,%22z%22:542,%22timestamp%22:8256494,%22type%22:0%7D,%7B%22x%22:5360,%22y%22:4147,%22z%22:3295,%22timestamp%22:8256598,%22type%22:0%7D,%7B%22x%22:6318,%22y%22:5127,%22z%22:4279,%22timestamp%22:8256698,%22type%22:0%7D,%7B%22x%22:4785,%22y%22:3599,%22z%22:2754,%22timestamp%22:8256798,%22type%22:0%7D,%7B%22x%22:2046,%22y%22:860,%22z%22:15,%22timestamp%22:8256924,%22type%22:0%7D,%7B%22x%22:6501,%22y%22:5277,%22z%22:4584,%22timestamp%22:8257025,%22type%22:0%7D,%7B%22x%22:6255,%22y%22:4931,%22z%22:4431,%22timestamp%22:8257127,%22type%22:0%7D,%7B%22x%22:4716,%22y%22:3378,%22z%22:2957,%22timestamp%22:8257228,%22type%22:0%7D,%7B%22x%22:4635,%22y%22:3305,%22z%22:2898,%22timestamp%22:8257329,%22type%22:0%7D,%7B%22x%22:5551,%22y%22:4220,%22z%22:3840,%22timestamp%22:8257434,%22type%22:0%7D,%7B%22x%22:5143,%22y%22:3809,%22z%22:3441,%22timestamp%22:8257536,%22type%22:0%7D,%7B%22x%22:3198,%22y%22:1864,%22z%22:1496,%22timestamp%22:8257677,%22type%22:1%7D,%7B%22x%22:6138,%22y%22:4783,%22z%22:4453,%22timestamp%22:8257903,%22type%22:0%7D,%7B%22x%22:3563,%22y%22:2140,%22z%22:2082,%22timestamp%22:8258668,%22type%22:0%7D]&dm_img_str=V2ViR0wgMS4wIChPcGVuR0wgRVMgMi4wIENocm9taXVtKQ&dm_cover_img_str=QU5HTEUgKEludGVsIEluYy4sIEludGVsIElyaXMgT3BlbkdMIEVuZ2luZSwgT3BlbkdMIDQuMSlHb29nbGUgSW5jLiAoSW50ZWwgSW5jLi&w_rid=0e79e612a233508772b583b609240ccd&wts=1705830876"
    last_time = "2023-12-07 16:11:01"
    media_type = 'mp4'

    response,refresh= repeat_call(full_url)
    # print("response:",response)
    # print("refresh:",refresh)

    parseList(response, util.date2stamp(last_time), media_type, username, testMode)



