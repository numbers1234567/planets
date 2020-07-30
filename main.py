import players
import pyglet
import pyglet.window.key as pyglKey
from GravitationObject import on_collision, render_batch, planets
import time

soldier = players.Soldier(attached=planets[0])
planets.append(soldier)

a_pressed = False

class main(pyglet.window.Window):
    def __init__(self):
        super().__init__(800, 700)
        pyglet.clock.schedule_interval(self.update, 0.0167)
        self.left_pressed = False
        self.right_pressed = False
        self.attach_button = False

    def update(self, dt):
        start = time.time()
        for i in range(len(planets)):
            planet = planets[i]
            planet.next_move()
            for x in range(i, len(planets)):
                otherPlanet = planets[x]
                if otherPlanet != planet:
                    on_collision(planet, otherPlanet)

        if self.left_pressed:
            soldier.walk(-1)
        if self.right_pressed:
            soldier.walk(1)
        soldier.next_move()

    def on_draw(self):
        self.clear()
        render_batch.draw()
        #soldier.render_function()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglKey.A:
            self.left_pressed = True
        
        if symbol == pyglKey.D:
            self.right_pressed = True

        if symbol == pyglKey.SPACE:
            soldier.deattach()

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglKey.A:
            self.left_pressed = False
        
        if symbol == pyglKey.D:
            self.right_pressed = False

    def on_mouse_press(self, x, y, button, modifiers):
        return
        planets.append(GravitatedObject(x, y, 20, [0, 0], 5, 2, planets))


if __name__=="__main__":
    main()
    pyglet.app.run()