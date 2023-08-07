from app import app
from config import config
import routes, matchers, messages

app.run("localhost", 1407, config)
