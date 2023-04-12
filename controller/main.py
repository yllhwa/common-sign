from fastapi import FastAPI, Form
import time
from fastapi_socketio import SocketManager
import json

app = FastAPI()
socket_manager = SocketManager(app=app)


@app.get("/")
async def root():
    return {"message": "Hello World"}

latest_url = {
    "url": "",
    "time": 0
}


@app.sio.on("disconnect")
async def on_disconnect():
    pass


@app.sio.on('get_latest')
async def handle_join(sid, *args, **kwargs):
    global latest_url
    await socket_manager.emit('latest_url', json.dumps(latest_url), room=sid)


@app.post("/upload")
async def upload_url(url: str = Form()):
    global latest_url
    latest_url = {
        'url': url,
        'time': time.time()
    }
    # 广播
    await socket_manager.emit('new_url', json.dumps(latest_url))
    return {"message": "success"}


def main():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8248)


main()
