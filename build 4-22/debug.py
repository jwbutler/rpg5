import pygame
import levels
import rpg
game = rpg.RPG()
pygame.time.set_timer(pygame.USEREVENT, int(1000/game.fps))

def load_from_ini(game):
  debug_ini = fopen('debug.ini', 'r')
  for line in debug_ini.readlines():
    [key,value] = line.split("=")
    value = int(value)
    if key=='fps':
      game.fps = value
    elif key=='hp_regen':
      game.fps = value

game.load_level(levels)
while 1:
  game.loop()
