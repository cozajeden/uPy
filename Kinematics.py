from array import array
import math as m
from machine import Pin, PWM
from ucollections import namedtuple
from queue import Queue
import uasyncio as asyncio
import math

MotorTuple = namedtuple('Motor',('minimum', 'maximum', 'minAngle', 'maxAngle', 'zero', 'current', 'pwm', 'duty_u16'))

async def schedule(callback, time, *args, **kwargs):
    await asyncio.sleep_ms(time)
    callback(*args, **kwargs)
    
class Kinematics:
    def __init__(self):
        self.motors = []
        self.storedKMSG = []
        self.create_motor(1200, 8500, -math.pi*0.25, math.pi*0.25, 6)
        self.create_motor(2800, 6500, -math.pi*(35/180), math.pi*(55/180), 7)
        self.create_motor(5900, 8400, -math.pi*(65/180), math.pi*(10/180), 8)
        self.create_motor(1200, 5500, -math.pi, math.pi, 9)
        
    def command(self, msg):
        if msg[0] == 'L':
            current = self.motors[0]['current'] + int(msg[1])
            self.motors[0]['duty_u16'](current)
            self.motors[0]['current'] = current
            return str(current) + '\n'
        
    def pwm_from_angle(self, minimum, maximum, minAngle, maxAngle, angle):
        angleRange = maxAngle - minAngle
        pwmRange = maximum - minimum
        anglePos = angle - minAngle
        pwmPos = int(pwmRange*anglePos/angleRange) + minimum
        return pwmPos

    def create_motor(self, minimum, maximum, minAngle, maxAngle, pin):
        pwm =  PWM(Pin(pin))
        pwm.freq(50)
        center = self.pwm_from_angle(minimum, maximum, minAngle, maxAngle, 0)
        self.motors.append({
            'minimum':minimum,
            'maximum':maximum,
            'minAngle':minAngle,
            'maxAngle':maxAngle,
            'current':center,
            'currentAngle':0.,
            'pwm':pwm,
            'duty_u16':pwm.duty_u16
            })
        self.motors[-1]['duty_u16'](center)
        
async def start_kinematics():
    kinematics = Kinematics()
    kinematics.create_motor(900, 10000, 0, 3.14, 1.5, 6)
    while True:
        print('a')
        await asyncio.sleep(0.5)