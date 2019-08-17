from __future__ import division
import pygame
import random
import math

class Menu:
  #i'm guessing we haven't used this one in a while
  def __init__(self, game, image, rect, player, visible = False):
    self.game = game
    self.image = image
    self.rect = rect
    self.surface = pygame.image.load(self.image)
    self.background = pygame.image.load(self.image)
    self.buttons = []
    self.icons = []
    self.visible = visible

  def show(self):
    self.visible = True

  def hide(self):
    self.visible = False

  def toggle(self):
    self.visible = not self.visible

  def refresh(self, player):
    self.surface.blit(self.background, (0,0))
    for icon in self.icons:
      self.surface.blit(icon.surface, (icon.x, icon.y))