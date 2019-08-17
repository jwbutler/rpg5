import pygame
from pygame import *
import math

def key_to_dir(key):
    keyName = pygame.key.name(key)
    if keyName == '[1]': return 'S'
    if keyName == '[2]': return 'SE'
    if keyName == '[3]': return 'E'
    if keyName == '[4]': return 'SW'
    if keyName == '[6]': return 'NE'
    if keyName == '[7]': return 'W'
    if keyName == '[8]': return 'NW'
    if keyName == '[9]': return 'N'

def dir_to_coords(direction):
    if direction[0] == 'N':
        y = -1
    elif direction[0] == 'S':
        y = 1
    else:
        y = 0
    if direction[len(direction)-1] == 'W':
        x = -1
    elif direction[len(direction)-1] == 'E':
        x = 1
    else:
        x = 0
    return (x, y)

def get_angle(a, b):
    if a == b: return 0
    if a == 'N':
        if b in ['NW', 'NE']: return 45
        if b in ['W', 'E']: return 90
        if b in ['SW', 'SE']: return 135
        else: return 180
    if a == 'NE':
        if b in ['N', 'E']: return 45
        if b in ['NW', 'SE']: return 90
        if b in ['W', 'S']: return 135
        else: return 180
    if a == 'E':
        if b in ['NE', 'SE']: return 45
        if b in ['N', 'S']: return 90
        if b in ['NW', 'SW']: return 135
        else: return 180
    if a == 'SE':
        if b in ['E', 'S']: return 45
        if b in ['NE', 'SW']: return 90
        if b in ['W', 'N']: return 135
        else: return 180
    if a == 'S':
        if b in ['SW', 'SE']: return 45
        if b in ['W', 'E']: return 90
        if b in ['NW', 'NE']: return 135
        else: return 180
    if a == 'SW':
        if b in ['W', 'S']: return 45
        if b in ['NW', 'SE']: return 90
        if b in ['N', 'E']: return 135
        else: return 180
    if a == 'W':
        if b in ['NW', 'SW']: return 45
        if b in ['N', 'S']: return 90
        if b in ['NE', 'SE']: return 135
        else: return 180
    if a == 'NW':
        if b in ['W', 'N']: return 45
        if b in ['SW', 'NE']: return 90
        if b in ['S', 'E']: return 135
        else: return 180
    

pygame.init()
pygame.display.set_mode((640,480))
joystick = pygame.joystick.Joystick(0)
joystick.init()
keys = []
char_dir = 'N'
pygame.time.set_timer(USEREVENT, 1000) # 8 fps
list_dir_keys = [K_KP0, K_KP1, K_KP2, K_KP3, K_KP4, K_KP6, K_KP7, K_KP8, K_KP9]
while (1):
    for event in pygame.event.get():
        keyMods = pygame.key.get_mods()
        if event.type == pygame.KEYDOWN:
            if keyMods == KMOD_LSHIFT and event.key in list_dir_keys:
                keys.append(event.key)
                while len(keys) > 2:
                    keys.remove(keys[0])
            elif event.key in list_dir_keys:
                char_dir = key_to_dir(event.key)
        if event.type == pygame.USEREVENT:
            if len(keys) == 2:
                if keys[0] == keys[1]:
                    keys.remove(keys[0])
                elif get_angle(key_to_dir(keys[0]), key_to_dir(keys[1])) == 180:
                    keys.remove(keys[0])
            if keyMods == KMOD_LSHIFT:
                if len(keys) == 2:
                    print 'Slashing ',
                    print key_to_dir(keys[0]), '-', key_to_dir(keys[1])
                    print '(', get_angle(key_to_dir(keys[0]), key_to_dir(keys[1])), ' degrees)'
                    char_dir = key_to_dir(keys[1])
                elif len(keys) == 1:
                    print 'Stabbing', key_to_dir(keys[0])
                    char_dir = key_to_dir(keys[0])
                else:
                    print 'Stabbing', char_dir
            else:
                if len(keys) == 2:
                    print 'Slashing ',
                    print key_to_dir(keys[0]), '-', key_to_dir(keys[1])
                    print '(', get_angle(key_to_dir(keys[0]), key_to_dir(keys[1])), ' degrees)'
                    char_dir = key_to_dir(keys[1])
                elif len(keys) == 1:
                    print 'Stabbing', key_to_dir(keys[0])
                    char_dir = key_to_dir(keys[0])
                else:
                    print 'Walking', char_dir
            keys = []
