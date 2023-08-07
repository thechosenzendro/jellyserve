class Message:
    def __init__(self, websocket, path, data) -> None:
        self.websocket = websocket
        self.path = path
        self.data = data
        self.send = websocket.send

    def __str__(self) -> str:
        return self.data
