def print_test_header():
    print("\n" + "="*80)
    print(" "*30 + "LANGUAGE DETECTION TEST")
    print("="*80)


def print_table_header(languages):
    headers = ["#", "Text"] + [lang.capitalize() for lang in languages] + ["Detected", "Correct"]
    col_widths = [4, 30] + [10] * len(languages) + [10, 8]

    # Top border
    print("+" + "+".join(["-" * w for w in col_widths]) + "+")
    # Header row
    row = "|".join(f"{h:^{w}}" for h, w in zip(headers, col_widths))
    print(f"|{row}|")
    # Separator
    print("+" + "+".join(["=" * w for w in col_widths]) + "+")

    return col_widths

def print_table_row(i, text, distances, detected_lang, expected, languages, col_widths):
    row_data = [str(i), text[:28] + "…" if len(text) > 30 else text]
    for lang in languages:
        row_data.append(distances.get(lang.lower(), "N/A"))
    row_data.append(detected_lang)
    row_data.append("✓" if detected_lang == expected else "✗")

    row = "|".join(f"{val:^{w}}" for val, w in zip(row_data, col_widths))
    print(f"|{row}|")

def print_table_footer(col_widths):
    print("+" + "+".join(["-" * w for w in col_widths]) + "+")

def print_final_summary(total_cases, total_correct):
    print("\n" + "="*80)
    print(" "*30 + "FINAL SUMMARY")
    print("="*80)
    print(f"Total test cases: {total_cases}")
    print(f"Correct detections: {total_correct}")
    print(f"Accuracy: {(total_correct/total_cases)*100:.1f}%")
    print("="*80) 