from .__init__ import JellyServe

class Generator:
    def __init__(self, app: JellyServe) -> None:
        self.app = app
    
    def start(self):
        import os
        import time
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        print(self.app.used_templates)
        absolute_template_paths = {os.path.abspath(path) for path in self.app.used_templates}
        print(absolute_template_paths)

        class Handler(FileSystemEventHandler):
            def on_modified(self, event):
                print(f"File {event.src_path} modified.")

            def on_created(self, event):
                print(f"File {event.src_path} created.")

            def on_deleted(self, event):
                print(f"File {event.src_path} deleted.")

        observer = Observer()

        for path in absolute_template_paths:
            handler = Handler()
            observer.schedule(handler, path, recursive=False)

        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down svelte generator...")
            observer.stop()
        observer.join()