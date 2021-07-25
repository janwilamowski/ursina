import random
import time
from pathlib import Path
import numpy as np
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import basic_lighting_shader, lit_with_shadows_shader
from perlin import perlin

""" TODO
- coloring according to height or (better) curvature
- figure out uvs & get textures
"""

BASE = Path(__file__).resolve().parent

def update():
    if held_keys['left mouse down']:
        print('click')
    elif held_keys['1']:
        print(1)

def landscape_input(self, key=None):
    print(self, key)
    if self.hovered and key == 'left mouse down':
        print('click')

app = Ursina()
level_parent = Entity(model=Mesh(vertices=[], uvs=[]), texture='brick', color=color.dark_gray,
                      shader=lit_with_shadows_shader)
# level_parent.input = landscape_input

width = length = 50
noise_start = time.time()
lin_x = np.linspace(0, width, width)
lin_z = np.linspace(0, length, length)
x, z = np.meshgrid(lin_x, lin_z)
noise1 = perlin(x/8, z/8)
noise2 = perlin(x/2, z/2)
noise = noise1 * 4 + noise2 * 1
noise_time = time.time() - noise_start
# print(noise.min(), noise.max())

start_time = time.time()
for x in range(1, width):
    for z in range(1, length):
        # add two triangles for each new point
        level_parent.model.vertices += (
            (x, noise[x, z], z),
            (x-1, noise[x-1, z], z),
            (x-1, noise[x-1, z-1], z-1)
        )
        level_parent.model.vertices += (
            (x, noise[x, z], z),
            (x-1, noise[x-1, z-1], z-1),
            (x, noise[x, z-1], z-1)
        )
        # level_parent.model.uvs += (
        #     (1.0, 0.0), (0.0, 1.0), (1.0, 1.0),
        #     (0.0, 1.0), (1.0, -0.0), (1.0, 1.0)
        # )

level_parent.model.project_uvs()
level_parent.model.generate()
level_parent.model.generate_normals() # for lighting
level_parent.collider = 'mesh'
level_parent.shader = lit_with_shadows_shader
print('landscape created')
# EditorCamera()
Sky()#color=color.cyan)

# dec_tree_model = load_model('Deciduous_Tree.obj')
# dec_tree_model.generate_normals()
# print(len(dec_tree_model.uvs), dec_tree_model.uvs[:10])
# tree = Entity(model=dec_tree_model, position=(15, noise[15, 15], 15), texture='Deciduous_Tree.png',
#               scale=3, collider='mesh')

tree_models = {i: load_model(f'tree{i+1}') for i in range(5)}
n_trees = 100
for i in range(n_trees):
    x = random.randint(0, width-1)
    z = random.randint(0, length-1)
    y = noise[x, z] - .1
    Entity(model=deepcopy(tree_models[random.randint(0, 4)]), texture='tex1.png', position=(x, y, z),
           scale=.5, collider='mesh', rotation=(0, random.uniform(0, 360), 0))

print(f'level generation took {time.time()-start_time:.2f}s, of which were {noise_time:.2f}s for noise')
player = FirstPersonController(position=(width/2, 50, length/2))

# scene.fog_color = color.rgb(200,200,200)
# scene.fog_density = 0.05
# AmbientLight()
# pivot = Entity()
# sun = DirectionalLight(y=20, rotation=(90+30,90,0))
# sun._light.show_frustum()
# DirectionalLight(parent=pivot, y=20, z=3, shadows=True)
app.run()
