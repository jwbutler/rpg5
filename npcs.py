from __future__ import division
import random
import pygame
import equipment
from units import BasicUnit, PlayerMale, AltPlayerMale, PlayerFemale, PlayerHealer, EnemyMale, PlayerFemaleMelee, PlayerArcher
from classes import Corpse, ThrowingRock

class AltPlayerMaleNPC(AltPlayerMale):
  def __init__(self, game, name, (x, y)):
    AltPlayerMale.__init__(self, game, name, (x, y))
    self.playable = False

  def show_dialog(self, unit_name):
    #Write a method in RPG so we can reuse code instead of C&Ping this
    self.game.show_dialog = True
    self.game.dialog_boxes = [unit_name + ": " + self.name.split()[0] + ", what the hell is going on around here?",
                         self.name + ": I don't know " + unit_name.split()[0] + "... our patrol was attacked.  They tore up our lieutenant and two of my jickers.  They ate them alive!",
                         unit_name + ": We'd better get to town before more of them show up.",
                         self.name + ": Let's move.\n[" + self.name + " has joined your party.]"
                        ]
    self.game.dialog_index = 0
    self.game.dialog_ticks = 25
    self.game.dialog_box = self.game.draw_dialog(self.game.dialog_boxes[self.game.dialog_index])
    self.refresh_activity("talking")
    
  def end_dialog(self):
    self.playable = True
    for unit in self.game.units:
      if isinstance(unit, JickerNPC):
        unit.ally = True
    self.target_unit = None
    self.reset(self)
    
class PlayerFemaleNPC(PlayerFemale):
  def __init__(self, game, name, (x, y)):
    PlayerFemale.__init__(self, game, name, (x, y))
    self.playable = False

  def show_dialog(self, unit_name):
    self.game.show_dialog = True
    spearman = leader = None
    for unit in self.game.units:
      if not unit.hostile and unit.playable:
        for equip in unit.equipment:
          if equip.anim_name == 'spear':
            spearman = unit.name
          if equip.anim_name == 'sword' and unit.anim_name == 'player':
            leader = unit.name
    if leader and spearman:
      self.game.dialog_boxes = [leader + ": What are you doing out here "+self.name.split()[0]+"?  Don't you know it's dangerous?",
                           self.name + ": I was on my way to town to sell my eggs when a bunch of those horrible people attacked me!  I got away but i had to leave my cart and they killed my donkey!",
                           spearman + ": We're going to town too.  We'll be safe there.",
                           leader + ": Don't worry, you're safe with me.",
                           self.name + ": Sure "+leader.split()[0]+".\n[" + self.name + " has joined your party.]"
                          ]      
    else:
      self.game.dialog_boxes = [unit_name + ": What are you doing out here "+self.name.split()[0]+"?  Don't you know it's dangerous?",
                           self.name + ": I was on my way to town to sell my eggs when a bunch of those horrible people attacked me!  I got away but i had to leave my cart and they killed my donkey!",
                           unit_name + ": I'm going to town too.  Come with me, you'll be safe.",
                           self.name + ": Oh thank you, I knew you would help me!  Hey, where is your friend?\n[" + self.name + " has joined your party.]"
                          ]
    self.game.dialog_index = 0
    self.game.dialog_ticks = int(len(self.game.dialog_boxes[self.game.dialog_index])/2)
    self.game.dialog_box = self.game.draw_dialog(self.game.dialog_boxes[self.game.dialog_index])
    self.refresh_activity("talking")
    
  def end_dialog(self):
    self.playable = True
    self.target_unit = None
    self.reset(self)
    
class PlayerHealerNPC(PlayerHealer):
  def __init__(self, game, name, (x, y)):
    PlayerHealer.__init__(self, game, name, (x, y))
    self.playable = False

  def show_dialog(self, unit_name):
    self.game.show_dialog = True
    leader = girl = spearman = None
    noobs = False
    for unit in self.game.units:
      if not unit.hostile and unit.playable:
        if unit.anim_name == 'female':
          girl = unit.name
        for equip in unit.equipment:
          if equip.anim_name == 'spear':
            spearman = unit.name
          if equip.anim_name == 'sword' and unit.anim_name == 'player':
            leader = unit.name
      elif unit.ally:
        noobs = True
    if leader and girl and spearman:
      self.game.dialog_boxes = [
                           self.name + ": Well well well, if it isn't my good friends "+leader.split()[0]+" and "+spearman.split()[0]+".  I'm glad to see you alive and well.  I see "+girl+" has been taking care of you.",
                           leader + ": Oh yeah! Wait...",
                           spearman + ": We're trying to fight our way to the town, but there are more and more of these things everywhere.",
                           self.name + ": You look like you could use some more help.  I can heal you, just don't get ripped up too fast, all right?",
                           "[" + self.name + " has joined your party.]"
                          ]
      
    elif leader and (girl or spearman):
      second_party_member = girl or spearman
      self.game.dialog_boxes = [
                           self.name + ": Well well well, I'm happy to see my good friends "+unit_name.split()[0]+" and "+second_party_member.split()[0]+" are still among the living.  You look like you could use some help.",
                           leader + ": We could have used your help before.",
	                         self.name + ": Today there are many people who need help.  You must come with me to the town.  People from all around have fled there for shelter, and the Mayor needs every armed hand he can get.",
                         	 second_party_member + ": Thats where we're going.",
                           "[" + self.name + " has joined your party.]"
                          ]
    else:
      self.game.dialog_boxes = [
                           self.name + ": Hello " + unit_name.split()[0] + "!  You look like you could use some help.  What are you doing out here all by yourself?  Where are your friends?",
                           unit_name + ": My friends could have used your help a few minutes ago!",
                           self.name + ": I see.  But you are still among the living.  There are people who need your help in town.  I will go with you - I can heal you, just don't get yourself torn up too fast, all right?",
                           "[" + self.name + " has joined your party.]"
                          ]
    self.game.dialog_index = 0
    self.game.dialog_ticks = 25
    self.game.dialog_box = self.game.draw_dialog(self.game.dialog_boxes[self.game.dialog_index])
    self.refresh_activity("talking")
    
  def end_dialog(self):
    self.playable = True
    self.target_unit = None
    self.reset(self)
    
class BasicFriendlyNPC(EnemyMale, PlayerMale):
  def __init__(self, game, name, (x, y)):
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.name = name
    self.anim_name = 'player'
    self.hostile = False
    self.playable = False
    self.ally = False
    self.has_special = False
    self.palette_swaps.update({(128,64,0):(64,32,0), (0,0,0):(128,64,0)})
    self.equipment = [equipment.Hairpiece(self.game, "Hair of Suck", "hairpiece")]
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned']
    self.current_activity = 'standing'
    self.animations = []
    self.current_hp = self.max_hp = 80
    self.avoidance = self.mitigation = 0
    self.current_hp = self.max_hp
    self.load_animations(self.palette_swaps)
    self.reset()
    
  def draw_hp_bar(self, width, height, alpha=255):
    green_bar = pygame.Rect((1, 1, (width-2), (height-2)))
    surface = pygame.Surface((width, height))
    surface.fill((255, 255, 255))
    surface.fill((0,128,255), green_bar)
    hp_ratio = self.current_hp/self.max_hp
    red_left = round(hp_ratio*(width-2))+1
    red_left = max(red_left, 0)
    red_width = round((1-hp_ratio)*(width-2))
    red_bar = pygame.Rect((red_left, 1, red_width, (height-2)))
    surface.fill((128, 0, 128), red_bar)
    surface.set_alpha(alpha)
    return surface
    
  def get_action(self):
    self.target_unit = None
    for unit in self.game.units:
      if unit.hostile != self.hostile:
        if self.target_unit:
          target_unit = self.target_unit
          if self.game.distance((self.x,self.y), (unit.x,unit.y)) < self.game.distance((self.x,self.y), (target_unit.x,target_unit.y)):
            self.target_unit = unit
        else:
          if self.game.distance((self.x,self.y), (unit.x,unit.y)) <= 5:
            self.target_unit = unit
    if self.target_unit:
      target_unit = self.target_unit
      if not unit:
        self.target_unit = None
        self.reset()
        return False
      self.point_at(target_unit)
      (self.dx, self.dy) = (-self.dx, -self.dy)
      if self.game.obstacle((self.x+self.dx, self.y+self.dy)):
        self.sidestep()
      else:
        if (self.x - self.dx, self.y - self.dy) == (target_unit.x, target_unit.y):
          (self.dx, self.dy) = (-self.dx, -self.dy)   
          self.refresh_activity('attacking')
        else:
          if random.random() > 0.50:
            self.refresh_activity('walking')
            self.reset_ticks()
    else:
      #face nearest player unit
      min_distance = 100
      self.target_unit = None
      for unit in self.game.units:
        if self.game.distance((self.x,self.y), (unit.x,unit.y)) < min_distance:
          self.target_unit = unit
          self.point_at(unit)
          min_distance = self.game.distance((self.x,self.y), (unit.x,unit.y))
      if self.target_unit:
        if self.game.obstacle((self.x+self.dx, self.y+self.dy)):
          pass
        else:
          pass#self.refresh_activity(game, 'walking')
    self.reset_ticks()
  
  def show_dialog(self, unit_name):
    self.game.show_dialog = True
    self.game.dialog_boxes = [self.name + ": HELO HOW RU?"]      
    self.game.dialog_index = 0
    self.game.dialog_ticks = int(len(self.game.dialog_boxes[self.game.dialog_index])/2)
    self.game.dialog_box = self.game.draw_dialog(self.game.dialog_boxes[self.game.dialog_index])
    self.refresh_activity(self.game, "talking")
    
  def end_dialog(self):
    self.reset()
    
  def draw(self):
    PlayerMale.draw(self)
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    x += 4
    y -= 24
    alpha = 128
    for unit in self.game.units:
      if not unit.hostile:
        if unit.target_unit == self:
          alpha = 255
    self.game.screen.blit(self.draw_hp_bar(16, 5, alpha), (x,y))

class WaypointedCivilian(BasicFriendlyNPC):
  def __init__(self, game, name, (x, y), waypoints):
    BasicFriendlyNPC.__init__(self, game, name, (x,y))
    self.current_hp = self.max_hp = 50
    self.waypoints = waypoints
    
  def do_events(self):
    self.next_frame()
    for unit in self.game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep()
          return

    if self.current_activity == 'walking':
      if self.ticks == 2:
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
      elif self.ticks == 4:
        self.reset()
        
    elif self.current_activity == 'standing':
      if self.ticks == 4:
        self.reset()
        
    elif self.current_activity == 'falling':
      if self.ticks == 8:
        self.refresh_activity('dead')
        self.game.corpses.append(Corpse(self.game, self))
        self.selected = False
        for unit in self.game.units:
          if unit.target_unit == self:
            unit.target_unit = None
        self.game.units.remove(self)
        return
        
    elif self.current_activity == 'stunned':
      if self.ticks == 16:
        self.reset()

    if self.ticks >= 16:
      if self.game.debug: print "WaypointedCivilian failsafe"
      self.reset()
        
    if self.ticks == 0:
      self.get_action()
      
  def get_action(self):
    if random.random() < 0.25:
      self.reset()
      return
    else:
      enemy_units = [u for u in self.game.units if u.hostile != self.hostile]
      closest_enemy = None
      min_distance = 8
      for u in enemy_units:
        if self.game.distance((self.x,self.y),(u.x,u.y)) < min_distance:
          if self.game.LOS((self.x,self.y),(u.x,u.y)):
            if closest_enemy == None:
              closest_enemy = u
            else:
              if self.game.distance((self.x,self.y),(u.x,u.y)) < self.game.distance((self.x,self.y), (closest_enemy.x,closest_enemy.y)):
                closest_enemy = u
      if closest_enemy:
        if self.game.distance((self.x,self.y), (closest_enemy.x,closest_enemy.y)) <= 4:
          self.point_at(closest_enemy)
          (self.dx,self.dy) = (-self.dx,-self.dy)
          self.refresh_activity('walking')
          self.reset_ticks()
          return
        
      else:
        if self.waypoints:      
          if self.game.distance((self.x,self.y), self.waypoints[0]) <= 3:
            self.waypoints.pop(0)
        
        if self.waypoints:
          friendly_units = [u for u in self.game.units if u.playable]
          for u in friendly_units:
            if self.game.distance((self.x, self.y), (u.x, u.y)) <= 12:
              (x,y) = self.waypoints[0]
              (dx,dy) = (x-self.x, y-self.y)
              m = (dx**2 + dy**2)**0.5
              if m != 0:
                (self.dx, self.dy) = (round(dx/m), round(dy/m))

              self.refresh_activity('walking')
              self.reset_ticks()
              return

      self.reset()
      
class RockThrowingPeasant(WaypointedCivilian):
  # Phase out WaypointedCivilian entirely? There's a ton of C/P here
  def __init__(self, game, name, (x, y), waypoints):
    t1 = pygame.time.get_ticks()
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.name = name
    self.anim_name = 'player'
    self.hostile = False
    self.playable = False
    self.ally = False
    self.has_special = False
    self.palette_swaps.update({(128,64,0):(64,32,0), (0,0,0):(128,64,0)})
    self.activities = ['standing', 'walking', 'falling', 'dead', 'stunned', 'throwing']
    self.equipment = [equipment.Hairpiece(self.game, "Hair of Suck", "hairpiece", self.activities)]
    self.inventory = []
    self.current_activity = 'standing'
    self.animations = []
    self.current_hp = self.max_hp = 60
    self.avoidance = self.mitigation = 0
    self.waypoints = waypoints
    self.load_animations(self.palette_swaps)
    self.reset()
    t2 = pygame.time.get_ticks()
    if self.game.debug: print "Rock thrower load time:", t2-t1
    
  def do_events(self):
    self.next_frame()
    for unit in self.game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep()
          return

    if self.current_activity == 'walking':
      if self.ticks == 2:
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
      elif self.ticks == 4:
        self.reset()
        if (self.target_x,self.target_y) != (None, None):
          if (self.x,self.y) == (self.target_x,self.target_y):
            (self.target_x,self.target_y) = (None, None)
            enemy_units = [u for u in self.game.units if u.hostile != self.hostile]
            closest_enemy = None
            max_distance = 10
            for u in enemy_units:
              if self.game.distance((self.x,self.y),(u.x,u.y)) < max_distance:
                if self.game.LOS((self.x,self.y),(u.x,u.y)):
                  if closest_enemy == None:
                    closest_enemy = u
                  else:
                    if self.game.distance((self.x,self.y),(u.x,u.y)) < \
                    self.game.distance((self.x,self.y), (closest_enemy.x,closest_enemy.y)):
                      closest_enemy = u
            if closest_enemy:
              self.target_unit = closest_enemy
              self.point_at(closest_enemy)
              self.refresh_activity('throwing')
              for rocks in self.game.rock_piles:
                if (rocks.x,rocks.y) == (self.x,self.y):
                  rocks.remove_one()
        
    elif self.current_activity == 'standing':
      if self.ticks == 4:
        self.reset()
        
    elif self.current_activity == 'falling':
      if self.ticks == 8:
        self.refresh_activity('dead')
        self.game.corpses.append(Corpse(self.game, self))
        self.selected = False
        for unit in self.game.units:
          if unit.target_unit == self:
            unit.target_unit = None
        self.game.units.remove(self)
        return
        
    elif self.current_activity == 'stunned':
      if self.ticks == 16:
        self.reset()
    
    elif self.current_activity == 'throwing':
      if self.ticks == 4:
        self.game.darts.append(ThrowingRock(self.game, 8, self, self.target_unit))
      elif self.ticks == 16:
        self.reset()

    if self.ticks >= 16:
      print "WaypointedCivilian failsafe"
      self.reset()
        
    if self.ticks == 0:
      if self.current_activity != 'throwing':
        self.get_action()

  def get_action(self):
    if random.random() < 0.25:
      self.reset()
      return
    else:
      enemy_units = [u for u in self.game.units if u.hostile != self.hostile]
      closest_enemy = None
      max_distance = 10
      for u in enemy_units:
        if self.game.distance((self.x,self.y),(u.x,u.y)) < max_distance:
          if self.game.LOS((self.x,self.y),(u.x,u.y)):
            if closest_enemy == None:
              closest_enemy = u
            else:
              if self.game.distance((self.x,self.y),(u.x,u.y)) < self.game.distance((self.x,self.y), (closest_enemy.x,closest_enemy.y)):
                closest_enemy = u
      if closest_enemy:
        rock_piles = [o for o in self.game.rock_piles]
        closest_rocks = None
        max_distance = 10
        for rocks in rock_piles:
          if self.game.distance((closest_enemy.x,closest_enemy.y),(rocks.x,rocks.y)) < max_distance:
            if self.game.distance((self.x,self.y),(rocks.x,rocks.y)) < max_distance:
              if self.game.LOS((self.x,self.y),(rocks.x,rocks.y)):
                if closest_rocks == None:
                  closest_rocks = rocks
                else:
                  if self.game.distance((self.x,self.y),(rocks.x,rocks.y)) < \
                    self.game.distance((self.x,self.y), (closest_rocks.x,closest_rocks.y)):
                    closest_rocks = rocks

      if closest_enemy:
        if self.game.distance((self.x,self.y), (closest_enemy.x,closest_enemy.y)) <= 4:
          self.point_at(closest_enemy)
          (self.dx,self.dy) = (-self.dx,-self.dy)
          self.refresh_activity('walking')
          self.reset_ticks()
          return
        elif closest_rocks:
          self.point_at(closest_rocks)
          (self.target_x, self.target_y) = (closest_rocks.x, closest_rocks.y)
          self.refresh_activity('walking')
          self.reset_ticks()
          return
        
      if self.waypoints:      
        if self.game.distance((self.x,self.y), self.waypoints[0]) <= 1:
          self.waypoints.pop(0)
      
      if self.waypoints:
        friendly_units = [u for u in self.game.units if u.playable]
        for u in friendly_units:
          if self.game.distance((self.x, self.y), (u.x, u.y)) <= 8:
            (x,y) = self.waypoints[0]
            (dx,dy) = (x-self.x, y-self.y)
            m = (dx**2 + dy**2)**0.5
            if m != 0:
              (self.dx, self.dy) = (round(dx/m), round(dy/m))

            self.refresh_activity('walking')
            self.reset_ticks()
            return
          elif self.game.distance((u.x,u.y), self.waypoints[0]) < self.game.distance((self.x,self.y), self.waypoints[0]):
            (x,y) = self.waypoints[0]
            (dx,dy) = (x-self.x, y-self.y)
            m = (dx**2 + dy**2)**0.5
            if m != 0:
              (self.dx, self.dy) = (round(dx/m), round(dy/m))

            self.refresh_activity('walking')
            self.reset_ticks()
            return
      elif self.waypoints == []: #Not if it's None
        self.game.remove_unit(self)
        self.game.cleared_npcs += 1
        return
      elif self.waypoints == None:
        if random.random() > 0.5:        
          self.dx = random.randint(-1,1)
          self.dy = random.randint(-1,1)
          if not self.game.obstacle((self.x+self.dx,self.y+self.dy)):
            self.refresh_activity('walking')
            self.reset_ticks()
            return

      self.reset()
      
class RockThrowingPeasantChick(RockThrowingPeasant, PlayerFemale):
  # Phase out WaypointedCivilian entirely? There's a ton of C/P here
  def __init__(self, game, name, (x, y), waypoints):
    t1 = pygame.time.get_ticks()
    BasicUnit.__init__(self, game, name, 'female', (x,y))
    self.name = name
    self.anim_name = 'female'
    self.hostile = False
    self.playable = False
    self.ally = False
    self.has_special = False
    self.palette_swaps.update({(128,64,0):(64,32,0), (0,0,0):(128,64,0)})
    self.activities = ['standing', 'walking', 'falling', 'dead', 'stunned', 'throwing']
    self.equipment = []
    self.inventory = []
    self.current_activity = 'standing'
    self.animations = []
    self.current_hp = self.max_hp = 40
    self.avoidance = self.mitigation = 0
    self.waypoints = waypoints
    self.load_animations(self.palette_swaps)
    self.reset()
    t2 = pygame.time.get_ticks()
    if self.game.debug: print "Rock thrower girl load time:", t2-t1

  def load_animations(self, palette_swaps):
    PlayerFemale.load_animations(self, palette_swaps)

class ShopkeeperNPC(BasicFriendlyNPC):
  def show_dialog(self, game, unit_name):
    self.game.enable_buysell_screen(["bronze_sword", "bronze_shield", "iron_chain_mail", "chain_mail_cloak", "iron_shield",
                                "iron_sword", "white_wizard_hat", "steel_sword", "antimagic_vest"])

class MayorNPC(BasicFriendlyNPC):
  def __init__(self, game, name, (x, y)):
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.name = name
    self.anim_name = 'player'
    self.hostile = False
    self.playable = False
    self.ally = False
    self.has_special = False
    self.palette_swaps = {}
    self.equipment = [
                      equipment.Hairpiece(self.game, "Gray Hair", "hairpiece", {(0,0,0):(128,128,128)}),
                      equipment.Hairpiece(self.game, "Gray Beard", "beard", {(0,0,0):(128,128,128)}),                      
                      equipment.make(self.game, "helm_of_suck"),
                      equipment.make(self.game, "blue_tunic")
                     ]
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.current_hp = self.max_hp
    self.load_animations(self.palette_swaps)
    self.reset()
    self.quest_given = False
    
  def show_dialog(self, game, unit_name):
    self.game.show_dialog = True
    self.game.dialog_index = 0
    self.game.dialog_ticks = 25
    self.refresh_activity("talking")

    if not self.quest_given:
      self.game.dialog_boxes = [
                           self.name + ": " + unit_name.split()[0] + "! Just the person I was looking for.  I have a job for you.",
                           unit_name + ": Where's the captain of the militia?",
                           self.name + ": Ah yes, that is the job I was referring to.  " + unit_name.split()[0] + ", those monsters are all around the walls of our town.  Anybody that tries to reach us here will be in danger.",
                           self.name + ": I want you to lead a patrol around the walls and clear the area of danger.",
                           unit_name + ": Are you crazy?  I've never led a patrol!  I don't even have a full kit!",
                           self.name + ": Well... as you know, the rank of Militia Captain carries with it a fitting salary.  I can give you and your troops a month's pay in advance to equip yourselves ...",
                           self.name + ": ... plus a bonus of the same amount upon securing the area.  My brother in law SMITH the smith will give you a special deal!  What do you say, " + unit_name.split()[0] + "?",
                           unit_name + ": Sign me up. [You have received 1000 gold.]"
                          ]
    else:
      self.game.dialog_boxes = [
                           self.name + ": Better go start your patrol, Captain " + str(unit_name) + "!"
                          ]
    self.game.dialog_box = self.game.draw_dialog(self.game.dialog_boxes[self.game.dialog_index])
    
  def end_dialog(self):
    self.target_unit = None
    self.reset(self)
    if not self.quest_given:   
      self.game.score += 1000
      self.quest_given = True


class SoldierNPC(EnemyMale):
  # contains the core code for JickerNPC
  # ally = false by default, just switch it to true to make them follow you
  # usurping this class for jickers in townlol
  def __init__(self, game, name, (x, y)):
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.name = name
    self.anim_name = "player"
    self.hostile = False
    self.playable = False
    self.ally = False
    self.has_special = False
    self.palette_swaps.update({(128,64,0): (0,0,255)})
    (self.x,self.y) = (x,y)
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'stunned']
    self.equipment = [equipment.Armor(self.game, "Blue Chain Mail", "mail", self.activities, {(128,128,128):(0,0,192)}),
                      equipment.Sword(self.game, "Sword of Suck", "sword", self.activities),
                      equipment.Helm(self.game, "Blue Helmet", "helm2", self.activities, {(128,128,128):(0,0,192)}),
                     ]
    #hair
    r = random.randint(0, 192)
    g = random.randint(int(r*0.5), int(r*0.9))
    b = random.randint(int(r*0.1), int(r*0.2))
    hair = equipment.Hairpiece(self.game, 'Hair', 'hairpiece', self.activities, {(0,0,0):(r,g,b)})
    self.equipment.append(hair)
    if random.random() < 0.25:
      self.equipment.append(equipment.Beard(self.game, 'Beard', self.activities, hair.palette_swaps))
    self.current_activity = 'standing'
    self.animations = []
    self.current_hp = self.max_hp = 70
    self.avoidance = self.mitigation = 0
    self.min_damage = 3; self.max_damage = 6
    self.load_animations(self.palette_swaps)
    self.reset()
    self.flee_threshold = 0.5
  
  def show_dialog(self, unit_name):
    pass
    
  def draw_hp_bar(self, width, height, alpha=255):
    #NPCs (soldiers, jickers...)
    green_bar = pygame.Rect((1, 1, (width-2), (height-2)))
    surface = pygame.Surface((width, height))
    surface.fill((255, 255, 255))
    surface.fill((64, 128, 255), green_bar)
    hp_ratio = self.current_hp/self.max_hp
    red_left = round(hp_ratio*(width-2))+1
    red_left = max(0, red_left)
    red_width = round((1-hp_ratio)*(width-2))
    red_bar = pygame.Rect((red_left, 1, red_width, (height-2)))
    surface.fill((0, 0, 128), red_bar)
    surface.set_alpha(alpha)
    return surface
    
  def get_action(self):
    self.reset_ticks()
    self.target_unit = None
    nearest_friendly_healer = None
    nearest_friendly_ranged = None
    nearest_friendly_melee = None
    for unit in self.game.units:
      if self.game.distance((self.x,self.y),(unit.x,unit.y)) <= 15:
        if unit.hostile == self.hostile and unit != self:
          # before and after joining the party
          if (self.ally and unit.playable) or ((not self.ally) and (not unit.playable) and (not unit.ally)):
            if isinstance(unit, PlayerHealer):
              if nearest_friendly_healer == None:
                nearest_friendly_healer = unit
              elif self.game.distance((self.x,self.y),(unit.x,unit.y)) < self.game.distance((self.x,self.y),
                            (nearest_friendly_healer.x, nearest_friendly_healer.y)):
                nearest_friendly_healer = unit
            elif isinstance(unit, PlayerFemale) or isinstance(unit, PlayerArcher):
              if nearest_friendly_ranged == None:
                nearest_friendly_ranged = unit
              elif self.game.distance((self.x,self.y),(unit.x,unit.y)) < self.game.distance((self.x,self.y),(nearest_friendly_ranged.x,nearest_friendly_ranged.y)):
                nearest_friendly_ranged = unit
            else:
              if nearest_friendly_melee == None:
                nearest_friendly_melee = unit
              elif self.game.distance((self.x,self.y),(unit.x,unit.y)) < self.game.distance((self.x,self.y),(nearest_friendly_melee.x,nearest_friendly_melee.y)):
                nearest_friendly_melee = unit
    if nearest_friendly_healer:
      friendly_target = nearest_friendly_healer
    elif nearest_friendly_ranged:
      friendly_target = nearest_friendly_ranged
    else:
      friendly_target = None
    
    #move closer to friendlies, if necessary
    if friendly_target:
      if self.game.distance((self.x,self.y), (friendly_target.x,friendly_target.y)) > 10:
        self.point_at(friendly_target)
        if self.game.obstacle((self.x+self.dx, self.y+self.dy)):
          self.sidestep()
          return True
        else:
          self.refresh_activity("walking")
          return True

    #target an enemy
    for unit in self.game.units:
      if unit.hostile != self.hostile:
        if self.game.distance((self.x,self.y),(unit.x,unit.y)) <= 10:
          if self.target_unit:
            current_target = self.target_unit
            if self.game.distance((self.x,self.y), (unit.x,unit.y)) < self.game.distance((self.x,self.y), (current_target.x,current_target.y)):
              if friendly_target:
                if self.game.distance((friendly_target.x,friendly_target.y), (unit.x,unit.y)) > 10:
                  continue
              self.target_unit = unit
          else:
            self.target_unit = unit
    
    if self.target_unit:
      target_unit = self.target_unit
      if (self.current_hp/self.max_hp) > self.flee_threshold:
        self.point_at(target_unit)
        if self.game.obstacle((self.x+self.dx, self.y+self.dy)):
          if (target_unit.x, target_unit.y) == (self.x+self.dx, self.y+self.dy):
            self.refresh_activity('attacking')
          elif self.game.obstacle_unit((self.x+self.dx, self.y+self.dy)):
            unit_2 = self.game.obstacle_unit((self.x+self.dx, self.y+self.dy))
            if unit_2.hostile != self.hostile:
              self.target_unit = unit_2
              self.refresh_activity('attacking')
            else:
              self.sidestep()
          else:
            self.sidestep()
        else:
          self.refresh_activity('walking')
          self.reset_ticks()
      else: #cowardly behavior
        if nearest_friendly_healer:
          if self.game.distance((self.x,self.y), (nearest_friendly_healer.x, nearest_friendly_healer.y)) > 10: #check range of heals
            self.point_at(nearest_friendly_healer)
            if self.game.obstacle((self.x+self.dx, self.y+self.dy)):
              self.sidestep()
              return
            else:
              self.refresh_activity("walking")        
              return
        if self.game.distance((self.x,self.y),(target_unit.x,target_unit.y)) <= 4:
          self.point_at(target_unit)
          (self.dx,self.dy) = (-self.dx,-self.dy)
          if self.game.obstacle((self.x+self.dx, self.y+self.dy)):
            self.sidestep()
            return
          else:
            self.refresh_activity("walking")
            return
    else:
      if random.random() > 0.5:
        
        self.dx = random.randint(-1,1)
        self.dy = random.randint(-1,1)
        if not self.game.obstacle((self.x+self.dx,self.y+self.dy)):
          self.refresh_activity('walking')
          self.reset_ticks()
          return
      """
      if nearest_friendly_melee:
        if distance((self.x,self.y), (nearest_friendly_melee.x,nearest_friendly_melee.y)) > 5:
          self.point_at(nearest_friendly_melee) 
          if self.game.obstacle((self.x+self.dx, self.y+self.dy)):
            self.sidestep()
            return
          else:
            self.refresh_activity("walking")
            return    
     """
    
  def draw(self):
    #Need to code palette_swap_black for equipment
    self.sort_equipment()    
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    x -= 8; y -= 30
    for equip in self.equipment:
      f = equip.current_animation.get_current_filename()
      if f[len(f)-6:] == '_B.tga':
        equip.draw(x, y)
    source = self.get_current_frame()
    self.game.screen.blit(source, (x, y))
    #self.game.draw_black(self, source, (x,y))
    
    for equip in self.equipment:
      f = equip.current_animation.get_current_filename()
      if f[len(f)-6:] != '_B.tga':
        equip.draw(x, y)

    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    x += 4
    y -= 24
    self.game.screen.blit(self.draw_hp_bar(16, 5), (x,y))
    
class JickerNPC(SoldierNPC):
  def __init__(self, game, name, (x, y)):
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.hostile = False
    self.playable = False
    self.ally = True
    self.has_special = False
    self.palette_swaps.update({(128,128,64):(50,100,150), (128,64,0):(64,48,32), (128,128,0):(64,48,32), (0,64,64):(64,48,32)})
    self.equipment = [
                      equipment.make(self.game, 'jick'),
                      equipment.Hairpiece(self.game, 'Hair', 'hairpiece')
                     ]
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.current_hp = self.max_hp
    self.load_animations(self.game, self.palette_swaps)
    self.reset(self.game)

class JickerPeasant(SoldierNPC):
  #Used in town levels
  def __init__(self, game, name, (x, y)):
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.name = name
    self.anim_name = "player"
    self.hostile = False
    self.playable = False
    self.ally = False
    self.has_special = False
    self.palette_swaps.update({(128,64,0): (128,128,128)})
    (self.x,self.y) = (x,y)
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'stunned']
    self.equipment = [equipment.Spear(self.game, "Jick", "spear", self.activities,
                        {(192,192,192):(178,96,32), (85,43,0):(178,96,32), (128,128,128):(100, 60, 20)}),
                      equipment.Cloak(self.game, 'Cloak', 'cloak', self.activities,
                        {(0,0,0):(64,32,16), (128,128,128):(128,64,32), (255,0,0):(128,64,32), (255,128,64):(64,32,16)})
                     ]
    #hair
    r = random.randint(0, 192)
    g = random.randint(int(r*0.5), int(r*0.9))
    b = random.randint(int(r*0.1), int(r*0.2))
    hair = equipment.Hairpiece(self.game, 'Hair', 'hairpiece', self.activities, {(0,0,0):(r,g,b)})
    self.equipment.append(hair)
    if random.random() < 0.25:
      self.equipment.append(equipment.Beard(self.game, 'Beard', self.activities, hair.palette_swaps))
    self.current_activity = 'standing'
    self.animations = []
    self.current_hp = self.max_hp = 70
    self.avoidance = self.mitigation = 0
    self.min_damage = 3; self.max_damage = 5
    self.load_animations(self.palette_swaps)
    self.reset()
    self.flee_threshold = 0.75
    
class PlayerFemaleMeleeNPC(PlayerFemaleMelee):
  def __init__(self, game, name, (x, y)):
    PlayerFemaleMelee.__init__(self, game, name, (x, y))
    self.playable = False
    self.ally = False

  def show_dialog(self, unit_name):
    self.game.show_dialog = True
    self.game.dialog_boxes = [self.name + ": HELO HOW RU?\n[" + self.name + " has joined your party.]"
                        ]
    self.game.dialog_index = 0
    self.game.dialog_ticks = int(len(self.game.dialog_boxes[self.game.dialog_index])/2)
    self.game.dialog_box = self.game.draw_dialog(self.game.dialog_boxes[self.game.dialog_index])
    self.refresh_activity("talking")
    
  def end_dialog(self):
    self.playable = True
    self.target_unit = None
    self.reset(self)