from array import array
import math as m

class Kinematics:
    def __init__(self, a):
        self.a     = array('f', a)                # (a0, a1, a2, a3) - lengths
        self.angle = array('f', (0, 0, 0, 0))     # angles
        self.pos   = array('f', (0, 0, 0))        # X, Y, Z
        
    def inverse(x, y, z):
        for i, pos in enumerate((x,y,z)):
            self.pos[i] = pos
        self.angle[0] = m.atan(self.pos[1]/self.pos[0])
        x  -= self.a[3]*m.cos(self.angle[0])
        y  -= self.a[3]*m.cos(self.angle[0])
        r1 = m.sqrt(self.pos[0]**2 + self.pos[1]**2)
        r2 = z - self.a[0]
        phi2 = m.atan(r2/r1)
        r3 = m.sqrt(r1**2 + r2**2)
        phi1 = m.acos((self.a[2]**2 - self.a[1]**2 - r3**2)/(-2*self.a[1]*r3))
        self.angle[1] = phi1 + phi2
        self.angle[2] = m.acos((r3**2 - self.a[1]**2 - self.a[2]**2)/(-2*self.a[1]*self.a[2]))
        return self.angle
        
    def forward(a0, a1, a2):
        return self.pos