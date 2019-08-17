from __future__ import division
import pygame
import random
# We should always do imports this way
from units import BasicUnit, EnemyMale
from classes import Animation, Pointer, Corpse, HealthPowerup

class EnemyZombie(EnemyMale):
  # aka weak zombie
  def __init__(self, game, name, (x,y), palette_swaps=None):
    BasicUnit.__init__(self, game, name, 'zombie', (x,y))  
    self.hostile = True
    self.playable = False
    self.ally = False    
    self.has_special = False
    if palette_swaps:
      self.palette_swaps = palette_swaps
    else:
      #clothes
      r = random.randint(80,160)
      g = random.randint(80,160)
      b = random.randint(80,160)
      clothes_color = (r,g,b)
      #skin
      r = random.randint(180, 230)
      g = random.randint(int(r*0.6), int(r*0.9))
      b = random.randint(int(r*0.6), int(r*0.9))
      skin_color = (r,g,b)
      self.palette_swaps = {(128,128,128):clothes_color,
                            (186,183,120):skin_color}
    self.vision_radius = 10
    self.smell_radius = 20
    self.equipment = []
    self.inventory = []
    self.activities = ['standing', 'walking', 'attacking', 'stunned', 'falling', 'dead', 'decapitated', \
                       'dead_decapitated', 'lurching', 'rising']
    self.current_activity = 'standing'
    self.animations = []
    self.current_hp = self.max_hp = 90
    self.avoidance = 0
    self.mitigation = 0
    self.min_damage = 5
    self.max_damage = 8
    self.move_frequency_1 = 0.3
    self.move_frequency_2 = 0.5
    self.lurch_frequency = 0.6
    self.load_animations(game, self.palette_swaps)
    self.reset(game)
    
  def load_animations(self, game, palette_swaps = {}):
    frames_surfaces = {}
    for activity in self.activities:
      for dir in game.directions:
        frames = []
        frame_surfaces = []
        if activity == 'walking':
          for x in [1,1,1,2,2,2]:
            frames.append('tga/' + self.anim_name + '_walking_' + dir + '_' + str(x) + '.tga')
        elif activity == 'lurching':
          for x in [1,1,2]:
            #2 tiles in 3 frames
            frames.append('tga/' + self.anim_name + '_walking_' + dir + '_' + str(x) + '.tga')
        elif activity == 'rising':
          for x in [1,2,3,4]:
            for n in range(2):
              frames.append('tga/' + self.anim_name + '_rising_' + str(x) + '.tga')
        elif activity == 'standing':
          for x in [1,1,2,2]:
            frames.append('tga/' + self.anim_name + '_standing_' + dir + '_' + str(x) + '.tga')
        elif activity == 'attacking':
          # 2 standing, 6 attacking, 4 standing = 12
          for x in [1,1]:
            frames.append('tga/' + self.anim_name + '_standing_' + dir + '_' + str(x) + '.tga')          
          for x in [1,1,2,2,1,1]:
            frames.append('tga/' + self.anim_name + '_attacking_' + dir + '_' + str(x) + '.tga')
          for x in [1,1,2,2]:
            frames.append('tga/' + self.anim_name + '_standing_' + dir + '_' + str(x) + '.tga')
        elif activity == 'falling':
          if dir in ['N', 'NE', 'E', 'SE']:
            for x in [1,1,2,2,3,3,3,3]:
              frames.append('tga/' + self.anim_name + '_falling_' + str(x) + '.tga')
          else:
            for x in [1,1,2,2,3,3,3,3]:
              frames.append('tga/' + self.anim_name + '_fallingB_' + str(x) + '.tga')
        elif activity == 'stunned':
          anim_directions = game.get_slash_directions(dir)
          for d in anim_directions:
            for n in range(2):
              frame = 'tga/' + self.anim_name + '_standing_' + d + '_1.tga'
              frames.append(frame)
        elif activity == 'dead':
          for n in range(6):
            if dir in ['N', 'NE', 'E', 'SE']:
              frames.append('tga/' + self.anim_name + '_falling_3.tga')
            else:
              frames.append('tga/' + self.anim_name + '_fallingB_3.tga')
        elif activity == 'decapitated':
          for x in [1,2,3,3]:
            for n in range(2):
              frame = 'tga/' + self.anim_name + '_decapitated_' + str(x) + '.tga'
              frames.append(frame)
              surface = pygame.image.load(frame)
              head_surface = pygame.image.load('tga/zombiehead_falling_' + str(x) + '.tga')
              head_surface.set_colorkey((255,255,255))
              surface.blit(head_surface, (0,0))
              surface = game.palette_swap_multi(surface, palette_swaps)
              surface.set_colorkey((255,255,255))
              surface.convert()
              frame_surfaces.append(surface)
          self.animations.append(Animation(activity, [dir], frame_surfaces, frames))
        elif activity == 'dead_decapitated':
          frame = 'tga/' + self.anim_name + '_decapitated_3.tga'
          for x in [4,5,6]:
            frames.append(frame)
            surface = pygame.image.load(frame)
            head_surface = pygame.image.load('tga/zombiehead_falling_' + str(x) + '.tga')
            head_surface.set_colorkey((255,255,255))
            surface.blit(head_surface, (0,0))
            surface = game.palette_swap_multi(surface, palette_swaps)
            surface.set_colorkey((255,255,255))
            surface.convert()
            frame_surfaces.append(surface)
          self.animations.append(Animation(activity, [dir], frame_surfaces, frames))

        # now we load from filenames
        if activity in ['decapitated', 'dead_decapitated']:
          #we're doing extra operations to composite the head object
          pass
        else:
          for frame in frames:
            try:
              surface = frames_surfaces[frame]#.copy() #Not sure if copy() is necessary here
            except KeyError:
              try:
                surface = game.sprite_cache[frame].copy()
                surface = game.palette_swap_multi(surface, palette_swaps)
                frames_surfaces[frame] = surface
              except KeyError:
                surface = pygame.image.load(frame).convert()
                surface = game.palette_swap_multi(surface, palette_swaps)
                surface.set_colorkey((255,255,255))
                frames_surfaces[frame] = surface          
            frame_surfaces.append(surface)
          self.animations.append(Animation(activity, [dir], frame_surfaces, frames))

  def end_attack(self, game):
    target_unit = self.target_unit
    if not target_unit:
      self.reset(game)
      #print self.name + " cancelled attack"
      return False
    else:
      dmg = self.damage()
      target_unit.take_damage(game, dmg)
      target_unit.bleed(game, dmg)
      self.play_hit_sound()

  def do_events(self, game):
    if self.current_activity in ["falling", "decapitated"]:
      if self.current_animation.findex < len(self.current_animation.frames)-1:
        self.next_frame(game)
    else:
      self.next_frame(game)
    #Emergency maneuvers
    for obj in game.units + game.trees:
      if obj != self:
        if (obj.x, obj.y) == (self.x, self.y):
          self.sidestep(game)
          #self.move((self.dx, self.dy))

    if self.current_activity == 'walking':
      if self.ticks == 3:
        game.pointers.append(Pointer((self.x,self.y), self))
        self.move((self.dx, self.dy))
      elif self.ticks == 6:
        self.reset(game)
    if self.current_activity == 'lurching':
      if self.ticks < 3:
        unit = self.target_unit
        if not unit:
          self.reset(game)
          return False
        self.point_at(unit)
        if game.distance((self.x,self.y), (unit.x, unit.y)) > 1:
          if game.obstacle((self.x+self.dx, self.y+self.dy)):
            pass
          elif not game.obstacle_unit((self.x+self.dx, self.y+self.dy)):
            game.pointers.append(Pointer((self.x,self.y), self))
            self.move((self.dx, self.dy))
          else:
            pass
      elif self.ticks == 3:
        self.reset(game)
    elif self.current_activity == 'rising':
      if self.ticks == 8:
        self.reset(game)
        self.play_target_sound()
        
    elif self.current_activity == 'attacking':
      if self.ticks == 8:
        self.end_attack(game)
      elif self.ticks == 12:
        self.reset(game)
                  
    elif self.current_activity == 'standing':
      if self.ticks == 4:
        self.reset(game)
        
    elif self.current_activity == 'falling':
      if self.ticks == 8:
        self.reset_ticks()
        self.refresh_activity(game, 'dead')
        game.corpses.append(Corpse(game, self))
        powerup_chance = 0.30
        if random.random() < powerup_chance:
          for powerup in game.powerups:
            if (powerup.x, powerup.y) == (self.x,self.y):
              break
          else:
            game.powerups.append(HealthPowerup(game, (self.x,self.y), 25))
        for unit in game.units:
          if unit.target_unit == self:
            unit.target_unit = None
        game.units.remove(self)
        return True
        
    elif self.current_activity == 'decapitated':
      if self.ticks == 8:
        self.reset_ticks()      
        self.refresh_activity(game, 'dead_decapitated')
        game.corpses.append(Corpse(game, self))
        powerup_chance = 0.30
        if random.random() < powerup_chance:
          for powerup in game.powerups:
            if (powerup.x, powerup.y) == (self.x,self.y):
              break
          else:
            game.powerups.append(HealthPowerup(game, (self.x,self.y), 25))
        for unit in game.units:
          if unit.target_unit == self:
            unit.target_unit = None
        game.units.remove(self)
        return True

    elif self.current_activity == 'stunned':        
      if self.ticks == 16:
        self.reset(game)
    if self.ticks >= 16:
      self.reset(game)
      print "Zombie failsafe"  
    if self.ticks == 0:
      if self.current_activity in ['falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned']:
        #print 'bad zombie!'
        pass
      else:
        self.get_action(game)

  def get_action(self, game):
    #EnemyZombie
    
    #Drop target if it's too far away
    if self.target_unit:
      if game.distance((self.x,self.y), (self.target_unit.x, self.target_unit.y)) > self.smell_radius:
        self.target_unit = None
      
    old_target = self.target_unit
    #target an enemy
    for unit in game.units:
      if unit.hostile != self.hostile:
        if game.LOS((self.x,self.y), (unit.x,unit.y)):
          if old_target:
            if game.distance((self.x,self.y), (unit.x,unit.y)) < game.distance((self.x,self.y), (old_target.x, old_target.y)):
              self.target_unit = unit
          else:
            if game.distance((self.x,self.y), (unit.x,unit.y)) <= self.vision_radius:
              self.target_unit = unit
    if self.target_unit: # i.e. enemy target unit
      if not old_target:
        self.play_target_sound()
      self.move_to_target_unit(game)
    else:
      #Find a unit by smell
      for unit in game.units:
        if unit.hostile != self.hostile:
          if self.target_unit:
            current_target = self.target_unit
            if current_target.hostile == self.hostile:
              if game.distance((self.x,self.y), (unit.x,unit.y)) <= self.smell_radius:
                self.target_unit = unit
                if self in current_target.zombies: #if target is a wizard
                  current_target.zombies.remove(self)
            elif game.distance((self.x,self.y), (unit.x,unit.y)) < game.distance((self.x,self.y), (current_target.x,current_target.y)):
              self.target_unit = unit
          else:
            if game.distance((self.x,self.y), (unit.x,unit.y)) <= self.smell_radius:
              self.target_unit = unit
      if self.target_unit: # i.e. enemy target unit
        self.wander_to_target_unit(game)
      else:
        # wander around at random!
        if random.random() < 0.25:
          dx = random.randint(-1,1)
          dy = random.randint(-1,1)
          if game.obstacle((self.x + dx, self.y + dy)):
            self.sidestep(game)
          else:
            (self.dx, self.dy) = (dx, dy)          
            self.refresh_activity(game, 'walking')
    self.reset_ticks()
    
  def move_to_target_unit(self, game):
    self.target_unit
    if not unit:
      self.target_unit = None
      self.reset(game)
      return False
    self.point_at(unit)
    if game.obstacle((self.x+self.dx, self.y+self.dy)):
      if (unit.x, unit.y) == (self.x+self.dx, self.y+self.dy):
        if unit.hostile != self.hostile:
          self.refresh_activity(game, 'attacking')
      elif game.obstacle_unit((self.x+self.dx, self.y+self.dy)):
        unit_2 = game.obstacle_unit((self.x+self.dx, self.y+self.dy))
        if unit_2.hostile != self.hostile:
          self.target_unit = unit_2
          self.refresh_activity(game, 'attacking')
        else:
          self.sidestep(game)
      else:
        self.sidestep(game)      
    else:
      if random.random() < self.move_frequency_2:
        if random.random() < self.lurch_frequency and game.distance((self.x,self.y),(unit.x,unit.y)) >= 3:
          self.refresh_activity(game, 'lurching')
        else:
          self.refresh_activity(game, 'walking')
    self.reset_ticks()
        
  def wander_to_target_unit(self, game):
    #For units in smell range, aka far away.
    unit = self.target_unit
    if not unit:
      self.reset(game)
      return False
    else:
      self.point_at(unit)
      rand_seed = random.random()
      # Small chance to move in random direction
      if rand_seed < 0.1:
        self.dx = random.randint(-1,1)
        self.dy = random.randint(-1,1)
      if rand_seed < self.move_frequency_1:
        if game.obstacle((self.x + self.dx, self.y + self.dy)):
          self.sidestep(game)
        else:
          self.refresh_activity(game, 'walking')
          self.reset_ticks()
    self.target_unit = None
    if random.random() < 0.05:
      self.play_smell_sound()
  
  def play_hit_sound(self):    
    filenames = ["sounds/zombiebite.ogg", "sounds/zombiebite2.ogg", "sounds/zombiebite3.ogg", "sounds/zombiebite4.ogg"]
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(False)
    if channel:
      channel.play(sound)
      
  def play_smell_sound(self):
    filenames  = []
    for x in range(1, 6):
      filenames.append("sounds/zombiesmellsyou" + str(x) + ".ogg")
    filename = random.choice(filenames)
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(False)
    if channel:
      channel.set_volume(0.5)
      channel.play(sound)
        
  def scream(self):
    filename = "sounds/zombiegroan2.ogg"
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(True)
    channel.play(sound)
      
  def play_target_sound(self):
    filename = "sounds/zombiegroan1.ogg"
    sound = pygame.mixer.Sound(filename)
    channel = pygame.mixer.find_channel(False) #we don't want them overwriting death screams
    if channel:
      sound.set_volume(0.75)
      channel.play(sound)
      
  def play_swish_sound(self):
    pass
    
class Ghost(EnemyZombie):
  def __init__(self, game, name, (x,y)):
    palette_swaps = {(128,128,128):(247,247,255), (186,183,120):(247,247,255), (128,128,64):(247,247,255),
                     (0,128,128):(255,0,0), (128,64,0):(247,247,255), (128,0,0):(192,192,192),
                     (0,0,0):(247,247,255)}
    EnemyZombie.__init__(self, game, name, (x,y), palette_swaps)
    for anim in self.animations:
      for frame in anim.frames:
        frame.set_alpha(128)
    
class Wraith(EnemyZombie):
  def __init__(self, game, name, (x,y)):
    palette_swaps = {(128,128,128):(0,0,0), (186,183,120):(0,0,0), (128,128,64):(0,0,0),
                     (0,128,128):(255,0,0), (128,64,0):(0,0,0), (128,0,0):(96,96,128)}
    EnemyZombie.__init__(self, game, name, (x,y), palette_swaps)
    for anim in self.animations:
      for frame in anim.frames:
        frame.set_alpha(128)
        
class LavaZombie(EnemyZombie):
  def __init__(self, game, name, (x,y)):
    palette_swaps = {(0,0,0):(128,20,0),
                     (128,128,128):(255,0,0), (186,183,120):(255,0,0),
                     (128,128,64):(128,20,0),
                     (128,64,0):(192,40,0),
                     (128,0,0):(255,255,0),
                     (0,128,128):(255,255,0)}
    EnemyZombie.__init__(self, game, name, (x,y), palette_swaps)
    fire_frames = []
    for filename in ["tga/fire_on_person_" + str(x) + ".tga" for x in [1,2,3,4]]:
      surface = pygame.image.load(filename)
      surface.set_colorkey((255,255,255))
      fire_frames.append(surface)
    for anim in self.animations:
      for f in xrange(len(anim.frames)):
        anim.frames[f].blit(fire_frames[f % 4], (0,0))
        
class SuperZombie(EnemyZombie):
  def __init__(self, game, name, (x,y)):
    skin_color = (186, 183, 120)
    palette_swaps = {(186, 183, 120):skin_color, #skin (green-blue)
                     (0,128,128): (255,0,0),        #eyes (red)
                     (128,128,128): skin_color,   #shirt
                     (128,128,64): (128,0,0),
                     (0, 0, 0): (112,90,54)
                    }
                     
    EnemyZombie.__init__(self, game, name, (x,y), palette_swaps)
    self.max_hp = self.current_hp = 110
    self.min_damage = 6
    self.max_damage = 10
    self.move_frequency_1 = 0.3
    self.move_frequency_2 = 0.6
    self.lurch_frequency = 0.4
    
class ZerkerZombie(EnemyZombie):
  #hard-hitting, low health
  def __init__(self, game, name, (x,y)):
    skin_color = (219, 83, 88)
    palette_swaps = {(186, 183, 120):skin_color, #skin (green-blue)
                     (0,128,128): (255,0,0),        #eyes (red)
                     (128,128,128): skin_color,   #shirt
                     (128,128,64): (128,0,0), #alt skin color
                     (0, 0, 0): (170, 58, 48), #pants
                     (128,64,0): skin_color #hair
                    }
                     
    EnemyZombie.__init__(self, game, name, (x,y), palette_swaps)
    self.max_hp = self.current_hp = 50
    self.min_damage = 10
    self.max_damage = 16
    self.move_frequency_1 = 0.3
    self.move_frequency_2 = 0.7
    self.lurch_frequency = 0.7
