shifts = {
'a': 'ah',
'b': 'bv',
'c': 'kh',
'd': 'dh',
'e': 'eh',
'f': 'bv',
'g': 'gh',
'h': 'k',
'i': 'ei',
'j': 'zh',
'k': 'gk',
'l': 'lh',
'm': 'mh',
'n': 'nd',
'o': 'oh',
'p': 'br',
'qu': 'kv',
'r': 'rh',
's': 'dz',
't': 'tr',
'u': 'uh',
'v': 'bv',
'w': 'gv',
'x': 'gz',
'y': 'ny',
'z': 'sz',
}

vowels = ['a', 'e', 'i', 'o', 'u', 'y', 'ae', 'ai', 'ao', 'au', 'ea', 'ee', 'ei', 'eu', 'oa', 'oi', 'oo', 'ou']
consonants = ['b', 'c', 'ch', 'ck', 'd', 'dd', 'f', 'ff', 'g', 'h', 'j', 'k', 'l', 'm', 'mm', 'n', 'ng', 'p', 'ph', 'qu', 'r', 's', 'sch', 'sh', 'ss', 't', 'th', 'tt', 'v', 'w', 'wh', 'x', 'y', 'z', 'zh']
cc_blends = ['bl', 'br', 'bv', 'bw', 'bz', 'chr', 'cl', 'cr', 'cz', 'dr', 'dv', 'dz', 'fl', 'fr', 'fy', 'gh', 'gl', 'gn', 'gr', 'gv', 'gw', 'gy', 'gz', 'kh', 'kl', 'kr', 'ks', 'kv', 'kw', 'ky', 'kz', 'nd', 'nk', 'nt', 'ny', 'pl', 'pr', 'ps', 'py', 'pz', 'rg', 'rh', 'rv', 'rz', 'sc', 'scr', 'shr', 'sk', 'skl', 'skr', 'sl', 'st', 'str', 'sv', 'sw', 'sz', 'tr', 'ts', 'tz', 'vr', 'wr', 'zh']

def string_to_array(source_word):
    global vowels, consonants
    letters = vowels + consonants
    array = []
    lindex = 0
    while lindex < len(source_word):
        next_letter = auto_caps(source_word[lindex])
        for i in [4,3,2,1]:
            block = source_word[lindex:lindex+i]
            if block.lower() in letters:
                next_letter = auto_caps(block)
                break
        array.append(next_letter)
        lindex += len(next_letter)
    return array

def array_to_string(array):
    string = ''
    for i in array:
        string += i
    return string

def auto_caps(letter):
    output = ''
    if letter[0] == letter[0].upper():
        output += letter[0].upper()
    else:
        output += letter[0]
    for x in range(1, len(letter)):
        output += letter[x]
    return output

def transform(string):
    global shifts
    new_array = []
    lindex = 0
    while lindex < len(string):
        next_letter = string[lindex]
        for i in [4,3,2,1]:
            if lindex+i <= len(string):
                block = string[lindex:lindex+i]
                if block.lower() in shifts:
                    next_letter = shifts[block.lower()]
                    break
        new_array.append(next_letter)
        lindex += i
    string = array_to_string(new_array)
    return string

def CVCC_to_CCVC(string):
    global consonants, vowels
    lindex = 0
    dest_array = []
    array = string_to_array(string)
    if string[0].lower() in vowels and string[1].lower() in consonants and string[2].lower() in consonants:
        block = string[1] + string[0] + string[2]
        dest_array += block
        lindex += 3
    while lindex < len(array):
        if lindex+4 <= len(array):
            block = array[lindex:lindex+4]
            if block[0].lower() in consonants and block[1].lower() in vowels and block[2].lower() in consonants and block[3].lower() in consonants:
                if block[0].lower() + block[2].lower() in cc_blends:
                    block = block[0] + block[2] + block[1] + block[3]
                    dest_array += block
                    lindex += 4
                elif block[0].lower() + block[3].lower() in cc_blends:
                    block = block[0] + block[3] + block[1] + block[2]
                    dest_array += block
                    lindex += 4
                else:
                    dest_array += block[0]
                    lindex += 1
            else:
                dest_array += block[0]
                lindex += 1
        else:
            dest_array += array[lindex]
            lindex += 1
    return array_to_string(dest_array)

def CC_to_CaC(string):
    global consonants, vowels
    lindex = 0
    dest_array = []
    array = string_to_array(string)
    while lindex < len(array):
        if lindex+2 <= len(array):
            block = array[lindex:lindex+2]
            if block[0].lower() in consonants and block[1].lower() in consonants and block[0].lower() + block[1].lower() not in cc_blends:
                if block[0].lower() == block[1].lower():
                    dest_array += block[0]
                    lindex += 2
                else:
                    dest_array += block[0]
                    dest_array += 'a'
                    dest_array += block[1]
                    lindex += 2
            else:
                dest_array += block[0]
                lindex += 1
        else:
            dest_array += array[lindex]
            lindex += 1
    return array_to_string(dest_array)

while (1):
    input = raw_input()
    input = transform(input)
    input = CVCC_to_CCVC(input)
    input = CC_to_CaC(input)
    print input
