from __future__ import division
import pygame
import random
import math

class UnitCard:
  def __init__(self, game, unit):
    self.game = game
    self.unit = unit
    self.surface = pygame.Surface((88,80))
    if unit.current_activity in ['dead', 'dead_decapitated']:
      self.surface.fill((255,128,128))
    elif unit.selected:
      self.surface.fill((128,255,128))
    else:
      self.surface.fill((128,128,128))
    hp_bar = unit.draw_hp_bar(80,16)
    self.surface.blit(hp_bar, (4, 4))
    if unit.has_special:
      cooldown_bar = unit.draw_cooldown_bar(80,8)
      self.surface.blit(cooldown_bar, (4, 22))
    font = pygame.font.SysFont('Arial', 12, True)
    color = (128,0,255)
    if len(unit.name.split()) > 1:
      (first_name, last_name) = unit.name.split()
      self.surface.blit(font.render(first_name, False, color), (4, 32))
      self.surface.blit(font.render(last_name, False, color), (4, 46))
      self.surface.blit(font.render("Level " + str(unit.level), False, (255,255,255)), (4, 62))
    else:
      self.surface.blit(font.render(unit.name, False, color), (4, 33))
      self.surface.blit(font.render("Level " + str(unit.level), False, (255,255,255)), (4,48))
      
  def update(self, unit):
    print 'UCU'
    #check whether this actually requires the game to be passed
    if unit.current_activity in ['dead', 'dead_decapitated']:
      self.surface.fill((255,128,128))
    elif unit.selected:
      self.surface.fill((128,255,128))
    else:
      self.surface.fill((128,128,128))
    hp_bar = unit.draw_hp_bar(80,16)
    self.surface.blit(hp_bar, (4, 4))
    if unit.has_special:
      cooldown_bar = unit.draw_cooldown_bar(80,8)
      self.surface.blit(cooldown_bar, (4, 22))
    font = pygame.font.SysFont('Arial', 12, True)
    color = (128,0,255)
    
    # If unit's name has first & last name, render them on separate lines
    if len(unit.name.split()) > 1:
      (first_name, last_name) = unit.name.split()
      self.surface.blit(font.render(first_name, False, color), (4, 32))
      self.surface.blit(font.render(last_name, False, color), (4, 46))
      self.surface.blit(font.render("Level " + str(unit.level), False, (255,255,255)), (4, 62))
    else:
      self.surface.blit(font.render(unit.name, False, color), (4, 33))
      self.surface.blit(font.render("Level " + str(unit.level), False, (255,255,255)), (4,48))