from GravitationObject import GravitatedObject, AttachableObject
import players
import pyglet

planets = []
planets.append(GravitatedObject(100, 300, 5, [0, 0.3], 1, 0.5, planets))
planets.append(GravitatedObject(500, 300, 5, [0, -0.3], 1, 0.5, planets))
planets.append(GravitatedObject(300, 300, 10, [0, 0], 1, 1, []))
print(planets)

img = pyglet.image.load("bro.png")
img.anchor_x = int(img.width/2)
img.anchor_y = int(img.height/2)

thing = AttachableObject(img, 20, planets, x=10, y=10, attached=planets[1])

window = pyglet.window.Window(600, 600)

def update(dt):
    for planet in planets:
        planet.next_move()

    thing.next_move()

@window.event
def on_draw():
    window.clear()
    for planet in planets:
        planet.render_function()
    thing.render_function()

pyglet.clock.schedule_interval(update, 0.0167)
pyglet.app.run()