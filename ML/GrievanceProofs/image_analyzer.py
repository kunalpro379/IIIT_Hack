import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import os
from tqdm import tqdm
import pandas as pd
import json

def setup_env():
    """Setup environment variables to use E drive"""
    cache_dir = 'E:/ML/ModelCache'
    os.makedirs(cache_dir, exist_ok=True)
    
    # Set all possible cache/storage variables to E drive
    os.environ['TRANSFORMERS_CACHE'] = cache_dir
    os.environ['HF_HOME'] = cache_dir
    os.environ['TORCH_HOME'] = os.path.join(cache_dir, 'torch')
    os.environ['XDG_CACHE_HOME'] = cache_dir
    os.environ['HF_DATASETS_CACHE'] = os.path.join(cache_dir, 'datasets')
    
    return cache_dir

def ensure_directories():
    """Ensure all required directories exist"""
    dirs = {
        'cache': 'E:/ML/ModelCache',
        'saved_models': 'E:/ML/GrievanceProofs/saved_models',
        'results': 'E:/ML/GrievanceProofs/results',
        'train_images': 'E:/ML/GrievanceProofs/Images/Train',
        'test_images': 'E:/ML/GrievanceProofs/Images/Test'
    }
    
    for name, path in dirs.items():
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created directory: {path}")
        else:
            print(f"Directory exists: {path}")
    
    return dirs

class GrievanceImageAnalyzer:
    def __init__(self, model_name="Salesforce/blip-image-captioning-base", cache_dir=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        if cache_dir is None:
            cache_dir = 'E:/ML/ModelCache'
        
        # Load BLIP model and processor
        print("Loading BLIP model and processor...")
        self.processor = BlipProcessor.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            local_files_only=False
        )
        
        self.model = BlipForConditionalGeneration.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            local_files_only=False
        ).to(self.device)
        
        # Save models locally to E drive
        save_dir = 'E:/ML/GrievanceProofs/saved_models'
        os.makedirs(save_dir, exist_ok=True)
        
        print("Saving models locally...")
        self.model.save_pretrained(os.path.join(save_dir, 'blip_model'))
        self.processor.save_pretrained(os.path.join(save_dir, 'blip_processor'))
        
        # Severity keywords and their weights
        self.severity_keywords = {
            'high': [
                'severe', 'dangerous', 'critical', 'hazardous', 'emergency', 'major',
                'dark', 'no light', 'electricity', 'power', 'outage', 'blackout',
                'unsafe', 'night', 'pitch dark', 'unlit'
            ],
            'medium': [
                'moderate', 'concerning', 'notable', 'significant', 'affected',
                'dim', 'poor lighting', 'inadequate', 'insufficient'
            ],
            'low': ['minor', 'small', 'slight', 'minimal', 'limited']
        }
        
        # Add description templates
        self.description_templates = {
            'start': [
                "The image shows",
                "This photograph depicts",
                "In this image, we can observe",
                "The visual evidence presents"
            ],
            'location': [
                "located in",
                "situated at",
                "positioned in",
                "found in"
            ],
            'condition': [
                "The condition appears to be",
                "The state of the area is",
                "The situation can be described as",
                "The overall condition shows"
            ]
        }
        
        # Add infrastructure-specific condition indicators
        self.infrastructure_indicators = {
            'lighting': ['dark', 'night', 'unlit', 'dim', 'no light', 'poor lighting'],
            'electricity': ['power outage', 'no electricity', 'blackout', 'no power'],
            'safety': ['unsafe', 'dangerous', 'hazardous', 'risk']
        }

    def generate_detailed_description(self, caption, severity):
        """Generate a detailed paragraph description from the caption"""
        import random
        
        # Extract key elements
        objects = extract_objects(caption)
        conditions = extract_conditions(caption)
        severity_factors = extract_severity_factors(caption)
        
        # Build detailed description
        description_parts = []
        
        # Start with a random template
        description_parts.append(random.choice(self.description_templates['start']))
        
        # Add main caption with first letter capitalized
        description_parts.append(caption[0].upper() + caption[1:] + ".")
        
        # Add condition details if available
        if conditions:
            description_parts.append(f"{random.choice(self.description_templates['condition'])} {', '.join(conditions)}.")
        
        # Add severity assessment
        severity_description = self.get_severity_description(severity, severity_factors)
        if severity_description:
            description_parts.append(severity_description)
        
        # Add recommendation based on severity
        recommendation = self.get_recommendation(severity, conditions)
        if recommendation:
            description_parts.append(recommendation)
        
        # Detect infrastructure issues
        has_lighting_issue = any(term in caption.lower() for term in self.infrastructure_indicators['lighting'])
        has_electricity_issue = any(term in caption.lower() for term in self.infrastructure_indicators['electricity'])
        
        # Add infrastructure-specific details
        if has_lighting_issue:
            description_parts.append("The area appears to have inadequate lighting, which poses safety concerns for citizens.")
        if has_electricity_issue:
            description_parts.append("Residents are facing electricity supply issues in this area.")
        if 'night' in caption.lower() and severity == 'High':
            description_parts.append("The lack of proper lighting creates unsafe conditions for pedestrians and vehicles.")
        
        # Add severity assessment
        description_parts.append(f"This issue has been assessed as {severity.lower()} severity.")
        
        # Add specific recommendation
        if severity == 'High':
            description_parts.append("Immediate attention required to restore proper lighting and ensure citizen safety.")
        else:
            description_parts.append(self.get_recommendation(severity, []))
        
        # Combine all parts into a paragraph
        return " ".join(description_parts)

    def get_severity_description(self, severity, factors):
        """Generate severity description"""
        if not factors:
            return f"This issue has been assessed as {severity.lower()} severity."
            
        factor_descriptions = []
        for factor in factors:
            for category, items in factor.items():
                factor_descriptions.append(f"{category} concerns ({', '.join(items)})")
        
        return f"This issue has been assessed as {severity.lower()} severity due to {' and '.join(factor_descriptions)}."

    def get_recommendation(self, severity, conditions):
        """Generate recommendation based on severity and conditions"""
        recommendations = {
            'High': "Immediate attention and corrective action is strongly recommended.",
            'Medium': "This issue should be addressed in the near term to prevent potential escalation.",
            'Low': "Monitor the situation and plan for maintenance as needed."
        }
        
        if severity in recommendations:
            return recommendations[severity]
        return ""

    def predict_caption(self, image):
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        
        # Process image
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        
        # Generate caption
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=50,
                num_beams=5,
                min_length=5,
                top_p=0.9,
                repetition_penalty=1.5,
                length_penalty=1.0,
                temperature=1.0
            )
        
        # Decode caption
        caption = self.processor.decode(outputs[0], skip_special_tokens=True)
        return caption

    def analyze_severity(self, caption):
        caption = caption.lower()
        severity_scores = {level: 0 for level in self.severity_keywords}
        
        # Check for night/darkness conditions
        night_indicators = ['night', 'dark', 'unlit']
        has_night_condition = any(indicator in caption for indicator in night_indicators)
        
        # Calculate severity with infrastructure context
        for level, keywords in self.severity_keywords.items():
            for keyword in keywords:
                if keyword in caption:
                    # Increase severity score for infrastructure issues
                    if has_night_condition and any(infra in keyword for infra in ['dark', 'light', 'electricity']):
                        severity_scores[level] += 2  # Double score for lighting issues
                    else:
                        severity_scores[level] += 1
        
        # Determine final severity with infrastructure context
        if has_night_condition and not any(light_term in caption for light_term in ['street light', 'lit']):
            return 'High'  # Dark areas without lighting are high severity
        elif severity_scores['high'] > 0:
            return 'High'
        elif severity_scores['medium'] > 0:
            return 'Medium'
        return 'Low'
    
    def analyze_image(self, image_path):
        """Analyze a single image and return detailed analysis"""
        try:
            # Generate basic caption with more detail
            caption = self.predict_caption(image_path)
            severity = self.analyze_severity(caption)
            
            # Generate detailed description
            detailed_description = self.generate_detailed_description(caption, severity)
            
            return {
                'image_path': image_path,
                'caption': caption,
                'severity': severity,
                'detailed_description': detailed_description,
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"Error analyzing image {image_path}: {str(e)}")
            return None

def save_detailed_analysis(result, output_dir):
    """Save detailed analysis for a single image"""
    if result is None:
        return
        
    image_name = os.path.basename(result['image_path'])
    base_name = os.path.splitext(image_name)[0]
    
    # Create detailed analysis
    analysis = {
        'image_path': result['image_path'],
        'caption': result['caption'],
        'severity': result['severity'],
        'detailed_description': result['detailed_description'],
        'analysis_date': result['analysis_date'],
        'details': {
            'objects_detected': extract_objects(result['caption']),
            'conditions_mentioned': extract_conditions(result['caption']),
            'severity_factors': extract_severity_factors(result['caption'])
        }
    }
    
    # Save as JSON
    json_path = os.path.join(output_dir, f'{base_name}_analysis.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=4, ensure_ascii=False)

def extract_objects(caption):
    """Extract key objects mentioned in caption"""
    # Add NLP processing here if needed
    return [word.strip() for word in caption.lower().split() if len(word) > 3]

def extract_conditions(caption):
    """Extract environmental or condition-related terms"""
    conditions = ['damaged', 'broken', 'dirty', 'clean', 'wet', 'dry', 'dark', 'bright']
    return [word for word in conditions if word in caption.lower()]

def extract_severity_factors(caption):
    """Extract factors contributing to severity"""
    factors = []
    severity_indicators = {
        'safety': ['dangerous', 'hazardous', 'unsafe', 'risk'],
        'urgency': ['immediate', 'urgent', 'critical', 'emergency'],
        'impact': ['affecting', 'impacting', 'damaging', 'harming']
    }
    
    for category, words in severity_indicators.items():
        found = [word for word in words if word in caption.lower()]
        if found:
            factors.append({category: found})
    
    return factors

def get_image_files(folder_path):
    """Recursively get all image files from folder and subfolders"""
    image_files = []
    image_extensions = ('.png', '.jpg', '.jpeg', '.webp')
    
    try:
        print(f"\nScanning directory: {folder_path}")
        # Print absolute path for verification
        abs_path = os.path.abspath(folder_path)
        print(f"Absolute path: {abs_path}")
        
        if not os.path.exists(folder_path):
            print(f"ERROR: Directory does not exist: {folder_path}")
            return image_files
            
        # List all contents of directory for debugging
        print("\nDirectory contents:")
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                print(f"[DIR] {item}")
            else:
                print(f"[FILE] {item}")
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(image_extensions):
                    full_path = os.path.join(root, file)
                    try:
                        # Verify if it's a valid image file
                        with Image.open(full_path) as img:
                            img.verify()
                            image_files.append(full_path)
                            print(f"Added valid image: {full_path}")
                    except Exception as e:
                        print(f"Invalid or corrupted image {full_path}: {str(e)}")
        
        if not image_files:
            print("\nNo valid images found!")
            print(f"Expected extensions: {image_extensions}")
            print("Please check:")
            print("1. Image files exist in the directory")
            print("2. Image files have correct extensions")
            print("3. Image files are not corrupted")
            print("4. File permissions are correct")
    except Exception as e:
        print(f"Error scanning directory {folder_path}: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return image_files

def process_dataset(train_folder="E:/ML/GrievanceProofs/Images/Train", test_folder="E:/ML/GrievanceProofs/Images/Test"):
    """Process entire dataset and create analysis results"""
    print("\nStarting dataset processing...")
    print(f"Current working directory: {os.getcwd()}")
    
    # Normalize paths
    train_folder = os.path.normpath(train_folder)
    test_folder = os.path.normpath(test_folder)
    
    print("\nVerifying paths:")
    print(f"Train folder: {os.path.abspath(train_folder)}")
    print(f"Test folder: {os.path.abspath(test_folder)}")
    
    # Ensure directories exist
    dirs = ensure_directories()
    
    # Create sample image if no images exist
    def create_sample_image(folder):
        if not os.listdir(folder):
            print(f"\nCreating sample image in {folder}")
            sample_img = Image.new('RGB', (100, 100), color='red')
            sample_path = os.path.join(folder, 'sample.png')
            sample_img.save(sample_path)
            print(f"Created sample image: {sample_path}")
    
    create_sample_image(train_folder)
    create_sample_image(test_folder)
    
    analyzer = GrievanceImageAnalyzer()
    results = []
    
    # Create results directory for detailed analyses
    details_dir = os.path.join(dirs['results'], 'detailed_analyses')
    os.makedirs(details_dir, exist_ok=True)
    
    def process_folder(folder_path, dataset_type):
        if not os.path.exists(folder_path):
            print(f"Warning: {dataset_type} folder not found: {folder_path}")
            return []
            
        folder_results = []
        print(f"\nProcessing {dataset_type} images...")
        
        # Get all image files including those in subfolders
        image_files = get_image_files(folder_path)
        
        if not image_files:
            print(f"No images found in {folder_path} or its subfolders")
            return []
        
        print(f"Found {len(image_files)} images in {dataset_type} folder")
        
        for img_path in tqdm(image_files):
            try:
                # Get relative category from subfolder name
                relative_path = os.path.relpath(img_path, folder_path)
                category = os.path.dirname(relative_path).replace('\\', '/').split('/')[0]
                
                result = analyzer.analyze_image(img_path)
                if result:
                    result['dataset'] = dataset_type
                    result['category'] = category if category else 'uncategorized'
                    folder_results.append(result)
                    # Save detailed analysis
                    save_detailed_analysis(result, details_dir)
            except Exception as e:
                print(f"Error processing {img_path}: {str(e)}")
        
        return folder_results
    
    # Process both folders
    train_results = process_folder(train_folder, 'train')
    test_results = process_folder(test_folder, 'test')
    
    results = train_results + test_results
    
    if not results:
        print("No images were successfully processed!")
        return None
    
    # Save results
    df = pd.DataFrame(results)
    
    # Save main results CSV
    output_path = os.path.join(dirs['results'], 'image_analysis_results.csv')
    df.to_csv(output_path, index=False)
    print(f"\nResults saved to: {output_path}")
    
    # Generate and save summary report
    summary_path = os.path.join(dirs['results'], 'analysis_summary.txt')
    with open(summary_path, 'w') as f:
        f.write("Analysis Summary\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total images processed: {len(results)}\n\n")
        f.write("Category Distribution:\n")
        f.write(str(df['category'].value_counts()) + "\n\n")
        f.write("Severity Distribution:\n")
        f.write(str(df['severity'].value_counts()) + "\n\n")
        f.write("Dataset Distribution:\n")
        f.write(str(df['dataset'].value_counts()) + "\n\n")
        f.write("\nDetailed analyses saved in: " + details_dir)
    
    print(f"Summary report saved to: {summary_path}")
    
    # Print category-wise severity distribution
    print("\nCategory-wise Severity Distribution:")
    print(pd.crosstab(df['category'], df['severity']))
    
    return df

if __name__ == "__main__":
    try:
        # Setup environment
        cache_dir = setup_env()
        
        # Process images
        results_df = process_dataset()
        
        if results_df is not None:
            print("\nAnalysis completed successfully!")
            print("\nSample Analyses:")
            print(results_df.head())
    except Exception as e:
        print(f"\nError during execution: {str(e)}")
        print("\nPlease ensure:")
        print("1. All required directories exist")
        print("2. You have permission to access the directories")
        print("3. There is enough disk space")
        print("4. The images are in valid format (PNG, JPG, JPEG, WEBP)")
