import socketio
import requests
import json
from config import WS_SERVER
from refresh_cookie import refresh_cookie
from threading import Timer

sio = socketio.Client()


@sio.event
def connect():
    print('connection established')


@sio.event
def latest_url(data):
    print('latest_url received with ', data)


def QrSign(name, cookie, url):
    headers = {
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; M2007J3SC Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/96.0.4664.104 Mobile Safari/537.36 Language/zh_CN com.chaoxing.mobile/ChaoXingStudy_3_6.1.0_android_phone_906_100",
    }
    # 从 url 分离 enc、id
    enc = url.split("enc=")[1].split("&")[0]
    id = url.split("id=")[1].split("&")[0]
    # 从 cookie 分离 uid、fid
    uid = cookie.split("UID=")[1].split(";")[0]
    fid = cookie.split("fid=")[1].split(";")[0]
    # 请求 url
    res = requests.get(url, headers=headers, allow_redirects=False)
    if res.status_code == 302:
        res = requests.get(res.headers['Location'], headers=headers)
        if res.status_code == 200:
            print("预签")
        else:
            print("预签失败")
    res = requests.get(
        f"https://mobilelearn.chaoxing.com/pptSign/stuSignajax?enc={enc}&name={name}&activeId={id}&uid={uid}&clientip=&useragent=&latitude=-1&longtitude=-1&fid={fid}&appType=15", headers=headers)
    print(res.text)


@sio.event
def new_url(data):
    print('new_url received with ', data)
    data = json.loads(data)
    if not data['url'].startswith('https://mobilelearn.chaoxing.com/widget/sign'):
        return
    with open('cookies.json', 'r', encoding="utf-8") as f:
        cookies = json.load(f)
    for cookie in cookies:
        cookie = cookies[cookie]
        try:
            QrSign(cookie['name'], cookie['cookie'], data['url'])
        except Exception as e:
            print(e)


@sio.event
def disconnect():
    print('disconnected from server')


sio.connect(WS_SERVER, socketio_path='/ws/socket.io')

# 每一天刷新一次 cookie
Timer(86400, refresh_cookie).start()
sio.emit('get_latest')
sio.wait()
