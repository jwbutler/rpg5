# Contains units that are not used in the current game.

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
                      equipment.make(self.game, 'blue_chain_mail'),
                      equipment.make(self.game, 'fire_sword'),
                      equipment.make(self.game, 'cloak_of_suck')
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
    self.floor_fire = None
    
  def do_events(self):
    if self.floor_fire:
      (self.floor_fire.x, self.floor_fire.y) = (self.x,self.y)
      self.floor_fire.next_frame()
    else:
      fire_filenames = ["tga/floor_fire_" + str(x) + ".tga" for x in [1,2,3,4]]
      fire_frames = [pygame.image.load(f) for f in fire_filenames]
      for f in fire_frames:
        f.set_colorkey((255,255,255))
      self.floor_fire = FireTile(fire_frames, (self.x,self.y), 10)
    PlayerMale.do_events(self)
    
  def draw(self):
    self.floor_fire.draw()
    PlayerMale.draw(self)
    
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
                      equipment.make(self.game, 'red_triangle_hat'),
                      equipment.Hairpiece(self.game, 'Hair of Suck', 'hairpiece',{(0,0,0):hair_color}),
                      equipment.make(self.game, 'red_tunic'),
                      equipment.make(self.game, 'gold_klub')
                     ]
    self.activities = ['standing', 'walking', 'attacking', 'falling', 'dead', 'decapitated', 'dead_decapitated', 'stunned']
    self.current_activity = 'standing'
    self.animations = []
    self.max_hp = 100
    self.current_hp = self.max_hp
    self.load_animations(self.palette_swaps)
    self.reset()

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
    
  def load_animations(self, game, palette_swaps):
    PlayerMale.load_animations(self, game, palette_swaps)

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
    
  def get_action(self, game):
    PlayerMale.get_action(self, game)
    
  def move_to_target_unit(self, game):
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
        equip.draw(, x, y)
        
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