import pygame
import random

def generate_tile(r,g,b):
  for color in [r,g,b]:
    if color not in range(256):
      print "Invalid arguments to generate_tile().  Arguments must be \"r g b\", with each value between 0 and 255."
      sys.exit(0)
  tile = pygame.image.load("tga/tilemask.tga")
  pixelarray = pygame.PixelArray(tile)
  for y in range(12):
    for x in range(24):
      (tr,tg,tb, alpha) = tile.unmap_rgb(pixelarray[x][y])
      if (tr,tg,tb) == (255,255,255):
        c = []
        for color in (r,g,b):
          color += random.randint(-16,16)
          color = min(color, 255)
          color = max(color, 0)
          c.append(color)
        pixelarray[x][y] = (c[0],c[1],c[2])
  pixelarray.replace((0,0,0), (255,255,255))
  tile = pixelarray.make_surface()
  tile.set_colorkey((255,255,255))
  return tile
