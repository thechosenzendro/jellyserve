from typing import Callable


class Message:
    def __init__(self, websocket, path, data) -> None:
        self.websocket = websocket
        self.path = path
        self.data = data
        self.send = websocket.send

    def __str__(self) -> str:
        return self.data


class MessageServer:
    def __init__(
            self,
            port: int,
            handler: Callable,
    ) -> None:
        print("test")
        self.port = port
        self.handler = handler
        print("test2")

    def start(self):
        import websockets
        import functools
        import asyncio

        async def message_handler(websocket, path, _handler: Callable):
            async for data in websocket:
                message = Message(websocket, path, data)
                await _handler(message)

        try:
            handler = functools.partial(message_handler, _handler=self.handler)
            server = websockets.serve(handler, "localhost", self.port)
            print(f"Message server started at ws://localhost:{self.port}")

            asyncio.get_event_loop().run_until_complete(server)
            asyncio.get_event_loop().run_forever()

        except KeyboardInterrupt:
            asyncio.get_event_loop().stop()
            print(f"Message server on port {self.port} stopped.")
