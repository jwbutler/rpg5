class NPC(BasicCharacter):
    """
    Non-player characters.  Structurally, basically a clone of a Player, but with different
    input (ai).
    """

    def __init__(self, game, name, anim_name, (x, y), palette_swaps = {}):
        self.name = name
        self.anim_name = anim_name
        (self.x, self.y) = (x,y)
        self.type = 'Humanoid'
        self.dx = 0
        self.dy = -1
        self.stats = Stats(game, 10,10,10,10,10)
        zero_stats = Stats(game, 0, 0, 0, 0, 0)
        self.equipment = [Armor(game, 'Chain Mail', 'mail', zero_stats, StatBonuses(mitigation = 20)), Helm(game, 'Helm of Mega Suck', 'helm2', zero_stats, StatBonuses(mitigation = 20)), Shield(game, 'Metal Shield', 'shield2', zero_stats, StatBonuses(avoid_chance = 20)), Sword(game, 'Gladius Pessimus', 'sword', 4, 8, zero_stats, StatBonuses())]
        self.inventory = []
        self.attack_targets = []
        self.activities = ['standing', 'walking', 'attacking', 'dazed', 'falling', 'dead', 'decapitated', 'dead_decapitated']
        self.spells = []
        self.current_activity = 'standing'
        self.animations = []
        self.max_hp = self.stats.fortitude * 10
        self.avoid_chance = self.stats.dexterity
        self.current_hp = self.max_hp
        self.ticks = 0
        self.palette_swaps = palette_swaps
        self.load_animations(game)

    

    def in_line(self, obj):
        """ Is there a direct horizontal/vertical/diagonal path to the target? (for fireballs) """
        if self.x == obj.x:
            return True
        elif self.y == obj.y:
            return True
        elif self.x + self.y == obj.x + obj.y:
            return True
        elif self.x - self.y == obj.x - obj.y:
            return True
        return False

    def do_events(self, game):
        # any type of npc
        if self.ticks >= 4:
            if self.current_activity == 'falling':
                self.refresh_activity(game, 'dead')
                self.reset_ticks()
                game.npcs.remove(self)
                npc_corpse = Container(game, self.x, self.y, self.get_current_frame(), self.get_current_frame(), self.get_current_frame(), self.equipment + self.inventory, True)
                game.containers.append(npc_corpse)
                if game.target == self:
                    game.target = None
            if self.current_activity == 'dazed':
                self.point_at(game, game.player)
                self.refresh_activity(game, 'standing')
                self.reset_ticks()
        if self.ticks == 4:
            if self.current_activity == 'decapitated':
                self.refresh_activity(game, 'dead_decapitated')
                game.npcs.remove(self)
                npc_corpse = Container(game, self.x, self.y, self.get_current_frame(), self.get_current_frame(), self.get_current_frame(), self.equipment, True)
                game.containers.append(npc_corpse)
                if game.target == self:
                    game.target = None
                self.reset_ticks()
            # reset to standing animation if an attack is completing
            elif self.current_activity == 'attacking':
                self.refresh_activity(game, 'standing')
                for obj in self.attack_targets:
                    if (obj.x, obj.y) == (self.x + self.dx, self.y + self.dy):
                        obj.take_damage(self, self.damage())
                self.attack_targets = []
                self.reset_ticks()
        
class NPC_Humanoid(NPC):

    def __init__(self, game, name, anim_name, (x, y), palette_swaps = {}):
        NPC.__init__(self, game, name, anim_name, (x, y), palette_swaps)

    def do_events(self, game):
        NPC.do_events(self, game)
        if self.ticks == 2:
            # reset to standing animation if an attack is completing
            if self.current_activity in ['standing', 'walking']:
                self.point_at(game, game.player)
                if not obstacle(game, (self.x+self.dx, self.y+self.dy)):
                    if random.randint(1,4) > 1:
                        self.refresh_activity(game, 'walking')
                        self.move(self.current_animation.directions[0])
                        self.reset_ticks()
                    else:
                        self.refresh_activity(game, 'standing')
                        self.reset_ticks()
                elif (self.x + self.dx, self.y + self.dy) == (game.player.x, game.player.y):
                    self.attack_targets = [game.player]
                    self.refresh_activity(game, 'attacking')
                    self.reset_ticks()
                else:
                    self.refresh_activity(game, 'standing')
                    self.reset_ticks()

class NPC_Wizard(NPC):
    def __init__(self, game, name, palette_swaps):
        self.name = name
        self.type = 'Wizard'
        self.x = 3
        self.y = 21
        self.dx = 0
        self.dy = -1
        self.stats = Stats(game, 10,10,50,50,50)
        self.equipment = []
        self.inventory = [Herb(game, 'Green Herb', 'herb.bmp', 50, 0)]
        self.spells = [DamageSpell(game, 'Fireball', 'fireball_flying', 25, 10, 20), Spell('teleport', 10, 20)]
        self.activities = ['standing', 'walking', 'vanishing', 'appearing', 'casting', 'stunned', 'dazed', 'falling', 'dead']
        self.current_activity = 'standing'
        self.animations = []
        self.max_hp = self.stats.fortitude * 10
        self.max_mp = self.stats.intellect * 10
        self.avoid_chance = self.stats.dexterity
        self.current_hp = self.max_hp
        self.current_mp = self.max_mp
        self.ticks = 0
        self.spell_ticks = 0
        self.palette_swaps = palette_swaps
        #convert this game.load_wizard_animations(self, self.palette_swaps, directions)

    def increment_ticks(self):
        self.ticks += 1
        self.spell_ticks += 1

    def reset_ticks(self):
        self.ticks = 0
        return True

    def reset_spells(self):
        self.spell_ticks = 0
        return True

    def do_events(self, game):
        NPC.do_events(self, game)
        if self.ticks == 12: #reset
            self.refresh_activity(game, 'standing')
            self.reset_ticks()
        elif self.ticks == 8:
            if self.current_activity == 'casting':
                projectiles.append(Projectile(self.spells[0].name, self.spells[0].damage, self.x, self.y, self.dx, self.dy, self, self.spells[0].frames, self.spells[0].filenames))
                if self.current_mp >= 0.25*self.max_mp and self.spells[1].ticks >= self.spells[1].cooldown and self.check_teleport():
                    self.current_mp -= self.spells[1].mana_cost
                    self.point_at(game, game.player)
                    self.refresh_activity(game, 'vanishing')
                    self.reset_ticks()
                elif self.current_mp >= npc.spells[0].mana_cost and npc.spells[0].ticks >= npc.spells[0].cooldown and in_line(npc, player):
                    self.current_mp -= npc.spells[0].mana_cost
                    self.refresh_activity(game, 'casting')
                    self.reset_ticks()
                    self.reset_spell_ticks()
                else:
                    # walk away from the player
                    self.refresh_activity(game, 'walking')
                    self.point_at(game, game.player)
                    (self.dx, self.dy) = (-self.dx, -self.dy)
                    self.reset_ticks()
        elif self.ticks == 4:
            if self.current_activity == 'vanishing':
                self.teleport()
                self.point_at(game, game.player)
                self.refresh_activity(game, 'appearing')
                self.reset_ticks()
            elif self.current_activity == 'appearing':
                self.point_at(game, game.player)
                self.refresh_activity(game, 'standing')
                self.reset_ticks()
            elif self.current_activity == 'dazed':
                self.point_at(game, game.player)
                self.refresh_activity(game, 'standing')
                self.reset_ticks()
            elif self.current_activity == 'standing':
                if self.current_mp >= 0.5*self.max_mp and self.spell_ticks >= self.spell_cooldown and self.check_teleport():
                    self.current_mp -= self.spells[1].mana_cost
                    self.point_at(game, game.player)
                    self.refresh_activity(game, 'vanishing')
                    self.reset_ticks()
                    self.reset_spell_ticks()
                elif self.current_mp >= self.spells[0].mana_cost and self.spell_ticks >= self.spell_cooldown and self.check_line(game.player):
                    self.current_mp -= npc.spells[0].mana_cost
                    self.refresh_activity(game, 'casting')
                    self.reset_ticks()
                    self.reset_spell_ticks()
                else:
                    npc.point_at(game, game.player)
                    (npc.dx, npc.dy) = (-npc.dx, -npc.dy)
                    self.refresh_activity(game, 'walking')
                    self.reset_ticks()
        elif self.ticks == 2:
            if self.current_activity == 'walking':
                if not obstacle(game, (self.x+self.dx, self.y+self.dy)):
                    self.move(self.current_animation.directions[0])
                self.point_at(game, game.player)
                self.refresh_activity(game, 'standing')
                self.reset_ticks()

    def teleport(self):
        """
        Teleport via knight move
        """
        squares = knight_move((self.x, self.y))
        squares.sort(lambda a,b: distance_sort(a,b,player))
        if game.distance(self, player) < 3:
            squares.reverse()
        for square in squares:
            if game.check_los((npc.x, npc.y), (player.x, player.y)):
                if game.check_los(square, (player.x, player.y)) and not game.obstacle(square):
                    (self.x, self.y) = square
                    return True
            else:
                if not game.obstacle(square):
                    (self.x, self.y) = square
                    return True

    def check_teleport(self):
        """
        Check candidates
        """
        squares = knight_move((self.x, self.y))
        squares.sort(lambda a,b: distance_sort(a,b,player))
        if distance(self, player) < 3:
            squares.reverse()
        for square in squares:
            if check_los((npc.x, npc.y), (player.x, player.y)):
                if check_los(square, (player.x, player.y)) and not obstacle(game, square):
                    return True
            else:
                if not obstacle(game, square):
                    return True
        return False

    def take_damage(self, source, damage):
        avoid_chance = self.avoid_chance
        mitigation = 0
        for equip in self.equipment:
            if equip.slot == 'offhand':
                if 'avoid_chance' in equip.stat_bonuses.dict:
                    avoid_chance += equip.stat_bonuses.dict['avoid_chance']
                    if self.current_activity == 'bashing':
                        avoid_chance += equip.stat_bonuses.dict['avoid_chance']
            elif equip.slot in ['head', 'chest']:
                if 'mitigation' in equip.stat_bonuses.dict:
                    mitigation += equip.stat_bonuses.dict['mitigation']
        damage *= (100 - mitigation) / 100
        if self.current_activity == 'stunned':
            damage *= 4
        i = random.randint(1,100)
        if i > avoid_chance:
            self.current_hp -= damage

    def take_magic_damage(self, source, damage):
        """ This will include stat-based avoidance and item-based mitigation soon. """
        if self.current_activity == 'bashing':
            if random.randint(1,2) == 1: # should be stat-based :(
                return True
        if self.current_activity == 'stunned':
            damage *= 4
        self.current_hp -= damage
