#!/usr/bin/env python3
"""
Unit tests for text frequency analyzer with Pydantic validation.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from pydantic import ValidationError

from text_frequency_analyzer import (
    AnalysisConfig,
    WordFrequency,
    AnalysisResult,
    TextAnalyzer
)

# Set the file that will be used for all the tests
test_file_path = "claude-generated-space-text.txt"


class TestTextAnalyzer:
    """Test cases for TextAnalyzer class."""
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        analyzer = TextAnalyzer()
        
        # Test basic cleaning
        text = "Hello, World! How are you?"
        cleaned = analyzer.clean_text(text)
        assert cleaned == "hello world how are you"
        
        # Test with various punctuation
        text = "Python's great... isn't it? Yes! (definitely)"
        cleaned = analyzer.clean_text(text)
        assert cleaned == "pythons great isnt it yes definitely"
        
        # Test with numbers and mixed case
        text = "Python3 is AWESOME!!!"
        cleaned = analyzer.clean_text(text)
        assert cleaned == "python3 is awesome"
    
    def test_analyze_file_success(self, tmp_path):
        """Test successful file analysis."""
        analyzer = TextAnalyzer()
        test_file = tmp_path / test_file_path
        
        # Create test file with known content
        test_content = "python is great python is fun python programming"
        test_file.write_text(test_content)
        
        config = AnalysisConfig(filepath=test_file, top_n=3, min_length=2)
        result = analyzer.analyze_file(config)
        
        assert result is not None
        assert result.filepath == test_file
        assert result.total_words == 8  # All words >= 2 chars
        assert result.unique_words == 5  # python, is, great, fun, programming
        assert len(result.word_frequencies) == 3  # top_n = 3
        
        # Check that "python" is the most frequent word
        assert result.word_frequencies[0].word == "python"
        assert result.word_frequencies[0].count == 3
    
    def test_analyze_file_with_min_length_filter(self, tmp_path):
        """Test file analysis with minimum length filtering."""
        analyzer = TextAnalyzer()
        test_file = tmp_path / test_file_path
        
        # Content with short and long words
        test_content = "a big python is a great programming language"
        test_file.write_text(test_content)
        
        config = AnalysisConfig(filepath=test_file, min_length=4)
        result = analyzer.analyze_file(config)
        
        assert result is not None
        # Only words >= 4 chars: "python", "great", "programming", "language"
        assert result.total_words == 4
        
        # Ensure short words are filtered out
        word_list = [wf.word for wf in result.word_frequencies]
        assert "a" not in word_list
        assert "big" not in word_list
        assert "is" not in word_list
    
    def test_analyze_file_no_words_matching_criteria(self, tmp_path):
        """Test analysis when no words match the criteria."""
        analyzer = TextAnalyzer()
        test_file = tmp_path / test_file_path
        
        # Content with only short words
        test_content = "a b c is it"
        test_file.write_text(test_content)
        
        config = AnalysisConfig(filepath=test_file, min_length=10)
        
        with patch('builtins.print') as mock_print:
            result = analyzer.analyze_file(config)
        
        assert result is None
        mock_print.assert_called_with("No words found matching the criteria.")
    
    def test_analyze_file_handles_file_read_error(self, tmp_path):
        """Test analysis handles file read errors gracefully."""
        analyzer = TextAnalyzer()
        test_file = tmp_path / test_file_path
        test_file.write_text("test content")
        
        config = AnalysisConfig(filepath=test_file)
        
        # Mock file read to raise an exception
        with patch.object(Path, 'read_text', side_effect=IOError("Read error")):
            with patch('builtins.print') as mock_print:
                result = analyzer.analyze_file(config)
        
        assert result is None
        mock_print.assert_called_with("Error analyzing file: Read error")
    
    def test_display_results(self, capsys):
        """Test results display formatting."""
        analyzer = TextAnalyzer()
        config = AnalysisConfig(filepath=test_file_path)
        
        word_freqs = [
            WordFrequency(word="python", count=5, percentage=50.0),
            WordFrequency(word="programming", count=3, percentage=30.0),
            WordFrequency(word="language", count=2, percentage=20.0)
        ]
        
        result = AnalysisResult(
            filepath=Path(test_file_path),
            total_words=10,
            unique_words=5,
            word_frequencies=word_freqs,
            config=config
        )
        
        analyzer.display_results(result)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check that key information is displayed
        assert test_file_path in output
        assert "Total words analyzed: 10" in output
        assert "Unique words found: 5" in output
        assert "python" in output
        assert "programming" in output
        assert "language" in output
        assert "50.0%" in output


class TestMainFunction:
    """Test cases for the main function."""
    
    @patch('text_frequency_analyzer.TextAnalyzer')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_success_flow(self, mock_args, mock_analyzer_class):
        """Test successful main function execution."""
        from text_frequency_analyzer import main
        
        # Mock command line arguments
        mock_args.return_value.file = test_file_path
        mock_args.return_value.top = 5
        mock_args.return_value.min_length = 2
        
        # Mock analyzer and result
        mock_analyzer = mock_analyzer_class.return_value
        mock_result = AnalysisResult(
            filepath=Path(test_file_path),
            total_words=10,
            unique_words=5,
            word_frequencies=[],
            config=AnalysisConfig(filepath=test_file_path, top_n=5, min_length=2)
        )
        mock_analyzer.analyze_file.return_value = mock_result
        
        with patch('builtins.print'):
            main()
        
        # Verify analyzer was called with correct config
        mock_analyzer.analyze_file.assert_called_once()
        config_arg = mock_analyzer.analyze_file.call_args[0][0]
        assert config_arg.filepath == Path(test_file_path)
        assert config_arg.top_n == 5
        assert config_arg.min_length == 2
        
        # Verify display_results was called
        mock_analyzer.display_results.assert_called_once_with(mock_result)
    
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_validation_error(self, mock_args):
        """Test main function handles validation errors."""
        from text_frequency_analyzer import main
        
        # Mock invalid arguments
        mock_args.return_value.file = test_file_path
        mock_args.return_value.top = 0  # Invalid: should be >= 1
        mock_args.return_value.min_length = 3
        
        with patch('builtins.print') as mock_print:
            main()
        
        # Should print configuration error
        mock_print.assert_called()
        error_call = str(mock_print.call_args_list[-1])
        assert "Configuration error" in error_call


# Pytest fixtures for common test data
@pytest.fixture
def sample_config():
    """Fixture providing a sample AnalysisConfig."""
    return AnalysisConfig(filepath=test_file_path, top_n=5, min_length=3)


@pytest.fixture
def sample_word_frequencies():
    """Fixture providing sample WordFrequency list."""
    return [
        WordFrequency(word="python", count=10, percentage=40.0),
        WordFrequency(word="programming", count=6, percentage=24.0),
        WordFrequency(word="language", count=4, percentage=16.0)
    ]


@pytest.fixture
def sample_analysis_result(sample_config, sample_word_frequencies):
    """Fixture providing a sample AnalysisResult."""
    return AnalysisResult(
        filepath=Path(test_file_path),
        total_words=25,
        unique_words=10,
        word_frequencies=sample_word_frequencies,
        config=sample_config
    )


if __name__ == "__main__":
    pytest.main([__file__])
