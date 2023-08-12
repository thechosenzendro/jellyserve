from urllib.parse import unquote_plus
from .internals import keys_to_dict


def form_data(body: bytes) -> dict:
    body_str = unquote_plus(body.decode(), encoding="utf-8")
    return keys_to_dict(body_str)
