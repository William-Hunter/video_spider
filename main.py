#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import json
import time
import bilibili
import youtube
import sys
import util


def loopYT(user_list,check_type):
    for user_name in user_list:
        if user_name is None or ""==user_name:
            continue

        user = user_list[user_name]
        try:
            if (check_type == user['check']):
                print('\n\n',user_name)
                response_str = youtube.postList(user['uid'])
                
                user['last5download']=youtube.parseListByTitle(
                    response_str, user['_type'], user['folder'], user['last5download'], testMode)

                # generate a new time stamp and save to file
                user['last_update'] = util.stamp2date(time.time())
                
        except Exception as err:
            print(f"異常賬戶：{user_name},Unexpected {err=}, {type(err)=}")
            # exit(1)

        user_list[user_name] = user

if __name__ == "__main__":
    testMode = False
    # testMode=True

    task = "bilibili"
    if len(sys.argv) > 1:
        task = sys.argv[1]

    check_type = "daily"
    if len(sys.argv) > 2:
        check_type = sys.argv[2]     # hourly    daily     weekly      monthly

    now = util.stamp2date(time.time())
    print(now+"----------------------------------------------------------------------")

    stamp_path = "/opt/workspace/video_spider/{}_list.json".format(task)
    # readJson(stamp_path)
    user_list = util.readJson(stamp_path)

    if "bilibili" == task:
        bilibili.loopBB(user_list,check_type,testMode)
        pass
    elif "youtube" == task:
        loopYT(user_list,check_type)
        pass

    util.writeJson(stamp_path, user_list)
