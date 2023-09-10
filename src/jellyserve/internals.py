def keys_to_dict(keys: str) -> dict:
    entry_list = keys.split("&")
    entries = {}
    for entry in entry_list:
        try:
            entry_name, entry_value = entry.split("=")
            entries[entry_name] = entry_value
        except ValueError:
            entry_name = entry.split("=")[0]
            entries[entry_name] = True
    return entries


def dict_to_keys(_dict: dict) -> str:
    keys_string = ""

    for key_name, key_value in _dict.items():
        keys_string = keys_string + f"{key_name}={key_value};"

    return keys_string


def get_module(module_name: str, module_path: str):
    from importlib.machinery import SourceFileLoader

    module = SourceFileLoader(module_name, module_path).load_module()

    return module
