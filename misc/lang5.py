def string_to_array(source_word):
    """ Converts a string to an array of phonemes.  Only used within functions. """
    global vowels, initial_consonants, middle_consonants, final_consonants
    consonants = initial_consonants + middle_consonants + final_consonants
    letters = vowels + consonants
    array = []
    lindex = 0
    while lindex < len(source_word):
        next_letter = auto_caps(source_word[lindex])
        for i in [5,4,3,2,1]:
            block = source_word[lindex:lindex+i]
            if block.lower() in letters:
                next_letter = auto_caps(block)
                break
        array.append(next_letter)
        lindex += len(next_letter)
    return array

def array_to_string(array):
    """ Converts an array of phonemes back into a string.  Only used within functions. """
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

vowels = ['a', 'e', 'i', 'o', 'u', 'y', 'ae', 'ai', 'ao', 'au', 'ea', 'ee', 'ei', 'eu', 'oa', 'oi', 'oo', 'ou']
initial_consonants = ['b', 'bl', 'br', 'bv', 'by', 'c', 'ch', 'cl', 'cn', 'cr', 'cs', 'cz', 'd', 'dr', 'dz', 'f', 'fl', 'fr', 'ft', 'g', 'gl', 'gn', 'gr', 'gu', 'gv', 'gz', 'h', 'hr', 'j', 'k', 'kl', 'kn', 'kr', 'ks', 'kv', 'kz', 'l', 'm', 'mm', 'mn', 'n', 'p', 'ph', 'pl', 'pr', 'pz', 'qu', 'r', 'rv', 's', 'sc', 'sch', 'scr', 'sh', 'shr', 'sk', 'skl', 'skr', 'sl', 'ss', 'sv', 't', 'th', 'tr', 'tz', 'v', 'vr', 'vt', 'w', 'wh', 'wr', 'y', 'z', 'zh']
middle_consonants = ['b', 'bb', 'br', 'c', 'cc', 'ch', 'cl', 'cn', 'cqu', 'cr', 'cv', 'cz', 'd', 'dd', 'dj', 'dr', 'dv', 'dz', 'f', 'ff', 'fr', 'ft', 'g', 'gg', 'ggl', 'ggr', 'gl', 'gn', 'gr', 'gv', 'gz', 'h', 'j', 'k', 'kl', 'kn', 'kr', 'ks', 'kz', 'l', 'ld', 'll', 'lt', 'lv', 'lz', 'm', 'mb', 'mm', 'mp', 'n', 'nd', 'ng', 'nn', 'nt', 'nv', 'nz', 'p', 'ph', 'pl', 'pr', 'ps', 'pz', 'qu', 'r', 'rc', 'rk', 'rqu', 'rv', 's', 'sc', 'sch', 'sh', 'shr', 'sk', 'skr', 'ss', 'str', 't', 'th', 'tr', 'ts', 'tt', 'tz', 'v', 'vr', 'w', 'wh', 'wr', 'x', 'xc', 'xcl', 'xcr', 'y', 'z', 'zh']
final_consonants = ['b', 'bb', 'c', 'ch', 'ck', 'ct', 'd', 'dd', 'f', 'ff', 'ft', 'g', 'h', 'j', 'k', 'l', 'll', 'm', 'mm', 'n', 'ng', 'nn', 'p', 'ph', 'pse', 'que', 'r', 'rque', 's', 'sch', 'sh', 'ss', 'str', 't', 'th', 'tt', 'w', 'x', 'y', 'z', 'zh']

while (1):
    str = raw_input()
    if str: str = remove_vowels(str)
    if str: str = insert_vowels(str)
    if str: print str

