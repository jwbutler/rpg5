from __future__ import division
import pygame
from classes import *

import equipment
import os
import random
import language

class BasicUnit:
  def __init__(self, game, name, anim_name, (x,y)):
    self.game = game
    self.name = name
    self.anim_name = anim_name
    self.x = x
    self.y = y
    self.dx = 0
    self.dy = -1
    self.selected = False
    self.selected_in_menu = False
    self.level = 1 #!!!
    self.target_x = self.target_y = None
    self.target_unit = None
    
    self.set_face_features()

  def set_face_features(self):
    skin_colors = [(251,172,94), (253,177,128), (255,128,64), (197,156,73), (153,129,70), (151,90,36)]
    eye_colors = [(0,192,0), (0,0,192), (0,128,192), (128,64,0), (128,128,128), (64,192,64)]
    lip_colors = [(128,0,0), (81,0,0), (146,43,55), (129,59,38), (204,116,118), (180,115,133)]
    self.skin_color = random.choice(skin_colors)
    self.lip_color = random.choice(lip_colors)
    self.eye_color = random.choice(eye_colors)
    self.palette_swaps = {
      (255,128,64):self.skin_color,
      (0,64,64):self.eye_color,
      (128,0,0):self.lip_color
    }
    
  def move(self, (dx, dy)):
    """
    Increment the NPC's coordinates by (dx, dy).  No checking!
    """
    self.x += dx
    self.y += dy
    print("count " + str(self.game.depth_tree.count()))
    self.game.depth_tree.remove(self)
    self.game.depth_tree.insert(DepthTreeNode(self))
    print("count2 " + str(self.game.depth_tree.count()))
    

  def increment_ticks(self):
    self.ticks += 1

  def refresh_animation(self, directions):
    """ Find the animation that matches current activity & direction, and queue it up. """
    """ Queue is a misnomer... """
    for anim in self.animations:
      if anim.activity == self.current_activity and anim.directions == directions:
        self.current_animation = anim
        self.current_animation.findex = 0
    for equip in self.equipment:
      equip.set_animation(self.current_activity, directions)

  def knockback(self, (dx, dy)):
    """ Push SELF back """
    if not self.game.obstacle((self.x+dx, self.y+dy)):
      self.x += dx
      self.y += dy
      self.game.depth_tree.remove(self)
      self.game.depth_tree.insert(DepthTreeNode(self))

  def get_current_frame(self):
      """ Retrieve the current animation frame. """
      return self.current_animation.get_current_frame()
  
  def next_frame(self):
    """ Iterates frame index of self and equipment. """
    for x in self.equipment + [self]:
      x.current_animation.next_frame()

  def take_damage(self, damage, magic=False):
    if magic:
      self.current_hp = max(0, self.current_hp - damage)
    else:
      if random.random() > self.avoidance:
        self.current_hp = max(0, self.current_hp - int(damage*(1-self.mitigation)))
      else:
        self.play_block_sound()

    if self.current_hp <= 0 and self.current_activity not in ['falling', 'decapitated', 'dead', 'dead_decapitated']:
      self.die()

  def die(self):
    self.current_hp = 0
    self.refresh_activity('falling')
    self.reset_ticks()
    self.scream()


  def draw(self):
    self.sort_equipment()
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    x -= 8; y -= 30
    
    # Draw equipment that renders under unit
    for equip in self.equipment:
      f = equip.current_animation.get_current_filename()
      if f[len(f)-6:] == '_B.tga':
        equip.draw(x, y)
    source = self.get_current_frame()
    self.game.screen.blit(source, (x, y))
    # Draw equipment that renders over unit
    for equip in self.equipment:
      f = equip.current_animation.get_current_filename()
      if f[len(f)-6:] != '_B.tga':
        equip.draw(x, y)

  def draw_in_place(self, (x,y)):
    #Draws the unit standing, for the menu screen
    #(x,y) are PIXELS
    surface = pygame.surface.Surface((40,40))
    surface.fill((255,255,255))
    surface.set_colorkey((255,255,255))
    self.sort_equipment()
    # Draw equipment that renders under unit
    for equip in self.equipment:
      for anim in equip.animations:
        if anim.directions == ["SE"] and anim.activity == "standing":
          f = anim.filenames[0]
          if f[len(f)-6:] == '_B.tga':
            source = anim.frames[0]
            if isinstance(equip, equipment.Spear): #GHETTO!
              surface.blit(source, (-10,-20))
            else:
              surface.blit(source, (0,0))
    for anim in self.animations:
      if anim.directions == ["SE"] and anim.activity == "standing":
        source = anim.frames[0]
        surface.blit(source, (0,0))
        break
    # Draw equipment that renders over unit
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
    self.game.screen.blit(surface2, (x, y))

  def get_z(self):
    #to determine overlaps
    return 6*self.x + 6*self.y + 2
      
  def get_rect(self):
    (left, top) = self.game.grid_to_pixel((self.x, self.y))#might be wrong offset
    top -= 16 
    rect = self.get_current_frame().get_rect()
    (width, height) = (rect.width, rect.height)
    return pygame.Rect(left, top, width, height)
    
  def get_center(self):
    return self.game.grid_to_pixel((self.x, self.y))
    
  def refresh_activity(self, activity, directions = []):
    self.current_activity = activity
    if directions:
      pass
    else:
      directions = [self.game.coords_to_dir((self.dx, self.dy))]
    self.refresh_animation(directions)
          
  def reset_ticks(self):
    self.ticks = 0
      
  def draw_hp_bar(self, width, height, alpha=255):
    # Draw the health meter, to be used for unit cards
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
    # Draw the mana bar
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
  
  """
  def point_at_OLD(self, target):
    squares = self.game.adjacent_squares((self.x, self.y))
    squares.sort(lambda a,b: self.game.distance_sort_posn(a,b,(target.x,target.y)))
    for square in squares:
      if square == (target.x, target.y):
        self.dx = square[0] - self.x
        self.dy = square[1] - self.y
        return True
      elif not self.game.obstacle(square):
        self.dx = square[0] - self.x
        self.dy = square[1] - self.y
        return True
  """
  
  def point_at(self, target):
    (dx,dy) = (target.x-self.x, target.y-self.y)
    m = (dx**2 + dy**2)**0.5
    if m != 0:
      #(self.dx, self.dy) = (int(dx/m + 0.5), int(dy/m + 0.5))
      (self.dx, self.dy) = (round(dx/m), round(dy/m))

  def point_at_point(self, (x,y)):
    (dx,dy) = (x-self.x, y-self.y)
    m = (dx**2 + dy**2)**0.5
    if m != 0:
      #(self.dx, self.dy) = (int(dx/m + 0.5), int(dy/m + 0.5))
      (self.dx, self.dy) = (round(dx/m), round(dy/m))
            
  def sort_equipment(self):
    sorted_equipment = []
    slots = []
    if self.current_activity == 'standing' and self.current_animation.directions[0] in ["E", "SE", "S"]:
      slots = ["beard", "hair", "cloak", "chest", "head", "weapon", "shield"]
    elif self.current_activity == 'standing' and self.current_animation.directions[0] in ["NE"]:
      slots = ["beard", "hair", "cloak", "chest", "head", "shield", "weapon"]
    elif self.current_activity == 'walking' and self.current_animation.directions[0] in ["E"]:
      slots = ["beard", "hair", "cloak", "chest", "head", "weapon", "shield"]
    else:
      slots = ["beard", "hair", "chest", "cloak", "head", "weapon", "shield"]
      
    for slot in slots:
      for equip in self.equipment:
        if equip.slot == slot:
          sorted_equipment.append(equip)
          break

    self.equipment = sorted_equipment
    
  def bleed(self, damage):
    self.game.blood.append(Blood(self.game, self.x, self.y, damage*2))
    
  def decapitate(self):
    # Make sure this gets inherited by zombies, etc
    self.bleed(target_unit.current_hp*2)
    self.current_hp = 0
    self.reset()
    self.refresh_activity('decapitated')

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
    
    # These let us remember we're planning to use a special on a unit out of range
    self.queue_special = False
    self.queue_secondary_special = False
    
    self.special_ticks = self.max_special_ticks = 60
    clothes_colors = [(128,0,0), (0,128,0), (0,0,128), (128,128,64),
                    (64,64,64), (128,128,128)]
    belt_colors = [(64,64,64), (128,64,0)]
    self.palette_swaps.update({(128,128,64):random.choice(clothes_colors), #shirt
                               (128,64,0):random.choice(clothes_colors), #pants
                               (128,128,0):random.choice(belt_colors)}) #belt
    self.activities = ['standing', 'walking', 'attacking', 'bashing', 'slashing', 'falling', 'dead']
    self.equipment = [equipment.Sword(self.game, "Sword", 'sword', self.activities)]
    armor_colors = [(128,128,128), (192,96,32), (128,128,192), (64,64,64)]
    (r,g,b) = random.choice(armor_colors)
    (rr,gg,bb) = (int(r/2),int(g/2),int(b/2))
    
    self.equipment.append(equipment.Shield(self.game, "Tower Shield", "shield3", self.activities,
      {(255,255,0): (r,g,b), (0,0,128): (r,g,b), (0,0,255): (rr,gg,bb)}))
    self.equipment.append(equipment.Helm(self.game, "Helm of Suck", "helmet", self.activities,
      {(0,0,0):(rr,gg,bb), (128,128,128):(r,g,b)}))
    if random.random() <= 0.5:
      tunic_color = random.choice(clothes_colors)
      self.equipment.append(equipment.Armor(self.game, "Chain Mail", "mail", self.activities,
        {(128,128,128):tunic_color,(0,0,0):tunic_color}))
    hairpiece = equipment.Hairpiece(self.game, 'Hair', "hairpiece", self.activities)
    self.equipment.append(hairpiece)
    if random.random() <= 0.25:
      self.equipment.append(equipment.Beard(self.game, 'Beard', self.activities, hairpiece.palette_swaps))
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 140
    self.avoidance = 0.3
    self.mitigation = 0
    self.min_damage = 4
    self.max_damage = 6
    self.current_hp = self.max_hp
    self.load_animations(self.palette_swaps)
    self.reset()
    t2 = pygame.time.get_ticks()
    if self.game.debug: print "Playermale load time:", t2-t1, "ms"

  def get_attack_targets(self):
    attack_directions = self.current_animation.directions
    targets = []
    for dir in attack_directions:
      (dx, dy) = self.game.dir_to_coords(dir)
      for target_unit in self.game.units:
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
  
  def do_events(self):
    self.next_frame()
    
    # If there's a positional conflict, move out of the way (non-instantaneous)
    for unit in self.game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep()

    # Do walking events
    if self.current_activity == 'walking':
      if self.ticks == 2:
        # Push aside friendly, idle units
        for unit in self.game.units:
          if (unit.x,unit.y) == (self.x+self.dx,self.y+self.dy):
            if unit.hostile == self.hostile:
              if unit.current_activity == 'standing':
                if unit != self.target_unit:
                  unit.knockback((self.dx,self.dy))
        # If something else is in our way, sidestep
        if self.game.obstacle((self.x+self.dx, self.y+self.dy)):
          self.sidestep()
        else:
          # Move
          self.move((self.dx, self.dy))
          self.game.redraw_floor = True
      elif self.ticks == 4:
        self.reset()
        
    elif self.current_activity == 'standing':
      if self.ticks == 4:
        self.reset()
        
    elif self.current_activity == 'attacking':
      if self.ticks == 4:
        self.end_attack()
      elif self.ticks == 8:
        self.reset()
        
    elif self.current_activity == 'bashing':
      if self.ticks == 4:
        self.end_bash()
      elif self.ticks == 8:
        self.reset()
        self.queue_special = False
        self.queue_secondary_special = False        

    elif self.current_activity == 'falling':
      if self.ticks == 8:
        self.refresh_activity('dead')
        self.game.corpses.append(Corpse(self.game, self))
        self.game.remove_unit(self)
        self.selected = False
        return
        
    # Slashing events
    elif self.current_activity == 'slashing':
      if self.ticks < 9:
        # Deal damage on every frame
        self.mid_slash()
      if self.ticks == 10:
        self.reset()
        self.special_ticks = 0
        self.queue_special = False
        self.queue_secondary_special = False        

    # Stunned lasts 16 frames
    elif self.current_activity == 'stunned':
      if self.ticks == 16:
        self.reset()
    
    # Workaround to make sure the unit resets if something weird happens
    if self.ticks >= 16:
      if self.game.debug: print "Sword failsafe"
      self.reset()
    
    if self.ticks == 0:
      if self.current_activity in ['bashing', 'slashing']: #weird
        pass
      else:
        self.get_action()
      
  def load_animations(self, palette_swaps = {}):
    # Load all the animations for this unit.
    t1 = pygame.time.get_ticks()
    # Also used by spearguy, healer, archer, etc. So it includes
    # animations for their specials too.
    frames_surfaces = {}
    for activity in self.activities:
      for dir in self.game.directions:
        frame_filenames = []
        frame_surfaces = []
        if activity == 'walking':
          for x in [1,2]:
            for n in range(2):
              frame_filenames.append('tga/' + self.anim_name + '_walking_' + dir + '_' + str(x) + '.tga')
        elif activity == 'standing':
          for n in range(4):
            frame_filenames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'attacking':
          for x in [1,2,1]:
            for n in range(2):
              frame_filenames.append('tga/' + self.anim_name + '_attacking_' + dir + '_' + str(x) + '.tga')
          frame_filenames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
          frame_filenames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'attacking_club':
          #Twice as long; damage on 8th frame
          for x in [1,1,2,2,2,2,1]:
            for n in range(2):
              frame_filenames.append('tga/' + self.anim_name + '_attacking_' + dir + '_' + str(x) + '.tga')
          frame_filenames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
          frame_filenames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'charging':
          for n in range(10):
            frame_filenames.append('tga/' + self.anim_name + '_attacking_' + dir + '_2.tga')
        elif activity in ['shooting', 'shooting_special']: #originally A1 > A2b > A2b > S1
          for x in ['1','1','2b','2b','2b','2b','1','1']:
            frame_filenames.append('tga/' + self.anim_name + '_attacking_' + dir + '_' + x + '.tga')
          for n in range(8):
            frame_filenames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'throwing': #originally A1 > A2b > A2b > S1
          for x in ['1','1','2b','2b','2b','2b','1','1']:
            frame_filenames.append('tga/' + self.anim_name + '_attacking_' + dir + '_' + x + '.tga')
          for n in range(8):
            frame_filenames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'slashing':
          frame_filenames = []
          frame_surfaces = []
          dir_2 = self.game.rccw(dir)
          frame_filenames.append('tga/' + self.anim_name + '_attacking_' + dir_2 + '_1.tga')
          for n in range(8):
            dir_2 = self.game.rcw(dir_2)
            frame_filenames.append('tga/' + self.anim_name + '_attacking_' + dir_2 + '_2.tga')
          frame_filenames.append('tga/' + self.anim_name + '_attacking_' + dir + '_1.tga')
        elif activity == 'bashing':
          for x in ['1','2b','1',]:
            for n in range(2):
              frame_filenames.append('tga/' + self.anim_name + '_attacking_' + dir + '_' + str(x) + '.tga')
          frame_filenames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
          frame_filenames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'taunting': #Unused
          for x in ['attacking_1', 'standing_1']:
            for n in range(2):
              frame_filenames.append('tga/' + self.anim_name + '_' + x + '.tga')
        elif activity == 'falling':
          if dir in ['S', 'SW', 'W']:
            anim_dir = 'S'
          elif dir in ['NW', 'SE']:
            anim_dir = 'NW'
          elif dir in ['N', 'NE', 'E']:
            anim_dir = 'NE'
          for x in [1,2,3,4,4]: #to compensate for the buggy falling behavior - KLUDGE
            for n in range(2):
              frame_filenames.append('tga/' + self.anim_name + '_falling_' + anim_dir + '_' + str(x) + '.tga')
        elif activity == 'dead':
          if dir in ['S', 'SW', 'W']:
            anim_dir = 'S'
          elif dir in ['NW', 'SE']:
            anim_dir = 'NW'
          elif dir in ['N', 'NE', 'E']:
            anim_dir = 'NE'
          frame_filenames.append('tga/' + self.anim_name + '_falling_' + anim_dir + '_4.tga')
        elif activity == 'decapitated':
          if dir in ['S', 'SW', 'W']:
            anim_dir = 'S'
          elif dir in ['NW', 'SE']:
            anim_dir = 'NW'
          elif dir in ['N', 'NE', 'E']:
            anim_dir = 'NE'
          for x in [1,2,3,4]:
            for n in range(2):
              frame_filenames.append('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_' + str(x) + '.tga')
        elif activity == 'dead_decapitated':
          if dir in ['S', 'SW', 'W']:
            anim_dir = 'S'
          elif dir in ['NW', 'SE']:
            anim_dir = 'NW'
          elif dir in ['N', 'NE', 'E']:
            anim_dir = 'NE'
          frame_filenames.append('tga/' + self.anim_name + '_decapitated_' + anim_dir + '_4.tga')
     
        elif activity == 'stunned':
          anim_directions = self.game.get_slash_directions(dir)
          for d in anim_directions:
            frame_filename = 'tga/' + self.anim_name + '_standing_' + d + '_1.tga'          
            for n in range(2):
              frame_filenames.append(frame_filename)
        # Now we load from filenames.  There are two ways to expedite this:
        # frames_surfaces is a dict that stores every frame already used by this
        # object, and sprite_cache is a dict that stores every frame used by all
        # objects
        
        for frame_filename in frame_filenames:
          try:
            surface = frames_surfaces[frame_filename]#.copy() #Not sure if copy() is necessary here
          except KeyError:
            try:
              surface = self.game.sprite_cache[frame_filename].copy()
              surface = self.game.palette_swap_multi(surface, palette_swaps)
              frames_surfaces[frame_filename] = surface
            except KeyError:
              surface = pygame.image.load(frame_filename).convert()
              surface = self.game.palette_swap_multi(surface, palette_swaps)
              surface.set_colorkey((255,255,255))
              frames_surfaces[frame_filename] = surface
          frame_surfaces.append(surface)
        self.animations.append(Animation(activity, [dir], frame_surfaces, frame_filenames))
    t2 = pygame.time.get_ticks()
    if self.game.debug: print self.anim_name, t2-t1

  def end_attack(self):
    target_unit = self.target_unit
    if not target_unit:
      self.reset()
      return False
    else:  
      can_decapitate = False
      for equip in self.equipment:
        if equip.anim_name in ['sword', 'sword2']:
          can_decapitate = True
      if 'decapitated' not in target_unit.activities:
        can_decapitate = False
      dmg = self.damage()
      if can_decapitate and target_unit.current_activity not in ['falling', \
      'dead','decapited','dead_decapitated'] and target_unit.current_hp > 0 \
      and target_unit.current_hp <= dmg*2 and random.random() > 0.05:
        target_unit.decapitate()
        self.play_hit_sound()
      else:
        target_unit.take_damage(dmg)
        target_unit.bleed(dmg)
        if target_unit.current_hp > 0:
          self.play_hit_sound()

  def end_bash(self):
    target_unit = self.target_unit
    if not target_unit:
      self.reset()
      return False
    else:
      dmg = 10 #Test this value!
      target_unit.take_damage(dmg)
      target_unit.bleed(dmg)
      self.play_bash_sound()
      self.special_ticks = 0
      if (target_unit.anim_name == 'zombie') or (target_unit.anim_name == 'player') \
      or ((target_unit.anim_name == 'robed_wizard') and (target_unit.current_activity in ['casting', 'teleporting'])):
        if target_unit.current_activity not in ['falling', 'dead']:
          for n in range(2):
            self.knockback((self.dx, self.dy))
            target_unit.knockback((self.dx, self.dy))
          self.game.redraw_floor = True
          target_unit.refresh_activity('stunned')
          target_unit.reset_ticks()
          
  def mid_slash(self):
    dir = self.game.coords_to_dir((self.dx, self.dy))
    for n in range(self.ticks-1):
      dir = self.game.rcw(dir)
    (dx,dy) = self.game.dir_to_coords(dir)
    (x,y) = (self.x + dx,self.y + dy)
    target_unit = self.game.obstacle_unit((x,y))
    if target_unit:
      if self.hostile != target_unit.hostile:
        dmg = self.damage()*3
        target_unit.take_damage(dmg)
        (dx,dy) = (target_unit.x - self.x, target_unit.y - self.y)
        knockback_length = 1
        (dx,dy) = (dx*knockback_length,dy*knockback_length)
        target_unit.knockback((dx,dy))
        target_unit.refresh_activity('stunned')
            
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

  def reset(self):
    self.refresh_activity('standing')
    self.reset_ticks()
        
  def get_action(self):
    # After resetting, pick our next behavior based on input etc
    
    # Look for adjacent units
    adjacent_enemy_units = []
    for square in self.game.adjacent_squares((self.x, self.y)):
      for unit in self.game.units:
        if (unit.x, unit.y) == square and unit.hostile != self.hostile:
          adjacent_enemy_units.append(unit)
          
    if self.target_unit:
      if self.queue_special:
        self.move_to_target_unit_special()
      elif self.queue_secondary_special:
        self.move_to_target_unit_special(True)
      else:
        self.move_to_target_unit()
      
    elif (self.target_x, self.target_y) != (None, None):
      self.move_to_target_posn()
      
    elif adjacent_enemy_units:
      self.target_unit = random.choice(adjacent_enemy_units)
      self.move_to_target_unit()
    
  def move_to_target_unit(self):
    target_unit = self.target_unit
    if not target_unit:
      self.target_unit = None
      return
     
    dx = target_unit.x - self.x
    dy = target_unit.y - self.y
    if (dx, dy) == (0,0):
      self.reset()
      self.dx = random.randint(-1,1)
      self.dy = random.randint(-1,1)
      return
    else:
      m = (dx**2 + dy**2)**0.5
      if m != 0:
        #(self.dx, self.dy) = (int(dx/m + 0.5), int(dy/m + 0.5))
        (self.dx, self.dy) = (round(dx/m), round(dy/m))
    for unit in self.game.units:
      if unit != target_unit:
        if unit.hostile == self.hostile:
          if (unit.x,unit.y) == (self.x+self.dx,self.y+self.dy):
            if unit.current_activity == 'standing':
              if unit != self.target_unit:
                unit.knockback((self.dx,self.dy))
    
    if target_unit.hostile != self.hostile:
      if (target_unit.x, target_unit.y) == (self.x + self.dx, self.y + self.dy):    
        self.refresh_activity('attacking')
        self.reset_ticks()
        return
        
    elif not target_unit.playable:
      if (target_unit.x, target_unit.y) == (self.x + self.dx, self.y + self.dy):
        self.refresh_activity('talking')
        self.reset_ticks()
        target_unit.show_dialog(self.name)
        return
      elif self.game.obstacle((self.x + self.dx, self.y + self.dy)):
        if self.game.distance((self.x,self.y), (target_unit.x, target_unit.y)) < 3: #longer distance for bars
          self.refresh_activity('talking')
          self.reset_ticks()
          target_unit.show_dialog(self.name)
          return
          
    if not self.game.obstacle((self.x + self.dx, self.y + self.dy)):
      self.refresh_activity('walking')
      self.reset_ticks()
      return
    elif self.game.obstacle((self.x + self.dx, self.y + self.dy)):
      if (self.x + dx, self.y + self.dy) == (self.target_x, self.target_y):
        self.reset()
      else:
        self.sidestep()
        
  def move_to_target_unit_special(self, secondary=False):
    # defaults to shield bash
    # can be used for slash attack
    if secondary:
      activity_name = self.secondary_special_activity_name
      self.queue_special = False
      self.queue_secondary_special = True
      
    else:
      activity_name = self.special_activity_name
      self.queue_special = True
      self.queue_secondary_special = False
      
    # If we don't have a valid unit targeted, reset or something 
    target_unit = self.target_unit
    if not target_unit:
      return
     
    dx = target_unit.x - self.x
    dy = target_unit.y - self.y
    
    # If we don't point in a valid direction, reset or something
    if (dx, dy) == (0,0):
      self.reset()
      self.dx = random.randint(-1,1)
      self.dy = random.randint(-1,1)
      return
    m = (dx**2 + dy**2)**0.5
    if m != 0:
      #(self.dx, self.dy) = (int(dx/m + 0.5), int(dy/m + 0.5))
      (self.dx, self.dy) = (round(dx/m), round(dy/m))
    dist = self.game.distance((self.x,self.y), (target_unit.x,target_unit.y))
    if target_unit.hostile:
      if dist <= 2:
        self.refresh_activity(activity_name)
        if activity_name == 'slashing':
          self.play_slash_sound()
        self.reset_ticks()
        return
    if not self.game.obstacle((self.x + self.dx, self.y + self.dy)):
      self.refresh_activity('walking')
      self.reset_ticks()
      #at this point, we lose the intention to perform the special attack
      # EXCEPT that we just added the queue_special stuff
      return
      
    # If there's an obstacle in our way, move around it.
    # If there's an obstacle at our destination, reset
    elif self.game.obstacle((self.x + self.dx, self.y + self.dy)):
      if (self.x + dx, self.y + self.dy) == (self.target_x, self.target_y):
        self.reset()
      else:
        self.sidestep()
        
  def move_to_target_posn(self):
    dx = self.target_x - self.x
    dy = self.target_y - self.y
    if (dx, dy) == (0,0):
      (self.target_x, self.target_y) = (None, None)
      self.reset()
      return True
    m = (dx**2 + dy**2)**0.5
    if m != 0:
      #(self.dx, self.dy) = (int(dx/m + 0.5), int(dy/m + 0.5))
      (self.dx, self.dy) = (round(dx/m), round(dy/m))
    target = self.game.obstacle_unit((self.x+self.dx, self.y+self.dy))
    if target:
      if (target.x, target.y) == (self.target_x, self.target_y):
        if target.hostile != self.hostile:
          self.refresh_activity('attacking')
        else:
          if target.current_activity == 'standing':
            target.knockback((self.dx,self.dy))
      else:
        self.sidestep()
    elif self.game.obstacle((self.x+self.dx, self.y+self.dy)):
      self.sidestep()
    else:
      self.refresh_activity('walking')
      self.reset_ticks()
  """
  def sidestep_OLD(self):
    if not self.game.coords_to_dir((self.dx, self.dy)):
      (self.dx,self.dy) = self.game.dir_to_coords(random.choice(self.game.directions))
      
    min_distance = 5
    (target_dx,target_dy) = (None,None)
    for dir in self.game.directions:
      (dx, dy) = self.game.dir_to_coords(dir)
      if not self.game.obstacle((self.x+dx, self.y+dy)):
        if self.game.distance((self.x+dx, self.y+dy), (self.x+self.dx,self.y+self.dy)) < min_distance:
          (target_dx,target_dy) = (dx,dy)
          min_distance = self.game.distance((self.x+dx, self.y+dy), (self.x+self.dx,self.y+self.dy))
    if (target_dx,target_dy) != (None, None):
      (self.dx, self.dy) = (target_dx,target_dy)
      self.refresh_activity('walking')
      return True
    else:
      return False
  """
  def sidestep(self):
    # Finds alternative points closest to current target point, and moves INSTANTLY to one of the closer ones.
    if not self.game.coords_to_dir((self.dx, self.dy)):
      (self.dx,self.dy) = self.game.dir_to_coords(random.choice(self.game.directions))
    distance_dict = {}
    for dir in self.game.directions:
      (dx, dy) = self.game.dir_to_coords(dir)
      if not self.game.obstacle((self.x+dx,self.y+dy)):      
        distance_dict[(dx,dy)] = self.game.distance((self.x+dx, self.y+dy), (self.x+self.dx,self.y+self.dy))
    if len(distance_dict) == 0:
      print self.name, 'sidestep error: no valid directions'
      return False
    distance_dict = sorted(distance_dict, key=(lambda k: distance_dict[k]))
    (target_dx,target_dy) = random.choice(distance_dict[:2])
    if (target_dx,target_dy) != (None, None):
      (self.dx, self.dy) = (target_dx,target_dy)
      self.move((self.dx,self.dy))
      self.reset()
      return True
    else:
      print 'sidestep error misc'
      return False

  def take_damage(self, damage, magic=False):
    if magic:
      self.current_hp = max(0, self.current_hp - damage)
    else:
      if random.random() > self.avoidance:
        self.current_hp = max(0, self.current_hp - int(damage*(1-self.mitigation)))
      else:
        self.play_block_sound()

    if self.current_hp <= 0 and self.current_activity not in ['falling', 'decapitated', 'dead', 'dead_decapitated']:
      self.die()
    self.game.redraw_unit_cards = True

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
    self.load_animations(self.palette_swaps)
    self.reset()

  def load_animations(self, palette_swaps = {}):
    """
    Loads animations automatically, referring to strict naming conventions.
    """
    for activity in self.activities:
      for dir in self.game.directions:
        frames = []
        frame_surfaces = []
        if activity == 'walking':
          # two frames
          for x in [1,2]:
            for n in range(2):
              frames.append('tga/' + self.anim_name + '_walking_' + dir + '_' + str(x) + '.tga')
        elif activity == 'standing':
          for n in range(4):
            frames.append('tga/' + self.anim_name + '_standing_' + dir + '_1.tga')
        elif activity == 'attacking':
          for x in ['attacking_1', 'attacking_2', 'attacking_1', 'standing_1']:
            for n in range(2):
              frames.append('tga/' + self.anim_name + x + '.tga')
        elif activity == 'falling':
          if dir in ['N', 'NE', 'E', 'SE']:
            for x in [1,2,3,3]:
              for n in range(2):
                frames.append('tga/' + self.anim_name + '_falling_' + str(x) + '.tga')
          else:
            for x in [1,2,3,3]:
              for n in range(2):              
               frames.append('tga/' + self.anim_name + '_fallingB_' + str(x) + '.tga')
        elif activity == 'dead':
          if dir in ['N', 'NE', 'E', 'SE']:
            frames.append('tga/' + self.anim_name + '_falling_3.tga')
          else:
            frames.append('tga/' + self.anim_name + '_fallingB_3.tga')
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
        for frame in frames:
          surface = pygame.image.load(frame)
          surface = self.game.palette_swap_multi(surface, palette_swaps)
          surface.set_colorkey((255,255,255))
          frame_surfaces.append(surface)
        self.animations.append(Animation(activity, [dir], frame_surfaces, frames))    

  def scream(self):
    filenames = ["sounds/Girl Scream.ogg", "sounds/Girl Scream2.ogg"]
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(True)
    channel.play(sound)
    
  def get_action(self):
    # PlayerFemale
    adjacent_enemy_units = []
    for square in self.game.adjacent_squares((self.x, self.y)):
      for unit in self.game.units:
        if (unit.x, unit.y) == square and unit.hostile != self.hostile:
          adjacent_enemy_units.append(unit)
    
    if self.target_unit:
      if self.queue_special:
        self.move_to_target_unit_special()
      elif self.queue_secondary_special:
        self.move_to_target_unit_special(True)
      else:
        self.move_to_target_unit()
      
    elif (self.target_x, self.target_y) != (None, None):
      self.move_to_target_posn()
    else:
      #Auto-acquire a nearby target
      min_distance = self.max_distance
      for unit in self.game.units:
        if unit.hostile != self.hostile and self.game.distance((self.x, self.y), \
        (unit.x, unit.y)) < 5:
          if self.game.distance((self.x,self.y), (unit.x,unit.y)) < min_distance:
            self.target_unit = unit
            min_distance = self.game.distance((self.x, self.y), (unit.x, unit.y))
          #self.target_unit = unit # I do not understand this line
      if self.target_unit:
        self.move_to_target_unit()
      
  def do_events(self):
    """ Player Female """
    self.next_frame()    
    for unit in self.game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep()
          self.reset()
          return
          
    if self.target_unit:
      target_unit = self.target_unit
      if target_unit.current_hp <= 0 and target_unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
        target_unit.reset()
        target_unit.refresh_activity('falling')
    if self.ticks == 1:
      if self.current_activity == 'walking':
        for unit in self.game.units:
          if (unit.x,unit.y) == (self.x+self.dx,self.y+self.dy):
            if unit.hostile == self.hostile:
              if not unit.playable:
                if unit.ally:
                  unit.knockback((self.dx,self.dy))    
        if self.game.obstacle((self.x+self.dx, self.y+self.dy)):
          self.sidestep()
        else:
          self.move((self.dx, self.dy))
    if self.ticks == 2:
      if self.current_activity == 'walking':
        self.reset()
      if self.current_activity == 'standing':
        self.reset()
      if self.current_activity == 'attacking':
        self.game.darts.append(Dart(self.game, 10, self, self.target_unit))
        
    if self.ticks == 4:
      if self.current_activity == 'attacking':
        self.reset()
      elif self.current_activity == 'falling':
        self.refresh_activity('dead')
        self.game.corpses.append(Corpse(self.game, self))
        self.selected = False
        for unit in self.game.units:
          if unit.target_unit == self:
            unit.target_unit = None
        self.game.remove_unit(self)
        return True
      else:
        self.reset()
        
    if self.ticks == 0:
      self.get_action()
    
  def move_to_target_unit(self):
    target_unit = self.target_unit
    if not target_unit:
      return False
     
    dx = target_unit.x - self.x
    dy = target_unit.y - self.y
    if (dx, dy) == (0,0):
      self.reset()
      self.dx = random.randint(-1,1)
      self.dy = random.randint(-1,1)     
    else:      
      m = (dx**2 + dy**2)**0.5
      if m != 0:
        #(self.dx, self.dy) = (int(dx/m + 0.5), int(dy/m + 0.5))
        (self.dx, self.dy) = (round(dx/m), round(dy/m))
    # NPC!
    if (not target_unit.playable) and (not target_unit.hostile) and (not target_unit.ally):
      if (self.x+self.dx, self.y+self.dy) == (target_unit.x,target_unit.y):
        self.refresh_activity('talking')
        target_unit.show_dialog(self.name)
      elif self.game.obstacle((self.x+self.dx,self.y+self.dy)):
        self.sidestep()
      else:
        self.refresh_activity('walking')
        self.reset_ticks()
    elif target_unit.hostile:
      dist = self.game.distance((self.x,self.y), (target_unit.x,target_unit.y))
      if dist >= 4 and dist <= 10:
        self.refresh_activity('attacking')
        self.reset_ticks()
      else:
        if dist < 4:
          (self.dx, self.dy) = (-self.dx, -self.dy)
        if not self.game.obstacle((self.x + self.dx, self.y + self.dy)):
          self.refresh_activity('walking')
          self.reset_ticks()          
        elif self.game.obstacle((self.x + self.dx, self.y + self.dy)):
          if (self.x + dx, self.y + self.dy) == (self.target_x, self.target_y):
            self.reset()
          else:
            self.sidestep()
    
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
    self.queue_special = False
    self.queue_secondary_special = False    
    clothes_colors = [(128,0,0), (0,128,0), (0,0,128), (128,128,64),
                    (64,64,64), (128,128,128)]
    belt_colors = [(64,64,64), (128,64,0)]
    self.palette_swaps.update({(128,128,64):random.choice(clothes_colors), #shirt
                               (128,64,0):random.choice(clothes_colors), #pants
                               (128,128,0):random.choice(belt_colors)}) #belt
    armor_colors = [(128,128,128), (64,64,64), (192,96,32), (128,128,192)]
    self.activities = ['standing', 'walking', 'attacking', 'charging', 'falling', 'dead']
    self.equipment = [equipment.Spear(self.game, "Spear", "spear", self.activities)]
    armor_colors = [(128,128,128), (192,96,32), (128,128,192), (64,64,64)]
    (r,g,b) = random.choice(armor_colors)
    (rr,gg,bb) = (int(r/2),int(g/2),int(b/2))
    (rrr,ggg,bbb) = (min(r*2,255),min(g*2,255),min(b*2,255))
    self.equipment.append(equipment.Shield(self.game, "Shield of Suck", "shield2", self.activities,
      {(128,128,128):(rr,gg,bb), (192,192,192): (r,g,b)}))
    self.equipment.append(equipment.Helm(self.game, "Helm2", "helm2", self.activities,
      {(128,128,128):(r,g,b), (192,192,192): (rrr,ggg,bbb)}))
    if random.random() <= 0.5:
      tunic_color = random.choice(clothes_colors)
      self.equipment.append(equipment.Armor(self.game, "Chain Mail", "mail", self.activities,
        {(128,128,128):tunic_color,(0,0,0):tunic_color}))
    hairpiece = equipment.Hairpiece(self.game, 'Hair', "hairpiece", self.activities)
    self.equipment.append(hairpiece)
    if random.random() <= 0.25:
      self.equipment.append(equipment.Beard(self.game, 'Beard', self.activities, hairpiece.palette_swaps))

    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 120
    self.current_hp = self.max_hp
    self.load_animations(self.palette_swaps)
    self.reset()
    self.avoidance = 0.3
    self.mitigation = 0
    self.min_damage = 6
    self.max_damage = 8
    t2 = pygame.time.get_ticks()
    if self.game.debug: print "Altplayermale load time:", t2-t1, "ms"
    
  def get_attack_targets(self):
    target_unit = self.target_unit
    if target_unit:
      return [target_unit]
    else:
      return None
      
  def end_attack(self):
    target_unit = self.target_unit
    if not target_unit:
      self.reset()
      return False
    else:
      dmg = self.damage()
      target_unit.take_damage(dmg)
      target_unit.bleed(dmg)
      self.play_hit_sound()
      
  def do_charge_damage(self):
    target_unit = self.target_unit
    if not target_unit:
      self.reset()
      return False
    else:
      dmg = 3
      target_unit.take_damage(dmg)
      target_unit.bleed(dmg)
    
  def get_action(self):
    """ Alt Player [Spear Guy] """
    adjacent_enemy_units = []
    #Radius 2
    for unit in self.game.units:
      if unit.hostile != self.hostile:
        if self.game.distance((self.x,self.y),(unit.x, unit.y)) <= 2:
          adjacent_enemy_units.append(unit)
          
    if self.current_activity == 'charging':
      if self.target_unit:
        self.charge_at_unit()
      else:
        self.reset()
        #print 'bad spearman'
    elif self.target_unit:
      if self.queue_special:
        self.move_to_target_unit_special()
      else:
        self.move_to_target_unit()
      
    elif (self.target_x, self.target_y) != (None, None):
      self.move_to_target_posn()
      
    elif adjacent_enemy_units:
      self.target_unit = random.choice(adjacent_enemy_units)
      self.move_to_target_unit()
      
  def do_events(self):
    self.next_frame()
    for unit in self.game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep()
    
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
          self.game.redraw_floor = True
      elif self.ticks == 4:
        self.reset()
        
    if self.current_activity == 'standing':
      if self.ticks == 4:
        self.reset()

    elif self.current_activity == 'attacking':
      if self.ticks == 4:
        self.end_attack()
      elif self.ticks == 8:
        self.reset()
        
    elif self.current_activity == 'falling':
      if self.ticks == 8:      
        self.refresh_activity('dead')
        self.game.corpses.append(Corpse(self))
        self.selected = False
        for unit in self.game.units:
          if unit.target_unit == self:
            unit.target_unit = None
        self.game.remove_unit(self)
        return True
        
    elif self.current_activity == 'charging':
      self.charge_at_unit()
      if self.ticks == 5:
        self.reset()
        self.special_ticks = 0
        self.queue_special = False
        self.queue_secondary_special = False


    if self.ticks >= 16:
      if self.game.debug: print "Spear failsafe"
      self.reset()
        
    if self.ticks == 0:
      self.get_action()
    
  def move_to_target_unit(self):
    target_unit = self.target_unit
    if not target_unit:
      self.target_unit = None
      return False
     
    dx = target_unit.x - self.x
    dy = target_unit.y - self.y
    if (dx, dy) == (0,0):
      self.reset()
      self.dx = random.randint(-1,1)
      self.dy = random.randint(-1,1)
    else:
      m = (dx**2 + dy**2)**0.5
      if m != 0:
        #(self.dx, self.dy) = (int(dx/m + 0.5), int(dy/m + 0.5))
        (self.dx, self.dy) = (round(dx/m), round(dy/m))
    # NPC!
    if (not target_unit.playable) and (not target_unit.hostile) and (not target_unit.ally):
      if (self.x+self.dx, self.y+self.dy) == (target_unit.x,target_unit.y):
        self.refresh_activity('talking')
        target_unit.show_dialog(self.name)
      elif not self.game.obstacle((self.x + self.dx, self.y + self.dy)):
        self.refresh_activity('walking')
        self.reset_ticks()
      elif self.game.obstacle((self.x + self.dx, self.y + self.dy)):
        self.sidestep()
        
    elif target_unit.hostile != self.hostile:
      dist = self.game.distance((self.x,self.y), (target_unit.x,target_unit.y))
      if dist > 1.5 and dist < 3:
        unit = self.game.obstacle_unit((self.x+self.dx, self.y+self.dy))
        if unit:
          if not unit.hostile:
            if unit.playable or unit.ally:
              self.sidestep()
              return True
        self.refresh_activity('attacking')
        self.reset_ticks()
      else:
        if dist <= 1.5: #too close, walk back
          (self.dx, self.dy) = (-self.dx, -self.dy)
        if not self.game.obstacle((self.x + self.dx, self.y + self.dy)):
          self.refresh_activity('walking')
          self.reset_ticks()
          
        elif self.game.obstacle((self.x + self.dx, self.y + self.dy)):
          #if (self.x + dx, self.y + self.dy) == (self.target_x, self.target_y):
          #  self.reset()
          #else:
          self.sidestep()
          
  def charge_at_unit(self):
    unit = self.target_unit
    if not unit:
      self.target_unit = None
      self.reset()
      return False
    
    if not self.game.obstacle((self.x + self.dx, self.y + self.dy)):
      pass
    elif self.game.obstacle_unit((self.x + self.dx, self.y + self.dy)):
      unit_2 = self.game.obstacle_unit((self.x + self.dx, self.y + self.dy))
      if unit_2 != unit:
        (dx,dy) = (self.dx,self.dy)
        while (dx,dy) in [(self.dx,self.dy), (-self.dx,-self.dy)]:
          dir = random.choice(self.game.directions)
          (dx,dy) = self.game.dir_to_coords(dir)
        unit_2.knockback((dx,dy))
    else:
      self.reset()
      return
    
    #if the path is clear:

    self.special_ticks = 0
    self.move((self.dx,self.dy))
    self.game.redraw_floor = True
    dist = self.game.distance((self.x,self.y), (unit.x,unit.y))
    if dist <= 1.5:
      self.do_charge_damage()
      unit_2 = self.game.obstacle_unit((unit.x + self.dx, unit.y + self.dy))
      if unit_2:
        (dx,dy) = (self.dx,self.dy)
        while (dx,dy) in [(self.dx,self.dy), (-self.dx,-self.dy)]:
          dir = random.choice(self.game.directions)
          (dx,dy) = self.game.dir_to_coords(dir)
        unit_2.knockback((dx,dy))
      unit.knockback((self.dx, self.dy))
    else:
      dx = unit.x - self.x
      dy = unit.y - self.y
      if (dx, dy) == (0,0):
        self.reset()
        unit.reset()
        self.special_ticks = 0
        return
      m = (dx**2 + dy**2)**0.5
      if m != 0:
        #(self.dx, self.dy) = (int(dx/m + 0.5), int(dy/m + 0.5))
        (self.dx, self.dy) = (round(dx/m), round(dy/m))
          
  def move_to_target_unit_special(self, secondary=False):
    if secondary:
      activity_name = self.secondary_special_activity_name
      self.queue_special = False
      self.queue_secondary_special = True
      
    else:
      activity_name = self.special_activity_name
      self.queue_special = True
      self.queue_secondary_special = False
      
    target_unit = self.target_unit
    if not target_unit:
      self.reset()
      return
     
    dx = target_unit.x - self.x
    dy = target_unit.y - self.y
    if (dx, dy) == (0,0):
      self.reset()
      self.dx = random.randint(-1,1)
      self.dy = random.randint(-1,1)     
      return
    m = (dx**2 + dy**2)**0.5
    if m != 0:
      #(self.dx, self.dy) = (int(dx/m + 0.5), int(dy/m + 0.5))
      (self.dx, self.dy) = (round(dx/m), round(dy/m))
    dist = self.game.distance((self.x,self.y), (target_unit.x,target_unit.y))
    if target_unit.hostile:
      if activity_name == 'charging':
        if dist <= 5:
          self.refresh_activity(activity_name)
          self.reset_ticks()
          self.play_charge_sound()
          return
      else:
        #NYI!
        if dist <= 2:
          self.refresh_activity(activity_name)
          self.reset_ticks()
          return
    if not self.game.obstacle((self.x + self.dx, self.y + self.dy)):
      self.refresh_activity('walking')
      self.reset_ticks()
      #at this point, we lose the intention to perform the special attack
      #not anymore?
      return
    elif self.game.obstacle((self.x + self.dx, self.y + self.dy)):
      if (self.x + dx, self.y + self.dy) == (self.target_x, self.target_y):
        self.reset()
      else:
        self.sidestep()

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
    self.equipment = [equipment.make(self.game, 'scepter')]
    self.equipment.append(equipment.make(self.game, 'white_wizard_cloak'))
    hair = equipment.Hairpiece(self.game, 'Hair of Suck', 'hairpiece')
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
    self.reset()

  def increment_ticks(self):
    self.ticks += 1
        
  def do_events(self):
    self.next_frame()  
    """ Modified player action tree """
    for unit in self.game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep()
          self.reset()
    if self.target_unit:
      unit = self.target_unit
      if unit.current_hp <= 0 and unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
        unit.reset()
        unit.refresh_activity('falling')
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
        self.reset()
        
    if self.ticks == 2:
      if self.current_activity == 'attacking':
        self.end_attack()        
        
    if self.ticks == 4:
      if self.current_activity == 'attacking':
        self.reset()
        
      elif self.current_activity == 'falling':
        self.refresh_activity('dead')
        self.game.corpses.append(Corpse(self.game, self))
        self.selected = False
        for unit in self.game.units:
          if unit.target_unit == self:
            unit.target_unit = None
        self.game.remove_unit(self)
        return True
      elif self.current_activity == 'healing':
        self.reset()
        self.refresh_activity('healing')
        for unit in self.game.units:
          if unit.hostile == self.hostile:
            if self.game.distance((self.x,self.y), (unit.x,unit.y)) <= 12:
              if unit.current_hp < unit.max_hp:
                if unit.current_hp > 0:
                  if unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
                    unit.current_hp = min(unit.current_hp + self.heal_amount, unit.max_hp)
      elif self.current_activity == 'standing':
        self.reset()
        self.refresh_activity('healing')
      else:
        self.reset()
    if self.ticks == 0:
      self.get_action()      
      
  def load_animations(self, palette_swaps = {}):
    """
    Loads animations automatically, referring to strict naming conventions.
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
              surface = self.game.palette_swap_multi(surface, palette_swaps)
              surface.set_colorkey((255,255,255))
              overlay_surface = pygame.image.load('tga/fireball_forming_' + dir + '_1.tga')
              overlay_surface.set_colorkey((255,255,255))
              surface.blit(overlay_surface, (0,0))
              frame_surfaces.append(surface)
              surface = pygame.image.load(frames[1])
              surface = self.game.palette_swap_multi(surface, palette_swaps)
              surface.set_colorkey((255,255,255))
              frame_surfaces.append(surface)
              self.animations.append(Animation(activity, [dir], frame_surfaces, frames))
            elif activity == 'healing':
              for x in range(1,5):
                filename = 'tga/' + self.anim_name + '_standing_SE_1.tga'
                frames.append(filename)
                player_surface = pygame.image.load(filename)
                player_surface.set_colorkey((255,255,255))
                surface = self.game.palette_swap_multi(surface, palette_swaps)
                glow_surface = pygame.image.load('tga/goldenglow_' + str(x) + '.tga')
                glow_surface.set_colorkey((255,255,255))
                glow_surface.blit(player_surface, (0,0))
                frame_surfaces.append(glow_surface)
              self.animations.append(Animation(activity, [dir], frame_surfaces, frames))
            elif activity == 'stunned':
              anim_directions = []
              i = self.game.directions.index(dir)
              for d in self.game.directions:
                j = self.game.directions.index(d)
                if j >= i:
                  anim_directions.append(d)
              for d in self.game.directions:
                j = self.game.directions.index(d)                       
                if j < i:
                  anim_directions.append(d)
              for d in anim_directions:
                frame = 'tga/' + self.anim_name + '_standing_' + d + '_1.tga'
                frames.append(frame)
                    
            # now we load from filenames
            if activity != 'healing':
              for frame in frames:
                surface = pygame.image.load(frame)
                surface = self.game.palette_swap_multi(surface, palette_swaps)
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
                      equipment.make(self.game, 'blue_chain_mail'),
                      equipment.make(self.game, 'sword_of_suck'),
                      equipment.make(self.game, 'iron_shield'),
                      equipment.Hairpiece(self.game, 'Hair', 'hairpiece'),
                      equipment.make(self.game, 'helm_of_suck')
                     ]
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.current_hp = self.max_hp
    self.load_animations(self.palette_swaps)
    self.reset()
    
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
                      equipment.make(self.game, 'blue_chain_mail'),
                      equipment.make(self.game, 'sword_of_suck'),
                      equipment.make(self.game, 'tower_shield'),
                      equipment.Hairpiece(self.game, 'Hair', 'hairpiece'),
                      equipment.make(self.game, 'officer_helm')
                     ]
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'bashing', 'falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.special_ticks = 30
    self.max_special_ticks = 30
    self.current_hp = self.max_hp
    self.load_animations(self.palette_swaps)
    self.reset()
    

    
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
    self.equipment = [equipment.make(self.game, 'sword_of_suck')]
    hair = equipment.Hairpiece(self.game, 'Hair of Suck', 'hairpiece')
    self.equipment.append(hair)
    self.equipment.append(equipment.Hairpiece(self.game, 'Beard of Suck', 'beard', hair.palette_swaps))
    self.equipment.append(equipment.make(self.game, 'cloak_of_the_forest'))
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'healing', 'falling', 'dead', 'decapitated', 'dead_decapitated']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100    
    self.heal_amount = 2
    self.current_hp = self.max_hp
    self.load_animations(self.palette_swaps)
    self.reset()
    
  def do_events(self):
    self.next_frame()
    """ Modified player action tree """
    for unit in self.game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep()
    if self.target_unit:
      unit = self.target_unit
      if unit.current_hp <= 0 and unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
        unit.reset()
        unit.refresh_activity('falling')
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
        self.reset()
        
    if self.ticks == 2:
      if self.current_activity == 'attacking':
        self.end_attack()        
        
    if self.ticks == 4:
      if self.current_activity == 'attacking':
        self.reset()
        
      elif self.current_activity == 'falling':
        self.refresh_activity('dead')
        self.game.corpses.append(Corpse(self.game, self))
        self.selected = False
        for unit in self.game.units:
          if unit.target_unit == self:
            unit.target_unit = None
        self.game.remove_unit(self)
        return True
      elif self.current_activity == 'healing':
        min_percent_hp = 100
        healing_target = None
        for unit in self.game.units:
          if unit.hostile == self.hostile:
            if self.game.distance((self.x,self.y), (unit.x,unit.y)) <= 10:
              if unit.current_hp > 0 and unit.current_hp < unit.max_hp:
                if unit.current_activity not in ['falling', 'dead', 'decapitated', 'dead_decapitated']:
                  percent_hp = unit.current_hp/unit.max_hp
                  if percent_hp < min_percent_hp:
                    healing_target = unit
                    min_percent_hp = percent_hp
        if healing_target:
          unit = healing_target
          if unit:
            unit.current_hp = min(unit.current_hp + self.heal_amount, unit.max_hp)

        self.reset()
        self.refresh_activity('healing')
      elif self.current_activity == 'standing':
        self.reset()
        self.refresh_activity('healing')
      else:
        self.reset()
    if self.ticks == 0:
      self.get_action()
    
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
                      equipment.make(self.game, "sword_of_suck", True),
                      equipment.make(self.game, "helm_of_suck", True)
                     ]
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.current_hp = self.max_hp
    self.load_animations(self.palette_swaps)
    self.reset()
    
  def load_animations(self, palette_swaps):
    PlayerFemale.load_animations(self, palette_swaps)

  def do_events(self):
    PlayerMale.do_events(self)
    
  def get_action(self):
    PlayerMale.get_action(self)
    
  def move_to_target_unit(self):
    PlayerMale.move_to_target_unit(self)
  
  def end_attack(self):
    target_unit = self.target_unit
    if not target_unit:
      self.reset()
      return False
    else:
      can_decapitate = False
      #for equip in self.equipment:
      #  if equip.anim_name in ['sword', 'sword2']:
      #    can_decapitate = True
      #if 'decapitated' not in target_unit.activities:
      #  can_decapitate = False
      dmg = self.damage()
      if can_decapitate and target_unit.current_activity not in ['falling', \
      'dead','decapited','dead_decapitated'] and target_unit.current_hp > 0 \
      and target_unit.current_hp <= dmg*3 and random.random() > 0.05:
        target_unit.bleed(target_unit.current_hp)
        target_unit.current_hp = 0
        target_unit.reset()
        target_unit.refresh_activity('decapitated')
        self.play_hit_sound()
      else:
        target_unit.take_damage(dmg)
        
        # Healing code here.  Rest of the function is just PlayerMale.end_attack()
        healing_target = None
        for u in self.game.units:
          if u.hostile == self.hostile:
            if self.game.distance((u.x,u.y),(self.x,self.y)) <= 5:
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
          self.game.healing_flashes.append(HealingFlash(self.game, healing_target))
        # End healing code
        
        target_unit.bleed(dmg)
        if target_unit.current_hp > 0:
          self.play_hit_sound()
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
        self.game.remove_unit(self)
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
        equip.draw(self.game, x, y)
        
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
            
class PlayerArcher(PlayerFemale, PlayerMale):
  def __init__(self, game, name, (x,y)):
    t1 = pygame.time.get_ticks()
    BasicUnit.__init__(self, game, name, 'player', (x,y))
    self.activities = ['standing', 'walking', 'shooting', 'shooting_special', 'falling', 'dead']
    self.hostile = False
    self.playable = True
    self.ally = False
    self.has_special = True
    self.has_secondary_special = False
    self.special_activity_name = "shooting_special"
    self.special_ticks = self.max_special_ticks = 80
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
    self.equipment = [equipment.Hairpiece(self.game, "Hair", "hairpiece", self.activities, {(0,0,0):random.choice(hair_colors)}),
                      equipment.Bow(self.game, "Green Bow", self.activities, {(0,255,0):(190,170,150)}),
                      equipment.Helm(self.game, "Green Helm", "hat2", self.activities,
                        {(0,0,128):(0,128,0), (0,0,255):(0,192,0), (0,128,255):(0,192,128)}),
                      equipment.Armor(self.game, "Brown Bandit Tunic", "mail", self.activities,
                        {(128,128,128):(128,64,0), (0,0,0):(85,43,0)})
                      ]
    self.inventory = []
    self.current_activity = 'standing'
    self.animations = []
    self.current_hp = self.max_hp = 80
    self.avoidance = self.mitigation = 0
    self.current_hp = self.max_hp
    
    self.queue_special = False
    self.queue_secondary_special = False
    
    self.min_distance = 6
    self.max_distance = 12
    self.min_damage = 8
    self.max_damage = 12
    self.load_animations(self.palette_swaps)
    self.reset()
    t2 = pygame.time.get_ticks()
    if self.game.debug: print "Archer load time:", t2-t1
    
  def load_animations(self, palette_swaps={}):
    PlayerMale.load_animations(self, palette_swaps)
  
  def get_action(self):
    PlayerFemale.get_action(self)
  
  def scream(self):
    PlayerMale.scream(self)
  
  def do_events(self):
    self.next_frame()  
    for unit in self.game.units:
      if unit != self:
        if (unit.x, unit.y) == (self.x, self.y):
          self.sidestep()
    if self.target_unit:
      u = self.target_unit
      if u.current_hp <= 0 and u.current_activity not in ['falling', 'dead', \
      'decapitated', 'dead_decapitated']:
        self.target_unit.reset()
        self.target_unit.refresh_activity('falling')
    if self.ticks == 2:
      if self.current_activity == 'walking':
        for unit in self.game.units:
          if (unit.x,unit.y) == (self.x+self.dx,self.y+self.dy):
            if unit.hostile == self.hostile:
              if not unit.playable:
                if unit.ally:
                  unit.knockback((self.dx,self.dy))    
        if self.game.obstacle((self.x+self.dx, self.y+self.dy)):
          self.sidestep()
        else:
          self.move((self.dx,self.dy))
          self.game.redraw_floor = True
    if self.ticks == 4:
      if self.current_activity == 'standing':
        self.reset()
      elif self.current_activity == 'walking':
        self.reset()        
      elif self.current_activity == 'shooting':
        arrow_damage = random.randint(self.min_damage, self.max_damage)
        self.game.darts.append(Arrow(self.game, arrow_damage, self, self.target_unit))
      elif self.current_activity == 'shooting_special':
        # Need to figure out special damage
        arrow_damage = random.randint(self.min_damage*2, self.max_damage*2)
        # Need to define StunArrow class
        self.game.darts.append(StunArrow(self.game, arrow_damage, self, self.target_unit))
        self.special_ticks = 0
        self.queue_special = False
        
    if self.ticks == 8:
      if self.current_activity in ['shooting', 'shooting_special']:
        pass#so we don't reset; shot will cooldown @ 16
      elif self.current_activity == 'falling':
        self.refresh_activity('dead')
        self.game.corpses.append(Corpse(self.game, self))
        self.selected = False
        for unit in self.game.units:
          if unit.target_unit == self:
            unit.target_unit = None
        self.game.remove_unit(self)
        return True
      else:
        self.reset()
        
    if self.ticks == 16:
      if self.current_activity in ['shooting', 'shooting_special']:
        self.reset()
      else:
        if self.game.debug: print "Archer failsafe"
        self.reset()
        
    if self.ticks == 0:
      self.get_action()
      
  def move_to_target_unit(self, shooting_activity="shooting"):
    # same as PlayerFemale, but uses "shooting" instead of "attacking"
    if not self.target_unit:
      return False
     
    target_unit = self.target_unit
    dx = target_unit.x - self.x
    dy = target_unit.y - self.y
    # If our orientation is buggy, reset the unit
    if (dx, dy) == (0,0):
      self.reset()
      self.dx = random.randint(-1,1)
      self.dy = random.randint(-1,1)
    else:      
      m = (dx**2 + dy**2)**0.5
      if m != 0:
        #(self.dx, self.dy) = (int(dx/m + 0.5), int(dy/m + 0.5))
        (self.dx, self.dy) = (round(dx/m), round(dy/m))

    # Move towards an NPC to talk to it
    if (not target_unit.playable) and (not target_unit.hostile) and (not target_unit.ally):
      if (self.x+self.dx, self.y+self.dy) == (target_unit.x,target_unit.y):
        self.refresh_activity('talking')
        target_unit.show_dialog(self.name)
      elif self.game.obstacle((self.x+self.dx,self.y+self.dy)):
        self.sidestep()
      else:
        self.refresh_activity('walking')
        
    # Move towards an enemy to shoot at it
    elif target_unit.hostile:
      dist = self.game.distance((self.x,self.y), (target_unit.x,target_unit.y))
      if dist >= self.min_distance and dist <= self.max_distance and \
      self.game.LOS((self.x,self.y), (target_unit.x,target_unit.y)):
        self.refresh_activity(shooting_activity)
        
        # If special, set mana to 0 and unqueue special
        if shooting_activity == self.special_activity_name:
          self.special_ticks = 0
          self.queued_special = self.queued_secondary_special = False
      else:
        if dist < self.min_distance:
          (self.dx, self.dy) = (-self.dx, -self.dy)
        if not self.game.obstacle((self.x + self.dx, self.y + self.dy)):
          self.refresh_activity('walking')
        elif self.game.obstacle((self.x + self.dx, self.y + self.dy)):
          if (self.x + dx, self.y + self.dy) == (self.target_x, self.target_y):
            self.reset()
          else:
            self.sidestep()
            
  def move_to_target_unit_special(self, secondary=False):
    # Same as the basic shooting behavior, except that we'll use the special activity
    if secondary:
      activity_name = self.secondary_special_activity_name
      self.queue_special = False
      self.queue_secondary_special = True
      
    else:
      activity_name = self.special_activity_name
      self.queue_special = True
      self.queue_secondary_special = False
    self.move_to_target_unit(activity_name)

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
    self.evade_speed = 0.5
    self.load_animations(self.palette_swaps)
    self.reset()
    
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
        
    elif self.current_activity == 'decapitated':
      if self.ticks == 8:
        self.refresh_activity(self.game, 'dead_decapitated')
        self.game.corpses.append(Corpse(self.game, self))
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
    # I forget why this is different from EnemyMale
    target_unit = self.target_unit
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
            self.refresh_activity('attacking')
          elif self.game.obstacle_unit((self.x+self.dx, self.y+self.dy)):
            unit_2 = self.game.obstacle_unit((self.x+self.dx, self.y+self.dy))
            if unit_2.hostile != self.hostile:
              self.target_unit = unit_2
              self.refresh_activity('attacking')  
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
      
  def draw(self):
    """
    self.sort_equipment()
    (x,y) = grid_to_pixel(self.x, self.y)
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
    """
    PlayerMale.draw(self)
    
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    x += 4
    y -= 24
    alpha = 0
    for unit in self.game.units:
      if not unit.hostile:
        if unit.target_unit == self:
          alpha = 255
          break
        elif self.game.distance((self.x,self.y), (unit.x,unit.y)) <= 12:
          alpha = 128
        elif self.game.distance((self.x,self.y), (unit.x,unit.y)) <= 18:
          if alpha < 64:
            alpha = 64
    self.game.screen.blit(self.draw_hp_bar(16, 5, alpha), (x,y))
