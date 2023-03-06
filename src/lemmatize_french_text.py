import sys
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from french_lefff_lemmatizer.french_lefff_lemmatizer import FrenchLefffLemmatizer

nltk.download('wordnet')

lemmatizer = FrenchLefffLemmatizer()

if (len(sys.argv) != 3):
    raise ValueError('Mauvaise utilisation du script : python lemmatize_french_text.py input_file output_file')

input_file = sys.argv[1] # fichier d'entrée
output_file = sys.argv[2] # fichier de sortie

def lemmatize_file(input_file, output_file):
    with open(input_file, 'r', encoding="utf-8") as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            tokens = word_tokenize(line) # tokenisation du corpus
            lemmatized_words = [lemmatizer.lemmatize(token) for token in tokens]  # lemmatisation des mots
            lemmatized_line = ' '.join(lemmatized_words)  # Ajout des mots lemmatize 
            f_out.write(lemmatized_line + '\n')  # écriture de la ligne complète lemmatisée dans le fichier de sortie

lemmatize_file(input_file, output_file)