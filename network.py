import uasyncio as asyncio
from uasyncio import Event, Lock
from WizFi360Drv.socket import Socket
from queue import Queue
from machine import UART
from SSIDPASS import *



async def schedule(callback, time, *args, **kwargs):
    await asyncio.sleep_ms(time)
    callback(*args, **kwargs)

async def start_listening(recQueue = Queue(), sndQueue = Queue()):
    uart = UART(1)
    wifi = Socket(uart)
    wifi.init(Socket.STA, (SSID, PASS))
    swriter, sreader = wifi.listen(3000)
    #swriter, sreader = wifi.bind('192.168.8.100', 3000)
    asyncio.create_task(reciver(sreader, recQueue))
    asyncio.create_task(sender(swriter, sndQueue))
          
async def sender(swriter, queue):
    while True:
        swriter.write(await queue.get())
        await swriter.drain()

async def reciver(sreader, queue):
    while True:
        await queue.put(await sreader.readline())
