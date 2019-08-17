from __future__ import division
import pygame
from functions import *
from classes import *

import equipment
import os
import random
import language

class BasicUnit:
    def __init__(self, game, name, anim_name, (x,y)):
      self.name = name
      self.anim_name = anim_name
      self.x = x
      self.y = y
      self.dx = 0
      self.dy = -1
      self.selected = False
      self.selected_in_menu = False
      self.level = 1 #!!!
      self.target_x = self.target_y = self.target_unit = None
      # This shouldn't really be here, but I guess it's better than c&ping it to all humans
      skin_colors = [(251,172,94), (253,177,128), (255,128,64), (197,156,73), (153,129,70), (151,90,36)]
      eye_colors = [(0,192,0), (0,0,192), (0,128,192), (128,64,0), (128,128,128), (64,192,64)]
      lip_colors = [(128,0,0), (81,0,0), (146,43,55), (129,59,38), (204,116,118), (180,115,133)]
      self.palette_swaps = {
                            (255,128,64):random.choice(skin_colors),
                            (0,64,64):random.choice(eye_colors),
                            (128,0,0):random.choice(lip_colors)
                           }
      
    def move(self, (dx, dy)):
      """
      Increment the NPC's coordinates by (dx, dy).  No checking!
      """
      self.x += dx
      self.y += dy

    def increment_ticks(self):
      self.ticks += 1

    def refresh_animation(self, game, directions):
      """ Find the animation that matches current activity & direction, and queue it up. """
      """ Queue is a misnomer... """
      for anim in self.animations:
        if anim.activity == self.current_activity and anim.directions == directions:
          self.current_animation = anim
          self.current_animation.findex = 1
      for equip in self.equipment:
        equip.set_animation(game, self.current_activity, directions)

    def knockback(self, game, (dx, dy)):
      """ Push SELF back """
      if not obstacle(game, (self.x+dx, self.y+dy)):
        self.x += dx
        self.y += dy

    def get_current_frame(self):
        """ Retrieve the current animation frame. """
        return self.current_animation.get_current_frame()
    
    def next_frame(self, game):
      """ Iterates frame index of self and equipment. """
      for x in self.equipment + [self]:
        x.current_animation.next_frame()

    def take_damage(self, game, damage, magic=False):
      if magic:
        self.current_hp = max(0, self.current_hp - damage)
      else:
        if random.random() > self.avoidance:
          self.current_hp = max(0, self.current_hp - int(damage*(1-self.mitigation)))
        else:
          self.play_block_sound()

      if self.current_hp <= 0 and self.current_activity not in ['falling', 'decapitated', 'dead', 'dead_decapitated']:
        self.current_hp = 0
        self.refresh_activity(game, 'falling')
        self.reset_ticks()
        self.scream()

    def draw(self, game):
      (x,y) = grid_to_pixel(game, self.x, self.y)
      x -= 8; y -= 30
      self.sort_equipment()
      for equip in self.equipment:
        f = equip.current_animation.get_current_filename()
        if f[len(f)-6:] == '_B.tga':
          equip.draw(game, x, y)
      source = self.get_current_frame()
      game.screen.blit(source, (x, y))
      for equip in self.equipment:
        f = equip.current_animation.get_current_filename()
        if f[len(f)-6:] != '_B.tga':
          equip.draw(game, x, y)

    def draw_in_place(self, game, (x,y)):
      #Draws the unit standing, for the menu screen
      #(x,y) are PIXELS
      surface = pygame.surface.Surface((40,40))
      surface.fill((255,255,255))
      surface.set_colorkey((255,255,255))
      self.sort_equipment()
      for equip in self.equipment:
        for anim in equip.animations:
          if anim.directions == ["SE"] and anim.activity == "standing":
            f = anim.filenames[0]
            if f[len(f)-6:] == '_B.tga':
              source = anim.frames[0]
              if isinstance(equip, equipment.Spear):
                surface.blit(source, (-10,-20))
              else:
                surface.blit(source, (0,0))
      for anim in self.animations:
        if anim.directions == ["SE"] and anim.activity == "standing":
          source = anim.frames[0]
          surface.blit(source, (0,0))
          break
      for equip in self.equipment:
        for anim in equip.animations:
          if anim.directions == ["SE"] and anim.activity == "standing":
            f = anim.filenames[0]
            if f[len(f)-6:] != '_B.tga':
              source = anim.frames[0]
              if isinstance(equip, equipment.Spear):
                surface.blit(source, (-10,-20))
              else:
                surface.blit(source, (0,0))
      surface2 = surface.subsurface(pygame.Rect(8,9,24,31))
      surface2.set_colorkey((255,255,255))
      game.screen.blit(surface2, (x, y))

    def get_z(self):
      #to determine overlaps
      return 6*self.x + 6*self.y + 2
        
    def get_rect(self, game):
      (left, top) = grid_to_pixel(game, self.x, self.y)#might be wrong offset
      top -= 16 
      rect = self.get_current_frame().get_rect()
      (width, height) = (rect.width, rect.height)
      return pygame.Rect(left, top, width, height)
      
    def get_center(self, game):
      return grid_to_pixel(game, self.x, self.y)
      
    def refresh_activity(self, game, activity, directions = []):
      self.current_activity = activity
      if directions:
        self.refresh_animation(game, directions)
      else:
        self.refresh_animation(game, [coords_to_dir((self.dx, self.dy))])
            
    def reset_ticks(self):
      self.ticks = 0
        
    def draw_hp_bar(self, width, height, alpha=255):
      #BasicUnit, used by all player units (in cards)
      green_bar = pygame.Rect((1, 1, (width-2), (height-2)))
      surface = pygame.Surface((width, height))
      surface.fill((255, 255, 255))
      surface.fill((0, 255, 0), green_bar)
      hp_ratio = self.current_hp/self.max_hp
      red_left = round(hp_ratio*(width-2))+1
      red_width = round((1-hp_ratio)*(width-2))
      red_bar = pygame.Rect((red_left, 1, red_width, (height-2)))
      surface.fill((0, 128, 0), red_bar)
      surface.set_alpha(alpha)
      return surface

    def draw_cooldown_bar(self, width, height):
      deficit = round((self.max_special_ticks-self.special_ticks)/self.max_special_ticks*(width-2))
      deficit = min(width-2, deficit)
      left = (width - 2) - deficit
      yellow_bar = pygame.Rect((1, 1), ((width-2), height-2))
      surface = pygame.Surface((width, height))
      surface.fill((255,255,255))
      surface.fill((255,255,0), yellow_bar)
      black_bar = pygame.Rect((left+1, 1), (deficit, height-2))
      surface.fill((128,128,0), black_bar)
      return surface

    def damage(self):
      return random.randint(self.min_damage, self.max_damage)
      
    def point_at_OLD(self, game, target):
      squares = adjacent_squares((self.x, self.y))
      squares.sort(lambda a,b: distance_sort_posn(a,b,(target.x,target.y)))
      for square in squares:
        if square == (target.x, target.y):
          self.dx = square[0] - self.x
          self.dy = square[1] - self.y
          return True
        elif not obstacle(game, square):
          self.dx = square[0] - self.x
          self.dy = square[1] - self.y
          return True
    
    def point_at(self, target):
      (dx,dy) = (target.x-self.x, target.y-self.y)
      m = (dx**2 + dy**2)**0.5
      if m != 0:
        (self.dx, self.dy) = (round(dx/m), round(dy/m))
              
    def sort_equipment(self):
      sorted_equipment = []
      if self.current_activity == 'standing' and self.current_animation.directions[0] in ["E", "SE", "S"]:
        for slot in ["shield", "weapon", "head", "hair", "beard", "chest", "cloak"]:
          for equip in self.equipment:
            if equip.slot == slot:
              sorted_equipment.append(equip)
              break
      elif self.current_activity == 'standing' and self.current_animation.directions[0] in ["NE"]:
        for slot in ["weapon", "shield", "head", "hair", "beard", "chest", "cloak"]:
          for equip in self.equipment:
            if equip.slot == slot:
              sorted_equipment.append(equip)
              break
      elif self.current_activity == 'walking' and self.current_animation.directions[0] in ["E"]:
        for slot in ["weapon", "shield", "head", "hair", "beard", "chest", "cloak"]:
          for equip in self.equipment:
            if equip.slot == slot:
              sorted_equipment.append(equip)
              break              
      else:
        for slot in ["shield", "weapon", "head", "hair", "beard", "cloak", "chest"]:
          for equip in self.equipment:
            if equip.slot == slot:
              sorted_equipment.append(equip)
              break
      sorted_equipment.reverse()
      self.equipment = sorted_equipment
      
    def bleed(self, game, damage):
      game.blood.append(Blood(self.x, self.y, damage*2))

class PlayerMale (BasicUnit):
  def __init__(self, game, name, (x, y)):
    t1 = pygame.time.get_ticks()
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.hostile = False
    self.playable = True
    self.ally = False
    self.has_special = True
    self.special_activity_name = 'bashing'
    self.has_secondary_special = True
    self.secondary_special_activity_name = 'slashing'
    self.special_ticks = self.max_special_ticks = 60
    clothes_colors = [(128,0,0), (0,128,0), (0,0,128), (128,128,64),
                    (64,64,64), (128,128,128)]
    belt_colors = [(64,64,64), (128,64,0)]
    self.palette_swaps.update({(128,128,64):random.choice(clothes_colors), #shirt
                               (128,64,0):random.choice(clothes_colors), #pants
                               (128,128,0):random.choice(belt_colors)}) #belt
    self.equipment = [equipment.make(game, 'tower_shield'),
                      equipment.make(game, 'helm_of_suck'),
                      equipment.make(game, 'sword_of_suck')]
    hairpiece = equipment.Hairpiece(game, 'Hair', 'hairpiece')
    self.equipment.append(hairpiece)
    if random.random() <= 0.25:
      self.equipment.append(equipment.Beard(game, 'Beard', hairpiece.palette_swaps))
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'bashing', 'falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned', 'slashing']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.avoidance = 0.3
    self.mitigation = 0
    self.min_damage = 6
    self.max_damage = 8
    self.current_hp = self.max_hp
    self.load_animations(game, self.palette_swaps)
    self.reset(game)
    t2 = pygame.time.get_ticks()
    print "Playermale load time:", t2-t1, "ms"

  def get_attack_targets(self, game):
    attack_directions = self.current_animation.directions
    targets = []
    for dir in attack_directions:
      (dx, dy) = dir_to_coords(dir)
      for target_unit in game.units:
        if (target_unit.x, target_unit.y) == (self.x + dx, self.y + dy):
          if target_unit.hostile != self.hostile:
            if target_unit.current_hp > 0 and target_unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
              targets.append(target_unit)
    return targets

  def increment_ticks(self):
    self.ticks += 1
    if self.has_special:
      if self.special_ticks < self.max_special_ticks:
        self.special_ticks += 1
    
  def reset_spell_ticks(self):
    self.current_spell.ticks = 0
  
  def do_events(self, game):
    self.next_frame(game)
    for unit in game.units:
      if unit.name != self.name:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep(game)

    if self.current_activity == 'walking':
      if self.ticks == 2:
        for unit in game.units:
          if (unit.x,unit.y) == (self.x+self.dx,self.y+self.dy):
            if unit.hostile == self.hostile:
              if unit.current_activity == 'standing':
                if unit.name != self.target_unit:
                  unit.knockback(game,(self.dx,self.dy))
        if obstacle(game, (self.x+self.dx, self.y+self.dy)):
          self.sidestep(game)
        else:
          self.move((self.dx, self.dy))
          game.redraw_floor = True
      elif self.ticks == 4:
        self.reset(game)
        
    elif self.current_activity == 'standing':
      if self.ticks == 4:
        self.reset(game)
        
    elif self.current_activity == 'attacking':
      if self.ticks == 4:
        self.end_attack(game)
      elif self.ticks == 8:
        self.reset(game)
        
    elif self.current_activity == 'bashing':
      if self.ticks == 4:
        self.end_bash(game)
      elif self.ticks == 8:
        self.reset(game)

    elif self.current_activity == 'falling':
      if self.ticks == 8:
        self.refresh_activity(game, 'dead')
        game.corpses.append(Corpse(game, self))
        self.selected = False
        for unit in game.units:
          if unit.target_unit == self.name:
            unit.target_unit = None
        game.units.remove(self)
        return
        
    elif self.current_activity == 'slashing':
      #We need to spread out the damage, add knockbacks, etc.
      if self.ticks < 9:
        self.mid_slash(game)
      if self.ticks == 10:
        self.reset(game)
        self.special_ticks = 0
        
    elif self.current_activity == 'stunned':
      if self.ticks == 16:
        self.reset(game)
    
    if self.ticks >= 16:
      print "Sword failsafe"
      self.reset(game)
        
    if self.ticks == 0:
      if self.current_activity in ['bashing', 'slashing']: #weird
        pass
      else:
        self.get_action(game)
      
  def load_animations(self, game, palette_swaps = {}):
    # Also used by spearguy, healer, archer, etc. So it includes
    # animations for their specials too.
    frames_surfaces = {}
    for activity in self.activities:
      for dir in game.directions:
        frames = []
        frame_surfaces = []
        if activity == 'walking':
          for x in [1,1,2,2]:
            frames.append('tga/' + self.anim_name + '_walking_' + dir + '_' + str(x) + '.tga')
        elif activity == 'standing':
          for n in range(4):
            frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
            frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'attacking':
          for x in [1,1,2,2,1,1]:
            frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_' + str(x) + '.tga')
          frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
          frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'charging':
          for n in range(10):
            frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_2.tga')
        elif activity == 'shooting': #originally A1 > A2b > A2b > S1
          for x in ['1','1','2b','2b','2b','2b','1','1']:
            frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_' + x + '.tga')
          for n in range(8):
            frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'throwing': #originally A1 > A2b > A2b > S1
          for x in ['1','1','2b','2b','2b','2b','1','1']:
            frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_' + x + '.tga')
          for n in range(8):
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
        elif activity == 'bashing':
          for x in ['1','1','2b','2b','1','1']:
            frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_' + str(x) + '.tga')
          frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
          frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'taunting': #Unused
          for x in ['attacking_1', 'standing_1']:
            for n in range(2):
              frames.append('tga/' + self.anim_name + '_' + x + '.tga')
        elif activity == 'falling':
          if dir in ['S', 'SW', 'W']:
            anim_dir = 'S'
          elif dir in ['NW', 'SE']:
            anim_dir = 'NW'
          elif dir in ['N', 'NE', 'E']:
            anim_dir = 'NE'
          for x in [1,2,3,4,4]: #to compensate for the buggy falling behavior - KLUDGE
            for n in range(2):
              frames.append('tga/' + self.anim_name + '_falling_' + anim_dir + '_' + str(x) + '.tga')
        elif activity == 'dead':
          if dir in ['S', 'SW', 'W']:
            anim_dir = 'S'
          elif dir in ['NW', 'SE']:
            anim_dir = 'NW'
          elif dir in ['N', 'NE', 'E']:
            anim_dir = 'NE'
          frames.append('tga/' + self.anim_name + '_falling_' + anim_dir + '_4.tga')
        elif activity == 'decapitated':
          if dir in ['S', 'SW', 'W']:
            anim_dir = 'S'
          elif dir in ['NW', 'SE']:
            anim_dir = 'NW'
          elif dir in ['N', 'NE', 'E']:
            anim_dir = 'NE'
          for x in [1,2,3,4]:
            for n in range(2):
              frames.append('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_' + str(x) + '.tga')
        elif activity == 'dead_decapitated':
          if dir in ['S', 'SW', 'W']:
            anim_dir = 'S'
          elif dir in ['NW', 'SE']:
            anim_dir = 'NW'
          elif dir in ['N', 'NE', 'E']:
            anim_dir = 'NE'
          frames.append('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_4.tga')
     
        elif activity == 'stunned':
          anim_directions = get_slash_directions(game, dir)
          for d in anim_directions:
            for n in range(2):          
              frame = 'tga/' + self.anim_name + '_standing_' + d + '_1.tga'
              frames.append(frame)
        # now we load from filenames
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

  def end_attack(self, game):
    target_unit = game.unit_by_name(self.target_unit)
    if not target_unit:
      self.reset(game)
      return False
    else:  
      can_decapitate = False
      for equip in self.equipment:
        if equip.anim_name in ['sword', 'sword2']:
          can_decapitate = True
      if 'decapitated' not in target_unit.activities:
        can_decapitate = False
      dmg = self.damage()
      if can_decapitate and target_unit.current_activity not in ['falling','dead','decapited','dead_decapitated'] and target_unit.current_hp > 0 and target_unit.current_hp <= dmg*2 and random.random() > 0.05:
        target_unit.bleed(game, target_unit.current_hp*2)
        target_unit.current_hp = 0
        target_unit.reset(game)
        target_unit.refresh_activity(game, 'decapitated')
        self.play_hit_sound()        
      else:
        target_unit.take_damage(game, dmg)
        target_unit.bleed(game, dmg)
        if target_unit.current_hp > 0:
          self.play_hit_sound()
        
  def end_bash(self, game):
    target_unit = game.unit_by_name(self.target_unit)
    if not target_unit:
      self.reset(game)
      return False
    else:
      dmg = 10 #Test this value!
      target_unit.take_damage(game, dmg)
      target_unit.bleed(game, dmg)
      self.play_bash_sound()
      self.special_ticks = 0
      if (target_unit.anim_name == 'zombie') or (target_unit.anim_name == 'player') \
      or ((target_unit.anim_name == 'robed_wizard') and (target_unit.current_activity in ['casting', 'teleporting'])):
        if target_unit.current_activity not in ['falling', 'dead']:
          for n in range(2):
            self.knockback(game, (self.dx, self.dy))
            target_unit.knockback(game, (self.dx, self.dy))
          game.redraw_floor = True
          target_unit.refresh_activity(game, 'stunned')
          target_unit.reset_ticks()
          
  def mid_slash(self, game):
    dir = coords_to_dir((self.dx, self.dy))
    for n in range(self.ticks-1):
      dir = rcw(dir)
    (dx,dy) = dir_to_coords(dir)
    (x,y) = (self.x + dx,self.y + dy)
    target_unit = obstacle_unit(game, (x,y))
    if target_unit:
      if self.hostile != target_unit.hostile:
        dmg = self.damage()*3
        target_unit.take_damage(game, dmg)
        (dx,dy) = (target_unit.x - self.x, target_unit.y - self.y)
        knockback_length = 1
        (dx,dy) = (dx*knockback_length,dy*knockback_length)
        target_unit.knockback(game, (dx,dy))
        target_unit.refresh_activity(game, 'stunned')
            
  def play_hit_sound(self):
    filenames = ["sounds/sword on armor.ogg", "sounds/sword on flesh.ogg"]
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(False)
    if channel:
      channel.play(sound)
      
  def play_bash_sound(self):
    filename = "sounds/shieldbash.ogg"
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(False)
    if channel:
      channel.play(sound)
      
  def play_block_sound(self):
    filenames = ["sounds/sword on armor.ogg", 'sounds/sword on sword.ogg', 'sounds/sword on shield 2.ogg']
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(False)
    if channel:
      channel.play(sound)
          
  def play_swish_sound(self):
    #Unused? Possibly for misses
    filenames = ["sounds/sword swish.ogg"]
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(False)
    if channel:
      channel.play(sound)
      
  def play_slash_sound(self):
    filenames = ["sounds/slash2.ogg"]
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(True)
    if channel:
      channel.play(sound)
  
  def scream(self):
    filenames = ["sounds/scream.ogg", "sounds/grunt.ogg"]
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(True)
    channel.play(sound)

  def reset(self, game):
    self.refresh_activity(game, 'standing')
    self.reset_ticks()
        
  def get_action(self, game):
    # PlayerMale
    adjacent_enemy_units = []
    for square in adjacent_squares((self.x, self.y)):
      for unit in game.units:
        if (unit.x, unit.y) == square and unit.hostile != self.hostile:
          adjacent_enemy_units.append(unit.name)
          
    if self.target_unit:
      self.move_to_target_unit(game)
      
    elif (self.target_x, self.target_y) != (None, None):
      self.move_to_target_posn(game)
      
    elif adjacent_enemy_units:
      self.target_unit = random.choice(adjacent_enemy_units)
      self.move_to_target_unit(game)
    
  def move_to_target_unit(self, game):
    target_unit = game.unit_by_name(self.target_unit)
    if not target_unit:
      self.target_unit = None
      return
     
    dx = target_unit.x - self.x
    dy = target_unit.y - self.y
    if (dx, dy) == (0,0):
      self.reset(game)
      self.dx = random.randint(-1,1)
      self.dy = random.randint(-1,1)
      return
    else:
      m = (dx**2 + dy**2)**0.5
      if m != 0:
        (self.dx, self.dy) = (round(dx/m), round(dy/m))
    for unit in game.units:
      if unit != target_unit:
        if unit.hostile == self.hostile:
          if (unit.x,unit.y) == (self.x+self.dx,self.y+self.dy):
            if unit.current_activity == 'standing':
              if unit.name != self.target_unit:
                unit.knockback(game, (self.dx,self.dy))
    
    if target_unit.hostile != self.hostile:
      if (target_unit.x, target_unit.y) == (self.x + self.dx, self.y + self.dy):    
        self.refresh_activity(game, 'attacking')
        self.reset_ticks()
        return
        
    elif not target_unit.playable:
      if (target_unit.x, target_unit.y) == (self.x + self.dx, self.y + self.dy):
        self.refresh_activity(game, 'talking')
        self.reset_ticks()
        target_unit.show_dialog(game, self.name)
        return
      elif obstacle(game, (self.x + self.dx, self.y + self.dy)):
        if distance((self.x,self.y), (target_unit.x, target_unit.y)) < 3: #longer distance for bars
          self.refresh_activity(game, 'talking')
          self.reset_ticks()
          target_unit.show_dialog(game, self.name)
          return
          
    if not obstacle(game, (self.x + self.dx, self.y + self.dy)):
      self.refresh_activity(game, 'walking')
      self.reset_ticks()
      return
    elif obstacle(game, (self.x + self.dx, self.y + self.dy)):
      if (self.x + dx, self.y + self.dy) == (self.target_x, self.target_y):
        self.reset(game)
      else:
        self.sidestep(game)
        
  def move_to_target_unit_special(self, game, secondary=False):
    # defaults to shield bash
    # can be used for slash attack
    if secondary:
      activity_name = self.secondary_special_activity_name
    else:
      activity_name = self.special_activity_name
    target_unit = game.unit_by_name(self.target_unit)
    if not target_unit:
      self.target_unit = None
      return
     
    dx = target_unit.x - self.x
    dy = target_unit.y - self.y
    if (dx, dy) == (0,0):
      self.reset(game)
      self.dx = random.randint(-1,1)
      self.dy = random.randint(-1,1)
      return
    m = (dx**2 + dy**2)**0.5
    if m != 0:
      (self.dx, self.dy) = (round(dx/m), round(dy/m))
    dist = distance((self.x,self.y), (target_unit.x,target_unit.y))
    if target_unit.hostile:
      if dist <= 2:
        self.refresh_activity(game, activity_name)
        if activity_name == 'slashing':
          self.play_slash_sound()
        self.reset_ticks()
        return
    if not obstacle(game, (self.x + self.dx, self.y + self.dy)):
      self.refresh_activity(game, 'walking')
      self.reset_ticks()
      #at this point, we lose the intention to perform the special attack
      return
    elif obstacle(game, (self.x + self.dx, self.y + self.dy)):
      if (self.x + dx, self.y + self.dy) == (self.target_x, self.target_y):
        self.reset(game)
      else:
        self.sidestep(game)
        
  def move_to_target_posn(self, game):
    dx = self.target_x - self.x
    dy = self.target_y - self.y
    if (dx, dy) == (0,0):
      (self.target_x, self.target_y) = (None, None)
      self.reset(game)
      return True
    m = (dx**2 + dy**2)**0.5
    if m != 0:
      (self.dx, self.dy) = (round(dx/m), round(dy/m))
    target = obstacle_unit(game, (self.x+self.dx, self.y+self.dy))
    if target:
      if (target.x, target.y) == (self.target_x, self.target_y):
        if target.hostile != self.hostile:
          self.refresh_activity(game, 'attacking')
        else:
          if target.current_activity == 'standing':
            target.knockback(game, (self.dx,self.dy))
      else:
        self.sidestep(game)
    elif obstacle(game, (self.x+self.dx, self.y+self.dy)):
      self.sidestep(game)
    else:
      self.refresh_activity(game, 'walking')
      self.reset_ticks()
  
  def sidestep_OLD(self, game):
    if not coords_to_dir((self.dx, self.dy)):
      (self.dx,self.dy) = dir_to_coords(random.choice(game.directions))
      
    min_distance = 5
    (target_dx,target_dy) = (None,None)
    for dir in game.directions:
      (dx, dy) = dir_to_coords(dir)
      if not obstacle(game, (self.x+dx, self.y+dy)):
        if distance((self.x+dx, self.y+dy), (self.x+self.dx,self.y+self.dy)) < min_distance:
          (target_dx,target_dy) = (dx,dy)
          min_distance = distance((self.x+dx, self.y+dy), (self.x+self.dx,self.y+self.dy))
    if (target_dx,target_dy) != (None, None):
      (self.dx, self.dy) = (target_dx,target_dy)
      self.refresh_activity(game, 'walking')
      return True
    else:
      return False
  
  def sidestep(self, game):
    if not coords_to_dir((self.dx, self.dy)):
      (self.dx,self.dy) = dir_to_coords(random.choice(game.directions))
    distance_dict = {}
    for dir in game.directions:
      (dx, dy) = dir_to_coords(dir)
      if not obstacle(game, (self.x+dx,self.y+dy)):      
        distance_dict[(dx,dy)] = distance((self.x+dx, self.y+dy), (self.x+self.dx,self.y+self.dy))
    if len(distance_dict) == 0:
      print self.name, 'sidestep error: no valid directions'
      return False
    distance_dict = sorted(distance_dict, key=(lambda k: distance_dict[k]))
    (target_dx,target_dy) = random.choice(distance_dict[:2])
    if (target_dx,target_dy) != (None, None):
      (self.dx, self.dy) = (target_dx,target_dy)
      self.move((self.dx,self.dy))
      self.reset(game)
      return True
    else:
      print 'sidestep error misc'
      return False
      
class PlayerFemale(PlayerMale):
  # AKA DartGirl
  def __init__(self, game, name, (x,y)):
    BasicUnit.__init__(self, game, name, 'female', (x,y))  
    self.hostile = False
    self.playable = True
    self.ally = False
    self.has_special = False
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
    self.palette_swaps.update({(79,39,0):random.choice(hair_colors)})
    self.equipment = []
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.current_hp = self.max_hp
    self.load_animations(game, self.palette_swaps)
    self.reset(game)
    
  def increment_ticks(self):
    self.ticks += 1

  def load_animations(self, game, palette_swaps = {}):
    """
    Loads animations automatically, referring to strict naming conventions.
    """
    for activity in self.activities:
        for dir in game.directions:
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
            elif activity == 'falling':
              if dir in ['N', 'NE', 'E', 'SE']:
                frames.append('tga/' + self.anim_name + '_falling_1.tga')
                frames.append('tga/' + self.anim_name + '_falling_2.tga')
                frames.append('tga/' + self.anim_name + '_falling_3.tga')
                frames.append('tga/' + self.anim_name + '_falling_3.tga')
              else:
                frames.append('tga/' + self.anim_name + '_fallingB_1.tga')
                frames.append('tga/' + self.anim_name + '_fallingB_2.tga')
                frames.append('tga/' + self.anim_name + '_fallingB_3.tga')
                frames.append('tga/' + self.anim_name + '_fallingB_3.tga')
            elif activity == 'dead':
              if dir in ['N', 'NE', 'E', 'SE']:
                frames.append('tga/' + self.anim_name + '_falling_3.tga')
              else:
                frames.append('tga/' + self.anim_name + '_fallingB_3.tga')
            else:
              for x in xrange(1, 5):
                frames.append(self.anim_name + '_' + activity + '_' + dir + '_' + str(x) + '.tga')
            for frame in frames:
              surface = pygame.image.load(frame)
              surface = palette_swap_multi(surface, palette_swaps)
              surface.set_colorkey((255,255,255))
              frame_surfaces.append(surface)
            self.animations.append(Animation(activity, [dir], frame_surfaces, frames))    

  def scream(self):
    filenames = ["sounds/Girl Scream.ogg", "sounds/Girl Scream2.ogg"]
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(True)
    channel.play(sound)
    
  def get_action(self, game):
    # PlayerFemale
    adjacent_enemy_units = []
    for square in adjacent_squares((self.x, self.y)):
      for unit in game.units:
        if (unit.x, unit.y) == square and unit.hostile != self.hostile:
          adjacent_enemy_units.append(unit.name)
          
    if self.target_unit:
      self.move_to_target_unit(game)
      
    elif (self.target_x, self.target_y) != (None, None):
      self.move_to_target_posn(game)
    else:
      #Auto-acquire a nearby target
      min_distance = self.max_distance
      for unit in game.units:
        if unit.hostile != self.hostile and distance((self.x, self.y), (unit.x, unit.y)) < 5:
          if distance((self.x,self.y), (unit.x,unit.y)) < min_distance:
            self.target_unit = unit.name
            min_distance = distance((self.x, self.y), (unit.x, unit.y))
          self.target_unit = unit.name
      if self.target_unit:
        self.move_to_target_unit(game)
      
  def do_events(self, game):
    """ Player Female """
    self.next_frame(game)    
    for unit in game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep(game)
          self.move((self.dx, self.dy))
          self.reset(game)
    if self.target_unit:
      target_unit = game.unit_by_name(self.target_unit)
      if target_unit == None:
        self.target_unit = None
        return False
      if target_unit.current_hp <= 0 and target_unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
        target_unit.reset(game)
        target_unit.refresh_activity(game, 'falling')
    if self.ticks == 1:
      if self.current_activity == 'walking':
        for unit in game.units:
          if (unit.x,unit.y) == (self.x+self.dx,self.y+self.dy):
            if unit.hostile == self.hostile:
              if not unit.playable:
                if unit.ally:
                  unit.knockback(game,(self.dx,self.dy))    
        if obstacle(game, (self.x+self.dx, self.y+self.dy)):
          self.sidestep(game)
        else:
          self.move((self.dx, self.dy))
    if self.ticks == 2:
      if self.current_activity == 'walking':
        self.reset(game)
      if self.current_activity == 'standing':
        self.reset(game)
      if self.current_activity == 'attacking':
        game.darts.append(Dart(game, 10, self.name, self.target_unit))
        
    if self.ticks == 4:
      if self.current_activity == 'attacking':
        self.reset(game)
      elif self.current_activity == 'falling':
        self.refresh_activity(game, 'dead')
        game.corpses.append(Corpse(game, self))
        self.selected = False
        for unit in game.units:
          if unit.target_unit == self.name:
            unit.target_unit = None
        game.units.remove(self)
        return True
      else:
        self.reset(game)
        
    if self.ticks == 0:
      self.get_action(game)
    
  def move_to_target_unit(self, game):
    target_unit = game.unit_by_name(self.target_unit)
    if not target_unit:
      self.target_unit = None
      return False
     
    dx = target_unit.x - self.x
    dy = target_unit.y - self.y
    if (dx, dy) == (0,0):
      self.reset(game)
      self.dx = random.randint(-1,1)
      self.dy = random.randint(-1,1)     
    else:      
      m = (dx**2 + dy**2)**0.5
      if m != 0:
        (self.dx, self.dy) = (round(dx/m), round(dy/m))
    # NPC!
    if (not target_unit.playable) and (not target_unit.hostile) and (not target_unit.ally):
      if (self.x+self.dx, self.y+self.dy) == (target_unit.x,target_unit.y):
        self.refresh_activity(game, 'talking')
        target_unit.show_dialog(game, self.name)
      elif obstacle(game, (self.x+self.dx,self.y+self.dy)):
        self.sidestep(game)
      else:
        self.refresh_activity(game, 'walking')
        self.reset_ticks()
    elif target_unit.hostile:

      dist = distance((self.x,self.y), (target_unit.x,target_unit.y))
      if dist >= 4 and dist <= 10:
        self.refresh_activity(game, 'attacking')
        self.reset_ticks()
      else:
        if dist < 4:
          (self.dx, self.dy) = (-self.dx, -self.dy)
        if not obstacle(game, (self.x + self.dx, self.y + self.dy)):
          self.refresh_activity(game, 'walking')
          self.reset_ticks()          
        elif obstacle(game, (self.x + self.dx, self.y + self.dy)):
          if (self.x + dx, self.y + self.dy) == (self.target_x, self.target_y):
            self.reset(game)
          else:
            self.sidestep(game)
    
class AltPlayerMale(PlayerMale):
  def __init__(self, game, name, (x, y)):
    t1 = pygame.time.get_ticks()
    BasicUnit.__init__(self, game, name, 'player', (x,y))  
    self.hostile = False
    self.playable = True
    self.ally = False
    self.has_special = True
    self.special_activity_name = 'charging'
    self.has_secondary_special = False #add this later!
    self.secondary_special_activity_name = 'taunting'
    self.special_ticks = self.max_special_ticks = 60
    clothes_colors = [(128,0,0), (0,128,0), (0,0,128), (128,128,64),
                    (64,64,64), (128,128,128)]
    belt_colors = [(64,64,64), (128,64,0)]
    self.palette_swaps.update({(128,128,64):random.choice(clothes_colors), #shirt
                               (128,64,0):random.choice(clothes_colors), #pants
                               (128,128,0):random.choice(belt_colors)}) #belt
    self.equipment = [
                      equipment.make(game, 'spear'),
                      equipment.make(game, 'wooden_shield'),
                     ]
    hairpiece = equipment.Hairpiece(game, 'Hair', 'hairpiece')
    self.equipment.append(hairpiece)
    if random.random() <= 0.25:
      self.equipment.append(equipment.Beard(game, 'Beard', hairpiece.palette_swaps))
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned', 'charging']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.current_hp = self.max_hp
    self.load_animations(game, self.palette_swaps)
    self.reset(game)
    self.avoidance = 0.3
    self.mitigation = 0
    self.min_damage = 6
    self.max_damage = 10
    t2 = pygame.time.get_ticks()
    print "Altplayermale load time:", t2-t1, "ms"    
    
  def get_attack_targets(self, game):
    target_unit = game.unit_by_name(self.target_unit)
    if target_unit:
      return [target_unit]
    else:
      return None
      
  def end_attack(self, game):
    target_unit = game.unit_by_name(self.target_unit)
    if not target_unit:
      self.reset(game)
      return False
    else:
      dmg = self.damage()
      target_unit.take_damage(game, dmg)
      target_unit.bleed(game, dmg)
      self.play_hit_sound()
      
  def do_charge_damage(self, game):
    target_unit = game.unit_by_name(self.target_unit)
    if not target_unit:
      self.reset(game)
      return False
    else:
      dmg = 3
      target_unit.take_damage(game, dmg)
      target_unit.bleed(game, dmg)
    
  def get_action(self, game):
    """ Alt Player [Spear Guy] """
    adjacent_enemy_units = []
    #Radius 2
    for unit in game.units:
      if unit.hostile != self.hostile:
        if distance((self.x,self.y),(unit.x, unit.y)) <= 2:
          adjacent_enemy_units.append(unit.name)
          
    if self.current_activity == 'charging':
      if self.target_unit:
        self.charge_at_unit(game)
      else:
        self.reset(game)
        #print 'bad spearman'
    elif self.target_unit:
      self.move_to_target_unit(game)
      
    elif (self.target_x, self.target_y) != (None, None):
      self.move_to_target_posn(game)
      
    elif adjacent_enemy_units:
      self.target_unit = random.choice(adjacent_enemy_units)
      self.move_to_target_unit(game)
      
  def do_events(self, game):
    self.next_frame(game)
    for unit in game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep(game)
    
    if self.current_activity == 'walking':
      if self.ticks == 2:
        for unit in game.units:
          if (unit.x,unit.y) == (self.x+self.dx,self.y+self.dy):
            if unit.hostile == self.hostile:
              if unit.current_activity == 'standing':
                if unit.name != self.target_unit:
                  unit.knockback(game,(self.dx,self.dy))
        if obstacle(game, (self.x+self.dx, self.y+self.dy)):
          self.sidestep(game)
        else:
          self.move((self.dx, self.dy))
          game.redraw_floor = True
      elif self.ticks == 4:
        self.reset(game)
        
    if self.current_activity == 'standing':
      if self.ticks == 4:
        self.reset(game)

    elif self.current_activity == 'attacking':
      if self.ticks == 4:
        self.end_attack(game)
      elif self.ticks == 8:
        self.reset(game)
        
    elif self.current_activity == 'falling':
      if self.ticks == 8:      
        self.refresh_activity(game, 'dead')
        game.corpses.append(Corpse(game, self))
        self.selected = False
        for unit in game.units:
          if unit.target_unit == self.name:
            unit.target_unit = None
        game.units.remove(self)
        return True
        
    elif self.current_activity == 'charging':
      self.charge_at_unit(game)
      if self.ticks == 5:
        self.reset(game)
        self.special_ticks = 0

    if self.ticks >= 16:
      print "Spear failsafe"
      self.reset(game)
        
    if self.ticks == 0:
      self.get_action(game)
    
  def move_to_target_unit(self, game):
    target_unit = game.unit_by_name(self.target_unit)
    if not target_unit:
      self.target_unit = None
      return False
     
    dx = target_unit.x - self.x
    dy = target_unit.y - self.y
    if (dx, dy) == (0,0):
      self.reset(game)
      self.dx = random.randint(-1,1)
      self.dy = random.randint(-1,1)
    else:
      m = (dx**2 + dy**2)**0.5
      if m != 0:
        (self.dx, self.dy) = (round(dx/m), round(dy/m))
    # NPC!
    if (not target_unit.playable) and (not target_unit.hostile) and (not target_unit.ally):
      if (self.x+self.dx, self.y+self.dy) == (target_unit.x,target_unit.y):
        self.refresh_activity(game, 'talking')
        target_unit.show_dialog(game, self.name)
      elif not obstacle(game, (self.x + self.dx, self.y + self.dy)):
        self.refresh_activity(game, 'walking')
        self.reset_ticks()
      elif obstacle(game, (self.x + self.dx, self.y + self.dy)):
        self.sidestep(game)
        
    elif target_unit.hostile != self.hostile:
      dist = distance((self.x,self.y), (target_unit.x,target_unit.y))
      if dist > 1.5 and dist < 3:
        unit = obstacle_unit(game, (self.x+self.dx, self.y+self.dy))
        if unit:
          if not unit.hostile:
            if unit.playable or unit.ally:
              self.sidestep(game)
              return True
        self.refresh_activity(game, 'attacking')
        self.reset_ticks()
      else:
        if dist <= 1.5: #too close, walk back
          (self.dx, self.dy) = (-self.dx, -self.dy)
        if not obstacle(game, (self.x + self.dx, self.y + self.dy)):
          self.refresh_activity(game, 'walking')
          self.reset_ticks()
          
        elif obstacle(game, (self.x + self.dx, self.y + self.dy)):
          #if (self.x + dx, self.y + self.dy) == (self.target_x, self.target_y):
          #  self.reset(game)
          #else:
          self.sidestep(game)
          
  def charge_at_unit(self, game):
    unit = game.unit_by_name(self.target_unit)
    if not unit:
      self.target_unit = None
      self.reset(game)
      return False
    
    if not obstacle(game, (self.x + self.dx, self.y + self.dy)):
      pass
    elif obstacle_unit(game, (self.x + self.dx, self.y + self.dy)):
      unit_2 = obstacle_unit(game, (self.x + self.dx, self.y + self.dy))
      if unit_2 != unit:
        (dx,dy) = (self.dx,self.dy)
        while (dx,dy) in [(self.dx,self.dy), (-self.dx,-self.dy)]:
          dir = random.choice(game.directions)
          (dx,dy) = dir_to_coords(dir)
        unit_2.knockback(game, (dx,dy))
    else:
      self.reset(game)
      return
    
    #if the path is clear:

    self.special_ticks = 0
    self.move((self.dx,self.dy))
    game.redraw_floor = True
    dist = distance((self.x,self.y), (unit.x,unit.y))
    if dist <= 1.5:
      self.do_charge_damage(game)
      unit_2 = obstacle_unit(game, (unit.x + self.dx, unit.y + self.dy))
      if unit_2:
        (dx,dy) = (self.dx,self.dy)
        while (dx,dy) in [(self.dx,self.dy), (-self.dx,-self.dy)]:
          dir = random.choice(game.directions)
          (dx,dy) = dir_to_coords(dir)
        unit_2.knockback(game, (dx,dy))
      unit.knockback(game, (self.dx, self.dy))
    else:
      dx = unit.x - self.x
      dy = unit.y - self.y
      if (dx, dy) == (0,0):
        self.reset(game)
        unit.reset(game)
        self.special_ticks = 0
        return
      m = (dx**2 + dy**2)**0.5
      if m != 0:
        (self.dx, self.dy) = (round(dx/m), round(dy/m))
          
  def move_to_target_unit_special(self, game, secondary=False):
    if secondary:
      activity_name = self.secondary_special_activity_name
    else:
      activity_name = self.special_activity_name
    target_unit = game.unit_by_name(self.target_unit)
    if not target_unit:
      self.target_unit = None
      self.reset(game)
      return
     
    dx = target_unit.x - self.x
    dy = target_unit.y - self.y
    if (dx, dy) == (0,0):
      self.reset(game)
      self.dx = random.randint(-1,1)
      self.dy = random.randint(-1,1)     
      return
    m = (dx**2 + dy**2)**0.5
    if m != 0:
      (self.dx, self.dy) = (round(dx/m), round(dy/m))
    dist = distance((self.x,self.y), (target_unit.x,target_unit.y))
    if target_unit.hostile:
      if activity_name == 'charging':
        if dist <= 5:
          self.refresh_activity(game, activity_name)
          self.reset_ticks()
          self.play_charge_sound()
          return
      else:
        #NYI!
        if dist <= 2:
          self.refresh_activity(game, activity_name)
          self.reset_ticks()
          return
    if not obstacle(game, (self.x + self.dx, self.y + self.dy)):
      self.refresh_activity(game, 'walking')
      self.reset_ticks()
      #at this point, we lose the intention to perform the special attack
      return
    elif obstacle(game, (self.x + self.dx, self.y + self.dy)):
      if (self.x + dx, self.y + self.dy) == (self.target_x, self.target_y):
        self.reset(game)
      else:
        self.sidestep(game)

  def play_charge_sound(self):
    filenames = ["sounds/charge2.ogg"]
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(True)
    if channel:
      channel.play(sound)
    
class PlayerHealer(PlayerMale):
  def __init__(self, game, name, (x, y)):
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.hostile = False
    self.playable = True
    self.ally = False    
    self.has_special = False
    self.palette_swaps.update({(128,128,64): (192,192,192),
                               (128,64,0):(210,230,230)})
    self.equipment = [equipment.make(game, 'scepter')]
    self.equipment.append(equipment.make(game, 'white_wizard_cloak'))
    hair = equipment.Hairpiece(game, 'Hair of Suck', 'hairpiece')
    self.equipment.append(hair)
    self.equipment.append(equipment.Hairpiece(game, 'Beard of Suck', 'beard', hair.palette_swaps))
    self.equipment.append(equipment.make(game, 'white_wizard_hat'))
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'healing', 'falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.heal_amount = 2
    self.current_hp = self.max_hp
    self.load_animations(game, self.palette_swaps)
    self.reset(game)

  def increment_ticks(self):
    self.ticks += 1
        
  def do_events(self, game):
    self.next_frame(game)  
    """ Modified player action tree """
    for unit in game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep(game)
          self.move((self.dx, self.dy))
          self.reset(game)
    if self.target_unit:
      for unit in game.units:
        if unit.name == self.target_unit:
          if unit.current_hp <= 0 and unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
            unit.reset(game)
            unit.refresh_activity(game, 'falling')
    if self.ticks == 1:
      if self.current_activity == 'walking':
        for unit in game.units:
          if (unit.x,unit.y) == (self.x+self.dx,self.y+self.dy):
            if unit.hostile == self.hostile:
              if unit.current_activity == 'standing':
                if unit.name != self.target_unit:
                  unit.knockback(game,(self.dx,self.dy))
        if obstacle(game, (self.x+self.dx, self.y+self.dy)):
          self.sidestep(game)
        else:
          self.move((self.dx, self.dy))
          
    if self.ticks == 2:
      if self.current_activity == 'walking':
        self.reset(game)
        
    if self.ticks == 2:
      if self.current_activity == 'attacking':
        self.end_attack(game)        
        
    if self.ticks == 4:
      if self.current_activity == 'attacking':
        self.reset(game)
        
      elif self.current_activity == 'falling':
        self.refresh_activity(game, 'dead')
        game.corpses.append(Corpse(game, self))
        self.selected = False
        for unit in game.units:
          if unit.target_unit == self.name:
            unit.target_unit = None
        game.units.remove(self)
        return True
      elif self.current_activity == 'healing':
        self.reset(game)
        self.refresh_activity(game, 'healing')
        for unit in game.units:
          if unit.hostile == self.hostile:
            if distance((self.x,self.y), (unit.x,unit.y)) <= 12:
              if unit.current_hp < unit.max_hp:
                if unit.current_hp > 0:
                  if unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
                    unit.current_hp = min(unit.current_hp + self.heal_amount, unit.max_hp)
      elif self.current_activity == 'standing':
        self.reset(game)
        self.refresh_activity(game, 'healing')
      else:
        self.reset(game)
    if self.ticks == 0:
      self.get_action(game)      
      
  def load_animations(self, game, palette_swaps = {}):
    """
    Loads animations automatically, referring to strict naming conventions.
    """
    for activity in self.activities:
        for dir in game.directions:
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
            elif activity == 'falling':
                if dir in ['S', 'SW', 'W']:
                    anim_dir = 'S'
                elif dir in ['NW', 'SE']:
                    anim_dir = 'NW'
                elif dir in ['N', 'NE', 'E']:
                    anim_dir = 'NE'
                for x in xrange(1, 5):
                    if os.path.exists('tga/' + self.anim_name + '_falling_' + anim_dir + '_' + str(x) + '_B.tga'):
                        frames.append('tga/' + self.anim_name + '_falling_' + anim_dir + '_' + str(x) + '_B.tga')
                    elif os.path.exists('tga/' + self.anim_name + '_falling_' + anim_dir + '_' + str(x) + '.tga'):
                        frames.append('tga/' + self.anim_name + '_falling_' + anim_dir + '_' + str(x) + '.tga')
            elif activity == 'dead':
                if dir in ['S', 'SW', 'W']:
                    anim_dir = 'S'
                elif dir in ['NW', 'SE']:
                    anim_dir = 'NW'
                elif dir in ['N', 'NE', 'E']:
                    anim_dir = 'NE'
                if os.path.exists('tga/' + self.anim_name + '_falling_' + anim_dir + '_4_B.tga'):
                    frames.append('tga/' + self.anim_name + '_falling_' + anim_dir + '_4_B.tga')
                if os.path.exists('tga/' + self.anim_name + '_falling_' + anim_dir + '_4.tga'):
                    frames.append('tga/' + self.anim_name + '_falling_' + anim_dir + '_4.tga')
            elif activity == 'decapitated':
              if dir in ['S', 'SW', 'W']:
                anim_dir = 'S'
              elif dir in ['NW', 'SE']:
                anim_dir = 'NW'
              elif dir in ['N', 'NE', 'E']:
                anim_dir = 'NE'
              for x in xrange(1, 5):
                if os.path.exists('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_' + str(x) + '_B.tga'):
                  frames.append('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_' + str(x) + '_B.tga')
                elif os.path.exists('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_' + str(x) + '.tga'):
                  frames.append('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_' + str(x) + '.tga')
            elif activity == 'dead_decapitated':
              if os.path.exists('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_4_B.tga'):
                frames.append('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_4_B.tga')
              elif os.path.exists('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_4.tga'):
                frames.append('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_4.tga')
            elif activity == 'casting':
              frames = [
                'tga/' + self.anim_name + '_attacking_' + dir + '_1.tga',
                'tga/' + self.anim_name + '_standing_' + dir + '_1.tga'
              ]
              surface = pygame.image.load(frames[0])
              surface = palette_swap_multi(surface, palette_swaps)
              surface.set_colorkey((255,255,255))
              overlay_surface = pygame.image.load('tga/fireball_forming_' + dir + '_1.tga')
              overlay_surface.set_colorkey((255,255,255))
              surface.blit(overlay_surface, (0,0))
              frame_surfaces.append(surface)
              surface = pygame.image.load(frames[1])
              surface = palette_swap_multi(surface, palette_swaps)
              surface.set_colorkey((255,255,255))
              frame_surfaces.append(surface)
              self.animations.append(Animation(activity, [dir], frame_surfaces, frames))
            elif activity == 'healing':
              for x in range(1,5):
                filename = 'tga/' + self.anim_name + '_standing_SE_1.tga'
                frames.append(filename)
                player_surface = pygame.image.load(filename)
                player_surface.set_colorkey((255,255,255))
                surface = palette_swap_multi(surface, palette_swaps)
                glow_surface = pygame.image.load('tga/goldenglow_' + str(x) + '.tga')
                glow_surface.set_colorkey((255,255,255))
                glow_surface.blit(player_surface, (0,0))
                frame_surfaces.append(glow_surface)
              self.animations.append(Animation(activity, [dir], frame_surfaces, frames))
            elif activity == 'stunned':
              anim_directions = []
              i = game.directions.index(dir)
              for d in game.directions:
                j = game.directions.index(d)
                if j >= i:
                  anim_directions.append(d)
              for d in game.directions:
                j = game.directions.index(d)                       
                if j < i:
                  anim_directions.append(d)
              for d in anim_directions:
                frame = 'tga/' + self.anim_name + '_standing_' + d + '_1.tga'
                frames.append(frame)
                    
            # now we load from filenames
            if activity != 'healing':
              for frame in frames:
                surface = pygame.image.load(frame)
                surface = palette_swap_multi(surface, palette_swaps)
                surface.set_colorkey((255,255,255))
                frame_surfaces.append(surface)
            self.animations.append(Animation(activity, [dir], frame_surfaces, frames))

class RandomSoldier(PlayerMale):
  def __init__(self, game, name, (x, y)):
    BasicUnit.__init__(self, game, name, 'player', (x,y))  
    self.hostile = False
    self.playable = True
    self.ally = False    
    self.has_special = False    
    r = random.randint(150, 255)
    g = random.randint(int(r*0.5), int(r*0.9))
    b = random.randint(int(r*0.2), int(r*0.5))
    #hair
    r = random.randint(0, 192)
    g = random.randint(int(r*0.5), int(r*0.9))
    b = random.randint(int(r*0.1), int(r*0.2))
    self.equipment = [
                      equipment.make(game, 'blue_chain_mail'),
                      equipment.make(game, 'sword_of_suck'),
                      equipment.make(game, 'iron_shield'),
                      equipment.Hairpiece(game, 'Hair', 'hairpiece'),
                      equipment.make(game, 'helm_of_suck')
                     ]
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.current_hp = self.max_hp
    self.load_animations(game, self.palette_swaps)
    self.reset(game)
    
  def increment_ticks(self):
    self.ticks += 1
    
class PlayerOfficer(PlayerMale):
  def __init__(self, game, name, (x,y)):
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.hostile = False
    self.playable = True
    self.ally = False
    self.has_special = True
    self.palette_swaps.update({(128,128,64): (0,0,128), (128,64,0): (128,0,0)})
    self.equipment = [
                      equipment.make(game, 'blue_chain_mail'),
                      equipment.make(game, 'sword_of_suck'),
                      equipment.make(game, 'tower_shield'),
                      equipment.Hairpiece(game, 'Hair', 'hairpiece'),
                      equipment.make(game, 'officer_helm')
                     ]
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'bashing', 'falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.special_ticks = 30
    self.max_special_ticks = 30
    self.current_hp = self.max_hp
    self.load_animations(game, self.palette_swaps)
    self.reset(game)
    

    
class BattleHealer(PlayerHealer):
  #Delete this and implement similar behavior for PlayerFemale
  def __init__(self, game, name, (x, y)):
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.name = name
    self.anim_name = 'player'
    self.hostile = False
    self.playable = True
    self.ally = False
    self.has_special = False
    self.palette_swaps.update({
                               (128,128,64): (0,0,128),
                               (128,64,0): (0,0,128),
                               (128,128,0): (0,0,128),
                               (0,0,0):(0,32,32)
                              })
    self.equipment = [equipment.make(game, 'sword_of_suck')]
    hair = equipment.Hairpiece(game, 'Hair of Suck', 'hairpiece')
    self.equipment.append(hair)
    self.equipment.append(equipment.Hairpiece(game, 'Beard of Suck', 'beard', hair.palette_swaps))
    self.equipment.append(equipment.make(game, 'cloak_of_the_forest'))
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'healing', 'falling', 'dead', 'decapitated', 'dead_decapitated']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100    
    self.heal_amount = 2
    self.current_hp = self.max_hp
    self.load_animations(game, self.palette_swaps)
    self.reset(game)
    
  def do_events(self, game):
    self.next_frame(game)
    """ Modified player action tree """
    for unit in game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep(game)
          self.move((self.dx, self.dy))
    if self.target_unit:
      for unit in game.units:
        if unit.name == self.target_unit:
          if unit.current_hp <= 0 and unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
            unit.reset(game)
            unit.refresh_activity(game, 'falling')
    if self.ticks == 1:
      if self.current_activity == 'walking':
        for unit in game.units:
          if (unit.x,unit.y) == (self.x+self.dx,self.y+self.dy):
            if unit.hostile == self.hostile:
              if unit.current_activity == 'standing':
                if unit.name != self.target_unit:
                  unit.knockback(game,(self.dx,self.dy))       
        if obstacle(game, (self.x+self.dx, self.y+self.dy)):
          self.sidestep(game)
        else:
          self.move((self.dx, self.dy))
          
    if self.ticks == 2:
      if self.current_activity == 'walking':
        self.reset(game)
        
    if self.ticks == 2:
      if self.current_activity == 'attacking':
        self.end_attack(game)        
        
    if self.ticks == 4:
      if self.current_activity == 'attacking':
        self.reset(game)
        
      elif self.current_activity == 'falling':
        self.refresh_activity(game, 'dead')
        game.corpses.append(Corpse(game, self))
        self.selected = False
        for unit in game.units:
          if unit.target_unit == self.name:
            unit.target_unit = None
        game.units.remove(self)
        return True
      elif self.current_activity == 'healing':
        min_percent_hp = 100
        healing_target = None
        for unit in game.units:
          if unit.hostile == self.hostile:
            if distance((self.x,self.y), (unit.x,unit.y)) <= 10:
              if unit.current_hp > 0 and unit.current_hp < unit.max_hp:
                if unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
                  percent_hp = unit.current_hp/unit.max_hp
                  if percent_hp < min_percent_hp:
                    healing_target = unit.name
                    min_percent_hp = percent_hp
        if healing_target:
          unit = game.unit_by_name(healing_target)
          if unit:
            unit.current_hp = min(unit.current_hp + self.heal_amount, unit.max_hp)

        self.reset(game)
        self.refresh_activity(game, 'healing')
      elif self.current_activity == 'standing':
        self.reset(game)
        self.refresh_activity(game, 'healing')
      else:
        self.reset(game)
    if self.ticks == 0:
      self.get_action(game)
    
class PlayerFemaleMelee(PlayerFemale, PlayerMale):
  #combat healer
  #parts might still be sketchy, there's a lot of inheritance stuff
  def __init__(self, game, name, (x,y), palette_swaps = {}):
    BasicUnit.__init__(self, game, name, 'female', (x,y))
    self.name = name
    self.anim_name = 'female'
    self.hostile = False
    self.playable = True
    self.ally = False
    self.has_special = False
    self.palette_swaps.update({(79,39,0):(148,39,0),(0,64,64):(57,135,0), (255,128,64):(255,195,139)})
    self.equipment = [
                      equipment.make(game, "sword_of_suck", True),
                      equipment.make(game, "helm_of_suck", True)
                     ]
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.current_hp = self.max_hp
    self.load_animations(game, self.palette_swaps)
    self.reset(game)
    
  def load_animations(self, game, palette_swaps):
    PlayerFemale.load_animations(self, game, palette_swaps)

  def do_events(self, game):
    PlayerMale.do_events(self, game)
    
  def get_action(self, game):
    PlayerMale.get_action(self, game)
    
  def move_to_target_unit(self, game):
    PlayerMale.move_to_target_unit(self, game)
  
  def end_attack(self, game):
    target_unit = game.unit_by_name(self.target_unit)
    if not target_unit:
      self.reset(game)
      return False
    else:  
      can_decapitate = False
      #for equip in self.equipment:
      #  if equip.anim_name in ['sword', 'sword2']:
      #    can_decapitate = True
      #if 'decapitated' not in target_unit.activities:
      #  can_decapitate = False
      dmg = self.damage()
      if can_decapitate and target_unit.current_activity not in ['falling','dead','decapited','dead_decapitated'] and target_unit.current_hp > 0 and target_unit.current_hp <= dmg*3 and random.random() > 0.05:
        target_unit.bleed(game, target_unit.current_hp)
        target_unit.current_hp = 0
        target_unit.reset(game)
        target_unit.refresh_activity(game, 'decapitated')
        self.play_hit_sound()
      else:
        target_unit.take_damage(game, dmg)
        
        # Healing code here.  Rest of the function is just PlayerMale.end_attack()
        healing_target = None
        for u in game.units:
          if u.hostile == self.hostile:
            if distance((u.x,u.y),(self.x,self.y)) <= 5:
              if u.current_hp < u.max_hp:
                if healing_target:
                  if (u.current_hp/u.max_hp) < (healing_target.current_hp / healing_target.max_hp):
                    healing_target = u
                  elif (u.current_hp/u.max_hp) == (healing_target.current_hp / healing_target.max_hp):
                    healing_target = random.choice([u, healing_target])
                else:
                  healing_target = u
        if healing_target:
          healing_chance = 0.5
          healing_coefficient = 0.2
          if random.random() <= healing_chance:
            healing_target.current_hp = min(healing_target.current_hp + dmg*healing_coefficient,
                                          healing_target.max_hp)
          game.healing_flashes.append(HealingFlash(game, healing_target.name))
        # End healing code
        
        target_unit.bleed(game, dmg)
        if target_unit.current_hp > 0:
          self.play_hit_sound()
    
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
    self.load_animations(game, self.palette_swaps)
    self.reset(game)
    
  def increment_ticks(self):
      self.ticks += 1
    
  def load_animations(self, game, palette_swaps):
    PlayerMale.load_animations(self, game, palette_swaps)

  def do_events(self, game):
    self.next_frame(game)  
    """ Copy/pasted from PlayerMale. """
    for unit in game.units:
      if unit.name != self.name:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep(game)
    if self.ticks == 1:
      if self.current_activity == 'walking':
        for unit in game.units:
          if (unit.x,unit.y) == (self.x+self.dx,self.y+self.dy):
            if unit.hostile == self.hostile:
              if unit.current_activity == 'standing':
                if unit.name != self.target_unit:
                  unit.knockback(game,(self.dx,self.dy))
        if obstacle(game, (self.x+self.dx, self.y+self.dy)):
          self.sidestep(game)
        else:
          self.move((self.dx, self.dy))
    if self.ticks == 2:
      if self.current_activity == 'walking':
        if (self.x,self.y) != (self.target_x,self.target_y):
          if obstacle(game, (self.x+self.dx, self.y+self.dy)):
            pass
          else:
            self.move((self.dx, self.dy))      
        self.reset(game)
      elif self.current_activity == 'standing':
        self.reset(game)
      elif self.current_activity == 'attacking':
        self.end_attack(game)
      elif self.current_activity == 'bashing':
        self.end_bash(game)
        
    if self.ticks == 4:
      if self.current_activity == 'attacking':
        self.reset(game)
      elif self.current_activity == 'bashing':
        self.reset(game)
      elif self.current_activity == 'falling':
        self.refresh_activity(game, 'dead')
        game.corpses.append(Corpse(game, self))
        self.selected = False
        for unit in game.units:
          if unit.target_unit == self.name:
            unit.target_unit = None
        game.units.remove(self)
        return True
      elif self.current_activity != 'stunned': #i'm not sure why we need this, but it's a good failsafe
        self.reset(game)
        
    if self.ticks == 8:
      if self.current_activity == 'stunned':
        self.reset(game)
        
    if self.ticks == 0:
      if self.current_activity == 'bashing': #weird
        pass#print 'bad playermale!'
      else:
        self.get_action(game)
    
  def get_action(self, game):
    PlayerMale.get_action(self, game)
    
  def move_to_target_unit(self, game):
    PlayerMale.move_to_target_unit(self, game)
    
  def draw(self, game):
    (x,y) = grid_to_pixel(game, self.x, self.y)
    #x -= 8; y -= 30
    x -= 18; y -= 50
    for equip in self.equipment:
      f = equip.current_animation.get_current_filename()
      if f[len(f)-6:] == '_B.tga':
        equip.draw(game, x, y)
    source = self.get_current_frame()
    game.screen.blit(source, (x, y))
    for equip in self.equipment:
      f = equip.current_animation.get_current_filename()
      if f[len(f)-6:] != '_B.tga':
        equip.draw(game, x, y)
        
  def load_animations(self, game, palette_swaps = {}):
    """
    C/P'ed from PlayerMale.
    """
    for activity in self.activities:
      for dir in game.directions:
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
          surface = palette_swap_multi(surface, palette_swaps)
          surface.set_colorkey((255,255,255))
          if activity in ['standing', 'walking']:
            rider_surface = pygame.image.load("tga/" + self.rider_anim_name + "_" + dir + "_1.tga")
            rider_surface.set_colorkey((255,255,255))
          offset = (0, 0)
          surface.blit(rider_surface, offset)
          frame_surfaces.append(surface)
        self.animations.append(Animation(activity, [dir], frame_surfaces, frames))
            
class PlayerArcher(PlayerFemale, PlayerMale):
  def __init__(self, game, name, (x,y)):
    t1 = pygame.time.get_ticks()
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.hostile = False
    self.playable = True
    self.ally = False    
    self.has_special = False
    self.has_secondary_special = False
    self.palette_swaps.update({(128,64,0):(0,64,0)})
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
    self.equipment = [equipment.Hairpiece(game, "Hair", "hairpiece", {(0,0,0):random.choice(hair_colors)}),
                      equipment.make(game, "green_bow"),
                      equipment.Helm(game, "Green Helm", "hat2", {(0,0,128):(0,128,0),
                      (0,0,255):(0,192,0), (0,128,255):(0,192,128)}),
                      equipment.make(game, "brown_bandit_tunic")
                      ]
    self.inventory = []
    self.activities = ['standing', 'walking', 'shooting', 'falling', 'dead']
    self.current_activity = 'standing'
    self.animations = []
    self.current_hp = self.max_hp = 100
    self.avoidance = self.mitigation = 0
    self.current_hp = self.max_hp
    self.min_distance = 6
    self.max_distance = 12
    self.arrow_damage = 10
    self.load_animations(game, self.palette_swaps)
    self.reset(game)
    t2 = pygame.time.get_ticks()
    print "Archer load time:", t2-t1
    
  def load_animations(self, game, palette_swaps={}):
    PlayerMale.load_animations(self, game, palette_swaps)
  
  def get_action(self, game):
    PlayerFemale.get_action(self, game)
  
  def scream(self):
    PlayerMale.scream(self)
  
  def do_events(self, game):
    self.next_frame(game)  
    for unit in game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep(game)
          self.move((self.dx, self.dy))
    if self.target_unit:
      target_unit = game.unit_by_name(self.target_unit)
      if target_unit == None:
        self.target_unit = None
        return False
      if target_unit.current_hp <= 0 and target_unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
        target_unit.reset(game)
        target_unit.refresh_activity(game, 'falling')
    if self.ticks == 2:
      if self.current_activity == 'walking':
        for unit in game.units:
          if (unit.x,unit.y) == (self.x+self.dx,self.y+self.dy):
            if unit.hostile == self.hostile:
              if not unit.playable:
                if unit.ally:
                  unit.knockback(game,(self.dx,self.dy))    
        if obstacle(game, (self.x+self.dx, self.y+self.dy)):
          self.sidestep(game)
        else:
          self.move((self.dx,self.dy))
          game.redraw_floor = True
    if self.ticks == 4:
      if self.current_activity == 'standing':
        self.reset(game)
      if self.current_activity == 'walking':
        self.reset(game)        
      if self.current_activity == 'shooting':
        game.darts.append(Arrow(game, self.arrow_damage, self.name, self.target_unit))
    if self.ticks == 8:
      if self.current_activity == 'shooting':
        pass#so we don't reset; shot will cooldown @ 8
      elif self.current_activity == 'falling':
        self.refresh_activity(game, 'dead')
        game.corpses.append(Corpse(game, self))
        self.selected = False
        for unit in game.units:
          if unit.target_unit == self.name:
            unit.target_unit = None
        game.units.remove(self)
        return True
      else:
        self.reset(game)
    if self.ticks == 16:
      if self.current_activity == 'shooting':
        self.reset(game)
      else:
        print "Archer failsafe"
        self.reset(game)        
        
    if self.ticks == 0:
      self.get_action(game)
      
  def move_to_target_unit(self, game):
    # same as PlayerFemale, but uses "shooting" instead of "attacking"
    target_unit = game.unit_by_name(self.target_unit)
    if not target_unit:
      self.target_unit = None
      return False
     
    dx = target_unit.x - self.x
    dy = target_unit.y - self.y
    if (dx, dy) == (0,0): #this looks weird
      self.reset(game)
      self.dx = random.randint(-1,1)
      self.dy = random.randint(-1,1)
    else:      
      m = (dx**2 + dy**2)**0.5
      if m != 0:
        (self.dx, self.dy) = (round(dx/m), round(dy/m))

    if (not target_unit.playable) and (not target_unit.hostile) and (not target_unit.ally):
      if (self.x+self.dx, self.y+self.dy) == (target_unit.x,target_unit.y):
        self.refresh_activity(game, 'talking')
        target_unit.show_dialog(game, self.name)
      elif obstacle(game, (self.x+self.dx,self.y+self.dy)):
        self.sidestep(game)
      else:
        self.refresh_activity(game, 'walking')
    elif target_unit.hostile:

      dist = distance((self.x,self.y), (target_unit.x,target_unit.y))
      if dist >= self.min_distance and dist <= self.max_distance and \
      game.LOS((self.x,self.y), (target_unit.x,target_unit.y)):
        self.refresh_activity(game, 'shooting')
      else:
        if dist < self.min_distance:
          (self.dx, self.dy) = (-self.dx, -self.dy)
        if not obstacle(game, (self.x + self.dx, self.y + self.dy)):
          self.refresh_activity(game, 'walking')
        elif obstacle(game, (self.x + self.dx, self.y + self.dy)):
          if (self.x + dx, self.y + self.dy) == (self.target_x, self.target_y):
            self.reset(game)
          else:
            self.sidestep(game)
      
class InvisibleMan(PlayerMale):
  def __init__(self, game, name, (x,y)):
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.hostile = False
    self.playable = True
    self.ally = False    
    self.has_special = True
    self.palette_swaps.update({(128,0,0):(0,0,1), (0,0,0):(255,255,255), (128,128,64): (0,0,128), (128,64,0): (255,255,255),
                               (0,64,64):(255,0,0), (255,128,64):(0,0,1)})
    self.equipment = [
                      equipment.make(game, 'blue_chain_mail'),
                      equipment.make(game, 'fire_sword'),
                      equipment.make(game, 'cloak_of_suck')
                     ]
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'bashing', 'falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.special_ticks = 30
    self.max_special_ticks = 30
    self.current_hp = self.max_hp
    self.load_animations(game, self.palette_swaps)
    self.reset(game)
    self.floor_fire = None
    
  def do_events(self, game):
    if self.floor_fire:
      (self.floor_fire.x, self.floor_fire.y) = (self.x,self.y)
      self.floor_fire.next_frame()
    else:
      fire_filenames = ["tga/floor_fire_" + str(x) + ".tga" for x in [1,2,3,4]]
      fire_frames = [pygame.image.load(f) for f in fire_filenames]
      for f in fire_frames:
        f.set_colorkey((255,255,255))
      self.floor_fire = FireTile(fire_frames, (self.x,self.y), 10)
    PlayerMale.do_events(self, game)
    
  def draw(self, game):
    self.floor_fire.draw(game)
    PlayerMale.draw(self, game)
    
class HajjiFiruz(PlayerMale):
  def __init__(self, game, name, (x, y)):
    BasicUnit.__init__(self, game, name, 'player', (x,y))  
    self.hostile = False
    self.playable = True
    self.ally = False    
    self.has_special = False
    self.special_ticks = self.max_special_ticks = 0
    skin_color = (0,0,0)
    clothes_color = (255,0,0)
    eye_color = (64,128,192)
    lip_color = (255,0,0)
    hair_color = (98,49,0)
    self.palette_swaps.update({(128,0,0):lip_color,(255,128,64):skin_color, (32,32,16):clothes_color, (128,64,0):clothes_color,(128,128,0):clothes_color, (0,64,64):eye_color})
    self.equipment = [
                      equipment.make(game, 'red_triangle_hat'),
                      equipment.Hairpiece(game, 'Hair of Suck', 'hairpiece',{(0,0,0):hair_color}),
                      equipment.make(game, 'red_tunic'),
                      equipment.make(game, 'gold_klub')
                     ]
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.current_hp = self.max_hp
    self.load_animations(game, self.palette_swaps)
    self.reset(game)
    

class EnemyMale(PlayerMale):
  #Basically unused, but other stuff inherits from it
  def __init__(self, game, name, (x,y), palette_swaps = {}):
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.hostile = True
    self.playable = False
    self.ally = False
    self.has_special = False
    self.palette_swaps = palette_swaps
    self.equipment = [equipment.make('iron_chainmail'),
                      equipment.make('wooden_shield'),
                      equipment.make('helm_of_suck'),
                      equipment.make('sword_of_suck')]
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'stunned']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.current_hp = self.max_hp
    self.min_damage = 6
    self.max_damage = 10
    self.load_animations(game, self.palette_swaps)
    self.reset(game)
    
  def do_events(self, game):
    self.next_frame(game)
    #Emergency maneuvers
    for obj in game.units + game.trees:
      if obj != self:
        if (obj.x, obj.y) == (self.x, self.y):
          self.sidestep(game)
          self.move((self.dx, self.dy))
          self.reset(game)
    
    if self.current_activity == 'walking':
      if self.ticks == 2:
        self.move((self.dx, self.dy))
      elif self.ticks == 4:
        self.reset(game)
    
    elif self.current_activity == 'attacking':
      if self.ticks == 4:
        self.end_attack(game)
      elif self.ticks == 8:
        self.reset(game)
                
    elif self.current_activity == 'standing':
      if self.ticks == 4:
        self.reset(game)

    elif self.current_activity == 'falling':
      if self.ticks == 8:
        self.refresh_activity(game, 'dead')
        self.reset_ticks()
        game.corpses.append(Corpse(game, self))
        powerup_chance = 0.30
        if random.random() < powerup_chance:
          for powerup in game.powerups:
            if (powerup.x, powerup.y) == (self.x,self.y):
              break
          else:
            game.powerups.append(HealthPowerup((self.x,self.y), 30))
        for unit in game.units:
          if unit.target_unit == self.name:
            unit.target_unit = None
        game.units.remove(self)
        return True
    elif self.current_activity == 'decapitated':
      if self.ticks == 8:
        self.refresh_activity(game, 'dead_decapitated')
        game.corpses.append(Corpse(game, self))
        powerup_chance = 0.30
        if random.random() < powerup_chance:
          for powerup in game.powerups:
            if (powerup.x, powerup.y) == (self.x,self.y):
              break
          else:
            game.powerups.append(HealthPowerup((self.x,self.y), 30))
        for unit in game.units:
          if unit.target_unit == self.name:
            unit.target_unit = None
        game.units.remove(self)
        return True
    
    elif self.ticks == 16:
      if self.current_activity == 'stunned':
        self.reset(game)
      
    if self.ticks == 0:
      if self.current_activity in ['falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned']:
        pass
      else:
        self.get_action(game)
  
  def get_action(self, game):
    #EnemyMale
    new_target = True
    if self.target_unit:
      target_unit = game.unit_by_name(self.target_unit)
      if not target_unit:
        self.target_unit = None
      else:
        new_target = False
  
    for unit in game.units:
      if unit.hostile != self.hostile:
        if game.LOS((self.x,self.y),(unit.x,unit.y)):
          if self.target_unit:
            target_unit = game.unit_by_name(self.target_unit)
            if distance((self.x,self.y), (unit.x,unit.y)) < distance((self.x,self.y), (target_unit.x,target_unit.y)):
              self.target_unit = unit.name
          else:
            if distance((self.x,self.y), (unit.x,unit.y)) <= 10:
              self.target_unit = unit.name
    if self.target_unit:
      unit = game.unit_by_name(self.target_unit)
      if not unit:
        self.target_unit = None
        self.reset(game)
        return False
      if new_target:
        self.play_target_sound()
      self.point_at(unit)
      if (self.current_hp / self.max_hp) <= 0.25:
        (self.dx,self.dy) = (-self.dx,-self.dy)
        if obstacle(game, (self.x+self.dx,self.y+self.dy)):
          self.sidestep(game)
        else:
          if random.random() < 0.6:
            if not obstacle(game, (self.x+self.dx,self.y+self.dy)):
              self.refresh_activity(game, 'walking')
      else: # non-critical HP      
        if obstacle(game, (self.x+self.dx, self.y+self.dy)):      
          if (unit.x, unit.y) == (self.x+self.dx, self.y+self.dy):
            self.refresh_activity(game, 'attacking')
          elif obstacle_unit(game, (self.x+self.dx, self.y+self.dy)):
            unit_2 = obstacle_unit(game, (self.x+self.dx, self.y+self.dy))
            if unit_2.hostile != self.hostile:
              self.target_unit = unit_2.name
              self.refresh_activity(game, 'attacking')  
            else:
              self.sidestep(game)
        else:
          self.refresh_activity(game, 'walking')
    else:
      if random.random() > 0.50:
        self.dx = random.randint(-1,1)
        self.dy = random.randint(-1,1)
        if not obstacle(game, (self.x+self.dx,self.y+self.dy)):
          self.refresh_activity(game, 'walking')
    self.reset_ticks()
    
  def draw_hp_bar(self, width, height, alpha=255):
    #enemymale
    green_bar = pygame.Rect((1, 1, (width-2), (height-2)))
    surface = pygame.Surface((width, height))
    surface.fill((255, 255, 255))
    surface.fill((255, 0, 255), green_bar)
    hp_ratio = self.current_hp/self.max_hp
    red_left = round(hp_ratio*(width-2))+1
    red_left = max(red_left, 0)
    red_width = round((1-hp_ratio)*(width-2))
    red_bar = pygame.Rect((red_left, 1, red_width, (height-2)))
    surface.fill((128, 0, 128), red_bar)
    surface.set_alpha(alpha)
    return surface
      
  def draw(self, game):
    (x,y) = grid_to_pixel(game, self.x, self.y)
    x -= 8; y -= 30
    for equip in self.equipment:
      f = equip.current_animation.get_current_filename()
      if f[len(f)-6:] == '_B.tga':
        equip.draw(game, x, y)
    #print self.name, self.current_animation.get_current_filename(), self.current_animation.findex
    source = self.get_current_frame()
    game.screen.blit(source, (x, y))
    #game.draw_black(self, source, (x,y))
    
    for equip in self.equipment:
      f = equip.current_animation.get_current_filename()
      if f[len(f)-6:] != '_B.tga':
        equip.draw(game, x, y)

    (x,y) = grid_to_pixel(game, self.x, self.y)
    x += 4
    y -= 24
    alpha = 0
    for unit in game.units:
      if not unit.hostile:
        if unit.target_unit == self.name:
          alpha = 255
          break
        elif distance((self.x,self.y), (unit.x,unit.y)) <= 12:
          alpha = 128
        elif distance((self.x,self.y), (unit.x,unit.y)) <= 18:
          if alpha < 64:
            alpha = 64
    game.screen.blit(self.draw_hp_bar(16, 5, alpha), (x,y))
