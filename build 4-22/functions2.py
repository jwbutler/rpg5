""" Most of the functions in this module concern level generation; see levels.py """

import pygame
from classes import *
from units import *
from enemy_humans import *
from wizards import * #Unused
from zombies import *
from generators import *
from functions import generate_tile
import copy

tiles = {}
#tiles['dirt'] = ["tga/dirt_24x12_" + str(x) + ".tga" for x in [1,2,3,4]]
#tiles['stone'] = ["tga/floor_24x12_stone_" + str(x) + ".tga" for x in [1,2,3,4]]
#tiles['grassdirt'] = ["tga/grassdirt_24x12_" + str(x) + ".tga" for x in [1,2,3,4]]
#tiles['grass'] = ["tga/grass_24x12_" + str(x) + ".tga" for x in [1,2,3,4]]
tiles['water'] = ["tga/water_" + str(x) + ".tga" for x in [1,2,3,4]]
tiles['dirtwater'] = ["tga/dirtwater_" + str(x) + ".tga" for x in [1,2,3,4]]
tile_surfaces_dict = {}
for (key,filename_list) in tiles.items():
  surface_list = [pygame.image.load(filename) for filename in filename_list]
  for surface in surface_list:
    surface.set_colorkey((255,255,255))
  tile_surfaces_dict[key] = surface_list
tile_surfaces_dict['grass'] = [generate_tile((0,128,0),0.1,0.3,True) for x in range(8)]
tile_surfaces_dict['grassdirt'] = [generate_tile((48,96,0),0.2,0.4,False) for x in range(8)]
tile_surfaces_dict['dirt'] = [generate_tile((72,48,0),0.2,0.4,True) for x in range(8)]
tile_surfaces_dict['rocky'] = [generate_tile((64,64,64), 0.2,0.5, True) for x in range(8)]
tile_surfaces_dict['stone'] = [generate_tile((96,96,96), 0.2,0.2, True) for x in range(8)]
tile_color_dict = {
  (128,128,128): 'stone',
  (128,64,0): 'dirt',
  (0,255,0): 'grass',
  (128,128,0): 'grassdirt',
  (0,128,128): 'water',
  (0,128,255): 'water',
  (0,255,255): 'dirtwater',
  (0,128,0): 'grass', #tree
  (255,0,255): 'grass', #boulder
  (128,0,128): 'grass', #rocks
  (255,128,0): 'dirt', #fire
  (255,192,128): 'dirt', #fire
  (0,0,0): 'rocky', #rocky floor
  (96,96,96): 'rocky', #stalagmite
  (128,0,64): 'rocky', #cave rock
  (128,64,64): 'rocky', #rocks on rocky floor
  (192,0,192): 'rocky', #boulder on rocky floor
}

def rgb_to_tile((r,g,b), tile_color_dict, tile_surfaces_dict, default_tile_type):
  if (r,g,b) in tile_color_dict.keys():
    tile_type = tile_color_dict[(r,g,b)]
    tile_surface_list = tile_surfaces_dict[tile_type]
    tile_surface = random.choice(tile_surface_list)
  else:
    tile_surface_list = tile_surfaces_dict[default_tile_type]
    tile_surface = random.choice(tile_surface_list)
  return tile_surface

def rgb_to_tile_OLD((r,g,b)):
  if (r,g,b) == (128,128,128):
    tiles = ["tga/floor_24x12_stone_" + str(x) + ".tga" for x in [1,2,3,4]]
  elif (r,g,b) == (128,64,0):
    tiles = ["tga/dirt_24x12_" + str(x) + ".tga" for x in [1,2,3,4]]
  elif (r,g,b) == (0,255,0):
    tiles = ["tga/grass_24x12_" + str(x) + ".tga" for x in [1,2,3,4]]
  elif (r,g,b) == (128,128,0):
    tiles = ["tga/grassdirt_24x12_" + str(x) + ".tga" for x in [1,2,3,4]]
  elif (r,g,b) == (0,128,0): #tree
    tiles = ["tga/grass_24x12_" + str(x) + ".tga" for x in [1,2,3,4]]
  elif (r,g,b) == (255,0,255): #boulder
    tiles = ["tga/grass_24x12_" + str(x) + ".tga" for x in [1,2,3,4]]
  elif (r,g,b) == (128,0,128): #rocks
    tiles = ["tga/grass_24x12_" + str(x) + ".tga" for x in [1,2,3,4]]
  elif (r,g,b) == (0,128,128): #water
    tiles = ["tga/water_" + str(x) + ".tga" for x in [1,2,3,4]]  
  elif (r,g,b) == (255,128,0): #lava
    tiles = ["tga/dirt_24x12_" + str(x) + ".tga" for x in [1,2,3,4]]
  elif (r,g,b) == (255,192,128): #lava
    tiles = ["tga/dirt_24x12_" + str(x) + ".tga" for x in [1,2,3,4]]
  elif (r,g,b) == (0,255,255): #dirtwater
    tiles = ["tga/dirtwater_" + str(x) + ".tga" for x in [1,2,3,4]]  
  else: #player start, et al
    tiles = ["tga/dirt_24x12_" + str(x) + ".tga" for x in [1,2,3,4]]
  surface = pygame.image.load(random.choice(tiles))
  surface.set_colorkey((255,255,255))
  return surface
  
def rgb_to_wall_icons((r,g,b)):
  if (r,g,b) == (192,192,192):
    icons = ['tga/wall_24x39_rocks1.tga']
  elif (r,g,b) == (0,0,128):
    icons = ['tga/wall_24x39_rocks1.tga']
  elif (r,g,b) == (0,0,255):
    icons = ['tga/wall_24x39_rocks1.tga']
  elif (r,g,b) == (128,0,0): #wood
    icons = ['tga/wall_12x39_wood_column.tga']
  else:
    icons = []
  return icons

def rgb_to_wall_offset((r,g,b)):
  offset = 0
  if (r,g,b) == (192,192,192):
    offset = 0
  elif (r,g,b) == (0,0,128):
    offset = 1
  elif (r,g,b) == (0,0,255):
    offset = 2
  elif (r,g,b) == (0,128,128): #water
    offset = 0
  elif (r,g,b) == (255,128,0): #fire
    offset = 0
  elif (r,g,b) == (255,192,128): #fire
    offset = 0
  elif (r,g,b) == (0,255,255): #dirtwater
    offset = 0    
  elif (r,g,b) == (128,0,0):
    offset = 0
  return offset
  
def rgb_to_walls((r,g,b), (x,y)):
  icons = rgb_to_wall_icons((r,g,b))
  offset = rgb_to_wall_offset((r,g,b))
  walls = []
  if icons:
    for z in range(offset+1):
      wall = Wall(x, y, random.choice(icons), z)
      walls.append(wall)
  return walls
  
def rgb_to_counters((r,g,b), (x,y)):
  #Results are in list form for easy addition to game.counters list
  if (r,g,b) == (128,0,255):
    return [Counter(x, y, "tga/counter_stone_1.tga", 0)]
  elif (r,g,b) == (128,128,64):
    return [Counter(x, y, "tga/counter_wood_1.tga", 0)]
  elif (r,g,b) == (128,0,64):
    return [Counter(x, y, random.choice(cave_rock_icons), 0)]
  elif (r,g,b) == (96,96,96):
    return [Counter(x, y, random.choice(stalagmite_icons), 0)]
  else:
    return []
    
def rgb_to_trees((r,g,b), (x,y)):
  trees = []
  icons = ["tga/tree4.tga", "tga/tree5.tga", "tga/tree6.tga"]
  if (r,g,b) == (0,128,0):
    trees.append(Tree(x, y, random.choice(icons), 0))
  return trees
  
def rgb_to_rocks((r,g,b), (x,y)):
  rocks = []
  #icons = ["tga/rocks_24x12_1.tga", "tga/rocks_24x12_2.tga", "tga/rocks_24x12_3.tga"]
  icons = ["tga/floor_rocks_1.tga", "tga/floor_rocks_2.tga", "tga/floor_rocks_3.tga"]  
  if (r,g,b) == (128,0,128):
    rocks.append(Rocks(x, y))
  elif (r,g,b) == (128,64,64):
    rocks.append(Rocks(x, y))
  return rocks

def rgb_to_water_tiles((r,g,b), (x,y), water_frames):
  #doesn't include still water
  water_tiles = []
  if (r,g,b) == (0,128,128):
    water_tiles.append(WaterTile(water_frames, (x,y)))
  return water_tiles
  
def rgb_to_boulders((r,g,b), (x,y)):
  boulders = []
  icons = ["tga/boulder_24x12_1.tga", "tga/boulder_24x12_2.tga", "tga/boulder_24x12_3.tga"]
  if (r,g,b) == (255,0,255):
    boulders.append(Boulder(x, y, random.choice(icons), 0)) #on grass
  if (r,g,b) == (192,0,192):
    boulders.append(Boulder(x, y, random.choice(icons), 0)) #on rocky
  return boulders
  
def rgb_to_fire_tiles((r,g,b), (x,y), fire_frames, fire_frames_small):
  fire_tiles = []
  if (r,g,b) == (255,0,128): #fire
    fire_tiles.append(FireTile(fire_frames, (x,y), 3))
  elif (r,g,b) == (255,192,128): #fire small
    fire_tiles.append(FireTile(fire_frames_small, (x,y), 2))
  return fire_tiles
  
def rgb_to_crops((r,g,b), (x,y)):
  crops = []
  shrub_icons = ["tga/shrubs_"+str(n)+".tga" for n in [1,2,3]]
  darkshrub_icons = ["tga/darkshrub_"+str(n)+".tga" for n in [1,2,3]]  
  grass_shrub_frequency = 0.005
  if (r,g,b) == (255,255,128):
    crops.append(Crops(x, y, 'tga/crops_transparent.tga', 0))
  elif (r,g,b) == (0,255,0): #small chance of shrubs on grass
    if random.random() <= grass_shrub_frequency:
      crops.append(Crops(x, y, random.choice(shrub_icons), 0))
  elif (r,g,b) == (0,0,0): #small chance of shrubs on grass - what's black?
    if random.random() <= grass_shrub_frequency:
      crops.append(Crops(x, y, random.choice(darkshrub_icons), 0))
  return crops
  
def pixel_array_to_trees(pixel_array):
  trees = []
  icons = ["tga/tree4.tga", "tga/tree5.tga", "tga/tree6.tga"]
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
      if (r,g,b) == (0,128,0):
        trees.append(Tree(x, y, random.choice(icons), 0))
  return trees
  
def pixel_array_to_boulders(pixel_array):
  boulders = []
  icons = ["tga/boulder_24x12_1.tga", "tga/boulder_24x12_2.tga", "tga/boulder_24x12_3.tga"]
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
      if (r,g,b) == (255,0,255):
        boulders.append(Boulder(x, y, random.choice(icons), 0)) #on grass
      if (r,g,b) == (192,0,192):
        boulders.append(Boulder(x, y, random.choice(icons), 0)) #on rocky
  return boulders
  
def pixel_array_to_rocks(pixel_array):
  rocks = []
  #icons = ["tga/rocks_24x12_1.tga", "tga/rocks_24x12_2.tga", "tga/rocks_24x12_3.tga"]
  icons = ["tga/floor_rocks_1.tga", "tga/floor_rocks_2.tga", "tga/floor_rocks_3.tga"]  
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
      if (r,g,b) == (128,0,128):
        rocks.append(Rocks(x, y, random.choice(icons), 0))
      elif (r,g,b) == (128,64,64):
        rocks.append(Rocks(x, y, random.choice(icons), 0))
  return rocks
  
def pixel_array_to_counters(pixel_array):
  t1 = pygame.time.get_ticks()
  # Also includes cave rocks, stalagmites
  counters = []
  cave_rock_icons = ["tga/cave_rocks_"+str(n)+".tga" for n in [1,2,3]]
  stalagmite_icons = ["tga/stalagmite_24x39_"+str(n)+".tga" for n in [1,2,3]]
  indexed_rgb = {}
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      indexed = pixel_array[x][y]
      if indexed in indexed_rgb.keys():
        (r,g,b,a) = indexed_rgb[indexed]
      else:
        (r,g,b,a) = pixel_array.surface.unmap_rgb(indexed)
        indexed_rgb[indexed] = (r,g,b,a)
      if (r,g,b) == (128,0,255):
        counters.append(Counter(x, y, "tga/counter_stone_1.tga", 0))
      elif (r,g,b) == (128,128,64):
        counters.append(Counter(x, y, "tga/counter_wood_1.tga", 0))
      elif (r,g,b) == (128,0,64):
        counters.append(Counter(x, y, random.choice(cave_rock_icons), 0))
      elif (r,g,b) == (96,96,96):
        counters.append(Counter(x, y, random.choice(stalagmite_icons), 0))
  t2 = pygame.time.get_ticks()
  print "PATC:", t2-t1, len(counters)
  return counters

def pixel_array_to_floor(pixel_array, tile_color_dict, tile_surfaces_dict, default_tile_type):
  #floor = Floor(["tga/black_floor_24x12.tga"], pixel_array.surface.get_rect())
  floor = BlankFloor(pixel_array.surface.get_rect())
  indexed_rgb = {}

  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      indexed = pixel_array[x][y]
      if indexed in indexed_rgb.keys():
        (r,g,b,a) = indexed_rgb[indexed]
      else:
        (r,g,b,a) = pixel_array.surface.unmap_rgb(indexed)
        indexed_rgb[indexed] = (r,g,b,a)
      floor.tiles[(x,y)] = rgb_to_tile((r,g,b), tile_color_dict, tile_surfaces_dict, default_tile_type)
  return floor
  
def pixel_array_to_floor_OLD(pixel_array, tile_color_dict, tile_surfaces_dict, default_tile_type):
  t1 = pygame.time.get_ticks()
  #floor = Floor(["tga/black_floor_24x12.tga"], pixel_array.surface.get_rect())
  floor = BlankFloor(pixel_array.surface.get_rect())
  indexed_rgb = {}
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      indexed = pixel_array[x][y]
      if indexed in indexed_rgb.keys():
        (r,g,b,a) = indexed_rgb[indexed]
      else:
        (r,g,b,a) = pixel_array.surface.unmap_rgb(indexed)
        indexed_rgb[indexed] = (r,g,b,a)
      floor.tiles[(x,y)] = rgb_to_tile((r,g,b), tile_color_dict, tile_surfaces_dict, default_tile_type)
  t2 = pygame.time.get_ticks()
  print "PATF", t2-t1, m, n
  return floor  
  
def pixel_array_to_water_tiles(pixel_array):
  #doesn't include still water
  water_filenames = ["tga/water_" + str(n) + ".tga" for n in [1,2,3,4]]
  water_frames = [pygame.image.load(f) for f in water_filenames]
  for f in water_frames:
    f.set_colorkey((255,255,255))
  water_tiles = []
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
      if (r,g,b) == (0,128,128):
        water_tiles.append(WaterTile(water_frames, (x,y)))
  return water_tiles

def pixel_array_to_fire_tiles(pixel_array):
  fire_filenames = ["tga/floor_fire_" + str(n) + ".tga" for n in [1,2,3,4]]
  fire_frames = [pygame.image.load(f) for f in fire_filenames]
  fire_filenames_small = ["tga/floor_fire_small_" + str(n) + ".tga" for n in [1,2,3,4]]
  fire_frames_small = [pygame.image.load(f) for f in fire_filenames_small]  
  for f in fire_frames + fire_frames_small:
    f.set_colorkey((255,255,255))
  fire_tiles = []
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
      if (r,g,b) == (255,0,128): #fire
        fire_tiles.append(FireTile(fire_frames, (x,y), 3))
      elif (r,g,b) == (255,192,128): #fire small
        fire_tiles.append(FireTile(fire_frames_small, (x,y), 2))
  return fire_tiles
  
def pixel_array_to_walls(pixel_array):
  walls = []
  indexed_rgb = {}
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      indexed = pixel_array[x][y]
      if indexed in indexed_rgb.keys():
        (r,g,b,a) = indexed_rgb[indexed]
      else:
        (r,g,b,a) = pixel_array.surface.unmap_rgb(indexed)
        indexed_rgb[indexed] = (r,g,b,a)
      icons = rgb_to_wall_icons((r,g,b))
      if icons:
        offset = rgb_to_wall_offset((r,g,b))
        for z in range(offset+1):
          wall = Wall(x, y, random.choice(icons), z)
          walls.append(wall)
  return walls
  
def pixel_array_to_invisible_walls(pixel_array):
  walls = []
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
    if (r,g,b) in [(0,128,128), #river
                   (255,128,0), #fire?
                   (0,255,255), #edge of river
                   (255,192,128) #more fire?
                  ]:
      wall = Wall(x, y, 'tga/wall_24x39_rocks1.tga', 1) #try w/o the icon next time
  return walls
  
def pixel_array_to_crops(pixel_array):
  crops = []
  shrub_icons = ["tga/shrubs_"+str(n)+".tga" for n in [1,2,3]]
  darkshrub_icons = ["tga/darkshrub_"+str(n)+".tga" for n in [1,2,3]]  
  grass_shrub_frequency = 0.005
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
      if (r,g,b) == (255,255,128):
        crops.append(Crops(x, y, 'tga/crops_transparent.tga', 0))
      elif (r,g,b) == (0,255,0): #small chance of shrubs on grass
        if random.random() <= grass_shrub_frequency:
          crops.append(Crops(x, y, random.choice(shrub_icons), 0))
      elif (r,g,b) == (0,0,0): #small chance of shrubs on grass - what's black?
        if random.random() <= grass_shrub_frequency:
          crops.append(Crops(x, y, random.choice(darkshrub_icons), 0))
  return crops
  
def pixel_array_to_starting_point(pixel_array):
  starting_points = []
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
      if (r,g,b) == (255,0,0):
        starting_points.append((x,y))
  if len(starting_points) > 1: #Shouldn't be happening ...
    return starting_points[0]
  elif len(starting_points) == 1:
    return starting_points[0]
  else:
    print "Couldn't find starting point"
    return (0,0)
        
def pixel_array_to_goal_squares(pixel_array):
  goal_squares = []
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
      if (r,g,b) == (255,255,0):
        goal_squares.append((x,y))
  return goal_squares
        
def pixel_array_to_zombies(game, pixel_array):
  zombies = []
  n = 1
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
      if (r,g,b) == (255,128,64):
        for unit in game.units:
          if unit.name == 'Zombie ' + str(n):
            print "Error creating '" + unit.name + "'"
            n += 1
        zombies.append(EnemyZombie(game, "Zombie " + str(n), (x,y)))
        n += 1
  return zombies
  
def pixel_array_to_generators(game, pixel_array, super_frequency):
  # radius should be an argument!
  generators = []
  rad = 20
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
      if (r,g,b) == (255,128,64):
        if random.randint(1,3) == 1:
          generators.append(RisingZombieGenerator(game, (x,y), super_frequency))
        else:
          generators.append(ZombieGenerator(game, (x,y), rad, super_frequency))
  return generators
  
def pixel_array_to_rising_generators(game, pixel_array):
  # radius should be an argument!
  generators = []
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
      if (r,g,b) == (255,128,64):
        generators.append(RisingZombieGenerator(game, (x,y)))
  return generators

def pixel_array_to_battle_generators(game, pixel_array, radius,
  max_zombies, max_superzombies, max_bandits, max_wizards, max_total):
  #having to use all those as arguments instead of getting them from the level (or game?) is not optimal
  generators = []
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
      if (r,g,b) == (255,128,64):
        generators.append(InfiniteZombieGenerator(game, (x,y), radius,
          max_zombies, max_superzombies, max_bandits, max_wizards, max_total))
  return generators
          
def pixel_array_to_bandit_generators(game, pixel_array):
  # important: uses the same color as zombie generators, using existing zombie placement
  generators = []
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
      if (r,g,b) == (255,128,64):
        generators.append(BanditGenerator(game, (x,y), 20))
  return generators
  
def pixel_array_to_soldier_generators(game, pixel_array):
  # important: uses the same color as zombie generators, using existing zombie placement
  generators = []
  for y in range(pixel_array.surface.get_height()):
    for x in range(pixel_array.surface.get_width()):
      (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
      if (r,g,b) == (255,128,64):
        generators.append(SoldierGenerator(game, (x,y), 20))
  return generators
