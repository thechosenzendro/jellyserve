import pathlib
import os
import json
from .config import get_config_value


class Response:
    def __init__(
        self,
        content: str | bytes = 'Looks like you did not specify "content" in your Response.',
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
            server_mode = get_config_value("server/mode")
            runtime_path = get_config_value("server/runtime_path")
            if server_mode == "dev":
                html = generate_component(template_location, title=title)
                return Response(content=html)
            elif server_mode == "prod":
                component_name = os.path.basename(template_location).replace(
                    ".svelte", ""
                )
                html_path = f"{runtime_path}{component_name}/template.html"
                if os.path.exists(html_path):
                    with open(html_path) as html:
                        return Response(content=html.read())
                else:
                    return error(404, f"Component {component_name} not found.")
            else:
                file_extension = pathlib.Path(template_location).suffix
                return error(501, f"{file_extension} files not supported")


def populate(template_location: str, context: (dict, list)) -> Response:
    if template_location.endswith(".html"):
        return error(501, ".html files cannot be used with populate()")
    elif template_location.endswith(".svelte"):
        server_mode = get_config_value("server/mode")
        if server_mode == "dev":
            html = generate_component(template_location, context=context)
            return Response(content=html)
        elif server_mode == "prod":
            runtime_path = get_config_value("server/runtime_path")
            runtime_url = get_config_value("server/runtime_url")
            component_name = os.path.basename(template_location).replace(".svelte", "")
            with open(f"{runtime_path}{component_name}/populated_output.js", "w+") as populated_output:
                with open(f"{runtime_path}{component_name}/output.js", "r") as output_template:
                    output_template = output_template.read()
                    context = json.dumps(context)
                    populated_output.write(output_template.replace("\"%jellyserve.component.data%\"", context))
            with open(f"{runtime_path}{component_name}/template.html", "r") as html_template:
                html = html_template.read().replace(
                    f"{runtime_url}{component_name}/output.js",
                    f"{runtime_url}{component_name}/populated_output.js")
                return Response(content=html)


def error(status: int, message: str = ...) -> Response:
    error_template_path = get_config_value("server/errors/template_path")
    with open(error_template_path) as error_template:
        html = (
            error_template.read()
            .replace("%jellyserve.error.status%", str(status))
            .replace("%jellyserve.error.message%", message)
        )
        return Response(status=status, content=html)


def redirect(status: int, redirect_url: str) -> Response:
    return Response(status=status, headers={"Location": redirect_url})


def generate_component(
    url: str,
    title: str = "NO_TITLE",
    context=None
) -> str:
    component_name = os.path.basename(url).replace(".svelte", "")

    runtime_path = get_config_value("server/runtime_path")
    templates_path = get_config_value("templates/templates_path")
    frontend_path = get_config_value("templates/frontend_path")
    runtime_url = get_config_value("server/runtime_url")
    if title == "NO_TITLE":
        title = get_config_value("templates/default_title")
    os.makedirs(f"{runtime_path}{component_name}", exist_ok=True)
    with open(f"{runtime_path}{component_name}/template.js", "w+", encoding="utf-8") as js:
        with open(f"{templates_path}template.js", "r", encoding="utf-8") as js_template:
            js.write(
                js_template.read().replace(
                    "%jellyserve.component.not-compiled%", os.path.abspath(url)
                )
            )
    if context is not None:
        js = open(f"{runtime_path}{component_name}/template.js", "r")
        with open(f"{runtime_path}{component_name}/populated_template.js", "w+", encoding="utf-8") as js_pop_template:
            context = json.dumps(context)
            content = js.read().replace("\"%jellyserve.component.data%\"", context)
            js_pop_template.write(content)
            js.close()
    with open(f"{runtime_path}{component_name}/rollup.config.mjs", "w+", encoding="utf-8") as rollup:
        with open(f"{templates_path}template.rollup.config.mjs", "r", encoding="utf-8") as rollup_template:
            if context is not None:
                template_js_path = os.path.abspath(f"{runtime_path}{component_name}/populated_template.js"),
            else:
                template_js_path = os.path.abspath(f"{runtime_path}{component_name}/template.js"),
            print(template_js_path)
            rollup.write(
                rollup_template.read()
                .replace(
                    "%jellyserve.rollup.svelte.path%",
                    os.path.abspath(
                        f"{frontend_path}node_modules/rollup-plugin-svelte/index.js"
                    ),
                )
                .replace(
                    "%jellyserve.rollup.resolve.path%",
                    os.path.abspath(
                        f"{frontend_path}node_modules/@rollup/plugin-node-resolve/dist/es/index.js"
                    ),
                )
                .replace(
                    "%jellyserve.component.template.js%",
                    "".join(template_js_path),
                )
                .replace(
                    "%jellyserve.component.compiled%",
                    os.path.abspath(f"{runtime_path}{component_name}/output.js"),
                )
                .replace("%jellyserve.frontend.path%", os.path.abspath(frontend_path))
            )
    os.system(
        f"{frontend_path}/node_modules/.bin/rollup -c {runtime_path}{component_name}/rollup.config.mjs"
    )
    with open(
        f"{frontend_path}/.templates/template.html", "r", encoding="utf-8"
    ) as html_template:
        with open(
            f"{runtime_path}{component_name}/template.html", "w+", encoding="utf-8"
        ) as html:
            html_result = (
                html_template.read()
                .replace(
                    "%jellyserve.component.compiled%",
                    f"{runtime_url}{component_name}/output.js",
                )
                .replace("%jellyserve.title%", title)
            )
            html.write(html_result)
            print(f"Component {component_name} generated succesfully.")
            return html_result
