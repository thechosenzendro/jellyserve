<script>
  import { onMount } from "svelte";

  const socket = new WebSocket("ws://localhost:8080");
  export let data;
  console.log(data);
  let message_data;
  let message = "";
  let api_response = "";
  onMount(async () => {
    console.log("PLS FETCH!");
    api_response = await fetch("/api", { method: "POST" });
    api_response = await api_response.json();
    api_response = JSON.stringify(api_response);
  });
  socket.addEventListener("open", function (event) {
    console.info("It opened!!");
    socket.send("Connection Established");
  });

  socket.addEventListener("message", function (event) {
    console.log(event.data);
    message_data = event.data;
    return false;
  });

  socket.addEventListener("error", (error) => {
    console.error("WebSocket error:", error);
  });
  socket.addEventListener("close", function (event) {
    console.error("It closed!!!!", event);
  });
  function contactServer() {
    if (socket.readyState === WebSocket.OPEN) {
      console.log("WebSocket connection");
      socket.send(message);
    } else {
      console.error(
        `WebSocket connection is not open. status ${socket.readyState}`
      );
    }
  }
</script>

<h1>Chat...or is it?</h1>
<h1>{message_data}</h1>
<h1 class="test">API: {api_response}</h1>
<input type="text" bind:value={message} placeholder="Message to be sent" />
<button on:click={contactServer}>Send</button>

<style>
  .test {
    background-color: purple;
  }
</style>
