def auto_caps(key, letters):
    output = ''
    value = letters[key.lower()]
    if key[0] == key[0].upper():
        output += value[0].upper()
    else:
        output += value[0]
    for x in range(1, len(letters[key.lower()])):
        output += value[x]
    return output

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
phonetic = {}
for letter in letters:
    phonetic[letter] = letter
phonetic.update({
'ae': 'ei',
'c': 'k',
'igh': 'ei',
'ck': 'k',
'it\'s': 'it is',
'\'ll': 'will',
'\'m': ' am',
'qu': 'kw',
'\'re': ' are',
'rr': 'r',
'ss': 's',
'tion': 'shin',
'tr': 'chr',
'tt': 't',
'wh': 'w',
'x': 'ks',
})

def transform(source_word, letters):
    transformation = []
    dest_word = ''
    lindex = 0
    while lindex < len(source_word):
        letter = source_word[lindex]
        if source_word[lindex:lindex+4].lower() in letters:
            transformation.append(auto_caps(source_word[lindex:lindex+4], letters))
            lindex += 4
        elif source_word[lindex:lindex+3].lower() in letters:
            transformation.append(auto_caps(source_word[lindex:lindex+3], letters))
            lindex += 3
        elif source_word[lindex:lindex+2].lower() in letters:
            transformation.append(auto_caps(source_word[lindex:lindex+2], letters))
            lindex += 2
        elif source_word[lindex].lower() in letters:
            transformation.append(auto_caps(source_word[lindex], letters))
            lindex += 1
        else:
            transformation.append(letter)
            lindex += 1
    for i in transformation:
        dest_word += i
    return dest_word

while (1):
    input = raw_input()
    print transform(input, phonetic)
