import asyncio
from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop

from classes.MainWindow import MainWindow

def main() -> None:

    #load_config()
    
    app = QApplication([])
    window = MainWindow()
    window.show()

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    asyncio.gather(
        #esp32_conn(window),
        #server_conn(window),
    )

    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
