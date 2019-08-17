import pygame
import sys, os, glob

class SpriteMaker:

  def __init__(self):
    pygame.init()
    self.screen = pygame.display.set_mode((1024,768))
    self.make_sprites()
    
  def make_sprites(self):
    sprite_names = ["player", "zombie", "female"]
    activities = ["standing", "walking", "attacking"]
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    for sprite_name in sprite_names:
      for activity in activities:
        frame_filenames = glob.glob("tga//" + sprite_name + "_" + activity + "_*.tga")        
        first_frame = pygame.image.load(frame_filenames[0])
        frame_height = first_frame.get_height()
        frame_width = first_frame.get_width()
        sprite = pygame.Surface((first_frame.get_width() * len(frame_filenames), first_frame.get_height() * len(frame_filenames)))
        y = 0
        for filename in frame_filenames:
          frame = pygame.image.load(filename)
          sprite.blit(frame, (0,y))
          y += frame_height
        sprite_filename = sprite_name + "_" + activity + ".tga"
        pygame.image.save(sprite, sprite_filename)

  def test_sprites(self):
    t1 = pygame.time.get_ticks()
    sprite_names = ["player", "zombie", "female"]
    activities = ["standing", "walking", "attacking"]
    blits = 0
    for sprite_name in sprite_names:
      for activity in activities:
        sprite_filename = sprite_name + "_" + activity + ".tga"
        sprite_surface = pygame.image.load(sprite_filename)
        y = 0
        rect = pygame.rect.Rect((0,y,40,40))
        while y < sprite_surface.get_height():
          rect.top = y
          self.screen.blit(sprite_surface, (0,0), rect)
          y += 40
          blits += 1
    t2 = pygame.time.get_ticks()
    print "Sprite load/display time:", t2-t1
    print "Blits:", blits

  def test_single_frames(self):
    t1 = pygame.time.get_ticks()
    sprite_names = ["player", "zombie", "female"]
    activities = ["standing", "walking", "attacking"]
    blits = 0
    for sprite_name in sprite_names:
      for activity in activities:
        frame_filenames = glob.glob("tga//" + sprite_name + "_" + activity + "_*.tga")
        for frame_filename in frame_filenames:
          frame_surface = pygame.image.load(frame_filename)
          self.screen.blit(frame_surface, (0,0))
          blits += 1
    t2 = pygame.time.get_ticks()
    print "Single frame load/display time:", t2-t1
    print "Blits:", blits
    
sm = SpriteMaker()
sm.test_sprites()
sm.test_single_frames()
