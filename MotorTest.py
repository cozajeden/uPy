from machine import Pin, PWM, ADC
from time import sleep
from joyTest import Joy
import uasyncio as asyncio
from queue import Queue
from network import start_listening
import WizFi360Drv.commands as cmd
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


async def schedule(callback, time, *args, **kwargs):
    await asyncio.sleep_ms(time)
    callback(*args, **kwargs)

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
        
async def listener(queue, sendQ):
    clients = {}
    while True:
        msg = await queue.get()
        msg = msg[:-2]
        if len(msg) > 0:
            if msg[2:] == b'CONNECT':
                if msg[0] not in clients:
                    clients[msg[0]] = Client(int(msg[0]), queue)
            if msg[:4] == b'+IPD':
                msg = msg[5:]
                #print(msg)
                msg = 'Love You!'
                await sendQ.put(cmd.PREP_SEND_BUFF + b'0,{0}'.format(len(msg)) + cmd.EOL )
                await sendQ.put(cmd.SEND_BUFF + b'{0}'.format(msg) + cmd.EOL )
                print('sent')
        
class Client:
    def __init__(self, id, sendQ, recvQ = Queue(5)):
        print('[Client {0}] Connected!'.format(id))
        self.id = id
        self.rQ = recvQ
        self.sQ = sendQ
        asyncio.create_task(self.listen())
        
    async def get(self):
        return await self.rQ.get()
    
    async def put(self, msg):
        await self.sQ.put((self.id, msg))
        
    async def listen(self):
        print('[Client {0}] Startet listening to.'.format(int(self.id)))
        try:
            first = True
            length = 0
            while True:
                msg = await self.get()
                print('[Client {0}] got message!',format(int(self.id)))
                print('[client', self.id, ']', msg)
                if msg == b'CLOSED':
                    break
                if msg == b'':
                    continue
                if first:
                    first = False
                    length = int(msg)
                    print(length)
                else:
                    length -= len(msg)
                if length == 0:
                    first = True
                    continue
                
        except OSError as e:
            print('[CLIENT {0}] Lost connection! {1}'.format(self.id, str(e)))
            
    async def send(self, queue, msg):
        pass

#while True:
#    pwm.duty_u16(int(MIN_PWM+(MAX_PWM*adc.read_u16()/CAP_PWM)))
async def main():
    recvQ = Queue()
    sendQ = Queue()
    asyncio.create_task(start_listening(recvQ, sendQ))
    asyncio.create_task(listener(recvQ, sendQ))
    resolution = 4
    m1 = motor(7, 1150, 5000, 0.02)
    m2 = motor(8, 4000, 7300, 0.02)
    m3 = motor(6, 1200, 8500, 0.02)
    button = Button(9, 1150, 5500, 0.02)
    joy = Joy(26, 27, 22, 0, button.button_callback, resolution)
    xPos = 0.51
    yPos = 0.51
    
    while True:
        pos = joy.getxy()
        if  pos[0] < 0.49 or pos[0] > 0.51:
            xPos += (pos[0] - 0.5)/50
        if pos[1] < 0.49 or pos[1] > 0.51:
            yPos += (pos[1] - 0.5)/50
        if xPos > 1:
            xPos = 1
        elif xPos < 0:
            xPos = 0
        if yPos > 1:
            yPos = 1
        elif yPos < 0:
            yPos = 0
        
        await m1((None, xPos))
        await m2((None, yPos))
        await m3((None, (adc.read_u16() >> resolution) / (CAP_PWM >> resolution)))
        await asyncio.sleep(0.02)
    
asyncio.run(main())