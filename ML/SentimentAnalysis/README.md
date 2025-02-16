# Grievance Analysis System

## Project Overview
This project implements a sophisticated grievance analysis system that processes complaint texts to predict multiple aspects:
- Emotional sentiment detection
- Resolution time estimation
- Urgency level classification

## Features

### 1. Multi-lingual Support
- Handles both English and Hindi text input
- Automatic translation and standardization of emotion labels and urgency levels
- Built-in mappings for Hindi-English emotional terms and urgency indicators

### 2. Sentiment Analysis
- Classifies complaints into various emotional categories:
  - Angry
  - Disappointed
  - Concerned
  - Neutral
  - And other relevant emotional states
- Uses TF-IDF vectorization for text feature extraction
- Implements Random Forest classifier for robust emotion prediction

### 3. Resolution Time Prediction
- Estimates the number of days required to resolve the grievance
- Uses regression modeling to provide numeric predictions
- Takes into account the complexity and nature of the complaint
- Handles missing values through mean imputation

### 4. Urgency Level Classification
- Categorizes complaints into urgency levels:
  - High
  - Medium
  - Low
- Uses machine learning to determine priority based on complaint content
- Helps in efficient resource allocation and complaint handling

### 5. Data Processing Pipeline
- Text cleaning and standardization
- Missing value handling
- Feature extraction using TF-IDF
- Model training and validation
- Performance metrics calculation

## Workflow

1. **Data Preprocessing**
   - Load complaint data from CSV
   - Clean and standardize text data
   - Handle missing values
   - Convert Hindi labels to English
   - Vectorize text using TF-IDF

2. **Model Training**
   - Three separate models are trained:
     - Emotion classifier (Random Forest)
     - Resolution time predictor (Random Forest Regressor)
     - Urgency classifier (Random Forest)
   - Models are saved for future use

3. **Prediction Process**
   - Input text is processed through TF-IDF vectorizer
   - Each model makes its specific prediction
   - Results are combined into a comprehensive analysis
   - Predictions include:
     - Emotional state
     - Expected resolution time
     - Urgency level

4. **Results Analysis**
   - Generates detailed classification reports
   - Provides performance metrics
   - Creates summary statistics
   - Option to save predictions to CSV

