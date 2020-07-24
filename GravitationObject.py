"""
Contains base classes for gravity calculations.
Most of the math stays here.
"""
import math
import pyglet.shapes as pyglShapes
import pyglet.sprite as pyglSprite
import constants

"""
Main object which contains mathematics for gravity
"""
class GravitatedObject:
    """
    gravitationFriends are other GravitatedObject's which affect the force on this object.
    start_velocity is an (x, y) vector holding... Velocity!
    Size is in radius of circle
    """
    def __init__(self, x, y, size, start_velocity, turn_spd, mass, gravitationFriends):

        self.circle = pyglShapes.Circle(x, y, size, segments=10)
        self.in_circle = pyglShapes.Circle(x, y, size-1, segments=10, color=(0,0,0))

        self.velocity = start_velocity
        self.mass = mass
        self.physrotation = 0

        self.gravitationFriends = gravitationFriends
        self.drotation = turn_spd

    """
    Calculates and sets the next self.x, self.y and self.velocity, assuming spontaneous change.
    Sums F=g*m*m2/r^2 and uses the summed force vector in a=F/m. 

    I might try to use my new calculus knowledge to make this more precise (but slow), though that isn't necessary
    """
    def next_move(self):
        # Find the force vector
        forceVector = [0, 0]
        for mass in self.gravitationFriends:
            if mass == self:
                continue
            # Get lets to make calculations easier
            this_x = self.circle.x
            this_y = self.circle.y
            other_x = mass.circle.x
            other_y = mass.circle.y
            # Calculate force
            distanceSquared = (this_x-other_x)**2 + (this_y-other_y)**2
            forceScalar = self.mass*mass.mass*constants.gravConstant/distanceSquared
            forceX = math.cos(math.atan((other_y-this_y)/(other_x-this_x))) * forceScalar
            forceY = math.sin(math.atan((other_y-this_y)/(other_x-this_x))) * forceScalar
            # Make sure forces are in the right direction, atan is a bit tricky in this regard.
            if (other_x > this_x and forceX < 0) or (other_x < this_x and forceX > 0):
                forceX *= -1
            if (other_y > this_y and forceY < 0) or (other_y < this_y and forceY > 0):
                forceY *= -1
            forceVector[0] += forceX
            forceVector[1] += forceY

        # Apply force
        self.force_on_center(forceVector)

        # [--TODO--] Torque
        self.physrotation += self.drotation
        # Probably we could do some collision checks here

        self.in_circle.x = self.circle.x
        self.in_circle.y = self.circle.y

    """
    It is a common task to enact a force on the center of gravity.
    """
    def force_on_center(self, forceVector):
        acceleration = [forceVector[0]/self.mass, forceVector[1]/self.mass]
        
        self.velocity[0] += acceleration[0]
        self.velocity[1] += acceleration[1]
        
        self.circle.x += self.velocity[0]
        self.circle.y += self.velocity[1]
    
    """"def torque(self):
        pass"""

    """
    Single render, for testing
    """
    def render_function(self):
        self.circle.draw()
        self.in_circle.draw()


class AttachableObject(GravitatedObject, pyglSprite.Sprite):
    """
    attached might not be obvious, but this is the other object that this one is attached to
    orientation is in relation to attached object if attached to something, but is normal rotation if not attached to something
    """
    def __init__(self, sprite_img, spritesize, gravitationFriends, velocity=[0, 0], x=0, y=0, orientation=0, attached=None):
        pyglSprite.Sprite.__init__(self, sprite_img, x=x, y=y, subpixel=True)
        GravitatedObject.__init__(self, x, y, spritesize/2, velocity, 0, 0.25, gravitationFriends)

        self.scale = spritesize/self.height
        self.attached = attached
        self.rotation = orientation
        if self.attached:
            self.attached_rotation = orientation
            self.set_position()
            self.align_transformations()

        #self.circle.visible = False
        #self.in_circle.visible = False

    """
    Aligns the circle and sprite transformations
    Should be called after any change in orientation or position
    """
    def align_transformations(self):
        if self.attached:
            # Circle is irrelevant, but it should still follow
            self.circle.x = self.x
            self.circle.y = self.y
            self.physrotation = self.rotation

        else:
            # Other way around
            self.x = self.circle.x
            self.y = self.circle.y
            self.rotation = self.physrotation

    """
    Set coordinates based on position on attached object
    """
    def set_position(self):
        assert self.attached != None # bruh
        
        self.x = self.attached.circle.x + math.sin(self.rotation*math.pi/180)*(self.circle.radius + self.attached.circle.radius)
        self.y = self.attached.circle.y + math.cos(self.rotation*math.pi/180)*(self.circle.radius + self.attached.circle.radius)
        self.align_transformations()

    """
    Again, this just handles spontaneous transformations.
    Other forces placed on object is handled in parent
    """
    def next_move(self):
        if not self.attached:
            super().next_move() # If it isn't attached, so it behaves like any other gravitatedObject!
            return self.align_transformations()

        # Update orientation
        self.rotation = self.attached.physrotation + self.attached_rotation
        #print(self.rotation)
        self.set_position()

    """
    Attach object to other.
    Attaches based on closest landing point, so rotation is resolved afterwards
    """
    def attach(self, other):
        world_orientation = math.atan((self.y-other.circle.y)/(self.x-other.circle.x)) # Soon to be self.attached_rotation + self.attached.rotation
        self.attached = other
        self.x = other.circle.x
        self.y = other.circle.y
        # resolve orientation
        self.rotation = world_orientation
        self.attached_rotation = world_orientation-self.attached.physrotation

    def render_function(self):
        self.draw()