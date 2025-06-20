#!/bin/bash

pytest tests/test_text_analyzer.py --cov=text_frequency_analyzer --cov-report=term-missing
