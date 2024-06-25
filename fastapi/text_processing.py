import unicodedata
import json
import Levenshtein
import re

final_op = ""
final_arb = ""
final_arbz = ""
final_price = "1000"

# List of Arabic stop words
arabic_stop_words = {
    'في', 'من', 'على', 'و', 'ب', 'إلى', 'عن', 'أن', 'إن', 'كان', 'ما', 'هذه', 'هذا', 'ذلك', 'كل', 'أي', 'أو', 'لكن', 'كما', 'لقد', 'الذي', 'التي', 'اللذان', 'اللتان', 'الذين', 'اللواتي', 'اللاتي', 'الذي', 'الذين', 'اللذان', 'اللتان','نحب','دينار','DT','dt'
}

# Function to remove diacritics from Arabic text
def remove_diacritics(text):
    arabic_diacritics = re.compile(r'[\u0617-\u061A\u064B-\u0652]')
    return re.sub(arabic_diacritics, '', text)

# Function to remove Arabic stop words
def remove_stop_words(text):
    words = text.split()
    filtered_words = [word for word in words if word not in arabic_stop_words]
    return ' '.join(filtered_words)

# Function to normalize text by removing diacritics
def normalize_text(text):
    text = unicodedata.normalize('NFD', text)
    text = ''.join([c for c in text if unicodedata.category(c) != 'Mn'])
    return text

# Define normalization functions
phonetic_doublelettre = {'ch': 'ش', 'sh': 'ش', 'dh': 'ض', 'ou': 'و'}
phonetic_numbers = {'3': 'ع', '5': 'خ', '9': 'ق', '7': 'ح', 'a': 'ا', 'i': 'ي', 'b': 'ب', 'c': 'س', 'd': 'د',
                    'f': 'ف', 'j': 'ج', 'k': 'ك', 'l': 'ل', 'm': 'م', 'n': 'ن', 'r': 'ر', 's': 'س', 't': 'ت',
                    'w': 'و', 'y': 'ي', 'z': 'ز', 'h': 'ه', 'g': 'غ', 'p': 'ب', 'q': 'ك', 'v': 'ف', 'u': 'و',
                    'o': '', 'e': '', 'é': 'ي', 'è': 'ي', 'ê': 'ي', 'à': 'ا', 'â': 'ا', 'û': 'و', 'ù': 'و', 'ü': 'و'}
ar9am = {'3': 'ع', '5': 'خ', '9': 'ق', '7': 'ح'}

def normalize1_text(text):
    for num, char in phonetic_doublelettre.items():
        text = text.replace(num, char)
    return text.lower()

def normalize2_text(text):
    for num, char in phonetic_numbers.items():
        if not num.isdigit():
            text = text.replace(num, char)
    return text.lower()

def normalize3_text(text):
    normalized_text = ""
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
    return normalized_text.lower()

def preproc_txt(text):
    text = normalize1_text(text)
    text = normalize3_text(text)
    text = normalize2_text(text)
    text = remove_stop_words(text)
    return text

# Load the Arabic words from the JSON file into a list
with open('AF.txt', 'r', encoding='utf-8') as file:
    arabic_words_dict = json.load(file)
    arabic_words_list = list(arabic_words_dict.keys())

# List of phrases related to price comparisons in Tunisian Arabic
price_comparison_phrases = ["ارخص", "اقل", "يفوتش", "ar5es", "a9al", "سومو"]

# Function to calculate the similarity ratio using Levenshtein distance
def calculate_similarity_score(request, keyword):
    levenshtein_distance = Levenshtein.distance(request, keyword)
    max_length = max(len(request), len(keyword))
    similarity = 1 - levenshtein_distance / max_length
    return similarity

# Function to check if the word matches any price comparison phrases using Levenshtein distance
def check_price_comparison_phrases(word):
    for phrase in price_comparison_phrases:
        similarity = calculate_similarity_score(word, phrase)
        if similarity >= 0.5:
            print(f"Matched phrase '{phrase}' with similarity: {similarity * 100:.2f}%")
            return "LessOperator"
    return None

# Function to process each word individually
def process_word(word):     
    global final_op, final_arb, final_arbz
    # Normalize the Arabizi input to Arabic
    normalized_word = preproc_txt(word)
    
    # Check if the normalized input matches any price comparison phrases
    operator = check_price_comparison_phrases(normalized_word)
    if operator:
        final_op += word + " "
        return operator
    
    # Find the best match for the normalized input
    best_match = None
    best_similarity = 0
    
    for arabic_word in arabic_words_list:
        similarity = calculate_similarity_score(normalized_word, arabic_word)
        if similarity > best_similarity and similarity >= 0.45:
            best_match = arabic_word
            best_similarity = similarity
    
    print(f"Best similarity for '{word}' -> '{normalized_word}': {best_similarity * 100:.2f}%")
    if best_match and best_similarity >= 0.45:
        final_arb += best_match + " "
        return best_match
    else:
        final_arbz += word + " "
        return word

# Function to process user input and return results
def process_user_input(user_input):
    global final_op, final_arb, final_arbz, final_price
    final_op = ""
    final_arb = ""
    final_arbz = ""
    final_price = "1000"
    
    # Preprocess the user input
    user_input = remove_diacritics(user_input)
    user_input = remove_stop_words(user_input)

    words = user_input.split()
    processed_words = []
    price_value = None
    
    for word in words:
        if re.match(r'\d+', word):
            final_price = word
            price_value = word
        else:
            operator = check_price_comparison_phrases(word)
            if operator:
                processed_words.append(operator)
            else:
                processed_words.append(process_word(word))
    
    result = ' '.join(processed_words)
    if price_value:
        result += f" (Price value detected: {price_value})"
    
    return {
        "result": result,
        "final_op": final_op.strip(),
        "final_arb": final_arb.strip(),
        "final_arbz": final_arbz.strip(),
        "final_price": final_price.strip()
    }

# Example usage for testing
if __name__ == "__main__":
    # Simulate user input
    user_input = "chapo sayafi mayfoutech 400 "
    results = process_user_input(user_input)
    print(f"Result: {results['result']}")
    print(f"Operators: {results['final_op']}")
    print(f"Arabic Result: {results['final_arb']}")
    print(f"Arabizi Result: {results['final_arbz']}")
    print(f"Price: {results['final_price']}")
