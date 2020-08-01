import GravitationObject
import pyglet.sprite
from constants import *
from math import atan, pi, sqrt


"""
Skeleton for projectile. 
Each projectile does a different thing, so it is very important we
    keep this flexible
"""
class Projectile(GravitationObject.GravitatedObject, pyglet.sprite.Sprite):
    img = None
    speed = 3
    mass = 10
    def __init__(self, x, y, vel):
        velScalar = sqrt(vel[0]**2 + vel[1]**2)
        startVel = [type(self).speed*vel[0]/velScalar, type(self).speed*vel[1]/velScalar]
        GravitationObject.GravitatedObject.__init__(self, x, y, 5, startVel, 0, type(self).mass, True)
        pyglet.sprite.Sprite.__init__(self, type(self).img, x=x, y=y, subpixel=True)

    """
    What does projectile do on impact?
    """
    def on_collision(self, other, first_caller=True):
        super().on_collision(other, first_caller=first_caller)

    def destroy(self):
        self.circle.x += 10000
        self.circle.y += 10000
        self.set_physics_data()

class Rocket(Projectile):
    img = soldier_img
    speed = 3
    mass = 0.1
    def __init__(self, x, y, vel):
        super().__init__(x, y, vel)

    def next_move(self):
        super().next_move()
        self.rotation = atan(self.velocity[1]/self.velocity[0])*pi/180
        if (self.velocity[1] > 0 and self.rotation%360. > 180.) or (self.velocity[1] < 0 and self.rotation%360. < 180.):
            self.rotation += 180.
    
    def on_collision(self, other, first_caller=True):
        super().on_collision(other, first_caller=first_caller)

        forceVec = [other.circle.x - self.circle.x, other.circle.y - self.circle.y]
        scalar = sqrt(forceVec[0]**2 + forceVec[1]**2)
        forceVec[0] *= 10/scalar
        forceVec[1] *= 10/scalar

        other.force_on_center(forceVec)

        self.destroy()
