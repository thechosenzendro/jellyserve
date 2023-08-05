import pathlib, os

class Response:
    def __init__(
        self,
        content: str = "Looks like you did not specify \"contentW\" in your Response.",
        status: int = 200,
        headers: dict = {"Content-type": "text/html; charset=utf-8"},
    ) -> None:
        self.status = status
        self.content = content
        self.headers = headers


def template(template_location: str, title: str="JellyServe Page") -> Response:
    with open(template_location, encoding="utf-8") as template:
        if template_location.endswith(".html"):
            return Response(template.read())
        elif template_location.endswith(".svelte"):
            component_name = os.path.basename(template_location).replace(".svelte", "")
            os.makedirs(f"public/.runtime/{component_name}", exist_ok=True)
            with open(f"public/.runtime/{component_name}/template.js","w+", encoding="utf-8") as js:
                with open("frontend/.templates/template.js", "r", encoding="utf-8") as js_template:
                    js.write(js_template.read().replace("%jellyserve.component.not-compiled%", os.path.abspath(template_location)))
            os.system(f"frontend/node_modules/.bin/rollup --input public/.runtime/{component_name}/template.js --output.format iife --output.name app --output.file public/.runtime/{component_name}/output.js --plugin svelte --plugin @rollup/plugin-node-resolve")
            with open("frontend/.templates/template.html", "r", encoding="utf-8") as html_template:
                html = html_template.read().replace("%jellyserve.component.compiled%", f".runtime/{component_name}/output.js").replace("%jellyserve.title%", title)
                return Response(content=html)
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
    return Response(status=status, content=html)
