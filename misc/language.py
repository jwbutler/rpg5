import random
class Cycle:
    def __init__(self, letters):
        self.letters = letters
        self.lindex = 0

    def increment(self, letter, steps):
        self.lindex = self.letters.index(letter.lower())
        self.lindex += steps
        self.lindex %= len(self.letters)
        if self.lindex == len(self.letters):
            self.lindex = 0
        if letter == letter.upper():
            return self.letters[self.lindex].title()
        else:
            return self.letters[self.lindex]

cycles = [Cycle(('p', 'b', 'v', 'ff')), Cycle(('k', 'c', 'g', 'gh', 'h', 'kh')),
Cycle(('ck', 'gg', 'ng', 'nk')), Cycle(('ss', 's', 'z', 'dz')), Cycle(('f', 'ph', 'v', 'gv')), Cycle(('wh', 'gw', 'w', 'gu', 'qu', 'kw')), Cycle(('x', 'ks', 'kz', 'gz')),
Cycle(('ky', 'gy')), Cycle(('t', 'd', 'dh', 'th')), Cycle(('ch', 'j', 'zh',
'tio', 'sh')), Cycle(('ee', 'y', 'ey', 'ei', 'ae', 'ai', 'ay', 'ea')), Cycle(('i', 'e',
'a')), Cycle(('oo', 'ou', 'eu')), Cycle(('o', 'au', 'ah', 'oh'))]

def transform(source_word, steps = [1,1,1,1,1,1,1,1,1,1,1,1,1,1]):
    transformation = []
    dest_word = ''
    lindex = 0
    while lindex < len(source_word):
        letter = source_word[lindex]
        next_letter = letter
        for cycle in cycles:
            blend = source_word[lindex:lindex+3]
            if blend.lower() in cycle.letters:
                next_letter = cycle.increment(blend, \
                steps[cycles.index(cycle)])
                lindex += 2
            blend = source_word[lindex:lindex+2]
            if blend.lower() in cycle.letters:
                next_letter = cycle.increment(blend, \
                steps[cycles.index(cycle)])
                lindex += 1
            elif letter.lower() in cycle.letters:
                next_letter = cycle.increment(letter, \
                steps[cycles.index(cycle)])
        transformation.append(next_letter)
        lindex += 1
    for i in transformation:
        dest_word += i
    return dest_word

def create_random_key(n):
    key = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    for i in range(0,n):
        j = random.randint(0,13)
        key[j] += 1
    return key
        

str = '\n\narma virumque cano, Troiae qui primus ab oris\n\
Italiam fato profugus Laviniaque venit\n\
litora, multum ille et terris iactatus et alto\n\
vi superum, saevae memorem Iunonis ob iram,\n\
multa quoque et bello passus, dum conderet urbem\n\
inferretque deos Latio; genus unde\n\
Albanique patres atque altae moenia Romae.\n\n'

while (1):
    str = raw_input()
    #print '> '+transform(str, create_random_key(1))
    print '> '+transform(str)

