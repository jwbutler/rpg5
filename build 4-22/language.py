from __future__ import division
import random
import string
import sys
consonants = [
              "b", "ch", "d",
              "f", "g", "h", "j", "k",
              "kh", #as in "loCH"
              "l", "m", "n", "p", "r", "s", "sh", "t", "th", "v", "w", "y", "z",
              "zh" #as in "pleaSure"
             ]
vowels = [
          "a",  #as in "bat"
          "e",  #as in "get"
          "i",  #as in "pit"
          "o",  #as in "pot"
          "u"   #as in "put"
         ]
cleanup_shifts = {
  "dge": "j",
  "ck": "k",
  "ph": "f",
  "qu": "kw",
  "wh": "w",
  "c": "k",
  "x": "ks"
}
possible_shifts = {
                   "a":  ["a", "e", "o"],
                   "b":  ["b", "p", "m"],
                   "ch": ["ch", "j", "sh", "zh"],
                   "d":  ["d", "t", "th", "n"],
                   "e":  ["a", "e", "i"],
                   "f":  ["f", "p", "th", "v"],
                   "g":  ["g", "h", "kh", "k"],
                   "h":  ["h", "kh", "y", "g"],
                   "i":  ["i", "e", "u"],
                   "j":  ["j", "ch", "sh", "zh"],
                   "k":  ["k", "kh", "g"],
                   "kh": ["kh", "k", "h", "g"],
                   "l":  ["l"],
                   "m":  ["m", "b"],
                   "n":  ["n", "d"],
                   "o":  ["o", "a", "e"],
                   "p":  ["p", "b", "f"],
                   "r":  ["r"],
                   "s":  ["s", "z"],
                   "sh": ["sh", "ch", "j", "zh"],
                   "t":  ["t", "d", "n", "th"],
                   "th": ["th", "f", "t"],
                   "u":  ["u", "o"],
                   "v":  ["v", "f", "w"],
                   "w":  ["w", "v"],
                   "y":  ["y", "g", "h"],
                   "z":  ["z", "s"],
                   "zh": ["zh", "ch", "j", "sh"]
                  }
shifts = {}
for key in possible_shifts.keys():
  shifts[key] = random.choice(possible_shifts[key])
# Next_consonants: returns the consonants that can follow a consonant to form single-syllable blends.
# Varies 
next_consonants_initial = { 
                   "b": ["l", "r", "v", "w", "y", "z", "zh"],
                   "ch": ["r", "w", "y"],
                   "d": ["j", "r", "v", "w", "y", "z", "zh"],
                   "f": ["l", "n", "r", "w", "y"],
                   "g": ["l", "n", "r", "v", "w", "y", "z", "zh"],
                   "h": ["r", "v", "w", "y"],
                   "j": ["r", "w", "y"],
                   "k": ["l", "n", "r", "s", "sh", "v", "w", "y"],
                   "kh": ["l", "n", "r", "v", "w", "y"],
                   "l": ["w", "y"],
                   "m": ["l", "n", "r", "y", "w"],
                   "n": ["r"],
                   "p": ["l", "r", "s", "sh", "w", "y"],
                   "r": [],
                   "s": ["l", "m", "n", "p", "t", "v", "w", "y"],
                   "sh": ["l", "m", "n", "p", "t", "w", "y"],
                   "t": ["r", "s", "sh", "w", "y"],
                   "th": ["r", "w"],
                   "v": ["l", "r", "w", "y"],
                   "w": ["r"],
                   "y": [],
                   "z": ["d", "l", "m", "r", "v", "y"],
                   "zh": ["b", "d", "l", "m", "r", "v", "w"]
                  }
next_consonants_final = {
                         "b": ["v", "z"],
                         "ch": ["t"],
                         "d": ["z", "zh"],
                         "f": ["s"],
                         "g": ["z", "zh"],
                         "h": [],
                         "j": [],
                         "k": ["s", "sh", "t"],
                         "kh": ["s", "t"],
                         "l": ["d", "g", "s", "t", "z"],
                         "m": ["d", "y", "z"],
                         "n": ["d", "s", "t", "z", "zh"],
                         "p": ["s", "t", "sh"],
                         "r": ["d", "k", "t", "s", "sh", "z"],
                         "s": ["k", "p", "t"],
                         "sh": ["k", "p", "t"],
                         "t": ["s"],
                         "th": ["k", "p", "t"],
                         "v": ["b", "d", "z"],
                         "w": ["b", "d", "f", "g", "j", "k", "p", "sh", "t", "th", "z", "zh"],
                         "y": ["b", "d", "f", "k", "g", "j", "s", "sh", "t", "th", "z", "zh"],
                         "z": ["d"],
                         "zh": ["d", "g"]
                        }

def word_to_word_array(word, consonants, vowels, cleanup_shifts):
  word_array = []
  letter_index = 0
  length = len(word)
  while (letter_index < len(word)):
    while letter_index+length-1 < len(word):
      cluster = word[letter_index:letter_index+length].lower()
      if cluster in cleanup_shifts.keys():
        word_array.append(cleanup_shifts[cluster])
        letter_index += length
        length = len(word)
      elif cluster in consonants+vowels:
        word_array.append(cluster)
        letter_index += length
        length = len(word)
      elif length == 1:
        word_array.append(cluster)
        letter_index += length
        length = len(word)
      else:
        length -= 1
    length -= 1
  return word_array

def generate_consonant_array(consonants, num_consonants):
  """ Returns a length-3 array of consonant strings. """
  consonant_array = []
  for n in range(num_consonants):
    consonant_array.append(random.choice(consonants))
  return consonant_array

def generate_vowel_patterns(vowels, min_v, max_v):
  num_v = random.randint(min_v, max_v)
  patterns = []
  for v_1 in vowels + [""]:
    for v_2 in vowels + [""]:
      for v_3 in vowels + [""]:
        for v_4 in vowels + [""]:
          num_vowels = 4
          pattern = [v_1, "C", v_2, "C", v_3, "C", v_4]
          for letter in pattern:
            if letter == "":
              pattern.remove(letter)
              num_vowels -= 1
          if (num_vowels == num_v):
            patterns.append(pattern)
  return patterns

def add_vowels(consonant_array, vowel_pattern):
  consonant_index = 0
  word = vowel_pattern[:]
  for pattern_index in range(len(vowel_pattern)):
    if word[pattern_index] == "C":
      word[pattern_index] = consonant_array[consonant_index]
      consonant_index += 1
  return word
  
def check_word_array(word_array, consonants):
  word = string.join(word_array, "")
  if word_array[0] in consonants:
    if word_array[1] in consonants:
      if word_array[2] in consonants:
        if word_array[2] not in next_consonants_initial[word_array[1]]:
          #print word, "bad initial cluster [experimental]"
          return False
        elif word_array[1] not in next_consonants_final[word_array[0]]:
          #print word, "bad initial triphthong [experimental]"
          return False
      if word_array[1] not in next_consonants_initial[word_array[0]]:
        #print word, "bad initial cluster"
        return False

  if word_array[-1] in consonants:
    if word_array[-2] in consonants and word_array[-1] not in next_consonants_final[word_array[-2]]:
      #print word, "bad final cluster"
      return False
  for i in range(len(word_array)-2): #max index: len - 1
    if word_array[i] in consonants:
      if word_array[i+1] in consonants and word_array[i+2] in consonants:
        if word_array[i+2] not in next_consonants_initial[word_array[i+1]]:
          cluster = string.join(word_array[i:i+3], "")
          #print word, "bad middle cluster", cluster
          return False
        elif (i+2) == len(word_array)-1 and word_array[i+1] not in next_consonants_initial[word_array[i]]:
          cluster = string.join(word_array[i:i+3], "")
          #print word, "bad final cluster [experimental]", cluster
          return False
  return True

def generate_word_array(consonants, vowels, vowel_patterns, num_consonants=3):
  valid_vowel_patterns = []
  root = generate_consonant_array(consonants, num_consonants)
  for vp in vowel_patterns:
    word_array = add_vowels(root, vp)
    if check_word_array(word_array, consonants):
      valid_vowel_patterns.append(vp)
  if len(valid_vowel_patterns) > 0:
    vowel_pattern = random.choice(valid_vowel_patterns)
    word_array = add_vowels(root, vowel_pattern)
    return word_array
  else:
    return generate_word_array(consonants, vowels, vowel_patterns) #zomg recursion

def generate_word(consonants, vowels, vowel_patterns):
  # Basically just a helper function for generate_word_array
  word_array = generate_word_array(consonants, vowels, vowel_patterns)
  word = string.join(word_array, "")
  return word.title()
  
def generate_name_with_suffix(consonants, vowels, suffixes, min_root_length=1, max_root_length=2):
  """ AKA Triconsonant + Suffix """
  vowel_patterns = generate_vowel_patterns(vowels, min_root_length, max_root_length)
  word_array = generate_word_array(consonants, vowels, vowel_patterns)
  suffix = random.choice(suffixes)
  suffix_array = word_to_word_array(suffix, consonants, vowels, cleanup_shifts)
  
  word = string.join(word_array, "").title()
  """  
  if word_array[-1] in vowels and suffix_array[0] in vowels:
    word += "'"
  elif word_array[-1] in consonants and suffix_array[0] in consonants:
    word += "'"
  """    
  word += string.join(suffix_array, "").lower()
  return word

def generate_name_with_prefix(consonants, vowels, prefixes, min_root_length=1, max_root_length=2):
  """ AKA Prefix + Triconsonant """
  vowel_patterns = generate_vowel_patterns(vowels, min_root_length, max_root_length)
  word_array = generate_word_array(consonants, vowels, vowel_patterns)
  prefix = random.choice(prefixes)
  prefix_array = word_to_word_array(prefix, consonants, vowels, cleanup_shifts)
  
  word = string.join(prefix_array, "").title()
  """
  if prefix_array[-1] in vowels and word_array[0] in vowels:
    word += "'"
  elif prefix_array[-1] in consonants and word_array[0] in consonants:
    word += "'"
  """
  word += string.join(word_array, "").lower()
  return word
  
def prefix_plus_suffix(consonants, vowels, prefixes, suffixes, min_root_length=1, max_root_length=2):
  prefix = random.choice(prefixes)
  prefix_array = word_to_word_array(prefix, consonants, vowels, cleanup_shifts)
  suffix = random.choice(suffixes)
  suffix_array = word_to_word_array(suffix, consonants, vowels, cleanup_shifts)

  word = string.join(prefix_array, "").title()
  """  
  if prefix_array[-1] in vowels and suffix_array[0] in vowels:
    word += "'"
  elif prefix_array[-1] in consonants and suffix_array[0] in consonants:
    word += "'"
  """    
  word += string.join(suffix_array, "").lower()
  return word
  
def shift(word, shifts, consonants, vowels, cleanup_shifts):
  word_array = word_to_word_array(word, consonants, vowels, cleanup_shifts)
  shifted_word = ""
  for char in word_array:
    if char in (consonants+vowels):
      shifted_word += shifts[char]
    else:
      shifted_word += char
  if word == word.title():
    shifted_word = shifted_word.title()
  return shifted_word
  
class Dialect:
  def __init__(self, name, consonants, vowels,
               male_first_name_suffixes, female_first_name_suffixes,
               male_last_name_suffixes, female_last_name_suffixes,
               prefixes=None):
    self.name = name
    self.consonants = consonants
    self.vowels = vowels
    self.male_first_name_suffixes = male_first_name_suffixes
    self.female_first_name_suffixes = female_first_name_suffixes
    self.male_last_name_suffixes = male_last_name_suffixes
    self.female_last_name_suffixes = female_last_name_suffixes
    self.prefixes = prefixes

#fine to use these in game now
female_name_suffixes = ["ea", "ia", "isa", "ana", "iana", "ela", "ika", "ina"]
last_name_suffixes = ["az", "ak", "ar", "ach", "an", "ev", "og", "ot", "op", "iz", "it", "im", "ask"]
vowel_patterns = generate_vowel_patterns(vowels, 1, 2)

dialects = []

turkish_consonants = consonants[:]
turkish_consonants.remove("th")
turkish_consonants.remove("w")
turkish_male_first_name_suffixes = ["un", "ur", "er", "an", "met", "bey"]
turkish_female_first_name_suffixes = ["ik", "e", "a", "iye", "ya"]
turkish_male_last_name_suffixes = ["ik", "lik", "uk", "ug", "ar", "er", "an", "en", "op"]
turkish_female_last_name_suffixes = ["ik", "lik", "uk", "ug", "ar", "er", "an", "en", "op"]

dialects.append(
  Dialect("Turkish", turkish_consonants, vowels,
          turkish_male_first_name_suffixes, turkish_female_first_name_suffixes,
          turkish_male_last_name_suffixes, turkish_female_last_name_suffixes))
          
persian_consonants = consonants[:]
for c in ["th", "w"]:
  persian_consonants.remove(c)
persian_male_first_name_suffixes = ["an", "ad", "ang", "osh", "am"]
persian_female_first_name_suffixes = ["eh", "dokht", "a"]
persian_male_last_name_suffixes = ["avi", "ami", "ari", "uri", "ubi", "azi", "ali", "ani", "i", "ati", "pur", "var"]
persian_female_last_name_suffixes = ["avi", "ami", "ari", "uri", "ubi", "azi", "ali", "ani", "i", "ati", "pur", "var"]

dialects.append(
  Dialect("Persian", persian_consonants, vowels,
          persian_male_first_name_suffixes, persian_female_first_name_suffixes,
          persian_male_last_name_suffixes, persian_female_last_name_suffixes))
          
sanskrit_consonants = consonants[:]
sanskrit_consonants.remove("th")
sanskrit_male_first_name_suffixes = ["shak", "daman", "sena", "arman", "datta", "putra", "ishka", "arha", "varma", "an", "darsh"]
sanskrit_female_first_name_suffixes = ["sha", "ika", "i", "ini", "ya", "ita", "ashi", "a", "isha", "aka", "la", "na"]
sanskrit_male_last_name_suffixes = ["ak", "ar", "kar", "an", "ni", "ama", "anda", "al"]
sanskrit_female_last_name_suffixes = ["ak", "ar", "kar", "an", "ni", "ama", "anda", "al"]

dialects.append(
  Dialect("Sanskrit", sanskrit_consonants, vowels,
          sanskrit_male_first_name_suffixes, sanskrit_female_first_name_suffixes,
          sanskrit_male_last_name_suffixes, sanskrit_female_last_name_suffixes))
          
armenian_consonants = consonants[:]
armenian_consonants.remove("w")
armenian_male_first_name_suffixes = ["an", "en", "ak", "ur"]
armenian_female_first_name_suffixes = ["ush", "a", "e", "ik", "i"]
armenian_male_last_name_suffixes = ["ian", "tsi"]
armenian_female_last_name_suffixes = ["ian", "tsi"]

dialects.append(
  Dialect("Armenian", armenian_consonants, vowels,
          armenian_male_first_name_suffixes, armenian_female_first_name_suffixes,
          armenian_male_last_name_suffixes, armenian_female_last_name_suffixes))
          
greek_consonants = consonants[:]
for c in ["sh", "ch", "zh", "w", "j", "h"]:
  greek_consonants.remove(c)
greek_male_first_name_suffixes = ["os", "on", "as", "es", "agoras", "filos", "dorus", "dotus", "fanes", "poulos", "krates", "mander", "andros", "idas", "ros", "foros"]
greek_female_first_name_suffixes = ["e", "ia", "ea", "dora", "fila"]
greek_male_last_name_suffixes = ["os", "is", "es", "cles", "arkhos", "critus", "ides", "iades", "medes", "stratos", "urgos", "menes"]
greek_female_last_name_suffixes = ["os", "is", "es"]
greek_prefixes = ["anax", "andro", "apollo", "demo", "dio", "epi", "fil", "hero", "hippo", "niko", "poly", "themisto", "theo", "kseno", "lyc"]

dialects.append(
  Dialect("Greek", greek_consonants, vowels,
          greek_male_first_name_suffixes, greek_female_first_name_suffixes,
          greek_male_last_name_suffixes, greek_female_last_name_suffixes,
          greek_prefixes))
          
slavic_consonants = consonants[:]
for c in ["th", "w", "f", "h", "j"]:
  slavic_consonants.remove(c)
slavic_male_first_name_suffixes = ["an", "dan", "drag", "lyub", "ko", "mil", "mir", "rad", "slav", "van"]
slavic_female_first_name_suffixes = ["ya", "a", "ka", "ila", "ina"]
slavic_male_last_name_suffixes = ["ich", "in", "ov", "ev", "ets", "ats", "ek", "ak"]
slavic_female_last_name_suffixes = ["ich", "in", "ova", "eva", "etsa", "ats", "ek", "ak"]
slavic_prefixes = ["bog", "bol", "boy", "drag", "lyub", "mil", "mir", "myech", "rad", "slav", "svyat", "tikh", "trp", "tvrt", "vlad", 
"vyach", "vyel", "yar"]

dialects.append(
  Dialect("Slavic", slavic_consonants, vowels,
          slavic_male_first_name_suffixes, slavic_female_first_name_suffixes,
          slavic_male_last_name_suffixes, slavic_female_last_name_suffixes,
          slavic_prefixes))

latvian_consonants = consonants[:]
for c in ["th", "w"]:
  latvian_consonants.remove(c)
latvian_male_first_name_suffixes = ["s", "is"]
latvian_female_first_name_suffixes = ["ia", "na", "ita", "a"]
latvian_male_last_name_suffixes = ["is", "avs", "aks", "ins"]
latvian_female_last_name_suffixes = ["is", "avs", "aks", "ins"]

dialects.append(
  Dialect("Latvian", latvian_consonants, vowels,
          latvian_male_first_name_suffixes, latvian_female_first_name_suffixes,
          latvian_male_last_name_suffixes, latvian_female_last_name_suffixes))

ossetian_consonants = consonants[:]
for c in ["th", "w"]:
  ossetian_consonants.remove(c)
ossetian_male_first_name_suffixes = ["an", "bek", "o", "az", "ag"]
ossetian_female_first_name_suffixes = ["a", "ika"]
ossetian_male_last_name_suffixes = ["ay", "ty", "oity", "uty", "aty"]
ossetian_female_last_name_suffixes = ["ay", "ty", "oity", "uty", "aty"]

dialects.append(
  Dialect("Ossetian", ossetian_consonants, vowels,
          ossetian_male_first_name_suffixes, ossetian_female_first_name_suffixes,
          ossetian_male_last_name_suffixes, ossetian_female_last_name_suffixes))
          
indo_scythian_consonants = consonants[:]
for c in ["th", "w"]:
  indo_scythian_consonants.remove(c)
indo_scythian_male_first_name_suffixes = ["asa", "asha", "ika", "aka"]
indo_scythian_female_first_name_suffixes = ["ana"]
indo_scythian_male_last_name_suffixes = ["aka", "asa"]
indo_scythian_female_last_name_suffixes = ["asa", "aka"]

dialects.append(
  Dialect("Indo-Scythian", indo_scythian_consonants, vowels,
          indo_scythian_male_first_name_suffixes, indo_scythian_female_first_name_suffixes,
          indo_scythian_male_last_name_suffixes, indo_scythian_female_last_name_suffixes))

georgian_consonants = consonants[:]
for c in ["th", "w", "j", "y", "h"]:
  georgian_consonants.remove(c)
georgian_male_first_name_suffixes = ["o", "az", "ab", "ad", "im", "i", "ar"]
georgian_female_first_name_suffixes = ["ea", "ko", "a"]
georgian_male_last_name_suffixes = ["adze", "idze", "ashvili", "eli", "vari", "ava", "ia"]
georgian_female_last_name_suffixes = ["adze", "idze", "ashvili", "eli", "vari", "ava", "ia"]

dialects.append(
  Dialect("Georgian", georgian_consonants, vowels,
          georgian_male_first_name_suffixes, georgian_female_first_name_suffixes,
          georgian_male_last_name_suffixes, georgian_female_last_name_suffixes))

hungarian_consonants = consonants[:]
for c in ["w"]:
  hungarian_consonants.remove(c)
hungarian_male_first_name_suffixes = ["os", "ar", "or", "an"]
hungarian_female_first_name_suffixes = ["a"]
hungarian_male_last_name_suffixes = ["y", "asi", "osi", "or", "os"]
hungarian_female_last_name_suffixes = ["y", "asi", "osi", "or", "os"]

dialects.append(
  Dialect("Hungarian", hungarian_consonants, vowels,
          hungarian_male_first_name_suffixes, hungarian_female_first_name_suffixes,
          hungarian_male_last_name_suffixes, hungarian_female_last_name_suffixes))

albanian_consonants = consonants[:]
for c in ["w"]:
  albanian_consonants.remove(c)
albanian_male_first_name_suffixes = ["id", "im", "an"]
albanian_female_first_name_suffixes = ["a", "ia", "ie"]
albanian_male_last_name_suffixes = ["na", "ra", "oni", "ani", "asi", "oti", "ari", "ini"]
albanian_female_last_name_suffixes = ["na", "ra", "oni", "ani", "asi", "oti", "ari", "ini"]

dialects.append(
  Dialect("Albanian", albanian_consonants, vowels,
          albanian_male_first_name_suffixes, albanian_female_first_name_suffixes,
          albanian_male_last_name_suffixes, albanian_female_last_name_suffixes))

anglo_saxon_consonants = consonants[:]
for c in ["zh", "v", "kh"]:
  anglo_saxon_consonants.remove(c)
  
anglo_saxon_male_first_name_suffixes = ["bald","bert","frith","gar", "hard","helm","mund","red","ric","ulf","wald","ward","win","wulf"]
anglo_saxon_female_first_name_suffixes = ["a", "burga", "dred", "win"]
anglo_saxon_male_last_name_suffixes = ["bald","bert","frith","gar","hard","helm","mund","red","ric","ulf","wald","ward","win","wulf"]
anglo_saxon_female_last_name_suffixes = ["bald","bert","frith","gar","hard","helm","mund","red","ric","ulf","wald","ward","win","wulf"]
anglo_saxon_prefixes = ["al","ald","alf","athel","cuth","ed","eg","egel","eo","ethel","her","mild","os","ric","rod","saks", "sig", "wig"]
dialects.append(
  Dialect("Anglo-Saxon", anglo_saxon_consonants, vowels,
          anglo_saxon_male_first_name_suffixes, anglo_saxon_female_first_name_suffixes,
          anglo_saxon_male_last_name_suffixes, anglo_saxon_female_last_name_suffixes,
          anglo_saxon_prefixes))
          
romanian_male_first_name_suffixes = ["u", "in", "an", "iu"]
romanian_female_first_name_suffixes = ["a", "ina"]
romanian_male_last_name_suffixes = ["escu", "esco", "asco", "eanu", "iciu", "u", "iu"]
romanian_female_last_name_suffixes = ["escu", "esco", "asco", "eanu", "iciu", "u", "iu"]
dialects.append(
  Dialect("Romanian", consonants, vowels,
          romanian_male_first_name_suffixes, romanian_female_first_name_suffixes,
          romanian_male_last_name_suffixes, romanian_female_last_name_suffixes))

dialects = sorted(dialects, None, lambda d: d.name)

profanity_male_first_name_suffixes = ["fart", "dam", "dik", "hole", "me", "fuk", "shit", "ass", "piss"]
profanity_female_first_name_suffixes = ["fart", "dam", "bich", "kunt", "hole", "me", "fuk", "shit", "ass", "piss"]
profanity_male_last_name_suffixes = ["fart", "dam", "dik", "hole", "fuk", "shit", "ass", "piss"]
profanity_female_last_name_suffixes = ["fart", "dam", "bich", "hole", "fuk", "shit", "ass", "piss"]
profanity_prefixes = ["fart", "fuk", "dam", "dik", "shit", "ass", "piss"]

dialects.append(
  Dialect("Profanity", consonants, vowels,
          profanity_male_first_name_suffixes, profanity_female_first_name_suffixes,
          profanity_male_last_name_suffixes, profanity_female_last_name_suffixes,
          profanity_prefixes))

dialects = sorted(dialects, None, lambda d: d.name)


### Debug/test output ###
"""
print " ==============================================="
print " * * * * * * * * * * NEW SET * * * * * * * * * *"
print " ==============================================="
for dialect in dialects:
  shifts = {}
  for key in possible_shifts.keys():
    shifts[key] = random.choice(possible_shifts[key])
  for gender in ["Female", "Male"]:
    if gender == 'Female':
      first_name_suffixes = dialect.female_first_name_suffixes
      last_name_suffixes = dialect.female_last_name_suffixes
    else:
      first_name_suffixes = dialect.male_first_name_suffixes
      last_name_suffixes = dialect.male_last_name_suffixes
    if dialect.prefixes:
      if dialect.name in ["Slavic", "Greek"] and gender == "Female":
        r = random.randint(1,2)
        if r == 1:
          first_name = generate_name_with_suffix(dialect.consonants, dialect.vowels, first_name_suffixes)        
        elif r == 2:
          first_name = prefix_plus_suffix(dialect.consonants, dialect.vowels, dialect.prefixes, first_name_suffixes)
      else:
        r = random.randint(1,3)
        if r == 1:
          first_name = generate_name_with_suffix(dialect.consonants, dialect.vowels, first_name_suffixes)
        elif r == 2:
          first_name = generate_name_with_prefix(dialect.consonants, dialect.vowels, dialect.prefixes)
        elif r == 3:
          first_name = prefix_plus_suffix(dialect.consonants, dialect.vowels, dialect.prefixes, first_name_suffixes)
    else:
      first_name = generate_name_with_suffix(dialect.consonants, dialect.vowels, first_name_suffixes)
    last_name = generate_name_with_suffix(dialect.consonants, dialect.vowels, last_name_suffixes)
    
    print "(" + dialect.name + " " + gender +") " + first_name + " " + last_name + " => ",    
    shifted_first_name = shift(first_name, shifts, dialect.consonants, dialect.vowels, cleanup_shifts)
    shifted_last_name = shift(last_name, shifts, dialect.consonants, dialect.vowels, cleanup_shifts)
    print shifted_first_name + " " + shifted_last_name
""" 
