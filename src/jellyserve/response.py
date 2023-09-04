import pathlib
import os
import json
from string import Template
from ._config import config
from .request import Cookie, Cookies


class Response:
    def __init__(
        self,
        content: str
        | bytes = 'Looks like you did not specify "content" in your Response.',
        status: int = 200,
        headers: dict = config.get_config_value("server/default_headers"),
        cookies: Cookies = Cookies({}),
    ) -> None:
        self.status = status
        self.content = content
        self.headers = headers
        self.cookies = cookies


def template(
    template_location: str,
    headers: dict = config.get_config_value("server/default_headers"),
    cookies: Cookies = Cookies({}),
) -> Response:
    with open(template_location, encoding="utf-8") as template:
        if template_location.endswith(".html"):
            return Response(template.read(), headers=headers, cookies=cookies)

        elif template_location.endswith(".svelte"):
            server_mode = config.get_config_value("server/mode")
            runtime_path = config.get_config_value("server/runtime_path")
            if server_mode == "dev":
                html = generate_component(template_location)
                return Response(content=html, headers=headers, cookies=cookies)
            elif server_mode == "prod":
                component_name = os.path.basename(template_location).replace(
                    ".svelte", ""
                )
                html_path = f"{runtime_path}/{component_name}/template.html"
                if os.path.exists(html_path):
                    with open(html_path) as html:
                        return Response(
                            content=html.read(), headers=headers, cookies=cookies
                        )
                else:
                    return error(
                        404,
                        f"Component {component_name} not found.",
                        headers=headers,
                        cookies=cookies,
                    )
            else:
                file_extension = pathlib.Path(template_location).suffix
                return error(
                    501,
                    f"{file_extension} files not supported",
                    headers=headers,
                    cookies=cookies,
                )


def populate(
    template_location: str,
    context: (dict, list),
    headers: dict = config.get_config_value("server/default_headers"),
    cookies: Cookies = Cookies({}),
) -> Response:
    if template_location.endswith(".html"):
        return error(
            501,
            ".html files cannot be used with populate()",
            headers=headers,
            cookies=cookies,
        )
    elif template_location.endswith(".svelte"):
        server_mode = config.get_config_value("server/mode")
        if server_mode == "dev":
            html = generate_component(template_location, context=context)
            return Response(content=html, headers=headers, cookies=cookies)
        elif server_mode == "prod":
            runtime_path = config.get_config_value("server/runtime_path")
            runtime_url = config.get_config_value("server/runtime_url")
            component_name = os.path.basename(template_location).replace(".svelte", "")
            with open(
                f"{runtime_path}/{component_name}/populated_output.js", "w+"
            ) as populated_output:
                with open(
                    f"{runtime_path}/{component_name}/output.js", "r"
                ) as output_template:
                    output_template = output_template.read()
                    context = json.dumps(context)
                    populated_output.write(
                        output_template.replace('"#component_data"', context)
                    )
            with open(
                f"{runtime_path}/{component_name}/template.html", "r"
            ) as html_template:
                html = html_template.read().replace(
                    f"{runtime_url}{component_name}/output.js",
                    f"{runtime_url}{component_name}/populated_output.js",
                )
                return Response(content=html, headers=headers, cookies=cookies)


class Error:
    def __init__(
        self,
        status: int,
        message: str = ...,
        headers: dict = config.get_config_value("server/default_headers"),
        cookies: Cookies = Cookies({}),
    ) -> Response:
        self.status = status
        self.message = message
        self.headers = headers
        self.cookies = cookies

    def get_response(self) -> Response:
        return Response(
            status=self.status,
            content=self.message,
            headers=self.headers,
            cookies=self.cookies,
        )


def error(
    status: int,
    message: str = ...,
    headers: dict = config.get_config_value("server/default_headers"),
    cookies: Cookies = Cookies({}),
) -> Response:
    error_template_path = str(config.get_config_value("server/errors/template_path"))
    with open(error_template_path) as error_template:
        error_template = Template(error_template.read())
        error_template = error_template.substitute(
            error_status=str(status),
            error_message=message,
        )

        return Error(status, error_template, headers, cookies)


def redirect(
    status: int,
    redirect_url: str,
    headers: dict = config.get_config_value("server/default_headers"),
    cookies: Cookies = Cookies({}),
) -> Response:
    final_headers = {"Location": redirect_url}
    for header_name, header_value in headers.items():
        final_headers[header_name] = header_value
    return Response(status=status, headers=final_headers, cookies=cookies)


def generate_component(url: str, context=None) -> str:
    print(url)
    component_name = os.path.basename(url).replace(".svelte", "")
    print(url, component_name)
    runtime_path = config.get_config_value("server/runtime_path")
    templates_path = config.get_config_value("templates/templates_path")
    frontend_path = config.get_config_value("templates/frontend_path")
    runtime_url = config.get_config_value("server/runtime_url")

    os.makedirs(f"{runtime_path}/{component_name}", exist_ok=True)

    js_path = f"{runtime_path}/{component_name}/template.js"
    js_template_path = f"{templates_path}/template.js"
    with open(js_path, "w+", encoding="utf-8") as js, open(
        js_template_path, "r", encoding="utf-8"
    ) as js_template:
        js_template = Template(js_template.read())
        js_template = js_template.substitute(component_code=os.path.abspath(url))
        js.write(js_template)

    if context is not None:
        populated_template_path = (
            f"{runtime_path}{component_name}/populated_template.js"
        )
        with open(js_path, "r") as js, open(
            populated_template_path,
            "w+",
            encoding="utf-8",
        ) as js_populated_template:
            context = json.dumps(context)
            content = js.read().replace('"#component_data"', context)
            js_populated_template.write(content)
    with open(
        f"{runtime_path}/{component_name}/rollup.config.mjs", "w+", encoding="utf-8"
    ) as rollup:
        with open(
            f"{templates_path}/template.rollup.config.mjs", "r", encoding="utf-8"
        ) as rollup_template:
            if context is not None:
                template_js_path = (
                    os.path.abspath(
                        f"{runtime_path}{component_name}/populated_template.js"
                    ),
                )
            else:
                template_js_path = (
                    os.path.abspath(f"{runtime_path}/{component_name}/template.js"),
                )
            rollup_template = Template(rollup_template.read())
            rollup_template = rollup_template.substitute(
                svelte_path=os.path.abspath(
                    f"{frontend_path}/node_modules/rollup-plugin-svelte/index.js"
                ),
                resolve_path=os.path.abspath(
                    f"{frontend_path}/node_modules/@rollup/plugin-node-resolve/dist/es/index.js"
                ),
                css_path=os.path.abspath(
                    f"{frontend_path}/node_modules/rollup-plugin-css-only/dist/index.mjs"
                ),
                js_input="".join(template_js_path),
                js_output=os.path.abspath(f"{runtime_path}/{component_name}/output.js"),
                frontend_path=os.path.abspath(frontend_path),
            )

            rollup.write(rollup_template)
    if os.name == "posix":
        os.system(
            f"{frontend_path}/node_modules/.bin/rollup -c {runtime_path}/{component_name}/rollup.config.mjs"
        )
    elif os.name == "nt":
        os.system(
            f'{os.path.abspath(f"{frontend_path}/node_modules/.bin/rollup.cmd")} -c {runtime_path}/{component_name}/rollup.config.mjs'
        )
    html_path = f"{runtime_path}/{component_name}/template.html"
    print(html_path)
    html_template_path = f"{frontend_path}/.templates/template.html"
    with open(html_path, "w+", encoding="utf-8") as html, open(
        html_template_path, "r", encoding="utf-8"
    ) as html_template:
        html_result = Template(html_template.read())
        html_result = html_result.substitute(
            component_code=f"{runtime_url}{component_name}/output.js",
            component_styles=f"{runtime_url}{component_name}/output.css",
        )

        html.write(html_result)
        print(f"Component {component_name} generated succesfully.")
        return html_result
