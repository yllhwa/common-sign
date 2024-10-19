import time
import json
from fastapi import FastAPI, Form
import socketio

app = FastAPI()

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins ='*')
combined_asgi_app = socketio.ASGIApp(sio, app, socketio_path="/ws/socket.io")


@app.get("/")
async def root():
    return {"message": "Hello World"}


latest_url = {"url": "", "time": 0}


@sio.on("get_latest")
async def handle_join(sid, *args, **kwargs):
    global latest_url
    await sio.emit("latest_url", json.dumps(latest_url), room=sid)


@app.post("/upload")
async def upload_url(url: str = Form()):
    global latest_url
    latest_url = {"url": url, "time": time.time()}
    # 广播
    await sio.emit("new_url", json.dumps(latest_url))
    return {"message": "success"}


def main():
    import uvicorn

    uvicorn.run(combined_asgi_app, host="0.0.0.0", port=7001)


if __name__ == "__main__":
    main()
