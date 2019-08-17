class StatBonuses:
    """
    Contains information for the stat bonuses granted by an item.  Also allows
    tooltip output.
    """
    def __init__(self, **dict):
        self.dict = dict

    def output_tooltip(self):
        tooltip = []
        """ generates the item's stat bonuses for tooltip construction. """
        if 'attack_power' in self.dict:
            tooltip.append('+ ' + str(self.dict['attack_power']) + ' Attack Power')
        if 'spell_power' in self.dict:
            tooltip.append('+ ' + str(self.dict['spell_power']) + ' Spell Power')
        if 'magic_resistance' in self.dict:
            tooltip.append('+ ' + str(self.dict['magic_resistance']) + '% Magic Resistance')
        if 'mitigation' in self.dict:
            tooltip.append('+ ' + str(self.dict['mitigation']) + '% Mitigation')
        if 'avoid_chance' in self.dict:
            tooltip.append('+ ' + str(self.dict['avoid_chance']) + '% Avoidance')
        return tooltip

