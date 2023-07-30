from .exceptions import MatcherNotFoundError


def send_error(self, code: int, message: str = ...) -> None:
    self.send_response(code)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(bytes(f"<html><body><h1>{code}</h1><p>{message}</p></body></html>", "utf-8"))
    
    
def route_exists_and_is_valid(self, url: str, route_patterns: dict, matchers: dict):
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
                        send_error(self, 400, "Invalid request")
                        return "invalid", None
                else:
                    var_name = matcher.split(":")[0]
                    variables[var_name] = url_list[i]
                    if should_continue(i, route_list):
                        continue
                    else:
                        return route, variables
            else:
                break
                    