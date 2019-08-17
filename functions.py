import pygame
import random
import math

# THIS MODULE HAS BEEN PHASED OUT
# FUNCTIONS ARE NOW INCORPORATED INTO RPG.PY

print "*** FUNCTIONS.PY ***"

def coords_to_dir((x,y)):
    dir = ''
    if (y == -1):
        dir = 'N'
    elif (y == 1):
        dir = 'S'
    if (x == -1):
        dir += 'W'
    elif (x == 1):
        dir += 'E'
    return dir

def draw_target(game, obj):
  """ Draws the target symbol over the target. """
  source = pygame.image.load('tga/target.tga')
  source.set_colorkey((255,255,255))
  game.screen.blit(source, adjusted_posn(game, obj.x, obj.y, 152, 20))

def z_sort(obj_1, obj_2):
  z_1 = obj_1.get_z()
  z_2 = obj_2.get_z()
  if z_1 > z_2: return 1
  elif z_1 == z_2: return 0
  elif z_1 < z_2: return -1

def distance(obj_1, obj_2):
    x_1 = obj_1[0]
    y_1 = obj_1[1]
    x_2 = obj_2[0]
    y_2 = obj_2[1]
    dx = x_2 - x_1
    dy = y_2 - y_1
    return (dx*dx + dy*dy)**0.5

def distance_sort(a, b, target):
    """
    Sort a list of npcs/objects by distance from the target.
    """
    target_posn = (target.x, target.y)
    a_posn = (a.x, a.y)
    b_posn = (b.x, b.y)
    if distance(target_posn, a_posn) > distance(target_posn, b_posn): return 1
    if distance(target_posn, a_posn) == distance(target_posn, b_posn): return 0
    if distance(target_posn, a_posn) < distance(target_posn, b_posn): return -1
    
def distance_sort_posn(a, b, target):
    """
    Sort a list of npcs/objects by distance from the target.
    """
    if distance(target, a) > distance(target, b): return 1
    if distance(target, a) == distance(target, b): return 0
    if distance(target, a) < distance(target, b): return -1
        
def obstacle(game, (x, y)):
    """
    True if there is an object or npc at the given (x,y).
    True if the given (x,y) is out of bounds.
    False if it is "safe".
    """
    for obj in game.units + game.walls + game.trees + game.counters + game.water_tiles:
      #collide with any object/npc? (not doors, not corpses)
      if (x,y) == (obj.x, obj.y):
        return True
    for obj in game.invisible_walls:
      if (x,y) == obj:
        return True
    for obj in game.gates:
      if obj.collide(x,y):
        return True
      # collide with boundary?
    if not game.floor.rect.collidepoint((x, y)):
      return True
    return False

def obstacle_unit(game, (x,y)):
  """ Is there an NPC at (x,y)? """
  for unit in game.units:
    if (unit.x, unit.y) == (x, y):
      return unit
  return None
  
def acquire_target(game, shift = None):
    game.npcs.sort(lambda a,b: distance_sort(a, b, game.player))
    if game.target == None:
        if game.npcs:
            return game.npcs[0]
    else:
        index = game.npcs.index(game.target)
        if shift:
            return game.npcs[(index-1) % len(game.npcs)]
        else:
            return game.npcs[(index+1) % len(game.npcs)]

def adjacent_squares((x, y)):
    squares = [(x-1, y-1), (x, y-1), (x+1, y-1), (x-1, y), (x+1, y), (x-1, y+1), (x, y+1), (x+1, y+1)]
    return squares

def knight_move((x, y)):
    return [(x-1, y-2), (x+1, y-2), (x-2, y-1), (x+2, y-1), (x-2, y+1), (x+2, y+1), (x-1, y+2), (x+1, y+2)]

def get_next_square(source, target):
  squares = adjacent_squares((source[0], source[0]))
  squares.sort(lambda a,b: distance_sort(a,b,target))
  for square in squares:
    if not obstacle(square):
      return square

def point_at(source, target):
  squares = adjacent_squares((source.x, source.y))
  squares.sort(lambda a,b: distance_sort(a,b,target))
  for square in squares:
    if square == (target.x, target.y):
      source.dx = square[0] - source.x
      source.dy = square[1] - source.y
      return True
    elif not obstacle(square):
      source.dx = square[0] - source.x
      source.dy = square[1] - source.y
      return True

def check_los(game, (x1,y1), (x2,y2)):
  (x,y) = (x1,y1)
  h = ( (x2-x1)**2 + (y2-y1)**2 ) ** 0.5
  if h == 0:
    return True
  dx = (x2-x1)/h
  dy = (y2-y1)/h
  while abs(x2-x) > 0.5 or abs(y2-y) > 0.5:
    (rx, ry) = (round(x), round(y))
    if (rx, ry) not in [(x1,y1), (x2,y2)]:
      if obstacle(game, (rx, ry)):
        if not obstacle_unit(game, (rx, ry)):
          return False
    x += dx
    y += dy
  return True
    
def key_to_dir(key):
    keyName = pygame.key.name(key)
    if keyName == '[1]': return 'S'
    elif keyName == '[2]': return 'SE'
    elif keyName == '[3]': return 'E'
    elif keyName == '[4]': return 'SW'
    elif keyName == '[6]': return 'NE'
    elif keyName == '[7]': return 'W'
    elif keyName == '[8]': return 'NW'
    elif keyName == '[9]': return 'N'

def dir_to_key(dir):
    if dir == 'N': return K_KP9
    elif dir == 'NE': return K_KP6
    elif dir == 'E': return K_KP3
    elif dir == 'SE': return K_KP2
    elif dir == 'S': return K_KP1
    elif dir == 'SW': return K_KP4
    elif dir == 'W': return K_KP7
    elif dir == 'NW': return K_KP8

def get_angle(a, b):
    if a == b: return 0
    elif a == 'N':
        if b in ['NW', 'NE']: return 45
        elif b in ['W', 'E']: return 90
        elif b in ['SW', 'SE']: return 135
        else: return 180
    elif a == 'NE':
        if b in ['N', 'E']: return 45
        elif b in ['NW', 'SE']: return 90
        elif b in ['W', 'S']: return 135
        else: return 180
    elif a == 'E':
        if b in ['NE', 'SE']: return 45
        elif b in ['N', 'S']: return 90
        elif b in ['NW', 'SW']: return 135
        else: return 180
    elif a == 'SE':
        if b in ['E', 'S']: return 45
        elif b in ['NE', 'SW']: return 90
        elif b in ['W', 'N']: return 135
        else: return 180
    elif a == 'S':
        if b in ['SW', 'SE']: return 45
        elif b in ['W', 'E']: return 90
        elif b in ['NW', 'NE']: return 135
        else: return 180
    elif a == 'SW':
        if b in ['W', 'S']: return 45
        elif b in ['NW', 'SE']: return 90
        elif b in ['N', 'E']: return 135
        else: return 180
    elif a == 'W':
        if b in ['NW', 'SW']: return 45
        elif b in ['N', 'S']: return 90
        elif b in ['NE', 'SE']: return 135
        else: return 180
    elif a == 'NW':
        if b in ['W', 'N']: return 45
        elif b in ['SW', 'NE']: return 90
        elif b in ['S', 'E']: return 135
        else: return 180

def in_line(obj_1, obj_2):
    if obj_1.x == obj_2.x:
        return True
    elif obj_1.y == obj_2.y:
        return True
    elif obj_1.x + obj_1.y == obj_2.x + obj_2.y:
        return True
    elif obj_1.x - obj_1.y == obj_2.x - obj_2.y:
        return True
    return False

def draw_text(txt, surface, (x, y), size=12):
    """ Render string txt at the specified x and y coordinates. """
    font = pygame.font.SysFont('Arial', size)    
    source = font.render(txt, False, (255,255,255))
    surface.blit(source, (x,y))
    
def grid_to_pixel(game, x, y):
    # returns top left point of the floor tile?
    a = (x - game.camera.x)*12 - (y - game.camera.y)*12 + 152
    b = (x - game.camera.x)*6 + (y - game.camera.y)*6 + 80
    return(a,b)
    
def pixel_to_grid_defunct(game, a, b):
    x = (a + 2*b - 312)/24 + game.camera.x
    y = (a - 2*b + 8)/(-24) + game.camera.y
    return (x,y)

def pixel_to_grid_improved(game, x, y):
  camera_rect = game.camera.get_rect()
  for ty in range(camera_rect.top, camera_rect.bottom):
    for tx in range(camera_rect.left, camera_rect.right):
      try:
        tile = game.floor.tiles[(tx,ty)]
        (left, top) = grid_to_pixel(game, tx, ty)
        tile_rect = pygame.Rect(left, top, 24, 12)
        pixel_array = pygame.PixelArray(tile)
        if tile_rect.collidepoint((x,y)):
          #(r,g,b,a) = tile.get_at((x - left, y - top))
          (r,g,b,a) = tile.unmap_rgb(pixel_array[x - left][y - top])
          if (r,g,b,a) != (255,255,255,255):
            t2 = pygame.time.get_ticks()
            #print 'PTGI:', t2-t1
            return (tx,ty)
      except KeyError as e:
         pass
      except e:
        print e
        return None
  return None

def adjacent_directions(dir):
  if dir == 'N': return ['NW', 'NE']
  if dir == 'NE': return ['N', 'E']
  if dir == 'E': return ['NE', 'SE']
  if dir == 'SE': return ['E', 'S']
  if dir == 'S': return ['SE', 'SW']
  if dir == 'SW': return ['S', 'W']
  if dir == 'W': return ['SW', 'NW']
  if dir == 'NW': return ['W', 'N']

def palette_swap_multi(surface, palette_swaps):
  t1 = pygame.time.get_ticks()
  temp_colors_1 = {}
  temp_colors_2 = {}
  for (src_color, dest_color) in palette_swaps.iteritems():
    (r,g,b) = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    used_colors = palette_swaps.keys()+palette_swaps.values()
    while (r,g,b) in used_colors:
      (r,g,b) = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    temp_colors_1[src_color] = (r,g,b)
    temp_colors_2[(r,g,b)] = dest_color
      
  pixel_array = pygame.PixelArray(surface)
  for src_color in palette_swaps.keys():
    pixel_array.replace(src_color, temp_colors_1[src_color])
  for src_color in temp_colors_2.keys():
    pixel_array.replace(src_color, temp_colors_2[src_color])
  surf2 = pixel_array.surface.convert()
  surf2.set_colorkey(surface.get_colorkey())
  t2 = pygame.time.get_ticks()
  return surf2
  
def palette_swap(surface, source_color, dest_color):
    """ surface --> surface """
    pixel_array = pygame.PixelArray(surface)
    pixel_array.replace(source_color, dest_color)
    #surf2 = pixel_array.make_surface()
    surf2 = pixel_array.surface
    surf2.set_colorkey(surface.get_colorkey())
    return surf2

"""
def palette_swap_black(surface):
    colorkey = surface.get_colorkey()
    pixel_array = pygame.PixelArray(surface)
    pixel_array_2 = pixel_array.extract(colorkey)
    surface2 = pixel_array_2.make_surface()
    surface2.set_colorkey((255,255,255))
    return surface2
"""

def sort_equipment(a, b):
    #overhaul this, it does not work
    if a.__class__ == 'Armor':
        z_1 = 0
    elif a.__class__ == 'Helm':
        z_1 = 1
    elif a.__class__ == 'Shield':
        z_1 = 2
    elif a.__class__ == 'Sword':
        z_1 = 3
    else:
        z_1 = 0

    if b.__class__ == 'Armor':
        z_2 = 0
    elif b.__class__ == 'Helm':
        z_2 = 1
    elif b.__class__ == 'Shield':
        z_2 = 2
    elif b.__class__ == 'Sword':
        z_2 = 3
    else:
        z_2 = 0

    if z_1 > z_2:
        return 1
    elif z_1 == z_2:
        return 0
    elif z_1 < z_2:
        return -1

def draw(game, obj, dx = -8, dy = -10):
    """ draw a whole bunch of things, player or npcs mostly, with awkward conditionals for things """
    source = obj.get_current_frame()
    screen.blit(source, adjusted_posn(game, obj.x, obj.y,152+dx, dy))

def dir_to_coords(direction):
    if direction[0] == 'N':
        y = -1
    elif direction[0] == 'S':
        y = 1
    else:
        y = 0
    if direction[len(direction)-1] == 'W':
        x = -1
    elif direction[len(direction)-1] == 'E':
        x = 1
    else:
        x = 0
    return (x, y)
    
def distance_to_alpha(distance):
  alpha = 255 - (distance-16)*64
  alpha = min(alpha, 255)
  alpha = max(alpha, 0)
  return alpha
  
def get_tiles_in_line((x1,y1), (x2,y2)):
  (x,y) = (x1,y1)
  r = 1
  tiles = []
  while distance((x,y),(x2,y2)) > r:
    for xx in [x-r/4, x, x+r/4]:
      for yy in [y-r/4, y, y+r/4]:
        if (int(xx), int(yy)) not in tiles:
          tiles.append((int(xx),int(yy)))
    theta = math.atan2((y2-y),(x2-x))
    x += (r*math.cos(theta))
    y += (r*math.sin(theta))
  return tiles
  
def line_of_sight(game, (x1,y1), (x2,y2), radius=10):
  if distance((x1,y1),(x2,y2)) <= radius:
    line_of_tiles = get_tiles_in_line((x1,y1),(x2,y2))
    for tile in line_of_tiles:
      if tile == (x1,y1):
        continue
      elif obstacle_unit(game, tile):
        pass
      elif obstacle(game, tile):
        return False
    return True
  else:
    return False
    
# document this, variable names really suck
def generate_tile(color,var1=0.2,var2=0.2,uniform=False):
  for color_component in color:
    if color_component not in range(256):
      print "Invalid arguments to generate_tile().  Arguments must be \"r g b\", with each value between 0 and 255."
      sys.exit(0)
  (r,g,b) = color
  c = random.random() * (2*var1) + (1-var1)
  r = int(r * c)
  if not uniform:  
    c = random.random() * (2*var1) + (1-var1)
  g = int(g * c)
  if not uniform:
    c = random.random() * (2*var1) + (1-var1)
  b = int(b * c)
  tile = pygame.image.load("tga/tilemask.tga")
  pixelarray = pygame.PixelArray(tile)
  for y in range(12):
    for x in range(24):
      (tr,tg,tb, alpha) = tile.unmap_rgb(pixelarray[x][y])
      if (tr,tg,tb) == (255,255,255):
        c = random.random() * (2*var2) + (1-var2)
        rr = int(r * c)
        if not uniform:
          c = random.random() * (2*var2) + (1-var2)
        gg = int(g * c)
        if not uniform:
          c = random.random() * (2*var2) + (1-var2)
        bb = int(b * c)      
        pixelarray[x][y] = (rr,gg,bb)
  pixelarray.replace((0,0,0), (255,255,255))
  tile = pixelarray.surface
  tile.set_colorkey((255,255,255))
  return tile
  
def get_slash_directions(game, dir):
  # Given a compass direction, return all compass directions in a circle
  # starting on the initial dir.
  anim_directions = []
  i = game.directions.index(dir)
  for d in game.directions:
    j = game.directions.index(d)
    if j >= i:
      anim_directions.append(d)
  for d in game.directions:
    j = game.directions.index(d)                
    if j < i:
      anim_directions.append(d)
  return anim_directions

def rotate_45_degrees_clockwise(direction):
# ex: 'N' => 'NE'
  directions_dict = {"N":"NE", "NE":"E", "E":"SE", "SE":"S", "S":"SW", "SW":"W", "W":"NW", "NW":"N"}
  return directions_dict[direction]
  
def rotate_45_degrees_counterclockwise(direction):
# ex: 'N' => 'NE'
  directions_dict = {"N":"NW", "NW":"W", "W":"SW", "SW":"S", "S":"SE", "SE":"E", "E":"NE", "NE":"N"}
  return directions_dict[direction]
  
def rcw(dir):
  return rotate_45_degrees_clockwise(dir)
  
def rccw(dir):
  return rotate_45_degrees_counterclockwise(dir)
