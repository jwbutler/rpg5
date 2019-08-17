from __future__ import division
import random
import os
import pygame
#import levels
#from pygame import * # To be removed
import sys

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()
pygame.mixer.init()

#Skipping this shit for now!
import story

mode_index = 0
mode = 'story'
show_modes = False

fullscreen = True
for arg in sys.argv:
  if arg in ['-w', '-windowed', '-window', '--w', '--windowed', '--window']:
    fullscreen = False
if fullscreen:
  screenbig = pygame.display.set_mode((640,480), pygame.FULLSCREEN)
else:
  screenbig = pygame.display.set_mode((640,480))
screen = pygame.surface.Surface((320,240))
screen.fill((0,0,0))
background_1 = pygame.image.load('tga/titlescreenFIXED_1.tga')
background_2 = pygame.image.load('tga/titlescreenFIXED_2.tga')
background_3 = pygame.image.load('tga/titlescreenFIXED_3.tga')
clouds_1 = pygame.image.load('tga/titlescreen_Clouds1.tga')
clouds_2 = pygame.image.load('tga/titlescreen_Clouds2.tga')
clouds_3 = pygame.image.load('tga/titlescreen_Clouds3.tga')
for c in [clouds_1, clouds_2, clouds_3]:
  c.set_colorkey((255,255,255))

cx1 = 0
cx2 = 0
cx3 = 0

pygame.time.set_timer(pygame.USEREVENT, 200)
show_title = True
title = pygame.image.load('tga/titlewords.tga')
title.set_colorkey((0,0,0))
ticks = 0
title_y = 240
modes = ['story', 'battle', 'battle2', 'debug']

pygame.mixer.music.load('sounds/DorianPirateSong.ogg')
pygame.mixer.music.play(-1)
font = pygame.font.SysFont('Arial', 18, True)
text_surface = font.render("Press ENTER to begin", False, (255,255,255))
while show_title:
  for event in pygame.event.get():
    if event.type == pygame.USEREVENT:
      t = ticks % 3
      if t == 0:
        screen.blit(background_1,(0,0))
      elif t == 1:
        screen.blit(background_2,(0,0))
      elif t == 2:
        screen.blit(background_3,(0,0))
      try:
        screen.blit(clouds_1, (cx1, 0))
        screen.blit(clouds_2, (cx2, 0))
        screen.blit(clouds_3, (cx3, 0))
        screen.blit(clouds_1, (cx1-320, 0))
        screen.blit(clouds_2, (cx2-320, 0))
        screen.blit(clouds_3, (cx3-320, 0))                
        screen.blit(title, (0, title_y))
      except:
        print 'title gfx error'
      if ticks >= 40:
        if int(ticks/2) % 3 != 0:
          if not show_modes:
            left = 160 - text_surface.get_width()/2
            screen.blit(text_surface, (left, 180))
      if show_modes:
        font = pygame.font.SysFont('Arial', 16, True)

        if mode == 'story':
          color = (255,255,255)
        else:
          color = (192,192,192)
        story_surface = font.render("STORY", False, color)
        left = 160 - story_surface.get_width()/2
        screen.blit(story_surface, (left, 160))
        
        if mode == 'battle':
          color = (255,255,255)
        else:
          color = (192,192,192)
        battle_surface = font.render("BATTLE", False, color)
        left = 160 - battle_surface.get_width()/2
        screen.blit(battle_surface, (left, 180))

        if mode == 'battle2':
          color = (255,255,255)
        else:
          color = (192,192,192)
        battle_surface = font.render("BATTLE2", False, color)
        left = 160 - battle_surface.get_width()/2
        screen.blit(battle_surface, (left, 200))
        
        if mode == 'debug':
          color = (255,255,255)
        else:
          color = (192,192,192)
        battle_surface = font.render("DEBUG", False, color)
        left = 160 - battle_surface.get_width()/2
        screen.blit(battle_surface, (left, 220))
      
      ticks += 1
      if title_y > 30:
        title_y -= 6
      cx1 += 2
      cx2 += 3
      cx3 += 4
      
      if cx1 >= clouds_1.get_width():
        cx1 = 0
      if cx2 >= clouds_2.get_width():
        cx2 = 0
      if cx3 >= clouds_3.get_width():
        cx3 = 0
      pygame.transform.scale(screen, (640,480), screenbig)
      pygame.display.flip()
    elif event.type == pygame.KEYDOWN:
      if not show_modes:
        show_modes = True
        continue
      if pygame.key.name(event.key) == 'return':
        show_title = False
        pygame.time.set_timer(pygame.USEREVENT, 0)
        pygame.mixer.music.stop()
        if mode == 'story':
          import story
        elif mode == 'battle':
          import battle
        elif mode == 'battle2':
          import battle2
        elif mode == 'debug':
          import debug
        break
      elif pygame.key.name(event.key) == 'escape':
        quit()
      elif pygame.key.name(event.key) == 'down':
        mode_index = (mode_index+1) % len(modes)
        mode = modes[mode_index]
      elif pygame.key.name(event.key) == 'up':
        mode_index = (mode_index-1) % len(modes)
        mode = modes[mode_index]
