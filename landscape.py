#!/usr/bin/env python3

import random
import time
from collections import defaultdict
from pathlib import Path
import numpy as np
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import basic_lighting_shader, lit_with_shadows_shader
from perlin import perlin
from utils import timer

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

def smoothen_landscape_normals(mesh, grid_vertices):
    """ Custom implementation of normals smoothing that's linear with number of vertexes,
        as opposed to the costly squared complexity of the default implementation
    """
    for x, z_vert in grid_vertices.items():
        for z, verts_indices in z_vert.items():
            average_normal = sum([mesh.normals[e] for e in verts_indices]) / 3
            for index in verts_indices:
                mesh.normals[index] = average_normal
    mesh.generate()

app = Ursina()
level_parent = Entity(model=Mesh(vertices=[], uvs=[]), texture='brick', color=color.dark_gray,
                      shader=lit_with_shadows_shader)
# level_parent.input = landscape_input

width = length = 100
noise_start = time.time()
with timer('generate noise'):
    lin_x = np.linspace(0, width, width)
    lin_z = np.linspace(0, length, length)
    x, z = np.meshgrid(lin_x, lin_z)
    noise4 = perlin(x/128, z/128) # largest scale
    noise3 = perlin(x/32, z/32) # largest scale
    noise2 = perlin(x/8, z/8) # smooth
    noise1 = perlin(x/2, z/2) # smallest scale
    noise = noise4 * 64 + noise3 * 16 +  noise2 * 4 + noise1 * 1
print('landscape range =', noise.min(), noise.max())

start_time = time.time()
grid_vertices = defaultdict(lambda: defaultdict(list))
vertex_index = 0
with timer('create vertices'):
    for x in range(1, width):
        for z in range(1, length):
            # add two triangles for each new point
            level_parent.model.vertices += (
                (x, noise[x, z], z),
                (x-1, noise[x-1, z], z),
                (x-1, noise[x-1, z-1], z-1),
                (x, noise[x, z], z),
                (x-1, noise[x-1, z-1], z-1),
                (x, noise[x, z-1], z-1)
            )
            # save overlapping vertex indices for smoothing
            grid_vertices[x][z].append(vertex_index)
            vertex_index += 1
            grid_vertices[x-1][z].append(vertex_index)
            vertex_index += 1
            grid_vertices[x-1][z-1].append(vertex_index)
            vertex_index += 1
            grid_vertices[x][z].append(vertex_index)
            vertex_index += 1
            grid_vertices[x-1][z-1].append(vertex_index)
            vertex_index += 1
            grid_vertices[x][z-1].append(vertex_index)
            vertex_index += 1

with timer('project_uvs'):
    level_parent.model.project_uvs() # for texture
with timer('generate model'):
    level_parent.model.generate()
with timer('generate_normals'):
    level_parent.model.generate_normals(smooth=False) # for lighting
with timer('smoothen normals'):
    smoothen_landscape_normals(level_parent.model, grid_vertices)
with timer('set mesh collider'):
    level_parent.collider = 'mesh'
with timer('set shader'):
    level_parent.shader = lit_with_shadows_shader
# EditorCamera()
Sky()#color=color.cyan)
print(f'created landscape in {time.time()-start_time:.2f}s')

# dec_tree_model = load_model('Deciduous_Tree.obj')
# dec_tree_model.generate_normals()
# print(len(dec_tree_model.uvs), dec_tree_model.uvs[:10])
# tree = Entity(model=dec_tree_model, position=(15, noise[15, 15], 15), texture='Deciduous_Tree.png',
#               scale=3, collider='mesh')

with timer('load tree models'):
    tree_models = [load_model(f'tree{i+1}') for i in range(5)]

# put fewer trees the higher the landscape is (i.e. barren mountain tops)
heightmap_flat = noise.reshape(-1)
heightmap_norm = (heightmap_flat - noise.min()) / noise.ptp()
location_prob = (1 - heightmap_norm) ** 2

def create_tree(loc_idx):
    x = loc_idx // width
    z = loc_idx % width
    y = noise[x, z] - .1
    return Entity(model=deepcopy(random.choice(tree_models)), texture='tex1.png', position=(x, y, z),
                  scale=.5, collider='mesh', rotation=(0, random.uniform(0, 360), 0))

with timer('create trees'):
    n_trees = 100
    tree_locations = random.choices(range(len(heightmap_flat)), location_prob, k=n_trees)
    trees = [create_tree(loc_idx) for loc_idx in tree_locations]
    # trees = ThreadPool().map(create_tree, range(n_trees), chunksize=n_trees//cpu_count())
    # print(len(trees))

print(f'level generation took {time.time()-start_time:.2f}s')
player_y = noise[width//2, length//2] #+ 10
player = FirstPersonController(position=(width//2, player_y, length//2))
# with timer('create collision_zone'):
#     collision_zone = CollisionZone(parent=player, radius=32)
#     level_parent.collision = True

# alpaca = Entity(model='alpaca.obj', position=(width/2+2, noise[width//2+2, length//2+2], length/2+2), texture='alpaca1.png')

# capybara = Animal('capybara', x=width//2-2, z=length//2-2, scale=.5, texture='capybara1_texture.png', noise=noise)

# capybara = Entity(model='capybara.obj', position=(width/2-2, noise[width//2-2, length//2-2], length/2-2), scale=.5, texture='capybara1_texture.png')
# scene.fog_color = color.rgb(200,200,200)
# scene.fog_density = 0.05
# AmbientLight()
# pivot = Entity()
# sun = DirectionalLight(y=20, rotation=(90+30,90,0))
# sun._light.show_frustum()
# DirectionalLight(parent=pivot, y=20, z=3, shadows=True)
app.run()
