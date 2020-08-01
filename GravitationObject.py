"""
Contains base classes for gravity calculations.
Most of the math stays here.
"""
import math
import pyglet.shapes as pyglShapes
import pyglet.sprite as pyglSprite
import constants
from ctypes import CDLL, c_float, c_int, byref
from pyglet.graphics import Batch

render_batch = Batch()

planets = []

physicsLib = CDLL("physics.dylib")
physicsLib.addGravObject.restype = c_int

"""
Handles collision between two gravitatedObject's
Uses law of conservation of momentum and law of conservatino of energy
"""
def on_collision_get_normal(c1, other): # Gets normals for on_collision
    # Make sure the objects are sufficiently close
    assert c1.circle.radius + other.circle.radius + 1 > math.sqrt((c1.circle.x-other.circle.x)**2 + (c1.circle.y-other.circle.y)**2)
    centroidDistance = c1.circle.radius + other.circle.radius
    normalVelocityDir = [(other.circle.x-c1.circle.x)/centroidDistance, (other.circle.y-c1.circle.y)/centroidDistance] # Normalized to be length 1
    normalVelocityScalar = (normalVelocityDir[0]*c1.velocity[0] + normalVelocityDir[1]*c1.velocity[1]) # Length of self.velocity cancels out with cos() vector formula

    normalVelocity = [normalVelocityDir[0]*normalVelocityScalar, normalVelocityDir[1]*normalVelocityScalar]
    return normalVelocity

def check_collision(c1, other):
    # Return if distance between centers is less than the sum of radius
    return c1.circle.radius + other.circle.radius + 1 > math.sqrt((c1.circle.x-other.circle.x)**2 + (c1.circle.y-other.circle.y)**2)


"""
Converts polar to cartesian coordinates
First number is the angle (in degrees), second is length
"""
def to_cartesian(vec):
    return [math.cos(vec[0])*vec[1], math.sin(vec[0])*vec1]

"""Cartesian to polar coordinates"""
def to_polar(vec):
    return [math.atan(vec[1]/vec[0])*180/math.pi, math.sqrt(vec[0]**2 + vec[1]**2)]

def distance(vec1, vec2):
    return math.sqrt((vec1[0]-vec2[0])**2 + (vec1[1]-vec2[1])**2)

"""
Main object which contains mathematics for gravity
"""
class GravitatedObject:
    """
    gravitationFriends are other GravitatedObject's which affect the force on this object.
    start_velocity is an (x, y) vector holding... Velocity!
    Size is in radius of circle
    """
    def __init__(self, x, y, size, start_velocity, turn_spd, mass, visible=True):
        if visible:
            self.circle = pyglShapes.Circle(x, y, size, segments=10, batch=render_batch)
            self.in_circle = pyglShapes.Circle(x, y, size-1, segments=10, color=(0,0,0), batch=render_batch)
        else:
            self.circle = pyglShapes.Circle(x, y, size, segments=10)
            self.in_circle = pyglShapes.Circle(x, y, size-1, segments=10, color=(0,0,0))

        self.velocity = start_velocity
        self.mass = mass
        self.physrotation = 0
        self.drotation = turn_spd

        self.set_physics_data(first_call=True)

    def move(self, x, y, rotation=0):
        self.circle.x += x
        self.circle.y += y
        self.physrotation += rotation
        self.in_circle.x = self.circle.x
        self.in_circle.y = self.circle.y

        self.set_physics_data()

    """
    Calculates and sets the next self.x, self.y and self.velocity, assuming spontaneous change.
    Sums F=g*m*m2/r^2 and uses the summed force vector in a=F/m. 

    I might try to use my new calculus knowledge to make this more precise (but slow), though that isn't necessary
    """
    def next_move(self):
        # Find the force vector
        forceVector = [c_float(0.), c_float(0.)]
        physicsLib.getGravForce(self.id, byref(forceVector[0]), byref(forceVector[1]))
        forceVector[0] = forceVector[0].value
        forceVector[1] = forceVector[1].value
        # Apply force
        self.force_on_center(forceVector)

        # [--TODO--] Torque
        self.physrotation += self.drotation

        # Apply
        self.force_on_center(forceVector)
        self.move(self.velocity[0], self.velocity[1], self.drotation)

    """
    It is a common task to enact a force on the center of gravity.
    """
    def force_on_center(self, forceVector):
        acceleration = [forceVector[0]/self.mass, forceVector[1]/self.mass] # F=ma!
        
        self.velocity[0] += acceleration[0]
        self.velocity[1] += acceleration[1]

        self.set_physics_data()
    
    """"def torque(self):
        pass"""

    """
    Single render, for testing
    """
    def render_function(self):
        self.circle.draw()
        self.in_circle.draw()

    """
    Copies data into the physics calculations
    """
    def set_physics_data(self, first_call=False):
        x = c_float(self.circle.x)
        y = c_float(self.circle.y)
        velx = c_float(self.velocity[0])
        vely = c_float(self.velocity[1])
        mass = c_float(self.mass)
        if first_call:
            self.id = physicsLib.addGravObject(x, y, velx, vely, mass)
            return
        physicsLib.updateData(self.id, x, y, velx, vely, mass)

    def bounce(self, other):
        c1 = self

        centerDistance = c1.circle.radius + other.circle.radius

        dotProduct = (c1.velocity[0]-other.velocity[0])*(c1.circle.x-other.circle.x) + (c1.velocity[1]-other.velocity[1])*(c1.circle.y-other.circle.y)

        newVel = [c1.velocity[0] - 2*other.mass*dotProduct*(c1.circle.x-other.circle.x)/((c1.mass + other.mass)*centerDistance*centerDistance),
                  c1.velocity[1] - 2*other.mass*dotProduct*(c1.circle.y-other.circle.y)/((c1.mass + other.mass)*centerDistance*centerDistance)]
        newOtherVel = [other.velocity[0] - 2*other.mass*dotProduct*(other.circle.x-c1.circle.x)/((c1.mass + other.mass)*centerDistance*centerDistance), 
                       other.velocity[1] - 2*other.mass*dotProduct*(other.circle.y-c1.circle.y)/((c1.mass + other.mass)*centerDistance*centerDistance)]

        c1.velocity = newVel
        other.velocity = newOtherVel
        """while check_collision(c1, other):
            c1.move(c1.velocity[0], c1.velocity[1], rotation=0)
            other.move(other.velocity[0], other.velocity[1], rotation=0)"""

    def on_collision(self, other, first_caller=True):
        # All the physics is handled here, but we need to let the other object know about and react to the collision. For the sake of polymorphism.

        if first_caller:
            self.bounce(other)
            other.on_collision(self, first_caller=False)

class AttachableObject(GravitatedObject, pyglSprite.Sprite):
    """
    attached might not be obvious, but this is the other object that this one is attached to
    orientation is in relation to attached object if attached to something, but is normal rotation if not attached to something
    """
    def __init__(self, sprite_img, spritesize, velocity=[0, 0], x=0, y=0, orientation=0, mass=0.1, attached=None):
        pyglSprite.Sprite.__init__(self, sprite_img, x=x, y=y, subpixel=True, batch=render_batch)
        GravitatedObject.__init__(self, x, y, spritesize/2, velocity, 0, mass, visible=False)

        self.scale = spritesize/self.height
        self.attached = attached
        self.rotation = orientation
        if self.attached:
            self.attached_rotation = orientation
            self.set_position()
            self.align_transformations()

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

        self.set_physics_data()

    """
    Set coordinates based on position on attached object
    """
    def set_position(self):
        assert self.attached != None # bruh
        
        self.x = self.attached.circle.x + math.sin(self.rotation*math.pi/180)*(self.circle.radius + self.attached.circle.radius + 1.2)
        self.y = self.attached.circle.y + math.cos(self.rotation*math.pi/180)*(self.circle.radius + self.attached.circle.radius + 1.2)
        self.align_transformations()
        
        self.set_physics_data()

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

    def move(self, x, y, rotation):
        super().move(x, y, rotation)
        self.update(x=self.circle.x, y=self.circle.y, rotation=self.physrotation)

    """
    Attach object to other.
    Attaches based on closest landing point, so rotation is resolved afterwards
    """
    def attach(self, other):
        self.attached = other
        self.attached_rotation = self.rotation - other.physrotation

    """
    Deattach, will follow its own physics freely
    """
    def deattach(self):
        if not self.attached: return
        self.velocity = [0, 0]
        # Calculate new velocity
        newVelocityX = math.sin(self.rotation*math.pi/180) * .5
        newVelocityY = math.cos(self.rotation*math.pi/180) * .5
        self.force_on_center([newVelocityX*self.mass, newVelocityY*self.mass])

        self.move(self.velocity[0], self.velocity[1], 0)

        self.drotation = self.attached.drotation
        self.attached = None

    def render_function(self):
        self.draw()


planets.append(GravitatedObject(300, 350, 10, [0, 0], 1, 25))
planets.append(GravitatedObject(500, 350, 10, [0, 0], 1, 25))