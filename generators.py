from __future__ import division
import pygame
from classes import *
from units import *
from npcs import *
from enemy_humans import *
from wizards import *
from zombies import *

import equipment
import os
import random
import language

class ZombieGenerator:
  def __init__(self, game, (x,y), radius, super_frequency):
    self.game = game
    (self.x,self.y) = (x,y)
    self.radius = radius #not vision radius but spawn radius
    self.super_frequency = super_frequency # 0.0 to 1.0, represents frequency of making a SuperZombie
    
  def generate(self):
    n = 1
    while 1:
      name_available = True
      for unit in self.game.units:
        if unit.name == 'Zombie ' + str(n):
          name_available = False
      if name_available:
        if random.random() <= self.super_frequency:
          r = random.randint(1,2)
          if r == 1:
            unit = SuperZombie(self.game, "Zombie " + str(n), (self.x, self.y))
          elif r == 2:
            unit = ZerkerZombie(self.game, "Zombie " + str(n), (self.x, self.y))
        else:
          unit = EnemyZombie(self.game, "Zombie " + str(n), (self.x, self.y))
        self.game.add_unit(unit)
        return unit.name
        break
      else:
        n += 1
        if n >= 1000: #reasonable upper bound?
          return False
        
  def do_events(self):
    #check for units in range, trigger if it finds any
    for unit in self.game.units:
      if not unit.hostile:
        if self.game.distance((unit.x,unit.y),(self.x,self.y)) <= self.radius:
          self.generate()
          self.game.generators.remove(self)
          return True

class RisingZombieGenerator(ZombieGenerator):
  def __init__(self, game, (x,y), super_frequency):
    (self.x,self.y) = (x,y)
    self.game = game
    self.radius = 5 #not vision radius but spawn radius
    self.super_frequency = super_frequency
  
  def generate(self):
    n = 1
    while 1:
      name_available = True
      for unit in self.game.units:
        if unit.name == 'Zombie ' + str(n):
          name_available = False
      if name_available:
        if random.random() <= self.super_frequency:
          r = random.randint(1,2)
          if r == 1:
            unit = SuperZombie(self.game, "Zombie " + str(n), (self.x, self.y))
          elif r == 2:
            unit = ZerkerZombie(self.game, "Zombie " + str(n), (self.x, self.y))
        else:
          unit = EnemyZombie(self.game, "Zombie " + str(n), (self.x, self.y))
        self.game.add_unit(unit)
        unit.refresh_activity(self.game, 'rising')
        return unit.name
        break
      else:
        n += 1
        if n >= 1000: #reasonable upper bound?
          return False

class InfiniteZombieGenerator(ZombieGenerator):
  # a.k.a. Battle Generator
  # can generate zombies, superzombies, bandits, or wizards depending on level maxima
  # does not generate if player unitss are within range
  def __init__(self, game, (x,y), radius, max_zombies, max_superzombies, max_bandits, max_wizards, max_total, probability=0.02):
    (self.x,self.y) = (x,y)
    self.game = game
    self.radius = radius
    self.active = True
    self.cooldown = 50 # 10 seconds
    self.cooldown_remaining = 0
    self.max_zombies = max_zombies
    self.max_superzombies = max_superzombies
    self.max_bandits = max_bandits
    self.max_wizards = max_wizards
    self.max_total = max_total
    self.probability = probability #just to slow it down a bit - maybe have this as a parameter
    
  def do_events(self):
    # this version is a little different - it only works if no friendly units are in range
    hostile_units = 0
    zombies = 0
    superzombies = 0
    bandits = 0
    wizards = 0
    for unit in self.game.units:
      if unit.hostile:
        hostile_units += 1
        #not using isinstance because it returns false positives in some inheritance situations
        if unit.__class__ == SuperZombie:
          superzombies += 1        
        elif unit.__class__ == EnemyZombie:
          zombies += 1
        elif unit.__class__ == EnemyBandit:
          bandits += 1
        elif unit.__class__ == RezOnlyWizard:
          wizards += 1
        if hostile_units >= self.max_total:
          return False
        elif (zombies + superzombies + bandits + wizards) >= (self.max_zombies + self.max_superzombies + self.max_bandits + self.max_wizards): #in case the numbers aren't synced up
          return False
      else:
        if self.game.distance((unit.x,unit.y),(self.x,self.y)) <= self.radius:
          return False
    if self.active:
      if random.random() <= self.probability:
        self.generate(zombies, superzombies, bandits, wizards)
    else:
      self.cooldown_remaining -= 1
      if self.cooldown_remaining == 0:
        self.active = True

  def generate(self, zombies, superzombies, bandits, wizards):
    while 1:
      r = random.randint(1,4)
      if r == 1 and zombies < self.max_zombies:
        n = 1        
        while 1:
          name_available = True
          for unit in self.game.units:
            if unit.name == 'Zombie ' + str(n):
              name_available = False
              break              
          if name_available:
            unit = EnemyZombie("Zombie " + str(n), (self.x, self.y), None, 100) #these have extra vision radius
            self.game.add_unit(unit)
            self.active = False
            self.cooldown_remaining = self.cooldown
            return unit.name
          else:
            n += 1
            if n >= 1000:
              print 'generator error'
              return False
      elif r == 2 and superzombies < self.max_superzombies:
        n = 1
        while 1:
          name_available = True
          for unit in self.game.units:
            if unit.name == 'Zombie ' + str(n):
              name_available = False
              break              
          if name_available:
            unit = SuperZombie(self.game, "Zombie " + str(n), (self.x, self.y), 100)
            self.game.add_unit(unit)
            self.active = False
            self.cooldown_remaining = self.cooldown
            return unit.name
          else:
            n += 1
            if n >= 1000:
              print 'generator error'
              return False
      elif r == 3 and bandits < self.max_bandits:
        n = 1
        while 1:
          name_available = True
          for unit in self.game.units:
            if unit.name == 'Bandit ' + str(n):
              name_available = False
              break              
          if name_available:
            unit = EnemyBandit(self.game, "Bandit " + str(n), (self.x, self.y))
            self.game.add_unit(unit)
            self.active = False
            self.cooldown_remaining = self.cooldown
            return unit.name
          else:
            n += 1
            if n >= 1000:
              print 'generator error'
              return False
      elif r == 4 and wizards < self.max_wizards:
        n = 1
        while 1:
          name_available = True
          for unit in self.game.units:
            if unit.name == 'Wizard ' + str(n):
              name_available = False
              break
          if name_available:
            unit = RezOnlyWizard(self.game, "Wizard " + str(n), (self.x, self.y))
            self.game.add_unit(unit)
            self.active = False
            self.cooldown_remaining = self.cooldown
            return unit.name
          else:
            n += 1
            if n >= 1000:
              print 'generator error'
              return False

class BanditGenerator(ZombieGenerator):
  #def __init__(self, game, (x,y), radius, super_frequency):
    
  def generate(self):
    n = 1
    while 1:
      name_available = True
      for unit in self.game.units:
        if unit.name == 'Bandit ' + str(n):
          name_available = False
      if name_available:
        if random.random() < self.super_frequency:
          if random.randint(1,2) == 1:
            self.game.add_unit(EnemyBanditVar(self.game, "Bandit " + str(n), (self.x, self.y)))
          else:
            self.game.add_unit(EnemyBanditClub(self.game, "Bandit " + str(n), (self.x, self.y)))
        else:
          self.game.add_unit(EnemyBandit(self.game, "Bandit " + str(n), (self.x, self.y)))
        return
      else:
        n += 1

class InfiniteBanditGenerator(BanditGenerator):
  def __init__(self, game, (x,y), super_frequency, max_bandits, probability=0.02):
    self.game = game  
    (self.x,self.y) = (x,y)
    self.active = False
    self.cooldown = self.game.tps * 15
    self.cooldown_remaining = random.randint(0,self.cooldown)
    self.super_frequency = super_frequency
    self.max_bandits = max_bandits
    self.probability = probability #just to slow it down a bit
    
  def do_events(self):
    # this version is a little different - it only works if no friendly units are in range
    hostile_units = len([u for u in self.game.units if u.hostile])
    if hostile_units >= self.max_bandits:
      return False
    if self.active:
      if random.random() <= self.probability:
        self.generate()
    else:
      self.cooldown_remaining -= 1
      if self.cooldown_remaining == 0:
        self.active = True
        
  def generate(self):
    BanditGenerator.generate(self)
    self.active = False
    self.cooldown_remaining = self.cooldown
    
class BanditGeneratorNetwork(BanditGenerator):
  def __init__(self, game, pixel_array, super_frequency, max_bandits):
    spawn_points = []
    for y in range(pixel_array.surface.get_height()):
      for x in range(pixel_array.surface.get_width()):
        (r,g,b,a) = pixel_array.surface.unmap_rgb(pixel_array[x][y])
        if (r,g,b) == (255,128,64):
          spawn_points.append((x,y))
    self.spawn_points = spawn_points #list of posns
    self.active = False
    self.min_cooldown = self.game.tps * 3
    self.max_cooldown = self.game.tps * 7
    self.cooldown_remaining = self.min_cooldown
    self.super_frequency = super_frequency
    self.max_bandits = max_bandits
    
  def do_events(self):
    # this version is a little different - it only works if no friendly units are in range
    hostile_units = len([u for u in self.game.units if u.hostile])
    if hostile_units >= self.max_bandits:
      return False
    # despawns after a minute and a half. i forget why.
    if self.game.ticks > 90*self.game.tps:
      self.game.generators.remove(self)
      return
    if self.active:
      self.generate()
    else:
      self.cooldown_remaining -= 1
      if self.cooldown_remaining == 0:
        self.active = True
        
  def generate(self):
    n = 1
    (x,y) = random.choice(self.spawn_points)
    while 1:
      name_available = True
      for unit in self.game.units:
        if unit.name == 'Bandit ' + str(n):
          name_available = False
      if name_available:
        if random.random() < self.super_frequency:
          if random.randint(1,2) == 1:
            self.game.add_unit(EnemyBanditVar(self.game, "Bandit " + str(n), (x, y)))
          else:
            self.game.add_unit(EnemyBanditClub(self.game, "Bandit " + str(n), (x, y)))
        else:
          self.game.add_unit(EnemyBandit(self.game, "Bandit " + str(n), (x, y)))
        break
      else:
        n += 1
    self.active = False
    self.cooldown_remaining = random.randint(self.min_cooldown, self.max_cooldown)

class SoldierGenerator(ZombieGenerator):
  def __init__(self, game, (x,y), radius):
    #no SuperBandits ...
    ZombieGenerator.__init__(self, game, (x,y), radius, 0)
  
  def generate(self):
    n = 1
    while 1:
      name_available = True
      for unit in self.game.units:
        if unit.name == 'Soldier ' + str(n):
          n += 1
          break
      else:
        self.game.add_unit(EnemySoldier(self.game, "Soldier " + str(n), (self.x, self.y)))
        return
