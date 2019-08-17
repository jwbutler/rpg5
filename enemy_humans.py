
from __future__ import division
import pygame
from units import BasicUnit, PlayerMale, EnemyMale
from npcs import SoldierNPC
from classes import Corpse, HealthPowerup
import equipment
import random

class EnemySoldier(EnemyMale):
  def __init__(self, game, name, (x,y)):
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.name = name
    self.anim_name = "player"
    self.hostile = True
    self.playable = False
    self.ally = False
    self.has_special = False
    self.palette_swaps.update({(128,128,64): (128,128,128), (128,64,0): (128,128,128)})
    self.equipment = [
                      equipment.make(self.game, 'iron_chain_mail'),
                      equipment.make(self.game, 'iron_sword'),
                      equipment.make(self.game, 'iron_shield'),
                      equipment.Hairpiece(self.game, 'Hair', 'hairpiece'),
                      equipment.make(self.game, 'helm_of_suck')
                     ]
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'stunned']
    self.current_activity = 'standing'
    self.animations = []
    self.current_hp = self.max_hp = 90
    self.min_damage = 6
    self.max_damage = 8
    self.mitigation = 0.1
    self.avoidance = 0.2
    self.evade_speed = 0.5
    self.load_animations(self.palette_swaps)
    self.reset()
    
class EnemyOfficer(EnemyMale):
  def __init__(self, game, name, (x,y)):
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.name = name
    self.anim_name = "player"
    self.hostile = True
    self.playable = False
    self.ally = False
    self.has_special = False
    self.palette_swaps.update({(128,128,64): (192,192,192), (128,64,0): (192,192,192), (0,0,0):(64,64,64)})
    #hair
    self.equipment = [
                      equipment.make(self.game, 'iron_chain_mail'),
                      equipment.make(self.game, 'iron_sword'),
                      equipment.make(self.game, 'iron_shield'),
                      equipment.Hairpiece(self.game, 'Hair', 'hairpiece'),
                      equipment.make(self.game, 'officer_helm')
                     ]
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'decapitated', 'dead_decapitated']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.current_hp = self.max_hp
    self.load_animations(self.palette_swaps)
    self.reset()
    
class EnemyBandit(EnemySoldier):
  def __init__(self, game, name, (x,y)):
    t1 = pygame.time.get_ticks()
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.vision_radius = 12
    self.hostile = True
    self.playable = False
    self.ally = False
    self.has_special = False
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'stunned']
    self.palette_swaps.update({(0,0,128):(90,60,0)})
    equip_palette_swaps =  {(128,64,0):(128,0,128), (128,128,128):(192,128,0), (192,192,192):(255,255,0)}
    self.equipment = [equipment.Sword(self.game, "Sword", 'sword', self.activities),
      equipment.Armor(self.game, "Brown Bandit Tunic", "mail", self.activities,
        {(128,128,128):(128,64,0), (0,0,0):(85,43,0)}),
      equipment.Helm(self.game, 'Brown Bandit Crown', 'crown', self.activities,
        {(128,128,128):(128,64,0), (0,0,0):(85,43,0), (192,192,192):(215,216,43)})]
    hairpiece = equipment.Hairpiece(self.game, 'Hair', 'hairpiece', self.activities)
    self.equipment.append(hairpiece)
    if random.random() <= 0.25:
      self.equipment.append(equipment.Beard(self.game, 'Beard', self.activities, hairpiece.palette_swaps))
    self.current_hp = self.max_hp = 80
    self.avoidance = 0
    self.mitigation = 0
    self.min_damage = 4
    self.max_damage = 7
    self.evade_speed = 0.4

    self.current_activity = 'standing'
    self.animations = []
    self.load_animations(self.palette_swaps)
    self.reset()
    t2 = pygame.time.get_ticks()
    if self.game.debug: print "Bandit load time:", t2-t1, "ms"

  def do_events(self):
    self.next_frame()
    #Emergency maneuvers
    for obj in self.game.units + self.game.trees:
      if obj != self:
        if (obj.x, obj.y) == (self.x, self.y):
          self.sidestep()
          self.reset()
    
    if self.current_activity == 'walking':
      if self.ticks == 2:
        self.move((self.dx, self.dy))
      elif self.ticks == 4:
        self.reset()
    
    elif self.current_activity == 'attacking':
      if self.ticks == 4:
        self.end_attack()
      elif self.ticks == 8:
        self.reset()
                
    elif self.current_activity == 'standing':
      if self.ticks == 4:
        self.reset()

    elif self.current_activity == 'falling':
      if self.ticks == 8:
        self.refresh_activity('dead')
        self.reset_ticks()
        self.game.corpses.append(Corpse(self.game, self))
        self.game.bandits_killed += 1
        powerup_chance = 0.30
        if random.random() < powerup_chance:
          for powerup in self.game.powerups:
            if (powerup.x, powerup.y) == (self.x,self.y):
              break
          else:
            self.game.powerups.append(HealthPowerup(self.game, (self.x,self.y), 25))
        for unit in self.game.units:
          if unit.target_unit == self:
            unit.target_unit = None
        self.game.remove_unit(self)
        return True
    
    elif self.ticks == 16:
      if self.current_activity == 'stunned':
        self.reset()
      
    if self.ticks == 0:
      if self.current_activity in ['falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned']:
        pass
      else:
        self.get_action()

  def play_target_sound(self):
    filenames = ["sounds/hey.ogg"]
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(False) #we don't want them overwriting death screams
    if channel:
      channel.play(sound)
      
class EnemyBanditVar(EnemyBandit):
  def __init__(self, game, name, (x,y)):
    t1 = pygame.time.get_ticks()
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.vision_radius = 12
    self.hostile = True
    self.playable = False
    self.ally = False
    self.has_special = False
    self.palette_swaps.update({(0,0,128):(90,60,0)})
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'stunned']
    self.equipment = [equipment.Sword(self.game, "Steel Sword", "sword", self.activities,
        {(128,128,128): (189,191,193), (192,192,192): (234,229,229)}),
      equipment.Helm(self.game, 'Crown', 'crown', self.activities),
      equipment.Shield(self.game, "Green Bandit Shield", "shield2", self.activities,
        {(128,128,128):(128,128,0), (192,192,192):(170,190,90), (0,0,0):(100,140,100)}),
      equipment.Armor(self.game, 'Chain Mail', 'mail', self.activities)]
    hairpiece = equipment.Hairpiece(self.game, 'Hair', 'hairpiece', self.activities)
    self.equipment.append(hairpiece)
    if random.random() <= 0.5:
      self.equipment.append(equipment.Beard(self.game, 'Beard', self.activities, hairpiece.palette_swaps))
      
    self.current_hp = self.max_hp = 80
    self.avoidance = 0.3
    self.mitigation = 0
    self.min_damage = 5
    self.max_damage = 8
    self.evade_speed = 0.4
    self.current_activity = 'standing'
    self.animations = []
    self.load_animations(self.palette_swaps)
    self.reset()
    t2 = pygame.time.get_ticks()
    if self.game.debug:  print "Banditvar load time:", t2-t1, "ms"
    
class EnemyBanditClub(EnemyBandit):
  def __init__(self, game, name, (x,y)):
    t1 = pygame.time.get_ticks()
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.vision_radius = 12
    self.hostile = True
    self.playable = False
    self.ally = False
    self.has_special = False
    self.palette_swaps.update({(0,0,128):(90,60,0), (128,128,64):self.skin_color, (0,0,0):self.skin_color,
                               (128,128,0):self.skin_color, (192,192,192):self.skin_color})
    self.activities = ['standing', 'walking', 'attacking_club', 'falling', 'dead', 'stunned']
    self.equipment = [equipment.Sword(self.game, "Club", "club", self.activities),
                      equipment.Cloak(self.game, 'Cloak', 'cloak', self.activities,
                        {(0,0,0):(64,64,64), (128,128,128):(128,128,64),
                        (255,0,0):(128,128,64), (255,128,64):(64,64,64)})
                     ]
    hairpiece = equipment.Hairpiece(self.game, 'Hair', 'hairpiece', self.activities)
    self.equipment.append(hairpiece)
    if random.random() <= 0.75:
      self.equipment.append(equipment.Beard(self.game, 'Beard', self.activities, hairpiece.palette_swaps))
      
    self.current_hp = self.max_hp = 100
    self.avoidance = 0
    self.mitigation = 0
    self.min_damage = 10
    self.max_damage = 16
    self.evade_speed = 0.2
    self.current_activity = 'standing'
    self.animations = []
    self.load_animations(self.palette_swaps)
    self.reset()
    t2 = pygame.time.get_ticks()
    if self.game.debug: print "Banditclub load time:", t2-t1, "ms"
    
  def do_events(self):
    self.next_frame()
    #Emergency maneuvers
    for obj in self.game.units + self.game.trees:
      if obj != self:
        if (obj.x, obj.y) == (self.x, self.y):
          self.sidestep()
          self.reset()
    
    if self.current_activity == 'walking':
      if self.ticks == 2:
        self.move((self.dx, self.dy))
      elif self.ticks == 4:
        self.reset()
    
    elif self.current_activity == 'attacking_club':
      if self.ticks == 8:
        self.end_attack()
      elif self.ticks == 16:
        self.reset()
                
    elif self.current_activity == 'standing':
      if self.ticks == 4:
        self.reset()

    elif self.current_activity == 'falling':
      if self.ticks == 8:
        self.refresh_activity('dead')
        self.reset_ticks()
        self.game.corpses.append(Corpse(self.game, self))
        self.game.bandits_killed += 1
        powerup_chance = 0.40
        if random.random() < powerup_chance:
          for powerup in self.game.powerups:
            if (powerup.x, powerup.y) == (self.x,self.y):
              break
          else:
            self.game.powerups.append(HealthPowerup(self.game, (self.x,self.y), 25))
        for unit in self.game.units:
          if unit.target_unit == self:
            unit.target_unit = None
        self.game.remove_unit(self)
        return True
    
    elif self.ticks == 16:
      if self.current_activity == 'stunned':
        self.reset()
      
    if self.ticks == 0:
      if self.current_activity in ['falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned']:
        pass
      else:
        self.get_action()
        
  def get_action(self):
    #EnemyMale
    new_target = True
    if self.target_unit:
      target_unit = self.target_unit
      if not target_unit:
        self.target_unit = None
      else:
        new_target = False
  
    for unit in self.game.units:
      if unit.hostile != self.hostile:
        if self.game.LOS((self.x,self.y),(unit.x,unit.y)):
          if self.target_unit:
            target_unit = self.target_unit
            if self.game.distance((self.x,self.y), (unit.x,unit.y)) < self.game.distance((self.x,self.y), (target_unit.x,target_unit.y)):
              self.target_unit = unit
          else:
            if self.game.distance((self.x,self.y), (unit.x,unit.y)) <= 10:
              self.target_unit = unit
    if self.target_unit:
      unit = self.target_unit
      if not unit:
        self.target_unit = None
        self.reset()
        return False
      if new_target:
        self.play_target_sound()
      self.point_at(unit)
      if (self.current_hp / self.max_hp) <= 0.25:
        (self.dx,self.dy) = (-self.dx,-self.dy)
        if self.game.obstacle((self.x+self.dx,self.y+self.dy)):
          self.sidestep()
        else:
          if random.random() <= self.evade_speed:
            if not self.game.obstacle((self.x+self.dx,self.y+self.dy)):
              self.refresh_activity('walking')
      else: # non-critical HP      
        if self.game.obstacle((self.x+self.dx, self.y+self.dy)):      
          if (unit.x, unit.y) == (self.x+self.dx, self.y+self.dy):
            self.refresh_activity('attacking_club')
          elif self.game.obstacle_unit((self.x+self.dx, self.y+self.dy)):
            unit_2 = self.game.obstacle_unit((self.x+self.dx, self.y+self.dy))
            if unit_2.hostile != self.hostile:
              self.target_unit = unit_2
              self.refresh_activity('attacking_club')  
            else:
              self.sidestep()
        else:
          self.refresh_activity('walking')
    else:
      if random.random() > 0.50:
        self.dx = random.randint(-1,1)
        self.dy = random.randint(-1,1)
        if not self.game.obstacle((self.x+self.dx,self.y+self.dy)):
          self.refresh_activity('walking')
    self.reset_ticks()
