import json
import unicodedata
import Levenshtein

# Read the contents of the file with UTF-8 encoding
with open('AF.txt', 'r', encoding='utf-8') as file:
    contents = file.read()

# Parse the JSON data
arabic_words = json.loads(contents)

# Normalize function to remove diacritics
def normalize_text(text):
    text = unicodedata.normalize('NFD', text)
    text = ''.join([c for c in text if unicodedata.category(c) != 'Mn'])
    return text

# Jaccard similarity function
def jaccard_similarity(str1, str2):
    a = set(str1)
    b = set(str2)
    intersection = len(a.intersection(b))
    union = len(a.union(b))
    return intersection / union

# Function to find the closest word
def find_closest_word(user_input, words):
    user_input = normalize_text(user_input)
    closest_word = None
    best_score = float('inf')

    for word, translation in words.items():
        normalized_word = normalize_text(word)
        levenshtein_distance = Levenshtein.distance(user_input, normalized_word)
        jaccard_sim = jaccard_similarity(user_input, normalized_word)

        # Weighted average: you can adjust the weights as needed
        score = levenshtein_distance * 0.5 + (1 - jaccard_sim) * 0.5

        if score < best_score:
            best_score = score
            closest_word = (word, translation)

    return closest_word

# Additional normalization functions provided by the user
phonetic_doublelettre = {'ch': 'ش', 'sh': 'ش', 'dh': 'ض', 'ou': 'و'}

def normalize1_text(text):
    """
    Normalise le texte en remplaçant certains chiffres par des caractères arabes phonétiques.
    """
    for num, char in phonetic_doublelettre.items():
        text = text.replace(num, char)
    return text.lower()

phonetic_numbers = {'3': 'ع', '5': 'خ', '9': 'ق', '7': 'ح', 'a': 'ا', 'i': 'ي', 'b': 'ب', 'c': 'س', 'd': 'د',
                    'f': 'ف', 'j': 'ج', 'k': 'ك', 'l': 'ل', 'm': 'م', 'n': 'ن', 'r': 'ر', 's': 'س', 't': 'ت',
                    'w': 'و', 'y': 'ي', 'z': 'ز', 'h': 'ه', 'g': 'غ', 'p': 'ب', 'q': 'ك', 'v': 'ف', 'u': 'و', 'o': '', 'e': '', 'é': 'ي', 'è': 'ي', 'ê': 'ي', 'à': 'ا', 'â': 'ا', 'û': 'و', 'ù': 'و', 'ü': 'و'}

def normalize2_text(text):
    """
    Normalizes the text by replacing certain phonetic numbers with Arabic characters.
    """
    for num, char in phonetic_numbers.items():
        if not num.isdigit():
            text = text.replace(num, char)
    return text.lower()

ar9am = {'3': 'ع', '5': 'خ', '9': 'ق', '7': 'ح'}

def normalize3_text(text):
    """
    Normalizes the text by replacing numbers with Arabic characters if they are near an Arabic character.
    """
    normalized_text = ""
    is_arabic = False

    for i, char in enumerate(text):
        if char.isdigit():
            if i > 0 and text[i - 1].isalpha():
                normalized_text += ar9am.get(char, char)
            elif i < len(text) - 1 and text[i + 1].isalpha():
                normalized_text += ar9am.get(char, char)
            else:
                normalized_text += char
        else:
            normalized_text += char
        if char.isalpha():
            is_arabic = True
        else:
            is_arabic = False

    return normalized_text.lower()

def preproc_txt(text):
    text = normalize1_text(text)
    text = normalize3_text(text)
    text = normalize2_text(text)
    return text

# Example usage of text preprocessing
example_text = "Ena louay 59 ans nhb 3la 9aredh saken bech n3ares ne5dem mais lproblem mazelt mtrasmtch kifh 9oulouli"
print(preproc_txt(example_text))

# Example usage for finding the closest word
user_input = input("Please enter a word in Tunisian Arabic: ")
processed_input = preproc_txt(user_input)
closest_word = find_closest_word(processed_input, arabic_words)

if closest_word:
    print(f"The closest word to '{user_input}' is '{closest_word[0]}' which means '{closest_word[1]}' in French.")
else:
    print(f"No close match found for '{user_input}'.")
 
 
 