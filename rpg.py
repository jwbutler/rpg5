from __future__ import division
import math
import sys
import os
import string
import glob

from classes import *
from equipment import *
from units import *
from enemy_humans import *
from npcs import *
from wizards import *
from zombies import *
from generators import *
import levels

class RPG:
  
  # # # # #
  # INIT  #
  # # # # #
    
  def __init__(self, battle_mode=False, time_remaining=0):
    
    self.VISION_RADIUS = 15
    
    self.debug = True # creates some console output
    self.directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    self.keyName = None
    self.keyMods = None
    #self.list_keys = [] #unused?
    
    # Used for double-tapping number keys
    # to bring the camera to a unit.
    self.last_number_key = None
    self.last_number_ticks = 0
    self.last_number_max_ticks = 4

    self.walls = []
    self.invisible_walls = []
    self.parapets = []
    self.trees = []
    self.objects = [] #unused?
    self.rock_piles = [] #mostly rocks
    self.corpses = []
    self.doors = []
    self.roofs = []
    self.gates = []
    self.counters = []
    self.units = [] 
    self.darts = []
    self.generators = []
    self.containers = [] #unused
    self.water_tiles = []
    self.fire_tiles = []
    self.blood = []
    self.healing_flashes = []
    self.pointers = []
    self.powerups = []
    self.crops = []
    self.fps = 12
    self.tps = 12
    self.ticks = 0
    self.score = 0
    self.kills = 0
    self.bandits_killed = 0
    self.list_dir_keys = [pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9]
    self.list_dir_names = [pygame.key.name(x) for x in self.list_dir_keys]
    self.main_menu = MainMenu(self, 'tga/menu.tga', pygame.Rect(0, 480, 800, 120), True)
    self.paused = False
    self.show_inventory_screen = False
    self.level_clear_screen_active = False
    self.scrolling_text_active = False
    self.show_buysell_screen = False
    self.show_dialog = False
    self.sound_paused = False
    self.music_paused = False
    self.draw_timer_disabled = False
    self.redraw_floor = False
    self.dialog_boxes = []
    self.dialog_background = pygame.image.load("tga/textbox_1.tga")
    self.dialog_arrow = pygame.image.load("tga/textbox_2.tga")
    self.dialog_arrow.set_colorkey((0,0,0))
    self.dialog_x = pygame.image.load("tga/textbox_3.tga")
    self.dialog_x.set_colorkey((0,0,0))
    self.dialog_index = 0
    self.dialog_box = None
    self.buysell_screen = pygame.image.load("tga/buysell.tga")
    self.text_lines = []
    self.drag_x1 = self.drag_y1 = self.drag_x2 = self.drag_y2 = None
    self.drag_rect = None
    self.drag_rect_locked = False
    self.death_screen_active = False
    self.menus = [self.main_menu]
    self.depth_tree = DepthTree(self)
    self.insert_depth_tree_nodes()
    
    self.load_level_filenames()
    #self.all_levels = self.load_all_levels(levels)
    
    # Target tiles: these show up under units based on whether they're
    # targeted by a player, hostile, friendly, or neutral.
    # Horribly named! Clean this up!
    self.target_tile_darkred = pygame.image.load('tga/tile_darkred.tga')
    self.target_tile_darkred.set_colorkey((255,255,255))    
    self.target_tile_white = pygame.image.load('tga/24x12 square tile.tga')
    self.target_tile_white.set_colorkey((0,0,0))   
    self.target_tile_lightred = pygame.image.load('tga/tile_lightred.tga')
    self.target_tile_lightred.set_colorkey((255,255,255))
    self.target_tile_green = pygame.image.load('tga/tile_green.tga')
    self.target_tile_green.set_colorkey((255,255,255))
    self.target_tile_blue = pygame.image.load('tga/tile_blue.tga')
    self.target_tile_blue.set_colorkey((255,255,255))
    self.target_tile_lightblue = pygame.image.load('tga/tile_lightblue.tga')
    self.target_tile_lightblue.set_colorkey((255,255,255))
    self.target_tile_cyan = pygame.image.load('tga/tile_cyan.tga')
    self.target_tile_cyan.set_colorkey((255,255,255))
    self.target_tile_black = pygame.image.load('tga/tile_black.tga')
    self.target_tile_black.set_colorkey((255,255,255))
    self.selected_tile = pygame.image.load('tga/tile_selected.tga')
    self.selected_tile.set_colorkey((255,255,255))
    
    for menu in self.menus:
      menu.refresh()
    self.fullscreen = True
    for arg in sys.argv:
      if arg in ['-w', '-windowed', '-window', '--w', '--windowed', '--window']:
        self.fullscreen = False
    if self.fullscreen:
      self.screenbig = pygame.display.set_mode((800,600), pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF, 16)
    else:
      self.screenbig = pygame.display.set_mode((800,600), 0, 16)
    self.screen = pygame.surface.Surface((400,300))
    self.floor_layer = pygame.surface.Surface((400,300))
    self.object_layer = pygame.surface.Surface((400,300))
    pygame.display.set_caption("Warpath")
    icon_surface = pygame.image.load("tga/sword_icon.tga").convert()
    icon_surface.set_colorkey((255,255,255))
    pygame.display.set_icon(icon_surface)
        
    self.level_index = 0
    self.battle_mode = battle_mode
    if battle_mode: #True or 'battle2'
      self.time_remaining = time_remaining
    
    self.sprite_cache = {}
    sprite_names = ["bow", "beard", "cloak", "club", "crown", "hairpiece",
                    "hat", "hat2", "helmet", "helm2", "mail", "player",
                    "robed_wizard", "shield", "shield2", "shield3",
                    "sword", "spear", "zombie"]
    t1 = pygame.time.get_ticks()
    self.preload_sprites(sprite_names)
    t2 = pygame.time.get_ticks()
    print "Preload sprites:", t2-t1
    
    self.load_tile_textures()
    
  def load_tile_textures(self):
    """ Set the textures for the default terrain types.
    Many of these are generated, so we call the generate_tile() function
    rather than loading image files. """
    
    self.tiles = {}
    #tiles['dirt'] = ["tga/dirt_24x12_" + str(x) + ".tga" for x in [1,2,3,4]]
    #tiles['stone'] = ["tga/floor_24x12_stone_" + str(x) + ".tga" for x in [1,2,3,4]]
    #tiles['grassdirt'] = ["tga/grassdirt_24x12_" + str(x) + ".tga" for x in [1,2,3,4]]
    #tiles['grass'] = ["tga/grass_24x12_" + str(x) + ".tga" for x in [1,2,3,4]]
    self.tiles['water'] = ["tga/water_" + str(x) + ".tga" for x in [1,2,3,4]]
    self.tiles['dirtwater'] = ["tga/dirtwater_" + str(x) + ".tga" for x in [1,2,3,4]]
    self.tile_surfaces_dict = {}
    for (key,filename_list) in self.tiles.items():
      surface_list = [pygame.image.load(filename) for filename in filename_list]
      for surface in surface_list:
        surface.set_colorkey((255,255,255))
      self.tile_surfaces_dict[key] = surface_list
    self.tile_surfaces_dict['grass'] = [self.generate_tile((0,128,0),0.1,0.3,True) for x in range(8)]
    self.tile_surfaces_dict['grassdirt'] = [self.generate_tile((48,96,0),0.2,0.4,False) for x in range(8)]
    self.tile_surfaces_dict['dirt'] = [self.generate_tile((72,48,0),0.2,0.4,True) for x in range(8)]
    self.tile_surfaces_dict['rocky'] = [self.generate_tile((64,64,64), 0.2,0.5, True) for x in range(8)]
    self.tile_surfaces_dict['stone'] = [self.generate_tile((96,96,96), 0.2,0.2, True) for x in range(8)]
    
    # Link the tiles with colors in map files
    self.tile_color_dict = {
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

  """
  ALL LEVELS
  """
  def distance(self, obj_1, obj_2):
    x_1 = obj_1[0]
    y_1 = obj_1[1]
    x_2 = obj_2[0]
    y_2 = obj_2[1]
    dx = x_2 - x_1
    dy = y_2 - y_1
    return (dx*dx + dy*dy)**0.5  

  def load_level_filenames(self):
    """Set the path for each level map.  In the future we should load this
    from a text file."""
    self.level_filenames = []
    self.level_filenames.append('tga/levels/wizardtest.tga')
    #self.level_filenames.append('tga/levels/level0a.tga') #zombie wizard playground
    #self.level_filenames.append('tga/levels/level0b.tga') #enemy humans
    #self.level_filenames.append('tga/levels/level0c.tga') #escort
    for n in [0,1,2]:
      #level 0 is a stupid, stupid hack to enable intro text
      self.level_filenames.append("tga/levels/" + str(n) + ".tga")
    self.level_filenames.append('tga/levels/townlol.tga') #town, LOL
    self.level_filenames.append('tga/levels/townlol2.tga') #exact copy of townlol but with wizards
    self.level_filenames.append('tga/levels/Road_1.tga')
    self.level_filenames.append('tga/levels/Road_3.tga') #marsh swamp bog
    self.level_filenames.append('tga/levels/lakemap.tga')
  
  """
  LOAD LEVEL
  """ 
  
  def load_level(self, levels):
    """ Load the next level into the game. """   
    #pygame.event.clear(pygame.USEREVENT)
    
    # Turn off both timers so we don't get a slowdown
    pygame.time.set_timer(pygame.USEREVENT, 0)
    pygame.time.set_timer(pygame.USEREVENT+1, 0)    
    self.paused = True
    filename = self.level_filenames[self.level_index]
    level = levels.LevelFromFile(self, filename)
    
    # Cancel all unit movement
    for unit in self.units:
      (unit.target_x, unit.target_y, unit.target_unit) = (None, None, None)
      (unit.dx, unit.dy) = (self.dir_to_coords(random.choice(self.directions)))
    level.load_level_data()
    
    """ Copy relevant parameters from the level object.
    Need to figure out which are actually necessary
    How do by-reference/by-value work in Python? """
    self.trees = level.trees
    self.roofs = level.roofs
    self.walls = level.walls
    self.parapets = level.parapets
    self.corpses = level.units
    
    self.player_units = [u for u in self.units if u.playable]
    self.check_victory = level.check_victory
    self.check_defeat = level.check_defeat
    for menu in self.menus:
      menu.refresh()
    self.text_lines = [level.filename.split("/")[-1]]
    self.text_ticks = 0
    self.paused = False
    self.ticks = 0
    if self.battle_mode: #True or battle2
      self.streak = 0
      self.streak_ticks = 0
    self.cleared_npcs = 0 #for waypointed escort guys
    self.bandits_killed = 0
    
    # Turn timers back on
    pygame.time.set_timer(pygame.USEREVENT, int(1000/self.fps)) #Frame timer
    pygame.time.set_timer(pygame.USEREVENT+1, int(1000/self.tps)) #Tick timer
    self.center_camera()
    self.floor.draw()
    self.draw()
    
    """ Show introductory dialog, if applicable """
    if self.filename == "tga/levels/2.tga":
      self.show_dialog = True
      self.dialog_boxes = ["PEASANTS: PLZ HALP US WE R TRYING 2 GET HOAM!"
                          ]
      self.dialog_index = 0
      self.dialog_ticks = len(self.dialog_boxes[self.dialog_index])
      self.dialog_box = self.draw_dialog(self.dialog_boxes[self.dialog_index])
    elif self.filename == "tga/levels/townlol.tga":
      self.show_dialog = True
      self.dialog_boxes = ["PEASANTS: PLZ SAVE R VILLAGE!"
                          ]
      self.dialog_index = 0
      self.dialog_ticks = len(self.dialog_boxes[self.dialog_index])
      self.dialog_box = self.draw_dialog(self.dialog_boxes[self.dialog_index])
    self.insert_depth_tree_nodes()
# # # # # # # # # #
# KEYBOARD INPUT  #
# # # # # # # # # #

  def keyboard_input(self):

    # If a dialog box is up, proceed to the next one
    if self.keyName == 'return':
      if self.show_dialog:
        self.show_next_dialog()
          
        # Level clear screen stuff, has been removed
        """
        self.level_clear_screen_active = False
        if self.battle_mode == 'battle2':
          self.time_remaining = 600
        scrolling_text_filename = self.filename.split(".tga")[0] + ".txt"
        if os.path.exists(scrolling_text_filename):
          f = open(scrolling_text_filename, "r")
          self.line_surfaces = self.draw_line_surfaces(f.read().rstrip())
          self.scrolling_text_active = True
          self.scrolling_text_y = 240
        else:
          if len(self.level_filenames) > self.level_index + 1:
            self.level_index += 1
            self.load_level(levels)
            self.ticks = 0
          else:
            print "YOU WIN"
            print self.ticks/self.tps, "s"
            sys.exit(0)
        """
      elif self.scrolling_text_active:
        self.scrolling_text_active = False
        if len(self.level_filenames) > self.level_index + 1:
          self.level_index += 1
          self.load_level(levels)
          self.ticks = 0
        else:
          print "YOU WIN"
          print self.ticks/self.tps, "s"
          sys.exit(0)
          
    # Select/deselect units
    if self.keyName in [str(x) for x in range(1, len(self.player_units)+1)]:
      k = int(self.keyName)
      keymods = pygame.key.get_mods()
      if self.show_inventory_screen:
        pass
        """
        for unit in player_units:
          unit.selected_in_menu = False
        unit = player_units[k]
        unit.selected_in_menu = True
        """
      else:
        unit = self.player_units[k-1]
        # ctrl + # to add to current selection
        for u in self.player_units:
          if self.keyMods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL):
            pass
          else:
            u.selected = False
        if keymods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL):
          unit.selected = not unit.selected
        else:
          unit.selected = True
          if self.last_number_key == k:
            if self.last_number_ticks > 0:
              (self.camera.x, self.camera.y) = (int(unit.x), int(unit.y))
              # it is retarded that these numbers are sometimes not ints
              self.redraw_floor = True
      self.last_number_key = k
      self.last_number_ticks = self.last_number_max_ticks
    # CTRL-A to select all
    elif self.keyName == 'a' and (self.keyMods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL)):
      for unit in self.player_units:
        unit.selected = True
    # CTRL-K to kill an enemy (cheat/dev)
    elif self.keyName == 'k' and (self.keyMods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL)):
      enemy_units = [u for u in self.units if u.hostile]
      if len(enemy_units) > 0:
        enemy_unit = random.choice(enemy_units)
        enemy_unit.die(self)
    # ESC to end
    elif self.keyName == 'escape':
      print 'Key pressed: ESC'
      print "Time:", round(self.ticks/self.tps,1), "s"
      sys.exit(0)
    # Spacebar or P to pause
    elif self.keyName in ['p', 'space']:
      if self.scrolling_text_active:
        if self.keyName == 'space':
          self.scrolling_text_active = False
          if len(self.level_filenames) > self.level_index + 1:
            self.level_index += 1
            self.load_level(levels)
            self.ticks = 0
          else:
            print "YOU WIN"
            print self.ticks/self.tps, "s"
            sys.exit(0)
      # Space also goes to next dialog
      elif self.show_dialog:
        if self.keyName == 'space':
          self.show_next_dialog()
      else:
        self.show_buysell_screen = False
        self.paused = not self.paused
        if self.sound_paused:
          pygame.mixer.unpause()
        else:
          pygame.mixer.pause()
        self.sound_paused = not self.sound_paused

    # CTRL-W to skip a level (cheat/dev)
    elif self.keyName == 'w' and (self.keyMods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL)):
      skip_again = True
      while skip_again:
        scrolling_text_filename = self.filename.split(".tga")[0] + ".txt"
        if os.path.exists(scrolling_text_filename):
          f = open(scrolling_text_filename, "r")
          self.line_surfaces = self.draw_line_surfaces(f.read().rstrip())
          self.scrolling_text_active = True
          self.paused = True
          self.scrolling_text_y = 240
        else:
          if len(self.level_filenames) > self.level_index + 1:
            self.level_index += 1
            self.load_level(levels)
            self.ticks = 0
          else:
            print "YOU WIN"
            print "Time:", self.ticks/self.tps
            sys.exit(0)
        if self.keyMods & (pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT):
          for unit in self.units:
            if not unit.hostile and not unit.playable and not unit.ally:
              skip_again = False
        else:
          break
    # CTRL-S to add score
    elif self.keyName == 's' and (self.keyMods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL)):        
      self.score += 100
    # CTRL-M To pause music
    elif self.keyName == 'm' and (self.keyMods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL)):
      if self.music_paused:
        pygame.mixer.music.unpause()
      else:
        pygame.mixer.music.pause()
      self.sound_music = not self.music_paused
      #music = pygame.mixer.Sound(random.choice(self.music_filenames))
      #music.play()
      
    # ALT-TAB
    elif self.keyName == 'tab' and (self.keyMods & (pygame.KMOD_LALT | pygame.KMOD_RALT)):
      if pygame.display.get_active():
        pygame.display.iconify()
        
    # ALT-ENTER
    elif self.keyName == 'return' and (self.keyMods & (pygame.KMOD_LALT | pygame.KMOD_RALT)):
      self.fullscreen = not self.fullscreen
      screen_buffer = self.screenbig.copy()
      if self.fullscreen:
        self.screenbig = pygame.display.set_mode((800,600), pygame.FULLSCREEN, 16)
      else:
        self.screenbig = pygame.display.set_mode((800,600), 0, 16)
      self.screenbig.blit(screen_buffer, (0,0))
    # Backspace to center the camera
    elif self.keyName == 'backspace':
      self.center_camera()

# # # # # # # #
# MOUSE INPUT #
# # # # # # # #

  def mouse_input(self, event):
    # Convert the mouse position to virtual pixels
    real_posn = pygame.mouse.get_pos() 
    posn = int(real_posn[0]/2), int(real_posn[1]/2)
    if event.type == pygame.MOUSEBUTTONDOWN:
      # # # # # # # # # # # # # # # # # # # # # # 
      # LEFT MOUSEDOWN HANDLER (selection rect) #
      # # # # # # # # # # # # # # # # # # # # # #
      if event.button == 1:
        """
        player_units = []
        for unit in self.player_units:
          if unit.playable:
            player_units.append(unit)
        """
        # Below is a bunch of old inventory screen stuff.
        """
        if self.show_inventory_screen:
          width = 24
          height = 31
          for n in xrange(len(player_units)):
            left = 27*n + 4
            top = 203
            rect = pygame.Rect((left,top,width,height))
            unit = player_units[n]
            if rect.collidepoint(posn):
              for u in player_units:
                u.selected_in_menu = False
                for equip in u.equipment:
                  equip.selected_in_menu = False 
              unit.selected_in_menu = True
              return True
            if unit.selected_in_menu:
              left = 187
              width = 24
              top = 22              
              height = 24
              for equip in unit.equipment:
                if equip.icon:
                  rect = pygame.Rect((left,top,width,height))
                  if rect.collidepoint(posn):
                    for e in unit.equipment:
                      e.selected_in_menu = False
                    equip.selected_in_menu = True
                    return True
                  top += 27
        elif self.show_buysell_screen:
          #handle clicking on items
          left = 10
          width = 100 #?
          top = 16
          height = 14 #?

          for (name, item) in self.items_for_sale:
            if item.icon:
              rect = pygame.Rect((left,top,width,height))
              if rect.collidepoint(posn):
                if item.selected_in_menu:
                  pass
                else:
                  for (n, i) in self.items_for_sale:
                    i.selected_in_menu = False
                  for u in self.units:
                    for e in u.equipment:
                      e.selected_in_menu = False
                  item.selected_in_menu = True
                  return
              top += 14
          buy_button_enabled = False
          for (name, item) in self.items_for_sale:
            if item.selected_in_menu:
              if self.score > item.value:
                buy_button_enabled = True
                selected_item_name = name
                break
          top += 10
          #Buy button
          if buy_button_enabled:
            rect = pygame.Rect((left,top, self.buy_button.get_width(), self.buy_button.get_height()))
            if rect.collidepoint(posn):
              for unit in self.units:
                if unit.selected_in_menu:
                  selected_item = equipment.make(self, selected_item_name)
                  for e in unit.equipment:
                    if e.slot == selected_item.slot:
                      self.score += e.value
                      unit.equipment.remove(e)
                  unit.equipment.append(selected_item) # experimental
                  self.score -= item.value
                  return
          done_button_rect = pygame.Rect((left + self.buy_button.get_width() + 10, top,
                                          self.done_button.get_width(), self.done_button.get_height()))
          if done_button_rect.collidepoint(posn):
            self.disable_buysell_screen()
            return
          #handle clicking on units
          width = 24
          height = 31
          for n in xrange(len(player_units)):
            left = 27*n + 4
            top = 203
            rect = pygame.Rect((left,top,width,height))
            unit = player_units[n]
            if rect.collidepoint(posn):
              for (nn, i) in self.items_for_sale:
                i.selected_in_menu = False
              for u in player_units:
                u.selected_in_menu = False
                for e in u.equipment:
                  e.selected_in_menu = False 
              unit.selected_in_menu = True
              return True
            # draw selected unit's equipment etc
            if unit.selected_in_menu:
              left = 187
              width = 24
              top = 22
              height = 24
              for equip in unit.equipment:
                if equip.icon:
                  rect = pygame.Rect((left,top,width,height))
                  if rect.collidepoint(posn):
                    for i in unit.equipment:
                      i.selected_in_menu = False
                    for (name, item) in self.items_for_sale:
                      item.selected_in_menu = False                    
                    equip.selected_in_menu = True
                    return True
                  top += 27
        else:
        """
        # default; no menu screen is up
        (self.drag_x1, self.drag_y1) = (None, None)
        self.drag_rect = None
        self.drag_rect_locked = False
        #cards are in 640x480, so we use real_posn
        if self.main_menu.rect.collidepoint(real_posn):
          for card in self.main_menu.cards:
            if self.main_menu.card_rect(card).collidepoint(real_posn):
              selected_unit = self.player_units[self.main_menu.cards.index(card)]
              for unit in self.player_units:
                keymods = pygame.key.get_mods()
                if keymods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL):
                  pass
                else:
                  unit.selected = False
              if keymods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL):
                selected_unit.selected = not selected_unit.selected
              else:
                selected_unit.selected = True
        else:
          (self.drag_x1, self.drag_y1) = posn
        
      # # # # # # # # # # # # # # # # # # #
      # RIGHT MOUSEDOWN HANDLER (attack)  #
      # # # # # # # # # # # # # # # # # # #
      elif event.button == 3:
        grid_posn = self.pixel_to_grid_improved(posn)
        if grid_posn:
          (x,y) = grid_posn
          do_right_click_stuff = False #damn is this ghetto
          if self.obstacle_unit((x,y)):
            do_right_click_stuff = True
          elif self.obstacle((x,y)) and not self.obstacle_unit((x,y)):
            #interact with objects?
            pass
          else:
            do_right_click_stuff = True
            for pointer in self.pointers:
              if (pointer.x,pointer.y) == (x,y):
                unit = pointer.return_unit()
                (x,y) = (unit.x,unit.y)
          if do_right_click_stuff:
            for unit in self.units:
              if unit.selected and unit.current_activity not in ['falling', 'decapitated']:
                unit.target_unit = None
                for unit_2 in self.units:
                  if ((unit_2.x, unit_2.y) == (x,y)):
                    if (unit_2.hostile):
                      unit.target_unit = unit_2
                      (unit.target_x, unit.target_y) = (None, None)
                      keymods = pygame.key.get_mods()
                      if unit.has_special and keymods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL) and unit.special_ticks == unit.max_special_ticks:
                        unit.move_to_target_unit_special()
                      elif unit.has_secondary_special and keymods & (pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT) and unit.special_ticks == unit.max_special_ticks:
                        unit.move_to_target_unit_special(True)
                      else:
                        unit.move_to_target_unit()
                    else:
                      if not unit_2.playable:
                        if not unit_2.ally:
                          unit.target_unit = unit_2
                          (unit.target_x, unit.target_y) = (None, None)
                          unit.move_to_target_unit() #do we need a new function?
                if unit.target_unit == None:
                  (unit.target_x, unit.target_y) = (x,y)
                  if unit.current_activity == 'standing':
                    unit.move_to_target_posn()
            

    # # # # # # # # # # # # # # # # # # # # #
    # MOUSE MOTION HANDLER (selection rect) #
    # # # # # # # # # # # # # # # # # # # # #
    elif event.type == pygame.MOUSEMOTION:
      if (pygame.mouse.get_pressed()[0] and self.drag_rect_locked == False):
        if (self.drag_x1, self.drag_y1) != (None, None):
          (self.drag_x2, self.drag_y2) = posn
          left = min(self.drag_x1, self.drag_x2)
          top = min(self.drag_y1, self.drag_y2)
          width = abs(self.drag_x2 - self.drag_x1)
          height = abs(self.drag_y2 - self.drag_y1)
          self.drag_rect = pygame.Rect(left, top, width, height)
        #else:
        #  (self.drag_x1, self.drag_y1) = posn
    # # # # # # # # # # # # # # # # # # # # # # # # #
    # MOUSE BUTTON UP HANDLER (select unit on map)  #
    # # # # # # # # # # # # # # # # # # # # # # # # #
    elif event.type == pygame.MOUSEBUTTONUP:
      if event.button == 1:
        if (self.drag_x1, self.drag_y1) != (None, None):
          (self.drag_x2, self.drag_y2) = posn
          left = min(self.drag_x1, self.drag_x2)
          top = min(self.drag_y1, self.drag_y2)
          width = abs(self.drag_x2 - self.drag_x1)
          height = abs(self.drag_y2 - self.drag_y1)
          self.drag_rect = pygame.Rect(left,top,width,height)
          keymods = pygame.key.get_mods()
          grid_posn = self.pixel_to_grid_improved(posn)
          for unit in self.units:
            if unit.playable:
              overlap_rect = unit.get_rect().clip(self.drag_rect)
              overlap_area = overlap_rect.width * overlap_rect.height
              drag_area = (self.drag_rect.width * self.drag_rect.height)
              if drag_area == 0: #I.E. single click, not drag
                if grid_posn:
                  (x,y) = grid_posn
                  if (unit.x, unit.y) == (x,y):
                    #If CTRL is down, alternate between selected/not selected
                    if keymods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL):
                      unit.selected = not unit.selected
                    else:
                      unit.selected = True
                  else:
                    #If CTRL is down, other units unaffected
                    if keymods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL):
                      pass
                    else:
                      unit.selected = False
              else:
                if overlap_area >= 400: #this is a very strange implementation (i.e. serious WTF).  needs a pixelwise collision detector
                  unit.selected = True
                else:
                  if keymods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL):
                    pass
                  else:
                    unit.selected = False
          self.drag_rect_locked = True

# # # # # #
# UPKEEP  #
# # # # # #

  def do_upkeep(self):
    self.update_camera()
    for unit in self.units:
      unit.increment_ticks()
      unit.do_events()
      for tile in self.fire_tiles:
        if (unit.x,unit.y) == (tile.x,tile.y):
          unit.take_damage(tile.damage, True)
          break

      # Passive health regen - move this to a unit function
      if unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
        if (self.ticks % self.tps) == 0:
          if (unit.current_hp + 1) <= unit.max_hp:
            unit.current_hp += 1

      if unit.playable:
        for powerup in self.powerups:
          if (unit.x, unit.y) == (powerup.x, powerup.y):
            if unit.current_hp < unit.max_hp:
              powerup.proc(unit)
    for tile in self.water_tiles + self.fire_tiles:
      tile.next_frame()
    for p in self.pointers:
      p.ticks -= 1
      if p.ticks == 0:
        self.pointers.remove(p)
    for blood in self.blood:
      if blood.findex == 2:
        if not self.paused:
          blood.ticks += 1
        for blood_2 in self.blood:
          if blood_2 != blood:
            if (blood.x, blood.y) == (blood_2.x, blood_2.y):
              if blood_2.findex == 2:
                blood.merge(blood_2)
                self.blood.remove(blood_2)
    for generator in self.generators:
      generator.do_events()
    for dart in self.darts:
      dart.do_events()
    self.text_ticks += 1
    if self.text_ticks == 10:
      if len(self.text_lines) > 0:
        self.text_lines.pop(0)
      self.text_ticks = 0
    self.ticks += 1
    if self.battle_mode: #True or battle2
      self.time_remaining -= 1
      if self.streak_ticks > 0:
        self.streak_ticks -= 1
      if self.streak_ticks == 0:
        self.streak = 0
    if self.last_number_key:
      if self.last_number_ticks > 0:
        self.last_number_ticks -= 1
    if self.last_number_ticks == 0:
      self.last_number_key = None
      
  def do_paused_upkeep(self):
    self.update_camera()
    for menu in self.menus:
      if menu.visible:
        menu.refresh()
    if self.battle_mode == True: #not battle2
      if self.time_remaining > 0:
        self.time_remaining -= 1 #new addition, for anti-pausing
    if self.last_number_key:
      if self.last_number_ticks > 0:
        self.last_number_ticks -= 1
    if self.last_number_ticks == 0:
      self.last_number_key = None

# # # # #
# DRAW  #
# # # # #
 
  def draw(self):
    ticks_1 = pygame.time.get_ticks()
    self.screen.fill((0,0,0))
    
    # Draw the floor
    if self.redraw_floor:
      self.floor.draw()
      self.redraw_floor = False
    self.screen.blit(self.floor_layer, (0,0))
    ticks_2 = pygame.time.get_ticks()
    
    # Draw animated tiles (water, fire)
    for tile in self.water_tiles + self.fire_tiles:
      for unit in self.units:
        if unit.playable:
          if self.distance((tile.x,tile.y),(unit.x,unit.y)) <= self.VISION_RADIUS:
            rect = tile.get_current_frame().get_rect()
            (rect.left, rect.top) = (tile.x,tile.y)
            if rect.colliderect(pygame.Rect((0,0,400,300))):              
              tile.draw()
              break
              
    ticks_2a = pygame.time.get_ticks()
    
    # Draw all blood! Fade out => destroy it if it's old.
    for blood in self.blood:
      for unit in self.units:
        if unit.playable:
          if self.distance((blood.x,blood.y),(unit.x,unit.y)) <= self.VISION_RADIUS:
            blood.draw()
            break
      if blood.ticks >= 200:
        alpha = blood.frame_3.get_alpha()
        if alpha == None:
          alpha = 255
        if alpha > 0:
          blood.frame_3.set_alpha(alpha - 1)
        else:
          self.blood.remove(blood)

    ticks_2b = pygame.time.get_ticks()
    
    # Draw targeting tiles and such
    mouse_posn = int(pygame.mouse.get_pos()[0]/2), int(pygame.mouse.get_pos()[1]/2)
    grid_posn = self.pixel_to_grid_improved(mouse_posn)
    if grid_posn:
      self.target_tile_white.set_alpha(192)
      self.screen.blit(self.target_tile_white, self.grid_to_pixel(grid_posn))
      self.target_tile_white.set_alpha(255)
      
    # Draw targeting tile under each unit
    for unit in self.units:
      self.draw_unit_tile(unit)

    ticks_3 = pygame.time.get_ticks()
    # Draw all objects, sort them
    #REPLACING THIS SOON
    for door in self.doors:
      door.show_open_icon = False
      squares = door.list_open_squares()
      for unit in self.units:
        if (unit.x, unit.y) in squares:
          door.show_open_icon = True
          break
    """    
    arr = self.objects + self.corpses + self.walls + self.crops + self.trees + self.counters \
        + self.roofs + self.gates + self.parapets + self.units + self.doors + self.darts \
        + self.healing_flashes + self.powerups + self.rock_piles

    print "SORT:", len(arr), '//', len(self.objects), len(self.corpses), len(self.walls), len(self.crops), \
          len(self.trees), len(self.counters), len(self.roofs), len(self.gates), len(self.parapets), len(self.units), \
          len(self.doors), len(self.darts), len(self.healing_flashes)
    """
    ticks_3a = pygame.time.get_ticks()
    # Look for ways to avoid doing this every frame
    #arr.sort(self.z_sort)
    ticks_4 = pygame.time.get_ticks()
    #screen_rect = pygame.Rect((0,0,400,300)) #this should just be an RPG field, right?
    self.depth_tree.draw_all();
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
    ticks_5 = pygame.time.get_ticks()
    if self.drag_rect:
      pygame.draw.rect(self.screen, (0,255,0), self.drag_rect, 2)
      if self.drag_rect_locked == True:
        self.drag_rect = False
        self.drag_rect_locked = False
        (self.drag_x1, self.drag_y1, self.drag_x2, self.drag_y2) = (None, None, None, None)
    for n in range(len(self.text_lines)): #status text, like level load messages
      self.draw_text(self.text_lines[n], self.screen, (1, 1+13*n), 12)
    font = pygame.font.SysFont('Arial', 12)
    if self.battle_mode: #True or battle2
      time = round(self.time_remaining/self.tps, 1)
      streak_ticks = int(self.streak_ticks/self.tps)
    else:
      time = round(self.ticks/self.tps, 1)
      
    # This is the upper-right corner display.  Score, kills, time, streak.
    skt = ["Score: " + str(self.score),
           "Kills: " + str(self.kills),
           "Time: " + str(time)]
    if self.battle_mode: #True or battle2
      skt.append("Streak: " + str(self.streak) + " (" + str(streak_ticks) + ")")

    for n in range(len(skt)):
      surface = font.render(skt[n], False, (255,255,255))
      self.screen.blit(surface, (400 - surface.get_width(), 1+13*n))
    pygame.transform.scale(self.screen, (800,600), self.screenbig)
    ticks_5a = pygame.time.get_ticks()
    for menu in self.menus:
      #if menu.visible:
      menu.refresh()
      self.screenbig.blit(menu.surface, menu.rect)
    ticks_6 = pygame.time.get_ticks()
    
    #Debug text
    
    font = pygame.font.SysFont("Arial", 12)
    txt = "fps:" + str(self.fps) + " draw:" + str(ticks_6 - ticks_1) + \
    " floor:" + str(ticks_2 - ticks_1) + " sort:" + str(ticks_4 - ticks_3a)
    surface = font.render(txt, False, (0,255,0))
    self.screenbig.blit(surface, (0, 0))

    if self.debug:
      print "draw:", ticks_6 - ticks_1
    """
      print "floor:", ticks_2 - ticks_1,
      print "fire/water:", ticks_2a - ticks_2,
      print "blood:", ticks_2b - ticks_2a,
      print "tiles:", ticks_3 - ticks_2b,
      print "doors:", ticks_3a - ticks_3
      print "sort:", ticks_4 - ticks_3,
      print "objects:", ticks_5 - ticks_4,
      print "text:", ticks_5a - ticks_5,
      print "menu:", ticks_6 - ticks_5a
    """
    
    if (ticks_6 - ticks_1) > (1000/self.fps):
      self.fps -= 1
      pygame.time.set_timer(pygame.USEREVENT, int(1000/self.fps))
    elif (ticks_6 - ticks_1) < (800/self.fps):
      if self.fps < 12:
        self.fps += 1
        pygame.time.set_timer(pygame.USEREVENT, int(1000/self.fps))

  # # # # # # # # # #
  # Misc functions  #
  # # # # # # # # # #

  def reset_input(self):
    self.keyName = None
    self.list_keys = []

  def update_camera(self):
    EDGE_WIDTH = 10
    EDGE_HEIGHT = 10
    
    posn = int(pygame.mouse.get_pos()[0]/2), int(pygame.mouse.get_pos()[1]/2)
    (old_x,old_y) = (self.camera.x,self.camera.y)
    if posn[0] < EDGE_WIDTH:
      self.camera.x -= 1
      self.camera.y += 1
    elif posn[0] > self.screen.get_width()-EDGE_WIDTH:
      self.camera.x += 1
      self.camera.y -= 1
    if posn[1] < EDGE_HEIGHT:
      self.camera.x -= 1  
      self.camera.y -= 1
    elif posn[1] > self.screen.get_height()-EDGE_HEIGHT:
      self.camera.x += 1
      self.camera.y += 1
    if not(self.camera.get_rect().colliderect(self.floor.rect)):
      (self.camera.x, self.camera.y) = (old_x, old_y)
    else:
      pass #This code has problems when party members are too spread out.
      """ 
      screen_rect = pygame.rect.Rect((0,0,320,240))
      for unit in self.units:
        if unit.playable:
          if screen_rect.colliderect(unit.get_rect()):
            break
      else:
        (self.camera.x, self.camera.y) = (old_x, old_y)
      """
    if (self.camera.x,self.camera.y) != (old_x, old_y):
      self.redraw_floor = True
      
  def unit_by_name(self, name):
    for unit in self.units:
      if unit.name == name:
        return unit
        
  def corpse_by_name(self, name):
    for unit in self.corpses:
      if unit.name == name:
        return unit
    
# # # # # # # # # # # # #
# THE MAIN EVENT LOOP   #
# consider moving this  #
# to main.py / story.py #
# # # # # # # # # # # # #

  def loop(self):
    draw_events = pygame.event.get(pygame.USEREVENT)
    if len(draw_events) > 2:
      print "Lag!"
      pygame.event.post(draw_events[-1])
    else:
      for e in draw_events:
        pygame.event.post(e)
     
    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        self.key = event.key
        self.keyName = pygame.key.name(event.key)
        self.keyMods = pygame.key.get_mods()
        self.keyboard_input()

      elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
        if self.show_dialog:
          pass
        else:
          self.mouse_input(event)
      elif event.type == pygame.QUIT:
        #handles stuff like alt-F4, maybe others
        sys.exit(0)
           
      elif event.type == pygame.USEREVENT:
        if self.death_screen_active:
          self.draw_death_screen()
        elif self.show_inventory_screen:
          self.draw_inventory_screen()
          pygame.transform.scale(self.screen, (800,600), self.screenbig)
          #pygame.transform.scale2x(self.screen, self.screenbig)
          pygame.display.flip()
        elif self.show_dialog:
          self.screen.fill((0,0,0))
          self.draw()
          self.screen.blit(self.dialog_box, (0,160))
          if self.dialog_ticks % 2 == 0:
            if self.dialog_index + 1 == len(self.dialog_boxes):
              self.screen.blit(self.dialog_x, (0,160))
            else:
              self.screen.blit(self.dialog_arrow, (0,160))
          pygame.transform.scale(self.screen, (800,600), self.screenbig)
          pygame.display.flip()
          if self.dialog_ticks == 0:
            if self.dialog_index >= len(self.dialog_boxes):
              pass
            else:
              self.dialog_box = self.draw_dialog(self.dialog_boxes[self.dialog_index])
              self.dialog_ticks = int(len(self.dialog_boxes[self.dialog_index]))
          pygame.event.clear(pygame.USEREVENT)
        elif self.level_clear_screen_active:        
          """
          self.screen.blit(self.level_clear_screen, (0,0))
          for n in xrange(len(self.text_lines)):
            draw_text(self.text_lines[n], self.screen, (1, 1+13*n), 12)
          pygame.transform.scale(self.screen, (640,480), self.screenbig)
          #pygame.transform.scale2x(self.screen, self.screenbig)
          pygame.display.flip()
          """
        elif self.scrolling_text_active:
          self.screen.fill((0,0,0))
          y = self.scrolling_text_y
          for surface in self.line_surfaces:
            y += surface.get_height()
            x = (400-surface.get_width())/2
            rect = self.screen.blit(surface,(x,y))
          pygame.transform.scale(self.screen, (800,600), self.screenbig)
          pygame.display.flip()
        elif self.show_buysell_screen:
          self.draw_buysell_screen()
          pygame.transform.scale(self.screen, (800,600), self.screenbig)
          pygame.display.flip()
        elif self.paused == False:
          if self.check_victory():
            scrolling_text_filename = self.filename.split(".tga")[0] + ".txt"
            if os.path.exists(scrolling_text_filename):
              f = open(scrolling_text_filename, "r")
              self.line_surfaces = self.draw_line_surfaces(f.read().rstrip())
              self.scrolling_text_active = True
              self.paused = True
              self.scrolling_text_y = 240
            else:
              if len(self.level_filenames) > self.level_index + 1:
                self.level_index += 1
                self.load_level(levels)
                self.ticks = 0
              else:
                print "YOU WIN"
                print self.ticks/self.tps, "s"
                sys.exit(0)
            """
            self.level_clear_screen_active = True
            self.level_clear_screen = pygame.image.load("tga/level_clear.tga") # get Will to make a good one?
            # Rewrite this? Not that it's being used.
            if hasattr(self, 'level_name'):
              level_name = self.level_name
            else:
              level_name = self.filename.split("/")[-1]
            self.text_lines = [
                               level_name + " clear!",
                               "Time: " + str(int(self.ticks/self.tps)) + "seconds",
                               "kills:" + str(self.kills),
                               "", # Let's see if this works to make a blank line
                              ]
            self.text_ticks = 0 #just in case
            """
            """
            scores_path = "scores.txt"
            high_score = 0
            lines = []
            if os.path.exists(scores_path):
              f = open(scores_path, "r")
              for line in f:
                if line.split(",")[0] == self.filename.split("/")[2]:
                  high_score = line.split(",")[1]
                  lines = f.readlines()
                  f.close()
                  break
            else:
              lines = [self.filename.split("/")[1] + "," + str(self.score)]
            if self.score > high_score:
              f = open(scores_path, "w")
              for line in lines:
                if line.split(",")[0] == self.filename.split("/")[1]:
                  print line
                  f.write(self.filename.split("/")[1] + "," + str(self.score))
                else:
                  f.write(line)
              f.close()
            """
            """
            self.text_lines.append("")
            self.text_lines.append("Press ENTER to continue")
            """
          elif self.check_defeat():
            self.death_screen_active = True
            self.paused = True
            self.death_screen = pygame.image.load('tga/gameoverscreen.tga')
            self.death_screen.set_alpha(0)
            pygame.mixer.music.fadeout(3000)
            self.ticks = 0
          else:
            self.draw() #draw everything
            pygame.display.flip()
            if not pygame.mixer.music.get_busy():
              pygame.mixer.music.load(random.choice(self.music_filenames))
              pygame.mixer.music.set_volume(0.5)
              pygame.mixer.music.play(1)
        # end of main conditional
        elif self.paused:
          self.draw() #draw everything
          self.draw_text('Game paused.  Press P to continue', self.screenbig, (5, 5))
          self.draw_text(str(round(self.ticks/self.tps,1)) + " s", self.screenbig, (5, 15))
          self.draw_text("Kills: " + str(self.kills), self.screenbig, (5, 25))
          for menu in self.menus:
            if menu.visible:
              self.screenbig.blit(menu.surface, menu.rect)
          pygame.display.flip()

      elif event.type == pygame.USEREVENT+1: #ticks
        if self.show_dialog:
          self.ticks += 1
          self.dialog_ticks -= 1
          if self.dialog_ticks == 0:
            self.dialog_index += 1
            if self.dialog_index >= len(self.dialog_boxes):
              self.show_dialog = False
              self.dialog_boxes = []
              self.dialog_index = 0
              self.dialog_box = None
              for unit in self.units:
                if unit.current_activity == 'talking':
                  if not unit.playable:
                    unit.end_dialog()
                  else:
                    unit.target_unit = None
                    unit.reset()
                target = unit.target_unit
                if not target:
                  unit.reset()                
                elif (not target.playable) and (not target.hostile) and (not target.ally):
                  unit.reset()
        elif self.paused:
          self.do_paused_upkeep()          
          if self.scrolling_text_active:
            self.scrolling_text_y -= 3
            #if self.scrolling_text_y + surface.get_height() < 0:
            if self.scrolling_text_y < 0:
              self.scrolling_text_active = False
              self.paused = False
              if len(self.level_filenames) > self.level_index + 1:
                self.level_index += 1
                self.load_level(levels)
                self.ticks = 0
              else:
                print "YOU WIN"
                print self.ticks/self.tps, "s"
                quit()

        elif not self.paused:
          self.do_upkeep() # ticks, mana regen, EVENTS!, etc
      else: #includes KeyUp and ActiveEvent
        pass #event is removed from queue
  # Additional functions:

  def draw_black(self, obj, source, (x,y)):
    min_distance = self.floor.rect.width * self.floor.rect.height #upper bound...
    for unit in self.units:
      if unit.playable:
        dist = self.distance((unit.x, unit.y), (obj.x, obj.y))
        if dist < min_distance:
          min_distance = dist
    alpha = 255 - self.distance_to_alpha(min_distance)
    black_source = palette_swap_black(source)
    black_source.set_alpha(alpha)
    self.screen.blit(black_source, (x, y))
    return alpha

  def draw_black_roof(self, obj, source, (x,y)):
    min_distance = self.floor.rect.width * self.floor.rect.height
    for unit in self.units:
      if unit.playable:
        for j in xrange(obj.rect.top, obj.rect.top+obj.rect.height):      
          for i in xrange(obj.rect.left, obj.rect.left+obj.rect.width):
            dx = unit.x - i
            dy = unit.y - j
            distance = ((dx**2) + (dy**2))**0.5
            if distance < min_distance:
              min_distance = distance
    black_alpha = 255 - self.distance_to_alpha(min_distance)
    black_source = palette_swap_black(source)
    black_source.set_alpha(black_alpha)
    self.screen.blit(black_source, (x, y))
    
  def draw_death_screen(self):
    self.screen.blit(self.death_screen, (0,0))
    a = self.death_screen.get_alpha()
    if a < 255:
      self.death_screen.set_alpha(min(a + 5, 255))
    if self.ticks >= 20:
      font = pygame.font.SysFont("Arial", 12)
      score_text = font.render("Your score: " + str(self.score), False, (255,64,64,0))
      w = score_text.get_width()
      x = (400 - w)/2
      self.screen.blit(score_text, (x,188))
    pygame.transform.scale(self.screen, (800,600), self.screenbig)
    #pygame.transform.scale2x(self.screen, self.screenbig)
    pygame.display.flip()
    if not pygame.mixer.music.get_busy():
      pygame.mixer.music.load('sounds/japan.ogg')
      pygame.mixer.music.play(1)
    self.ticks += 1 #use them for fades, etc.
    
  def draw_inventory_screen(self):
    self.screen.blit(self.inventory_screen, (0,0))
    player_units = []
    for unit in self.units:
      if unit.playable and not unit.hostile: #redundant...
        player_units.append(unit)
    for n in range(len(player_units)):
      x = 27*n + 4
      y = 203
      unit = player_units[n]
      unit.draw_in_place((x,y))
      if unit.selected_in_menu:
        #write unit's name
        self.draw_text(unit.name, self.screen, (8, 8))
        #write unit's stats
        #inelegant.  Make a draw_tooltip function for basicunit
        self.draw_text("Level: " + str(unit.level), self.screen, (8,28))              
        self.draw_text("Strength: " + str(unit.strength), self.screen, (8,38))
        self.draw_text("Health: " + str(unit.max_hp), self.screen, (8,48))
        if hasattr(unit, 'heal_amount'): 
          self.draw_text("Heal amount: " + str(unit.heal_amount), self.screen, (8,58))
        rect = pygame.Rect((x-1,y-1,26,35))
        pygame.draw.rect(self.screen, (255,255,255), rect, 1)
        #draw equipment
        x1 = 187
        x2 = 213
        y = 22
        for equip in unit.equipment:
          if equip.icon:
            self.screen.blit(equip.icon, (x1,y))
            self.draw_text(equip.name, self.screen, (x2, y))
            if equip.selected_in_menu:
              self.screen.blit(equip.draw_tooltip(), (188,200))
            y += 27
            
  def draw_buysell_screen(self):
    self.screen.blit(self.buysell_screen, (0,0))
    player_units = []
    for unit in self.units:
      if unit.playable and not unit.hostile: #redundant...
        player_units.append(unit)
    
    #draw items for sale - maybe we should use icons instead of text
    font = pygame.font.SysFont("Arial", 12)
    self.screen.blit(font.render("I have the following items for sale:", False, (255,128,255)), (10,2))
    y = 16
    for (name, item) in self.items_for_sale:
      surface1 = font.render(item.name, False, (255,255,255))
      if self.score > item.value:
        price_color = (0,255,0)
      else:
        price_color = (255,0,0)
      surface2 = font.render(" (" + str(item.value) + "g)", False, price_color)
      
      #surfaces 1 and 2 should have the same height
      surface = pygame.surface.Surface((surface1.get_width() + surface2.get_width(), max(surface1.get_height(), surface2.get_height())))
      surface.fill((0,0,0))
      surface.set_colorkey((0,0,0))
      surface.blit(surface1, (0,0))
      surface.blit(surface2, (surface1.get_width(), 0))
      if item.selected_in_menu:
        rect = surface.get_rect()
        self.screen.fill((128,128,192), (10,y,rect.width,rect.height))
      self.screen.blit(surface, (10,y))
      y += surface.get_height()
    y += 10
    
    #draw "Buy" and "Done" buttons
    buy_button_enabled = False
    for (name, item) in self.items_for_sale:
      if item.selected_in_menu:
        if self.score > item.value:
          buy_button_enabled = True
    if buy_button_enabled:
      self.screen.blit(self.buy_button, (10,y))
    else:
      self.screen.blit(self.buy_button_disabled, (10,y))
    self.screen.blit(self.done_button, (20 + self.buy_button.get_width(), y))

    y += max(self.buy_button.get_height(), self.done_button.get_height()) #should be the same
    self.screen.blit(font.render("Gold: " + str(self.score), False, (255,255,0)), (10, y))

    
    #draw player icons (along bottom)
    for n in xrange(len(player_units)):
      x = 27*n + 4
      y = 203
      unit = player_units[n]
      unit.draw_in_place((x,y))
      #write tooltips for units
      if unit.selected_in_menu:
        rect = pygame.Rect((x-1,y-1,26,35))
        pygame.draw.rect(self.screen, (255,255,255), rect, 1)
        #draw icons for equipment
        x1 = 187
        x2 = 213
        y = 22
        for equip in unit.equipment:
          if equip.slot != "hair":
            try:
              self.screen.blit(equip.icon, (x1,y))
            except:
              pass#print "TODO: make icon for " + equip.anim_name
            self.draw_text(equip.name, self.screen, (x2, y))
            if equip.selected_in_menu:
              self.screen.blit(equip.draw_tooltip(), (188,200))
            y += 27
      for (name, item) in self.items_for_sale:
        if item.selected_in_menu:
          self.screen.blit(item.draw_tooltip(), (188,200))            
            
  def draw_dialog(self, message):
    surface = self.dialog_background.copy()
    font = pygame.font.SysFont("Arial", 12)
    y = 10
    line_surfaces = self.draw_line_surfaces(message, 300)
    for line_surface in line_surfaces:
      surface.blit(line_surface, (10, y))
      y += line_surface.get_height()
    return surface
    
  def draw_line_surfaces(self, str, width=400):
    """ Lines of dialog, that is. """
    words = str.split()
    line_surfaces = []
    font = pygame.font.SysFont("Arial", 12)
    lines = []
    line_index = 0
    lines.append("")
    for word in words:
      new_line = string.join([lines[line_index], word])
      surface = font.render(new_line, True, (255,255,255))
      if surface.get_width() > width:
        line_index += 1
        lines.append(word)
        continue
      else:
        lines[line_index] = new_line
    for line in lines:
      line_surface = font.render(line, True, (255,255,255))
      line_surfaces.append(line_surface)
    return line_surfaces
    
  def enable_buysell_screen(self, items_for_sale):
    self.show_buysell_screen = True
    self.items_for_sale = [] #this way we don't lose ordering
    for item_name in items_for_sale:
      self.items_for_sale.append(
                                 (item_name, equipment.make(self, item_name))
                                )
    self.buy_button = pygame.image.load("tga/buy.tga")
    self.done_button = pygame.image.load("tga/done.tga")    
    self.buy_button_disabled = pygame.image.load("tga/buy_disabled.tga")
    for unit in self.units:
      if not unit.hostile:
        unit.selected_in_menu = True
        break
        
  def draw_unit_tile(self, unit):
    if unit.hostile:
      in_range = targeted = False
      for friendly_unit in self.units:
        if not friendly_unit.hostile:
          if not in_range:
            if self.distance((friendly_unit.x,friendly_unit.y), (unit.x,unit.y)) <= self.VISION_RADIUS:
              in_range = True
          if friendly_unit.target_unit == unit:
            targeted = True
      if in_range:
        if targeted:
          self.screen.blit(self.target_tile_lightred, self.grid_to_pixel((unit.x, unit.y)))
        else:
          self.screen.blit(self.target_tile_darkred, self.grid_to_pixel((unit.x, unit.y)))
    elif unit.playable:
      if unit.selected:
        self.screen.blit(self.selected_tile, self.grid_to_pixel((unit.x, unit.y)))
      else:    
        self.screen.blit(self.target_tile_green, self.grid_to_pixel((unit.x, unit.y)))
      if (unit.target_x, unit.target_y) != (None, None):
        self.screen.blit(self.target_tile_white, self.grid_to_pixel((unit.target_x, unit.target_y)))
    elif unit.ally:
      self.screen.blit(self.target_tile_cyan, self.grid_to_pixel((unit.x, unit.y)))
    else: #NPCs
      for unit_2 in self.units:
        if unit_2.playable:
          if unit_2.target_unit == unit:
            self.screen.blit(self.target_tile_lightblue, self.grid_to_pixel((unit.x, unit.y)))
      else:
        self.screen.blit(self.target_tile_blue, self.grid_to_pixel((unit.x, unit.y)))
        
  def disable_buysell_screen(self):
    self.show_buysell_screen = False
    self.items_for_sale = buy_button = self.done_button = self.buy_button_disabled = None
    for unit in self.units:
      unit.selected_in_menu = False
      if unit.playable:
        unit.target_unit = None
        unit.reset()
  
  def award_streak_bonus(self):
    if self.battle_mode == True:
      if self.streak >= 10:
        bonus_time = 25
      elif self.streak >= 7:
        bonus_time = 20
      elif self.streak >= 4:
        bonus_time = 15
      else:
        bonus_time = 10
      self.time_remaining += bonus_time
    elif self.battle_mode == "battle2":
      if self.streak >= 10:
        bonus_score = 25
      elif self.streak >= 7:
        bonus_score = 20
      elif self.streak >= 4:
        bonus_score = 15
      else:
        bonus_score = 10    
      self.score += bonus_score
    self.text_lines.append("Streak: " + str(self.streak) + "!")
    
  def center_camera(self):
    total_x = 0; total_y = 0; num_units = 0
    for unit in self.units:
      if unit.playable:
        total_x += unit.x
        total_y += unit.y
        num_units += 1
    avg_x = int(total_x / num_units); avg_y = int(total_y / num_units)
    (self.camera.x, self.camera.y) = (avg_x, avg_y)
    self.redraw_floor = True

  def LOS(self, (x1,y1), (x2,y2)):
    dx = x2 - x1
    dy = y2 - y1
    error = 0
    if (dx != 0) and (dy == 0 or abs(dy) < abs(dx)): #Trial and error FTW
      x_sign = dx/abs(dx)
      if dy != 0:
        y_sign = dy/abs(dy)
      else:
        y_sign = 1
      y = y1
      for x in range(int(x1), int(x2), int(x_sign)): #try x2+x_sign
        if self.obstacle((x,y)) and not self.obstacle_unit((x,y)):
          return False
        if dx != 0:
          error += abs(dy/dx)
        else:
          error += 1
        while error >= 0.5:
          error -= 1
          y += y_sign
        #if (x,y) not in self.floor.tiles:
        if not self.floor.rect.collidepoint((x,y)):        
          return False
    else:
      if dy != 0:
        y_sign = dy/abs(dy)
      else:
        y_sign = 1
      if dx != 0:
        x_sign = dx/abs(dx)
      else:
        x_sign = 1
      x = x1
      for y in range(int(y1), int(y2), int(y_sign)): #try y2+y_sign
        if self.obstacle((x,y)) and not self.obstacle_unit((x,y)):
          return False
        if dy != 0:
          error += abs(dx/dy)
        else:
          error += 1
        while error >= 0.5:
          error -= 1
          x += x_sign
        #if (x,y) not in self.floor.tiles:
        if not self.floor.rect.collidepoint((x,y)):
          return False
    return True
    
  def preload_sprites(self, sprite_names):
    filenames = glob.glob("tga//*.tga")
    for f in filenames:
      for s in sprite_names:
        base_filename = os.path.split(f)[-1]
        if base_filename[:len(s)] == s:
          surface = pygame.image.load(f).convert()
          surface.set_colorkey((255,255,255))
          self.sprite_cache[f] = surface
          break

  def show_next_dialog(self):
    self.dialog_index += 1
    self.dialog_ticks = 0
    if self.dialog_index >= len(self.dialog_boxes):
      self.show_dialog = False
      self.dialog_boxes = []
      self.dialog_index = 0
      self.dialog_box = None
      for unit in self.units:
        if unit.current_activity == 'talking':
          if not unit.playable:
            unit.end_dialog()
          else:
            unit.target_unit = None
            unit.reset()
    else:
      self.dialog_box = self.draw_dialog(self.dialog_boxes[self.dialog_index])
      self.dialog_ticks = int(len(self.dialog_boxes[self.dialog_index]))

  ### From the old functions.py ###
  
  def coords_to_dir(self, (x,y)):
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

  def draw_target(self, obj):
    """ Draws the target symbol over the target. """
    source = pygame.image.load('tga/target.tga')
    source.set_colorkey((255,255,255))
    self.screen.blit(source, adjusted_posn(game, obj.x, obj.y, 152, 20))



  def distance_sort(self, a, b, target):
    """
    Sort a list of npcs/objects by distance from the target.
    """
    target_posn = (target.x, target.y)
    a_posn = (a.x, a.y)
    b_posn = (b.x, b.y)
    if self.distance(target_posn, a_posn) > self.distance(target_posn, b_posn): return 1
    if self.distance(target_posn, a_posn) == self.distance(target_posn, b_posn): return 0
    if self.distance(target_posn, a_posn) < self.distance(target_posn, b_posn): return -1
      
  def distance_sort_posn(self, a, b, target):
    """
    Sort a list of POSNS by distance from the target.
    """
    if self.distance(target, a) > self.distance(target, b): return 1
    if self.distance(target, a) == self.distance(target, b): return 0
    if self.distance(target, a) < self.distance(target, b): return -1
          
  def obstacle(self, (x, y)):
    """
    True if there is an object or npc at the given (x,y).
    True if the given (x,y) is out of bounds.
    False if it is "safe".
    """
    for obj in self.units + self.walls + self.trees + self.counters + self.water_tiles:
      #collide with any object/npc? (not doors, not corpses)
      if (x,y) == (obj.x, obj.y):
        return True
    for obj in self.invisible_walls:
      if (x,y) == obj:
        return True
    for obj in self.gates:
      if obj.collide(x,y):
        return True
      # collide with boundary?
    if not self.floor.rect.collidepoint((x, y)):
      return True
    return False

  def obstacle_unit(self, (x,y)):
    """ Is there an NPC at (x,y)? """
    for unit in self.units:
      if (unit.x, unit.y) == (x, y):
        return unit
    return None
    
  """
  def acquire_target(self, shift = None):
    t1 = pygame.time.get_ticks()
    self.npcs.sort(lambda a,b: distance_sort(a, b, self.player))
    t2 = pygame.time.get_ticks()
    print "NPCs sort: ", t2-t1, len(self.npcs)
    if self.target == None:
      if self.npcs:
        return self.npcs[0]
    else:
      index = self.npcs.index(game.target)
      if shift:
        return self.npcs[(index-1) % len(self.npcs)]
      else:
        return self.npcs[(index+1) % len(self.npcs)]
  """
  def adjacent_squares(self, (x, y)):
    squares = [(x-1, y-1), (x, y-1), (x+1, y-1), (x-1, y), (x+1, y), (x-1, y+1), (x, y+1), (x+1, y+1)]
    return squares

  def knight_move(self, (x, y)):
    return [(x-1, y-2), (x+1, y-2), (x-2, y-1), (x+2, y-1), (x-2, y+1), (x+2, y+1), (x-1, y+2), (x+1, y+2)]

  """
  def get_next_square(self, source, target):
    print "In get_next_square()"
    squares = adjacent_squares((source[0], source[0]))
    squares.sort(lambda a,b: self.distance_sort(a,b,target))
    for square in squares:
      if not self.obstacle(square):
        return square

  def point_at(self, source, target):
    print "In point_at()"
    squares = adjacent_squares((source.x, source.y))
    squares.sort(lambda a,b: self.distance_sort(a,b,target))
    for square in squares:
      if square == (target.x, target.y):
        source.dx = square[0] - source.x
        source.dy = square[1] - source.y
        return True
      elif not self.obstacle(square):
        source.dx = square[0] - source.x
        source.dy = square[1] - source.y
        return True
  """
  def check_los(self, (x1,y1), (x2,y2)):
    (x,y) = (x1,y1)
    h = ( (x2-x1)**2 + (y2-y1)**2 ) ** 0.5
    if h == 0:
      return True
    dx = (x2-x1)/h
    dy = (y2-y1)/h
    while abs(x2-x) > 0.5 or abs(y2-y) > 0.5:
      (rx, ry) = (round(x), round(y))
      if (rx, ry) not in [(x1,y1), (x2,y2)]:
        if self.obstacle((rx, ry)):
          if not self.obstacle_unit((rx, ry)):
            return False
      x += dx
      y += dy
    return True

  # For the way old numpad based controls
  """      
  def key_to_dir(self, key):
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
  """

  """
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
  """

  def draw_text(self, txt, surface, (x, y), size=12):
    """ Render string txt at the specified x and y coordinates. """
    font = pygame.font.SysFont('Arial', size)    
    source = font.render(txt, False, (255,255,255))
    surface.blit(source, (x,y))
      
  def grid_to_pixel_OLD_RESOLUTION(self, (x, y)):
    # returns top left point of the floor tile?
    # THIS NEEDS TO BE TESTED
    a = (x - self.camera.x)*12 - (y - self.camera.y)*12 + 152
    b = (x - self.camera.x)*6 + (y - self.camera.y)*6 + 80
    return (a,b)

  def grid_to_pixel(self, (x, y)):
    # returns top left point of the floor tile?
    # THIS NEEDS TO BE TESTED
    X_OFFSET = int(self.screen.get_width()/2 - 12)
    Y_OFFSET = int(self.screen.get_height()/2 - 8)
    
    a = (x - self.camera.x)*12 - (y - self.camera.y)*12 + X_OFFSET
    b = (x - self.camera.x)*6 + (y - self.camera.y)*6 + Y_OFFSET
    return (a,b)

  """      
  def pixel_to_grid_defunct(game, a, b):
      x = (a + 2*b - 312)/24 + game.camera.x
      y = (a - 2*b + 8)/(-24) + game.camera.y
      return (x,y)
  """

  def pixel_to_grid_improved(self, (x, y)):
    ticks_1 = pygame.time.get_ticks()
    camera_rect = self.camera.get_rect()
    for ty in range(camera_rect.top, camera_rect.bottom):
      for tx in range(camera_rect.left, camera_rect.right):
        (left, top) = self.grid_to_pixel((tx, ty))
        tile_rect = pygame.Rect(left, top, 24, 12)
        if tile_rect.collidepoint((x,y)):
          try:
            tile = self.floor.get_tile((tx,ty))
            pixel_array = pygame.PixelArray(tile)
            #(r,g,b,a) = tile.get_at((x - left, y - top))
            (r,g,b,a) = tile.unmap_rgb(pixel_array[x - left][y - top])
            if (r,g,b,a) != (255,255,255,255):
              ticks_2 = pygame.time.get_ticks()
              return (tx,ty)
          except KeyError as e:
            pass
          except Exception as e:
            print e
            return None
    return None

  def adjacent_directions(self, dir):
    if dir == 'N': return ['NW', 'NE']
    if dir == 'NE': return ['N', 'E']
    if dir == 'E': return ['NE', 'SE']
    if dir == 'SE': return ['E', 'S']
    if dir == 'S': return ['SE', 'SW']
    if dir == 'SW': return ['S', 'W']
    if dir == 'W': return ['SW', 'NW']
    if dir == 'NW': return ['W', 'N']

  def palette_swap_multi(self, surface, palette_swaps):
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
    
  def palette_swap(self, surface, source_color, dest_color):
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
    # draw a whole bunch of things, player or npcs mostly, with awkward conditionals for things
    source = obj.get_current_frame()
    screen.blit(source, adjusted_posn(game, obj.x, obj.y,152+dx, dy))
  """

  def dir_to_coords(self, direction):
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
  
  """
  def distance_to_alpha(self, distance):
    alpha = 255 - (distance-16)*64
    alpha = min(alpha, 255)
    alpha = max(alpha, 0)
    return alpha
  """
    
  def get_tiles_in_line(self, (x1,y1), (x2,y2)):
    # Used for LOS calculations
    (x,y) = (x1,y1)
    r = 1
    tiles = []
    while self.distance((x,y),(x2,y2)) > r:
      for xx in [x-r/4, x, x+r/4]:
        for yy in [y-r/4, y, y+r/4]:
          if (int(xx), int(yy)) not in tiles:
            tiles.append((int(xx),int(yy)))
      theta = math.atan2((y2-y),(x2-x))
      x += (r*math.cos(theta))
      y += (r*math.sin(theta))
    return tiles
    
  def line_of_sight(self, (x1,y1), (x2,y2), radius=10):
    if self.distance((x1,y1),(x2,y2)) <= radius:
      line_of_tiles = get_tiles_in_line((x1,y1),(x2,y2))
      for tile in line_of_tiles:
        if tile == (x1,y1):
          continue
        elif self.obstacle_unit(tile):
          pass
        elif self.obstacle(tile):
          return False
      return True
    else:
      return False
      
  # document this, variable names really suck
  def generate_tile(self, color, var1=0.2, var2=0.2,uniform=False):
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
    
  def get_slash_directions(self, dir):
    # Given a compass direction, return all compass directions in a circle
    # starting on the initial dir.
    # I don't think we need this, thanks to the below
    anim_directions = []
    i = self.directions.index(dir)
    for d in self.directions:
      j = self.directions.index(d)
      if j >= i:
        anim_directions.append(d)
    for d in self.directions:
      j = self.directions.index(d)
      if j < i:
        anim_directions.append(d)
    return anim_directions

  def rotate_45_degrees_clockwise(self, direction):
  # ex: 'N' => 'NE'
    directions_dict = {"N":"NE", "NE":"E", "E":"SE", "SE":"S", "S":"SW", "SW":"W", "W":"NW", "NW":"N"}
    return directions_dict[direction]
    
  def rotate_45_degrees_counterclockwise(self, direction):
  # ex: 'N' => 'NE'
    directions_dict = {"N":"NW", "NW":"W", "W":"SW", "SW":"S", "S":"SE", "SE":"E", "E":"NE", "NE":"N"}
    return directions_dict[direction]
    
  def rcw(self, dir):
    return self.rotate_45_degrees_clockwise(dir)
    
  def rccw(self, dir):
    return self.rotate_45_degrees_counterclockwise(dir)
    
  #Old functions2.py

  def rgb_to_tile(self, (r,g,b), tile_color_dict, tile_surfaces_dict, default_tile_type):
    try:
      tile_type = tile_color_dict[(r,g,b)]
      tile_surface_list = tile_surfaces_dict[tile_type]
      tile_surface = random.choice(tile_surface_list)
    except:
      tile_surface_list = tile_surfaces_dict[default_tile_type]
      tile_surface = random.choice(tile_surface_list)
    return tile_surface

  def rgb_to_tile_OLD(self, (r,g,b)):
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
    
  def rgb_to_wall_icons(self, (r,g,b)):
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

  def rgb_to_wall_offset(self, (r,g,b)):
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
    
  def rgb_to_walls(self, (r,g,b), (x,y)):
    icons = self.rgb_to_wall_icons((r,g,b))
    offset = self.rgb_to_wall_offset((r,g,b))
    walls = []
    if icons:
      for z in range(offset+1):
        wall = Wall(self, x, y, random.choice(icons), z)
        walls.append(wall)
    return walls
    
  def rgb_to_counters(self, (r,g,b), (x,y)):
    #Results are in list form for easy addition to game.counters list
    #if (r,g,b) == (128,0,255):
    #  return [Counter(x, y, "tga/counter_stone_1.tga", 0)]
    if (r,g,b) == (128,128,64):
      return [Counter(self, x, y, "tga/counter_wood_1.tga", 0)]
    elif (r,g,b) == (128,0,64):
      return [Counter(self, x, y, random.choice(cave_rock_icons), 0)]
    elif (r,g,b) == (96,96,96):
      return [Counter(self, x, y, random.choice(stalagmite_icons), 0)]
    else:
      return []
      
  def rgb_to_trees(self, (r,g,b), (x,y)):
    trees = []
    icons = ["tga/tree4.tga", "tga/tree5.tga", "tga/tree6.tga"]
    if (r,g,b) == (0,128,0):
      trees.append(Tree(self, x, y, random.choice(icons), 0))
    return trees
    
  def rgb_to_rocks(self, (r,g,b), (x,y)):
    rocks = []
    #icons = ["tga/rocks_24x12_1.tga", "tga/rocks_24x12_2.tga", "tga/rocks_24x12_3.tga"]
    icons = ["tga/floor_rocks_1.tga", "tga/floor_rocks_2.tga", "tga/floor_rocks_3.tga"]  
    if (r,g,b) == (128,0,128):
      rocks.append(Rocks(self, x, y))
    elif (r,g,b) == (128,64,64):
      rocks.append(Rocks(self, x, y))
    return rocks

  def rgb_to_water_tiles(self, (r,g,b), (x,y), water_frames):
    #doesn't include still water
    water_tiles = []
    if (r,g,b) == (0,128,128):
      water_tiles.append(WaterTile(water_frames, (x,y)))
    return water_tiles
    
  def rgb_to_boulders(self, (r,g,b), (x,y)):
    boulders = []
    icons = ["tga/boulder_24x12_1.tga", "tga/boulder_24x12_2.tga", "tga/boulder_24x12_3.tga"]
    if (r,g,b) == (255,0,255):
      boulders.append(Boulder(x, y, random.choice(icons), 0)) #on grass
    if (r,g,b) == (192,0,192):
      boulders.append(Boulder(x, y, random.choice(icons), 0)) #on rocky
    return boulders
    
  def rgb_to_fire_tiles(self, (r,g,b), (x,y), fire_frames, fire_frames_small):
    fire_tiles = []
    if (r,g,b) == (255,0,128): #fire
      fire_tiles.append(FireTile(fire_frames, (x,y), 3))
    elif (r,g,b) == (255,192,128): #fire small
      fire_tiles.append(FireTile(fire_frames_small, (x,y), 2))
    return fire_tiles
    
  def rgb_to_invisible_walls(self, (r,g,b), (x,y)):
    if (r,g,b) in [(0,128,128), #river
                   (255,128,0), #fire?
                   (0,255,255), #edge of river
                   (255,192,128) #more fire?
                  ]:
      return [(x,y)]
    else:
      return []
    
  def rgb_to_crops(self, (r,g,b), (x,y)):
    crops = []
    shrub_icons = ["tga/shrubs_"+str(n)+".tga" for n in [1,2,3]]
    darkshrub_icons = ["tga/darkshrub_"+str(n)+".tga" for n in [1,2,3]]  
    grass_shrub_frequency = 0.005
    if (r,g,b) == (255,255,128):
      crops.append(Crops(self, x, y, 'tga/crops_transparent.tga', 0))
    elif (r,g,b) == (0,255,0): #small chance of shrubs on grass
      if random.random() <= grass_shrub_frequency:
        crops.append(Crops(self, x, y, random.choice(shrub_icons), 0))
    elif (r,g,b) == (0,0,0): #small chance of shrubs on grass - what's black?
      if random.random() <= grass_shrub_frequency:
        crops.append(Crops(self, x, y, random.choice(darkshrub_icons), 0))
    return crops
    
  def pixel_array_to_trees(self, pixel_array):
    trees = []
    icons = ["tga/tree4.tga", "tga/tree5.tga", "tga/tree6.tga"]
    for y in range(pixel_array.surface.get_height()):
      for x in range(pixel_array.surface.get_width()):
        (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
        if (r,g,b) == (0,128,0):
          trees.append(Tree(self, x, y, random.choice(icons), 0))
    return trees
    
  def pixel_array_to_boulders(self, pixel_array):
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
    
  def pixel_array_to_rocks(self, pixel_array):
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
    
  def pixel_array_to_counters(self, pixel_array):
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

  def pixel_array_to_floor(self, pixel_array, tile_color_dict, tile_surfaces_dict, default_tile_type):
    #floor = Floor(["tga/black_floor_24x12.tga"], pixel_array.surface.get_rect())
    t1 = pygame.time.get_ticks()
    floor = BlankFloor(self, pixel_array.surface.get_rect())
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
    print "PATF", t2-t1
    return floor
  """
  def pixel_array_to_floor_OLD(self, pixel_array, tile_color_dict, tile_surfaces_dict, default_tile_type):
    t1 = pygame.time.get_ticks()
    #floor = Floor(["tga/black_floor_24x12.tga"], pixel_array.surface.get_rect())
    floor = BlankFloor(self, pixel_array.surface.get_rect())
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
    """
    
  def pixel_array_to_water_tiles(self, pixel_array):
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

  def pixel_array_to_fire_tiles(self, pixel_array):
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
    
  def pixel_array_to_walls(self, pixel_array):
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
        icons = self.rgb_to_wall_icons((r,g,b))
        if icons:
          offset = rgb_to_wall_offset((r,g,b))
          for z in range(offset+1):
            wall = Wall(self, x, y, random.choice(icons), z)
            walls.append(wall)
    return walls
    
  def pixel_array_to_invisible_walls(self, pixel_array):
    walls = []
    for y in range(pixel_array.surface.get_height()):
      for x in range(pixel_array.surface.get_width()):
        (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
      if (r,g,b) in [(0,128,128), #river
                     (255,128,0), #fire?
                     (0,255,255), #edge of river
                     (255,192,128) #more fire?
                    ]:
        wall = Wall(self, x, y, 'tga/wall_24x39_rocks1.tga', 1) #try w/o the icon next time
    return walls
    
  def pixel_array_to_crops(self, pixel_array):
    crops = []
    shrub_icons = ["tga/shrubs_"+str(n)+".tga" for n in [1,2,3]]
    darkshrub_icons = ["tga/darkshrub_"+str(n)+".tga" for n in [1,2,3]]  
    grass_shrub_frequency = 0.005
    for y in range(pixel_array.surface.get_height()):
      for x in range(pixel_array.surface.get_width()):
        (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
        if (r,g,b) == (255,255,128):
          crops.append(Crops(self, x, y, 'tga/crops_transparent.tga', 0))
        elif (r,g,b) == (0,255,0): #small chance of shrubs on grass
          if random.random() <= grass_shrub_frequency:
            crops.append(Crops(self, x, y, random.choice(shrub_icons), 0))
        elif (r,g,b) == (0,0,0): #small chance of shrubs on grass - what's black?
          if random.random() <= grass_shrub_frequency:
            crops.append(Crops(self, x, y, random.choice(darkshrub_icons), 0))
    return crops
    
  def pixel_array_to_starting_point(self, pixel_array):
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
          
  def pixel_array_to_goal_squares(self, pixel_array):
    goal_squares = []
    for y in range(pixel_array.surface.get_height()):
      for x in range(pixel_array.surface.get_width()):
        (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
        if (r,g,b) == (255,255,0):
          goal_squares.append((x,y))
    return goal_squares
          
  def pixel_array_to_zombies(self, pixel_array):
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
          zombies.append(EnemyZombie(self, "Zombie " + str(n), (x,y)))
          n += 1
    return zombies
    
  def pixel_array_to_generators(self, pixel_array, super_frequency):
    # radius should be an argument!
    generators = []
    rad = 20
    for y in range(pixel_array.surface.get_height()):
      for x in range(pixel_array.surface.get_width()):
        (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
        if (r,g,b) == (255,128,64):
          if random.randint(1,3) == 1:
            generators.append(RisingZombieGenerator(self, (x,y), super_frequency))
          else:
            generators.append(ZombieGenerator(self, (x,y), rad, super_frequency))
    return generators

  def pixel_array_to_battle_generators(self, pixel_array, radius,
    max_zombies, max_superzombies, max_bandits, max_wizards, max_total):
    #having to use all those as arguments instead of getting them from the level (or game?) is not optimal
    generators = []
    for y in range(pixel_array.surface.get_height()):
      for x in range(pixel_array.surface.get_width()):
        (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
        if (r,g,b) == (255,128,64):
          generators.append(InfiniteZombieGenerator(self, (x,y), radius,
            max_zombies, max_superzombies, max_bandits, max_wizards, max_total))
    return generators

  def pixel_array_to_bandit_generators(self, pixel_array, super_frequency):
    # important: uses the same color as zombie generators, using existing zombie placement
    generators = []
    for y in range(pixel_array.surface.get_height()):
      for x in range(pixel_array.surface.get_width()):
        (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
        if (r,g,b) == (255,128,64):
          generators.append(BanditGenerator(self, (x,y), 20, super_frequency))
    return generators
    
  def pixel_array_to_infinite_bandit_generators(self, pixel_array, super_frequency):
    generators = []
    for y in range(pixel_array.surface.get_height()):
      for x in range(pixel_array.surface.get_width()):
        (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
        if (r,g,b) == (255,128,64):
          generators.append(InfiniteBanditGenerator(self, (x,y), super_frequency, 6, 0.008))
    return generators

  def pixel_array_to_soldier_generators(self, pixel_array):
    # important: uses the same color as zombie generators, using existing zombie placement
    generators = []
    for y in range(pixel_array.surface.get_height()):
      for x in range(pixel_array.surface.get_width()):
        (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
        if (r,g,b) == (255,128,64):
          generators.append(SoldierGenerator(self, (x,y), 20))
    return generators
    
  def pixel_array_to_peasants(self, pixel_array):
    # radius should be an argument!
    units = []
    for y in range(pixel_array.surface.get_height()):
      for x in range(pixel_array.surface.get_width()):
        (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
        if (r,g,b) == (128,0,255):
          first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
          last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
          name = first_name+" "+last_name
          units.append(RockThrowingPeasant(self, name, (x,y), None))
    return units
    
  def wall_box(self, x1, y1, x2, y2, textures, height_offset = 0):
    """ empty in the middle """
    walls = []
    for z in range(0, height_offset+1):
      for y in range(y1, y2+1):
        for x in range(x1, x2+1):
          if (x == x1) or (x == x2) or (y == y1) or (y == y2):
            texture = random.choice(textures)
            walls.append(Wall(self, x, y, texture, z))
    return walls
    
  def parapet_box(self, x1, y1, x2, y2, direction, height_offset = 0):
    """ empty in the middle """
    parapets = []
    for y in range(y1, y2+1):
      for x in range(x1, x2+1):
        if (x == x1) or (x == x2) or (y == y1) or (y == y2):
          parapets.append(Parapet(x, y, direction, "tga/parapet_12x24.tga", "tga/parapet_12x24b.tga", height_offset))
    return parapets
    
  def z_sort(self, obj_1, obj_2):
    z_1 = obj_1.get_z()
    z_2 = obj_2.get_z()
    if z_1 > z_2: return 1
    elif z_1 == z_2: return 0
    elif z_1 < z_2: return -1
    
  def insert_depth_tree_nodes(self):
    arr = self.objects + self.corpses + self.walls + self.crops + self.trees + self.counters \
        + self.roofs + self.gates + self.parapets + self.units + self.doors + self.darts \
        + self.healing_flashes + self.powerups + self.rock_piles
    for obj in arr:
      node = DepthTreeNode(obj)
      self.depth_tree.insert(node)
  
  def add_unit(self, unit):
    self.units.append(unit)
    self.depth_tree.insert(DepthTreeNode(unit))
    
  def remove_unit(self, unit):
    for unit in self.units:
      if unit.target_unit == unit:
        unit.target_unit = None
    self.units.remove(unit)
    self.depth_tree.remove(unit)