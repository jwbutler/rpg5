from __future__ import division
import pygame

pygame.init()
big_screen = pygame.display.set_mode((640,480))
screen = pygame.surface.Surface((320,240))
f = open("scrolling_text.txt")
line_surfaces = []

for line in f:
  font = pygame.font.SysFont("Arial", 10)
  surface = font.render(line.rstrip(), True, (255,255,255))
  line_surfaces.append(surface)
y = 240

pygame.time.set_timer(pygame.USEREVENT, 200)
while 1:
  for event in pygame.event.get():
    if event.type == pygame.USEREVENT:
      screen.fill((0,0,0))
      y2 = y
      for surface in line_surfaces:
        y2 += surface.get_height()
        x = (320-surface.get_width())/2
        screen.blit(surface,(x,y2))
        
      pygame.transform.scale(screen, (640,480), big_screen)
      pygame.display.flip()
      y -= 3
