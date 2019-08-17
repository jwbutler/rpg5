from __future__ import division
import pygame
import random
import math

class Animation:
  """
  Information for a single object animation.  Contains activity name,
  direction, and links to four frames.  Directions are 'N', 'NE', etc.
  """
  def __init__(self, activity, directions, frames, filenames):
    self.activity = activity
    self.directions = directions
    self.frames = frames
    self.filenames = filenames
    self.findex = 0

  def next_frame(self):
    """ Iterates the frame index. """
    self.findex += 1
    if self.findex == len(self.frames):
      self.findex = 0

  def get_current_frame(self):
    """ Returns the current frame # of the current animation. """
    return self.frames[self.findex]

  def get_current_filename(self):
    """ Returns the current frame # of the current animation. """
    return self.filenames[self.findex]

class Corpse:
  # Should probably be inheriting from PlayerMale
  def __init__(self, game, unit):
    self.game = game
    for key in unit.__dict__.keys():
      self.__dict__[key] = unit.__dict__[key]
    self.get_current_frame = unit.get_current_frame
    self.refresh_activity = unit.refresh_activity
    self.refresh_activity(game, unit.current_activity)
    if self.hostile: #this is probably the wrong place to be doing this, but...
      game.score += 50
      game.kills += 1
      if game.battle_mode:
        game.streak += 1
        game.streak_ticks = 25
        game.award_streak_bonus()
  
  def do_events(self):
    pass
  
  """
  def draw_OLD(self):
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    x -= 8
    y -= 30 
    source = self.get_current_frame()
    self.game.screen.blit(source, (x, y))
    #game.draw_black(self, source, (x,y))
  """

  def draw(self):
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    x -= 8; y -= 30
    self.sort_equipment()
    for equip in self.equipment:
      f = equip.current_animation.get_current_filename()
      if f[len(f)-6:] == '_B.tga':
        equip.draw(x, y)
    source = self.get_current_frame()
    self.game.screen.blit(source, (x, y))
    for equip in self.equipment:
      f = equip.current_animation.get_current_filename()
      if f[len(f)-6:] != '_B.tga':
        equip.draw(x, y)
        
  def get_z(self):
    return 6*self.x + 6*self.y + 2
    
  def get_rect(self):
    (left,top) = self.game.grid_to_pixel((self.x, self.y))
    top -= 28
    (width, height) = (self.get_current_frame().get_width(), self.get_current_frame().get_height())
    return pygame.Rect((left,top,width, height))
    
  def sort_equipment(self):
    sorted_equipment = []
    if self.current_activity == 'standing' and self.current_animation.directions[0] in ["E", "SE", "S"]:
      for slot in ["shield", "weapon", "head", "hair", "chest", "cloak"]:
        for equip in self.equipment:
          if equip.slot == slot:
            sorted_equipment.append(equip)
            break
    elif self.current_activity == 'standing' and self.current_animation.directions[0] in ["NE"]:
      for slot in ["weapon", "shield", "head", "hair", "chest", "cloak"]:
        for equip in self.equipment:
          if equip.slot == slot:
            sorted_equipment.append(equip)
            break
    elif self.current_activity == 'walking' and self.current_animation.directions[0] in ["E"]:
      for slot in ["weapon", "shield", "head", "hair", "chest", "cloak"]:
        for equip in self.equipment:
          if equip.slot == slot:
            sorted_equipment.append(equip)
            break              
    else:
      for slot in ["shield", "weapon", "head", "hair", "cloak", "chest"]:
        for equip in self.equipment:
          if equip.slot == slot:
            sorted_equipment.append(equip)
            break
    sorted_equipment.reverse()
    self.equipment = sorted_equipment

class Wall:
  def __init__(self, game, x, y, icon, height_offset = 0):
    self.game = game
    self.x = x
    self.y = y
    self.icon = pygame.image.load(icon)
    self.icon.set_colorkey((255,255,255))
    self.icon.convert()
    self.current_activity = None
    self.height_offset = height_offset

  def draw(self):
    self.icon.set_alpha(255)
    for unit in self.game.units + self.game.corpses:
      #if unit.playable:
      dx = (unit.x - self.x); dy = (unit.y - self.y)
      screen_dy = 12*(dx+dy)
      screen_dx = 12*(dx-dy)
      min_screen_dy = (-84)+((-27)*self.height_offset)
      if screen_dy <= 0 and screen_dy >= min_screen_dy:
        if screen_dx > -24 and screen_dx < 24:
          self.icon.set_alpha(128)
          break
    for unit in self.game.units + self.game.corpses:
      if unit.playable:
        if self.game.distance((unit.x,unit.y),(self.x,self.y)) <= self.game.VISION_RADIUS:
          self.game.screen.blit(self.icon, self.get_rect())
          self.icon.set_alpha(255)
          return
    
  def get_z(self):
    return 6*self.x + 6*self.y + 6
    
  def unit_to_alpha(self, unit):
    collide_rect = self.get_rect().clip(unit.get_rect())
    collide_area = collide_rect.width * collide_rect.height
    x = max(255-(collide_area), 0)
    return x
  
  def coords_to_alpha(self, x, y):
    (self_x, self_y) = (self.x, self.y)
    dx = abs(self.x - x - 2*self.height_offset)
    dy = abs(self.y - y - 2*self.height_offset)
    alpha = int(48*(dx+dy)) + 16
    alpha = min(255, alpha)
    alpha = max(0, alpha)
    return alpha
    
  def get_rect(self):
    (left,top) = self.game.grid_to_pixel((self.x, self.y))
    top += -27*self.height_offset - 27
    (width, height) = (self.icon.get_width(), self.icon.get_height())
    return pygame.Rect((left,top,width,height))

class WallNoTrans(Wall):
  #This class is just used for inheritance of basic objects
  def draw(self):
    for unit in self.game.units + self.game.corpses:
      if unit.playable:
        if self.game.distance((unit.x,unit.y),(self.x,self.y)) <= self.game.VISION_RADIUS:
          self.game.screen.blit(self.icon, self.get_rect())
          return

class Tree(WallNoTrans):
  def get_rect(self):
    (left,top) = self.game.grid_to_pixel((self.x, self.y))
    top += -27*self.height_offset - 48
    (width, height) = (self.icon.get_width(), self.icon.get_height())
    return pygame.Rect((left,top,width,height))
    
class Counter(WallNoTrans):
  def get_rect(self):
    (left,top) = self.game.grid_to_pixel((self.x, self.y))
    top += -27*self.height_offset - 26
    (width, height) = (self.icon.get_width(), self.icon.get_height())
    return pygame.Rect((left,top,width,height))
    
class Boulder(WallNoTrans):
  def get_rect(self):
    (left,top) = self.game.grid_to_pixel((self.x, self.y))
    top += -27*self.height_offset - 14
    (width, height) = (self.icon.get_width(), self.icon.get_height())
    return pygame.Rect((left,top,width,height))
    
class Rocks(WallNoTrans):
  def __init__(self, game, x, y):
    self.game = game
    self.x = x
    self.y = y
    self.icons = {}
    self.count = 4
    for x in range(1, self.count+1):
      filename = "tga/rock_pile_24x12_" + str(x) + ".tga"
      icon = pygame.image.load(filename)
      icon.set_colorkey((255,255,255))
      icon.convert()
      self.icons[x] = icon
    self.icon = self.icons[self.count]
    self.current_activity = None
    self.height_offset = 0
    
  def get_rect(self):
    (left,top) = self.game.grid_to_pixel((self.x, self.y))
    top += -27*self.height_offset
    (width, height) = (self.icon.get_width(), self.icon.get_height())
    return pygame.Rect((left,top,width,height))
  
  def get_z(self):
    return 6*self.x + 6*self.y
    
  def remove_one(self):
    self.count -= 1
    if self.count == 0:
      self.game.rock_piles.remove(self)
    else:
      self.icon = self.icons[self.count]
    
class Crops(WallNoTrans):
  def get_rect(self):
    (left,top) = self.game.grid_to_pixel((self.x, self.y))
    top += -27*self.height_offset - 20
    (width, height) = (self.icon.get_width(), self.icon.get_height())
    return pygame.Rect((left,top,width,height))
    
  def get_z(self):
    return 6*self.x + 6*self.y + 7
    
class Parapet(WallNoTrans):
  def __init__(self, x, y, direction, NS_image, EW_image, height_offset = 0):
    self.x = x
    self.y = y
    self.direction = direction
    if self.direction == 'N':
      self.icon = pygame.image.load(NS_image)
    elif self.direction == 'E':
      self.icon = pygame.image.load(EW_image)
    elif self.direction == 'S':
      self.icon = pygame.image.load(NS_image)
    elif self.direction == 'W':
      self.icon = pygame.image.load(EW_image)
    self.icon.set_colorkey((255,255,255))
    self.current_activity = None
    self.height_offset = height_offset

  def get_z(self):
    #make sure we render over the wall
    if self.direction == 'N':
      z_offset = 5
    elif self.direction == 'E':
      z_offset = 5
    elif self.direction == 'S':
      z_offset = 5
    elif self.direction == 'W':
      z_offset = 5
    return 6*self.x + 6*self.y + 12*self.height_offset + z_offset
        
  def get_rect(self):
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    y += -27*self.height_offset
    if self.direction == 'N':
      x += 12
      y -= 18
    elif self.direction == 'E':
      x += 12
      y -= 12
    elif self.direction == 'S':
      y -= 12
    elif self.direction == 'W':
      y -= 18
    (width, height) = (self.icon.get_width(), self.icon.get_height())
    return pygame.Rect((x,y,width,height))
    
class Window(Wall):
  def get_rect(self):
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    y += -27*self.height_offset - 14
    if self.direction == 'N':
      x += 12
      y -= 20
    elif self.direction == 'E':
      x += 12
      y -= 14
    elif self.direction == 'S':
      y -= 14
    elif self.direction == 'W':
      y -= 20
    #game.screen.blit(img, (x,y))
        
class Roof(Wall):
  def __init__(self, rect, icon, height_offset=0):
    self.rect = rect
    self.icon = icon
    self.icon.set_colorkey((255,255,255))
    self.height_offset = height_offset
    (self.x, self.y) = self.rect.center
    
  def draw(self):
    (x1, y1) = self.game.grid_to_pixel((self.rect.left, self.rect.top))
    (x2, y2) = self.game.grid_to_pixel((self.rect.left, self.rect.bottom))
    xx = min(x1,x2); yy = min(y1,y2)
    xx += 12
    yy -= (self.height_offset*28)
    for y in range(self.rect.top-2, self.rect.bottom):
      for x in range(self.rect.left-2, self.rect.right):
        for unit in self.game.units:
          if (unit.x,unit.y) == (x,y):
            return
    self.icon.set_alpha(255)
    self.game.screen.blit(self.icon, (xx,yy))
        
  def get_rect(self):
    (x,y) = self.game.grid_to_pixel((self.rect.left, self.rect.top))
    if (self.rect.width, self.rect.height) == (3,3):
      x -= 24
      y += -27*self.height_offset - 28
    elif (self.rect.width, self.rect.height) == (5,5):
      x -= 48
      y += -27*self.height_offset - 28
    elif (self.rect.width, self.rect.height) == (10,5):
      x -= 48
      y += -27*self.height_offset - 28
    elif (self.rect.width, self.rect.height) == (5,10):
      x -= 108
      y += -27*self.height_offset - 28
    (width, height) = (self.icon.get_rect().width, self.icon.get_rect().height)
    return pygame.Rect((x,y,width, height))

  def get_z(self):
    return 6*(self.rect.right) + 6*(self.rect.bottom) + 12*self.height_offset

  def coords_to_alpha(self, x, y):
    (center_x,center_y) = (self.rect.left + self.rect.width/2, self.rect.top + self.rect.height/2)
    dx = abs(center_x - x)
    dy = abs(center_y - y)
    if (dx+dy) < 4:
      return 0
    else:
      alpha = int(32*(dx+dy))
      alpha = min(255, alpha)
      alpha = max(0, alpha)
      return alpha
      
  def unit_to_alpha(self, unit):
    if self.rect.collidepoint((unit.x,unit.y)):
      return 0
    else:
      return 255      
      
  def collide(self, x, y):
    return self.rect.collidepoint((x,y))
      
class Gate(Wall):

  def __init__(self, x_1, y_1, x_2, y_2, icon, height_offset = 0):
    (self.x_1, self.y_1, self.x_2, self.y_2) = (x_1, y_1, x_2, y_2)
    self.icon = pygame.image.load(icon)
    self.icon.set_colorkey((255,255,255))
    self.height_offset = height_offset
    
  def draw(self):
    img = self.icon
    img.set_alpha(255)
    for unit in self.game.units:
      #if (unit.x, unit.y) in self.blocked_squares():
      alpha = self.coords_to_alpha(self.game, unit.x, unit.y)
      if alpha < img.get_alpha():
        self.icon.set_alpha(alpha)
    (x,y) = self.game.grid_to_pixel((self.x_1, self.y_1))
    y -= 84
    x -= 3
    self.game.screen.blit(img, (x,y))

  def get_z(self):
    return 6*(self.x_2) + 6*(self.y_2) + 12*self.height_offset

  def coords_to_alpha(self, x, y):
    return 255
    
  def collide(self, x, y):
    if x in range(self.x_1, self.x_2+1) and y in range(self.y_1, self.y_2+1):
      return True
    return False
    
  def get_rect(self):
    (left,top) = self.game.grid_to_pixel((self.x_1, self.y_1))
    top += -27*self.height_offset - 28
    (width, height) = (self.icon.get_rect().width, self.icon.get_rect().height)
    return pygame.Rect((left,top,width, height))    

class Door:
  def __init__(self, x, y, dir):
    (self.x, self.y) = (x,y)
    self.dir = dir #S or E only
    self.icon = pygame.image.load('tga/door_' + dir + '_bigsquare_1.tga')
    self.icon.set_colorkey((255, 255, 255))
    self.open_icon = pygame.image.load('tga/door_' + dir + '_bigsquare_2.tga')
    self.open_icon.set_colorkey((255, 255, 255))
    self.show_open_icon = False
    self.current_activity = None

  def list_open_squares(self):
    return [(self.x, self.y)]

  def draw(self):
    """ draw a door, and auto-open it """
    if self.show_open_icon:
      source = self.open_icon
    else:
      source = self.icon
    if self.dir == 'E':
      self.game.screen.blit(source, self.game.grid_to_pixel(self.x, self.y))
    elif self.dir == 'S':
      self.game.screen.blit(source, self.game.grid_to_pixel(self.x, self.y))

  def get_z(self):
    z = 6*self.x + 6*self.y
    if self.dir == 'E':
      if self.show_open_icon:
        z += 12
      else:
        z += 6
    else: #dir == 'S'
      if self.show_open_icon:
        z += 3
      else:
        z += 0
    return z

class Floor:  
  def __init__(self, icons=[], rect=pygame.Rect((0,0,0,0))):
    self.rect = rect
    self.tile_surfaces = icons
    self.xy_tiles = {}
    #self.black_surface = pygame.image.load("tga/black_floor_24x12.tga")
    #self.black_surface.set_colorkey((255,255,255))
    for y in range(self.rect.height):
      for x in range(self.rect.width):
        self.set_tile((x,y), random.choice(self.tile_surfaces))

  """
  def append_rect(self, floor_type, rect):
    icons = []
    i = 1
    while os.path.exists(floor_type + '_' + str(i) + '.tga'):
      surface = pygame.image.load(floor_type + '_' + str(i) + '.tga')
      surface.set_colorkey((255,255,255))
      icons.append(surface)
      i += 1
    for y in range(rect.top, rect.top+rect.height):
      for x in range(rect.left, rect.left+rect.width):
        self.tiles[(x,y)] = random.choice(icons)
  """
        
  def set_tile(self, (x,y), tile_surface):
    for t in self.tile_surfaces:
      if tile_surface == t:
        self.xy_tiles[(x,y)] = self.tile_surfaces.index(t)
        return
    else:
      self.tile_surfaces.append(tile_surface)
      self.xy_tiles[(x,y)] = self.tile_surfaces.index(tile_surface)
  
  def get_tile(self, (x,y)):
    tile_index = self.xy_tiles[(x,y)]
    return self.tile_surfaces[tile_index]

  def draw(self):
    rect = self.game.camera.get_rect()
    screen_rect = pygame.rect.Rect((0,0,self.game.screen.get_width(), self.game.screen.get_height()))
    self.game.floor_layer.fill((0,0,0))
    tile_rect = pygame.rect.Rect((0,0,24,12))
    for (x,y) in self.xy_tiles.keys():
      if rect.collidepoint((x,y)):
        for unit in self.game.units:
          if unit.playable:
            if self.game.distance((unit.x,unit.y), (x,y)) <= self.game.VISION_RADIUS:
              (xx,yy) = self.game.grid_to_pixel((x, y))
              #tile_rect = pygame.rect.Rect((xx,yy,24,12))
              tile_rect.move(xx,yy)
              if screen_rect.colliderect(tile_rect):
                self.game.floor_layer.blit(self.get_tile((x,y)), (xx, yy))
                break

class BlankFloor(Floor):
  def __init__(self, game, rect):
    self.game = game
    self.rect = rect
    self.tile_surfaces = []
    self.xy_tiles = {}
    #self.tiles = {}

class BasicObject(Wall):
  # used for stuff like bar stools, mugs, etc
  # i.e. anything that fits in a wall frame and needs to render on a counter
  def __init__(self, x, y, icon):
    Wall.__init__(self, x, y, icon)

  def get_z(self):
    return 6*self.x + 6*self.y + 12*self.height_offset + 6
    
  def draw(self):
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    y += -27*self.height_offset - 27
    self.game.screen.blit(self.icon, (x,y))
  

class Menu:
  #i'm guessing we haven't used this one in a while
  def __init__(self, game, image, rect, player, visible = False):
    self.game = game
    self.image = image
    self.rect = rect
    self.surface = pygame.image.load(self.image)
    self.background = pygame.image.load(self.image)
    self.buttons = []
    self.icons = []
    self.visible = visible

  def show(self):
    self.visible = True

  def hide(self):
    self.visible = False

  def toggle(self):
    self.visible = not self.visible

  def refresh(self, player):
    self.surface.blit(self.background, (0,0))
    for icon in self.icons:
      self.surface.blit(icon.surface, (icon.x, icon.y))

class MainMenu(Menu):
  def __init__(self, game, image, rect, visible = False):
    self.game = game
    self.image = image
    self.rect = rect
    self.background = pygame.image.load(self.image)
    self.background.set_colorkey((255,0,0))
    self.surface = self.background.copy()
    self.surface.set_colorkey((255,0,0))      
    self.icons = []
    self.buttons = []
    self.cards = []    
    self.visible = visible

  def refresh(self):
    self.surface.blit(self.background, (0,0))
    self.cards = []
    for unit in self.game.units:
      if unit.playable:
        self.cards.append(UnitCard(self.game, unit))
    
    font = pygame.font.SysFont("Arial", 16, True)
    
    # Draw unit numbers
    for (n, card) in enumerate(self.cards):
      self.surface.blit(card.surface, (92*n + 4, 37))
      text = font.render(str(n+1), False, (0,0,0))
      x = 92*n + 38 + (21 - text.get_width())/2
      y = (22 - text.get_height())/2 + 14
      self.surface.blit(text, (x,y))
    
  def card_rect(self, card):
    return pygame.Rect(92*self.cards.index(card)+4, 410, 88, 80)

class UnitCard:
  def __init__(self, game, unit):
    self.game = game
    self.unit = unit
    self.surface = pygame.Surface((88,80))
    if unit.current_activity in ['dead', 'dead_decapitated']:
      self.surface.fill((255,128,128))
    elif unit.selected:
      self.surface.fill((128,255,128))
    else:
      self.surface.fill((128,128,128))
    hp_bar = unit.draw_hp_bar(80,16)
    self.surface.blit(hp_bar, (4, 4))
    if unit.has_special:
      cooldown_bar = unit.draw_cooldown_bar(80,8)
      self.surface.blit(cooldown_bar, (4, 22))
    font = pygame.font.SysFont('Arial', 12, True)
    color = (128,0,255)
    if len(unit.name.split()) > 1:
      (first_name, last_name) = unit.name.split()
      self.surface.blit(font.render(first_name, False, color), (4, 32))
      self.surface.blit(font.render(last_name, False, color), (4, 46))
      self.surface.blit(font.render("Level " + str(unit.level), False, (255,255,255)), (4, 62))
    else:
      self.surface.blit(font.render(unit.name, False, color), (4, 33))
      self.surface.blit(font.render("Level " + str(unit.level), False, (255,255,255)), (4,48))
      
  def update(self, unit):
    print 'UCU'
    #check whether this actually requires the game to be passed
    if unit.current_activity in ['dead', 'dead_decapitated']:
      self.surface.fill((255,128,128))
    elif unit.selected:
      self.surface.fill((128,255,128))
    else:
      self.surface.fill((128,128,128))
    hp_bar = unit.draw_hp_bar(80,16)
    self.surface.blit(hp_bar, (4, 4))
    if unit.has_special:
      cooldown_bar = unit.draw_cooldown_bar(80,8)
      self.surface.blit(cooldown_bar, (4, 22))
    font = pygame.font.SysFont('Arial', 12, True)
    color = (128,0,255)
    
    # If unit's name has first & last name, render them on separate lines
    if len(unit.name.split()) > 1:
      (first_name, last_name) = unit.name.split()
      self.surface.blit(font.render(first_name, False, color), (4, 32))
      self.surface.blit(font.render(last_name, False, color), (4, 46))
      self.surface.blit(font.render("Level " + str(unit.level), False, (255,255,255)), (4, 62))
    else:
      self.surface.blit(font.render(unit.name, False, color), (4, 33))
      self.surface.blit(font.render("Level " + str(unit.level), False, (255,255,255)), (4,48))
    
class EquipmentIcon:
  def __init__(self, item, (x, y)):
    if item and os.path.exists(item.icon):
      self.item = item
      self.image = self.item.icon
      self.surface = pygame.image.load(self.image)
    elif item:
      self.item = item
      self.surface = pygame.Surface((24, 24))
      self.surface.fill((255,255,255))
    else:
      self.item = None
      self.surface = pygame.Surface((24, 24))
      self.surface.fill((255,255,255))
      (self.x, self.y) = (x,y)

  def get_border_rect(self):
    return (self.x, self.y, 26, 26)
  
  def get_icon_rect(self):
    return pygame.rect.Rect(self.x+1, self.y+1, 24, 24)

class InventoryIcon:
  def __init__(self, item, (x, y)):
    (self.x, self.y) = (x, y)
    self.item = item
    if self.item and os.path.exists(self.item.icon_small):
      self.image = self.item.icon_small
      self.surface = pygame.image.load(self.image)
    else:
      self.image = None
      self.surface = None

  def get_border_rect(self):
    return (self.x, self.y, 18, 18)
  
  def get_icon_rect(self):
    return pygame.rect.Rect(self.x+1, self.y+1, 16, 16)

class Camera:
  def __init__(self, x = 0, y = 0):
    self.x = x
    self.y = y
  def get_rect(self):
    return pygame.rect.Rect((int(self.x - 20), int(self.y - 20), 40, 40))

class Level:
  def __init__(self, npcs, floor, walls):
    self.npcs = npcs
    self.floor = floor
    self.walls = walls
  
class Blood:
  def __init__(self, game, x, y, damage, (min_r,min_g,min_b)=(128,0,0), (max_r,max_g,max_b)=(224,32,24)):
    self.game = game
    (self.x, self.y) = (x,y)  
    self.frame_1 = pygame.Surface((40, 40))
    self.frame_2 = pygame.Surface((40, 40))
    self.frame_3 = pygame.Surface((40, 40))
    min_y = 10
    for frame in [self.frame_1, self.frame_2, self.frame_3]:
      frame.fill((255,255,255))
      for n in range(damage+1):
        color = (random.randint(min_r, max_r), random.randint(min_g, max_g), random.randint(min_b, max_b))
        y = random.randint(min_y, 40)
        dx = abs(10-2*(y%10))
        (min_x, max_x) = (dx,40 - dx)
        x = random.randint(min_x, max_x)
        pygame.draw.line(frame, color, (x,y), (x,y))
      frame.set_colorkey((255,255,255))
      min_y += 10
    self.findex = 0
    self.ticks = 0
    
  def merge(self, other_blood):
    # add other blood to self
    self.frame_3.blit(other_blood.frame_3, (0,0))
    self.ticks = max(self.ticks, other_blood.ticks)
    self.frame_3.set_alpha(255)
        
  def draw(self):
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    x -= 8; y -= 30
    if self.findex == 0:
      source = self.frame_1
      self.findex += 1
    elif self.findex == 1:
      source = self.frame_2
      self.findex += 1
    elif self.findex == 2:
      source = self.frame_3
    self.game.screen.blit(source, (x, y))
    
  def get_z(self):
    return 6*self.x + 6*self.y

class Dart:
  def __init__(self, game, damage, source_unit, target_unit):
    self.game = game
    self.source_unit = source_unit
    self.target_unit = target_unit
    self.icon = {}
    for direction in self.game.directions:
      self.icon[direction] = pygame.image.load("tga/dart_" + direction + ".tga")
      self.icon[direction].set_colorkey((255,255,255))
    self.current_icon = random.choice(self.icon.values())
    self.speed = 2
    self.damage = damage
    (self.x_i, self.y_i) = (self.source_unit.x, self.source_unit.y)
    (self.x, self.y) = (self.x_i, self.y_i)
    self.refresh()
    self.do_events() #this way it'll move once first
  
  def refresh(self):
    #find current position of target unit and aim accordingly
    target_unit = self.target_unit
    if target_unit:
      (self.x_f, self.y_f) = (target_unit.x, target_unit.y)    
      (self.dx, self.dy) = (self.x_f - self.x, self.y_f - self.y)
      m = max(abs(self.dx), abs(self.dy))
      (dx, dy) = (int(round(self.dx/m)), int(round(self.dy/m)))
      self.direction = self.game.coords_to_dir((dx, dy))
      if self.direction == '':
        del(self)
        print (dx,dy,self.direction)
        return False
      self.current_icon = self.icon[self.direction]
      theta = math.atan2(self.dy, self.dx)
      (self.dx, self.dy) = (math.cos(theta)*self.speed, math.sin(theta)*self.speed)
    else:
      pass#print 'darts r hrd'

  def do_events(self):
    if not self.target_unit:
      try:
        self.game.darts.remove(self)
      except:
        pass#print "(Dart error)"
      return
    self.refresh()
    self.x += self.dx
    self.y += self.dy
    if self.game.distance((self.x, self.y), (self.target_unit.x, self.target_unit.y)) <= self.speed:
      self.do_hit(self.target_unit)
      
  def do_hit(self, target_unit):
    target_unit.take_damage(self.damage)
    self.game.blood.append(Blood(self.game, target_unit.x, target_unit.y, self.damage))
    if target_unit.current_hp <= 0 and target_unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
      target_unit.refresh_activity('falling')
      target_unit.reset_ticks()
      target_unit.scream()
    else:
      self.source_unit.play_hit_sound()
      #if self.target_unit == target_unit.name:
      #  self.target_unit = None
    try:
      self.game.darts.remove(self)
    except:
      pass#print "(Dart error)"
  
  def draw(self):
    source_unit = self.source_unit
    target_unit = self.target_unit
    if (not target_unit) or (not source_unit):
      try:
        self.game.darts.remove(self)
      except:
        pass#print "(Dart error)"
      return
    self.refresh()
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    y -= 20
    remaining_distance = self.game.distance((self.x, self.y), (target_unit.x, target_unit.y))
    total_distance = self.game.distance((source_unit.x, source_unit.y), (target_unit.x, target_unit.y))
    distance_ratio = remaining_distance/total_distance
    max_height = 10
    #height_offset = max_height * (1 - 4*((distance_ratio-0.5)**2))
    height_offset = max_height * (1 - 1*((distance_ratio-0.5)**2))
    y -= height_offset
    self.game.screen.blit(self.current_icon, (x,y))
    
  def get_z(self):
    return 6*self.x + 6*self.y
    
  def get_rect(self):
    # might need work
    self.refresh()
    (left,top) = self.game.grid_to_pixel((self.x, self.y))
    top += -28
    (width, height) = (self.current_icon.get_width(), self.current_icon.get_height())
    return pygame.Rect((left,top,width, height))
    
class Arrow(Dart):
  def __init__(self, game, damage, source_unit, target_unit):
    self.game = game
    self.damage = damage
    self.source_unit = source_unit
    self.target_unit = target_unit
    self.icon = {}
    for direction in self.game.directions:
      self.icon[direction] = pygame.image.load("tga/arrow_" + direction + ".tga")
      self.icon[direction].set_colorkey((255,255,255))
    self.current_icon = random.choice(self.icon.values())
    self.speed = 2
    (self.x_i, self.y_i) = (self.source_unit.x, self.source_unit.y)
    (self.x, self.y) = (self.x_i, self.y_i)

class StunArrow(Arrow):
  def __init__(self, game, damage, source_unit, target_unit):
    Arrow.__init__(self, game, damage, source_unit, target_unit)

  def do_hit(self, target_unit):
    target_unit.take_damage(self.damage)
    target_unit.refresh_activity("stunned") #Define our own activity later?
    self.game.blood.append(Blood(self.game, target_unit.x, target_unit.y, self.damage))
    if target_unit.current_hp <= 0 and target_unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
      target_unit.die()
    else:
      self.source_unit.play_hit_sound()
    try:
      self.game.darts.remove(self)
    except:
      pass#print "(Dart error)"

class ThrowingRock(Dart):
  def __init__(self, game, damage, source_unit, target_unit):
    self.game = game
    self.source_unit = source_unit
    self.target_unit = target_unit
    self.icon = {}
    for direction in self.game.directions:
      self.icon[direction] = pygame.image.load("tga/rock_flying_" + str(random.randint(1,3)) + ".tga")
      self.icon[direction].set_colorkey((255,255,255))
    self.current_icon = random.choice(self.icon.values())
    self.speed = 1
    self.damage = damage
    (self.x_i, self.y_i) = (self.source_unit.x, self.source_unit.y)
    (self.x, self.y) = (self.x_i, self.y_i)
    
class WaterTile:
  """ Similar to the Animation class, except indexes begin at 0... """
   
  def __init__(self, frames, (x,y)):
    self.frames = frames
    self.speed = 1/3
    self.findex = random.randint(0,3)
    (self.x, self.y) = (x,y)
    
  def draw(self):
    self.game.screen.blit(self.get_current_frame(), self.game.grid_to_pixel((self.x, self.y)))
    #self.game.draw_black(self, self.get_current_frame(), grid_to_pixel(self.game, self.x, self.y))
    
  def next_frame(self):
    """ Iterates the frame index. """
    self.findex += self.speed
    if int(self.findex) >= len(self.frames):
        self.findex = 0

  def get_current_frame(self):
    """ Returns the current frame of the current animation. """
    return self.frames[int(self.findex)]

class FireTile(WaterTile):

  def __init__(self, frames, (x,y), damage):
    self.frames = frames
    self.speed = 1/2
    self.findex = random.randint(0,3)
    (self.x, self.y) = (x,y)
    self.damage = damage
    
  def draw(self):
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    y -= 18
    self.game.screen.blit(self.get_current_frame(), (x,y))
    #self.game.draw_black(self, self.get_current_frame(), (x,y))

class RaisedFireTile(FireTile):
  def draw(self):
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    y -= 18; y -= 14 # (height of a counter)
    self.game.screen.blit(self.get_current_frame(), (x,y))
    self.next_frame()

  def get_z(self):
    return 6*self.x + 6*self.y + 6 #probably totally wrong
  
  def get_rect(self):
    return pygame.Rect((0,0,0,0)) #durr
    
class Fireball(Dart):
  def refresh(self):
    #find current position of target unit and aim accordingly
    target_unit = self.target_unit
    if target_unit:
      (self.x_f, self.y_f) = (target_unit.x, target_unit.y)    
      (self.dx, self.dy) = (self.x_f - self.x, self.y_f - self.y)
      (dx, dy) = (self.dx, self.dy)
      if dx != 0:
        dx /= abs(dx) 
      if dy != 0:
        dy /= abs(dy)
      if (dx,dy) != (0,0):
        (self.dx, self.dy) = (dx,dy)
        return True
    return False
      
  def __init__(self, game, source_unit, target_unit):
    self.game = game
    self.source_unit = source_unit
    self.target_unit = target_unit
    self.frames = []
    self.impact = False
    self.burning = False
    filenames = ["tga/fireball2_flying_SE_"+str(x)+".tga" for x in [1,2,3,4]]
    for filename in filenames:
      frame = pygame.image.load(filename)
      frame.set_colorkey((255,255,255))
      self.frames.append(frame)
    self.impact_frames = []
    
    filenames = ["tga/fireball2_impact_SE_"+str(x)+".tga" for x in [1,2,3]]
    for filename in filenames:
      frame = pygame.image.load(filename)
      frame.set_colorkey((255,255,255))
      self.impact_frames.append(frame)
    self.burning_frames = []
    
    filenames = ["tga/fire_on_person_"+str(x)+".tga" for x in [1,2,3,4]]
    for filename in filenames:
      frame = pygame.image.load(filename)
      frame.set_colorkey((255,255,255))
      self.burning_frames.append(frame)
    
    self.findex = random.randint(0,3)
    self.impact_findex = 0
    self.burning_findex = 0
    self.speed = 2
    (self.x_i, self.y_i) = (self.source_unit.x, self.source_unit.y)
    (self.x, self.y) = (self.x_i, self.y_i)
  
  def do_events(self):
    if not self.target_unit:
      self.game.darts.remove(self)
      return True  
    self.refresh()
    source_unit = self.source_unit
    target_unit = self.target_unit
    if (not source_unit) or (not target_unit):
      self.game.darts.remove(self)
      return False
    if self.impact:
      (self.x, self.y) = (target_unit.x, target_unit.y)
    elif self.burning:
      (self.x, self.y) = (target_unit.x, target_unit.y)
      target_unit.current_hp = max(0, target_unit.current_hp - 5)
      if target_unit.current_hp <= 0 and target_unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
        target_unit.refresh_activity('falling')
        target_unit.reset_ticks()
        target_unit.scream()
        self.game.darts.remove(self)
    else:
      self.x += self.dx
      self.y += self.dy
      if self.game.distance((self.x, self.y), (target_unit.x, target_unit.y)) <= 1:
        (self.x, self.y) = (target_unit.x, target_unit.y)
        dmg = source_unit.damage()
        target_unit.take_damage(dmg)
        self.game.blood.append(Blood(self.game, target_unit.x, target_unit.y, dmg))
        if target_unit.current_hp <= 0 and target_unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
          target_unit.refresh_activity('falling')
          target_unit.reset_ticks()
          target_unit.scream()
          self.game.darts.remove(self)          
        else:
          pass
        self.impact = True
  
  def draw(self):
    source_unit = self.source_unit
    target_unit = self.target_unit
    if not target_unit:
      self.game.darts.remove(self)
      return True
    self.refresh()
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    x -= 8; y -= 30
    remaining_distance = self.game.distance((self.x, self.y), (target_unit.x, target_unit.y))
    total_distance = self.game.distance((source_unit.x, source_unit.y), (target_unit.x, target_unit.y))
    distance_ratio = remaining_distance/total_distance
    max_height = 10
    height_offset = max_height * (1 - 4*((distance_ratio-0.5)**2))
    y -= height_offset
    if self.impact:
      y += 10
      self.game.screen.blit(self.impact_frames[self.impact_findex], (x,y))
      self.impact_findex += 1
      if self.impact_findex == 3:
        self.burning = True
        self.impact = False
    elif self.burning:
      self.game.screen.blit(self.burning_frames[self.burning_findex], (x,y))
      self.burning_findex += 1
      if self.burning_findex == 4:
        self.game.darts.remove(self)        
    else:
      y += 10
      self.game.screen.blit(self.frames[self.findex], (x,y))
      self.findex += 1
      if self.findex > 3:
        self.findex = 0
    
  def get_z(self):
    return 6*self.x + 6*self.y + 2
    
  def get_rect(self, game):
    # might need work
    self.refresh()
    (left,top) = self.game.grid_to_pixel((self.x, self.y))
    top += -28
    (width, height) = (self.frames[self.findex].get_width(), self.frames[self.findex].get_height())
    return pygame.Rect((left,top,width, height))
    
class LaserBeam(Dart):
  def __init__(self, game, source_unit, (x,y), (dx,dy)):
    self.game = game
    self.source_unit = source_unit
    (self.x,self.y) = (x,y)
    (self.dx,self.dy) = (dx,dy)
    if (self.dx,self.dy) in [(1,0), (-1,0)]:
      self.icon = pygame.image.load("tga/laser_beam_E_1.tga")
    elif (self.dx,self.dy) in [(0,1), (0,-1)]:
      self.icon = pygame.image.load("tga/laser_beam_S_1.tga")
    else:
      print 'icon error:',(self.dx,self.dy)
    self.icon.set_colorkey((255,255,255))
    self.speed = 1
    self.ticks = 0
  
  def do_events(self):
    if self.ticks >= 16:
      self.game.darts.remove(self)
      return True
    elif obstacle((self.x+self.dx,self.y+self.dy)):
      if not obstacle_unit((self.x+self.dx,self.y+self.dy)):
        self.game.darts.remove(self)
        return True
    self.x += self.dx
    self.y += self.dy
    for unit in self.game.units:
      if (unit.x,unit.y) == (self.x,self.y):
        source_unit = self.source_unit
        if source_unit:
          if unit != source_unit:
            unit.take_damage(20)
            self.game.blood.append(Blood(self.game, unit.x, unit.y, 20))
            if unit.current_hp <= 0 and unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
              unit.refresh_activity(self.game, 'falling')
              unit.reset_ticks()
              unit.scream()
            else:
              source_unit.play_hit_sound()
              #if self.target_unit == target_unit.name:
              #  self.target_unit = None
        else:
          del(self)
          return False
    self.ticks += 1
    
  def get_rect(self):
    # might need work
    (left,top) = self.game.grid_to_pixel((self.x, self.y))
    left -= 8; top -= 30
    (width, height) = (self.icon.get_width(), self.icon.get_height())
    return pygame.Rect((left,top,width, height))
    
  def draw(self):
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    x -= 8; y -= 30
    self.game.screen.blit(self.icon, (x,y))

class HealingFlash:
  def __init__(self, game, unit_name):
    self.game = game
    #Change this to a unit reference plx
    self.unit_name = unit_name
    unit = self.unit_name
    (self.x,self.y) = (unit.x,unit.y)    
    self.frames = []
    for filename in ["tga/healing_flash_"+str(x)+".tga" for x in [1,2,3,4]]:
    #for filename in ["tga/healing_spiral_"+str(x)+".tga" for x in [1,2,3,4,5]]:
    #for filename in ["tga/healing_dot_"+str(x)+".tga" for x in [1,2,3]]:    
      frame = pygame.image.load(filename)
      frame.set_colorkey((255,255,255))
      self.frames.append(frame)
    self.findex = 0
    
  def draw(self):
    unit = self.unit_name
    (self.x,self.y) = (unit.x,unit.y)
    (x,y) = self.game.grid_to_pixel((unit.x, unit.y))
    x -= 8; y -= 30    
    self.game.screen.blit(self.frames[self.findex], (x,y))
    if not self.game.paused:
      self.findex += 1
      if self.findex >= len(self.frames):
        self.game.healing_flashes.remove(self)
        
  def get_rect(self):
    # might need work
    (left,top) = self.game.grid_to_pixel((self.x, self.y))
    left -= 8; top -= 30
    (width, height) = (self.frames[self.findex].get_width(), self.frames[self.findex].get_height())
    return pygame.Rect((left,top,width, height))
        
  def get_z(self):
    return 6*self.x + 6*self.y + 3
    
class Pointer:
  """ To assist with clicking on (enemy) units.  Gets created whenever a unit moves, and
      remains for a set number of frames (6?). """
  def __init__(self, (x,y), unit):
    (self.x,self.y) = (x,y)
    self.unit = unit
    self.ticks = 8
    
  def return_unit(self):
    return self.unit
    
class HealthPowerup(Wall):
  def __init__(self, game, (x,y), heal_amount):
    self.game = game
    self.icon = pygame.image.load("tga/bottle_1.tga")
    self.icon.set_colorkey((255,255,255))
    palette_swaps = {(0,0,128):  (192,0,64),
                     (0,0,255):  (255,64,128),
                     (0,0,0):    (96,0,32),
                     (128,64,0): (255,64,128)}
    for (src_color, dest_color) in palette_swaps.iteritems():
      self.icon = self.game.palette_swap(self.icon, src_color, dest_color)
    (self.x,self.y) = (x,y)
    self.heal_amount = heal_amount
    self.height_offset = 0
    
  def proc(self, unit):
    unit.current_hp = min(unit.current_hp + self.heal_amount, unit.max_hp)
    self.play_proc_sound()
    self.game.powerups.remove(self)
    self.game.redraw_unit_cards = True

  def play_proc_sound(self):
    filename = "sounds/powerup.ogg"
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(True)
    channel.play(sound)  
  
  def get_z(self):
    return 6*self.x + 6*self.y + 3 #just make sure it's more than a corpse
    
  def get_rect(self):
    #No guarantees on this one!
    (left,top) = self.game.grid_to_pixel((self.x, self.y))
    top += -27*self.height_offset - 27
    (width, height) = (self.icon.get_width(), self.icon.get_height())
    return pygame.Rect((left,top,width,height))
    
  def draw(self):
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    y += -27*self.height_offset - 8
    x += 10
    self.game.screen.blit(self.icon, (x,y))

class DepthTree():
  # It's good to use a tree because we can insert in log(n) time.
  def __init__(self, game):
    self.root = None
    self.game = game
  # Traverse the tree in order, draw everything in it.
  # We should generalize this with an iterator-type method
  # Learn that later
  
  def insert(self, node, root=None):
    if not root:
      root = self.root

    if root:
      if root.data == node.data:
        return
      else:
        if node.data.get_z() <= root.data.get_z():
          if root.left:
            self.insert(node, root.left)
          else:
            root.left = node
            node.parent = root
        else:
          if root.right:
            self.insert(node, root.right)
          else:
            root.right = node
            node.parent = root
    else:
      self.root = node
      
  def remove(self, obj, root=False):
    #0. Find node N storing obj
    #1. Find next in-order node M.
    #2. Copy M to N.
    #3. Remove M.
    #4. Reinsert all of M's kids.
    if root == False:
      root = self.root
    elif root == None:
      return False
    
    if root.data == obj:
      # found it. ummm...
      if root.right != None:
        next = root.right
      elif root.parent != None and root.parent.left == root:
        next = root.parent
      if (root.left):
        self.insert(root.left)
      if (root.right):
        self.insert(root.right)
	  
      
    elif (obj.get_z() <= root.data.get_z()):
      self.remove(obj, root.left)
    else:
      self.remove(obj, root.right)
    
  
  """
  for obj in arr:
    if obj.get_rect().colliderect(screen_rect):
      for unit in self.units:
        if unit.playable:
          # Find one friendly unit in range of it
          # Here's where we'd check LOS, but too inefficient
          if self.distance((obj.x,obj.y),(unit.x,unit.y)) <= self.VISION_RADIUS:
            obj.draw()
            break
  """
  def draw_all(self, root=False):
    if root==False:
      root = self.root
    if root:  
      screen_rect = pygame.Rect((0,0,400,300)) #see if this is stored in RPG
      current = root
      if current.left:
        self.draw_all(current.left);
      obj = current.data
      if obj.get_rect().colliderect(screen_rect):
        for unit in self.game.units:
          if unit.playable:
            if self.game.distance((obj.x,obj.y),(unit.x,unit.y)) <= self.game.VISION_RADIUS:
              obj.draw()
              break
      if current.right:
        self.draw_all(current.right);
        
  def count(self, root=False):
    # using false as a sentinel value instead of none because, well, ugh
    if root==False:
      root=self.root
    if root==None:
      return 0
    else:
      rtn = 1
      rtn += self.count(root.left)
      rtn += self.count(root.right)
      return rtn
  
class DepthTreeNode:
  def __init__(self, data=None):
    self.data = data
    self.left = None
    self.right = None
    self.parent = None