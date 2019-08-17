from __future__ import division
import pygame
from functions import *
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
    (self.x,self.y) = (x,y)
    self.radius = radius #not vision radius but spawn radius
    self.super_frequency = super_frequency # 0.0 to 1.0, represents frequency
                                           # of making a SuperZombie
    
  def generate(self, game):
    n = 1
    while 1:
      name_available = True
      for unit in game.units:
        if unit.name == 'Zombie ' + str(n):
          name_available = False
      if name_available:
        if random.random() <= self.super_frequency:
          r = random.randint(1,2)
          if r == 1:
            unit = SuperZombie(game, "Zombie " + str(n), (self.x, self.y))
          elif r == 2:
            unit = ZerkerZombie(game, "Zombie " + str(n), (self.x, self.y))
        else:
          unit = EnemyZombie(game, "Zombie " + str(n), (self.x, self.y))
        game.units.append(unit)
        return unit.name
        break
      else:
        n += 1
        if n >= 1000: #reasonable upper bound?
          return False
        
  def do_events(self, game):
    #check for units in range, trigger if it finds any
    for unit in game.units:
      if not unit.hostile:
        if distance((unit.x,unit.y),(self.x,self.y)) <= self.radius:
          self.generate(game)
          game.generators.remove(self)
          return True

class RisingZombieGenerator(ZombieGenerator):
  def __init__(self, game, (x,y), super_frequency):
    (self.x,self.y) = (x,y)
    self.radius = 5 #not vision radius but spawn radius
    self.super_frequency = super_frequency
  
  def generate(self, game):
    n = 1
    while 1:
      name_available = True
      for unit in game.units:
        if unit.name == 'Zombie ' + str(n):
          name_available = False
      if name_available:
        if random.random() <= self.super_frequency:
          r = random.randint(1,2)
          if r == 1:
            unit = SuperZombie(game, "Zombie " + str(n), (self.x, self.y))
          elif r == 2:
            unit = ZerkerZombie(game, "Zombie " + str(n), (self.x, self.y))
        else:
          unit = EnemyZombie(game, "Zombie " + str(n), (self.x, self.y))
        game.units.append(unit)
        unit.refresh_activity(game, 'rising')
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
    
  def do_events(self, game):
    # this version is a little different - it only works if no friendly units are in range
    hostile_units = 0
    zombies = 0
    superzombies = 0
    bandits = 0
    wizards = 0
    for unit in game.units:
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
        if distance((unit.x,unit.y),(self.x,self.y)) <= self.radius:
          return False
    if self.active:
      if random.random() <= self.probability:
        self.generate(game, zombies, superzombies, bandits, wizards)
    else:
      self.cooldown_remaining -= 1
      if self.cooldown_remaining == 0:
        self.active = True

  def generate(self, game, zombies, superzombies, bandits, wizards):
    while 1:
      r = random.randint(1,4)
      if r == 1 and zombies < self.max_zombies:
        n = 1        
        while 1:
          name_available = True
          for unit in game.units:
            if unit.name == 'Zombie ' + str(n):
              name_available = False
              break              
          if name_available:
            unit = EnemyZombie(game, "Zombie " + str(n), (self.x, self.y), None, 100) #these have extra vision radius
            game.units.append(unit)
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
          for unit in game.units:
            if unit.name == 'Zombie ' + str(n):
              name_available = False
              break              
          if name_available:
            unit = SuperZombie(game, "Zombie " + str(n), (self.x, self.y), 100)
            game.units.append(unit)    
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
          for unit in game.units:
            if unit.name == 'Bandit ' + str(n):
              name_available = False
              break              
          if name_available:
            unit = EnemyBandit(game, "Bandit " + str(n), (self.x, self.y))
            game.units.append(unit)    
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
          for unit in game.units:
            if unit.name == 'Wizard ' + str(n):
              name_available = False
              break
          if name_available:
            unit = RezOnlyWizard(game, "Wizard " + str(n), (self.x, self.y))
            game.units.append(unit)
            self.active = False
            self.cooldown_remaining = self.cooldown
            return unit.name
          else:
            n += 1
            if n >= 1000:
              print 'generator error'
              return False

class BanditGenerator(ZombieGenerator):
  def __init__(self, game, (x,y), radius):
    #no SuperBandits ...
    ZombieGenerator.__init__(self, game, (x,y), radius, 0)
  
  def generate(self,game):
    n = 1
    while 1:
      name_available = True
      for unit in game.units:
        if unit.name == 'Bandit ' + str(n):
          name_available = False
      if name_available:
        game.units.append(EnemyBandit(game, "Bandit " + str(n), (self.x, self.y)))
        return
      else:
        n += 1
        
class SoldierGenerator(ZombieGenerator):
  def __init__(self, game, (x,y), radius):
    #no SuperBandits ...
    ZombieGenerator.__init__(self, game, (x,y), radius, 0)
  
  def generate(self,game):
    n = 1
    while 1:
      name_available = True
      for unit in game.units:
        if unit.name == 'Soldier ' + str(n):
          n += 1
          break
      else:
        game.units.append(EnemySoldier(game, "Soldier " + str(n), (self.x, self.y)))
        return
