class Middleware:
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
