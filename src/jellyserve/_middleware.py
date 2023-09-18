from typing import Callable

class Middleware:
    def __init__(
        self,
        handler: Callable,
    ) -> None:
        self.handler = handler

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)
