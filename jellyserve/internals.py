from .exceptions import MatcherNotFoundError
from .response import error, Response
import re, os, mimetypes

def route_exists_and_is_valid(url: str, route_patterns: dict, matchers: dict):
    if url.endswith("/") and url != "/":
        url = url[0:-1]

    def should_continue(index: int, list: list):
        if index == len(list) - 1:
            return False
        else:
            return True

    url_list = url.split("/")

    for route in route_patterns:
        variables = {}
        if url == route:
            return route, variables

        if re.fullmatch(r"^.*\..*$", url):
            file_url = f"public{url}"
            if os.path.isfile(file_url):
                mimetype = mimetypes.guess_type(file_url)[0]
                with open(file_url, "rb") as f:
                    return Response(f.read(), headers={
                        "Content-type": f"{mimetype}"
                    }), None
            else:
                return error(404, f"File {url} not found."), None
        route_list = route.split("/")

        if len(url_list) != len(route_list):
            continue

        for i, route_part in enumerate(route_list):
            if route_part == url_list[i]:
                if should_continue(i, route_list):
                    continue
                else:
                    return route, variables
            if route_part.startswith("[") and route_part.endswith("]"):
                matcher = route_part[1:-1]
                if len(matcher.split(":")) != 1:
                    matcher_name, var_name = matcher.split(":")
                    if matcher_name in matchers:
                        is_matching = matchers[matcher_name](url_list[i])
                    else:
                        raise MatcherNotFoundError(f"Matcher {matcher_name} not found.")
                    if is_matching:
                        variables[var_name] = url_list[i]
                        if should_continue(i, route_list):
                            continue
                        else:
                            return route, variables
                    else:
                        return error(400, "Invalid request"), None
                else:
                    var_name = matcher.split(":")[0]
                    variables[var_name] = url_list[i]
                    if should_continue(i, route_list):
                        continue
                    else:
                        return route, variables
            else:
                break
    return error(404, "Not found"), None