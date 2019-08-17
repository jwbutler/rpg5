from __future__ import division
import pygame
import classes
from classes import *
import os
import random
import language
from units import EnemyMale, BasicUnit
from zombies import EnemyZombie, SuperZombie, ZerkerZombie

class EnemyWizard(EnemyMale): #black wizard
  def __init__(self, game, name, (x,y), palette_swaps = {}):
    self.name = name
    self.game = game
    self.anim_name = 'robed_wizard'
    self.hostile = True
    self.ally = False
    self.playable = False 
    self.has_special = False    
    self.palette_swaps = palette_swaps
    self.x = x
    self.y = y
    self.dx = 0
    self.dy = -1
    self.equipment = []
    self.inventory = []
    self.activities = ['standing', 'walking', 'casting', 'stunned', 'falling', 'dead', 'teleporting', 'appearing']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 1000
    self.current_hp = self.max_hp
    self.ticks = 0
    self.teleport_ticks = 0
    self.teleport_cooldown = 60
    self.selected = False
    self.target_x = self.target_y = self.target_unit = self.target_corpse = None
    self.zombies = []
    self.load_animations(self.palette_swaps)
    self.reset()
    
  def do_events(self):
    self.next_frame()
    self.teleport_ticks += 1
    #Emergency maneuvers
    for unit in self.game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep()
          self.move((self.dx, self.dy))
          self.reset()
          
    if self.ticks == 2:
      if self.current_activity == 'walking':
        if self.game.obstacle((self.x+self.dx,self.y+self.dy)):
          self.sidestep()
        else:
          self.game.pointers.append(Pointer((self.x,self.y), self))
          self.move((self.dx, self.dy))
        
    if self.ticks == 4:
      if self.current_activity == 'walking':
        self.reset()
      elif self.current_activity == 'standing':
        self.reset()

    if self.ticks == 8:
      if self.current_activity == 'falling':
        self.refresh_activity('dead')
        self.game.corpses.append(Corpse(self.game, self))
        for unit in self.game.units:
          if unit.target_unit == self:
            unit.target_unit = None
        self.game.units.remove(self)
        return True
      elif self.current_activity == 'teleporting':
        self.end_teleport()
        return True
      elif self.current_activity == 'appearing':
        self.reset()
        if self.target_corpse:
          corpse = self.target_corpse
          if corpse:
            self.refresh_activity('casting')
            return True
      elif self.current_activity not in ['casting', 'stunned']:
        self.reset()

    if self.current_activity == 'casting':
      target_corpse = None
      for corpse in self.game.corpses:
        if (corpse.x,corpse.y) == (self.x,self.y):
          target_corpse = corpse
      if not target_corpse:
        self.reset()
      if self.ticks == 40:
        n = 1
        while 1:
          name_available = True
          for unit in self.game.units:
            if unit.name == 'Zombie ' + str(n):
              name_available = False
          if name_available:
            self.game.units.append(EnemyZombie(self.game, "Zombie " + str(n), (self.x,self.y)))
            break
          else:
            n += 1
        self.game.corpses.remove(target_corpse)
        self.reset()
    elif self.current_activity == 'stunned':
      if self.ticks == 40:
        self.reset()
    else: #hope we don't need this
      if self.ticks == 40:    
        self.reset()
      
    if self.ticks == 0:
      if self.current_activity == 'standing':
        self.get_action()
      else:
        pass#print 'bad wizard:', self.current_activity
  
  def get_action(self):
    #EnemyWizard
    self.target_unit = None
    num_zombies = 0
    for unit in self.game.units:
      if unit.anim_name == 'zombie': #includes superzombie
        num_zombies += 1
    for unit in self.game.units:
      if unit.hostile != self.hostile:
        if self.target_unit:
          target_unit = self.target_unit
          if self.game.distance((self.x,self.y), (unit.x,unit.y)) < self.game.distance((self.x,self.y), (target_unit.x, target_unit.y)):
            self.target_unit = unit
        else:
          self.target_unit = unit
    #check zombies in list
    # should equal None if they're dead
    for zombie in self.zombies:
      if zombie:
        if zombie.current_hp <= 0: #shouldn't ever be <0
          self.zombies.remove(zombie)
      else:
        self.zombies.remove(zombie)
    
    if (len(self.zombies) < 2) and (len(self.zombies) < num_zombies):
      #flee from nearby players
      if self.target_unit:
        target_unit = self.target_unit
        if self.game.distance((self.x,self.y),(target_unit.x,target_unit.y)) < 10:
          self.point_at(target_unit)
          (self.dx, self.dy) = (-self.dx, -self.dy)
          self.reset()
          if self.teleport_ticks >= 40:
            self.refresh_activity('teleporting')
            return True
          else:
            self.refresh_activity('walking')
            return True
      #round up zombies
      self.target_unit = None
      units = self.game.units
      for unit in units:
        if unit.hostile == self.hostile:
          if unit.anim_name == 'zombie':
            if unit not in self.zombies:
              if unit.target_unit:
                target_of_target = unit.target_unit
                if target_of_target.hostile != self.hostile:
                  pass
                else:
                  if self.target_unit:
                    target_unit = self.target_unit                  
                    if self.game.distance((self.x,self.y), (unit.x,unit.y)) < self.game.distance((self.x,self.y), (target_unit.x, target_unit.y)):
                      self.target_unit = unit
                    else:
                      self.target_unit = unit
              else:
                if self.target_unit:
                  target_unit = self.target_unit
                  if self.game.distance((self.x,self.y), (unit.x,unit.y)) < self.game.distance((self.x,self.y), (target_unit.x, target_unit.y)):
                    self.target_unit = unit
                else:
                  self.target_unit = unit
      #move to target zombie
      if self.target_unit:
        target_unit = self.target_unit
        if not target_unit:
          self.target_unit = None
          self.reset()
          return False
        if self.game.distance((self.x,self.y), (target_unit.x,target_unit.y)) > 3:
          self.point_at(target_unit)
          if self.game.obstacle((self.x+self.dx, self.y+self.dy)):
            self.sidestep()
            return True            
          else:
            self.refresh_activity('walking')
            return True            
    else:
      if len(self.zombies) > 0:
        #acquire target player
        for unit in self.game.units:
          if unit.hostile != self.hostile:
            if self.target_unit:
              target_unit = self.target_unit
              if target_unit:
                if self.game.distance((self.x,self.y), (unit.x,unit.y)) < self.game.distance((self.x,self.y), (target_unit.x, target_unit.y)):
                  self.target_unit = unit
              else:
                self.target_unit = unit
            else:
              self.target_unit = unit
        #move to target player
        if self.target_unit:
          unit = self.target_unit
          if not unit:
            self.target_unit = None
            self.reset()
            return False
          if self.game.distance((self.x,self.y), (unit.x,unit.y)) > 10:
            self.point_at(unit)
            if self.game.obstacle((self.x+self.dx, self.y+self.dy)):
              self.sidestep()
              return True     
            else:
              self.refresh_activity(self.game, 'walking')
              return True
      # elif len(self.zombies) == 0:
      min_distance = 100
      target_corpse = None
      for corpse in self.game.corpses:
        if ((self.x,self.y)==(corpse.x,corpse.y)) or (not self.game.obstacle((corpse.x,corpse.y))):
          if self.game.distance((self.x,self.y),(corpse.x,corpse.y)) < min_distance:
            target_corpse = corpse
            min_distance = self.game.distance((self.x,self.y),(corpse.x,corpse.y))
      if target_corpse:
        if (self.x,self.y)==(target_corpse.x,target_corpse.y):
          self.reset()
          self.target_corpse = target_corpse
          if self.teleport_ticks >= self.teleport_cooldown:
            self.refresh_activity('teleporting')
          else:
            self.refresh_activity('casting')
        else:
          self.point_at(target_corpse)
          if self.game.obstacle((self.x+self.dx, self.y+self.dy)):
            self.sidestep()
          else:
            self.target_corpse = target_corpse
            self.refresh_activity('walking')
      else:
        if self.teleport_ticks >= self.teleport_cooldown:
          self.refresh_activity('teleporting')
          return True
        else:    
          pass
  
  def load_animations(self, palette_swaps = {}):
    """
    Loads animations automatically, referring to strict naming conventions.
    """
    frames_surfaces = {}
    for activity in self.activities:
      for dir in self.game.directions:
        frames = []
        frame_surfaces = []
        if activity in ['walking', 'standing']:
          for x in range(1,5):
            for n in range(2):
              frames.append('tga/' + self.anim_name + '_' + dir + '_' + str(x) + '.tga')
        elif activity == 'falling':
          for x in range(1, 5):
            for n in range(2):
              frames.append('tga/' + self.anim_name + '_vanishing_SE_' + str(x) + '.tga')
            
        elif activity == 'dead':
          frames.append('tga/' + self.anim_name + '_dead.tga')
        elif activity == 'casting':
          for x in [1,2,3,4, 1,2,3,4, 1,2,3,4, 5,6,7,8, 5,6,7,8]: #40 frames long
            for n in range(2):              
              frames.append('tga/' + self.anim_name + '_casting_SE_' + str(x) + '.tga')
          for frame in frames:
            surface = pygame.image.load(frame)
            surface = self.game.palette_swap_multi(surface, palette_swaps)
            surface.set_colorkey((255,255,255))
            frame_surfaces.append(surface)
          self.animations.append(Animation(activity, [dir], frame_surfaces, frames))
        elif activity == 'teleporting':
          for x in [1,2,3,4]:
            for n in range(2):              
              frames.append('tga/' + self.anim_name + '_vanishing_SE_' + str(x) + '.tga')
        elif activity == 'appearing':
          for x in [4,3,2,1]:
            for n in range(2):              
              frames.append('tga/' + self.anim_name + '_vanishing_SE_' + str(x) + '.tga')
        elif activity == 'stunned':
          #this is the blue stuff, we can copy the zombie code if needed
          for n in range(8):
            for x in [1,1,2,2]:
              frames.append('tga/' + self.anim_name + '_' + activity + '_SE_' + str(x) + '.tga')
        else:
          #default scenario
          for x in range(1, 5):
            frames.append('tga/' + self.anim_name + '_' + activity + '_' + dir + '_' + str(x) + '.tga')
        # now we load from filenames
        if activity not in ['casting']:
          for frame in frames:
            try:
              surface = frames_surfaces[frame]#.copy() #Not sure if copy() is necessary here
            except KeyError:
              try:
                surface = self.game.sprite_cache[frame].copy()
                surface = self.game.palette_swap_multi(surface, palette_swaps)
                frames_surfaces[frame] = surface
              except KeyError:
                surface = pygame.image.load(frame).convert()
                surface = self.game.palette_swap_multi(surface, palette_swaps)
                surface.set_colorkey((255,255,255))
                frames_surfaces[frame] = surface
            frame_surfaces.append(surface)
          self.animations.append(Animation(activity, [dir], frame_surfaces, frames))
          
  def take_damage(self, damage, magic=False):
    if self.current_activity == 'stunned':
      damage *= 5
    self.current_hp = max(0, self.current_hp - damage)
    if self.current_hp <= 0:
      if self.current_activity not in ['falling', 'decapitated', 'dead', 'dead_decapitated']:
        self.current_hp = 0
        self.reset()
        self.refresh_activity('falling')
        self.scream()
        
  def end_teleport(self):
    (target_x, target_y) = (0,0)
    min_distances = {}
    for (x,y) in self.game.floor.xy_tiles.keys():
      if self.game.distance((self.x,self.y), (x,y)) >= 2 and self.game.distance((self.x,self.y), (x,y)) <= 8:
        if not self.game.obstacle((x,y)):
          min_distance = 100
          for unit in self.game.units:
            if unit.hostile != self.hostile:
              if self.game.distance((self.x,self.y), (unit.x,unit.y)) < min_distance:
                min_distance = self.game.distance((self.x,self.y),(unit.x,unit.y))
          if min_distance < 100:
            min_distances[(x,y)] = min_distance
    max_min_distance = 0
    for (x,y) in min_distances.keys():
      if min_distances[(x,y)] > max_min_distance:
        (target_x,target_y) = (x,y)
        max_min_distance = min_distances[(x,y)]
    if max_min_distance > 0:
      (self.x,self.y) = (target_x,target_y)
      if self.target_corpse:
        corpse = self.target_corpse
        if corpse:
          (corpse.x, corpse.y) = (target_x,target_y)
        else:
          self.target_corpse = None
    else:
      pass#print 'phail'
    self.reset()
    self.refresh_activity("appearing")
    self.play_teleport_sound()
    self.teleport_ticks = 0
    
  def play_teleport_sound(self):
    filenames = ["sounds/teleporting.ogg"]
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(True)
    channel.play(sound)
    
  def scream(self):
    filenames = ["sounds/deadwizard.ogg"]
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(True)
    channel.play(sound)
    
  def bleed(self, damage):
    self.game.blood.append(Blood(self.x, self.y, 2*damage, (32,32,192), (64,64,255)))
        
class HornedWizard(EnemyMale):

  def load_animations(self, palette_swaps = {}):
    """
    Loads animations automatically, referring to strict naming conventions.
    """
    for activity in self.activities:
      for dir in ["N", "E", "S", "W"]:
        frames = []
        frame_surfaces = []
        if activity == 'standing':
          for x in [1,2,3,4]:
            frames.append('tga/' + self.anim_name + '_' + dir + '_' + str(x) + '.tga')
        elif activity == 'walking':
          frames.append('tga/' + self.anim_name + '_' + dir + '_1.tga')    
        elif activity == 'falling':
          for x in [1,2,3,4]:
            frames.append('tga/' + self.anim_name + '_vanishing_SE_' + str(x) + '.tga')
        elif activity == 'teleporting':
          for x in [1,2,3,4]:
            frames.append('tga/' + self.anim_name + '_vanishing_SE_' + str(x) + '.tga')
        elif activity == 'appearing':
          for x in [4,3,2,1]:
            frames.append('tga/' + self.anim_name + '_vanishing_SE_' + str(x) + '.tga')            
        elif activity == 'stunned':
          for n in range(4):
            for x in [1,2,3,4]:
              frames.append('tga/' + self.anim_name + '_' + dir + '_' + str(x) + '.tga')
        elif activity == 'dead':
          frames.append('tga/' + self.anim_name + '_dead.tga')
        elif activity == 'casting':
          frame = 'tga/' + self.anim_name + '_' + dir + '_1.tga'
          frames.append(frame)
          surface = pygame.image.load(frame)
          surface = self.game.palette_swap_multi(surface, palette_swaps)
          surface.set_colorkey((255,255,255))
          overlay_surface = pygame.image.load('tga/laser_beam_firing_' + dir + '_1.tga')
          overlay_surface.set_colorkey((255,255,255))
          surface.blit(overlay_surface, (0,0))
          frame_surfaces.append(surface)
          self.animations.append(Animation(activity, [dir], frame_surfaces, frames))          
        else:
          #default scenario, probably unused
          for x in [1,2,3,4]:
            frames.append(self.anim_name + '_' + activity + '_' + dir + '_' + str(x) + '.tga')
                
        # now we load from filenames
        if activity not in ['casting']:
          for frame in frames:
            surface = pygame.image.load(frame)
            surface = self.game.palette_swap_multi(surface, palette_swaps)
            surface.set_colorkey((255,255,255))
            frame_surfaces.append(surface)
          self.animations.append(Animation(activity, [dir], frame_surfaces, frames))
          
  def __init__(self, game, name, (x,y)):
    self.game = game
    self.name = name
    self.anim_name = 'horned_wizard'
    self.hostile = True
    self.playable = False
    self.has_special = False    
    self.palette_swaps = {}
    self.x = x
    self.y = y
    self.dx = 0
    self.dy = -1
    self.equipment = []
    self.inventory = []
    self.activities = ['standing', 'walking', 'casting', 'teleporting', 'appearing', 'falling', 'dead']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 1000
    self.current_hp = self.max_hp
    self.ticks = 0
    self.selected = False
    self.teleport_ticks = 0
    self.target_x = self.target_y = self.target_unit = None
    self.load_animations(self.palette_swaps)
    self.reset()
    
  def increment_ticks(self):
    self.ticks += 1
    self.teleport_ticks += 1
          
  def do_events(self):
    self.next_frame()  
    #Emergency maneuvers
    for unit in self.game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep()
          self.move((self.dx, self.dy))
    if self.current_activity == 'walking':
      if self.ticks == 1:
        if not self.game.obstacle((self.x+self.dx, self.y+self.dy)):
          self.move((self.dx,self.dy))
      elif self.ticks == 2:
        if not self.game.obstacle((self.x+self.dx, self.y+self.dy)):
          self.move((self.dx,self.dy))
        self.reset()
    elif self.current_activity == 'casting':
      if self.ticks > 0:
        self.game.darts.append(LaserBeam(self.game, self, (self.x+self.dx,self.y+self.dy), (self.dx,self.dy)))
        self.play_laser_sound()
        (dx,dy) = (self.dy,self.dx)
        if not self.game.obstacle((self.x+dx, self.y+dy)):
          self.move((dx,dy))
      if self.ticks == 8:
        self.reset()
        self.teleport_ticks = 0
    elif self.current_activity == 'falling':
      if self.ticks == 4:
        self.reset()
        self.refresh_activity('dead')
        self.game.corpses.append(Corpse(self.game, self))
        for unit in self.game.units:
          if unit.target_unit == self:
            unit.target_unit = None
        self.game.units.remove(self)
    elif self.current_activity == 'standing':
      if self.ticks == 4:
        self.reset()
    elif self.current_activity == 'teleporting':
      if self.ticks == 4:
        self.end_teleport()
    if self.current_activity == 'appearing':
      if self.ticks == 4:
        self.reset()
        self.point_at(self.target_unit)
        self.refresh_activity('casting')
    if self.ticks == 0 and self.current_activity == 'standing':
      self.get_action()
  
  def get_action(self):
    self.target_unit = None
    min_distance = 20
    for unit in self.game.units:
      if not unit.hostile and self.game.distance((self.x, self.y), (unit.x,unit.y)) < min_distance:
        self.target_unit = unit
        min_distance = self.game.distance((self.x,self.y), (unit.x,unit.y))
    unit = self.target_unit
    if not unit:
      return False
    if min_distance <= 20:
      unit = self.target_unit
      if self.teleport_ticks >= 10:
        self.refresh_activity('teleporting')
        return True
      #(else)
    if min_distance < 5:
      if self.run_away():
        return True
    if min_distance > 20:
      self.run_toward()
    
  def end_teleport(self):
    unit = self.target_unit  
    candidate_posns = []
    for (x,y) in self.game.floor.xy_tiles.keys():
      if self.game.distance((unit.x,unit.y),(x,y)) <= 10:
        if self.game.distance((unit.x,unit.y),(x,y)) >= 3:        
          if self.game.distance((self.x,self.y),(x,y)) <= 10:          
            if (x == unit.x) or (y == unit.y):
              if not self.game.obstacle((x,y)):
                candidate_posns.append((x,y))
    if len(candidate_posns) > 0:
      (self.x,self.y) = random.choice(candidate_posns)
    else:
      return False#print "fail"
    self.reset()
    self.refresh_activity("appearing")
    self.play_teleport_sound()
    self.teleport_ticks = 0
      
  def run_away(self):
    unit = self.target_unit  
    (dx,dy) = (unit.x-self.x, unit.y-self.y)
    if dx != 0:
      dx /= abs(dx)
    if dy != 0:
      dy /= abs(dy)
    dirs = ["N","E","S","W"]
    max_distance = self.game.distance((self.x, self.y), (unit.x,unit.y))
    (target_dx,target_dy) = (0,0)
    for dir in dirs:
      (dx, dy) = self.game.dir_to_coords(dir)
      dist = self.game.distance((self.x+dx, self.y+dy), (unit.x,unit.y))
      if self.game.obstacle((self.x+dx, self.y+dy)) or self.game.obstacle((self.x+2*dx, self.y+2*dy)):
        pass
      elif self.x+dx == unit.x or self.y+dy == unit.y:
        max_distance = dist
        (target_dx, target_dy) = (dx,dy)
        break
      elif dist > max_distance:
        max_distance = dist
        (target_dx, target_dy) = (dx,dy)
    if (target_dx, target_dy) != (0,0):
      (self.dx,self.dy) = (target_dx,target_dy)
      self.refresh_activity('walking')
      return True
    else:
      return False
      
  def run_toward(self):
    unit = self.target_unit  
    (dx,dy) = (unit.x-self.x, unit.y-self.y)
    if dx != 0:
      dx /= abs(dx)
    if dy != 0:
      dy /= abs(dy)
    dirs = ["N","E","S","W"]
    min_distance = self.game.distance((self.x,self.y), (unit.x,unit.y))
    (target_dx,target_dy) = (None,None)
    for dir in dirs:
      (dx, dy) = self.game.dir_to_coords(dir)
      dist = self.game.distance((self.x+dx, self.y+dy), (unit.x,unit.y))
      if self.game.obstacle((self.x+dx, self.y+dy)) or self.game.obstacle((self.x+2*dx, self.y+2*dy)):
        pass
      elif dist < min_distance:
        min_distance = dist
        (target_dx, target_dy) = (dx,dy)
    if min_distance < self.game.distance((self.x,self.y), (unit.x,unit.y)):
      (self.dx,self.dy) = (target_dx,target_dy)
      self.refresh_activity('walking')
      return True
    else:
      return False#print 'trapped :( :( :('
      
  def point_at(self, target):
    (dx,dy) = (target.x-self.x, target.y-self.y)
    try:
      if abs(dx) > abs(dy):
        (dx,dy) = (dx/abs(dx), 0)
      elif abs(dx) < abs(dy):
        (dx,dy) = (0, dy/abs(dy))
      else:
        (dx,dy) = random.choice[(dx/abs(dx), 0), (0, dy/abs(dy))]
      (self.dx,self.dy) = (dx,dy)
      return True
    except:
      return False
      
  def play_teleport_sound(self):
    filenames = ["sounds/teleporting.ogg"]
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(True)
    channel.play(sound)
    
  def play_laser_sound(self):
    filenames = ["sounds/laser.ogg"]
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(True)
    channel.play(sound)
    
class RezOnlyWizard(EnemyWizard):
  def __init__(self, game, name, (x,y), palette_swaps = {}):
    EnemyWizard.__init__(self, game, name, (x,y), palette_swaps = {})
    del self.zombies # this is a hack to make the zombies not follow this wizard
                     # I think zombies use a hasattr() to find a leader
    self.resurrect_cooldown = self.game.tps * 12
    self.teleport_cooldown = self.game.tps * 8
    self.resurrect_cooldown_ticks = self.resurrect_cooldown
    self.rez_sound_channel = None
  
  def do_events(self):
    self.next_frame()
    self.teleport_ticks += 1
    self.resurrect_cooldown_ticks += 1
    if self.current_activity != 'casting':
      if self.rez_sound_channel:
        self.rez_sound_channel.stop()
        self.rez_sound_channel = None
    #Emergency maneuvers
    for unit in self.game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep()
          self.move((self.dx, self.dy))
          self.reset()

    if self.ticks == 2:
      if self.current_activity == 'walking':
        if self.game.obstacle((self.x+self.dx,self.y+self.dy)):
          self.sidestep()
        else:
          self.move((self.dx, self.dy))
        
    if self.ticks == 4:
      if self.current_activity == 'walking':
        self.reset()
      elif self.current_activity == 'standing':
        self.reset()

    if self.ticks == 8:
      if self.current_activity == 'falling':
        self.refresh_activity('dead')
        self.game.corpses.append(Corpse(self.game, self))
        for unit in self.game.units:
          if unit.target_unit == self:
            unit.target_unit = None
        self.game.units.remove(self)
        return True
      elif self.current_activity == 'teleporting':
        self.end_teleport()
        return True
      elif self.current_activity == 'appearing':
        self.reset()
        if self.target_corpse:
          corpse = self.target_corpse
          if corpse:
            self.refresh_activity('casting')
            return True
      elif self.current_activity not in ['casting', 'stunned']:
        self.reset()

    if self.current_activity == 'casting':
      target_corpse = None
      for corpse in self.game.corpses:
        if (corpse.x,corpse.y) == (self.x,self.y):
          target_corpse = corpse
      if not target_corpse:
        self.reset()
      if self.ticks == 40:
        n = 1
        while 1:
          name_available = True
          for unit in self.game.units:
            if unit.name == 'Zombie ' + str(n):
              name_available = False
          if name_available:
            self.game.units.append(EnemyZombie(self.game, "Zombie " + str(n), (self.x,self.y)))
            break
          else:
            n += 1
        self.game.corpses.remove(target_corpse)
        self.rez_sound_channel = None
        self.play_laugh_sound()
        self.reset()
    elif self.current_activity == 'stunned':
      if self.ticks == 40:
        self.reset()
    else: #hope we don't need this
      if self.ticks == 40:    
        self.reset()
      
    if self.ticks == 0:
      if self.current_activity == 'standing':
        self.get_action()
      else:
        pass#print 'bad wizard:', self.current_activity
    
  def get_action(self):
    #print self.resurrect_cooldown_ticks, self.resurrect_cooldown
    if self.resurrect_cooldown_ticks >= self.resurrect_cooldown:
      # If resurrect is ready, find a corpse & rez it
      min_distance = 100 #they can see corpses (almost) anywhere
      target_corpse = None
      for corpse in self.game.corpses:
        if ((self.x,self.y)==(corpse.x,corpse.y)) or (not self.game.obstacle((corpse.x,corpse.y))):
          if self.game.distance((self.x,self.y),(corpse.x,corpse.y)) < min_distance:
            target_corpse = corpse
            min_distance = self.game.distance((self.x,self.y),(corpse.x,corpse.y))
      if target_corpse:
        self.target_corpse = target_corpse
        if (self.x,self.y)==(target_corpse.x,target_corpse.y):
          self.reset()
          self.refresh_activity('casting')
          self.play_rez_sound()
          self.resurrect_cooldown_ticks = 0
          # start cooldown at the beginning of cast rather than the end
          # so he won't try to res again if he is interrupted
        else:
          self.point_at(target_corpse)
          if self.game.obstacle((self.x+self.dx, self.y+self.dy)):
            self.sidestep()
          else:
            self.refresh_activity('walking')
            
    #otherwise, stay out of trouble
    else:
      for unit in self.game.units:
        if unit.hostile != self.hostile:
          if self.game.distance((self.x, self.y), (unit.x, unit.y)) <= 20:
            self.reset()
            if self.teleport_ticks >= self.teleport_cooldown:
              self.refresh_activity('teleporting')
              return True
            else:
              self.point_at(unit)
              (self.dx, self.dy) = (-self.dx, -self.dy)
              self.refresh_activity('walking')
              return True

  def end_teleport(self):
    if self.game.filename == 'tga/levels/townlol2.tga':
      if self.game.ticks/self.game.tps > 60:
        self.game.units.remove(self)
    (target_x, target_y) = (0,0)
    max_min_distance = 0
    #bound_rect = pygame.rect.Rect((self.x-12,self.y-12,24,24))
    for (x,y) in self.game.floor.xy_tiles.keys():
      #if bound_rect.collidepoint((x,y)):
      d = self.game.distance((self.x,self.y), (x,y))
      if  d >= 10 and d <= 12:
        if not self.game.obstacle((x,y)):
          min_distance = 100
          for unit in self.game.units:
            if unit.hostile != self.hostile:
              d_2 = self.game.distance((x,y), (unit.x,unit.y))
              if d_2 < min_distance:
                min_distance = d_2
          if min_distance > max_min_distance:
            max_min_distance = min_distance
            (target_x,target_y) = (x,y)
          #if max_min_distance >= 20:
          #  break
    if max_min_distance > 0:
      (self.x,self.y) = (target_x,target_y)
      self.teleport_ticks = 0
    self.reset()
    self.refresh_activity("appearing")
    self.play_teleport_sound()
    self.teleport_ticks = 0
    
  def play_laugh_sound(self):
    filenames = ["sounds/wizardlaugh.ogg"]
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(True)
    if channel:
      channel.play(sound)
      
  def play_rez_sound(self):
    filenames = ["sounds/rez2.ogg"]
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(True)
    if channel:
      channel.play(sound)
      self.rez_sound_channel = channel
      
class RedWizard(EnemyWizard, EnemyMale):
  def __init__(self, game, name, (x,y)):
    BasicUnit.__init__(self, game, name, 'robed_wizard', (x,y))
    self.hostile = True
    self.playable = False
    self.has_special = False    
    self.palette_swaps = {(58,58,58):(192,0,0), (192,192,192):(255,128,64), (128,128,128):(128,0,0)}
    self.equipment = []
    self.inventory = []
    self.activities = ['standing', 'walking', 'casting', 'falling', 'dead', 'teleporting', 'appearing', 'stunned']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 600
    self.current_hp = self.max_hp
    self.evade_speed = 0.7
    self.fireball_ticks = 0
    self.max_fireball_ticks = 10
    self.teleport_ticks = 0
    self.max_teleport_ticks = 40
    self.target_x = self.target_y = self.target_unit = None
    self.zombies = []
    self.load_animations(self.palette_swaps)
    self.reset()
    
  def do_events(self):
    self.teleport_ticks += 1
    self.fireball_ticks += 1
    self.next_frame()
    #Emergency maneuvers
    for unit in self.game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep()
          self.move((self.dx, self.dy))
          
    if self.ticks == 2:
      if self.current_activity == 'walking':
        self.move((self.dx, self.dy))

    if self.ticks == 4:
      if self.current_activity == 'walking':
        if not self.game.floor.rect.collidepoint((self.x, self.y)):
          self.game.units.remove(self)
        self.reset()
        
    if self.ticks == 4:
      if self.current_activity == 'standing':
        self.reset()

    if self.ticks == 8:
      if self.current_activity == 'falling':
        self.refresh_activity('dead')
        self.game.corpses.append(Corpse(self.game, self))
        for unit in self.game.units:
          if unit.target_unit == self.name:
            unit.target_unit = None
        self.game.units.remove(self)
        return True
      elif self.current_activity == 'casting':
        self.game.darts.append(Fireball(self.game, self, self.target_unit))
        self.fireball_ticks = 0
        self.reset()
      elif self.current_activity == 'teleporting':
        self.end_teleport()
      elif self.current_activity != 'stunned':
        self.reset()
        
    if self.ticks == 32:
      if self.current_activity == 'stunned':
        self.reset()
      
    if self.ticks == 0:
      if self.current_activity not in ['falling', 'dead', 'decapitated', \
      'dead_decapitated', 'appearing', 'casting']:
        self.get_action()
      else: #what does this leave?
        pass#print 'bad wizard'
        
  def end_teleport(self):
    (target_x, target_y) = (0,0)
    min_distances = {}
    
    # For each tile on the grid, find the distance to the closest player unit 
    for (x,y) in self.game.floor.xy_tiles.keys():
      if self.game.distance((self.x,self.y), (x,y)) >= 5 and self.game.distance((self.x,self.y), (x,y)) <= 15:
        if not self.game.obstacle((x,y)):
          min_distance = 20
          for unit in self.game.units:
            if unit.hostile != self.hostile:
              if self.game.distance((self.x,self.y), (unit.x,unit.y)) < min_distance:
                min_distance = self.game.distance((self.x,self.y), (unit.x,unit.y))
                target_unit = unit
          if min_distance < 20:
            min_distances[(x,y)] = min_distance
    max_min_distance = 0
    for (x,y) in min_distances.keys():
      if min_distances[(x,y)] > max_min_distance:
        (target_x,target_y) = (x,y)
        max_min_distance = min_distances[(x,y)]
    if max_min_distance > 0:
      (self.x,self.y) = (target_x,target_y)
      self.reset()
      self.refresh_activity("appearing")
      self.teleport_ticks = 0
      return True
    else:
      #print 'phail'
      return False
  
  def get_action(self):
    #RedWizard
    
    # Acquire a target
    self.target_unit = None
    for unit in self.game.units:
      if unit.hostile != self.hostile:
        if self.target_unit:
          if self.game.distance((self.x,self.y), (unit.x,unit.y)) < \
          self.game.distance((self.x,self.y), (self.target_unit.x, self.target_unit.y)):
            self.target_unit = unit
        else:
          if self.game.distance((self.x,self.y), (unit.x,unit.y)) <= 10:
            self.target_unit = unit
    
    # Evasive action
    if self.target_unit:
      unit = self.target_unit
      self.point_at(unit)
      if self.game.distance((self.x, self.y), (unit.x, unit.y)) <= 5:
        (self.dx,self.dy) = (-self.dx,-self.dy)
        if self.teleport_ticks >= self.max_teleport_ticks:
          self.reset()
          self.refresh_activity(self.game, 'teleporting')
        else:
          if random.random() < self.evade_speed:
            if self.game.obstacle((self.x+self.dx,self.y+self.dy)):
              self.sidestep()
            else:
              self.refresh_activity('walking')
      elif self.game.distance((self.x, self.y), (unit.x, unit.y)) <= 10:
        if self.fireball_ticks >= self.max_teleport_ticks:
          self.refresh_activity('casting')
      else:
        if self.game.obstacle((self.x+self.dx,self.y+self.dy)):
          self.sidestep()
        else:
          self.refresh_activity('walking')
    else:
      if random.random() < 0.75:
        (self.dx, self.dy) = self.game.dir_to_coords(random.choice(self.game.directions))
        if self.game.obstacle((self.x+self.dx,self.y+self.dy)):
          self.sidestep()
        else:
          self.refresh_activity('walking')
    self.reset_ticks()
  

  def load_animations(self, palette_swaps = {}):
    # C/P from enemywizard + casting stuff?
    for activity in self.activities:
      for dir in self.game.directions:
        frames = []
        frame_surfaces = []
        if activity in ['walking', 'standing']:
          for x in range(1,5):
            # two frames
              frames.append('tga/' + self.anim_name + '_' + dir + '_' + str(x) + '.tga')
            
        elif activity == 'falling':
          for x in range(1, 5):
            frames.append('tga/' + self.anim_name + '_vanishing_SE_' + str(x) + '.tga')
        elif activity == 'dead':
            frames.append('tga/' + self.anim_name + '_dead.tga')
        elif activity == 'casting':
          for x in [1,2,3,4]:
            frame = 'tga/' + self.anim_name + '_casting_SE_' + str(x) + '.tga'
            for y in range(2):
              frames.append(frame)
              surface = pygame.image.load(frame)
              surface = self.game.palette_swap_multi(surface, palette_swaps)
              surface.set_colorkey((255,255,255))
              overlay_surface = pygame.image.load('tga/fireball2_forming_SE_' + str(x) + '.tga')
              overlay_surface.set_colorkey((255,255,255))
              surface.blit(overlay_surface, (0,0))
              frame_surfaces.append(surface)
              self.animations.append(Animation(activity, [dir], frame_surfaces, frames))
        elif activity == 'teleporting':
          for x in [1,2,3,4]:
            frames.append('tga/' + self.anim_name + '_vanishing_SE_' + str(x) + '.tga')
        elif activity == 'appearing':
          for x in [4,3,2,1]:
            frames.append('tga/' + self.anim_name + '_vanishing_SE_' + str(x) + '.tga')
        elif activity == 'stunned':
          #this is the blue stuff, we can copy the zombie code if needed
          for n in range(8):
            for x in [1,1,2,2]:
              frames.append('tga/' + self.anim_name + '_' + activity + '_SE_' + str(x) + '.tga')
        else:
          #default scenario
          for x in range(1, 5):
            frames.append(self.anim_name + '_' + activity + '_' + dir + '_' + str(x) + '.tga')

        # now we load from filenames
        if activity not in ['casting']:
          doubled_frames = []
          for frame in frames:
            doubled_frames.append(frame)
            doubled_frames.append(frame)
          frames = doubled_frames
          for frame in frames:
            surface = pygame.image.load(frame)
            surface = self.game.palette_swap_multi(surface, palette_swaps)
            surface.set_colorkey((255,255,255))
            frame_surfaces.append(surface)
          self.animations.append(Animation(activity, [dir], frame_surfaces, frames))


  def damage(self):
    return 5
    
  def take_damage(self, game, damage, magic=False):
    self.current_hp -= damage
    if self.current_hp <= 0:
      if self.current_activity not in ['falling', 'decapitated', 'dead', 'dead_decapitated']:
        self.current_hp = 0
        self.reset()
        self.refresh_activity('falling')
