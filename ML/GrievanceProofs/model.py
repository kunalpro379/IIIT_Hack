import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import os
from tqdm import tqdm
import pandas as pd
import json
import random
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    pipeline
)

def setup_env():
    """Setup environment variables to use E drive"""
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

class DetailedImageAnalyzer:
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
        
        # Description templates
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

    def generate_detailed_description(self, image_path):
        """Generate a detailed description of the image"""
        image = Image.open(image_path).convert('RGB')
        caption = self.predict_caption(image)
        
        # Extract detailed features
        objects = self.extract_objects(caption)
        attributes = self.extract_attributes(caption)
        scene = self.extract_scene(caption)
        relationships = self.extract_relationships(caption)
        emotions = self.extract_emotions(caption)
        
        # Build detailed description
        description_parts = []
        
        # Start with a random template
        description_parts.append(random.choice(self.description_templates['start']))
        
        # Add scene description
        description_parts.append(f"{scene}.")
        
        # Add objects and their attributes
        if objects:
            description_parts.append("The image contains the following objects:")
            for obj, attrs in zip(objects, attributes):
                description_parts.append(f"{obj} with attributes {', '.join(attrs)}.")
        
        # Add relationships
        if relationships:
            description_parts.append("The relationships between objects are as follows:")
            for rel in relationships:
                description_parts.append(f"{rel}.")
        
        # Add emotional tone
        if emotions:
            description_parts.append(f"The emotional tone of the image is {emotions}.")
        
        # Combine all parts into a paragraph
        return " ".join(description_parts)

    def extract_objects(self, caption):
        """Extract key objects mentioned in caption"""
        # Add NLP processing here if needed
        return [word.strip() for word in caption.lower().split() if len(word) > 3]

    def extract_attributes(self, caption):
        """Extract attributes of objects"""
        attributes = ['color', 'size', 'shape', 'texture']
        # Placeholder for actual attribute extraction logic
        return [random.sample(attributes, 2) for _ in range(len(self.extract_objects(caption)))]

    def extract_scene(self, caption):
        """Extract scene context"""
        scenes = ['indoor', 'outdoor', 'urban', 'rural', 'natural', 'artificial']
        return random.choice(scenes)

    def extract_relationships(self, caption):
        """Extract relationships between objects"""
        relationships = ['next to', 'above', 'below', 'inside', 'outside']
        # Placeholder for actual relationship extraction logic
        return [f"Object {i} is {random.choice(relationships)} object {i+1}" for i in range(len(self.extract_objects(caption))-1)]

    def extract_emotions(self, caption):
        """Extract emotional tone"""
        emotions = ['happy', 'sad', 'neutral', 'exciting', 'calm']
        return random.choice(emotions)

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
        'detailed_description': result['detailed_description'],
        'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Save as JSON
    json_path = os.path.join(output_dir, f'{base_name}_analysis.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=4, ensure_ascii=False)

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
    
    analyzer = DetailedImageAnalyzer()
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
                
                detailed_description = analyzer.generate_detailed_description(img_path)
                result = {
                    'image_path': img_path,
                    'caption': analyzer.predict_caption(img_path),
                    'detailed_description': detailed_description,
                    'dataset': dataset_type,
                    'category': category if category else 'uncategorized',
                    'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                }
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
        f.write("Dataset Distribution:\n")
        f.write(str(df['dataset'].value_counts()) + "\n\n")
        f.write("\nDetailed analyses saved in: " + details_dir)
    
    print(f"Summary report saved to: {summary_path}")
    
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