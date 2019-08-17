from __future__ import division
import pygame
import random
import math

class Animation:
  """
  Information for a single object animation.  Contains activity name,
  direction, and links to four frames.  Directions are 'N', 'NE', etc.
  """
  def __init__(self, activity, directions, frames, filenames):
    self.activity = activity
    self.directions = directions
    self.frames = frames
    self.filenames = filenames
    self.findex = 0

  def next_frame(self):
    """ Iterates the frame index. """
    self.findex += 1
    if self.findex == len(self.frames):
      self.findex = 0

  def get_current_frame(self):
    """ Returns the current frame # of the current animation. """
    return self.frames[self.findex]

  def get_current_filename(self):
    """ Returns the current frame # of the current animation. """
    return self.filenames[self.findex]