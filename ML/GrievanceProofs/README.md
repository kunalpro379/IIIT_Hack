# Civic Grievance Image Analysis System

An AI-powered system for analyzing and documenting civic infrastructure issues through image analysis.

## Features

### 1. Image Analysis Capabilities
- **Multi-Model Architecture**: Utilizes both BLIP and ViT-GPT2 models for comprehensive image analysis
- **Automatic Caption Generation**: Generates detailed captions describing infrastructure issues
- **Severity Assessment**: Automatically categorizes issues into High/Medium/Low severity
- **Infrastructure-Specific Detection**: Specialized detection for:
  - Street lighting issues
  - Road conditions
  - Garbage disposal
  - Manhole/drainage problems

### 2. Smart Severity Analysis
- **Context-Aware Scoring**: Considers multiple factors:
  - Time of day (especially for lighting issues)
  - Location importance (residential/commercial/school zones)
  - Infrastructure type
  - Safety implications
- **Weighted Assessment**: Higher weights for critical infrastructure and safety issues
- **Location-Based Prioritization**: Enhanced severity scores for issues in sensitive areas

### 3. Detailed Reporting
- **Comprehensive Analysis Reports**: Generates:
  - Detailed image descriptions
  - Severity assessments
  - Contributing factors
  - Recommended actions
- **Multiple Output Formats**:
  - CSV reports
  - JSON detailed analyses
  - Summary text reports
  - Category-wise statistics

### 4. Batch Processing
- **Multi-folder Support**: Handles separate train/test image directories
- **Recursive Scanning**: Processes images in nested folders
- **Category Organization**: Automatic categorization based on folder structure
- **Progress Tracking**: Real-time progress bars and logging

### 5. Data Management
- **Organized Storage Structure**:
  - Cached models
  - Analysis results
  - Detailed reports
  - Summary statistics
- **Automatic Directory Management**: Creates required directories if not present


## Output Structure

### 1. Analysis Results
- `results/image_analysis_results.csv`: Main analysis results
- `results/detailed_analyses/`: Individual JSON files for each image
- `results/analysis_summary.txt`: Overall statistics and distribution

### 2. Generated Data
Each image analysis includes:
- Caption
- Severity level
- Detailed description
- Contributing factors
- Timestamp
- Category
- Authentication score

