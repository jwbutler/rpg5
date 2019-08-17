from __future__ import division
import math
import sys
import os
import string
import glob

from functions import *
from classes import *
from equipment import *
from units import *
from enemy_humans import *
from npcs import *
from wizards import *
from zombies import *
from generators import *
from functions2 import *
import levels

class RPG:

  """
  ALL LEVELS
  """
  
  def load_level_filenames(self):
    self.level_filenames = []
    #self.level_filenames.append('tga/levels/level0a.tga') #zombie wizard playground
    #self.level_filenames.append('tga/levels/level0b.tga') #enemy humans
    self.level_filenames.append('tga/levels/level0c.tga') #escort
    for n in map(str, range(1,21)):
      self.level_filenames.append("tga/levels/" + n + ".tga")
  
  """
  def load_all_levels(self, levels):
    #only call this once
    #story mode only
    # IMO don't call this at all
    all_levels = []
    for filename in level_filenames:
      if os.path.exists(filename):
        all_levels.append(levels.LevelFromFile(self, filename))
      else:
        pass#print filename + ": file not found"
    return all_levels
  """
  """
  LOAD LEVEL
  """ 
  
  def load_level(self, levels):
    #pygame.event.clear(pygame.USEREVENT)
    pygame.time.set_timer(pygame.USEREVENT, 0)
    pygame.time.set_timer(pygame.USEREVENT+1, 0)    
    self.paused = True
    filename = self.level_filenames[self.level_index]
    level = levels.LevelFromFile(self, filename)
    for unit in self.units:
      (unit.target_x, unit.target_y, unit.target_unit) = (None, None, None)
      (unit.dx, unit.dy) = (dir_to_coords(random.choice(self.directions)))
    level.load_level_data(self)
    for key in level.__dict__.keys():
      self.__dict__[key] = level.__dict__[key]
    self.check_victory = level.check_victory
    self.check_defeat = level.check_defeat
    for menu in self.menus:
      menu.refresh(self)
    self.text_lines = [level.filename.split("/")[-1]]
    self.text_ticks = 0
    self.paused = False
    self.ticks = 0
    if self.battle_mode: #True or battle2
      self.streak = 0
      self.streak_ticks = 0
    pygame.time.set_timer(pygame.USEREVENT, int(1000/self.fps)) #Frame timer
    pygame.time.set_timer(pygame.USEREVENT+1, int(1000/self.tps)) #Tick timer
    self.center_camera()
    self.floor.draw(self)
  
  # # # # #
  # INIT  #
  # # # # #
    
  def __init__(self, battle_mode=False, time_remaining=0):
    self.directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    self.keyName = None
    self.keyMods = None
    self.list_keys = [] #unused?
    self.walls = []
    self.parapets = []
    self.trees = []
    self.objects = [] #mostly rocks
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
    self.fps = 12 #Starting it high just for fun; no reason to go over 12
    self.tps = 12
    self.ticks = 0
    self.score = 0
    self.kills = 0
    self.vision_radius = 15
    self.list_dir_keys = [pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9]
    self.list_dir_names = [pygame.key.name(x) for x in self.list_dir_keys]
    self.main_menu = MainMenu('tga/menu.tga', pygame.Rect(0, 360, 640, 120), True)
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
      menu.refresh(self)
    self.fullscreen = True
    for arg in sys.argv:
      if arg in ['-w', '-windowed', '-window', '--w', '--windowed', '--window']:
        self.fullscreen = False
    if self.fullscreen:
      self.screenbig = pygame.display.set_mode((640,480), pygame.FULLSCREEN)
    else:
      self.screenbig = pygame.display.set_mode((640,480))
    self.screen = pygame.surface.Surface((320,240))
    self.floor_layer = pygame.surface.Surface((320,240))
    self.object_layer = pygame.surface.Surface((320,240))
    pygame.display.set_caption("Warpath")
        
    self.level_index = 0
    self.battle_mode = battle_mode
    if battle_mode: #True or 'battle2'
      self.time_remaining = time_remaining
        
# # # # # # # # # #
# KEYBOARD INPUT  #
# # # # # # # # # #

  def keyboard_input(self):
    #dialog

    if self.keyName == 'return':
      if self.show_dialog:
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
                unit.end_dialog(self)
              else:
                unit.target_unit = None
                unit.reset(self)  
        else:
          self.dialog_box = self.draw_dialog(self.dialog_boxes[self.dialog_index])
          self.dialog_ticks = int(len(self.dialog_boxes[self.dialog_index])/2)
          
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
    if self.keyName in [str(x) for x in xrange(0,10)]:
      k = int(self.keyName)
      if k == 0:
        k = 9
      else:
        k = k-1
      player_units = []
      for unit in self.units:
        if unit.playable:
          player_units.append(unit)        
      if k > (len(player_units)-1):
        return False
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
        # ctrl + # to add to current selection
        for unit in player_units:
          if self.keyMods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL):
            pass
          else:
            unit.selected = False
        unit = player_units[k]
        if keymods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL):
          unit.selected = not unit.selected
        else:                  
          unit.selected = True
    #select all
    elif self.keyName == 'a' and (self.keyMods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL)):
      for unit in self.units:
        if unit.playable:
          unit.selected = True
    # quit
    elif self.keyName == 'escape':
      print 'Key pressed: ESC'
      print "Time:", self.ticks/self.tps, "s"
      sys.exit(0)
    # pause
    elif self.keyName in ['p', 'space']:
      if not self.show_dialog:
        self.show_buysell_screen = self.scrolling_text_active = False
        self.paused = not self.paused
        if self.sound_paused:
          pygame.mixer.unpause()
        else:
          pygame.mixer.pause()
        self.sound_paused = not self.sound_paused

    elif self.keyName == 'w' and (self.keyMods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL)):
      skip_again = True
      while skip_again:
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
    elif self.keyName == 's' and (self.keyMods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL)):        
      self.score += 100
    elif self.keyName == 'm' and (self.keyMods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL)):
      if self.music_paused:
        pygame.mixer.music.unpause()
      else:
        pygame.mixer.music.pause()
      self.sound_music = not self.music_paused
      #music = pygame.mixer.Sound(random.choice(self.music_filenames))
      #music.play()
    elif self.keyName == 'tab' and (self.keyMods & (pygame.KMOD_LALT | pygame.KMOD_RALT)):
      if pygame.display.get_active():
        pygame.display.iconify()
    elif self.keyName == 'return' and (self.keyMods & (pygame.KMOD_LALT | pygame.KMOD_RALT)):
      self.fullscreen = not self.fullscreen
      screen_buffer = self.screenbig.copy()
      if self.fullscreen:
        self.screenbig = pygame.display.set_mode((640,480), pygame.FULLSCREEN)
      else:
        self.screenbig = pygame.display.set_mode((640,480))
      self.screenbig.blit(screen_buffer, (0,0))
    # center the camera
    elif self.keyName == 'backspace':
      self.center_camera()

# # # # # # # #
# MOUSE INPUT #
# # # # # # # #

  def mouse_input(self, event):
    real_posn = pygame.mouse.get_pos()              # for interacting with 640x480-based menus
    posn = int(real_posn[0]/2), int(real_posn[1]/2) # but most of the game is pseudo-320x240
    if event.type == pygame.MOUSEBUTTONDOWN:
      # # # # # # # # # # # # # # # # # # # # # # 
      # LEFT MOUSEDOWN HANDLER (selection rect) #
      # # # # # # # # # # # # # # # # # # # # # #
      if event.button == 1:
        player_units = []
        for unit in self.units:
          if unit.playable:
            player_units.append(unit)
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
              selected_unit = player_units[self.main_menu.cards.index(card)]
              for unit in player_units:
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
        grid_posn = pixel_to_grid_improved(self, *posn)
        if grid_posn:
          (x,y) = grid_posn
          do_right_click_stuff = False #damn is this ghetto
          if obstacle_unit(self, (x,y)):
            do_right_click_stuff = True
          elif obstacle(self, (x,y)) and not obstacle_unit(self, (x,y)):
            #interact with objects?
            pass
          else:
            do_right_click_stuff = True
            for pointer in self.pointers:
              if (pointer.x,pointer.y) == (x,y):
                unit = pointer.return_unit(self)
                (x,y) = (unit.x,unit.y)
          if do_right_click_stuff:
            for unit in self.units:
              if unit.selected and unit.current_activity not in ['falling', 'decapitated']:
                unit.target_unit = None
                for unit_2 in self.units:
                  if ((unit_2.x, unit_2.y) == (x,y)):
                    if (unit_2.hostile):
                      unit.target_unit = unit_2.name
                      (unit.target_x, unit.target_y) = (None, None)
                      keymods = pygame.key.get_mods()
                      if unit.has_special and keymods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL) and unit.special_ticks == unit.max_special_ticks:
                        unit.move_to_target_unit_special(self)
                      elif unit.has_secondary_special and keymods & (pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT) and unit.special_ticks == unit.max_special_ticks:
                        unit.move_to_target_unit_special(self, True)
                      else:
                        unit.move_to_target_unit(self)
                    else:
                      if not unit_2.playable:
                        if not unit_2.ally:
                          unit.target_unit = unit_2.name
                          (unit.target_x, unit.target_y) = (None, None)
                          unit.move_to_target_unit(self) #do we need a new function?
                if unit.target_unit == None:
                  (unit.target_x, unit.target_y) = (x,y)
                  if unit.current_activity == 'standing':
                    unit.move_to_target_posn(self)
            

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
          grid_posn = pixel_to_grid_improved(self, *posn)
          for unit in self.units:
            if unit.playable:
              overlap_rect = unit.get_rect(self).clip(self.drag_rect)
              overlap_area = overlap_rect.width * overlap_rect.height
              drag_area = (self.drag_rect.width * self.drag_rect.height)
              if drag_area == 0: #I.E. single click, not drag
                if grid_posn:
                  (x,y) = grid_posn
                  if (unit.x, unit.y) == (x,y):
                    if keymods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL):
                      unit.selected = not unit.selected
                    else:
                      unit.selected = True
                  else:
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
      unit.do_events(self)
      for tile in self.fire_tiles:
        if (unit.x,unit.y) == (tile.x,tile.y):
          unit.take_damage(self, tile.damage, True)
          break
      # Passive health regen

      if unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
        if (self.ticks % self.tps) == 0:
          if (unit.current_hp + 1) <= unit.max_hp:
            unit.current_hp += 1

      if unit.playable:
        for powerup in self.powerups:
          if (unit.x, unit.y) == (powerup.x, powerup.y):
            if unit.current_hp < unit.max_hp:
              powerup.proc(self, unit)
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
      generator.do_events(self)
    for dart in self.darts:
      dart.do_events(self)
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
    
# # # # #
# DRAW  #
# # # # #
 
  def draw(self):
    ticks_1 = pygame.time.get_ticks()
    self.screen.fill((0,0,0))
    if self.redraw_floor:
      self.floor.draw(self)
      self.redraw_floor = False
    self.screen.blit(self.floor_layer, (0,0))
    ticks_2 = pygame.time.get_ticks()
    for tile in self.water_tiles + self.fire_tiles:
      for unit in self.units:
        if unit.playable:
          if distance((tile.x,tile.y),(unit.x,unit.y)) <= self.vision_radius:
            rect = tile.get_current_frame().get_rect()
            (rect.left, rect.top) = (tile.x,tile.y)
            if rect.colliderect(pygame.Rect((0,0,320,240))):              
              tile.draw(self)
              break
    ticks_2a = pygame.time.get_ticks()
    for blood in self.blood:
      for unit in self.units:
        if unit.playable:
          if distance((blood.x,blood.y),(unit.x,unit.y)) <= self.vision_radius:
            blood.draw(self)
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
    mouse_posn = int(pygame.mouse.get_pos()[0]/2), int(pygame.mouse.get_pos()[1]/2)
    grid_posn = pixel_to_grid_improved(self, *mouse_posn)
    if grid_posn:
      self.target_tile_white.set_alpha(192)
      self.screen.blit(self.target_tile_white, grid_to_pixel(self, *grid_posn))
      self.target_tile_white.set_alpha(255)
    for unit in self.units:
      self.draw_unit_tile(unit)

    ticks_3 = pygame.time.get_ticks()    
    for door in self.doors:
      door.show_open_icon = False
      squares = door.list_open_squares()
      for unit in self.units:
        if (unit.x, unit.y) in squares:
          door.show_open_icon = True
          break
    arr = self.objects + self.corpses + self.walls + self.crops + self.trees + self.counters \
        + self.roofs + self.gates + self.parapets + self.units + self.doors + self.darts \
        + self.healing_flashes + self.powerups + self.rock_piles

    """
    print "SORT:", len(arr), '//', len(self.objects), len(self.corpses), len(self.walls), len(self.crops), \
          len(self.trees), len(self.counters), len(self.roofs), len(self.gates), len(self.parapets), len(self.units), \
          len(self.doors), len(self.darts), len(self.healing_flashes)
    """
    
    arr.sort(z_sort)
    ticks_4 = pygame.time.get_ticks()
    screen_rect = pygame.Rect((0,0,320,240))
    for obj in arr:
      if obj.get_rect(self).colliderect(screen_rect):
        for unit in self.units:
          if unit.playable:
            if distance((obj.x,obj.y),(unit.x,unit.y)) <= self.vision_radius:
              obj.draw(self)
              break
    ticks_5 = pygame.time.get_ticks()
    if self.drag_rect:
      pygame.draw.rect(self.screen, (0,255,0), self.drag_rect, 2)
      if self.drag_rect_locked == True:
        self.drag_rect = False
        self.drag_rect_locked = False
        (self.drag_x1, self.drag_y1, self.drag_x2, self.drag_y2) = (None, None, None, None)
    for n in range(len(self.text_lines)): #status text, like level load messages
      draw_text(self.text_lines[n], self.screen, (1, 1+13*n), 12)
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
      self.screen.blit(surface, (320 - surface.get_width(), 1+13*n))
    pygame.transform.scale(self.screen, (640,480), self.screenbig)
    ticks_5a = pygame.time.get_ticks()
    for menu in self.menus:
      #if menu.visible:
      menu.refresh(self)
      self.screenbig.blit(menu.surface, menu.rect)
    ticks_6 = pygame.time.get_ticks()
    
    #Debug text
    

    font = pygame.font.SysFont("Arial", 12)
    txt = "fps: " + str(self.fps) + " draw:" + str(ticks_6 - ticks_1)
    surface = font.render(txt, False, (0,255,0))
    self.screenbig.blit(surface, (0, 0))

    """
    print "draw:", ticks_6 - ticks_1
    print "floor:", ticks_2 - ticks_1,
    print "fire/water:", ticks_2a - ticks_2,
    print "blood:", ticks_2b - ticks_2a,
    print "tiles:", ticks_3 - ticks_2b,
    print "sort:", ticks_4 - ticks_3,
    print "objects:", ticks_5 - ticks_4,
    print "text:", ticks_5a - ticks_5,
    print "menu:", ticks_6 - ticks_5a
    """

    if (ticks_6 - ticks_1) > (1000/self.fps):
      self.fps -= 1
      pygame.time.set_timer(pygame.USEREVENT, int(1000/self.fps))
    elif (ticks_6 - ticks_1) < (750/self.fps):
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
    posn = int(pygame.mouse.get_pos()[0]/2), int(pygame.mouse.get_pos()[1]/2)
    (old_x,old_y) = (self.camera.x,self.camera.y)
    if posn[0] < 10:
      self.camera.x -= 1
      self.camera.y += 1
    elif posn[0] > 310:
      self.camera.x += 1
      self.camera.y -= 1
    if posn[1] < 10:
      self.camera.x -= 1
      self.camera.y -= 1
    elif posn[1] > 230:
      self.camera.x += 1
      self.camera.y += 1
    if not(self.camera.get_rect().colliderect(self.floor.rect)):
      (self.camera.x, self.camera.y) = (old_x, old_y)
      
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
          pygame.transform.scale(self.screen, (640,480), self.screenbig)
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
          pygame.transform.scale(self.screen, (640,480), self.screenbig)
          pygame.display.flip()
          if self.dialog_ticks == 0:
            if self.dialog_index >= len(self.dialog_boxes):
              pass
            else:
              self.dialog_box = self.draw_dialog(self.dialog_boxes[self.dialog_index])
              self.dialog_ticks = int(len(self.dialog_boxes[self.dialog_index])/2)
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
          y = self.scrolling_text_y
          for surface in self.line_surfaces:
            y += surface.get_height()
            x = (320-surface.get_width())/2
            rect = self.screen.blit(surface,(x,y))
          pygame.transform.scale(self.screen, (640,480), self.screenbig)
          pygame.display.flip()
        elif self.show_buysell_screen:
          self.draw_buysell_screen()
          pygame.transform.scale(self.screen, (640,480), self.screenbig)
          pygame.display.flip()
        elif self.paused == False:
          if self.check_victory(self):
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
          elif self.check_defeat(self):
            self.death_screen_active = True
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
          draw_text('Game paused.  Press P to continue', self.screenbig, (5, 5))
          draw_text(str(round(self.ticks/self.tps,1)) + " s", self.screenbig, (5, 15))
          draw_text("Kills: " + str(self.kills), self.screenbig, (5, 25))
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
                    unit.end_dialog(self)
                  else:
                    unit.target_unit = None
                    unit.reset(self)
                target = self.unit_by_name(unit.target_unit)
                if not target:
                  unit.reset(self)                
                elif (not target.playable) and (not target.hostile) and (not target.ally):
                  unit.reset(self)
        elif self.paused:
          self.update_camera()
          for menu in self.menus:
            if menu.visible:
              menu.refresh(self)
          if self.battle_mode == True: #not battle2
            if self.time_remaining > 0:
              self.time_remaining -= 1 #new addition, for anti-pausing

        elif not self.paused:
          self.do_upkeep() # ticks, mana regen, EVENTS!, etc
          if self.scrolling_text_active:
            self.scrolling_text_y -= 3
            if y + surface.get_height() < 0:
              self.scrolling_text_active = False
              if len(self.all_levels) > self.level_index + 1:
                self.level_index += 1
                self.load_level(levels)
                self.ticks = 0
              else:
                print "YOU WIN"
                print self.ticks/self.tps, "s"
                quit()
      else: #includes KeyUp and ActiveEvent
        pass #event is removed from queue
  # Additional functions:

  def draw_black(self, obj, source, (x,y)):
    min_distance = self.floor.rect.width * self.floor.rect.height #upper bound...
    for unit in self.units:
      if unit.playable:
        dist = distance((unit.x, unit.y), (obj.x, obj.y))
        if dist < min_distance:
          min_distance = dist
    alpha = 255 - distance_to_alpha(min_distance)
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
    black_alpha = 255 - distance_to_alpha(min_distance)
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
      x = (320 - w)/2
      self.screen.blit(score_text, (x,188))
    pygame.transform.scale(self.screen, (640,480), self.screenbig)
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
        player_units.append(unit.name)
    for n in range(len(player_units)):
      x = 27*n + 4
      y = 203
      unit = self.unit_by_name(player_units[n])
      unit.draw_in_place(self, (x,y))
      if unit.selected_in_menu:
        #write unit's name
        draw_text(unit.name, self.screen, (8, 8))
        #write unit's stats
        #inelegant.  Make a draw_tooltip function for basicunit
        draw_text("Level: " + str(unit.level), self.screen, (8,28))              
        draw_text("Strength: " + str(unit.strength), self.screen, (8,38))
        draw_text("Health: " + str(unit.max_hp), self.screen, (8,48))
        if hasattr(unit, 'heal_amount'): 
          draw_text("Heal amount: " + str(unit.heal_amount), self.screen, (8,58))
        rect = pygame.Rect((x-1,y-1,26,35))
        pygame.draw.rect(self.screen, (255,255,255), rect, 1)
        #draw equipment
        x1 = 187
        x2 = 213
        y = 22
        for equip in unit.equipment:
          if equip.icon:
            self.screen.blit(equip.icon, (x1,y))
            draw_text(equip.name, self.screen, (x2, y))
            if equip.selected_in_menu:
              self.screen.blit(equip.draw_tooltip(), (188,200))
            y += 27
            
  def draw_buysell_screen(self):
    self.screen.blit(self.buysell_screen, (0,0))
    player_units = []
    for unit in self.units:
      if unit.playable and not unit.hostile: #redundant...
        player_units.append(unit.name)
    
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
      unit = self.unit_by_name(player_units[n])
      unit.draw_in_place(self, (x,y))
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
            draw_text(equip.name, self.screen, (x2, y))
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
    
  def draw_line_surfaces(self, str, width=320):
    """ Lines of dialog, that is. """
    words = str.split()
    line_surfaces = []
    font = pygame.font.SysFont("Arial", 12)
    lines = []
    line_index = 0
    lines.append("")
    for word in words:
      new_line = string.join([lines[line_index], word])
      surface = font.render(new_line, False, (255,255,255))
      if surface.get_width() > width:
        line_index += 1
        lines.append(word)
        continue
      else:
        lines[line_index] = new_line
    for line in lines:
      line_surface = font.render(line, False, (255,255,255))
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
            if distance((friendly_unit.x,friendly_unit.y), (unit.x,unit.y)) <= self.vision_radius:
              in_range = True
          if friendly_unit.target_unit == unit.name:
            targeted = True
      if in_range:
        if targeted:
          self.screen.blit(self.target_tile_lightred, grid_to_pixel(self, unit.x, unit.y))
        else:
          self.screen.blit(self.target_tile_darkred, grid_to_pixel(self, unit.x, unit.y))
    elif unit.playable:
      if unit.selected:
        self.screen.blit(self.selected_tile, grid_to_pixel(self, unit.x, unit.y))
      else:    
        self.screen.blit(self.target_tile_green, grid_to_pixel(self, unit.x, unit.y))
      if (unit.target_x, unit.target_y) != (None, None):
        self.screen.blit(self.target_tile_white, grid_to_pixel(self, unit.target_x, unit.target_y))
    elif unit.ally:
      self.screen.blit(self.target_tile_cyan, grid_to_pixel(self, unit.x, unit.y))
    else: #NPCs
      for unit_2 in self.units:
        if unit_2.playable:
          if unit_2.target_unit == unit.name:
            self.screen.blit(self.target_tile_lightblue, grid_to_pixel(self, unit.x, unit.y))
      else:
        self.screen.blit(self.target_tile_blue, grid_to_pixel(self, unit.x, unit.y))
        
  def disable_buysell_screen(self):
    self.show_buysell_screen = False
    self.items_for_sale = buy_button = self.done_button = self.buy_button_disabled = None
    for unit in self.units:
      unit.selected_in_menu = False
      if unit.playable:
        unit.target_unit = None
        unit.reset(self)
  
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
        total_x += unit.x; total_y += unit.y; num_units += 1
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
        if obstacle(self, (x,y)) and not obstacle_unit(self, (x,y)):
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
        if obstacle(self, (x,y)) and not obstacle_unit(self, (x,y)):
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
