import pygame
import math
import random

class Member:
  def __init__(self, hp, damage, radius, x, y):
    self.current_hp = self.max_hp = hp
    self.damage = damage
    self.radius = radius
    self.x = x
    self.y = y

  def draw(self, game, unit):
    if unit.selected:
      color = (255,255,0)
    else:
      color = unit.color
    game.screen.fill(color, self.get_rect(unit))
  
  def get_rect(self, unit):
    return pygame.Rect(int(unit.x + 8*self.x), int(unit.y + 8*self.y), 6, 6)

  def get_center(self, unit):
    return (unit.x + self.x + self.get_rect(unit).width/2, unit.y + self.y + self.get_rect(unit).height/2)

    
class Unit:
  def __init__(self, team, name, color, count, width, height, x, y, hp, damage, radius):
    self.team = team
    self.name = name
    self.color = color
    self.members = []
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    (self.target_x, self.target_y) = (x + width*4,y + height*4)
    self.dx = self.dy = 0
    self.selected = False
    self.speed = 5
    for x in range(width):
      for y in range(height):
        self.members.append(Member(hp, damage, radius, x, y))

  def draw(self, game):
    for member in self.members:
      member.draw(game, self)

  def get_rect(self):
    return pygame.Rect(self.x, self.y, self.width*8-2, self.height*8-2)
  
  def get_center(self):
    return (self.x + self.get_rect().width/2, self.y + self.get_rect().height/2)
  
  def collide(self, unit):
    return self.get_rect().colliderect(unit.get_rect())

class Game:
  pass

pygame.init()
game = Game()
game.screen = pygame.display.set_mode((640,480))
game.units = []
game.drag_rect = None
game.drag_rect_locked = False
pygame.time.set_timer(pygame.USEREVENT, 50) # redraw
pygame.time.set_timer(pygame.USEREVENT+1, 100) # move
pygame.time.set_timer(pygame.USEREVENT+2, 500) # attack
game.units.append(Unit(0, "Red Dot", (255,0,0), 20, 5, 4, 200, 200, 10, 10, 100))
game.units.append(Unit(1, "Blue Dot", (0,0,255), 20, 5, 4, 300, 200, 10, 10, 100))
game.running = True
(game.drag_x1, game.drag_y1, game.drag_x2, game.drag_y2) = (None, None, None, None)

# # # # # # # # # #
# MAIN EVENT LOOP #
# # # # # # # # # #
while game.running:
  for event in pygame.event.get():
    if event.type == pygame.MOUSEBUTTONDOWN:
      # # # # # # # # # # # # # # # # # # # # # #
      # LEFT MOUSEDOWN HANDLER (selection rect) #
      # # # # # # # # # # # # # # # # # # # # # #
      if event.button == 1:
        (game.drag_x1, game.drag_y1) = pygame.mouse.get_pos()
      # # # # # # # # # # # # # # # # # # #
      # RIGHT MOUSEDOWN HANDLER (attack)  #
      # # # # # # # # # # # # # # # # # # #
      elif event.button == 3:
        for unit in game.units:
          if unit.selected:
            (unit.target_x, unit.target_y) = pygame.mouse.get_pos()
            dx = unit.target_x - unit.get_center()[0]
            dy = unit.target_y - unit.get_center()[1]
            theta = math.atan2(dy,dx)
            (unit.dx, unit.dy) = (unit.speed*math.cos(theta), unit.speed*math.sin(theta))
    # # # # # # # # # # # # # # # # # # # # #
    # MOUSE MOTION HANDLER (selection rect) #
    # # # # # # # # # # # # # # # # # # # # #
    if event.type == pygame.MOUSEMOTION:
      if (pygame.mouse.get_pressed()[0] and game.drag_rect_locked == False):
        if game.drag_x1 == None: game.drag_x1 = pygame.mouse.get_pos()[0]
        if game.drag_y1 == None: game.drag_y1 = pygame.mouse.get_pos()[1]
        (game.drag_x2, game.drag_y2) = pygame.mouse.get_pos()
        left = min(game.drag_x1, game.drag_x2)
        top = min(game.drag_y1, game.drag_y2)
        width = abs(game.drag_x2 - game.drag_x1)
        height = abs(game.drag_y2 - game.drag_y1)
        game.drag_rect = pygame.Rect(left,top,width,height)
    # # # # # # # # # # # # # # 
    # MOUSE BUTTON UP HANDLER #
    # # # # # # # # # # # # # #
    if event.type == pygame.MOUSEBUTTONUP:
      if event.button == 1:
        (game.drag_x2, game.drag_y2) = pygame.mouse.get_pos()
        left = min(game.drag_x1, game.drag_x2)
        top = min(game.drag_y1, game.drag_y2)
        width = abs(game.drag_x2 - game.drag_x1)
        height = abs(game.drag_y2 - game.drag_y1)
        game.drag_rect = pygame.Rect(left,top,width,height)
        for unit in game.units:
          if unit.team == 0:
            unit.selected = game.drag_rect.colliderect(unit.get_rect())
        game.drag_rect_locked = True
    # # # # # # # # # # # # # # # # # #
    # 100ms TIMER HANDLER (movement)  #
    # # # # # # # # # # # # # # # # # #
    if event.type == pygame.USEREVENT + 1:
      for unit in game.units:
        other_units = [] + game.units # otherwise, obj id is the same
        other_units.remove(unit) #can this be combined with prev line?
        safe_move = True
        new_rect = pygame.Rect(unit.x + unit.dx, unit.y + unit.dy, unit.get_rect().width, unit.get_rect().height)
        for u in other_units:
          if new_rect.colliderect(u.get_rect()):
            safe_move = False
        if safe_move == True:
          unit.x += unit.dx
          unit.y += unit.dy
        if unit.target_x and unit.target_y:
          if math.hypot(unit.target_x - unit.get_center()[0], unit.target_y - unit.get_center()[1]) < unit.speed:
            unit.x = unit.target_x - unit.get_rect().width/2
            unit.y = unit.target_y - unit.get_rect().height/2
            unit.dx = unit.dy = 0
            pass
    # # # # # # # # # # # # # # # # #
    # 500ms TIMER HANDLER (combat)  #
    # # # # # # # # # # # # # # # # #
      for unit_1 in game.units:
        for member_1 in unit_1.members:
          collide_members = []
          for unit_2 in game.units:
            for member_2 in unit_2.members:
              x_1 = member_1.get_center(unit_1)[0]
              y_1 = member_1.get_center(unit_1)[1]
              x_2 = member_2.get_center(unit_2)[0]
              y_2 = member_2.get_center(unit_2)[1]
              distance = math.hypot(y_2 - y_1, x_2 - x_1)
              if distance <= member_1.radius:
                collide_members.append(member_2)
          target = random.choice(collide_members)
          target.current_hp -= member_1.damage
          if target.current_hp <= 0:
            #unit_2.members.remove(target)
            del(target)
      # # # # # # # # # # # # # # # #
    # 50ms TIMER HANDLER (redraw) #
    # # # # # # # # # # # # # # # #
    if event.type == pygame.USEREVENT:
      game.screen.fill((0,0,0))
      for unit in game.units:
        unit.draw(game)
      if game.drag_rect:
        pygame.draw.rect(game.screen, (0,255,0), game.drag_rect, 2)
        if game.drag_rect_locked == True:
          game.drag_rect = False
          game.drag_rect_locked = False
          (game.drag_x1, game.drag_y1, game.drag_x2, game.drag_y2) = (None, None, None, None)
      pygame.display.flip()
      if event.type == pygame.QUIT:
        running = False
