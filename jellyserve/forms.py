from urllib.parse import unquote_plus


def form_data(body: bytes) -> dict:
    body_str = unquote_plus(body.decode(), encoding="utf-8")
    entry_list = body_str.split("&")
    entries = {}
    for entry in entry_list:
        entry_name, entry_value = entry.split("=")
        entries[entry_name] = entry_value
    return entries
