import pygame
import levels
import rpg
game = rpg.RPG()
pygame.time.set_timer(pygame.USEREVENT, int(1000/game.fps))

game.load_level(levels)
while 1:
  game.loop()

