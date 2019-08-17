shifts = {
'a': 'a',
'aa': 'e',
'ae': 'ai',
'ah': 'ag',
'ai': 'e',
'ala': 'la',
'ao': 'ou',
'as': 'az',
'ask': 'akz',
'au': 'av',
'aw': 'au',
'b': 'b',
'bj': 'vz',
'br': 'vr',
'bar': 'var',
'ber': 'ver',
'bir': 'vir',
'bor': 'vor',
'bv': 'vv',
'c': 'k',
'ch': 'k',
'chr': 'gr',
'ck': 'k',
'cl': 'gl',
'cr': 'gr',
'd': 'd',
'dd': 'dz',
'dj': 'g',
'ds': 's',
'dt': 'd',
'dw': 'dv',
'dz': 'z',
'e': 'e',
'ea': 'o',
'eau': 'eu',
'ed': 'ad',
'ee': 'ai',
'ei': 'e',
'eo': 'io',
'eou': 'io',
'es': 'ez',
'eu': 'u',
'ew': 'av',
'ey': 'i',
'eye': 'ey',
'f': 'f',
'ff': 'v',
'fr': 'pr',
'ft': 'pt',
'g': 'g',
'geo': 'jo',
'gg': 'g',
'gh': 'g',
'gn': 'n',
'gue': 'we',
'gui': 'wi',
'gua': 'wa',
'gt': 't',
'gv': 'v',
'gwe': 'we',
'gz': 'z',
'h': 'e',
'i': 'i',
'ii': 'i',
'ia': 'ie',
'ie': 'e',
'ig': 'ey',
'io': 'ia',
'ion': 'en',
'iou': 'io',
'iri': 'ri',
'is': 'es',
'iu': 'io',
'j': 'gz',
'k': 'g',
'kh': 'kz',
'l': 'l',
'll': 'l',
'm': 'm',
'mm': 'lm',
'mp': 'b',
'n': 'n',
'nn': 'nd',
'nf': 'dv',
'ng': 'g',
'nge': 'zh',
'ngh': 'nk',
'nk': 'k',
'ns': 'nz',
'o': 'o',
'oa': 'ia',
'oh': 'o',
'oi': 'i',
'oo': 'u',
'ol': 'el',
'ou': 'u',
'ow': 'ov',
'owl': 'ovel',
'own': 'one',
'p': 'p',
'ph': 'f',
'pp': 'ff',
'pr': 'br',
'pt': 't',
'q': 'q',
'qu': 'kv',
'r': 'r',
'rd': 'rz',
'rds': 'rzis',
're': 'ri',
'rh': 'gr',
'rr': 'rh',
'rt': 'rs',
'rth': 'rz',
's': 's',
'sc': 'sk',
'sch': 'sk',
'sg': 'gz',
'sh': 'sk',
'sion': 'skin',
'ssion': 'skin',
'sk': 'kz',
'sl': 'zl',
'sm': 'sp',
'ss': 's',
'st': 'tz',
'str': 'zdr',
'sw': 'sv',
'sz': 'z',
't': 't',
'tch': 'ch',
'tia': 'sha',
'tion': 'ten',
'tt': 't',
'th': 'dz',
'thr': 'zr',
"t's": "t is",
'td': 't',
'ts': 'tz',
'tz': 'z',
'tw': 'tv',
'tv': 'zv',
'u': 'o',
'v': 'v',
'vv': 'w',
'w': 'gv',
'wh': 'gv',
'wr': 'vr',
'x': 'z',
'y': 'i',
'ye': 'yi',
'yi': 'i',
'z': 'z',
'zdr': 'dr',
'zz': 'z',
'zs': 'tz',
}

vowels = ['a', 'e', 'i', 'o', 'u', 'y', 'ae', 'ai', 'ao', 'au', 'ea', 'ee', 'ei', 'eu', 'oa', 'oi', 'oo', 'ou']
consonants = ['b', 'c', 'ch', 'ck', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'ph', 'qu', 'r', 's', 'sch', 'sh', 'ss', 't', 'th', 'tt', 'v', 'w', 'x', 'y', 'z']
cc_blends = ['bl', 'br', 'bz', 'ch', 'cl', 'cr', 'cz', 'dr', 'dv', 'dz', 'fl', 'fr', 'gl', 'gn', 'gr', 'gv', 'gz', 'kl', 'kr', 'ks', 'kz', 'pl', 'pr', 'ps', 'pz', 'rg', 'rh', 'shr', 'sk', 'sl', 'st', 'sv', 'tr', 'ts', 'tz', 'vr', 'wr']

def auto_caps(key):
    output = ''
    global shifts
    value = shifts[key.lower()]
    if key[0] == key[0].upper():
        output += value[0].upper()
    else:
        output += value[0]
    for x in range(1, len(shifts[key.lower()])):
        output += value[x]
    return output
            
def transform(source_word):
    global shifts
    transformation = []
    dest_word = ''
    lindex = 0
    while lindex < len(source_word):
        letter = source_word[lindex]
        dl = 1
        for i in range(10):
            if source_word[lindex:lindex+i].lower() in shifts:
                letter = auto_caps(source_word[lindex:lindex+i])
                dl = i
        transformation.append(letter)
        lindex += dl
    for i in transformation:
        dest_word += i
    return dest_word

while (1):
    input = raw_input()
    print transform(input)
