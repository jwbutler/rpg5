from __future__ import division
import pygame
import random
import math
import os
from functions import *
from classes import *

class Armor:
  """ body armor """
  def __init__(self, game, name, anim_name, palette_swaps = {}):
      self.name = name
      self.anim_name = anim_name
      self.slot = "chest"
      self.palette_swaps = palette_swaps
      try:
        self.icon = pygame.image.load('tga/' + anim_name.split("_female")[0] + '_icon.tga')
      except: #ugh
        self.icon = pygame.image.load("tga/sword_icon.tga")

      try:
        self.icon_small = pygame.image.load('tga/' + anim_name + '_icon_small.tga')
      except: #ugh
        self.icon_small = pygame.image.load("tga/sword_icon.tga")
      self.icon = palette_swap_multi(self.icon, self.palette_swaps)
      self.icon_small = palette_swap_multi(self.icon_small, self.palette_swaps)
      self.animations = []
      self.current_animation = None
      self.activities = ['standing', 'walking', 'attacking', 'healing', 'bashing', 'casting', 'slashing',
      'falling', 'dead', 'stunned', 'decapitated', 'dead_decapitated', 'shooting', 'charging', 'taunting']
      self.current_activity = None
      self.load_animations(game, self.palette_swaps)
      self.selected_in_menu = False

  def set_animation(self, game, activity, directions):
    self.current_activity = activity
    for anim in self.animations:
      if anim.activity == activity and anim.directions == directions:
        self.current_animation = anim
        self.current_animation.findex = 1
        source = self.get_current_frame()
        self.x_offset = (40 - source.get_width())/2
        self.y_offset = 40 - source.get_height()

  def get_current_frame(self):
      """ Retrieve the current animation frame. """
      return self.current_animation.get_current_frame()
      
  def draw(self, game, x, y):
    source = self.get_current_frame()
    if source:
      source.set_colorkey((255,255,255)) #maybe unnecessary
      game.screen.blit(source, (x, y))
        
  def draw_tooltip(self):
    lines = [self.name]
    line_surfaces = []
    font = pygame.font.SysFont("Arial", 10)
    height = 0
    max_width = 0
    for line in lines:
      line_surface = font.render(line, False, (190,243,255,0))
      line_surfaces.append(line_surface)
      height += line_surface.get_height()
      if line_surface.get_width() > max_width:
        max_width = line_surface.get_width()
    surface = pygame.surface.Surface((max_width, height))
    surface.set_colorkey((0,0,0))
    y = 0
    for s in line_surfaces:
      surface.blit(s, (0,y))
      y += s.get_height()
    return surface
    
  def load_animations(self, game, palette_swaps = {}):
    frames_surfaces = {}
    for activity in self.activities:
      for dir in game.directions:
        frames = []
        frame_surfaces = []
        if activity == 'walking':
          # two frames
          for n in [1,1,2,2]:
            frames.append('tga/' + self.anim_name + '_walking_' + dir + '_' + str(n) + '.tga')
        elif activity == 'standing':
          for n in range(4):
            frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'attacking':
          for x in [1,1,2,2,1,1]:
            frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_' + str(x) + '.tga')
          frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
          frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'taunting':
          frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_1.tga')
          frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_1.tga')
          frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
          frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'charging':
          for n in range(10):
            frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_2.tga')
        elif activity == 'shooting':
          for x in ['1','1','2b','2b','2b','2b','1','1']:
            frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_' + x + '.tga')
          for n in range(8):
            frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'bashing':
          for x in ['1','1','2b','2b','1','1']:
            frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_' + x + '.tga')
          frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
          frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'slashing':
          frames = []
          frame_surfaces = []
          dir_2 = rccw(dir)
          frames.append('tga/' + self.anim_name + '_attacking_' + dir_2 + '_1.tga')
          for n in range(8):
            dir_2 = rcw(dir_2)
            frames.append('tga/' + self.anim_name + '_attacking_' + dir_2 + '_2.tga')
          frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_1.tga')
        elif activity == 'falling':
          """
          Supports several different sequences of falling frames.  These are as follows:
          Cloak: four frames, three directions
          Club: two frames, one direction
          Crown: four frames, one direction
          Hairpiece: four frames, three directions
          Hats: four frames, one direction
          Helms: four frames, three directions
          Helms (female): three frames, one direction
          Mail: four frames, three directions
          Shield(2): four frames, three directions, w/ "_B"
          Shield3: four frames, one direction
          Spear: three frames, one direction
          """
          if dir in ['S', 'SW', 'W']:
            anim_dir = 'S'
          elif dir in ['NW', 'SE']:
            anim_dir = 'NW'
          elif dir in ['N', 'NE', 'E']:
            anim_dir = 'NE'
          if os.path.exists('tga/' + self.anim_name + '_falling_' + anim_dir + '_1.tga') \
          or os.path.exists('tga/' + self.anim_name + '_falling_' + anim_dir + '_1_B.tga'):
            for x in [1,2,3,4]:
              for n in range(2):
                if os.path.exists('tga/' + self.anim_name + '_falling_' + anim_dir + '_' + str(x) + '_B.tga'):
                  frames.append('tga/' + self.anim_name + '_falling_' + anim_dir + '_' + str(x) + '_B.tga')
                elif os.path.exists('tga/' + self.anim_name + '_falling_' + anim_dir + '_' + str(x) + '.tga'):
                  frames.append('tga/' + self.anim_name + '_falling_' + anim_dir + '_' + str(x) + '.tga')
          elif os.path.exists('tga/' + self.anim_name + '_falling_4.tga'):
            for x in [1,2,3,4]:
              for n in range(2):
                frames.append('tga/' + self.anim_name + '_falling_'+str(x)+'.tga')
          elif os.path.exists('tga/' + self.anim_name + '_falling_3.tga'):
            for x in [1,2,3,3]:
              for n in range(2):
                frames.append('tga/' + self.anim_name + '_falling_'+str(x)+'.tga')
          elif os.path.exists('tga/' + self.anim_name + '_falling_2.tga'):
            for x in [1,2]:
              for n in range(4):
                frames.append('tga/' + self.anim_name + '_falling_'+str(x)+'.tga')
          else:
            #No animation drawn; use default standing anim
            for x in range(8):
              frames.append('tga/' + self.anim_name + '_standing_SE_1.tga')
        elif activity == 'stunned':
          anim_directions = get_slash_directions(game, dir)
          for d in anim_directions:
            for n in range(2):
              if os.path.exists('tga/' + self.anim_name + '_standing_' + d + '_1_B.tga'):
                frame = 'tga/' + self.anim_name + '_standing_' + d + '_1_B.tga'
              elif os.path.exists('tga/' + self.anim_name + '_standing_' + d + '_1.tga'):
                frame = 'tga/' + self.anim_name + '_standing_' + d + '_1.tga'
              frames.append(frame)
        elif activity == 'dead':
          if dir in ['S', 'SW', 'W']:
            anim_dir = 'S'
          elif dir in ['NW', 'SE']:
            anim_dir = 'NW'
          elif dir in ['N', 'NE', 'E']:
            anim_dir = 'NE'
          if os.path.exists('tga/' + self.anim_name + '_falling_' + anim_dir + '_4_B.tga'):
            frames.append('tga/' + self.anim_name + '_falling_' + anim_dir + '_4_B.tga')
          elif os.path.exists('tga/' + self.anim_name + '_falling_' + anim_dir + '_4.tga'):
            frames.append('tga/' + self.anim_name + '_falling_' + anim_dir + '_4.tga')
          elif os.path.exists('tga/' + self.anim_name + '_falling_4.tga'):
            frames.append('tga/' + self.anim_name + '_falling_4.tga')
          elif os.path.exists('tga/' + self.anim_name + '_falling_3.tga'):
            frames.append('tga/' + self.anim_name + '_falling_3.tga')
          elif os.path.exists('tga/' + self.anim_name + '_falling_2.tga'):
            frames.append('tga/' + self.anim_name + '_falling_2.tga')
          else:
            #No animation drawn; use default standing anim
            frames.append('tga/' + self.anim_name + '_standing_SE_1.tga')
        elif activity == 'decapitated':
          if dir in ['S', 'SW', 'W']:
            anim_dir = 'S'
          elif dir in ['NW', 'SE']:
            anim_dir = 'NW'
          elif dir in ['N', 'NE', 'E']:
            anim_dir = 'NE'
          if os.path.exists('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_4.tga'):
            for x in range(1, 5):
              for n in range(2):
                frames.append('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_' + str(x) + '.tga')
          elif os.path.exists('tga/' + self.anim_name + '_falling_' + anim_dir + '_1.tga') \
          or os.path.exists('tga/' + self.anim_name + '_falling_' + anim_dir + '_1_B.tga'):
            for x in range(1, 5):
              for n in range(2):
                if os.path.exists('tga/' + self.anim_name + '_falling_' + anim_dir + '_' + str(x) + '_B.tga'):
                  frames.append('tga/' + self.anim_name + '_falling_' + anim_dir + '_' + str(x) + '_B.tga')
                elif os.path.exists('tga/' + self.anim_name + '_falling_' + anim_dir + '_' + str(x) + '.tga'):
                  frames.append('tga/' + self.anim_name + '_falling_' + anim_dir + '_' + str(x) + '.tga')
          elif os.path.exists('tga/' + self.anim_name + '_falling_4.tga'):
            for n in [1,1,2,2,3,3,4,4]:
              frames.append('tga/' + self.anim_name + '_falling_'+str(n)+'.tga')
          elif os.path.exists('tga/' + self.anim_name + '_falling_3.tga'):
            for n in [1,1,2,2,3,3,3,3]:
              frames.append('tga/' + self.anim_name + '_falling_'+str(n)+'.tga')
          elif os.path.exists('tga/' + self.anim_name + '_falling_2.tga'):
            for n in [1,1,1,1,2,2,2,2]:
              frames.append('tga/' + self.anim_name + '_falling_'+str(n)+'.tga')
        elif activity == 'dead_decapitated':
          if dir in ['S', 'SW', 'W']:
            anim_dir = 'S'
          elif dir in ['NW', 'SE']:
            anim_dir = 'NW'
          elif dir in ['N', 'NE', 'E']:
            anim_dir = 'NE'
          for n in range(2):
            if os.path.exists('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_4_B.tga'):
              frames.append('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_4_B.tga')
            elif os.path.exists('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_4.tga'):
              frames.append('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_4.tga')
            elif os.path.exists('tga/' + self.anim_name + '_falling_' + anim_dir + '_4.tga'):
              frames.append('tga/' + self.anim_name + '_falling_' + anim_dir + '_4.tga')
            elif os.path.exists('tga/' + self.anim_name + '_falling_4.tga'):
              frames.append('tga/' + self.anim_name + '_falling_4.tga')
            elif os.path.exists('tga/' + self.anim_name + '_falling_3.tga'):
              frames.append('tga/' + self.anim_name + '_falling_3.tga')
            elif os.path.exists('tga/' + self.anim_name + '_falling_2.tga'):
              frames.append('tga/' + self.anim_name + '_falling_2.tga')     
        elif activity == 'healing':
          frame_surfaces = []
          frames = []
          for x in range(1, 5):
            for n in range(2):  
              filename = 'tga/' + self.anim_name + '_standing_SE_1.tga'
            frames.append(filename)
        for frame in frames:
          if frame in frames_surfaces.keys():
            surface = frames_surfaces[frame].copy() #Not sure if copy() is necessary here
          else:
            surface = pygame.image.load(frame)
            surface = palette_swap_multi(surface, palette_swaps)
            surface.set_colorkey((255,255,255))
            surface.convert()
            frames_surfaces[frame] = surface
          frame_surfaces.append(surface)
        self.animations.append(Animation(activity, [dir], frame_surfaces, frames))

class Helm(Armor):
  def __init__(self, game, name, anim_name, palette_swaps = {}):
    Armor.__init__(self, game, name, anim_name, palette_swaps)
    self.slot = "head"
        
class Cloak(Armor):
  def __init__(self, game, name, anim_name, palette_swaps = {}):
    Armor.__init__(self, game, name, anim_name, palette_swaps)
    self.slot = "cloak"
    
class Hairpiece(Armor):
  #beards too
  #has no icons
  #doesn't use Armor.__init__ because it doesn't use icons
  def __init__(self, game, name, anim_name, palette_swaps = None):
    self.name = name
    self.anim_name = anim_name
    self.slot = "hair"
    self.icon = None
    self.icon_small = None
    self.animations = []
    self.current_animation = None
    self.activities = ['standing', 'walking', 'attacking', 'healing', 'bashing', 'casting', 'slashing', 'falling', 'dead', 'stunned', 'decapitated', 'dead_decapitated', 'shooting', 'charging']
    self.current_activity = None
    if palette_swaps:
      self.palette_swaps = palette_swaps #beards need to match hair
    else:
      hair_colors = [
                 (151,90,36), #medium brown
                 (208,81,23), #red/orange
                 (102,30,0), #dark brown
                 (55,34,16), #black
                 (206,168,52), #blonde
                 (199,150,113), #light brown
                 (189,173,162), #medium gray
                 (239,232,220), #light gray
                ]
      self.palette_swaps = {(0,0,0):random.choice(hair_colors)}
    self.load_animations(game, self.palette_swaps)
    self.selected_in_menu = False
    
class Beard(Hairpiece):
  def __init__(self, game, name, palette_swaps):
    Hairpiece.__init__(self, game, name, 'beard', palette_swaps)
    self.slot = 'beard'

class Shield(Armor):
  #doesn't use Armor.__init__ because at least one shield is missing _icon_small.tga
  def __init__(self, game, name, anim_name, palette_swaps = {}):
    self.name = name
    self.anim_name = anim_name
    self.slot = "shield"
    self.palette_swaps = palette_swaps
    self.icon = pygame.image.load('tga/' + anim_name + '_icon.tga')
    #self.icon_small = pygame.image.load('tga/' + anim_name + '_icon_small.tga')
    self.icon = palette_swap_multi(self.icon, self.palette_swaps)
    #self.icon_small = palette_swap_multi(self.icon_small, self.palette_swaps)
    self.animations = []
    self.current_animation = None
    self.activities = ['standing', 'walking', 'attacking', 'bashing', 'slashing', 'falling', 'dead', 'stunned', 'decapitated', 'dead_decapitated', 'charging', 'taunting']
    self.current_activity = None
    self.load_animations(game, self.palette_swaps)
    self.selected_in_menu = False
        
  def load_animations(self, game, palette_swaps = {}):
    """
    Loads animations automatically, referring to strict naming conventions.
    Includes layer information for equipment.
    Why is this different from Armor?
    """
    anim_name = self.anim_name # later I'll go through and change all the below, but...
    frames_surfaces = {}
    for activity in self.activities:
      for dir in game.directions:
        frame_surfaces = []
        frames = []
        if activity == 'walking':
          # two frames          
          for x in ['walking_' + dir + '_1', 'walking_' + dir + '_2']:
            for n in range(2):
              if os.path.exists('tga/' + anim_name + '_' + x + '_B.tga'):
                frames.append('tga/' + anim_name + '_' + x + '_B.tga')
              elif os.path.exists('tga/' + anim_name + '_' + x + '.tga'):
                frames.append('tga/' + anim_name + '_' + x + '.tga')
                
        if activity == 'standing':
          # one, doubled frame
          # some are called B for behind
          x = 'standing_' + dir + '_1'
          for n in range(4):
            if os.path.exists('tga/' + anim_name + '_' + x + '_B.tga'):
              frames.append('tga/' + anim_name + '_' + x + '_B.tga')
            elif os.path.exists('tga/' + anim_name + '_' + x + '.tga'):
              frames.append('tga/' + anim_name + '_' + x + '.tga')
              
        elif activity == 'attacking':
          for x in ['attacking_' + dir + '_1', 'attacking_' + dir + '_2',
                    'attacking_' + dir + '_1', 'standing_' + dir + '_1']:
            for n in range(2):
              if os.path.exists('tga/' + anim_name + '_' + x + '_B.tga'):
                frames.append('tga/' + anim_name + '_' + x + '_B.tga')
              elif os.path.exists('tga/' + anim_name + '_' + x + '.tga'):
                frames.append('tga/' + anim_name + '_' + x + '.tga')
        elif activity == 'taunting':
          for x in ['attacking_' + dir + '_1', 'standing_' + dir + '_1']:
            for n in range(2):
              if os.path.exists('tga/' + anim_name + '_' + x + '_B.tga'):
                frames.append('tga/' + anim_name + '_' + x + '_B.tga')
              elif os.path.exists('tga/' + anim_name + '_' + x + '.tga'):
                frames.append('tga/' + anim_name + '_' + x + '.tga')

        elif activity == 'charging':
          for n in range(10):
            if os.path.exists('tga/' + self.anim_name + '_attacking_' + dir + '_2_B.tga'):
              frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_2_B.tga')
            elif os.path.exists('tga/' + self.anim_name + '_attacking_' + dir + '_2.tga'):
              frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_2.tga')

        elif activity == 'falling':
          if self.anim_name != 'shield3':
            if dir in ['S', 'SW', 'W']:
              anim_dir = 'S'
            elif dir in ['NW', 'SE']:
              anim_dir = 'NW'
            elif dir in ['N', 'NE', 'E']:
              anim_dir = 'NE'
            for x in range(1, 5):
              for n in range(2):
                if os.path.exists('tga/' + anim_name + '_falling_' + anim_dir + '_' + str(x) + '_B.tga'):
                  frames.append('tga/' + anim_name + '_falling_' + anim_dir + '_' + str(x) + '_B.tga')
                elif os.path.exists('tga/' + anim_name + '_falling_' + anim_dir + '_' + str(x) + '.tga'):
                  frames.append('tga/' + anim_name + '_falling_' + anim_dir + '_' + str(x) + '.tga')
          else:
            for x in range(1, 5):
              for n in range(2):
                if os.path.exists('tga/' + anim_name + '_falling_' + str(x) + '_B.tga'):
                  frames.append('tga/' + anim_name + '_falling_' + str(x) + '_B.tga')
                elif os.path.exists('tga/' + anim_name + '_falling_' + str(x) + '.tga'):
                  frames.append('tga/' + anim_name + '_falling_' + str(x) + '.tga')              
        elif activity == 'decapitated':
          for x in [1,1,1,1,2,2,2,2]:
            frames.append('tga/' + anim_name + '_falling_'+str(x)+'.tga')
        elif activity in ['dead', 'dead_decapitated']:
          frames.append('tga/' + anim_name + '_falling_2.tga')
        elif activity == 'bashing':
          for x in ['attacking_' + dir + '_1', 'attacking_' + dir + '_2b',
                    'attacking_' + dir + '_1', 'standing_' + dir + '_1']:
            for n in range(2):
              if os.path.exists('tga/' + anim_name + '_' + x + '_B.tga'):
                frames.append('tga/' + anim_name + '_' + x + '_B.tga')
              elif os.path.exists('tga/' + anim_name + '_' + x + '.tga'):
                frames.append('tga/' + anim_name + '_' + x + '.tga')
        elif activity == 'slashing':
          frames = []
          frame_surfaces = []
          frame_names = []
          dir_2 = rccw(dir)
          frame_names.append('_attacking_' + dir_2 + '_1')
          for n in range(8):
            dir_2 = rcw(dir_2)
            frame_names.append('_attacking_' + dir_2 + '_2')
          frame_names.append('_attacking_' + dir + '_1')
          for x in frame_names:
            if os.path.exists('tga/'+self.anim_name+x+'_B.tga'):
              frames.append('tga/'+self.anim_name+x+'_B.tga')
            elif os.path.exists('tga/'+self.anim_name+x+'.tga'):
              frames.append('tga/'+self.anim_name+x+'.tga')
              
        elif activity == 'stunned':
          anim_directions = get_slash_directions(game, dir)
          for d in anim_directions:
            for n in range(2):
              if os.path.exists('tga/' + self.anim_name + '_standing_' + d + '_1_B.tga'):
                frame = 'tga/' + self.anim_name + '_standing_' + d + '_1_B.tga'              
              elif os.path.exists('tga/' + self.anim_name + '_standing_' + d + '_1.tga'):              
                frame = 'tga/' + self.anim_name + '_standing_' + d + '_1.tga'
              frames.append(frame)

        #No healing exception: healers will never have shields
        frame_surfaces = []
        #if frames == []:
        #  print activity, dir#pass #What's up with this?
        for frame in frames:
          if frame in frames_surfaces.keys():
            surface = frames_surfaces[frame].copy() #Not sure if copy() is necessary here
          else:
            surface = pygame.image.load(frame)
            surface = palette_swap_multi(surface, palette_swaps)
            surface.set_colorkey((255,255,255))
            surface.convert()
            frames_surfaces[frame] = surface
          frame_surfaces.append(surface)
        self.animations.append(Animation(activity, [dir], frame_surfaces, frames))
        
  def bash_damage(self):
    return 10

  def draw_tooltip(self):
    lines = [self.name]
    line_surfaces = []
    font = pygame.font.SysFont("Arial", 10)
    height = 0
    max_width = 0
    for line in lines:
      line_surface = font.render(line, False, (190,243,255,0))
      line_surfaces.append(line_surface)
      height += line_surface.get_height()
      if line_surface.get_width() > max_width:
        max_width = line_surface.get_width()
    surface = pygame.surface.Surface((max_width, height))
    surface.set_colorkey((0,0,0))
    y = 0
    for s in line_surfaces:
      surface.blit(s, (0,y))
      y += s.get_height()
    return surface
    
class TowerShield(Shield):
  def __init__(self, game):
    Shield.__init__(self, game, "Tower Shield", "shield3", {(255,255,0):(0,0,128)})
    
class Sword:
    """
    Contains information for equippable swords.  Speed is in seconds.
    Doesn't inherit from BasicSprite because it needs custom animation code. (GOOD!)
    """
    def __init__(self, game, name, anim_name, palette_swaps):
      self.name = name
      self.anim_name = anim_name
      self.palette_swaps = palette_swaps
      self.icon = pygame.image.load('tga/' + anim_name.split("_female")[0] + '_icon.tga')
      self.icon_small = pygame.image.load('tga/' + anim_name.split("_female")[0] + '_icon_small.tga')
      self.icon = palette_swap_multi(self.icon, self.palette_swaps)
      self.icon_small = palette_swap_multi(self.icon_small, self.palette_swaps)
      self.slot = "weapon"
      self.animations = []
      self.current_animation = None
      self.activities = ['standing', 'walking', 'attacking', 'bashing', 'healing', 'dazed', 'falling', 'dead', 'decapitated', 'dead_decapitated', 'slashing']
      self.current_activity = None
      self.load_animations(game, self.palette_swaps)
      self.selected_in_menu = False

    def set_animation(self, game, activity, directions):
      for anim in self.animations:
        if anim.activity == activity and anim.directions == directions:
          self.current_activity = activity                
          self.current_animation = anim
          self.current_animation.findex = 1
          source = self.get_current_frame()
          #self.x_offset = (40 - source.get_width())/2
          #self.y_offset = 40 - source.get_height()

    def get_current_frame(self):
      """ Retrieve the current animation frame. """
      return self.current_animation.get_current_frame()

    def load_animations(self, game, palette_swaps = {}):
      frames_surfaces = {}
      for activity in self.activities:
        for dir in game.directions:
          frames = []
          frame_surfaces = []
          if activity == 'walking':
            # two frames
            for x in ['walking_'+dir+'_1','walking_'+dir+'_2']:
              for n in range(2):
                if os.path.exists('tga/'+self.anim_name+'_'+x+'_B.tga'):
                  frames.append('tga/'+self.anim_name+'_'+x+'_B.tga')                  
                elif os.path.exists('tga/'+self.anim_name+'_'+x+'.tga'):
                  frames.append('tga/'+self.anim_name+'_'+x+'.tga')
                  
          elif activity == 'standing':
            # one, doubled frame
            # some are called B for behind
            for n in range(2):
              x = "standing_"+dir+"_1"
              if os.path.exists('tga/'+self.anim_name+'_'+x+'_B.tga'):
                frames.append('tga/'+self.anim_name+'_'+x+'_B.tga')
                frames.append('tga/'+self.anim_name+'_'+x+'_B.tga')                  
              elif os.path.exists('tga/'+self.anim_name+'_'+x+'.tga'):
                frames.append('tga/'+self.anim_name+'_'+x+'.tga')
                frames.append('tga/'+self.anim_name+'_'+x+'.tga')
                
          elif activity == 'attacking':
            for x in ['attacking_'+dir+'_1','attacking_'+dir+'_2','attacking_'+dir+'_1','standing_'+dir+'_1']:
              for n in range(2):
                if os.path.exists('tga/'+self.anim_name+'_'+x+'_B.tga'):
                  frames.append('tga/'+self.anim_name+'_'+x+'_B.tga')
                elif os.path.exists('tga/'+self.anim_name+'_'+x+'.tga'):
                  frames.append('tga/'+self.anim_name+'_'+x+'.tga')
                  
          elif activity == 'charging':
            for n in range(10):
              if os.path.exists('tga/' + self.anim_name + '_attacking_' + dir + '_2_B.tga'):
                frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_2_B.tga')
              elif os.path.exists('tga/' + self.anim_name + '_attacking_' + dir + '_2.tga'):
                frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_2.tga')
                
          elif activity == 'bashing':
            for x in ['attacking_'+dir+'_1','attacking_'+dir+'_2b','attacking_'+dir+'_1','standing_'+dir+'_1']:
              for n in range(2):
                if os.path.exists('tga/'+self.anim_name+'_'+x+'_B.tga'):
                  frames.append('tga/'+self.anim_name+'_'+x+'_B.tga')
                elif os.path.exists('tga/'+self.anim_name+'_'+x+'.tga'):
                  frames.append('tga/'+self.anim_name+'_'+x+'.tga')
                  
          elif activity == 'slashing':
            frames = []
            frame_surfaces = []
            frame_names = []
            trails = []
            dir_2 = rccw(dir)
            frame_names.append('_attacking_' + dir_2 + '_1')
            trails.append(None)
            for n in range(8):
              dir_2 = rcw(dir_2)
              frame_names.append('_attacking_' + dir_2 + '_2')
              dir_3 = rccw(dir_2)
              trails.append("tga/trail_" + dir_3 + "_" + dir_2 + ".tga")
            frame_names.append('_attacking_' + dir + '_1')
            trails.append(None)
            for x in frame_names:
              if os.path.exists('tga/'+self.anim_name+x+'_B.tga'):
                frames.append('tga/'+self.anim_name+x+'_B.tga')
              elif os.path.exists('tga/'+self.anim_name+x+'.tga'):
                frames.append('tga/'+self.anim_name+x+'.tga')
            
            dir_2 = rccw(dir)
            for frame in frames:
              surface = pygame.image.load(frame)
              surface = palette_swap_multi(surface, palette_swaps)
              surface.set_colorkey((255,255,255))
              surface.convert()
              frames_surfaces[frame] = surface              
              #Add slash gfx
              trail_filename = trails.pop(0)
              if trail_filename:
                trail_surface = pygame.image.load(trail_filename)
                trail_surface.set_colorkey((255,255,255))
                trail_surface.set_alpha(128)
                surface.blit(trail_surface, (0,0))
              frame_surfaces.append(surface)
              dir_2 = rcw(dir_2)

            self.animations.append(Animation(activity, [dir], frame_surfaces, frames))
         
          elif activity in ['falling', 'decapitated']:
            if dir in ["NE", "E"]:
              anim_dir = "NE"
            elif dir in ["N", "NW", "W"]:
              anim_dir = "NW"
            elif dir in ["S", "SW", "SE"]:
              anim_dir = "S"
            if self.anim_name == 'sword_female':
              for x in [1,1,2,2,3,3,3,3]:
                frames.append('tga/'+self.anim_name+'_falling_'+str(x)+'.tga')
            elif self.anim_name == 'club':
              for x in range(8):
                if os.path.exists('tga/club_standing_' + dir + '_1_B.tga'):
                  frames.append('tga/club_standing_' + dir + '_1_B.tga')
                elif os.path.exists('tga/club_standing_' + dir + '_1.tga'):
                  frames.append('tga/club_standing_' + dir + '_1.tga')
                else:
                  print 'fuck'
                  return False
            else:
              for x in [1,2,3,4]:
                for n in range(2):
                  frames.append('tga/'+self.anim_name+'_falling_'+anim_dir+'_'+str(x)+'.tga')       

          elif activity in ['dead', 'dead_decapitated']:
            if dir in ["NE", "E"]:
              anim_dir = "NE"
            elif dir in ["N", "NW", "W"]:
              anim_dir = "NW"
            elif dir in ["S", "SW", "SE"]:
              anim_dir = "S"
            if self.anim_name == 'sword':
              frames.append('tga/'+self.anim_name+'_falling_'+anim_dir+'_4.tga')
            elif self.anim_name == 'club':
              if os.path.exists('tga/'+self.anim_name+'_standing_'+anim_dir+'_1_B.tga'):
                frames.append('tga/'+self.anim_name+'_standing_'+anim_dir+'_1_B.tga')                
              elif os.path.exists('tga/'+self.anim_name+'_standing_'+anim_dir+'_1.tga'):                
                frames.append('tga/'+self.anim_name+'_standing_'+anim_dir+'_1.tga')
            elif self.anim_name == 'sword_female':
              frames.append('tga/'+self.anim_name+'_falling_3.tga')
          elif activity == 'healing':
            for x in range(8):
              frames.append('tga/sword_tipdown_SE.tga')
            frame_surfaces = []
            for frame in frames:
              if frame in frames_surfaces.keys():
                surface = frames_surfaces[frame]#.copy() #Not sure if copy() is necessary here
              else:
                surface = pygame.image.load(frame)
                surface = palette_swap_multi(surface, palette_swaps)
                surface.set_colorkey((255,255,255))
                surface.convert()
                frames_surfaces[frame] = surface
              frame_surfaces.append(surface)
            self.animations.append(Animation(activity, [dir], frame_surfaces, frames))                            
          if activity not in ['healing', 'slashing']:
            frame_surfaces = []
            for frame in frames:
              if frame in frames_surfaces.keys():
                surface = frames_surfaces[frame]#.copy() #Not sure if copy() is necessary here
              else:
                surface = pygame.image.load(frame)
                surface = palette_swap_multi(surface, palette_swaps)
                surface.set_colorkey((255,255,255))
                surface.convert()
                frames_surfaces[frame] = surface
              frame_surfaces.append(surface)
            self.animations.append(Animation(activity, [dir], frame_surfaces, frames))
                
    def draw(self, game, x, y, black_alpha=0):
      source = self.get_current_frame()
      if source:
        source.set_colorkey((255,255,255))
        game.screen.blit(source, (x, y))
            
    def draw_tooltip(self):
      lines = [self.name]
      line_surfaces = []
      font = pygame.font.SysFont("Arial", 10)
      height = 0
      max_width = 0
      for line in lines:
        line_surface = font.render(line, False, (190,243,255,0))
        line_surfaces.append(line_surface)
        height += line_surface.get_height()
        if line_surface.get_width() > max_width:
          max_width = line_surface.get_width()
      surface = pygame.surface.Surface((max_width, height))
      surface.set_colorkey((0,0,0))
      y = 0
      for s in line_surfaces:
        surface.blit(s, (0,y))
        y += s.get_height()
      return surface
      
class Spear(Sword):
    def __init__(self, game, name, anim_name, palette_swaps={}):
      # Clone of sword __init__ but activities doesn't include slashing, healing, bashing
      self.name = name
      self.anim_name = anim_name
      self.palette_swaps = palette_swaps
      self.icon = pygame.image.load('tga/' + anim_name.split("_female")[0] + '_icon.tga')
      self.icon_small = pygame.image.load('tga/' + anim_name.split("_female")[0] + '_icon_small.tga')
      self.icon = palette_swap_multi(self.icon, self.palette_swaps)
      self.icon_small = palette_swap_multi(self.icon_small, self.palette_swaps)
      self.slot = "weapon"
      self.animations = []
      self.current_animation = None
      self.activities = ['standing', 'walking', 'attacking', 'dazed', 'falling', 'dead', 'decapitated', 'dead_decapitated', 'charging', 'taunting']
      self.current_activity = None
      self.load_animations(game, self.palette_swaps)
      self.selected_in_menu = False

    def load_animations(self, game, palette_swaps = {}):
      frames_surfaces = {}
      for activity in self.activities:
        for dir in game.directions:
          frames = []
          frame_surfaces = []
          if activity == 'walking':
            # two frames
            for x in [1,1,2,2]:
              if dir in ['N', 'NE', 'E', 'SE']:
                frames.append('tga/' + self.anim_name + '_walking_' + dir + '_' + str(x) + '.tga')
              elif dir in ['S', 'SW', 'W', 'NW']:
                frames.append('tga/' + self.anim_name + '_walking_' + dir + '_' + str(x) + '_B.tga')
                
          elif activity == 'standing':
            # one, doubled frame
            # some are called B for behind
            for n in range(4):
              if dir in ['S', 'SW','W','NW']:
               frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1_B.tga')
              else:
                frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
                
          elif activity == 'attacking':
            for x in ['_attacking_' + dir + '_1', '_attacking_' + dir + '_2',
                      '_attacking_' + dir + '_1', '_standing_' + dir + '_1']:
              filename = 'tga/' + self.anim_name + x + '.tga'
              alt_filename = 'tga/' + self.anim_name + x + '_B.tga'
              for n in range(2):
                if os.path.exists(filename):
                  frames.append(filename)
                elif os.path.exists(alt_filename):
                  frames.append(alt_filename)
          elif activity == 'taunting':
            for x in ['_attacking_' + dir + '_1', '_standing_' + dir + '_1']:
              filename = 'tga/' + self.anim_name + x + '.tga'
              alt_filename = 'tga/' + self.anim_name + x + '_B.tga'
              for n in range(2):
                if os.path.exists(filename):
                  frames.append(filename)
                elif os.path.exists(alt_filename):
                  frames.append(alt_filename)
                  
          elif activity == 'charging':
            for n in range(10):
              if os.path.exists('tga/' + self.anim_name + '_attacking_' + dir + '_2_B.tga'):
                frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_2_B.tga')
              elif os.path.exists('tga/' + self.anim_name + '_attacking_' + dir + '_2.tga'):
                frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_2.tga')
                  
          elif activity in ['falling', 'decapitated']:
            for x in range(1, 4):
              for n in range(2):
                frames.append('tga/' + self.anim_name + '_falling_' + str(x) + '.tga')
                
          elif activity == 'dazed':
            if dir in ['NW', 'S', 'SW', 'W']:
              frame ='tga/' + self.anim_name + '_standing_' + dir + '_1_B.tga'
            else:
              frame ='tga/' + self.anim_name + '_standing_' + dir + '_1.tga'
            frames = [frame] * 8
            
          elif activity in ['dead', 'dead_decapitated']:
            if os.path.exists('tga/' + self.anim_name + '_standing_SW_1_B.tga'):
              frames.append('tga/' + self.anim_name + '_standing_SW_1_B.tga')
            else:
              frames.append('tga/' + self.anim_name + '_standing_SW_1.tga')

          frame_surfaces = []
          for frame in frames:
            if frame in frames_surfaces.keys():
              surface = frames_surfaces[frame].copy() #Not sure if copy() is necessary here
            else:
              surface = pygame.image.load(frame)
              surface = palette_swap_multi(surface, palette_swaps)
              surface.set_colorkey((255,255,255))
              surface.convert()
              frames_surfaces[frame] = surface
            frame_surfaces.append(surface)

          self.animations.append(Animation(activity, [dir], frame_surfaces, frames))
      
    def draw(self, game, x, y, alpha=255):
      source = self.get_current_frame()
      if source:
        y -= 20
        x -= 10
        source.set_colorkey((255,255,255))
        source.set_alpha(alpha)
        game.screen.blit(source, (x, y))

class Bow(Sword):
  def __init__(self, game, name, anim_name, palette_swaps={}):
    self.name = name
    self.anim_name = anim_name
    self.palette_swaps = palette_swaps
    #self.icon = pygame.image.load('tga/' + anim_name.split("_female")[0] + '_icon.tga')
    #self.icon_small = pygame.image.load('tga/' + anim_name.split("_female")[0] + '_icon_small.tga')
    #self.icon = palette_swap_multi(self.icon, self.palette_swaps)
    #self.icon_small = palette_swap_multi(self.icon_small, self.palette_swaps)
    self.slot = "weapon"
    self.animations = []
    self.current_animation = None
    self.activities = ['standing', 'walking', 'shooting']
    self.current_activity = None
    self.load_animations(game, self.palette_swaps)
    self.selected_in_menu = False

  def load_animations(self, game, palette_swaps = {}):
    """
    Loads animations automatically, referring to strict naming conventions.
    Includes layer information for equipment.
    """
    for activity in self.activities:
      for dir in game.directions:
        frames = []
        frame_surfaces = []
        if activity == 'walking':
          # two frames
          for x in [1,1,2,2]:
            frames.append('tga/' + self.anim_name + '_walking_' + dir + '_' + str(x) + '.tga')
        elif activity == 'standing':
          # one, doubled frame
          # some are called B for behind
          for n in range(4):
            frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'shooting':
          # 8 frames of shooting, 8 standing
          for x in ["shooting_" + dir + "_1", "shooting_" + dir + "_2", "shooting_" + dir + "_3", "shooting_" + dir + "_1"]:
            for n in range(4):
              frames.append('tga/' + self.anim_name + "_" +  x + '.tga')
          for n in range(8):
            frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
          """
          elif activity in ['falling', 'decapitated']:
            for x in range(1, 4):
              frames.append('tga/' + self.anim_name + '_falling_' + str(x) + '.tga')
          elif activity == 'dazed':
              if dir in ['NW', 'S', 'SW', 'W']:
                  frame ='tga/' + self.anim_name + '_standing_' + dir + '_1_B.tga'
              else:
                  frame ='tga/' + self.anim_name + '_standing_' + dir + '_1.tga'
              frames = [frame, frame, frame, frame]
          elif activity in ['dead', 'dead_decapitated']:
              if os.path.exists('tga/' + self.anim_name + '_standing_SW_1_B.tga'):
                frames.append('tga/' + self.anim_name + '_standing_SW_1_B.tga')
              else:
                frames.append('tga/' + self.anim_name + '_standing_SW_1.tga')
          """
        frame_surfaces = []
        for frame in frames:
          surface = pygame.image.load(frame)
          surface = palette_swap_multi(surface, palette_swaps)
          surface.set_colorkey((255,255,255))
          frame_surfaces.append(surface)
        self.animations.append(Animation(activity, [dir], frame_surfaces, frames))

class FireSword(Sword):
  def __init__(self, game, name, anim_name):
    self.palette_swaps_1 = {(192,192,192):(255,255,0), (128,128,128):(255,128,0), (0,0,0):(255,0,0)}
    self.palette_swaps_2 = {(192,192,192):(255,128,0), (128,128,128):(255,0,0), (0,0,0):(255,255,0)}
    self.palette_swaps_3 = {(192,192,192):(255,0,0), (128,128,128):(255,255,0), (0,0,0):(255,128,0)}
    self.palette_swap_index = 0
    self.name = name
    self.anim_name = anim_name
    self.icon = pygame.image.load('tga/' + anim_name.split("_female")[0] + '_icon.tga')
    self.icon_small = pygame.image.load('tga/' + anim_name.split("_female")[0] + '_icon_small.tga')
    self.slot = "weapon"
    self.animations = []
    self.current_animation = None
    self.activities = ['standing', 'walking', 'attacking', 'bashing', 'healing', 'dazed', 'falling', 'dead', 'decapitated', 'dead_decapitated']
    self.current_activity = None
    self.load_animations(game, {})
    self.selected_in_menu = False
    
  def draw(self, game, x, y):
    if self.palette_swap_index == 0:
      ps = self.palette_swaps_1
    elif self.palette_swap_index == 1:
      ps = self.palette_swaps_2
    elif self.palette_swap_index == 2:
      ps = self.palette_swaps_3      
    self.palette_swap_index = (self.palette_swap_index + 1) % 3
    source = self.get_current_frame()
    if source:
      s2 = palette_swap(source, ps)
      s2.set_colorkey((255,255,255))
      game.screen.blit(s2, (x, y))

# # # # # # # # # # # #
# Equipment instances #
# # # # # # # # # # # #

def make(game, name, female=False):
  if name == 'sword_of_suck':
    if female:
      return Sword(game, "Sword of Suck", "sword_female", {})
    else:
      return Sword(game, "Sword of Suck", "sword", {})
  elif name == 'bronze_sword':
    if female:
      return Sword(game, "Bronze Sword", "sword_female", {(128,128,128):(193,135,77), (192,192,192):(246,204,142)})
    else:
      return Sword(game, "Bronze Sword", "sword", {(128,128,128):(193,135,77), (192,192,192):(246,204,142)})    
  elif name == 'iron_sword':
    if female:  
      return Sword(game, "Iron Sword", "sword_female", {(128,128,128): (88,67,51), (192,192,192): (130,117,107)})
    else:
      return Sword(game, "Iron Sword", "sword", {(128,128,128): (88,67,51), (192,192,192): (130,117,107)})
  elif name == 'steel_sword':
    if female:
      return Sword(game, "Steel Sword", "sword", {(128,128,128): (189,191,193), (192,192,192): (234,229,229)})
    else:
      return Sword(game, "Steel Sword", "sword", {(128,128,128): (189,191,193), (192,192,192): (234,229,229)})    
  elif name == 'fire_sword':
    return FireSword(game, "Fire Sword", "sword")
  elif name == 'klub':
    return Sword(game, "Klub", "club", {})
  elif name == 'scepter':
    return Sword(game, "Scepter", "club", {(0,0,0):(0,128,128),(128,128,128):(0,192,192),(192,192,192):(255,255,0)})
  elif name == 'gold_klub':
    return Sword(game, "Gold Klub", "club", {(0,0,0):(177,115,27),(128,128,128):(236,174,59),(192,192,192):(255,255,0)})    
  elif name == 'jick':
    return Spear(game, 'Jick', 'spear', {(192,192,192):(178,96,32), (85,43,0):(178,96,32), (128,128,128):(100, 60, 20)})
  elif name == 'spear':
    return Spear(game, "Spear", "spear", {})

  elif name == 'wooden_shield':
    return Shield(game, "Wooden Shield", "shield", {})
  elif name == 'bronze_shield':
    return Shield(game, "Bronze Shield", "shield2", {(128,128,128):(192,128,64), (192,192,192):(238,191,142), (0,0,0):(137,74,25)})
  elif name == 'iron_shield':
    return Shield(game, "Iron Shield", "shield2", {})
  elif name == 'tower_shield':
    return Shield(game, "Tower Shield", "shield3", {(255,255,0):(0,0,128)})

  elif name == 'green_bandit_shield':
    return Shield(game, "Green Bandit Shield", "shield2", {(128,128,128):(128,128,0), (192,192,192):(194,171,88), (0,0,0):(140,120,120)})

  elif name == 'iron_chain_mail':
    return Armor(game, "Iron Chain Mail", "mail", {})
  elif name == 'blue_chain_mail':
    return Armor(game, "Blue Chain Mail", "mail", {(128,128,128):(0,0,192)})
  elif name == 'blue_tunic':
    return Armor(game, "Blue Tunic", "mail", {(128,128,128):(0,0,192), (0,0,0):(0,0,128)})
  elif name == 'red_tunic': #for Hajji Firuz!
    return Armor(game, "Red Tunic", "mail", {(128,128,128):(255,0,0), (0,0,0):(192,0,0)})    
  elif name == 'brown_bandit_tunic':
    return Armor(game, "Brown Bandit Tunic", "mail", {(128,128,128):(128,64,0), (0,0,0):(85,43,0)})
  elif name == 'antimagic_vest':
    return Armor(game, "Antimagic Vest", "mail", {(0,0,0):(128,0,128), (128,128,128):(255,0,128)})
    
  elif name == 'helm_of_suck':
    if female:
      return Helm(game, "Helm of Suck", "helmet_female", {(128,128,128):(128,0,128)})    
    else:
      return Helm(game, "Helm of Suck", "helmet", {})
  elif name == 'officer_helm':
    return Helm(game, "Officer Helm", "helm2", {})
  elif name == 'blue_officer_helm':
    return Helm(game, "Officer Helm", "helm2", {(128,128,128):(0,0,128),(192,192,192):(0,0,192)})
  elif name == 'blue_triangle_hat':
    return Helm(game, "Blue Triangle Hat", "hat", {})
  elif name == 'red_triangle_hat': #for Hajji Firuz
    return Helm(game, "Red Triangle Hat", "hat", {(0,0,255):(255,0,0), (0,0,128):(128,0,0)})
  elif name == 'blue_wizard_hat':
    return Helm(game, "Blue Wizard Hat", "hat2", {})
  elif name == 'white_wizard_hat':
    return Helm(game, "White Wizard Hat", "hat2", {(0,0,128):(160,180,180), (0,0,255):(210,230,230), (0,128,255):(230,255,255)})
  elif name == 'crown':
    return Helm(game, 'Crown', 'crown', {})
  elif name == 'brown_bandit_crown':
    return Helm(game, 'Brown Bandit Crown', 'crown', {(128,128,128):(128,64,0), (0,0,0):(85,43,0), (192,192,192):(215,216,43)})
  elif name == 'cloak_of_suck':
    return Cloak(game, "Cloak of Suck", "cloak", {(0,0,0):(79,46,8), (128,128,128): (180,152,86), (255,0,0):(180,152,86)})
  elif name == 'white_wizard_cloak':
    return Cloak(game, "White Wizard Cloak", "cloak", {(0,0,0):(160,180,180), (128,128,128): (210,230,230), (255,0,0):(230,255,255)})    
  elif name == 'chain_mail_cloak':
    return Cloak(game, "Chain Mail Cloak", "cloak", {(255,0,0):(192,192,192)})
  elif name == 'cloak_of_the_forest':
    return Cloak(game, "Cloak of the Forest", "cloak", {(128,128,128):(0,128,0), (255,0,0):(0,255,0)})
  elif name == "green_bow":
    return Bow(game, "Green Bow", "bow", {(0,255,0):(190,170,150)})
  else:    
    print "BAD EQUIPMENT:", name
    sys.exit(0)
  

