from __future__ import division
import pygame
from classes import *

import equipment
import os
import random
import language

class Horse(PlayerMale):
  #Generic class for cavalry archer/lancer/swordsman
  def __init__(self, game, name, rider_anim_name, (x,y), palette_swaps = {}):
    BasicUnit.__init__(self, game, name, 'horse', (x,y))
    self.hostile = False
    self.playable = True
    self.has_special = False
    self.equipment = []
    self.inventory = []
    self.activities = ['standing', 'walking']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.current_hp = self.max_hp
    self.rider_anim_name = rider_anim_name
    self.load_animations(self.palette_swaps)
    self.reset()
    
  def increment_ticks(self):
      self.ticks += 1
    
  def load_animations(self, palette_swaps):
    PlayerMale.load_animations(self, palette_swaps)

  def do_events(self):
    self.next_frame()  
    """ Copy/pasted from PlayerMale. """
    for unit in self.game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep()
    if self.ticks == 1:
      if self.current_activity == 'walking':
        for unit in self.game.units:
          if (unit.x,unit.y) == (self.x+self.dx,self.y+self.dy):
            if unit.hostile == self.hostile:
              if unit.current_activity == 'standing':
                if unit != self.target_unit:
                  unit.knockback((self.dx,self.dy))
        if self.game.obstacle((self.x+self.dx, self.y+self.dy)):
          self.sidestep()
        else:
          self.move((self.dx, self.dy))
    if self.ticks == 2:
      if self.current_activity == 'walking':
        if (self.x,self.y) != (self.target_x,self.target_y):
          if self.game.obstacle((self.x+self.dx, self.y+self.dy)):
            pass
          else:
            self.move((self.dx, self.dy))      
        self.reset()
      elif self.current_activity == 'standing':
        self.reset()
      elif self.current_activity == 'attacking':
        self.end_attack()
      elif self.current_activity == 'bashing':
        self.end_bash()
        
    if self.ticks == 4:
      if self.current_activity == 'attacking':
        self.reset()
      elif self.current_activity == 'bashing':
        self.reset()
      elif self.current_activity == 'falling':
        self.refresh_activity('dead')
        self.game.corpses.append(Corpse(self.game, self))
        self.selected = False
        for unit in self.game.units:
          if unit.target_unit == self:
            unit.target_unit = None
        self.game.units.remove(self)
        return True
      elif self.current_activity != 'stunned': #i'm not sure why we need this, but it's a good failsafe
        self.reset()
        
    if self.ticks == 8:
      if self.current_activity == 'stunned':
        self.reset()
        
    if self.ticks == 0:
      if self.current_activity == 'bashing': #weird
        pass#print 'bad playermale!'
      else:
        self.get_action()
    
  def get_action(self):
    PlayerMale.get_action(self)
    
  def move_to_target_unit(self):
    PlayerMale.move_to_target_unit(self)
    
  def draw(self):
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    #x -= 8; y -= 30
    x -= 18; y -= 50
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
        
  def load_animations(self, palette_swaps = {}):
    """
    C/P'ed from PlayerMale.
    """
    for activity in self.activities:
      for dir in self.game.directions:
        frames = []
        frame_surfaces = []
        if activity == 'walking':
          # two frames
          frames.append('tga/' + self.anim_name + '_walking_' + dir + '_1.tga')
          frames.append('tga/' + self.anim_name + '_walking_' + dir + '_2.tga')
        elif activity == 'standing':
          frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
          frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'attacking':
          frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_1.tga')
          frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_2.tga')
          frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_1.tga')
          frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        else:
          #default scenario, (hopefully) unused
          for x in xrange(4):
            frames.append("tga/" + anim_name + '_' + activity + '_' + dir + '_' + str(x) + '.tga')
        # now we load from filenames
        for frame in frames:
          surface = pygame.image.load(frame)
          surface = self.game.palette_swap_multi(surface, palette_swaps)
          surface.set_colorkey((255,255,255))
          if activity in ['standing', 'walking']:
            rider_surface = pygame.image.load("tga/" + self.rider_anim_name + "_" + dir + "_1.tga")
            rider_surface.set_colorkey((255,255,255))
          offset = (0, 0)
          surface.blit(rider_surface, offset)
          frame_surfaces.append(surface)
        self.animations.append(Animation(activity, [dir], frame_surfaces, frames))