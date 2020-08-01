from GravitationObject import GravitatedObject, AttachableObject, planets
from constants import *
from Projectiles import *
from math import sqrt, acos, cos, sin, pi

class Soldier(AttachableObject):
    def __init__(self, x=0, y=0, speed=6, mass=1, attached=None):
        super().__init__(soldier_img, 20, x=x, y=y, mass=mass, attached=attached)
        self.speed = speed
        self.current_ammo = None
        self.current_projectile = Rocket
        
    def walk(self, speed_fac):
        if self.attached:
            self.attached_rotation += speed_fac*self.speed
        else:
            self.drotation += speed_fac*self.speed*0.01
        
    def next_move(self):
        super().next_move()
        if abs(self.drotation) > maxDO:
            self.drotation *= maxDO/abs(self.drotation) # A pretty concise method to keep the sign

    def on_collision(self, other, first_caller=True):
        super().on_collision(other, first_caller=first_caller)
        rotVector = [cos((self.rotation-90)*pi/180), sin((self.rotation-90)*pi/180)]
        
        rotVectorScalar = sqrt(rotVector[0]**2 + rotVector[1]**2)
        relPositionVector = [other.circle.x - self.circle.x, other.circle.y - self.circle.y]
        relPositionVectorScalar = sqrt(relPositionVector[0]**2 + relPositionVector[1]**2)

        angleBetween = acos((rotVector[0]*relPositionVector[0] + rotVector[1]*relPositionVector[1])/(relPositionVectorScalar*rotVectorScalar))*180/pi
        if angleBetween < 30:
            self.attach(other)

    """
    Shoot projectile while conserving momentum
    'at' is position on window
    """
    def shoot(self, at):
        if not self.current_projectile: return

        vecX = at[0] - self.x
        vecY = at[1] - self.y
        vecScalar = sqrt(vecX**2 + vecY**2)
        vecX /= vecScalar
        vecY /= vecScalar

        projectile = self.current_projectile(self.x + vecX*(self.circle.radius+10), self.y + vecY*(self.circle.radius+10), [vecX, vecY])

        if not self.attached:
            # Recoil
            self.velocity[0] -= projectile.mass*projectile.velocity[0]/self.mass
            self.velocity[1] -= projectile.mass*projectile.velocity[1]/self.mass

        planets.append(projectile)

        projectile.move(projectile.velocity[0], projectile.velocity[1], rotation=0)
