import uvicorn

from app import app
import routes
import matchers
import messages

if __name__ == "__main__":
    app.run()
    uvicorn.run("run:app", port=1407, reload=True)

