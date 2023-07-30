from app import app
from config import config
import routes
import matchers


print(routes.__name__, matchers.__name__)
app.run("localhost", 1407, config)
