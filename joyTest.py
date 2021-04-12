from machine import Pin, ADC
import rp2

class Joy:
    MAX = 65_025
    
    def __init__(self, xPin, yPin, button, smNr, func, res):
        self.res = res
        self.xPin = ADC(Pin(xPin))
        self.yPin = ADC(Pin(yPin))
        self._attach_button_callback(smNr, button, func)
        
    def getxy(self):
        return ((self.xPin.read_u16() >> self.res)/(Joy.MAX >> self.res), (self.yPin.read_u16() >> self.res)/(Joy.MAX >> self.res))
    
    def _attach_button_callback(self, smNr, pin, func):
        "func argument is a function that takes sm(StateMachine) as an argument, this function will be egezcuted when pin state will change from high to low. smNr is a number of sm to use."
        self.sm = rp2.StateMachine(smNr, Joy.wait_pin_low, freq=20, in_base=Pin(pin, Pin.IN, Pin.PULL_UP))
        self.sm.irq(func)
        self.sm.active(1)
        
    @staticmethod
    @rp2.asm_pio()
    def wait_pin_low():
        wrap_target()
        wait(0, pin, 0)
        irq(block, rel(0))
        wait(1, pin, 0) [31]
        wrap()