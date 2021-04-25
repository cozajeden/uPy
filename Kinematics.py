from array import array
import math as m
from machine import Pin, PWM
from queue import Queue
import uasyncio as asyncio
import math


async def schedule(callback, time, *args, **kwargs):
    await asyncio.sleep_ms(time)
    callback(*args, **kwargs)
    
class Kinematics:
    def __init__(self, a1, a2, a3, a4):
        self.lenghts = (a1, a2, a3, a4)
        self.motors = []
        self.storedKMSG = []
        self.q23limits = (math.pi*(0.5 - 35/180), math.pi*(0.5 + 55/180))
        self.create_motor(1200, 8500, -math.pi*0.25, math.pi*0.25, 6, 0)
        self.create_motor(6500, 2800, math.pi*(35/180), math.pi*(145/180), 7, math.pi/2)
        self.create_motor(5900, 8400, -math.pi*(65/180), math.pi*(10/180), 8, 0)
        self.create_motor(1200, 5500, 0., math.pi, 9, math.pi/2)
        print('forward0', self.forward(0,0,0))
        
    def validate_angles(self, q1, q2, q3):
        print('q', q1*180/math.pi, q2*180/math.pi, q3*180/math.pi, (q2-q3)*180/math.pi)
        if not (self.motors[0]['minAngle'] <= q1 <= self.motors[0]['maxAngle']):
            return False
        print('step 1 ok')
        if not (self.motors[1]['minAngle'] <= q2 <= self.motors[1]['maxAngle']):
            return False
        print('step 2 ok')
        if not (self.motors[2]['minAngle'] <= q3 <= self.motors[2]['maxAngle']):
            return False
        print('step 3 ok')
        if not(self.q23limits[0] <= q2+q3 <= self.q23limits[1]):
            return False
        print('step 4 ok')
        return True
    
    def forward(self, q1, q2, q3):
        #q2 = -q2
        #q3 = -q3
        sinq1 = math.sin(q1)
        cosq1 = math.cos(q1)
        d1 = self.lenghts[1]*math.cos(q2)
        d2 = self.lenghts[1]*math.sin(q2)
        d3 = d1+self.lenghts[2]*math.cos(q3)
        d4 = d2-self.lenghts[2]*math.sin(q3)
        d5 = d3+self.lenghts[3]
        
        return d5*cosq1, d5*sinq1, self.lenghts[0]+d4
    
    def inverse(self, x, y, z):
        q1 = math.atan2(y, x)
        x -= self.lenghts[3]*math.cos(q1)
        y -= self.lenghts[3]*math.sin(q1)
        r1 = math.sqrt(x**2 + y**2)
        r2 = z - self.lenghts[0]
        fi2 = math.atan2(r2, r1)
        r3 = math.sqrt(r1**2 + r2**2)
        fi1 = math.acos((self.lenghts[2]**2 - self.lenghts[1]**2 - r3**2)/(-2*self.lenghts[1]*r3))
        q2 = fi2 + fi1
        fi3 = math.acos((r3**2 - self.lenghts[1]**2 - self.lenghts[2]**2)/(-2*self.lenghts[1]*self.lenghts[2]))
        q3 = fi3 + q2 - math.pi

        return q1, q2, q3
        
    def command(self, msg):
        if msg[0] == 'L':
            q = self.inverse(float(msg[1]), float(msg[2]), float(msg[3]))
            validate = self.validate_angles(q[0], q[1], q[2])
            if validate:
                q1 = self.pwm_from_angle_by_motor(0, q[0])
                q2 = self.pwm_from_angle_by_motor(1, q[1])
                q3 = self.pwm_from_angle_by_motor(2, q[2])
                print(q1, q2, q3)
                print((self.forward(q[0], q[1], q[2])))
                self.motors[0]['duty_u16'](q1)
                self.motors[1]['duty_u16'](q2)
                self.motors[2]['duty_u16'](q3)
                return 'OK\n'
            else:
                return 'LS\n'
            #current = self.motors[0]['current'] + int(msg[1])
            #self.motors[0]['duty_u16'](current)
            #self.motors[0]['current'] = current
            #return str(current) + '\n'
        
    def pwm_from_angle_by_motor(self, motor, angle):
        return self.pwm_from_angle(
            self.motors[motor]['min'],
            self.motors[motor]['max'],
            self.motors[motor]['minAngle'],
            self.motors[motor]['maxAngle'],
            angle
            )
        
    def pwm_from_angle(self, minimum, maximum, minAngle, maxAngle, angle):
        angleRange = maxAngle - minAngle
        pwmRange = maximum - minimum
        anglePos = angle - minAngle
        pwmPos = int(pwmRange*anglePos/angleRange) + minimum
        return pwmPos

    def create_motor(self, min, max, minAngle, maxAngle, pin, startAngle):
        pwm =  PWM(Pin(pin))
        pwm.freq(50)
        center = self.pwm_from_angle(min, max, minAngle, maxAngle, startAngle)
        self.motors.append({
            'min':min,
            'max':max,
            'minAngle':minAngle,
            'maxAngle':maxAngle,
            'current':center,
            'currentAngle':startAngle,
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