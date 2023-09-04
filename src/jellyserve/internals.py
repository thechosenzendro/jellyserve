from .response import error, Response
from .messages import Message
from ._config import config
from typing import Callable
import inspect
import asyncio
import websockets
from functools import partial


def start_message_server(handler: Callable, port: int):
    from .messages import MessageServer

    async def message_handler(websocket, path, handler: MessageServer):
        async for data in websocket:
            message = Message(websocket, path, data)
            await handler.get_handler()(message)

    try:
        server = websockets.serve(
            partial(message_handler, handler=handler), "localhost", port
        )
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        asyncio.get_event_loop().stop()
        print(f"Message server on port {port} stopped.")


def keys_to_dict(keys: str) -> dict:
    entry_list = keys.split("&")
    entries = {}
    for entry in entry_list:
        try:
            entry_name, entry_value = entry.split("=")
            entries[entry_name] = entry_value
        except ValueError:
            entry_name = entry.split("=")[0]
            entries[entry_name] = True
    return entries


def dict_to_keys(_dict: dict) -> str:
    keys_string = ""

    for key_name, key_value in _dict.items():
        keys_string = keys_string + f"{key_name}={key_value};"

    return keys_string


def get_module(module_name: str, module_path: str):
    from importlib.machinery import SourceFileLoader

    module = SourceFileLoader(module_name, module_path).load_module()

    return module
