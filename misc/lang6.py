shifts = {
'a': 'a',
'b': 'r',
'c': 'k',
'ch': 'j',
'ck': 'k',
'd': 'd',
'e': 'e',
'f': 'v',
'g': 'g',
'h': 'g',
'i': 'i',
'ious': 'ioz',
'j': 'gz',
'k': 'k',
'l': 'l',
'll': 'ld',
'lm': 'lv',
'm': 'm',
'mm': 'm',
'mp': 'b',
'n': 'n',
'ng': 'g',
'o': 'a',
'oo': 'u',
'ous': 'az',
'p': 'b',
'qu': 'kv',
'r': 'r',
's': 'z',
'sh': 'j',
'st': 'ts',
't': 'd',
'th': 'v',
'tt': 'd',
'tion': 'jin',
'u': 'o',
'v': 'v',
'w': 'gv',
'wh': 'gv',
'x': 'kz',
'y': 'y',
'z': 'z'
}

vowels = ['a', 'e', 'i', 'o', 'u', 'y', 'ae', 'ai', 'ao', 'au', 'ea', 'ee', 'ei', 'eu', 'oa', 'oi', 'oo', 'ou']
initial_consonants = ['b', 'bl', 'br', 'bv', 'by', 'c', 'ch', 'cl', 'cn', 'cr', 'cs', 'cz', 'd', 'dr', 'dz', 'f', 'fl', 'fr', 'ft', 'g', 'gl', 'gn', 'gr', 'gu', 'gv', 'gz', 'h', 'hr', 'j', 'k', 'kl', 'kn', 'kr', 'ks', 'kv', 'kz', 'l', 'm', 'mm', 'mn', 'n', 'p', 'ph', 'pl', 'pr', 'pz', 'qu', 'r', 'rv', 's', 'sc', 'sch', 'scr', 'sh', 'shr', 'sk', 'skl', 'skr', 'sl', 'ss', 'sv', 't', 'th', 'tr', 'tz', 'v', 'vr', 'vt', 'w', 'wh', 'wr', 'y', 'z', 'zh']
middle_consonants = ['b', 'bb', 'br', 'c', 'cc', 'ch', 'cl', 'cn', 'cqu', 'cr', 'cv', 'cz', 'd', 'dd', 'dj', 'dr', 'dv', 'dz', 'f', 'ff', 'fr', 'ft', 'g', 'gg', 'ggl', 'ggr', 'gl', 'gn', 'gr', 'gv', 'gz', 'h', 'j', 'k', 'kl', 'kn', 'kr', 'ks', 'kz', 'l', 'ld', 'll', 'lt', 'lv', 'lz', 'm', 'mb', 'mm', 'mp', 'n', 'nd', 'ng', 'nn', 'nt', 'nv', 'nz', 'p', 'ph', 'pl', 'pr', 'ps', 'pz', 'qu', 'r', 'rc', 'rk', 'rqu', 'rv', 's', 'sc', 'sch', 'sh', 'shr', 'sk', 'skr', 'ss', 'str', 't', 'th', 'tr', 'ts', 'tt', 'tz', 'v', 'vr', 'w', 'wh', 'wr', 'x', 'xc', 'xcl', 'xcr', 'y', 'z', 'zh']
final_consonants = ['b', 'bb', 'c', 'ch', 'ck', 'ct', 'd', 'dd', 'f', 'ff', 'ft', 'g', 'h', 'j', 'k', 'l', 'll', 'm', 'mm', 'n', 'ng', 'nn', 'p', 'ph', 'pse', 'que', 'r', 'rque', 's', 'sch', 'sh', 'ss', 'str', 't', 'th', 'tt', 'w', 'x', 'y', 'z', 'zh']

def remove_vowels(str):
    global vowels, initial_consonants, middle_consonants, final_consonants, shifts
    consonants = initial_consonants + middle_consonants + final_consonants
    source_array = string_to_array(str, [vowels + consonants])
    dest_array = []
    dest_vowels = []
    for phoneme in source_array:
        if phoneme.lower() not in vowels or phoneme.lower() == 'y':
            dest_array.append(phoneme)
        else:
            dest_vowels.append(phoneme)
    str = array_to_string(dest_array)
    return dest_vowels

def insert_vowels(str, src_vowels):
    global initial_consonants, middle_consonants, final_consonants, vowels, shifts
    consonants = initial_consonants + middle_consonants + final_consonants
    letters = vowels + consonants
    source_array = string_to_array(str, shifts)
    dest_array = []

    #remove leading/trailing spaces
    if source_array[0].lower() not in letters:
        source_array = source_array[1:len(source_array)]
    if source_array[len(source_array)-1] not in letters:
        source_array = source_array[0:len(source_array)-1]

    if len(source_array) == 0: return False

    # if the first letter is invalid, prepend a vowel
    if source_array[0] == ' ':
        dest_array.append('a')
    elif source_array[0].lower() in letters and source_array[0].lower() not in initial_consonants:
        dest_array.append('a')
        source_array[0] = source_array[0].lower()

    for i in range(0, len(source_array)):

        # if the first letter of a word is invalid, prepend a vowel
        if i > 1:
            if source_array[i-1].lower() not in letters and source_array[i].lower() not in initial_consonants:
                dest_array.append(src_vowels.pop())
                source_array[i] = source_array[i].lower()

        # if the word consists of a single consonant, prepend a vowel
        if i > 1 and i < len(source_array)-1:
            if source_array[i].lower() in letters and source_array[i-1].lower() not in letters and source_array[i+1].lower() not in letters:
                if source_array[i].lower() in final_consonants:
                    dest_array.append(src_vowels.pop())

        # copy each consonant
        dest_array.append(source_array[i])

        # if the word consists of a single consonant, prepend a vowel
        if i > 1 and i < len(source_array)-1:
            if source_array[i].lower() in letters and source_array[i-1].lower() not in letters and source_array[i+1].lower() not in letters:
                if source_array[i].lower() not in final_consonants:
                    dest_array.append(src_vowels.pop())

        # insert a vowel between each consonant cluster pair
        if i < len(source_array)-1:
            if source_array[i].lower() in letters and source_array[i+1].lower() in letters:
                dest_array.append(src_vowels.pop())

        # if the last letter of a word is invalid, append a vowel
        if i < len(source_array)-1:
            if source_array[i].lower() in letters and source_array[i+1].lower() == ' ' and source_array[i].lower() not in final_consonants:
                dest_array.append(src_vowels.pop())

    # if the last letter is invalid, append a vowel
    if dest_array[len(dest_array)-1] not in final_consonants:
        dest_array.append(src_vowels.pop())
    return array_to_string(dest_array)

def string_to_array(source_word, blocks):
    array = []
    lindex = 0
    while lindex < len(source_word):
        next_letter = auto_caps(source_word[lindex], blocks)
        for i in range(1,10):
            block = source_word[lindex:lindex+i]
            if block.lower() in blocks:
                next_letter = get_next_letter(block, blocks)
                increment = i
        array.append(next_letter)
        lindex += len(next_letter)
    return array

def array_to_string(array):
    string = ''
    for i in array:
        string += i
    return string

def transform(source_word, shifts):
    transformation = []
    dest_word = ''
    lindex = 0
    while lindex < len(source_word):
        letter = source_word[lindex]
        next_letter = letter
        increment = 1
        for i in range(1,5):
            block = source_word[lindex:lindex+i]
            if block.lower() in shifts.keys():
                shifted = shifts[block.lower()]
                next_letter = get_next_letter(block, blocks)
                increment = i
        transformation.append(next_letter)
        lindex += increment
    for i in transformation:
        dest_word += i
    return dest_word

while 1:
    input = raw_input()
    vowels = remove_vowels(input)
    print input
