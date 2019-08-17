from __future__ import division
import pygame
import random
import math

class Floor:  
  def __init__(self, icons=[], rect=pygame.Rect((0,0,0,0))):
    self.rect = rect
    self.tile_surfaces = icons
    self.xy_tiles = {}
    #self.black_surface = pygame.image.load("tga/black_floor_24x12.tga")
    #self.black_surface.set_colorkey((255,255,255))
    for y in range(self.rect.height):
      for x in range(self.rect.width):
        self.set_tile((x,y), random.choice(self.tile_surfaces))

  """
  def append_rect(self, floor_type, rect):
    icons = []
    i = 1
    while os.path.exists(floor_type + '_' + str(i) + '.tga'):
      surface = pygame.image.load(floor_type + '_' + str(i) + '.tga')
      surface.set_colorkey((255,255,255))
      icons.append(surface)
      i += 1
    for y in range(rect.top, rect.top+rect.height):
      for x in range(rect.left, rect.left+rect.width):
        self.tiles[(x,y)] = random.choice(icons)
  """
        
  def set_tile(self, (x,y), tile_surface):
    for t in self.tile_surfaces:
      if tile_surface == t:
        self.xy_tiles[(x,y)] = self.tile_surfaces.index(t)
        return
    else:
      self.tile_surfaces.append(tile_surface)
      self.xy_tiles[(x,y)] = self.tile_surfaces.index(tile_surface)
  
  def get_tile(self, (x,y)):
    tile_index = self.xy_tiles[(x,y)]
    return self.tile_surfaces[tile_index]

  def draw(self):
    rect = self.game.camera.get_rect()
    screen_rect = pygame.rect.Rect((0,0,self.game.screen.get_width(), self.game.screen.get_height()))
    self.game.floor_layer.fill((0,0,0))
    tile_rect = pygame.rect.Rect((0,0,24,12))
    for (x,y) in self.xy_tiles.keys():
      if rect.collidepoint((x,y)):
        for unit in self.game.units:
          if unit.playable:
            if self.game.distance((unit.x,unit.y), (x,y)) <= self.game.VISION_RADIUS:
              (xx,yy) = self.game.grid_to_pixel((x, y))
              #tile_rect = pygame.rect.Rect((xx,yy,24,12))
              tile_rect.move(xx,yy)
              if screen_rect.colliderect(tile_rect):
                self.game.floor_layer.blit(self.get_tile((x,y)), (xx, yy))
                break