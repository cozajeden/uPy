# Example using PIO to wait for a pin change and raise an IRQ.
#
# Demonstrates:
#   - PIO wrapping
#   - PIO wait instruction, waiting on an input pin
#   - PIO irq instruction, in blocking mode with relative IRQ number
#   - setting the in_base pin for a StateMachine
#   - setting an irq handler for a StateMachine
#   - instantiating 2x StateMachine's with the same program and different pins

import time
from machine import Pin
import rp2


@rp2.asm_pio()
def wait_pin_low():
    wrap_target()
    wait(0, pin, 0)
    irq(block, rel(0))
    wait(1, pin, 0) [5]
    in_(pins,2)
    push()
    wrap()
    

def handler0(sm):
    print(sm.get() & 0xFF)
    #print(sm.irq().flags())
    if not pin11.value():
        print('right')
    else:
        print('left')
        
def handler1(sm):
    if not pin13.value():
        print('right')
    else:
        print('left')
        
def handler2(sm):
    if not pin15.value():
        print('right')
    else:
        print('left')
        
def handler3(sm):
    if not pin17.value():
        print('right')
    else:
        print('left')
        
def handler3(sm):
    print(sm.get() & 0xFF)


pin13 = Pin(13, Pin.IN, Pin.PULL_UP)
pin15 = Pin(15, Pin.IN, Pin.PULL_UP)
pin16 = Pin(16, Pin.IN, Pin.PULL_UP)
pin17 = Pin(17, Pin.IN, Pin.PULL_UP)
pin14 = Pin(14, Pin.IN, Pin.PULL_UP)
pin12 = Pin(12, Pin.IN, Pin.PULL_UP)
pin11 = Pin(11, Pin.IN, Pin.PULL_UP)
pin10 = Pin(10, Pin.IN, Pin.PULL_UP)
pin28 = Pin(28, Pin.IN, Pin.PULL_UP)

sm1 = rp2.StateMachine(1, wait_pin_low, in_base=pin12)
sm1.irq(handler1)

sm2 = rp2.StateMachine(2, wait_pin_low, in_base=pin14)
sm2.irq(handler2)

sm3 = rp2.StateMachine(3, wait_pin_low, in_base=pin16)
sm3.irq(handler3)

#sm0.active(1)
#sm1.active(1)
#sm2.active(1)
#sm3.active(1)
while True:
    print('aa')
    time.sleep(2)
    