# Unified Grievance Analysis System

## Project Overview
A comprehensive machine learning system for analyzing and processing citizen grievances. The system uses advanced NLP techniques to automatically categorize complaints, assess their impacts (social, economic, environmental), predict resolution times, and assign to relevant departments.

## Core Features

### 1. Multi-Task Prediction System
- **Category Classification**: Automatically identifies the main category of the grievance
- **Impact Assessment**:
  - Economic Impact Analysis
  - Environmental Impact Evaluation
  - Social Impact Measurement
- **Department Assignment**: Automatically suggests the appropriate department
- **Resolution Time Prediction**: Estimates the time required for resolution
- **Priority Scoring**: Calculates complaint priority based on multiple factors

### 2. Advanced NLP Capabilities

#### Text Processing
- Multilingual support using XLM-RoBERTa
- Text augmentation through:
  - Synonym replacement
  - Back translation
  - Semantic similarity-based augmentation

#### Model Architecture
- Base: XLM-RoBERTa-large
- Enhanced with:
  - Multi-head attention layers
  - Task-specific classification heads
  - Intermediate layer normalization
  - Dropout regularization
  - Label smoothing

### 3. Memory Management
- Optimized for GPUs with limited VRAM (6GB)
- Features:
  - Gradient checkpointing
  - Mixed precision training
  - Memory cleanup callbacks
  - Dynamic batch size adjustment
  - Disk space management

### 4. Data Pipeline

#### Input Processing
1. Text Combination: Merges complaint, title, and description
2. Tokenization: Using XLM-RoBERTa tokenizer
3. Augmentation: Applied during training for better generalization
4. Label Encoding: Handles categorical variables

#### Training Flow
1. Data splitting (80/20 train/test)
2. K-fold cross-validation (5 folds)
3. Model ensemble creation
4. Continuous evaluation

### 5. Prediction System

#### Unified Model
- Single model architecture handling multiple prediction tasks
- Ensemble predictions for improved accuracy
- Confidence scoring for predictions

#### Impact Analysis
- Separate specialized models for:
  - Economic impact assessment
  - Environmental impact evaluation
  - Social impact measurement
  - Policy relevance

### 6. Testing Framework
- Comprehensive evaluation metrics
- Cross-validation results
- Confusion matrices
- Performance analytics per category
- Impact assessment accuracy

## Workflow

1. **Data Input**
   - Receives grievance text
   - Processes multiple input fields
   - Handles multilingual content

2. **Processing Pipeline**
   ```
   Input Text → Tokenization → Augmentation → Model Ensemble → Predictions
   ```

3. **Analysis Layers**
   - Primary categorization
   - Impact assessment
   - Department routing
   - Priority calculation
   - Resolution time estimation

4. **Output Generation**
   - Comprehensive grievance analysis
   - Multiple impact scores
   - Department assignments
   - Priority level
   - Estimated resolution timeline

5. **Continuous Learning**
   - Model performance monitoring
   - Periodic retraining
   - Accuracy improvements
   - Error analysis

## Model Performance

### Accuracy Metrics
- Category Classification: ~85-90%
- Department Assignment: ~80-85%
- Impact Assessment: ~75-80%
- Resolution Time: ~70-75% (within acceptable range)

### System Capabilities
- Handles 500+ grievance categories
- Processes multiple regional languages
- Real-time prediction capability
- Scalable to large datasets
