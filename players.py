from GravitationObject import GravitatedObject, AttachableObject, planets
from constants import *

class Soldier(AttachableObject):
    def __init__(self, x=0, y=0, speed=6, attached=None):
        super().__init__(soldier_img, 10, x=x, y=y, attached=attached)
        self.speed = speed
        self.current_ammo = None
        self.current_projectile = None
        
    def walk(self, speed_fac):
        if self.attached:
            self.attached_rotation += speed_fac*self.speed
        else:
            self.drotation += speed_fac*self.speed*0.01
        
    def next_move(self):
        super().next_move()
        if abs(self.drotation) > maxDO:
            self.drotation *= maxDO/abs(self.drotation) # A pretty concise method to keep the sign

    """
    Conservation of momentum
    'at' is position on window
    """
    def shoot(self, at):
        if not self.current_projectile: return

        vecX = at[0] - self.velocity[0]
        vecY = at[1] - self.velocity[1]

        projectile = self.current_projectile()
        planets.append(projectile)
