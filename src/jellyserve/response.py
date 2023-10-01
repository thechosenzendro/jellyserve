import pathlib
import os
import json
from string import Template
from ._config import config
from .request import Cookies


class Response:
    def __init__(
        self,
        content: str
        | bytes = 'Looks like you did not specify "content" in your Response.',
        status: int = 200,
        headers: dict = config.get("server/default_headers"),
        cookies: Cookies = Cookies({}),
    ) -> None:
        self.status = status
        self.content = content
        self.headers = headers
        self.cookies = cookies


def template(
    location: str,
    headers: dict = config.get("server/default_headers"),
    cookies: Cookies = Cookies({}),
) -> Response:
    from ._exceptions import TemplateNotFound, FileNotSupported
    from string import Template
    with open(location, encoding="utf-8") as template:
        if location.endswith(".html"):
            return Response(template.read(), headers=headers, cookies=cookies)

        elif location.endswith(".svelte"):
            component_name = os.path.basename(location).replace(".svelte", "")
            runtime_component_url = f"{config.get('server/runtime_url')}/{component_name}"
            templates_path = config.get("templates/templates_path")
            html = f"{templates_path}/template.html"
            

            if os.path.exists(location):
                with open(html) as html:
                    template = Template(html.read())
                    content = template.substitute(component_code=f"{runtime_component_url}/bundle.js")
                    return Response(

                            content=content, headers=headers, cookies=cookies
                        )
            else:
                raise TemplateNotFound(f"Template location {location} not found.")
        else:
            file_extension = pathlib.Path(location).suffix
            raise FileNotSupported(f"{file_extension} files not supported.")


def populate(
    location: str,
    context: (dict, list),
    headers: dict = config.get("server/default_headers"),
    cookies: Cookies = Cookies({}),
) -> Response:
    from ._exceptions import FileNotCompatibleWithPopulate
    if location.endswith(".html"):
        raise FileNotCompatibleWithPopulate("HTML files cannot be used with populate.")
    elif location.endswith(".svelte"):
            assert 1 == 0
            runtime_path = config.get("server/runtime_path")
            runtime_url = config.get("server/runtime_url")
            component_name = os.path.basename(location).replace(".svelte", "")
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
        headers: dict = config.get("server/default_headers"),
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
    headers: dict = config.get("server/default_headers"),
    cookies: Cookies = Cookies({}),
) -> Response:
    error_template_path = str(config.get("server/errors/template_path"))
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
    headers: dict = config.get("server/default_headers"),
    cookies: Cookies = Cookies({}),
) -> Response:
    final_headers = {"Location": redirect_url}
    for header_name, header_value in headers.items():
        final_headers[header_name] = header_value
    return Response(status=status, headers=final_headers, cookies=cookies)