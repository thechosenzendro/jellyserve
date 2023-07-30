import pathlib


class Response:
    def __init__(
        self,
        html: str = "Looks like you did not specify HTML in your Response.",
        status: int = 200,
        headers: dict = {"Content-type": "text/html"},
    ) -> None:
        self.status = status
        self.html = html
        self.headers = headers


def template(template_location: str) -> Response:
    with open(template_location) as template:
        if template_location.endswith(".html"):
            return Response(template.read())
        else:
            file_extension = pathlib.Path(template_location).suffix
            return error(501, f"{file_extension} files not supported")


def error(status: int, message: str = ...) -> None:
    html = f"""
    <html>
    <head>
    <title>{status} - {message}</title>
    </head>
    <body>
    <h1>{status}</h1>
    <p>{message}</p>
    </body>
    </html>    
"""
    return Response(status=status, html=html)
