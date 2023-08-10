class Request:
    def __init__(self, url_params: dict, body):
        self.url_params = url_params
        self.body = body
        