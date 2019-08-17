import pickle
import glob
import random
import levels
import rpg
import pygame
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
pygame.mixer.init()

game = rpg.RPG()

files = glob.glob("saves/*.*")
filename = random.choice(files)
print "Loading", filename, "..."
f = open(filename, "r")
game2 = pickle.load(f)
for (k,v) in game2.__dict__.iteritems():
  game.__dict__[k] = v
game.load_all_levels(levels)
game.load_level(game.all_levels[game.level_index])
pygame.time.set_timer(pygame.USEREVENT, int(1000/game.fps))
while 1:
  game.loop()
