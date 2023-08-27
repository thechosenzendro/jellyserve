from sample_project.app import app
from jellyserve.messages import Message


@app.message_server(8080)
async def handler(message: Message):
    print("Got data!")
    await message.send(f"Data from the server: {message.data}")
