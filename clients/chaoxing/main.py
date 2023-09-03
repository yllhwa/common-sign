import socketio
import requests
import json
import time
from config import WS_SERVER
from selenium import webdriver
from selenium.webdriver.common.by import By

sio = socketio.Client()


@sio.event
def connect():
    print('connection established')


@sio.event
def latest_url(data):
    print('latest_url received with ', data)


def QrSign_simulate(name, cookies, url):
    # 使用 http替换 https
    if url.startswith("https://"):
        url = url.replace("https://", "http://")
    # driver配置
    options = webdriver.EdgeOptions()
    options.add_argument("--host=mobilelearn.chaoxing.com")
    options.add_argument("--connection=keep-alive")
    options.add_argument('--user-agent="Mozilla/5.0 (Linux; Android 13; 23049RAD8C Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/108.0.5359.128 Mobile Safari/537.36(schild:20fef079a368fe6417cdfa5535fe4472) (device:23049RAD8C) Language/zh_CN com.chaoxing.mobile/ChaoXingStudy_3_6.1.5_android_phone_911_103 (@Kalimdor)_0adde70add184d7a9ba90c9262d78643"')
    options.add_argument("--x-requested-with=com.chaoxing.mobile")
    options.add_argument('-ignore-certificate-errors')
    options.add_argument('-ignore -ssl-errors')
    # 无头模式
    options.add_argument('--headless')
    driver = webdriver.Edge(options=options)
    
    # 等待页面加载
    driver.implicitly_wait(10)

    # 打开签到页面
    driver.get(url)
    # 方法一：添加cookie(暂时不可用)
    # cookies = dict([l.split("=", 1) for l in cookies.split("; ")]) 
    # for k,v  in cookies.items():
    #     driver.add_cookie({
    #         "name": k,
    #         "value": v,
    #         "domain": ".chaoxing.com",
    #         "path": "/"
    #     })

    # 方法二：使用账号密码登录
    # 输入账号密码
    driver.find_element(By.ID, "phone").send_keys("")
    driver.find_element(By.ID, "pwd").send_keys("")
    # 点击登录按钮
    driver.find_element(By.CLASS_NAME, "btn-big-blue").click()
    time.sleep(1)
    # 跳转到最终页面
    sign_jscode = """
    var rcode = $("#rcode").val();
    console.log("rcode=="+rcode);
    if(rcode){
        var data = {message:"",cancelFlag:0};
        data.message = rcode;
        sacn_callback(data);
    }else{
        qiandao();
    }
    """
    # 完成签到
    driver.execute_script(sign_jscode)
    time.sleep(1)


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
            # QrSign(cookie['name'], cookie['cookie'], data['url'])
            QrSign_simulate(cookie['name'], cookie['cookie'], data['url'])
        except Exception as e:
            print(e)


@sio.event
def disconnect():
    print('disconnected from server')


sio.connect(WS_SERVER, socketio_path='/ws/socket.io')


sio.emit('get_latest')
sio.wait()
