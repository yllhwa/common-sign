import requests
import json
from config import users

try:
    with open('cookies.json', 'r', encoding='utf-8') as f:
        cookies = json.load(f)
except FileNotFoundError:
    cookies = {}

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 9 Build/QKQ1.190825.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Referer": "http://i.mooc.chaoxing.com/space/index"
}


for user in users:
    if user[0] not in cookies:
        cookies[user[0]] = {"cookie": "", "name": user[2]}
    if cookies[user[0]].get("cookie") != "":
        try:
            # 检验 cookie 是否有效
            r = requests.get("https://passport2.chaoxing.com/mooc/getAccountMessage", headers={
                "Cookie": cookies[user[0]].get("cookie"),
                **headers
            })
            if r.status_code == 200:
                print(f"用户 {user[0]} cookie 有效")
                continue
        except:
            pass
    try:
        # 登录
        r = requests.get(
            f"https://passport2-api.chaoxing.com/v11/loginregister?code={user[1]}&cx_xxt_passport=json&uname={user[0]}&loginType=1&roleSelect=true", headers=headers)
        if r.json().get("status") != True:
            print(f"用户 {user[0]} 登录失败")
            continue
        cookies[user[0]]["cookie"] = r.headers["Set-Cookie"]
        print(f"用户 {user[0]} 登录成功")
        r = requests.get("https://sso.chaoxing.com/apis/login/userLogin4Uname.do", headers={
            "Cookie": cookies[user[0]].get("cookie"),
            **headers
        })
        # 补充 cookies
        cookies[user[0]]["cookie"] += r.headers["Set-Cookie"]
        print(f"用户 {user[0]} cookie2 获取成功")
    except:
        print(f"用户 {user[0]} 登录失败")
        continue

with open('cookies.json', 'w', encoding='utf-8') as f:
    json.dump(cookies, f, ensure_ascii=False)
