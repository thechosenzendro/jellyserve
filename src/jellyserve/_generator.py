from .__init__ import JellyServe
import os
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ._config import config
import subprocess
class Generator:
    def __init__(self, app: JellyServe) -> None:
        self.app = app
    
    def start(self):
        template_paths = {os.path.abspath(path) for path in self.app.used_templates}
        runtime_path = config.get("server/runtime_path")
        generate_component()
        if not os.path.exists(runtime_path):
             os.mkdir(runtime_path)

        observer = Observer()

        for path in template_paths:
            handler = Handler()
            observer.schedule(handler, path, recursive=False)

        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down generator...")
            if os.path.exists(runtime_path):
                 shutil.rmtree(runtime_path)
            observer.stop()
        observer.join()


class Handler(FileSystemEventHandler):
            def on_modified(self, event):
                print(f"File {event.src_path} modified.")

            def on_created(self, event):
                print(f"File {event.src_path} created.")

            def on_deleted(self, event):
                print(f"File {event.src_path} deleted.")


def generate_component():
    code = '''const { rollup } = require("rollup")'''
    cmd = ["cd", config.get("templates/frontend_path"), "&&", "node", "--experimental-modules", "-e", code]
    print(" ".join(cmd))
    res = subprocess.check_output(cmd)
    print(res.decode())