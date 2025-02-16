# Grievance Analysis and Summarization System

A comprehensive system for analyzing and summarizing public grievances using advanced NLP techniques.

## Project Overview

This system processes grievance data to provide meaningful insights and summaries across different categories like Infrastructure, Healthcare, Education, etc. It uses multiple summarization approaches to handle both English and multilingual content.

## Core Components

### 1. Simple Grievance Analyzer (`simple_analyzer.py`)
- Basic analysis of grievances using BART-CNN model
- Sample-based analysis (first 20 grievances)
- Generates category-wise metrics:
  - Total grievances
  - Average resolution time
  - Common emotions
  - District-wise distribution
  - Status breakdown

### 2. Multilingual Grievance Analyzer (`multilingual_summarizer.py`)
- Handles mixed language content (Hindi/English)
- Uses mBART for better multilingual support
- Features:
  - Cross-lingual summarization
  - Category-wise analysis
  - Impact assessment (Economic, Social, Environmental)
  - Emotion analysis

### 3. Category-specific Analysis (`category_summarizer.py`)
- Dedicated analysis for each grievance category
- Generates:
  - Category summaries
  - Statistical metrics
  - Status distribution
  - Emotion patterns
  - Resolution timelines

### 4. Sample Analysis System (`analyze_sample.py`)
- Focused analysis of sample grievances
- Provides:
  - Detailed grievance summaries
  - Category-wise breakdowns
  - Impact assessments
  - District-level insights

### 5. Comprehensive Analysis (`analyze_grievances.py`)
- Complete dataset analysis
- Features:
  - Visual analytics
  - Category distribution plots
  - Detailed metrics
  - Multi-dimensional analysis of impacts

## Workflow

1. **Data Processing**
   - Load grievance data from CSV
   - Preprocess and clean data
   - Categorize grievances

2. **Basic Analysis**
   - Generate category-wise statistics
   - Calculate resolution metrics
   - Analyze emotion patterns
   - Map geographic distribution

3. **Advanced Analysis**
   - Generate summaries using BART/mBART
   - Analyze impacts (Economic/Social/Environmental)
   - Track resolution patterns
   - Identify common issues

4. **Report Generation**
   - Create detailed category reports
   - Generate sample analysis
   - Produce visualizations
   - Compile comprehensive summaries

## Key Features

### Summarization
- Multi-model approach (BART, mBART)
- Context-aware summaries
- Category-specific insights
- Multilingual support

### Analytics
- Category distribution analysis
- Resolution time tracking
- Impact assessment
- Emotion pattern recognition
- Geographic distribution mapping

### Reporting
- Detailed category reports
- Sample analysis reports
- Visual representations
- Comprehensive metrics

### Monitoring
- Resolution status tracking
- Impact assessment
- Urgency level analysis
- District-wise monitoring

### Impact Analysis
- Economic impact assessment
- Social impact evaluation
- Environmental impact tracking
- Multi-dimensional impact metrics

The system provides a comprehensive solution for understanding and analyzing grievances, helping identify patterns, track resolutions, and generate meaningful insights for better governance and decision-making.
