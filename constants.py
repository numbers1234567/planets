import pyglet.image

gravConstant = 10#Gravitational constant

speedFactor = 0.1

maxDO = 15

soldier_img = pyglet.image.load("bro.jpg")
soldier_img.anchor_x = int(soldier_img.width/2)
soldier_img.anchor_y = int(soldier_img.height/2)