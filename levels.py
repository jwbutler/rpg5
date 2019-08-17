from __future__ import division
from classes import *
from enemy_humans import *
from units import *
from wizards import *
from zombies import *
from npcs import *
from generators import BanditGeneratorNetwork
import math
import sys
      
class LevelFromFile:
  def __init__(self, game, filename):
    self.game = game
    self.filename = filename
    
  def load_level_data(self):
    t1 = pygame.time.get_ticks()
    self.units = []
    self.player_units = []
    map_surface = pygame.image.load(self.filename)
    pixel_array = pygame.PixelArray(map_surface)

    if self.filename in ['tga/levels/level0a.tga', 'tga/levels/level0b.tga']:
      default_tile_type = 'stone'
    else:
      default_tile_type = 'grass'
    self.floor = BlankFloor(self.game, map_surface.get_rect())#pixel_array_to_floor(pixel_array, tile_color_dict, tile_surfaces_dict, default_tile_type)
    (self.start_x, self.start_y) = self.game.pixel_array_to_starting_point(pixel_array)
    self.goal_squares = self.game.pixel_array_to_goal_squares(pixel_array)
    self.camera = Camera(self.start_x,self.start_y)
    self.walls = []
    self.invisible_walls = []
    self.crops = []
    self.trees = []
    self.counters = []
    self.objects = [] #Unused?
    self.roofs = []
    self.rock_piles = []
    self.water_tiles = []
    self.fire_tiles = []
    self.powerups = []
    water_filenames = ["tga/water_" + str(x) + ".tga" for x in [1,2,3,4]]
    water_frames = [pygame.image.load(f) for f in water_filenames]
    fire_filenames = ["tga/floor_fire_" + str(x) + ".tga" for x in [1,2,3,4]]
    fire_frames = [pygame.image.load(f) for f in fire_filenames]
    fire_filenames_small = ["tga/floor_fire_small_" + str(x) + ".tga" for x in [1,2,3,4]]
    fire_frames_small = [pygame.image.load(f) for f in fire_filenames_small]
    for f in water_frames + fire_frames + fire_frames_small:
      f.set_colorkey((255,255,255))
    t2 = pygame.time.get_ticks()
    indexed_rgb = {} #Stores the results of unmap_rgb for the surface
    for tile_list in self.game.tile_surfaces_dict.values():
      for tile in tile_list:
        tile.convert()
    for y in range(pixel_array.surface.get_height()):
      for x in range(pixel_array.surface.get_width()):
        indexed = pixel_array[x][y]
        try:
          (r,g,b) = indexed_rgb[indexed]
        except KeyError:
          (r,g,b,a) = pixel_array.surface.unmap_rgb(indexed)
          indexed_rgb[indexed] = (r,g,b)
        self.floor.set_tile((x,y), self.game.rgb_to_tile((r,g,b), self.game.tile_color_dict, self.game.tile_surfaces_dict, default_tile_type))
        #self.floor.tiles[(x,y)] = self.game.rgb_to_tile((r,g,b), self.game.tile_color_dict, self.game.tile_surfaces_dict, default_tile_type)
        self.walls += self.game.rgb_to_walls((r,g,b), (x,y))
        self.walls += self.game.rgb_to_boulders((r,g,b), (x,y))
        self.counters += self.game.rgb_to_counters((r,g,b), (x,y))
        self.trees += self.game.rgb_to_trees((r,g,b), (x,y))
        self.rock_piles += self.game.rgb_to_rocks((r,g,b), (x,y))
        self.crops += self.game.rgb_to_crops((r,g,b), (x,y))
        if random.random() < 0.3: #An attempt to improve FPS - only a fraction of animating tiles, well, animate
          self.water_tiles += self.game.rgb_to_water_tiles((r,g,b), (x,y), water_frames)
          self.fire_tiles += self.game.rgb_to_fire_tiles((r,g,b), (x,y), fire_frames, fire_frames_small)
        self.invisible_walls += self.game.rgb_to_invisible_walls((r,g,b), (x,y))
    t3 = pygame.time.get_ticks()
    """
    self.walls = pixel_array_to_walls(pixel_array) + pixel_array_to_boulders(pixel_array)
    self.invisible_walls = []#pixel_array_to_invisible_walls(pixel_array)
    self.crops = pixel_array_to_crops(pixel_array)
    self.trees = pixel_array_to_trees(pixel_array)
    self.counters = pixel_array_to_counters(pixel_array)
    self.objects = pixel_array_to_rocks(pixel_array)
    self.water_tiles = pixel_array_to_water_tiles(pixel_array)
    self.fire_tiles = pixel_array_to_fire_tiles(pixel_array)
    """

    self.game.walls = []
    self.game.parapets = []
    self.game.blood = []

    #Find a better place to do this
    if self.filename != 'tga/levels/townlol2.tga':
      self.game.corpses = []
    self.game.generators = []
    
    for unit in self.game.units:
      if unit.playable:
        self.units.append(unit)
        self.player_units.append(unit)
        if self.filename != 'tga/levels/townlol2.tga':
          (unit.x, unit.y) = (self.start_x, self.start_y)
      elif not unit.hostile:
        if self.filename == 'tga/levels/townlol2.tga':
          self.units.append(unit)
          #(unit.x, unit.y) = (self.start_x, self.start_y)
    self.load_map_features()

    t4 = pygame.time.get_ticks()
    #ghettoness
    
    if not hasattr(self, 'level_name'):
      print self.filename.split("/")[-1] + ": ",
    elif not self.level_name:
      print self.filename.split("/")[-1] + ": ",
    else:
      print self.level_name + ": ",
    print t4-t1, '(', t2-t1, t3-t2, t4-t3, ')'

  """ Mostly used to add units to levels. """
  def load_map_features(self):
    map_surface = pygame.image.load(self.filename)
    pixel_array = pygame.PixelArray(map_surface)
    if self.filename == 'tga/levels/level0a.tga':
      first_name = language.generate_word(language.consonants, language.vowels)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name1 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name2 = first_name + " " + last_name
      first_name = language.generate_word(language.consonants, language.vowels)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name3 = first_name+" "+last_name
      self.units = [
                    PlayerMale(self.game, name1, (self.start_x, self.start_y)),
                    AltPlayerMale(self.game, name2, (self.start_x, self.start_y)),
                    PlayerArcher(self.game, name3, (self.start_x, self.start_y)),                    
                    RezOnlyWizard(self.game, "Gviz", (3,3))
                   ]
    elif self.filename == 'tga/levels/lakemap.tga':
      first_name = language.generate_word(language.consonants, language.vowels)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name1 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name2 = first_name + " " + last_name
      first_name = language.generate_word(language.consonants, language.vowels)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name3 = first_name+" "+last_name
      self.units = [
                    PlayerMale(self.game, name1, (self.start_x, self.start_y)),
                    AltPlayerMale(self.game, name2, (self.start_x, self.start_y)),
                    PlayerArcher(self.game, name3, (self.start_x, self.start_y)),
                   ]
    elif self.filename == 'tga/levels/0.tga':
      first_name = language.generate_word(language.consonants, language.vowels)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name = first_name+" "+last_name
      self.units = [PlayerMale(self.game, name, (self.start_x, self.start_y))]
    elif self.filename == 'tga/levels/wizardtest.tga':
      first_name = language.generate_word(language.consonants, language.vowels)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name1 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name2 = first_name + " " + last_name
      first_name = language.generate_word(language.consonants, language.vowels)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name3 = first_name+" "+last_name
      self.units = [
                    PlayerMale(self.game, name1, (self.start_x, self.start_y)),
                    AltPlayerMale(self.game, name2, (self.start_x, self.start_y)),
                    PlayerArcher(self.game, name3, (self.start_x, self.start_y)),
                    RedWizard(self.game, "Gviz", (10,10))
                   ]  
    elif self.filename == 'tga/levels/townlol.tga':
      peasant_posns = []
      for y in range(pixel_array.surface.get_height()):
        for x in range(pixel_array.surface.get_width()):
          (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
          if (r,g,b) == (128,0,255):
            peasant_posns.append((x,y))
      
      for (n, (x,y)) in enumerate(peasant_posns):
        first_name = language.generate_word(language.consonants, language.vowels)
        last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
        name = first_name+" "+last_name
        if n % 3 == 0:
          self.units.append(JickerPeasant(self.game, name, (x,y)))
        elif n % 3 == 1:
          self.units.append(RockThrowingPeasantChick(self.game, name, (x,y), None))
        else:
          self.units.append(RockThrowingPeasant(self.game, name, (x,y), None))
      for (x1,y1,x2,y2) in [(4,3,8,7), (20,3,29,7), (6,26,10,30), (27,22,31,26)]:
        if (x2-x1+1, y2-y1+1) == (3,3):
          icon = "tga/roof_3x3_gray_tiled.tga"
        elif (x2-x1+1, y2-y1+1) == (5,5):
          icon = "tga/roof_5x5_gray_tiled.tga"
        elif (x2-x1+1, y2-y1+1) == (5,10):
          icon = "tga/roof_5x10_gray_tiledB.tga"
        elif (x2-x1+1, y2-y1+1) == (10,5):
          icon = "tga/roof_5x10_gray_tiled.tga"
        else:
          print "fuck"
        icon = pygame.image.load(icon)
        icon = icon.convert()
        icon.set_colorkey((255,255,255))
        self.roofs.append(Roof(pygame.rect.Rect(x1,y1,x2-x1+1,y2-y1+1), icon, 1))
    elif self.filename == 'tga/levels/townlol2.tga':
      self.corpses = self.game.corpses
      self.roofs = self.game.roofs
      self.units.append(RezOnlyWizard(self.game, "Wizard 1", (2,10)))
      self.units.append(RezOnlyWizard(self.game, "Wizard 2", (1,20)))
      self.units.append(RezOnlyWizard(self.game, "Wizard 3", (23,31)))
      self.units.append(RezOnlyWizard(self.game, "Wizard 4", (35,20)))
      rects = [(5,4,3,3), (21,4,8,3), (7,27,3,3), (28,23,3,3)]
      for (left,top,width,height) in rects:
        rect = pygame.Rect((left, top, width, height))
        for y in range(rect.top, rect.bottom):
          for x in range(rect.left, rect.right):
            self.invisible_walls.append((x,y))
    elif self.filename == 'tga/levels/1.tga':
      first_name = language.generate_word(language.consonants, language.vowels)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name1 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name2 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name3 = first_name+" "+last_name
      self.units = [
                    PlayerMale(self.game, name1, (self.start_x, self.start_y)),
                    AltPlayerMale(self.game, name2, (self.start_x, self.start_y)),
                    PlayerArcher(self.game, name3, (self.start_x, self.start_y))
                   ]
    elif self.filename == 'tga/levels/2.tga':
      for x in [1,2,3]:
        if x == 3:
          self.units.append(RockThrowingPeasantChick(self.game, "Civilian "+str(x), (38+x,46), [(44,33), (43,21), (33,15), (20,16), (5,15), (0,14)]))
        else:
          self.units.append(RockThrowingPeasant(self.game, "Civilian "+str(x), (38+x,46), [(44,33), (43,21), (33,15), (20,16), (5,15), (0,14)]))
    elif self.filename in ['tga/levels/3.tga']:
      pass
    if self.filename in ['tga/levels/1.tga', 'tga/levels/2.tga', 'tga/levels/20.tga', 'tga/levels/level0h.tga']: #Bandits
      self.generators = self.game.pixel_array_to_bandit_generators(pixel_array, 0.3)
    elif self.filename in ['tga/levels/townlol.tga']:
      self.generators = [BanditGeneratorNetwork(self.game, pixel_array, 0.3, 6)]
    elif self.filename in ['tga/levels/townlol2.tga']:
      self.generators = []
    elif self.filename in []:
      self.generators = self.game.pixel_array_to_soldier_generators(pixel_array)
    elif self.filename in []:
      self.generators = self.game.pixel_array_to_generators(pixel_array, 0.0)
    elif self.filename in ['tga/levels/lakemap.tga', 'tga/levels/Road_1.tga', 'tga/levels/Road_2.tga', 'tga/levels/Road_3.tga']:
      self.generators = self.game.pixel_array_to_generators(pixel_array, 0.1)
    elif self.filename in []:
      #includes wizard levels; wizard is independent of this
      self.generators = self.game.pixel_array_to_generators(pixel_array, 0.2)
    elif self.filename in []:
      self.generators = self.game.pixel_array_to_generators(pixel_array, 0.4)
    elif self.filename in []:
      self.generators = self.game.pixel_array_to_generators(pixel_array, 0.5)
    if self.filename in ["tga/levels/1.tga", "tga/levels/2.tga"]:
      self.music_filenames = ["sounds/TTK.ogg", "sounds/sputnikmarch.ogg", "sounds/no solution.ogg"]
    else:
      self.music_filenames = ["sounds/11.ogg",
                              "sounds/80s.ogg",
                              "sounds/C Bb Eb E Ab A Bb.ogg",
                              "sounds/CEB.ogg",
                              "sounds/crystal cave.ogg",
                              "sounds/funky ethnic.ogg",
                              "sounds/funkpop.ogg",
                              "sounds/horror.ogg",
                              "sounds/jack4.ogg",
                              "sounds/Jack5.ogg",
                              "sounds/synthscale.ogg",
                              "sounds/synthy.ogg"
                             ]
      
  def check_victory(self):
    hostile_units = []
    for unit in self.game.units:
      if unit.hostile:
        hostile_units.append(unit.name)  
        
    if self.filename in ["tga/levels/3.tga", "Road_1.tga", "Road_2.tga", "Road_3.tga"]:
      #Unwinnable lol
      return False
    elif self.filename in ["tga/levels/0.tga"]:
      #lololol
      return True
    elif self.filename in ["tga/levels/townlol.tga"]:
      # Elimination
      if len(hostile_units) > 0:
        return False
      elif len(self.generators) > 0:
        return False
      else:
        return True
    elif self.filename in ["tga/levels/townlol2.tga"]:
      # Elimination
      if len(hostile_units) > 0:
        return False
      else:
        return True

    elif self.filename in ["tga/levels/2.tga"]:
      # Escort
      npcs = [u for u in self.game.units if (not u.playable and not u.hostile)]
      if len(npcs) == 0:
        if self.game.cleared_npcs > 0:
          return True
      return False
    elif self.filename in ["tga/levels/wizardtest.tga"]:
      # Elimination
      if len(hostile_units) > 0:
        return False
      else:
        return True
    else:
      # Travel
      for unit in self.game.units:
        if unit.playable:
          if (unit.x, unit.y) in self.goal_squares:
            return True
      return False
  
  def check_defeat(self):
    #Escort
    if self.filename in ["tga/levels/2.tga"]:
      npcs = [u for u in self.game.units if (not u.playable and not u.hostile)]
      if len(npcs) == 0:
        if self.game.cleared_npcs == 0:
          return True
    """
    elif self.filename in ["tga/levels/0.tga"]:
      npcs = [u for u in self.game.units if (not u.playable and not u.hostile)]
      if len(npcs) == 0:
        if self.game.cleared_npcs == 0:
          return False
    """
    # Single unit death = lose
    friendly_units = []
    for unit in self.game.units:
      if unit.playable:
        friendly_units.append(unit)
    if len(friendly_units) == 3:
      return False
    else:
      return True

class BattleLevelFromFile(LevelFromFile):
  def __init__(self, game, filename, max_zombies, max_superzombies, max_bandits, max_wizards, max_total, name=None):
    LevelFromFile.__init__(self, game, filename)
    self.max_zombies = max_zombies
    self.max_superzombies = max_superzombies
    self.max_bandits = max_bandits
    self.max_wizards = max_wizards
    self.max_total = max_total
    if name:
      self.level_name = name
    else:
      self.level_name = filename

    
  def load_level_data(self):
    LevelFromFile.load_level_data(self)
    
    pixel_array = pygame.PixelArray(pygame.image.load(self.filename))
    # this is redundant, you should probably just set self.pixel_array in
    # the parent method instead
    self.generators = pixel_array_to_battle_generators(self, pixel_array, 10,
      self.max_zombies, self.max_superzombies, self.max_bandits, self.max_wizards, self.max_total)
    # I think these generators overwrite the ones set in the parent method
    
    
  def check_victory(self):
    if self.game.time_remaining == 0:
      return True
    else:  
      return False
      
  def check_defeat(self):
    if LevelFromFile.check_defeat(self):
      return True
    else:
      return False


      
