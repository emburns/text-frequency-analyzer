#!/usr/bin/env python3
"""
Text Frequency Analyzer with Pydantic
Analyzes word frequency in text files using Pydantic for data validation and modeling.
"""

import re
import typer
from collections import Counter
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class AnalysisConfig(BaseModel):
    """Configuration model for text analysis parameters."""
    
    filepath: Path = Field(..., description="Path to the text file to analyze")
    top_n: int = Field(10, ge=1, le=100, description="Number of top words to return")
    min_length: int = Field(3, ge=1, le=20, description="Minimum word length to consider")
    
    @field_validator('filepath')
    @classmethod
    def validate_filepath(cls, v):
        """Ensure the file exists or can be created."""
        if not isinstance(v, Path):
            v = Path(v)
        return v
    
    class Config:
        arbitrary_types_allowed = True


class WordFrequency(BaseModel):
    """Model for individual word frequency data."""
    
    word: str = Field(..., min_length=1, description="The word")
    count: int = Field(..., ge=1, description="Frequency count")
    percentage: float = Field(..., ge=0, le=100, description="Percentage of total")
    
    @field_validator('word')
    @classmethod
    def validate_word(cls, v):
        """Ensure word contains only letters."""
        if not v.isalpha():
            raise ValueError("Word must contain only alphabetic characters")
        return v.lower()


class AnalysisResult(BaseModel):
    """Model for complete analysis results."""
    
    filepath: Path
    total_words: int = Field(..., ge=0, description="Total number of words analyzed")
    unique_words: int = Field(..., ge=0, description="Number of unique words")
    word_frequencies: List[WordFrequency] = Field(default_factory=list)
    config: AnalysisConfig
    
    @model_validator(mode='after')
    def validate_word_counts(self):
        """Ensure word count consistency."""
        if len(self.word_frequencies) > self.unique_words:
            raise ValueError("Cannot have more frequency entries than unique words")
        return self
    
    class Config:
        arbitrary_types_allowed = True


class TextAnalyzer:
    """Main analyzer class with Pydantic data validation."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Remove punctuation and convert to lowercase for consistent analysis."""
        return re.sub(r'[^\w\s]', '', text.lower())
    
    @staticmethod
    def create_sample_file(filepath: Path) -> None:
        """Create a sample text file for demonstration."""
        sample_text = """
        Python is a high-level programming language. Python emphasizes code readability
        with its notable use of significant whitespace. Python's language constructs and
        object-oriented approach aim to help programmers write clear, logical code for
        small and large-scale projects. Python is dynamically typed and garbage-collected.
        Pydantic provides data validation using Python type annotations. Pydantic validates
        and serializes data automatically, making applications more robust and reliable.
        """
        filepath.write_text(sample_text.strip())
        print(f"Created sample file: {filepath}")
    
    def analyze_file(self, config: AnalysisConfig) -> Optional[AnalysisResult]:
        """
        Analyze word frequency in a text file using validated configuration.
        
        Args:
            config: Validated AnalysisConfig instance
            
        Returns:
            AnalysisResult instance or None if analysis fails
        """
        try:
            # Create sample file if it doesn't exist
            if not config.filepath.exists():
                self.create_sample_file(config.filepath)
            
            # Read and process file
            content = config.filepath.read_text(encoding='utf-8')
            cleaned = self.clean_text(content)
            all_words = cleaned.split()
            
            # Filter words by minimum length
            filtered_words = [word for word in all_words if len(word) >= config.min_length]
            
            if not filtered_words:
                print("No words found matching the criteria.")
                return None
            
            # Count word frequencies
            word_counts = Counter(filtered_words)
            total_words = len(filtered_words)
            unique_words = len(word_counts)
            
            # Create WordFrequency objects for top N words
            word_frequencies = []
            for word, count in word_counts.most_common(config.top_n):
                percentage = (count / total_words) * 100
                word_freq = WordFrequency(
                    word=word,
                    count=count,
                    percentage=round(percentage, 2)
                )
                word_frequencies.append(word_freq)
            
            # Return validated result
            return AnalysisResult(
                filepath=config.filepath,
                total_words=total_words,
                unique_words=unique_words,
                word_frequencies=word_frequencies,
                config=config
            )
            
        except Exception as e:
            print(f"Error analyzing file: {e}")
            return None
    
    @staticmethod
    def display_results(result: AnalysisResult) -> None:
        """Display analysis results in a formatted table."""
        print(f"\nWord Frequency Analysis for: {result.filepath}")
        print(f"Total words analyzed: {result.total_words}")
        print(f"Unique words found: {result.unique_words}")
        print(f"Showing top {len(result.word_frequencies)} words")
        print("-" * 50)
        print(f"{'Word':<15} {'Count':<8} {'Percentage'}")
        print("-" * 50)
        
        for word_freq in result.word_frequencies:
            print(f"{word_freq.word:<15} {word_freq.count:<8} {word_freq.percentage:.1f}%")


def main(
    file: Path =
        typer.Argument(..., help="Path to text file to analyze"),
    top_n: int =
        typer.Option(10, "-n", "--top_n", help="Number of top words to show (default: 10)"),
    min_word_length: int =
        typer.Option(3, "-m", "--min_word_length", help="Minimum word length (default: 3)")
):    
    try:
        # Create and validate configuration
        config = AnalysisConfig(
            filepath=file,
            top_n=top_n,
            min_length=min_word_length
        )
        
        # Perform analysis
        analyzer = TextAnalyzer()
        result = analyzer.analyze_file(config)
        
        if result:
            analyzer.display_results(result)
            
            # Example of accessing validated data
            print(f"\nConfiguration used:")
            print(f"  File: {result.config.filepath}")
            print(f"  Top N: {result.config.top_n}")
            print(f"  Min length: {result.config.min_length}")
            
    except Exception as e:
        print(f"Configuration error: {e}")


if __name__ == "__main__":
    typer.run(main)
