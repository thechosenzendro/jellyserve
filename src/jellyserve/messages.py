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
        module_name: str,
        module_path: str,
        handler: str,
    ) -> None:
        self.module_name = module_name
        self.module_path = module_path
        self.handler = handler

    def get_handler(self):
        from .internals import get_module

        handler_module = get_module(self.module_name, self.module_path)
        handler = getattr(handler_module, self.handler)

        return handler

    def start(self, port: int):
        import websockets
        import functools
        import asyncio

        async def message_handler(websocket, path, handler: MessageServer):
            async for data in websocket:
                message = Message(websocket, path, data)
                await handler.get_handler()(message)

        try:
            server = websockets.serve(
                functools.partial(message_handler, handler=self), "localhost", port
            )
            asyncio.get_event_loop().run_until_complete(server)
            asyncio.get_event_loop().run_forever()

        except KeyboardInterrupt:
            asyncio.get_event_loop().stop()
            print(f"Message server on port {port} stopped.")