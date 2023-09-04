# 0.安装

```bash
pip install -r requirements.txt
```

# 1.配置

修改config.demo.py为config.py，并修改其中的配置项
WS_SERVER为签到服务器地址。

```python
users = [("手机号", "密码", "姓名"), ("手机号", "密码", "姓名")]
WS_SERVER = "https://sign.example.com"
```

# 2.使用

```bash
python main.py
```