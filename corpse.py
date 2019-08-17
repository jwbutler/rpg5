class Corpse:
  # Should probably be inheriting from PlayerMale
  def __init__(self, game, unit):
    self.game = game
    for key in unit.__dict__.keys():
      self.__dict__[key] = unit.__dict__[key]
    self.get_current_frame = unit.get_current_frame
    self.refresh_activity = unit.refresh_activity
    self.refresh_activity(game, unit.current_activity)
    if self.hostile: #this is probably the wrong place to be doing this, but...
      game.score += 50
      game.kills += 1
      if game.battle_mode:
        game.streak += 1
        game.streak_ticks = 25
        game.award_streak_bonus()
  
  def do_events(self):
    pass
  
  """
  def draw_OLD(self):
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    x -= 8
    y -= 30 
    source = self.get_current_frame()
    self.game.screen.blit(source, (x, y))
    #game.draw_black(self, source, (x,y))
  """

  def draw(self):
    (x,y) = self.game.grid_to_pixel((self.x, self.y))
    x -= 8; y -= 30
    self.sort_equipment()
    for equip in self.equipment:
      f = equip.current_animation.get_current_filename()
      if f[len(f)-6:] == '_B.tga':
        equip.draw(x, y)
    source = self.get_current_frame()
    self.game.screen.blit(source, (x, y))
    for equip in self.equipment:
      f = equip.current_animation.get_current_filename()
      if f[len(f)-6:] != '_B.tga':
        equip.draw(x, y)
        
  def get_z(self):
    return 6*self.x + 6*self.y + 2
    
  def get_rect(self):
    (left,top) = self.game.grid_to_pixel((self.x, self.y))
    top -= 28
    (width, height) = (self.get_current_frame().get_width(), self.get_current_frame().get_height())
    return pygame.Rect((left,top,width, height))
    
  def sort_equipment(self):
    sorted_equipment = []
    if self.current_activity == 'standing' and self.current_animation.directions[0] in ["E", "SE", "S"]:
      for slot in ["shield", "weapon", "head", "hair", "chest", "cloak"]:
        for equip in self.equipment:
          if equip.slot == slot:
            sorted_equipment.append(equip)
            break
    elif self.current_activity == 'standing' and self.current_animation.directions[0] in ["NE"]:
      for slot in ["weapon", "shield", "head", "hair", "chest", "cloak"]:
        for equip in self.equipment:
          if equip.slot == slot:
            sorted_equipment.append(equip)
            break
    elif self.current_activity == 'walking' and self.current_animation.directions[0] in ["E"]:
      for slot in ["weapon", "shield", "head", "hair", "chest", "cloak"]:
        for equip in self.equipment:
          if equip.slot == slot:
            sorted_equipment.append(equip)
            break              
    else:
      for slot in ["shield", "weapon", "head", "hair", "cloak", "chest"]:
        for equip in self.equipment:
          if equip.slot == slot:
            sorted_equipment.append(equip)
            break
    sorted_equipment.reverse()
    self.equipment = sorted_equipment