import asyncio
from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop
import asyncio

from classes.MainWindow import MainWindow
from utils.subscriptions import subscribe, update_status

async def gui(event: asyncio.Event) -> None:
    
    app = QApplication([])
    window = MainWindow(event)
    window.show()

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        loop.create_task(subscribe(window))
        loop.create_task(update_status(window))
        loop.run_forever()

if __name__ == "__main__":
    asyncio.run(gui(asyncio.Event()))
