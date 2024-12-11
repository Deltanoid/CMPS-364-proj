from jiwer import wer, cer

def calculate_wer(original_text, generated_text):
    # Calculate Word Error Rate (WER) and Character Error Rate (CER) between two texts.

    word_error_rate = wer(original_text, generated_text)
    char_error_rate = cer(original_text, generated_text)
    return (word_error_rate, char_error_rate)

if __name__ == "__main__":
    original = "this is a sample text to evaluate word error rate of this text"
    generated = "this is sample text evaluate the error rate of this text"

    word_error_rate, char_error_rate = calculate_wer(original, generated)

    print("=== Error Rates ===")
    print(f"Word Error Rate (WER): {word_error_rate:.2%}")
    print(f"Character Error Rate (CER): {char_error_rate:.2%}")