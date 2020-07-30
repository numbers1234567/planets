import GravitationObject
import pyglet.sprite
from constants import *


"""
Skeleton for projectile. 
Each projectile does a different thing, so it is very important we
    keep this flexible
"""
class Projectile(GravitationObject.GravitatedObject, pyglet.sprite.Sprite):
    def __init__(self, x, y, dir, speed, img):
        GravitationObject.GravitatedObject.__init__(self, x, y, 10, startvel, 0, 0.1, False)
        pyglet.sprite.Sprite.__init__(self, img, x=x, y=y, subpixel=True)

    """
    What does projectile do?
    """
    def on_collision(self):
        return

    def destroy(self):
        self.x += 10000
        self.y += 10000
        self.set_physics_data()

class Rocket(Projectile):
    def __init__(self, x, y, vel):
        super().__init__(x, y, vel, 1, soldier_img)