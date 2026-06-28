import asyncio
from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop

from classes.MainWindow import MainWindow
from utils.subscriptions import subscribe

async def gui(event: asyncio.Event) -> None:
    
    app = QApplication([])
    window = MainWindow(event)
    window.show()

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    asyncio.gather(
        subscribe(window),
    )
    
    with loop:
        loop.run_forever()
