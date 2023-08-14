from app import app
from jellyserve.request import Request
from jellyserve.response import template, redirect, populate
from jellyserve.forms import form_data
from jellyserve.db import DB, Query
count = 0


@app.route("/")
def index(request):
    return "Wow, Thats index!"


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
def hidden(request):
    try:
        if request.url_params["hidden"] == "False":
            return template("frontend/Hidden.svelte")
        else:
            return "Still hidden!"
    except KeyError:
        return "Still hidden!"


@app.route("/hidden/posted", method="POST")
def post(request):
    data = form_data(request.body)
    print(data)
    return redirect(301, "/sveltetest")


@app.route("/populated")
def populated(request):
    global count
    count = count + 1
    db = DB("dev.db")
    with Query(db, "SELECT * FROM Users;") as result:
        return populate("frontend/Populated.svelte", {"count": count, "response": result})
