from app import app
import re


@app.matcher("int")
def int_matcher(value: str):
    return re.fullmatch(r'^-?\d+$', value)
