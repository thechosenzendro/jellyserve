class Request:
    def __init__(self, url_params: dict, body: bytes, cookies: dict):
        self.url_params = url_params
        self.body = body
        self.cookies = cookies
        