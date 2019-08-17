import pygame
import string

pygame.init()
screen = pygame.display.set_mode((320,240))

f = open("images/level1ai.txt", "r") #Lorem Ipsum!
str = f.read().rstrip()

def draw_line_surfaces(str):
  words = str.split()
  line_surfaces = []
  font = pygame.font.SysFont("Arial", 10)
  lines = []
  line_index = 0
  lines.append("")
  for word in words:
    new_line = string.join([lines[line_index], word])
    surface = font.render(new_line, False, (255,255,255))
    if surface.get_width() > 320:
      line_index += 1
      lines.append("")
      continue
    else:
      lines[line_index] = new_line
  for line in lines:
    line_surface = font.render(line, False, (255,255,255))
    line_surfaces.append(line_surface)
  return line_surfaces
