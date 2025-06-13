from language_detector import NGramLanguageDetector, load_training_data
from test_cases import TEST_CASES
from print_utils import (
    print_test_header,
    print_table_header,
    print_table_row,
    print_table_footer,
    print_final_summary
)

def test_language_detector():
    detector = NGramLanguageDetector()
    
    print_test_header()
    print("\nTraining on languages:")
    print("─" * 80)
    
    training_data = load_training_data('data')
    for language, text in training_data.items():
        detector.train(language, text)
        print(f"✓ {language}")
    
    total_correct = 0
    all_languages = list(training_data.keys())
    col_widths = print_table_header(all_languages)

    for i, (text, expected) in enumerate(TEST_CASES, 1):
        detected_lang, distances = detector.detect_language(text)
        print_table_row(i, text, distances, detected_lang, expected, all_languages, col_widths)
        if detected_lang == expected:
            total_correct += 1

    print_table_footer(col_widths)
    print_final_summary(len(TEST_CASES), total_correct)

if __name__ == "__main__":
    test_language_detector() 