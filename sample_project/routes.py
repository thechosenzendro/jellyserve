from app import app
from jellyserve.request import Request
from jellyserve.response import template, redirect, populate
from jellyserve.db import SQLite


@app.middleware(group="test")
def middleware(request: Request):
    print(f"Request: {request}")


@app.middleware(regex=r"/.*")
def catch_all_middleware(request: Request):
    print("Catch all!")


@app.route("/", group="test")
def index(request):
    return "Wow, Thats index!.."


@app.route("/example")
def example(request):
    return "Wow, Thats example!"


@app.route("/test/[int:id]")
def test(request, test_id):
    return f"Id: {test_id}"


@app.route("/nomatcher/[id]")
def test2(request, test_id):
    return f"Look ma! No matcher: {test_id}"


@app.route("/sveltetest")
def sveltetest(request: Request):
    print(request.body, request.url_params, request.cookies)
    return template("frontend/Index.svelte")


@app.route("/api", method="POST")
def api(request):
    return [{"WOW": "API?"}, {"Nene": "JJ"}]


@app.route("/hidden")
def hidden(request: Request):
    if request.url_params.get("hidden") == "False":
        return template("frontend/Hidden.svelte")
    else:
        return "Still hidden!"


@app.route("/hidden/posted", method="POST")
def post(request: Request):
    data = request.body.to_form_data()
    print(data)
    return redirect(301, "/sveltetest")


@app.route("/populated")
def populated(request):
    db = SQLite("dev.db")
    with db.query("SELECT * FROM Users;") as result:
        return populate("frontend/Populated.svelte", {"response": result})
