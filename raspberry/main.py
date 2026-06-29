import asyncio

from gui import gui
from publisher import publisher

async def main():
    
    event = asyncio.Event()
    await asyncio.gather(
        publisher(event),
        gui(event)
    )

if __name__ == "__main__":
    pass
    #asyncio.run(main())
