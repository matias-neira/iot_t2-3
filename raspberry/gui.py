import asyncio
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop
import asyncio

from publisher import publisher
from classes.MainWindow import MainWindow
from utils.subscriptions import subscribe, update_status

def gui() -> None:

    event = asyncio.Event()

    app = QApplication([])
    window = MainWindow(event)
    window.show()

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        loop.create_task(publisher(event))
        loop.create_task(subscribe(window))
        loop.create_task(update_status(window))
        loop.run_forever()

if __name__ == "__main__":
    gui()
