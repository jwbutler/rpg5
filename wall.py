from __future__ import division
import pygame
import random
import math

class Wall:
  def __init__(self, game, x, y, icon, height_offset = 0):
    self.game = game
    self.x = x
    self.y = y
    self.icon = pygame.image.load(icon)
    self.icon.set_colorkey((255,255,255))
    self.icon.convert()
    self.current_activity = None
    self.height_offset = height_offset

  def draw(self):
    self.icon.set_alpha(255)
    for unit in self.game.units + self.game.corpses:
      #if unit.playable:
      dx = (unit.x - self.x); dy = (unit.y - self.y)
      screen_dy = 12*(dx+dy)
      screen_dx = 12*(dx-dy)
      min_screen_dy = (-84)+((-27)*self.height_offset)
      if screen_dy <= 0 and screen_dy >= min_screen_dy:
        if screen_dx > -24 and screen_dx < 24:
          self.icon.set_alpha(128)
          break
    for unit in self.game.units + self.game.corpses:
      if unit.playable:
        if self.game.distance((unit.x,unit.y),(self.x,self.y)) <= self.game.VISION_RADIUS:
          self.game.screen.blit(self.icon, self.get_rect())
          self.icon.set_alpha(255)
          return
    
  def get_z(self):
    return 6*self.x + 6*self.y + 6
    
  def unit_to_alpha(self, unit):
    collide_rect = self.get_rect().clip(unit.get_rect())
    collide_area = collide_rect.width * collide_rect.height
    x = max(255-(collide_area), 0)
    return x
  
  def coords_to_alpha(self, x, y):
    (self_x, self_y) = (self.x, self.y)
    dx = abs(self.x - x - 2*self.height_offset)
    dy = abs(self.y - y - 2*self.height_offset)
    alpha = int(48*(dx+dy)) + 16
    alpha = min(255, alpha)
    alpha = max(0, alpha)
    return alpha
    
  def get_rect(self):
    (left,top) = self.game.grid_to_pixel((self.x, self.y))
    top += -27*self.height_offset - 27
    (width, height) = (self.icon.get_width(), self.icon.get_height())
    return pygame.Rect((left,top,width,height))