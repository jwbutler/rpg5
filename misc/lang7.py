vowels = ['a', 'e', 'i', 'o', 'u', 'y', 'ae', 'ai', 'ao', 'au', 'ea', 'ee', 'ei', 'eu', 'oa', 'oi', 'oo', 'ou']
initial_consonants = ['b', 'bl', 'br', 'bv', 'by', 'c', 'ch', 'cl', 'cn', 'cr', 'cs', 'cz', 'd', 'dr', 'dz', 'f', 'fl', 'fr', 'ft', 'g', 'gl', 'gn', 'gr', 'gu', 'gv', 'gz', 'h', 'hr', 'j', 'k', 'kl', 'kn', 'kr', 'ks', 'kv', 'kz', 'l', 'm', 'mm', 'mn', 'n', 'p', 'ph', 'pl', 'pr', 'pz', 'qu', 'r', 'rv', 's', 'sc', 'sch', 'scr', 'sh', 'shr', 'sk', 'skl', 'skr', 'sl', 'ss', 'sv', 't', 'th', 'tr', 'tz', 'v', 'vr', 'vt', 'w', 'wh', 'wr', 'y', 'z', 'zh']
middle_consonants = ['b', 'bb', 'br', 'c', 'cc', 'ch', 'cl', 'cn', 'cqu', 'cr', 'cv', 'cz', 'd', 'dd', 'dj', 'dr', 'dv', 'dz', 'f', 'ff', 'fr', 'ft', 'g', 'gg', 'ggl', 'ggr', 'gl', 'gn', 'gr', 'gv', 'gz', 'h', 'j', 'k', 'kl', 'kn', 'kr', 'ks', 'kz', 'l', 'ld', 'll', 'lt', 'lv', 'lz', 'm', 'mb', 'mm', 'mp', 'n', 'nd', 'ng', 'nn', 'nt', 'nv', 'nz', 'p', 'ph', 'pl', 'pr', 'ps', 'pz', 'qu', 'r', 'rc', 'rk', 'rqu', 'rv', 's', 'sc', 'sch', 'sh', 'shr', 'sk', 'skr', 'ss', 'str', 't', 'th', 'tr', 'ts', 'tt', 'tz', 'v', 'vr', 'w', 'wh', 'wr', 'x', 'xc', 'xcl', 'xcr', 'y', 'z', 'zh']
final_consonants = ['b', 'bb', 'c', 'ch', 'ck', 'ct', 'd', 'dd', 'f', 'ff', 'ft', 'g', 'h', 'j', 'k', 'l', 'll', 'm', 'mm', 'n', 'ng', 'nn', 'p', 'ph', 'pse', 'que', 'r', 'rque', 's', 'sch', 'sh', 'ss', 'str', 't', 'th', 'tt', 'w', 'x', 'y', 'z', 'zh']
shifts = {'j': 'gz'}

class Block:
    def __init__(self, string):
        self.string = string

    def transform(self, shifts):
        if self.string in shifts:
            return shifts[self.string]
        else:
            return self.string

    def length(self):
        return len(self.string)

    def lower(self):
        return self.string.lower()

    def upper(self):
        return self.string.upper()

class BlockArray():
    def __init__(self, block_list):
        self.block_list = block_list
        self.refresh()

    def refresh(self):
        global vowels, initial_consonants, middle_consonants, final_consonants
        self.vowels = self.match(vowels)
        self.consonants = self.match(initial_consonants + middle_consonants + final_consonants)
        print self.vowels, self.consonants

    def append(self, block):
        self.block_list.append(block)
        self.refresh()

    def match(self, match_list):
        dest_array = []
        i = 0
        while 1:
            dest_array.append([])
            for block in self.block_list:
                if block.lower() in match_list:
                    print i, len(dest_array)
                    dest_array[i].append(block)
                elif block.string == ' ':
                    i += 1
                    break
            return dest_array

    def recombine(self):
        global vowels, initial_consonants, middle_consonants, final_consonants
        array = BlockArray([])
        i = 0
        first_consonant = self.consonants[0].pop(0)
        if first_consonant.lower() in initial_consonants:
            array.append(Block(first_consonant.string.upper()))
        else:
            array.append(Block(self.vowels[0].pop(0).string.upper()))
            array.append(Block(first_consonant.string.lower()))

        while len(self.consonants) > 0 and len(self.vowels) > 0:
            if self.consonants[0] == ' ':
                if array[len(array)-1] != ' ':
                    array.append(self.consonants.pop(0))
            else:
                array.append(Block(self.vowels.pop(0).string.lower()))
                array.append(Block(self.consonants.pop(0).string.lower()))
        return array

    def to_string(self):
        str = ''
        for block in self.block_list:
            str += block.string
        return str

class StringObj:
    def __init__(self, string):
        self.string = string
    
    def decompose(self, blocks):
        array = BlockArray([])
        index = 0
        for length in range(len(self.string), index, -1):
            next_block = Block(self.string[index])
            for string in blocks:
                block = Block(string)
                if block.string == self.string[index:index+length]:
                    next_block = block
            array.append(next_block)
            index += next_block.length()
            if index >= len(self.string):
                return array

input = StringObj('Jack Butler is awesome')
array = input.decompose(vowels + initial_consonants + middle_consonants + final_consonants)
array2 = array.recombine()
print array2.to_string()

