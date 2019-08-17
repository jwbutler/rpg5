
from __future__ import division
import pygame
from units import BasicUnit, PlayerMale, EnemyMale
from npcs import SoldierNPC
import equipment
import random
from functions import distance, obstacle, obstacle_unit

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
                      equipment.make(game, 'iron_chain_mail'),
                      equipment.make(game, 'iron_sword'),
                      equipment.make(game, 'iron_shield'),
                      equipment.Hairpiece(game, 'Hair', 'hairpiece'),
                      equipment.make(game, 'helm_of_suck')
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
    self.load_animations(game, self.palette_swaps)
    self.reset(game)
    
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
                      equipment.make(game, 'iron_chain_mail'),
                      equipment.make(game, 'iron_sword'),
                      equipment.make(game, 'iron_shield'),
                      equipment.Hairpiece(game, 'Hair', 'hairpiece'),
                      equipment.make(game, 'officer_helm')
                     ]
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'decapitated', 'dead_decapitated']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.current_hp = self.max_hp
    self.load_animations(game, self.palette_swaps)
    self.reset(game)
    
class EnemyBandit(EnemySoldier):
  def __init__(self, game, name, (x,y)):
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.vision_radius = 12
    self.hostile = True
    self.playable = False
    self.ally = False
    self.has_special = False
    self.palette_swaps.update({(0,0,128):(90,60,0)})
    equip_palette_swaps =  {(128,64,0):(128,0,128), (128,128,128):(192,128,0), (192,192,192):(255,255,0)}
    self.equipment = [equipment.make(game, 'sword_of_suck'),
                      equipment.make(game, 'brown_bandit_tunic'),
                      equipment.Hairpiece(game, 'Hair of Suck', 'hairpiece'),
                      equipment.make(game, 'brown_bandit_crown'),
                      equipment.make(game, 'green_bandit_shield')
                     ]
    self.current_hp = self.max_hp = 90
    self.avoidance = 0.3
    self.mitigation = 0
    self.min_damage = 6
    self.max_damage = 8    
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'decapitated', 'dead_decapitated']
    self.current_activity = 'standing'
    self.animations = []
    self.load_animations(game, self.palette_swaps)
    self.reset(game)
    
  def play_target_sound(self):
    filenames = ["sounds/hey.ogg"]
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(False) #we don't want them overwriting death screams
    if channel:
      channel.play(sound)
