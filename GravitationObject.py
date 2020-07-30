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
        world_orientation = math.atan((self.y-other.circle.y)/(self.x-other.circle.x)) # Soon to be self.attached_rotation + self.attached.rotation
        self.attached = other
        # resolve orientation
        self.rotation = world_orientation
        self.attached_rotation = world_orientation-self.attached.physrotation
        self.set_position()
        self.set_physics_data()

    """
    Deattach, will follow its own physics freely
    """
    def deattach(self):
        if not self.attached: return
        # Calculate new velocity
        newVelocityX = math.sin(self.rotation*math.pi/180) * .5
        newVelocityY = math.cos(self.rotation*math.pi/180) * .5
        self.force_on_center([newVelocityX*self.mass, newVelocityY*self.mass])

        self.drotation = self.attached.drotation
        self.attached = None

    def render_function(self):
        self.draw()

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

def on_collision(c1, other):
    if c1.circle.radius + other.circle.radius + 1 <= math.sqrt((c1.circle.x-other.circle.x)**2 + (c1.circle.y-other.circle.y)**2):
        return
    
    # Make sure the objects are sufficiently close
    normalVelocity = on_collision_get_normal(c1, other)
    normalScalar = math.sqrt(normalVelocity[0]**2 + normalVelocity[1]**2)
    
    otherNormal = on_collision_get_normal(other, c1)
    otherScalar = math.sqrt(otherNormal[0]**2 + otherNormal[1]**2)

    if c1 not in planets:
        # Other is not affected by this one's physics
        c1.velocity = [-normalVelocity[0], -normalVelocity[1]]
        c1.move(c1.velocity[0], c1.velocity[1], 0)
        return
    if other not in planets:
        other.velocity = [-otherNormal[0], -otherNormal[1]]
        other.move(other.velocity[0], other.velocity[1], 0)
        return
    if normalScalar == 0 or otherScalar == 0:
        return
    # Now to use our equations!
    e_constant = c1.mass*(normalScalar**2) + other.mass*(otherScalar**2)
    m_constant = c1.mass*normalScalar + other.mass*otherScalar

    newOtherScalar = m_constant + math.sqrt(m_constant**2 - (c1.mass + other.mass)*((m_constant**2) - c1.mass*e_constant)/other.mass)
    newOtherScalar /= c1.mass + other.mass
    newOtherVelocity = [otherNormal[0]*newOtherScalar/otherScalar, otherNormal[1]*newOtherScalar/otherScalar]
    #if oth
    other.velocity[0] -= otherNormal[0] - newOtherVelocity[0]
    other.velocity[1] -= otherNormal[1] - newOtherVelocity[1]

    newNormalScalar = (m_constant - other.mass*newOtherScalar)/c1.mass
    newNormalVelocity = [normalVelocity[0]*newNormalScalar/normalScalar, normalVelocity[1]*newNormalScalar/normalScalar]
    
    c1.velocity[0] -= normalVelocity[0] - newNormalVelocity[0]
    c1.velocity[1] -= normalVelocity[1] - newNormalVelocity[1]
    # If the distance still isn't closed
    if distance([c1.circle.x + c1.velocity[0], c1.circle.y + c1.velocity[1]], [other.circle.x + other.velocity[0], other.circle.y + other.velocity[1]]) < c1.circle.radius + other.circle.radius + 1:
        c1.velocity[0] -= 2*newNormalVelocity[0]
        c1.velocity[1] -= 2*newNormalVelocity[1]
        other.velocity[0] -= 2*newOtherVelocity[0]
        other.velocity[1] -= 2*newOtherVelocity[1]
    
    c1.circle.x += c1.velocity[0]
    c1.circle.y += c1.velocity[1]
    other.circle.x += other.velocity[0]
    other.circle.y += other.velocity[1]
    c1.in_circle.x = c1.circle.x
    c1.in_circle.y = c1.circle.y
    other.in_circle.x = other.circle.x
    other.in_circle.y = other.circle.y

    c1.set_physics_data()
    other.set_physics_data()

planets.append(GravitatedObject(400, 350, 10, [0, 0], 5, 0.5))

        