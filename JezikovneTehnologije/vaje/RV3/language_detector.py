import re
from collections import Counter
from typing import List, Dict, Tuple
import os
import regex as re

class NGramLanguageDetector:
    def __init__(self, n_range: Tuple[int, int] = (1, 5), top_n: int = 400):
        self.n_range = n_range
        self.top_n = top_n
        self.language_profiles: Dict[str, List[str]] = {}
        
    def _generate_ngrams(self, text: str) -> List[str]:
        # Convert to lowercase and keep all letters, numbers, and apostrophes
        # This regex keeps all Unicode letters (\p{L}), numbers (\p{N}), and apostrophes
        text = re.sub(r"[^\p{L}\p{N}']", ' ', text.lower())
        text = '_' + text + '_'
        
        ngrams = []
        for n in range(self.n_range[0], self.n_range[1] + 1):
            for i in range(len(text) - n + 1):
                ngrams.append(text[i:i+n])
        return ngrams
    
    def train(self, language: str, training_text: str):
        ngrams = self._generate_ngrams(training_text)
        counter = Counter(ngrams)
        top_ngrams = [ngram for ngram, _ in counter.most_common(self.top_n)]
        self.language_profiles[language] = top_ngrams
        
        # Print detailed information about the profile
        print(f"\nProfile for {language}:")
        for i, ngram in enumerate(top_ngrams[:5]):
            print(f"Position {i+1}: {ngram}")
            
        for i in range(4, len(top_ngrams), 5):
            print(f"Position {i+1}: {top_ngrams[i]}")
            
        for i, ngram in enumerate(top_ngrams[-5:]):
            print(f"Position {len(top_ngrams)-4+i}: {ngram}")
        print("-" * 50)
    
    def _calculate_distance(self, doc_profile: List[str], lang_profile: List[str]) -> int:
        distance = 0
        for i, ngram in enumerate(doc_profile):
            try:
                lang_index = lang_profile.index(ngram)
                distance += abs(i - lang_index)
            except ValueError:
                # N-gram not in language profile
                distance += len(lang_profile)
        return distance
    
    def detect_language(self, text: str) -> Tuple[str, Dict[str, int]]:
        ngrams = self._generate_ngrams(text)
        counter = Counter(ngrams)
        doc_profile = [ngram for ngram, _ in counter.most_common(self.top_n)]

        distances = {}
        for language, profile in self.language_profiles.items():
            distance = self._calculate_distance(doc_profile, profile)
            distances[language] = distance
        
        best_language = min(distances.items(), key=lambda x: x[1])[0]
        return best_language, distances

def load_training_data(data_dir: str) -> Dict[str, str]:
    training_data = {}
    for filename in os.listdir(data_dir):
        if filename.endswith('.txt'):
            language = filename.split('.')[0]
            with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                training_data[language] = f.read()
    return training_data

def main():
    detector = NGramLanguageDetector()
    
    training_data = load_training_data('data')
    
    for language, text in training_data.items():
        detector.train(language, text)
        print(f"Trained on {language}")
    
    test_text = "This is a test text in English"
    detected_lang, distances = detector.detect_language(test_text)
    print(f"\nTest text: {test_text}")
    print(f"Detected language: {detected_lang}")
    print("\nDistances to all languages:")
    for lang, dist in sorted(distances.items(), key=lambda x: x[1]):
        print(f"{lang:10} : {dist:8d}")

if __name__ == "__main__":
    main() 