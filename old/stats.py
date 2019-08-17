class Stats:
    """
    Represents the player's stats for general purposes. Also allows
    output of stat requirements for items and spells.
    """
    def __init__(self, game, strength, dexterity, intellect, wisdom, fortitude):
        self.strength = strength
        self.dexterity = dexterity
        self.intellect = intellect
        self.wisdom = wisdom
        self.fortitude = fortitude

    def output_tooltip(self):
        """ generates the item's stat requirements for tooltip construction. """
        tooltip = []
        if self.strength:
            tooltip.append(str(self.strength) + ' Strength required')
        if self.dexterity:
            tooltip.append(str(self.dexterity) + ' Dexterity required')
        if self.intellect:
            tooltip.append(str(self.intellect) + ' Intellect required')
        if self.wisdom:
            tooltip.append(str(self.wisdom) + ' Wisdom required')
        if self.fortitude:
            tooltip.append(str(self.fortitude) + ' Fortitude required')
        return tooltip

