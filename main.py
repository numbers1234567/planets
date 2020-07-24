from GravitationObject import GravitatedObject, AttachableObject
import players
import pyglet

planets = []
planets.append(GravitatedObject(100, 300, 5, [0, 0.3], 0.5, planets))
planets.append(GravitatedObject(500, 300, 5, [0, -0.3], 0.5, planets))
planets.append(GravitatedObject(300, 300, 10, [0, 0], 1, []))
print(planets)



thing = AttachableObject()

window = pyglet.window.Window(600, 600)

def update(dt):
    for planet in planets:
        planet.next_move()

@window.event
def on_draw():
    window.clear()
    for planet in planets:
        planet.render_function()

pyglet.clock.schedule_interval(update, 0.0167)
pyglet.app.run()