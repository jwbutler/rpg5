from __future__ import division
import random
import os
import pygame
#from pygame import * # To be removed

import levels
from rpg import RPG
from units import *

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
pygame.mixer.init()
game = RPG(True, 600) #120 seconds, 2 minutes
# first, the battle menu / character selection screen

pygame.time.set_timer(pygame.USEREVENT, 100)
battle_menu_background = pygame.image.load("tga/battle_menu.tga")
first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
name1 = first_name+" "+last_name
first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
name2 = first_name+" "+last_name
first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
name3 = first_name+" "+last_name
first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)
last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
name4 = first_name+" "+last_name
first_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.female_name_suffixes)
last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
name5 = first_name+" "+last_name
first_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.female_name_suffixes)
last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
name6 = first_name+" "+last_name
units = [
  PlayerMale(game, name1, (0,0)),
  AltPlayerMale(game, name2, (0,0)),
  PlayerArcher(game, name3, (0,0)),
  PlayerHealer(game, name4, (0,0)),
  PlayerFemale(game, name5, (0,0)),
  PlayerFemaleMelee(game, name6, (0,0)),
]
for unit in units:
  for n in range(2):
    unit.level_up()
chosen_units = []
show_unit_select_screen = True
while (show_unit_select_screen):
  for event in pygame.event.get():
    if event.type == pygame.MOUSEBUTTONDOWN:
      posn = (int(event.pos[0]/2), int(event.pos[1]/2))
      (x,y) = (5,147)
      for u in range(len(units)):
        unit = units[u]
        rect = pygame.Rect((x,y, 24, 33))
        if rect.collidepoint(posn):
          for u in units:
            u.selected_in_menu = False
          unit.selected_in_menu = True
          break
        
        add_button_rect = pygame.Rect((x-1,y+36,26,9))
        if add_button_rect.collidepoint(posn):
          if len(chosen_units) < 5:
            chosen_units.append(unit)
            if unit.__class__ in [PlayerFemale, PlayerFemaleMelee]:
              first_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.female_name_suffixes)
            else:
              first_name = language.generate_word(language.consonants, language.vowels, language.vowel_patterns)            
            last_name = language.generate_name_with_suffix(language.consonants, language.vowels, language.last_name_suffixes)
            name = first_name+" "+last_name
            # generate a new unit of the same class
            new_unit = unit.__class__(game, name, (0,0))
            for n in range(2):
              new_unit.level_up()            
            units[u] = new_unit
            break
        x += 27
      
      (x,y) = (5,194)
      for unit in chosen_units:
        rect = pygame.Rect((x,y, 24, 33))
        if rect.collidepoint(posn):
          for u in units:
            u.selected_in_menu = False
          unit.selected_in_menu = True
          break
        
        remove_button_rect = pygame.Rect((x-1,y+36,26,9))
        if remove_button_rect.collidepoint(posn):
          if unit in chosen_units:
            chosen_units.remove(unit)
            break
        x += 27        
      #the Finish button    
      (x,y) = (140,225)
      rect = pygame.Rect((x,y,36,13))
      if rect.collidepoint(posn):
        game.units = chosen_units
        del units
        show_unit_select_screen = False
      
    if event.type == pygame.USEREVENT:
      game.screen.blit(battle_menu_background, (0,0))
      (x,y) = (5,147)
      for unit in units:
        if unit.selected_in_menu:
          rect = pygame.Rect((x-1,y-1,26,35))
          pygame.draw.rect(game.screen, (255,255,255), rect, 1)
        unit.draw_in_place(game, (x,y))
        x += 27
      (x,y) = (5,194)
      for unit in chosen_units:
        if unit.selected_in_menu:      
          rect = pygame.Rect((x-1,y-1,26,35))
          pygame.draw.rect(game.screen, (255,255,255), rect, 1)
        unit.draw_in_place(game, (x,y))
        x += 27
      pygame.transform.scale(game.screen, (640,480), game.screenbig)
      pygame.display.flip()
      
# the game has already loaded the standard set of levels.
#  now we're overwriting them with the correct levels. not ideal, but
# whatever

game.all_levels = []

filename = random.choice(["battlemap_1",
  #"battlemap_2", #Not including this one because the AI isn't good enough for it
  "battlemap_3", "battlemap_4"])
if filename == 'battlemap_1':
  max_zombies = 2
  max_superzombies = 2
  max_bandits = 0
  max_wizards = 1
  max_total = 6
  """
  elif filename == 'battlemap_2':
    max_zombies = 5
    max_superzombies = 2
    max_bandits = 0
    max_wizards = 1
    max_total = 7
  """
elif filename == 'battlemap_3':
  max_zombies = 2
  max_superzombies = 2
  max_bandits = 0
  max_wizards = 1
  max_total = 6
elif filename == 'battlemap_4':
  max_zombies = 2
  max_superzombies = 2
  max_bandits = 0
  max_wizards = 1
  max_total = 6
level = levels.BattleLevelFromFile(game, "tga/levels/"+filename+".tga",
  max_zombies, max_superzombies, max_bandits, max_wizards, max_total)
game.all_levels.append(level)
pygame.time.set_timer(pygame.USEREVENT, int(1000/game.fps))
game.load_level(levels)
while 1:
  game.loop()
