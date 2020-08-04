# planets
A program which uses physics concepts, such as the gravitational force equation, law of conservation of momentum, and Newton's famous second law of motion, to create a somewhat unwieldly but fun game where you play as a space marine.

This uses a Python library called pyglet which is a high-level binding to OpenGL, much like how pygame is bound to SDL.

Something I love about this is, if you start with a certain state for the program, there's no randomness, despite the apparent chaos. The state of the program after a certain number of frames is always calculable, demonstrated by running the program multiple times from the start state. That is, unless you change something manually.
