from app import app
from config import config
import routes
import matchers


app.run("localhost", 1407, config)
