from __future__ import division
import pygame
import random
import math

class MainMenu(Menu):
  def __init__(self, game, image, rect, visible = False):
    self.game = game
    self.image = image
    self.rect = rect
    self.background = pygame.image.load(self.image)
    self.background.set_colorkey((255,0,0))
    self.surface = self.background.copy()
    self.surface.set_colorkey((255,0,0))      
    self.icons = []
    self.buttons = []
    self.cards = []    
    self.visible = visible

  def refresh(self):
    self.surface.blit(self.background, (0,0))
    self.cards = []
    for unit in self.game.units:
      if unit.playable:
        self.cards.append(UnitCard(self.game, unit))
    
    font = pygame.font.SysFont("Arial", 16, True)
    
    # Draw unit numbers
    for (n, card) in enumerate(self.cards):
      self.surface.blit(card.surface, (92*n + 4, 37))
      text = font.render(str(n+1), False, (0,0,0))
      x = 92*n + 38 + (21 - text.get_width())/2
      y = (22 - text.get_height())/2 + 14
      self.surface.blit(text, (x,y))
    
  def card_rect(self, card):
    return pygame.Rect(92*self.cards.index(card)+4, 410, 88, 80)