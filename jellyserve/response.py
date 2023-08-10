import pathlib, os
from .config import get_config_value


class Response:
    def __init__(
        self,
        content: str = 'Looks like you did not specify "content" in your Response.',
        status: int = 200,
        headers: dict = {"Content-type": "text/html; charset=utf-8"},
    ) -> None:
        self.status = status
        self.content = content
        self.headers = headers


def template(template_location: str, title: str = "JellyServe Page") -> Response:
    with open(template_location, encoding="utf-8") as template:
        if template_location.endswith(".html"):
            return Response(template.read())

        elif template_location.endswith(".svelte"):
            SERVER_MODE = get_config_value("server/mode")
            RUNTIME_PATH = get_config_value("server/runtime_path")
            if SERVER_MODE == "dev":
                html = generate_component(template_location, title=title)
                return Response(content=html)
            elif SERVER_MODE == "prod":
                component_name = os.path.basename(template_location).replace(
                    ".svelte", ""
                )
                html_path = f"{RUNTIME_PATH}{component_name}/template.html"
                if os.path.exists(html_path):
                    with open(html_path) as html:
                        return Response(content=html.read())
                else:
                    return error(404, f"Component {component_name} not found.")
        else:
            file_extension = pathlib.Path(template_location).suffix
            return error(501, f"{file_extension} files not supported")


def error(status: int, message: str = ...) -> Response:
    ERROR_TEMPLATE_PATH = get_config_value("server/errors/template_path")
    with open(ERROR_TEMPLATE_PATH) as template:
        html = (
            template.read()
            .replace("%jellyserve.error.status%", str(status))
            .replace("%jellyserve.error.message%", message)
        )
        return Response(status=status, content=html)


def redirect(status: int, redirect_url: str) -> Response:
    return Response(status=status, headers={"Location": redirect_url})

def generate_component(
    url: str,
    title: str = "NO_TITLE",
) -> str:
    component_name = os.path.basename(url).replace(".svelte", "")

    RUNTIME_PATH = get_config_value("server/runtime_path")
    TEMPLATES_PATH = get_config_value("templates/templates_path")
    FRONTEND_PATH = get_config_value("templates/frontend_path")
    RUNTIME_URL = get_config_value("server/runtime_url")
    if title == "NO_TITLE":
        title = get_config_value("templates/default_title")
    os.makedirs(f"{RUNTIME_PATH}{component_name}", exist_ok=True)
    with open(
        f"{RUNTIME_PATH}{component_name}/template.js", "w+", encoding="utf-8"
    ) as js:
        with open(f"{TEMPLATES_PATH}template.js", "r", encoding="utf-8") as js_template:
            js.write(
                js_template.read().replace(
                    "%jellyserve.component.not-compiled%", os.path.abspath(url)
                )
            )
    with open(
        f"{RUNTIME_PATH}{component_name}/rollup.config.mjs", "w+", encoding="utf-8"
    ) as rollup:
        with open(
            f"{TEMPLATES_PATH}template.rollup.config.mjs", "r", encoding="utf-8"
        ) as rollup_template:
            rollup.write(
                rollup_template.read()
                .replace(
                    "%jellyserve.rollup.svelte.path%",
                    os.path.abspath(
                        f"{FRONTEND_PATH}node_modules/rollup-plugin-svelte/index.js"
                    ),
                )
                .replace(
                    "%jellyserve.rollup.resolve.path%",
                    os.path.abspath(
                        f"{FRONTEND_PATH}node_modules/@rollup/plugin-node-resolve/dist/es/index.js"
                    ),
                )
                .replace(
                    "%jellyserve.component.template.js%",
                    os.path.abspath(f"{RUNTIME_PATH}{component_name}/template.js"),
                )
                .replace(
                    "%jellyserve.component.compiled%",
                    os.path.abspath(f"{RUNTIME_PATH}{component_name}/output.js"),
                )
                .replace("%jellyserve.frontend.path%", os.path.abspath(FRONTEND_PATH))
            )
    os.system(
        f"{FRONTEND_PATH}/node_modules/.bin/rollup -c {RUNTIME_PATH}{component_name}/rollup.config.mjs"
    )
    with open(
        f"{FRONTEND_PATH}/.templates/template.html", "r", encoding="utf-8"
    ) as html_template:
        with open(
            f"{RUNTIME_PATH}{component_name}/template.html", "w+", encoding="utf-8"
        ) as html:
            html_result = (
                html_template.read()
                .replace(
                    "%jellyserve.component.compiled%",
                    f"{RUNTIME_URL}{component_name}/output.js",
                )
                .replace("%jellyserve.title%", title)
            )
            html.write(html_result)
            print(f"Component {component_name} generated succesfully.")
            return html_result
