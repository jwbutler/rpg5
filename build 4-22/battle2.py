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
game = RPG('battle2', 600) #120 seconds, 2 minutes
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
# now we're overwriting them with the correct levels. not ideal, but
# whatever

game.all_levels = []

""" Parameter hash: keys are round_levelno,
    values are [map_filename, max_zombies, max_superzombies, max_bandits, max_wizards, max_total]
    I'll add more enemy types to this array as we go """
parameters = {  
  "1_1": ['battlemap_4', 5,0,0,0,5], #forest
  "1_2": ['battlemap_4', 4,2,0,0,5],
  "1_3": ['battlemap_4', 6,0,0,1,6],
  "1_4": ['battlemap_4', 5,2,0,1,7],
  "1_5": ['battlemap_4', 0,0,5,0,5],
  "2_1": ['cavemap2', 6,0,0,0,6], #cave
  "2_2": ['cavemap2', 5,2,0,0,6],
  "2_3": ['cavemap2', 7,0,0,1,7],
  "2_4": ['cavemap2', 6,2,0,1,8],
  "2_5": ['cavemap2', 0,0,5,0,5]  
}
for key in sorted(parameters.keys()):
  [filename, max_zombies, max_superzombies, max_bandits, max_wizards, max_total] = parameters[key]
  level = levels.BattleLevelFromFile(game, "tga/levels/"+filename+".tga",
    max_zombies, max_superzombies, max_bandits, max_wizards, max_total, key)
  game.all_levels.append(level)
pygame.time.set_timer(pygame.USEREVENT, int(1000/game.fps))
game.load_level(levels)
while 1:
  game.loop()
