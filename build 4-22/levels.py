from __future__ import division
from functions import *
from classes import *
from functions2 import *
from enemy_humans import *
from units import *
from wizards import *
from zombies import *
import math
import sys
      
class LevelFromFile:
  def __init__(self, game, filename):
    self.filename = filename
    
  def load_level_data(self, game):
    t1 = pygame.time.get_ticks()
    self.units = []
    #ghetto but cute metaprogramming
    for key in game.__dict__.keys():
      if key in ['check_victory', 'check_defeat', 'filename', 'level_name', 'start_x', 'start_y', 'units',
                 'max_points', 'max_zombies', 'max_superzombies', 'max_wizards', 'max_bandits', 'max_total']:
        pass
      else:
        self.__dict__[key] = game.__dict__[key]
    map_surface = pygame.image.load(self.filename)
    pixel_array = pygame.PixelArray(map_surface)

    if self.filename in ['tga/levels/level0a.tga', 'tga/levels/level0b.tga']:
      default_tile_type = 'stone'
    else:
      default_tile_type = 'grass'
    self.floor = BlankFloor(map_surface.get_rect())#pixel_array_to_floor(pixel_array, tile_color_dict, tile_surfaces_dict, default_tile_type)
    (self.start_x, self.start_y) = pixel_array_to_starting_point(pixel_array)
    self.goal_squares = pixel_array_to_goal_squares(pixel_array)
    self.camera = Camera(self.start_x,self.start_y)
    self.walls = []
    self.invisible_walls = []
    self.crops = []
    self.trees = []
    self.counters = []
    self.objects = [] #Unused?
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
    for tile_list in tile_surfaces_dict.values():
      for tile in tile_list:
        tile.convert()
    for y in range(pixel_array.surface.get_height()):
      for x in range(pixel_array.surface.get_width()):
        indexed = pixel_array[x][y]
        if indexed in indexed_rgb.keys():
          (r,g,b) = indexed_rgb[indexed]
        else:
          (r,g,b,a) = pixel_array.surface.unmap_rgb(indexed)
          indexed_rgb[indexed] = (r,g,b)
        self.floor.tiles[(x,y)] = rgb_to_tile((r,g,b), tile_color_dict, tile_surfaces_dict, default_tile_type)

        self.walls += rgb_to_walls((r,g,b), (x,y))
        self.walls += rgb_to_boulders((r,g,b), (x,y))
        self.counters += rgb_to_counters((r,g,b), (x,y))
        self.trees += rgb_to_trees((r,g,b), (x,y))
        self.rock_piles += rgb_to_rocks((r,g,b), (x,y))
        self.crops += rgb_to_crops((r,g,b), (x,y))     
        self.water_tiles += rgb_to_water_tiles((r,g,b), (x,y), water_frames)
        self.fire_tiles += rgb_to_fire_tiles((r,g,b), (x,y), fire_frames, fire_frames_small)
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
    self.parapets = []
    self.blood = []
    self.corpses = []
    self.generators = []
    for unit in game.units:
      if unit.playable:
        self.units.append(unit)
        (unit.x, unit.y) = (self.start_x, self.start_y)
        continue        
      elif not unit.hostile:
        if unit.ally:
          (unit.x, unit.y) = (self.start_x, self.start_y)
          self.units.append(unit)
          continue
    self.load_map_features(game)
    if self.filename in ['tga/levels/level0c.tga', 'tga/levels/19.tga', 'tga/levels/20.tga', 'tga/levels/level0h.tga']: #Bandits
      self.generators = pixel_array_to_bandit_generators(self, pixel_array)
    if self.filename in ['tga/levels/level0b.tga']:
      self.generators = pixel_array_to_soldier_generators(self, pixel_array)
    elif self.filename in ['tga/levels/level0.tga', 'tga/levels/1.tga', 'tga/levels/2.tga', 'tga/levels/3.tga',
                           'tga/levels/level0g.tga']:
      self.generators = pixel_array_to_generators(self, pixel_array, 0.0)
    elif self.filename in ['tga/levels/4.tga', 'tga/levels/5.tga', 'tga/levels/6.tga']:
      self.generators = pixel_array_to_generators(self, pixel_array, 0.1)
    elif self.filename in ['tga/levels/level0a.tga', 'tga/levels/7.tga', 'tga/levels/8.tga', 
                          'tga/levels/9.tga', 'tga/levels/13.tga', 'tga/levels/14.tga']:
      #includes wizard levels; wizard is independent of this
      self.generators = pixel_array_to_generators(self, pixel_array, 0.2)
    elif self.filename in ['tga/levels/11.tga', 'tga/levels/12.tga', 'tga/levels/15.tga', 'tga/levels/18.tga']:
      self.generators = pixel_array_to_generators(self, pixel_array, 0.4)
    elif self.filename in ['tga/levels/16.tga', 'tga/levels/17.tga']:
      self.generators = pixel_array_to_generators(self, pixel_array, 0.5)
    if self.filename in ["tga/levels/18.tga", "tga/levels/19.tga", "tga/levels/battlemap_1.tga",
                         "tga/levels/battlemap_2.tga", "tga/levels/battlemap_3.tga", "tga/levels/battlemap_4.tga"]:
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
    t4 = pygame.time.get_ticks()
    #ghettoness
    
    if not hasattr(self, 'level_name'):
      print self.filename.split("/")[-1] + ": ",
    elif not self.level_name:
      print self.filename.split("/")[-1] + ": ",
    else:
      print self.level_name + ": ",
    print t4-t1, '(', t2-t1, t3-t2, t4-t3, ')'
    
  def load_map_features(self, game):
    if self.filename == 'tga/levels/level0.tga':
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name1 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name2 = first_name+" "+last_name  
      first_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.female_name_suffixes)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name3 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name4 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name5 = first_name+" "+last_name
      self.units = [
                    PlayerMale(self, name1, (self.start_x,self.start_y)),
                    AltPlayerMale(self, name2, (self.start_x,self.start_y)),
                    PlayerFemale(self, name3, (self.start_x, self.start_y)),
                    PlayerArcher(self, name4, (self.start_x,self.start_y)),
                    PlayerHealer(self, name5, (self.start_x, self.start_y)),
                    RezOnlyWizard(self, "Gviz", (3,3))
                   ]
    elif self.filename == 'tga/levels/level0a.tga':
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name1 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name2 = first_name + " " + last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name3 = first_name+" "+last_name
      self.units = [
                    PlayerMale(self, name1, (self.start_x, self.start_y)),
                    AltPlayerMale(self, name2, (self.start_x, self.start_y)),
                    PlayerArcher(self, name3, (self.start_x, self.start_y)),                    
                    RezOnlyWizard(self, "Gviz", (3,3))
                    
                   ]
    elif self.filename == 'tga/levels/level0b.tga':
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name1 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name2 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name3 = first_name+" "+last_name
      self.units = [
                    PlayerMale(self, name1, (self.start_x, self.start_y)),
                    AltPlayerMale(self, name2, (self.start_x, self.start_y)),
                    PlayerArcher(self, name3, (self.start_x, self.start_y))
                   ]
    elif self.filename == 'tga/levels/level0c.tga':
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name1 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name2 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name3 = first_name+" "+last_name
      self.units = [
                    PlayerMale(self, name1, (self.start_x, self.start_y)),
                    AltPlayerMale(self, name2, (self.start_x, self.start_y)),
                    PlayerArcher(self, name3, (self.start_x, self.start_y))
                   ]
      for x in [1,2,3]:
        self.units.append(RockThrowingPeasant(self, "Civilian "+str(x), (39,47), [(44,33), (43,21), (33,15), (20,16), (5,15), (0,14)]))
    elif self.filename == 'tga/levels/level0d.tga':
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name1 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name2 = first_name+" "+last_name  
      first_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.female_name_suffixes)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name3 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name4 = first_name+" "+last_name
      self.units = [
                    PlayerMale(self, name1, (self.start_x,self.start_y)),
                    PlayerOfficer(self, name2, (self.start_x,self.start_y)),
                    SoldierNPC(self, "Jicker 1", (self.start_x,self.start_y)),
                    SoldierNPC(self, "Jicker 2", (self.start_x,self.start_y)),
                    SoldierNPC(self, "Jicker 3", (self.start_x,self.start_y)),
                    SoldierNPC(self, "Jicker 4", (self.start_x,self.start_y)),
                    PlayerFemale(self, name3, (self.start_x, self.start_y)),
                    PlayerHealer(self, name4, (self.start_x, self.start_y)),
                    HornedWizard(self, "Gviz", (3,3))
      ]
    elif self.filename == 'tga/levels/level0e.tga':
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name = first_name + " " + last_name      
      self.units = [InvisibleMan(self, name, (self.start_x,self.start_y)),
                    #Wraith(self, "Zombie 1", (10,10)),
                    #Ghost(self, "Zombie 2", (10,10)),
                    #LavaZombie(self, "Zombie 3", (10,10))
                    ]
    elif self.filename == 'tga/levels/level0f.tga':
      self.units = [Horse(self, "Cav Sword", "cavalry_swordsman", (self.start_x,self.start_y)),
                    Horse(self, "Cav Spear", "cavalry_lancer", (self.start_x,self.start_y)),
                    Horse(self, "Cav Archer", "cavalry_archer", (self.start_x,self.start_y)),]
    elif self.filename == 'tga/levels/level0g.tga':
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name1 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name2 = first_name+" "+last_name
      first_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.female_name_suffixes)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name3 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name4 = first_name+" "+last_name      
      self.units = [
        PlayerMale(self, name1, (self.start_x,self.start_y)),
        AltPlayerMale(self, name2, (self.start_x, self.start_y)),
        PlayerFemale(self, name3, (self.start_x, self.start_y)),
        PlayerHealer(self, name4, (self.start_x, self.start_y)),
        EnemyWizard(self, "Wizard 1", (5,5)),
        EnemyWizard(self, "Wizard 2", (35,35)),      
      ]
      for i in range(1,6):
        x = random.randint(0,40)
        y = random.randint(0,40)
        self.units.append(SoldierNPC(self, "NPC "+str(i), (x,y)))
      for i in range(6,11):
        x = random.randint(0,40)
        y = random.randint(0,40)
        self.units.append(BasicFriendlyNPC(self, "NPC "+str(i), (x,y)))
    elif self.filename == 'tga/levels/level0h.tga':
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name1 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name2 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name3 = first_name+" "+last_name            
      first_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.female_name_suffixes)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name4 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name5 = first_name+" "+last_name            
      self.units = [
                    PlayerMale(self, name1, (self.start_x,self.start_y)),
                    AltPlayerMale(self, name2, (self.start_x,self.start_y)),
                    AltPlayerMale(self, name3, (self.start_x,self.start_y)),                                        
                    PlayerFemale(self, name4, (self.start_x,self.start_y)),
                    PlayerHealer(self, name5, (self.start_x,self.start_y)),
                   ]
    elif self.filename == 'tga/levels/level0i.tga':
      self.units = [
                    HajjiFiruz(self, "Hajji Firuz", (self.start_x,self.start_y)),
                   ]
      # # # # # # # # # # #
      # STORY MODE BEGIN  #
      # # # # # # # # # # #
    elif self.filename == 'tga/levels/1.tga':
      self.parapets.extend(parapet_box(41, 18, 45, 18, "N"))
      self.parapets.extend(parapet_box(41, 21, 45, 21, "S"))
      self.parapets.extend(parapet_box(136, 84, 142, 84, "N"))
      self.parapets.extend(parapet_box(136, 86, 142, 86, "S"))

      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name1 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name2 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name3 = first_name+" "+last_name
      self.units = [
                    PlayerMale(self, name1, (self.start_x, self.start_y)),
                    AltPlayerMale(self, name2, (self.start_x, self.start_y)),
                    PlayerArcher(self, name3, (self.start_x, self.start_y))
                   ]
    elif self.filename == 'tga/levels/2.tga':
      self.parapets.extend(parapet_box(4, 5, 8, 5, "N"))
      self.parapets.extend(parapet_box(4, 8, 8, 8, "S"))
      self.parapets.extend(parapet_box(99, 71, 105, 71, "N"))
      self.parapets.extend(parapet_box(99, 73, 105, 73, "S"))
    elif self.filename == 'tga/levels/3.tga':
      self.parapets.extend(parapet_box(6, 23, 12, 23, "N"))
      self.parapets.extend(parapet_box(6, 25, 12, 25, "S"))
    elif self.filename == 'tga/levels/4.tga':
      self.parapets.extend(parapet_box(71, 59, 71, 63, "W"))
      self.parapets.extend(parapet_box(73, 59, 73, 63, "E"))
      for unit in self.units:
        if isinstance(unit, JickerNPC):
          unit.ally = False
    elif self.filename == 'tga/levels/5.tga':
      self.parapets.extend(parapet_box(6, 5, 6, 9, "W"))
      self.parapets.extend(parapet_box(8, 5, 8, 9, "E"))
    elif self.filename == 'tga/levels/6.tga':
      first_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.female_name_suffixes)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name = first_name+" "+last_name    
      self.units.append(PlayerFemaleNPC(self, name, (self.start_x, self.start_y)))
    elif self.filename == 'tga/levels/8.tga':
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name = first_name+" "+last_name    
      self.units.append(PlayerHealerNPC(self, name, (self.start_x, self.start_y)))
    elif self.filename == 'tga/levels/10.tga':
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name1 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name2 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name3 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name4 = first_name+" "+last_name
      first_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.female_name_suffixes)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name5 = first_name+" "+last_name      
      self.units.extend([
        ShopkeeperNPC(self, name3, (9,29)),
        PlayerFemaleMeleeNPC(self, name5, (29,6))
      ])
      mayor = MayorNPC(self, name4, (18,8))
      self.units.append(mayor)
      self.units.extend([
        SoldierNPC(self, "SNPC 1", (15,6)),
        SoldierNPC(self, "SNPC 2", (21,6)),
        SoldierNPC(self, "SNPC 3", (29,13)),
        BasicFriendlyNPC(self, "FNPC 1", (26,27)),
        BasicFriendlyNPC(self, "FNPC 2", (25,33)),
        BasicFriendlyNPC(self, "FNPC 3", (30,28)),
      ])
      furnace_guy = BasicFriendlyNPC(self, "FNPC 4", (6,29))
      (furnace_guy.dx, furnace_guy.dy) = (-1,0)
      furnace_guy.reset(self)
      self.units.append(furnace_guy)
      anvil = Counter(7, 29, "tga/anvil.tga")
      self.walls.append(anvil)
      self.counters.append(Counter(5, 29, "tga/ashcounter.tga", 0))      
      fire_filenames = ["tga/floor_fire_small_" + str(x) + ".tga" for x in [1,2,3,4]]
      fire_frames = [pygame.image.load(f) for f in fire_filenames]
      for f in fire_frames:
        f.set_colorkey((255,255,255))
      self.objects.append(RaisedFireTile(fire_frames, (5,29), 10))

    elif self.filename == 'tga/levels/11.tga':
      self.units.extend([
                     JickerNPC(self, "NPC 3", (self.start_x,self.start_y)),
                     JickerNPC(self, "NPC 4", (self.start_x,self.start_y))
                   ])
      
    elif self.filename == 'tga/levels/13.tga':
      self.units.append(EnemyWizard(self, "Black Wizard", (99,24)))
    elif self.filename == 'tga/levels/14.tga':
      self.units.append(EnemyWizard(self, "Black Wizard", (2, 58)))
    elif self.filename == 'tga/levels/17.tga':
      num_playable_units = 0
      for unit in self.units:
        if unit.playable:
          num_playable_units += 1
      if num_playable_units < 5:
        first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
        last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
        name = first_name+" "+last_name
        self.units.append(PlayerArcher(self, name, (self.start_x,self.start_y)))
      # # # # # # # # # # # # # # # #
      # Town number 2, not in game  #
      # # # # # # # # # # # # # # # #
    elif self.filename == 'tga/levels/21.tga':
      # Bar scene
      for (x,y) in [(14,7), (15,7), (16,7), (18,7), (20,7)]:
        self.objects.append(BasicObject(x,y, "tga/bottle_2.tga"))
      for (x,y) in [(17,11), (19,11), (21,11)]:
        self.objects.append(BasicObject(x,y, "tga/mug_1.tga"))
      for (x,y) in [(17,12), (19,12), (21,12)]:
        self.walls.append(BasicObject(x,y, "tga/stool_1.tga"))

      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name1 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name2 = first_name+" "+last_name
      first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name3 = first_name+" "+last_name
      first_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.female_name_suffixes)
      last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
      name4 = first_name+" "+last_name
      self.units.append(BasicFriendlyNPC(self, name1, (18,10))) #Bartender
      self.units.append(BasicFriendlyNPC(self, name2, (42,14))) #Priest
      self.units.append(ShopkeeperNPC(self, name3, (10,23)))
      self.units.append(PlayerFemaleMeleeNPC(self, name4, (26,9)))
    t2 = pygame.time.get_ticks()
  def check_victory(self, game):
    hostile_units = []
    for unit in game.units:
      if unit.hostile:
        hostile_units.append(unit.name)  
        
    if self.filename in ["tga/levels/level0.tga", "tga/levels/level0a.tga", "tga/levels/level0b.tga"]:
      if len(hostile_units) > 0:
        return False
      elif len(self.generators) > 0:
        return False
      return True
    elif self.filename in ["tga/levels/level0c.tga"]:
      npcs = [u for u in game.units if (not u.playable and not u.hostile)]
      if len(npcs) == 0:
        return False
      for u in npcs:
        if len(u.waypoints) > 0:
          break
      else:
        return True
    else:
      for unit in game.units:
        if unit.playable:
          if (unit.x, unit.y) in self.goal_squares:
            return True
      #if len(hostile_units) == 0:
      #  return True
      return False
  
  def check_defeat(self, game):
    if self.filename in ["tga/levels/level0c.tga"]:
      npcs = [u for u in game.units if (not u.playable and not u.hostile)]
      if len(npcs) == 0:
        return True
    friendly_units = []
    for unit in game.units:
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

    
  def load_level_data(self, game):
    LevelFromFile.load_level_data(self, game)
    
    pixel_array = pygame.PixelArray(pygame.image.load(self.filename))
    # this is redundant, you should probably just set self.pixel_array in
    # the parent method instead
    self.generators = pixel_array_to_battle_generators(self, pixel_array, 10,
      self.max_zombies, self.max_superzombies, self.max_bandits, self.max_wizards, self.max_total)
    # I think these generators overwrite the ones set in the parent method
    
  def check_victory(self, game):
    if game.time_remaining == 0:
      return True
    else:  
      return False
      
  def check_defeat(self, game):
    if LevelFromFile.check_defeat(self, game):
      return True
    else:
      return False


      
