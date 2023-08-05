from app import app
from jellyserve.response import template


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
def sveltetest(request):
    return template("frontend/Index.svelte")
