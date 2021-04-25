from machine import Pin, PWM, ADC
from time import sleep
from joyTest import Joy
import uasyncio as asyncio, gc
from queue import Queue
from network import start_listening, Client
import WizFi360Drv.commands as cmd
from kinematics import Kinematics
import math
#1
#MIN_PWM = 1200
#MAX_PWM = 8500
#2
#MIN_PWM = 1150
#MAX_PWM = 5000
#3
#MIN_PWM = 4000
#MAX_PWM = 7300
#4
#MIN_PWM = 1150
#MAX_PWM = 5500
CAP_PWM = 65025
#pwm = PWM(Pin(9))
#pwm.freq(50)
adc = ADC(Pin(28))
clients = {}

async def loop(pin, _min, _max, get, dt):
    pwm =  PWM(Pin(pin))
    pwm.freq(50)
    while True:
        pos = await get()
        duty = int(_min+((_max-_min)*pos[1]))
        if pos[0] is not None:
            print(pos, duty)
        pwm.duty_u16(duty)
        await asyncio.sleep(dt)

def motor(pin, _min, _max, dt):
    queue = Queue(5)
    asyncio.create_task(loop(pin, _min, _max, queue.get, dt))
    return queue.put


class Button:
    def __init__(self, pin, _min, _max, dt):
        self.m = motor(pin, _min, _max, dt)
        self.BUTTON_STATE = False
        
    def button_callback(self, sm):
        self.BUTTON_STATE = not self.BUTTON_STATE
        asyncio.create_task(self.open_close(self.BUTTON_STATE, self.m))
        
    async def open_close(self, state, m4):
        await m4((None, (state)))
        
async def handle_message(msg, sendQ, kinematics):
    if len(msg) > 0:
        if msg[2:] == cmd.CONNECTED:
            if msg[0]-48 not in clients.keys():
                clients[msg[0]-48] = Client(msg[0]-48, None, sendQ)
        elif msg[2:] == cmd.CLOSED:
            if msg[0]-48 in clients:
                clients.pop(msg[0]-48)
                print('[CLIENT {0}] DISCONNECTED!'.format(msg[0]-48))
                gc.collect()
        elif msg[:4] == b'+IPD':
            client = msg[5]-48
            msg = str(msg)
            msg = msg[msg.find(':')+1:-3]
            if msg[0] == 'K':
                if msg[1:] == 'END':
                    response = kinematics.command(kinematics.storedKMSG)
                    kinematics.storedKMSG = []
                    await clients[client].send(response)
                else:
                    kinematics.storedKMSG.append(msg[1:])
        
async def listener(lock, queue, sendQ, kinematics):
    while True:
        msg = cmd.BUSY
        while msg == cmd.BUSY or msg == cmd.EOL or msg == cmd.ACK:
            msg = await queue.get()
        asyncio.create_task(handle_message(msg, sendQ, kinematics))

async def main():
    kinematics = Kinematics()
    kinematics.create_motor(1200, 8500, -math.pi*0.25, math.pi*0.25, 6)
    kinematics.create_motor(2800, 6500, -math.pi*(35/180), math.pi*(55/180), 7)
    kinematics.create_motor(5900, 8400, -math.pi*(65/180), math.pi*(10/180), 8)
    kinematics.create_motor(1200, 5500, -math.pi, math.pi, 9)
    lock = asyncio.Lock()
    recvQ = Queue(5)
    sendQ = Queue(5)
    asyncio.create_task(start_listening(lock, recvQ, sendQ))
    asyncio.create_task(listener(lock, recvQ, sendQ, kinematics))
    while True:
        await asyncio.sleep(0)

    
asyncio.run(main())