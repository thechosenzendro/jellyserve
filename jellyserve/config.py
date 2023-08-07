import jellyserve.runtime as runtime

default_config = {
    "server": {
        "mode": "dev",
        "allowed_methods": ["GET", "POST"],
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
    },
    "templates": {
        "frontend_path": "frontend/",
        "templates_path": "frontend/.templates/",
        "default_title": "JellyServe Page",
    },
}


def generate_config(config):
    runtime.config = default_config

    def get_all_keys(config, path=None):
        if path is None:
            path = []

        keys = []
        for key, value in config.items():
            current_path = path + [key]
            keys.append("/".join(current_path))
            if isinstance(value, dict):
                keys.extend(get_all_keys(value, current_path))
        return keys

    paths = get_all_keys(config)
    for path in paths:
        set_config_value(path, get_config_value(path))


def get_config_value(path_to_value: str):
    return get_value(runtime.config, path_to_value)


def get_value(dict: dict, path_to_value: str):
    keys = path_to_value.split("/")
    result = dict
    try:
        for key in keys:
            result = result[key]
        return result
    except (KeyError, TypeError):
        return None


def set_config_value(keys_str, value):
    set_value(runtime.config, keys_str, value)


def set_value(data, keys_str, value):
    keys = keys_str.split("/")
    current_dict = data
    for key in keys[:-1]:
        current_dict = current_dict.setdefault(key, {})
    current_dict[keys[-1]] = value
