# game_world.py
# game_world.py (손석민 교수님 정식 버전)
objects = [[], []]  # 0: 배경, 1: 캐릭터
collision_pairs = {}

def add_object(o, layer):
    objects[layer].append(o)

def add_objects(ol, layer):
    objects[layer] += ol

def remove_object(o):
    for layer in objects:
        if o in layer:
            layer.remove(o)
            return
    raise ValueError("Cannot delete non existing object")

def clear():
    for layer in objects:
        layer.clear()

def update():
    for layer in objects:
        for o in layer:
            o.update()

def render():
    for layer in objects:
        for o in layer:
            o.draw()

def add_collision_pair(group, a, b):
    if group not in collision_pairs:
        collision_pairs[group] = [[], []]
    if a:
        collision_pairs[group][0].append(a)
    if b:
        collision_pairs[group][1].append(b)

def handle_collisions():
    for group, pairs in collision_pairs.items():
        for a in pairs[0]:
            for b in pairs[1]:
                if a == b: continue
                if collide(a, b):
                    a.handle_collision(group, b)
                    b.handle_collision(group, a)

def collide(a, b):
    left_a, bottom_a, right_a, top_a = a.get_bb()
    left_b, bottom_b, right_b, top_b = b.get_bb()
    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False
    return True