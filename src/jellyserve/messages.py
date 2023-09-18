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
        handler: Callable,
    ) -> None:
        self.handler = handler

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)

    def start(self, port: int):
        import websockets
        import functools
        import asyncio

        async def message_handler(websocket, path, handler: MessageServer):
            async for data in websocket:
                message = Message(websocket, path, data)
                await handler(message)

        try:
            server = websockets.serve(
                functools.partial(message_handler, handler=self), "localhost", port
            )
            asyncio.get_event_loop().run_until_complete(server)
            asyncio.get_event_loop().run_forever()

        except KeyboardInterrupt:
            asyncio.get_event_loop().stop()
            print(f"Message server on port {port} stopped.")