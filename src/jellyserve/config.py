import jellyserve.runtime as runtime

default_config = {
    "server": {
        "mode": "dev",
        "allowed_methods": ["GET", "POST", "PATCH", "DELETE"],
        "public_path": "public/",
        "runtime_path": "public/.runtime/",
        "runtime_url": ".runtime/",
        "errors": {
            "template_path": "frontend/.templates/error.html",
            "messages": {
                "400": "Invalid request",
                "404": "Not found",
                "405": "Method not allowed",
            },
        },
        "default_headers": {"Content-type": "text/html; charset=utf-8"}
    },
    "templates": {
        "frontend_path": "frontend/",
        "templates_path": "frontend/.templates/",
        "default_title": "JellyServe Page",
    },
}


def generate_config(config):
    runtime.config = config


def get_config_value(path_to_value: str) -> str | int | dict | list | None:
    result = get_value(runtime.config, path_to_value)
    if result is None:
        result = get_value(default_config, path_to_value)
    return result


def get_value(_dict: dict, path_to_value: str):
    keys = path_to_value.split("/")
    result = _dict
    try:
        for key in keys:
            result = result[key]
        return result
    except (KeyError, TypeError) as e:
        return None


def set_config_value(keys_str, value):
    set_value(runtime.config, keys_str, value)


def set_value(data, keys_str, value):
    keys = keys_str.split("/")
    current_dict = data
    for key in keys[:-1]:
        current_dict = current_dict.setdefault(key, {})
    current_dict[keys[-1]] = value
