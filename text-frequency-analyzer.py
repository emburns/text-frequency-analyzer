#!/usr/bin/env python3
"""
Text Frequency Analyzer
Analyzes word frequency in text files and displays results in a clean format.
"""

import argparse
import re
from collections import Counter
from pathlib import Path


def clean_text(text):
    """Remove punctuation and convert to lowercase for consistent analysis."""
    return re.sub(r'[^\w\s]', '', text.lower())


def analyze_text_file(filepath, top_n=10, min_length=3):
    """
    Analyze word frequency in a text file.
    
    Args:
        filepath: Path to the text file
        top_n: Number of top words to return
        min_length: Minimum word length to consider
    
    Returns:
        Counter object with word frequencies
    """
    try:
        content = Path(filepath).read_text(encoding='utf-8')
        cleaned = clean_text(content)
        words = [word for word in cleaned.split() if len(word) >= min_length]
        return Counter(words).most_common(top_n)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []


def display_results(word_freq, total_words):
    """Display frequency analysis results in a formatted table."""
    if not word_freq:
        return
    
    print(f"\nWord Frequency Analysis")
    print(f"Total words analyzed: {total_words}")
    print("-" * 40)
    print(f"{'Word':<15} {'Count':<8} {'Percentage'}")
    print("-" * 40)
    
    for word, count in word_freq:
        percentage = (count / total_words) * 100
        print(f"{word:<15} {count:<8} {percentage:.1f}%")


def main():
    parser = argparse.ArgumentParser(description="Analyze word frequency in text files")
    parser.add_argument("file", help="Path to text file to analyze")
    parser.add_argument("-n", "--top", type=int, default=10, 
                       help="Number of top words to show (default: 10)")
    parser.add_argument("-m", "--min-length", type=int, default=3,
                       help="Minimum word length (default: 3)")
    
    args = parser.parse_args()
    
    # Create sample file if it doesn't exist
    if not Path(args.file).exists():
        sample_text = """
        Python is a high-level programming language. Python emphasizes code readability
        with its notable use of significant whitespace. Python's language constructs and
        object-oriented approach aim to help programmers write clear, logical code for
        small and large-scale projects. Python is dynamically typed and garbage-collected.
        """
        Path(args.file).write_text(sample_text.strip())
        print(f"Created sample file: {args.file}")
    
    word_freq = analyze_text_file(args.file, args.top, args.min_length)
    
    if word_freq:
        total_words = sum(count for _, count in word_freq)
        display_results(word_freq, total_words)


if __name__ == "__main__":
    main()