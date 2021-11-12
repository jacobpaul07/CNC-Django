import os.path
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class OnMyWatch:
    # Set the directory on watch

    def __init__(self, watchDirectory):
        self.observer = Observer()
        self.watchDirectory = watchDirectory

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        fileName = None
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            fileName = os.path.basename(event.src_path)
            # Event is created, you can process it now
            print("Watchdog received created event - % s." % event.src_path)
        elif event.event_type == 'modified':
            fileName = os.path.basename(event.src_path)
            # Event is modified, you can process it now
            print("Watchdog received modified event - % s." % event.src_path)

        return fileName


if __name__ == "__main__":
    watch = OnMyWatch("D:/CNC-OEE/CNC-Django/App/Excel")
    watch.run()
