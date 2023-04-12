<script setup>
import { reactive } from "vue";
import { io } from "socket.io-client";
const socket = io(import.meta.env.VITE_SOCKET_URL,
  {
    path: "/ws/socket.io",
  }
);
let lastLink = reactive({
  url: "此处应该有链接",
  time: "",
});
// socket send get_latest
socket.emit("get_latest");
// socket receive latest_link
socket.on("latest_url", (data) => {
  data = JSON.parse(data);
  lastLink.url = data.url;
  lastLink.time = data.time;
});
socket.on("new_url", (data) => {
  data = JSON.parse(data);
  lastLink.url = data.url;
  lastLink.time = data.time;
  if (lastLink.url !== "") {
    location.href = lastLink.url;
  } else {
    alert("No link found");
  }
});

class LogItem {
  constructor(msg) {
    this.msg = msg;
    this.time = new Date();
  }
}
let logs = reactive([
  new LogItem("Tring to connect server"),
]);
// 链接成功
socket.on("connect", () => {
  logs.push(
    new LogItem("Connected to server")
  )
});
// 链接失败
socket.on("error", (err) => {
  logs.push(
    new LogItem("Error: " + err)
  )
});
// 断开链接
socket.on("disconnect", () => {
  logs.push(
    new LogItem("Disconnected from server")
  )
});
// 重连
socket.on("reconnect", () => {
  logs.push(
    new LogItem("Reconnected to server")
  )
});
// 重连失败
socket.on("reconnect_failed", () => {
  logs.push(
    new LogItem("Reconnect failed")
  )
});
// 重连错误
socket.on("reconnect_error", (err) => {
  logs.push(
    new LogItem("Reconnect error: " + err)
  )
});
// 重连尝试
socket.on("reconnect_attempt", (attempt) => {
  logs.push(
    new LogItem("Reconnect attempt: " + attempt)
  )
});
// 重连中
socket.on("reconnecting", (attempt) => {
  logs.push(
    new LogItem("Reconnecting: " + attempt)
  )
});


</script>

<template>
  <div style="word-break: break-all">
    <a :href="lastLink?.url">{{ lastLink?.url || "此处应该有链接" }}</a>
    <div>{{ new Date(lastLink?.time * 1000).toLocaleString() }}</div>
  </div>
  <div class="log">
    <div v-for="log in logs" :key="log">
      <div>{{ log?.time.toLocaleTimeString() }} - {{ log?.msg }}</div>
    </div>
  </div>
</template>

<style scoped>
.log {
  /* word-break: break-all; */
  text-align: left;
  max-height: 80vh;
  overflow: auto;
}
</style>
