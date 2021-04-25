import uasyncio as asyncio
from uasyncio import Event, Lock
from WizFi360Drv.socket import Socket
from queue import Queue
from machine import UART
from SSIDPASS import *
  
class Client:
    def __init__(self, id, lock, sendQ, recvQ = Queue(5)):
        print('[CLIENT {0}] Connected!'.format(id))
        self.lock = lock
        self.id = id
        self.rQ = recvQ
        self.sQ = sendQ
        
    async def send(self, msg):
        await self.sQ.put(cmd.SEND + b'{0},{1}'.format(self.id, len(msg)) + cmd.EOL)
        await self.sQ.put(msg)

async def schedule(callback, time, *args, **kwargs):
    await asyncio.sleep_ms(time)
    callback(*args, **kwargs)

async def start_listening(lock, recQueue = Queue(), sndQueue = Queue()):
    uart = UART(1)
    wifi = Socket(uart)
    wifi.init(Socket.STA, (SSID, PASS))
    swriter, sreader = wifi.listen(3000)
    #swriter, sreader = wifi.bind('192.168.8.100', 3000)
    asyncio.create_task(reciver(lock, sreader, recQueue))
    asyncio.create_task(sender(lock, swriter, sndQueue))
          
async def sender(lock, swriter, queue):
    while True:
        swriter.write(await queue.get())
        await swriter.drain()
        await asyncio.sleep(0.001)

async def reciver(lock, sreader, queue):
    while True:
        await queue.put(await sreader.readline())
        await asyncio.sleep(0.001)
