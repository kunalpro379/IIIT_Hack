# Fake Grievance Detection System

## Overview
An advanced machine learning system designed to detect and verify the authenticity of grievances using multiple detection layers and NLP techniques. The system helps identify AI-generated, fake, or suspicious grievances while maintaining high accuracy for genuine complaints.

## Features

### 1. Multi-Model Detection Approach
- **Toxic Content Detection**: Uses `unitary/toxic-bert` model
- **Hate Speech Detection**: Implements `dehatebert-mono-english` model
- **AI-Generated Text Detection**: Utilizes `roberta-base-openai-detector`
- **Custom Random Forest Classifier**: For pattern and feature-based classification

### 2. Advanced Text Analysis
- Linguistic pattern recognition
- Part-of-speech (POS) tagging
- TF-IDF vectorization
- Suspicious pattern detection
- Text preprocessing and normalization

### 3. Feature Extraction
- Text length analysis
- Word count statistics
- Average word length calculation
- Special character detection
- Numerical content analysis
- POS tag distribution
- Linguistic pattern analysis

### 4. Red Flag Detection
- Repetitive pattern identification
- Excessive punctuation checking
- Suspicious phrase detection
- Combined scoring system

