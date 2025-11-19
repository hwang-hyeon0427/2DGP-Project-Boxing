world = [[], [], []] # layers for game objects

def add_object(o, depth):
    world[depth].append(o)

def add_objects(ol, depth):
    world[depth] += ol

def update():
    for layer in world:
        for o in layer:
            o.update()

def render():
    for layer in world:
        for o in layer:
            o.draw()

def remove_collision_object(o):
    pass

def clear():
    for layer in world:
        layer.clear()

def collide(a, b):
    pass

collision_pairs = {}
def add_collision_pair(group, a, b):
    pass

def handle_collisions():
    pass